import time, threading, os, cloudpickle
from collections import OrderedDict
from functools import wraps

def make_hashable(obj):
    """Recursively convert mutable objects to hashable types."""
    if isinstance(obj, (list, tuple)):
        return tuple(make_hashable(e) for e in obj)
    if isinstance(obj, dict):
        return tuple(sorted((k, make_hashable(v)) for k, v in obj.items()))
    return obj  # Assume obj is already hashable

def timed_lru_cache(max_size: int, minutes: float):
    """
    A decorator that caches function results up to a maximum size and discards
    them after a specified number of minutes.

    Args:
        max_size (int): Maximum number of items to cache.
        minutes (float): Time in minutes after which cached items expire.

    Returns:
        Decorator function.
    """
    def decorator(func):
        cache = OrderedDict()
        expiration_time = minutes * 60  # Convert minutes to seconds

        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (make_hashable(args), make_hashable(kwargs))

            # Remove expired items
            current_time = time.time()
            for k in list(cache.keys()):
                cached_time, _ = cache[k]
                if current_time - cached_time > expiration_time:
                    cache.pop(k)
                else:
                    break  # Stop once we hit a non-expired item

            # Check if the result is already cached
            if key in cache:
                cache.move_to_end(key)
                _, result = cache[key]
                return result

            # Compute the result
            result = func(*args, **kwargs)

            # Store in cache
            cache[key] = (current_time, result)
            cache.move_to_end(key)

            # Enforce max size
            if len(cache) > max_size:
                cache.popitem(last=False)

            return result

        return wrapper
    return decorator

class DiskLRUCache:
    """
    A thread-safe LRU cache that stores values on disk using cloudpickle.
    """
    def __init__(self, max_size: int, cache_file: str):
        """
        Initialize the disk-based LRU cache.

        Args:
            max_size (int): Maximum number of items to cache.
            cache_file (str): Path to the file where the cache is stored.
        """
        self.max_size = max_size
        self.cache_file = cache_file
        self.lock = threading.Lock()
        self.cache = self._load_cache()

    def _load_cache(self):
        """Load the cache from disk if the file exists."""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'rb') as f:
                try:
                    return cloudpickle.load(f)
                except EOFError:
                    return OrderedDict()
        return OrderedDict()

    def _save_cache(self):
        """Save the cache to disk."""
        with open(self.cache_file, 'wb') as f:
            cloudpickle.dump(self.cache, f)

    def get(self, key):
        """Retrieve a value from the cache."""
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)  # Mark as recently used
                return self.cache[key]
            return None

    def put(self, key, value):
        """Add or update a value in the cache."""
        with self.lock:
            self.cache[key] = value
            self.cache.move_to_end(key)  # Mark as recently used
            if len(self.cache) > self.max_size:
                self.cache.popitem(last=False)  # Remove the oldest item
            self._save_cache()  # Persist changes to disk

def disk_lru_cache(max_size: int, cache_file: str):
    """
    A decorator that caches function results to disk using an LRU policy.

    Args:
        max_size (int): Maximum number of items to cache.
        cache_file (str): Path to the file where the cache is stored.

    Returns:
        Decorator function.
    """
    cache = DiskLRUCache(max_size, cache_file)

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Convert arguments to a hashable form
            key = (make_hashable(args), make_hashable(kwargs))

            # Check if the result is already cached
            result = cache.get(key)
            if result is not None:
                return result

            # Compute the result if not cached
            result = func(*args, **kwargs)

            # Add the result to the cache
            cache.put(key, result)

            return result

        return wrapper

    return decorator

def retry(retry_count: int, delay: float):
    """
    A decorator that retries a function when it raises an exception.

    Args:
        retry_count (int): Maximum number of retry attempts.
        delay (float): Time (in seconds) to wait between retries.

    Returns:
        Decorator function.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while True:
                try:
                    # Attempt to execute the function
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts > retry_count:
                        # If max retries reached, re-raise the exception
                        print(f"Function {func.__name__} failed after {retry_count} retries.")
                        raise
                    print(f"Attempt {attempts} failed with error: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)

        return wrapper

    return decorator
