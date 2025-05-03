import time
from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Any


def now():
    return time.time()


@dataclass(frozen=True)
class Entry:
    value: Any
    timestamp: int
    ttl: Optional[int]

    def _is_expired(self) -> bool:
        return (self.ttl is not None) and (self.timestamp + self.ttl) <= now()

    def __repr__(self) -> str:
        created_at = datetime.fromtimestamp(self.timestamp)
        expiring_at = datetime.fromtimestamp(self.timestamp + self.ttl)
        return f"Entry(value={self.value!r}, expiring_at={expiring_at}, created_at={created_at})"


class MemPy:
    def __init__(self):
        self.store: dict[str, Entry] = {}

    def _make_entry(
        self, value: Any, timestamp: Optional[int] = None, ttl: Optional[int] = None
    ) -> Entry:
        return Entry(value, timestamp or now(), ttl=ttl)

    def _set_entry(
        self,
        key: str,
        value: Any,
        timestamp: Optional[int] = None,
        ttl: Optional[int] = None,
    ) -> bool:
        try:
            self.store[key] = self._make_entry(value, timestamp, ttl)
            return True
        except Exception as e:
            print(e)
            return False

    def _does_exists(self, key) -> bool:
        return key in self.store

    def set(self, key: str, value: Any, timestamp: Optional[int] = None) -> bool:
        if self._does_exists(key):
            existing_timestamp: int = self._get_entry(key).timestamp
            if not timestamp or timestamp > existing_timestamp:
                self._set_entry(key, value, timestamp)
                return True
            else:
                return False
        else:
            self._set_entry(key, value, timestamp)
            return True

    def get_value(self, key: str) -> Optional[Any]:
        item: Optional[Entry] = self._get_entry(key)
        return item.value if item else None

    def _get_entry(self, key: str) -> Optional[Entry]:
        item = self.store.get(key)
        if item and item._is_expired():
            self.delete(key)
            return None
        return item

    def delete(self, key: str) -> bool:
        if self._does_exists(key):
            del self.store[key]
            return True
        return False

    def incr(self, key: str) -> Optional[int]:
        if key not in self.keys():
            self._set_entry(key, 1)
            return 1
        elif isinstance(self.get_value(key), int):
            new_value = self.get_value(key) + 1
            self._set_entry(key, new_value)
            return new_value
        else:
            raise ValueError("Value is not an integer")

    def keys(self) -> list[str]:
        return list(self.store.keys())
