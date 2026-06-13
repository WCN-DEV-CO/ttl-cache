import pytest
from ttl_cache import TTLCache

def make_clock(start=0.0):
    t={"v":start}
    return t, (lambda: t["v"])

def test_set_get():
    c=TTLCache()
    c.set("a",1); assert c.get("a")==1

def test_miss_returns_default():
    c=TTLCache()
    assert c.get("x", default="d")=="d"
    assert c.misses==1

def test_expiry():
    t,clock=make_clock()
    c=TTLCache(default_ttl=10, time_fn=clock)
    c.set("a",1)
    t["v"]=9.9;  assert c.get("a")==1     # still valid
    t["v"]=10.0; assert c.get("a") is None # expired

def test_custom_ttl_per_entry():
    t,clock=make_clock()
    c=TTLCache(default_ttl=100, time_fn=clock)
    c.set("short",1,ttl=5)
    t["v"]=6; assert c.get("short") is None

def test_max_size_evicts_oldest():
    c=TTLCache(default_ttl=100, max_size=2)
    c.set("a",1); c.set("b",2); c.set("c",3)   # evicts "a"
    assert c.get("a") is None
    assert c.get("b")==2 and c.get("c")==3

def test_lru_on_access_protects_entry():
    c=TTLCache(default_ttl=100, max_size=2)
    c.set("a",1); c.set("b",2)
    c.get("a")                 # touch a -> b now oldest
    c.set("c",3)               # evicts b
    assert c.get("a")==1 and c.get("b") is None

def test_get_or_set():
    c=TTLCache(); calls=[]
    def f(): calls.append(1); return 99
    assert c.get_or_set("k", f)==99
    assert c.get_or_set("k", f)==99
    assert len(calls)==1       # factory ran once

def test_purge_removes_expired():
    t,clock=make_clock()
    c=TTLCache(default_ttl=10, time_fn=clock)
    c.set("a",1); c.set("b",2)
    t["v"]=11
    assert c.purge()==2

def test_contains_and_len():
    t,clock=make_clock()
    c=TTLCache(default_ttl=10, time_fn=clock)
    c.set("a",1)
    assert "a" in c and len(c)==1
    t["v"]=11
    assert "a" not in c and len(c)==0

def test_delete_and_hits():
    c=TTLCache()
    c.set("a",1)
    assert c.get("a")==1 and c.hits==1
    assert c.delete("a") is True
    assert c.delete("a") is False

def test_invalid_config():
    with pytest.raises(ValueError): TTLCache(default_ttl=0)
    with pytest.raises(ValueError): TTLCache(max_size=0)
