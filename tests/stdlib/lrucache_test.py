from pyrindow.stdlib.lrucache import LruCache
from time import sleep

def test_hasFalse():
    cache = LruCache(3)
    assert False == cache.has('a')
    assert False == cache.has('b')
    assert False == cache.has('c')
    assert False == cache.has('d')

def test_hasTrue():
    cache = LruCache(3)
    # ===Set to free space ===
    cache.set('a',1)
    cache.set('b',2)
    cache.set('c',3)
    assert True == cache.has('a')
    assert True == cache.has('b')
    assert True == cache.has('c')
    assert False == cache.has('d')

def test_get():
    cache = LruCache(3)
    # ===Overflow===
    cache.set('a',1)
    cache.set('b',2)
    cache.set('c',3)
    assert 1 == cache.get('a')
    assert 2 == cache.get('b')
    assert 3 == cache.get('c')
    assert 1000 == cache.get('d',1000)
    cache.set('e',4)
    assert 2000 == cache.get('a',2000)

def test_Overflow():
    cache = LruCache(3)
    # ===Overflow===
    cache.set('a',1)
    cache.set('b',2)
    cache.set('c',3)
    cache.set('d',4)
    assert False == cache.has('a')
    assert True == cache.has('b')
    assert True == cache.has('c')
    assert True == cache.has('d')

def test_recentlyUsed():
    cache = LruCache(3)
    cache.set('a',1)
    cache.set('b',2)
    cache.set('c',3)
    # ===Least Recently Used===
    assert 1 == cache.get('a')
    cache.set('d',5)
    assert True == cache.has('a')
    assert False == cache.has('b')
    assert True == cache.has('c')
    assert True == cache.has('d')

def test_expires():
    cache = LruCache(3)
    cache.set('a',1)
    cache.set('b',2)
    cache.set('c',3)
    # ===Expires(1)===
    cache.set('d',6,1)
    assert False == cache.has('a')
    assert True == cache.has('b')
    assert True == cache.has('c')
    assert True == cache.has('d')
    sleep(2)
    assert True == cache.has('b')
    assert True == cache.has('c')
    assert False == cache.has('d')

def test_expires2():
    cache = LruCache(3)
    cache.set('a',1)
    cache.set('b',2)
    cache.set('c',3)
    cache.set('d',6,1)
    assert False == cache.has('a')
    assert True == cache.has('b')
    assert True == cache.has('c')
    assert True == cache.has('d')
    sleep(2)
    assert False == cache.has('a')
    assert True == cache.has('b')
    assert True == cache.has('c')
    assert False == cache.has('d')

def test_replace():
    cache = LruCache(3)
    cache.set('a',1)
    cache.set('b',2)
    cache.set('c',3)
    # ===Replace===
    cache.set('b',6,1)
    assert True == cache.has('a')
    assert True == cache.has('b')
    assert True == cache.has('c')
    cache.set('c',100)
    assert 1 == cache.get('a')
    assert 6 == cache.get('b')
    assert 100 == cache.get('c')

def test_delete():
    cache = LruCache(3)
    cache.set('a',1)
    cache.set('b',2)
    cache.set('c',3)
    # ===Delete===
    assert True == cache.delete('a')
    assert False == cache.has('a')
    assert True == cache.has('b')
    assert True == cache.has('c')
    assert False == cache.delete('a')

def test_add():
    cache = LruCache(3)
    cache.set('a',1)
    cache.set('b',2)
    cache.set('c',3)
    # ===Add===
    assert True == cache.add('d',7)
    assert None == cache.get('a')
    assert 2 == cache.get('b')
    assert 3 == cache.get('c')
    assert 7 == cache.get('d')
    assert False == cache.add('d',1000)
    assert 2 == cache.get('b')
    assert 3 == cache.get('c')
    assert 7 == cache.get('d')

def test_peek():
    cache = LruCache(3)
    cache.set('a',1)
    cache.set('b',2)
    cache.set('c',3)
    # ===Peek===
    assert 1 == cache.peek('a')
    assert True == cache.add('d',8)
    assert False == cache.has('a')
    assert True == cache.has('b')
    assert True == cache.has('c')
    assert True == cache.has('d')

def test_clear():
    cache = LruCache(3)
    cache.set('a',1)
    cache.set('b',2)
    cache.set('c',3)
    # ===Clear===
    cache.clear()
    assert False == cache.has('a')
    assert False == cache.has('b')
    assert False == cache.has('c')
