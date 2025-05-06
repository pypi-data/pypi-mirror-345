# fastpluggy/core/global_registry.py

from typing import Any

class GlobalRegistry:
    _global_registry: dict[str, Any] = {}

    @classmethod
    def register_global(cls, key: str, obj: Any):
        cls._global_registry[key] = obj

    @classmethod
    def get_global(cls, key: str, default=None) -> Any:
        return cls._global_registry.get(key, default)

    @classmethod
    def has_global(cls, key: str) -> bool:
        return key in cls._global_registry

    @classmethod
    def get_all_globals(cls) -> dict[str, Any]:
        return dict(cls._global_registry)

    @classmethod
    def clear_globals(cls):
        cls._global_registry.clear()
