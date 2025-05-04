import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
import time
import random
from mempy_miladtsx.mempy import MemPy


def random_key(length: int = 10) -> str:
    import string

    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def test_set_and_get():
    mem = MemPy()
    mem.set("foo", "bar")
    assert mem.get_value("foo") == "bar"
    mem.set("num", 123)
    assert mem.get_value("num") == 123


def test_update_value():
    mem = MemPy()
    mem.set("key", "v1")
    mem.set("key", "v2")
    assert mem.get_value("key") == "v2"


def test_dont_update_old_value():
    mem = MemPy()
    mem.set("key", "v1")
    mem.set("key", "v2", 1)
    assert mem.get_value("key") == "v1"


def test_delete():
    mem = MemPy()
    mem.set("k", "v")
    mem.delete("k")
    assert mem.get_value("k") is None
    # Deleting non-existent key should not raise
    mem.delete("not_exist")


def test_increment():
    mem = MemPy()
    mem.set("count", 1)
    mem.incr("count")
    assert mem.get_value("count") == 2
    # Increment non-existent key
    mem.incr("new_count")
    assert mem.get_value("new_count") == 1
    # Increment non-integer value should raise
    mem.set("str", "abc")
    try:
        mem.incr("str")
    except Exception:
        pass
    else:
        raise AssertionError(
            "Expected an exception when incrementing a non-integer value"
        )


def test_ttl_expiry():
    mem = MemPy()
    mem.set("temp", "expires", ttl=1)
    assert mem.get_value("temp") == "expires"
    time.sleep(1.1)
    assert mem.get_value("temp") is None


def test_keys_and_get_entry():
    mem = MemPy()
    mem.set("a", 1)
    mem.set("b", 2)
    mem.set("c", 3)
    assert set(mem.keys()) == {"a", "b", "c"}
    assert mem._get_entry("a").value == 1
    assert mem._get_entry("notfound") is None


def test_large_batch_set_get():
    mem = MemPy()
    count = 10000
    keys = [random_key() for _ in range(count)]
    values = [random.randint(1, 1000) for _ in range(count)]
    for k, v in zip(keys, values):
        mem.set(k, v)
    for k, v in zip(keys, values):
        assert mem.get_value(k) == v


def test_branch_coverage_edge_cases():
    mem = MemPy()
    # Set with ttl=0 (should not expire)
    mem.set("persist", "val", ttl=0)
    assert mem.get_value("persist") == "val"
    # Set with negative ttl (should not expire)
    mem.set("persist2", "val2", ttl=-1)
    assert mem.get_value("persist2") == "val2"
    # Set None value
    mem.set("none", None)
    assert mem.get_value("none") is None
    # Delete after expiry
    mem.set("exp", "gone", ttl=1)
    time.sleep(1.1)
    mem.delete("exp")  # Should not raise
