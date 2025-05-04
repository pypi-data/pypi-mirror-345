"""
Adapter to instrument OpenAI Python SDK via proxy.

This file defines both the proxy machinery and the OpenAIAdapter,
so users don’t need separate modules.
"""
from __future__ import annotations

import importlib.metadata as im
import logging
import time
from typing import Any
from typing import Callable
from typing import Optional

# conditional import of OpenAI SDK
try:
    import openai
except ImportError:
    openai = None

from observai.core.buffer import capture_event
from .base import Adapter

_logger = logging.getLogger(__name__)
_patched = False


def _extract_useful(resp: Any) -> Any:
    """
    Extract the main payload from an OpenAI response:
      - chat.completions → .choices[0].message.content
      - text completions → .choices[0].text
      - otherwise return the raw response object
    """
    try:
        first = resp.choices[0]
        msg = getattr(first, "message", None)
        if msg is not None and hasattr(msg, "content"):
            return msg.content
    except Exception:
        pass

    try:
        first = resp.choices[0]
        text = getattr(first, "text", None)
        if text is not None:
            return text
    except Exception:
        pass

    return resp


class _MethodProxy:
    """
    Proxy call wrapper that measures latency and captures events.
    """
    def __init__(self, fn: Callable[..., Any], route: str) -> None:
        self._fn = fn
        self._route = route

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        t0 = time.time()
        result = self._fn(*args, **kwargs)
        t1 = time.time()

        model = kwargs.get("model") or getattr(result, "model", None)
        useful = _extract_useful(result)

        # find prompt argument by common keys
        prompt: Optional[Any] = None
        for key in ("messages", "prompt", "input"):  # common request keys
            if key in kwargs:
                prompt = kwargs[key]
                break
        if prompt is None and args:
            prompt = args[0]

        capture_event(
            provider="openai",
            route=self._route,
            model=model,
            prompt=prompt,
            response=useful,
            latency_ms=(t1 - t0) * 1000,
        )
        return result


class _OpenAIProxy:
    """
    Proxy object that delegates attribute access to the underlying client,
    wrapping callables in _MethodProxy to capture each API method.
    """
    def __init__(self, client: Any, prefix: str = "") -> None:
        object.__setattr__(self, "_client", client)
        object.__setattr__(self, "_prefix", prefix)

    def __getattr__(self, name: str) -> Any:
        orig = getattr(self._client, name)
        route = f"{self._prefix}.{name}".lstrip(".")
        if callable(orig):
            return _MethodProxy(orig, route)
        return _OpenAIProxy(orig, route)


def patch_openai_proxy() -> None:
    """
    Override openai.OpenAI (+ AsyncOpenAI) and rebind module shortcuts
    through our proxy implementation. Idempotent—only applies once.
    """
    global _patched
    if _patched:
        _logger.debug("OpenAI proxy already applied, skipping")
        return
    if openai is None:
        _logger.warning("openai package not installed; skipping OpenAIAdapter patch")
        return

    real_sync = getattr(openai, "OpenAI", None)
    if not real_sync:
        _logger.error("openai.OpenAI class not found; cannot patch proxy")
        return
    real_async = getattr(openai, "AsyncOpenAI", None)

    def sync_factory(*args: Any, **kwargs: Any) -> _OpenAIProxy:
        inst = real_sync(*args, **kwargs)
        return _OpenAIProxy(inst)
    openai.OpenAI = sync_factory

    if real_async:
        def async_factory(*args: Any, **kwargs: Any) -> _OpenAIProxy:
            inst = real_async(*args, **kwargs)
            return _OpenAIProxy(inst)
        openai.AsyncOpenAI = async_factory

    # rebind module-level shortcuts on a fresh proxy instance
    default = openai.OpenAI()
    for name in (
        "chat", "completions", "embeddings", "files", "images", "audio",
        "moderations", "models", "fine_tuning", "vector_stores",
        "batches", "uploads", "responses", "evals"
    ):
        if hasattr(default, name):
            setattr(openai, name, getattr(default, name))

    _patched = True
    _logger.info("ObservAI: OpenAI proxy applied successfully")


class OpenAIAdapter(Adapter):
    """
    Adapter that applies the OpenAI proxy to capture all LLM calls.
    """
    name = "openai.proxy"

    @classmethod
    def is_available(cls) -> bool:
        if openai is None:
            return False
        try:
            im.version("openai")
            return True
        except im.PackageNotFoundError:
            return False

    def patch(self) -> None:
        patch_openai_proxy()
