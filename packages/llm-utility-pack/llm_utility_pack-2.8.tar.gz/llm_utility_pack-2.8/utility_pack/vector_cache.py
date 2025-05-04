from utility_pack.vector_storage_helper import ShardedLmdbStorage
import xxhash

def _hash(key):
    return xxhash.xxh64(key).intdigest()

class VectorCache:
    def __init__(self, path='vector_cache', num_shards=5):
        self.storage = ShardedLmdbStorage(path, num_shards)
    
    def is_cached(self, key):
        return len(self.storage.get_vectors([_hash(key)])) > 0

    def put(self, key, value):
        self.storage.store_vectors([value], [_hash(key)])

    def get(self, key):
        return self.storage.get_vectors([_hash(key)])[0] if self.is_cached(key) else None
