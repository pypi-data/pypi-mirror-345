"""
ObservAI SDK — top-level interface

Expose the primary entrypoints and register built-in adapters.
"""
from __future__ import annotations

from typing import Dict
from typing import List
from typing import Optional
from typing import Type

from observai.adapters.base import Adapter
from observai.core.buffer import configure
from observai.core.buffer import flush
from observai.core.buffer import set_user
from observai.core.constants import DEFAULT_DB_PATH
from observai.core.constants import DEFAULT_ENDPOINT
from observai.core.constants import DEFAULT_FLUSH_INTERVAL
from observai.core.constants import DEFAULT_LOG_PATH
from observai.core.constants import DEFAULT_TRUNCATE
from observai.core.registry import register_adapter
from observai.core.registry import register_all_available

__all__ = [
    "init",
    "set_user",
    "flush",
]

def init(
    *,
    adapters: Optional[List[Type[Adapter]]] = None,
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
    Initialize ObservAI SDK.

    Parameters:
      adapters: Optionally specify which adapters to register (e.g., OpenAI).
      user_id: Optional user identifier to include in captured events.
      log_path: Fallback log file path.
      db_path: SQLite persistence file.
      endpoint: Remote collector endpoint for events.
      headers: HTTP headers for collector requests.
      truncate: Truncate long prompts/responses.
      flush_interval: Background flush interval in seconds.
      background: Enable periodic automatic flushing.

    If no adapters are specified, all available adapters are auto-loaded.
    """
    configure(
        user_id=user_id,
        log_path=log_path,
        db_path=db_path,
        endpoint=endpoint,
        headers=headers,
        truncate=truncate,
        flush_interval=flush_interval,
        background=background,
    )

    if adapters is None:
        register_all_available()
    else:
        for adapter_cls in adapters:
            register_adapter(adapter_cls())
