# src/guardianai/core/constants.py
from __future__ import annotations

from typing import Dict
from typing import Optional

DEFAULT_FLUSH_INTERVAL: float = 2.0
DEFAULT_MAX_BATCH_SIZE: int = 200
DEFAULT_LOG_PATH: str = "guardianai_events.log"
DEFAULT_TRUNCATE: Optional[int] = 500
DEFAULT_DB_PATH: str = "guardianai_buffer.sqlite"
DEFAULT_ENDPOINT: str = "https://collector.example.com/events/batch"
DEFAULT_HEADERS: Dict[str, str] = {}
