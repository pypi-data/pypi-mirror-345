import asyncio
from abc import ABC, abstractmethod
from typing import Generic, Optional, TypeVar

from diskcache import Cache

T = TypeVar("T")


class CacheAdapter(ABC, Generic[T]):
    """Abstract base class for cache adapters.

    This adapter supports both synchronous and asynchronous operations.
    """

    @abstractmethod
    def get(self, key: str) -> Optional[T]:
        """Get a value from the cache.

        Args:
            key: The key to retrieve

        Returns:
            The cached value or None if not found
        """
        pass

    @abstractmethod
    def set(self, key: str, value: T, ttl: Optional[int] = None) -> bool:
        """Set a value in the cache.

        Args:
            key: The key to store
            value: The value to store
            ttl: Time to live in seconds, None for no expiration

        Returns:
            True if the value was stored successfully
        """
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a value from the cache.

        Args:
            key: The key to delete

        Returns:
            True if the key was deleted, False if it didn't exist
        """
        pass

    @abstractmethod
    async def __aenter__(self):
        """Enter an async transaction context."""
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit an async transaction context."""
        pass


class DiskCacheAdapter(CacheAdapter[T]):
    """Cache adapter implementation using diskcache.

    This adapter provides a unified interface for working with diskcache,
    supporting both synchronous and asynchronous operations.
    """

    def __init__(self, cache_dir: str = ".cache", **kwargs):
        """Initialize the disk cache adapter.

        Args:
            cache_dir: Directory where cache files will be stored
            **kwargs: Additional arguments passed to diskcache.Cache
        """
        self._cache = Cache(cache_dir, **kwargs)
        self._transaction = None
        self._transaction_lock = asyncio.Lock()  # Lock for transaction safety

    def get(self, key: str) -> Optional[T]:
        """Get a value from the cache."""
        return self._cache.get(key)

    def set(self, key: str, value: T, ttl: Optional[int] = None) -> bool:
        """Set a value in the cache."""
        return self._cache.set(key, value, expire=ttl)

    def delete(self, key: str) -> bool:
        """Delete a value from the cache."""
        try:
            del self._cache[key]
            return True
        except KeyError:
            return False

    async def __aenter__(self):
        await self._transaction_lock.acquire()
        self._transaction = self._cache.transact()
        self._transaction.__enter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            result = self._transaction.__exit__(exc_type, exc_val, exc_tb)
            self._transaction = None
            return result
        finally:
            self._transaction_lock.release()
