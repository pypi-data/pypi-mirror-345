"""Plugin infrastructure: register adapters that patch third‑party SDKs."""
from __future__ import annotations

from typing import List

from observai.adapters.base import Adapter

_adapters: List["Adapter"] = []


def register_adapter(adapter: "Adapter") -> None:
    adapter.patch()
    _adapters.append(adapter)


def register_all_available() -> None:
    """Import every module in observai.adapters and register if available."""
    from importlib import import_module
    from pkgutil import iter_modules

    import observai.adapters as _pkg

    for info in iter_modules(_pkg.__path__):
        module = import_module(f"observai.adapters.{info.name}")
        for obj in module.__dict__.values():
            if (
                isinstance(obj, type)
                and issubclass(obj, Adapter)
                and obj is not Adapter
                and obj.is_available()
            ):
                register_adapter(obj())
