import time
from dataclasses import dataclass
from typing import Optional, Any


def now():
    # Get the current time in seconds since the epoch
    return time.time()


@dataclass(frozen=True)
class Entry:
    value: Any
    timestamp: int
    ttl: Optional[int]

    def _is_expired(self) -> bool:
        # Check if the entry has expired based on TTL
        return (
            (self.ttl is not None)
            and (self.ttl > 0)
            and (self.timestamp + self.ttl) <= now()
        )


class MemPy:
    def __init__(self) -> None:
        # Initialize the in-memory store
        self.store: dict[str, Entry] = {}

    def _make_entry(
        self, value: Any, timestamp: Optional[int] = None, ttl: Optional[int] = None
    ) -> Entry:
        # Create a new Entry object
        return Entry(value, timestamp or now(), ttl=ttl)

    def _set_entry(
        self,
        key: str,
        value: Any,
        timestamp: Optional[int] = None,
        ttl: Optional[int] = None,
    ) -> bool:
        # Set an entry in the store
        self.store[key] = self._make_entry(value, timestamp, ttl)
        return True

    def _does_exists(self, key) -> bool:
        # Check if a key exists in the store
        return key in self.store

    def set(
        self,
        key: str,
        value: Any,
        timestamp: Optional[int] = None,
        ttl: Optional[int] = 0,
    ) -> bool:
        """Set a value in the store. Optionally provide timestamp and TTL."""
        entry = self._get_entry(key)
        if entry is not None:
            existing_timestamp: int = entry.timestamp
            if not timestamp or timestamp > existing_timestamp:
                self._set_entry(key, value, timestamp, ttl)
                return True
            else:
                return False
        else:
            self._set_entry(key, value, timestamp, ttl)
            return True

    def get_value(self, key: str) -> Optional[Any]:
        """Get the value for a key if it exists and is not expired."""
        item: Optional[Entry] = self._get_entry(key)
        return item.value if item else None

    def _get_entry(self, key: str) -> Optional[Entry]:
        # Retrieve the Entry object for a key, handling expiration
        item = self.store.get(key)
        if item and item._is_expired():
            self.delete(key)
            return None
        return item

    def delete(self, key: str) -> bool:
        """Delete a key from the store."""
        if self._does_exists(key):
            del self.store[key]
            return True
        return False

    def incr(self, key: str) -> Optional[int]:
        """Increment the integer value for a key. Initializes to 1 if not present."""
        if key not in self.keys():
            self._set_entry(key, 1)
            return 1
        elif isinstance(self.get_value(key), int):
            new_value = (self.get_value(key) or 0) + 1
            self._set_entry(key, new_value)
            return new_value
        else:
            raise ValueError("Value is not an integer")

    def keys(self) -> list[str]:
        """Return a list of all keys in the store."""
        return list(self.store.keys())
