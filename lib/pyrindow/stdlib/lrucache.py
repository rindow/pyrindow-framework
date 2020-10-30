import threading
from time import time

class _Node(object):
    def __init__(self):
        self.empty = True

class LruCache(object):
    def __init__(self, threshold=500, default_timeout=None,ignore_errors=False):
        self._lock = threading.RLock()
        self._map = {}
        self._allocateNode(threshold)
        self._default_timeout = default_timeout
        self._hit_count = 0
        self._miss_count = 0

    def _allocateNode(self, threshold):
        if threshold < 1:
            raise Exception('threshold must be grater then 0')
        self._head = node = _Node()
        for i in range(threshold-1):
            node.next = _Node()
            node.next.prev = node
            node = node.next
        node.next = self._head
        self._head.prev = node
        self._threshold = threshold

    def _unsetNode(self, key):
        node = self._map[key]
        del self._map[key]
        node.empty = True
        node.key = None
        node.value = None
        self._bubbleupNode(node)
        self._head = node.next

    def _setNode(self,key,value,timeout=None):
        if key in self._map:
            node = self._map[key]
        else:
            node = self._head.prev
            if node.empty:
                node.empty = False
            else:
                del self._map[node.key]
            self._map[key] = node
            node.key = key
        node.value = value
        if timeout == None:
            node.expires = 0
        else:
            node.expires = time() + timeout
        self._bubbleupNode(node)
        self._head = node

    def _bubbleupNode(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = self._head.prev
        node.next = self._head.prev.next
        node.next.prev = node
        node.prev.next = node

    def clear(self):
        with self._lock:
            node = self._head
            for i in range(self._threshold):
                node.empty = True
                node.key = None
                node.value = None
                node = node.next
            self._map = {}
            self._hit_count = 0
            self._miss_count = 0

    def purge(self):
        with self._lock:
            keys = []
            for key,_ in self._map.items():
                keys.append(key)
            for key in keys:
                node = self._map[key]
                if node.expires != 0 and node.expires <= time():
                    self._unsetNode(key)

    def peek(self, key, default=None):
        with self._lock:
            try:
                node = self._map[key]
                if node.expires != 0 and node.expires <= time():
                    self._unsetNode(key)
                    self._miss_count += 1
                    return default
                self._hit_count += 1
                return node.value
            except KeyError:
                self._miss_count += 1
                return default

    def get(self, key, default=None):
        with self._lock:
            try:
                node = self._map[key]
                if node.expires != 0 and node.expires <= time():
                    self._unsetNode(key)
                    self._miss_count += 1
                    return default
                self._bubbleupNode(node)
                self._head = node
                self._hit_count += 1
                return node.value
            except KeyError:
                self._miss_count += 1
                return default

    def set(self, key, value, timeout=None):
        with self._lock:
            if timeout == None:
                timeout = self._default_timeout
            self._setNode(key,value,timeout)
            return True

    def add(self, key, value, timeout=None):
        with self._lock:
            if key in self._map:
                node = self._map[key]
                if node.expires == 0 or node.expires > time():
                    return False
            if timeout == None:
                timeout = self._default_timeout
            self._setNode(key,value,timeout)
            return True

    def delete(self, key):
        with self._lock:
            if not key in self._map:
                return False
            self._unsetNode(key)
            return True

    def has(self, key):
        with self._lock:
            try:
                node = self._map[key]
                if node.expires != 0 and node.expires <= time():
                    self._unsetNode(key)
                    return False
                return True
            except KeyError:
                return False

    def hit(self):
        return self._hit_count

    def miss(self):
        return self._miss_count

    def __len__(self):
        return len(self._map)
