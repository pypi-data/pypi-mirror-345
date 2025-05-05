from typing import BinaryIO, Callable, Generic, Iterable, Optional, Protocol, Tuple, TypeVar
import logging

from .digest import ContentDigest

logger = logging.getLogger(__name__)


U = TypeVar("U")

class DownloadCacheException(Exception):
    pass

class FetchInterrupted(DownloadCacheException, Generic[U]):
    def __init__(self, *, url: U) -> None:
        self.url = url
        super().__init__(f"Downloading of '{url}' was interrupted")

class Cache(Protocol[U]):
    def hits(self) -> int: ...
    def misses(self) -> int: ...
    def get_by_url(self, *, url: U) -> Optional[Tuple[BinaryIO, ContentDigest]]: ...
    def get(self, *, digest: ContentDigest) -> Optional[BinaryIO]: ...
    def try_fetch(self, url: U, fetcher: Callable[[U], Iterable[bytes]]) -> "Tuple[BinaryIO, ContentDigest] | FetchInterrupted[U]": ...
    def fetch(self, url: U, fetcher: Callable[[U], Iterable[bytes]], retries: int = 3) -> "Tuple[BinaryIO, ContentDigest]":
        for _ in range(retries):
            result = self.try_fetch(url, fetcher)
            if not isinstance(result, FetchInterrupted):
                return result
        raise RuntimeError("Number of retries exhausted")

from .disk_cache import DiskCache as DiskCache
from .memory_cache import MemoryCache as MemoryCache
from .noop_cache import NoopCache as NoopCache
