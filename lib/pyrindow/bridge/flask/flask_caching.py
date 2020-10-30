from flask_caching.backends.base import BaseCache
from pyrindow.stdlib.lrucache import LruCache as rindowCache

def lrucache(app, config, args, kwargs):
    kwargs.update(
        dict(
            cache_driver=app.config['serviceLocator'].get('flask_caching.cacheDriver'),
        )
    )
    return LRUCache(**kwargs)

class LRUCache(BaseCache):
    def __init__(self,**kwargs):
        super(LRUCache, self).__init__(default_timeout=kwargs.get('default_timeout'))
        self._cache = kwargs.get('cache_driver')
    def clear(self):
        return self._cache.clear()
    def get(self, key, default=None):
        return self._cache.get(key, default)
    def set(self, key, value, timeout):
        return self._cache.set(key, value, timeout)
    def add(self, key, value, timeout=None):
        return self._cache.add(key, value, timeout)
    def delete(self, key):
        return self._cache.delete(key)
    def has(self, key):
        return self._cache.has(key)
