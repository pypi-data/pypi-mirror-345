# 🧠 MemPy — A Minimal In-Memory Key-Value Store

It's a simplified, Python-based in-memory key-value store inspired by [Redis](https://redis.io/). It is built as an experiment to help understand the inner workings of **time-based data storage**, **expiration logic**, and **common data store commands**.

> ⚠️ Not production-ready.

---

## ✨ Features

- `SET` with optional timestamps
- `GET` retrieves value if not expired
- `DELETE` removes key manually
- `INCR` for integer counters
- Optional TTL (Time-To-Live) support
- Lazy expiration: expired keys are deleted on access
- Fully self-contained — no dependencies

---

## 🚀 Getting Started

Clone the repo:

```bash
git clone https://github.com/miladtsx/mempy.git
cd mempy

```

```python
from mempy import MemPy

mem = MemPy()
mem.set("foo", "bar", ttl=10)
print(mem.get_value("foo"))

```

## 🧪 Example Usage
```python

mem = MemPy()

# Basic set and get
mem.set("count", 1)
print(mem.get_value("count"))  # 1

# Increment
mem.incr("count")
print(mem.get_value("count"))  # 2

# TTL support
mem.set("temp", "expires soon", ttl=2)
time.sleep(3)
print(mem.get_value("temp"))  # None (expired)

# Delete
mem.set("to_remove", "bye")
mem.delete("to_remove")
print(mem.get_value("to_remove"))  # None

```

## 🧠 What You'll Learn
Explore:
- How Redis-like systems manage key/value storage
- TTL expiration models (lazy vs. eager deletion)
- Immutable data structures with @dataclass(frozen=True)
- Safe handling of time and conflict resolution
- Python patterns for clean design

## 💡 Inspiration
Inspired by the simplicity and power of Redis, this project aims to make its inner workings more accessible and learnable — one function at a time.

## 📝 Roadmap / Possible Extensions
[ ] Background cleaner thread for eager TTL expiration

[ ] Support for data types (sets, lists, hashes)

[ ] Persistence to disk (AOF/RDB style)

[ ] Pub/Sub model

[ ] CLI interface



## Package Publishing steps
```python

$ python install build twine

$ python3 -m build




```