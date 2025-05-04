# 🧠 MemPy — A Minimal In-Memory Key-Value Store

MemPy is a minimal, self-contained Python in-memory key-value store inspired by Redis. It supports basic commands (`SET`, `GET`, `DELETE`, `INCR`) and optional TTL (Time-To-Live) expiration.

> ⚠️ Not production-ready.

## Features

- Simple key-value storage
- Optional TTL (lazy expiration)
- Integer increment support
- No dependencies

## Installation

```bash
pip install mempy-miladtsx
```

## Example Usage

```python
from mempy_miladtsx.mempy import MemPy

mem = MemPy()
mem.set("foo", "bar", ttl=10)
print(mem.get_value("foo"))
```

## Contribution

[contribution](https://github.com/miladtsx/mempy/blob/main/CONTRIBUTING.md)

## Roadmap

- [ ] Eager TTL expiration (background thread)
- [ ] More data types (sets, lists, hashes)
- [ ] Persistence (AOF/RDB)
- [ ] Pub/Sub, CLI

## License

See [LICENSE](LICENSE).
