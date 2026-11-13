"""LRU cache for computed quotes."""
from collections import OrderedDict


class QuoteCache:
    def __init__(self, max_size=128):
        self.max_size = max_size
        self._items = OrderedDict()
        self.hits = 0
        self.misses = 0

    def get(self, key):
        if key in self._items:
            self._items.move_to_end(key)
            self.hits += 1
            return self._items[key]
        self.misses += 1
        return None

    def put(self, key, value):
        self._items[key] = value
        self._items.move_to_end(key)
        while len(self._items) > self.max_size:
            self._items.popitem(last=False)

    def clear(self):
        self._items.clear()
        self.hits = 0
        self.misses = 0

    def stats(self):
        return {"hits": self.hits, "misses": self.misses, "size": len(self._items)}
