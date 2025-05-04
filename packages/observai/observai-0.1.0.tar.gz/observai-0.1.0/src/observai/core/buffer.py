"""
Core buffering, persistence, and flushing logic for GuardianAI.

This module implements:
  - In-memory queue + SQLite-backed buffer
  - Event capture API for adapters
  - Synchronous and final flush behaviors
  - Optional background flusher thread

All public functions and configuration are exposed via the `init`, `set_user`, `capture_event`, and `flush` APIs.
"""
from __future__ import annotations

import atexit
import json
import logging
import sqlite3
import threading
import uuid
from collections import deque
from datetime import datetime
from datetime import timezone
from hashlib import sha256
from pathlib import Path
from typing import Any
from typing import Deque
from typing import Dict
from typing import List
from typing import Optional
from typing import Set

import httpx
from observai.core.constants import DEFAULT_DB_PATH
from observai.core.constants import DEFAULT_ENDPOINT
from observai.core.constants import DEFAULT_FLUSH_INTERVAL
from observai.core.constants import DEFAULT_HEADERS
from observai.core.constants import DEFAULT_LOG_PATH
from observai.core.constants import DEFAULT_MAX_BATCH_SIZE
from observai.core.constants import DEFAULT_TRUNCATE

_logger = logging.getLogger(__name__)

# Internal state
_queue: Deque[Dict[str, Any]] = deque(maxlen=10_000)
_user_id: Optional[str] = None
_stop_event: threading.Event = threading.Event()
_flusher_thread: Optional[threading.Thread] = None

# Configurable globals (set by init)
_log_path: str = DEFAULT_LOG_PATH
_truncate: Optional[int] = DEFAULT_TRUNCATE
_flush_interval: float = DEFAULT_FLUSH_INTERVAL
_db_path: str = DEFAULT_DB_PATH
_endpoint: str = DEFAULT_ENDPOINT
_headers: Dict[str, str] = DEFAULT_HEADERS

# ------------------------ Public API ----------------------------------

def configure(
    *,
    user_id: Optional[str] = None,
    log_path: str = DEFAULT_LOG_PATH,
    db_path: str = DEFAULT_DB_PATH,
    endpoint: str = DEFAULT_ENDPOINT,
    headers: Optional[Dict[str, str]] = None,
    truncate: Optional[int] = DEFAULT_TRUNCATE,
    flush_interval: float = DEFAULT_FLUSH_INTERVAL,
    background: bool = False,
) -> None:
    """
    Initialize GuardianAI buffering and persistence settings.
    """
    global _user_id, _log_path, _db_path, _endpoint, _headers, _truncate, _flush_interval
    _user_id = user_id
    _log_path = log_path
    _db_path = db_path
    _endpoint = endpoint
    _headers = headers or {}
    _truncate = truncate
    _flush_interval = flush_interval

    _ensure_db()
    atexit.register(_final_flush)
    if background:
        _start_flusher_thread()

def set_user(user_id: str) -> None:
    """Set or update the end user identifier."""
    global _user_id
    _user_id = user_id

def capture_event(
    *,
    provider: str,
    route: str,
    model: Any,
    prompt: Any,
    response: Any,
    latency_ms: float,
) -> None:
    """
    Capture an event from an adapter and buffer it.
    """
    now = datetime.now(timezone.utc)
    timestamp: str = now.isoformat().replace("+00:00", "Z")

    prompt_raw: str = json.dumps(prompt)
    resp_str: str = response if isinstance(response, str) else str(response)
    prompt_trunc: str = prompt_raw if _truncate is None else prompt_raw[:_truncate]
    resp_trunc: str = resp_str if _truncate is None else resp_str[:_truncate]

    ev: Dict[str, Any] = {
        "id": uuid.uuid4().hex,
        "ts": timestamp,
        "user_id": _user_id,
        "provider": provider,
        "route": route,
        "model": model,
        "latency_ms": round(latency_ms, 2),
        "hash": sha256((prompt_trunc + resp_trunc).encode()).hexdigest(),
        "prompt": prompt_trunc,
        "response": resp_trunc,
    }

    _queue.append(ev)
    with sqlite3.connect(_db_path) as con:
        con.execute(
            "INSERT OR IGNORE INTO buffer(id, ts, blob) VALUES(?,?,?)",
            (ev["id"], ev["ts"], json.dumps(ev)),
        )
        con.commit()

def flush(*, final: bool = False) -> None:
    """
    Flush buffered events.
    """
    batch = _collect_batch()
    if not batch:
        return
    success: bool = _send_sync(batch) if final else _write_batch_to_file(batch)
    if success:
        _delete_from_buffer(batch)
    else:
        _queue.extendleft(reversed(batch))

flush_now = flush

# ------------------------ Internal Helpers -----------------------------

def _ensure_db() -> None:
    if Path(_db_path).exists():
        return
    with sqlite3.connect(_db_path) as con:
        con.executescript(
            """
            CREATE TABLE buffer(
                id TEXT PRIMARY KEY,
                ts TEXT,
                blob TEXT
            );
            CREATE INDEX idx_ts ON buffer(ts);
            """
        )
        con.commit()

def _collect_batch() -> List[Dict[str, Any]]:
    if not Path(_db_path).exists():
        return []
    batch: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    with sqlite3.connect(_db_path) as con:
        cursor = con.execute(
            "SELECT id, blob FROM buffer ORDER BY ts LIMIT ?",
            (DEFAULT_MAX_BATCH_SIZE,)
        )
        for _id, blob in cursor:
            batch.append(json.loads(blob))
            seen.add(_id)
    while _queue and len(batch) < DEFAULT_MAX_BATCH_SIZE:
        ev = _queue.popleft()
        if ev["id"] not in seen:
            batch.append(ev)
            seen.add(ev["id"])
    return batch

def _delete_from_buffer(batch: List[Dict[str, Any]]) -> None:
    ids = [(e["id"],) for e in batch]
    with sqlite3.connect(_db_path) as con:
        con.executemany("DELETE FROM buffer WHERE id=?", ids)
        con.commit()

def _write_batch_to_file(batch: List[Dict[str, Any]]) -> bool:
    try:
        with open(_log_path, "a", encoding="utf-8") as f:
            for ev in batch:
                f.write(json.dumps(ev, ensure_ascii=False) + "\n")
        return True
    except OSError as exc:
        _logger.exception("[GuardianAI] file error", exc)
        return False

def _send_sync(batch: List[Dict[str, Any]]) -> bool:
    try:
        resp = httpx.post(
            _endpoint,
            json={"events": batch},
            headers=_headers,
            timeout=5.0,
        )
        return bool(resp.status_code == 200)
    except Exception as exc:
        _logger.exception("[GuardianAI] network error", exc)
        return False

def _final_flush() -> None:
    flush(final=True)
    _stop_event.set()

def _flusher_loop() -> None:
    while not _stop_event.is_set():
        flush()
        _stop_event.wait(_flush_interval)

def _start_flusher_thread() -> None:
    global _flusher_thread
    if _flusher_thread is None or not _flusher_thread.is_alive():
        _flusher_thread = threading.Thread(
            target=_flusher_loop,
            daemon=True,
            name="guardianai-flusher",
        )
        _flusher_thread.start()
