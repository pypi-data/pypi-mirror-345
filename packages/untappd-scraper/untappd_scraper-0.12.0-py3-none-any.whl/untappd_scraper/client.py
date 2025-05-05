"""Handle httpx client and hishel caching."""

import logging
from datetime import timedelta
from typing import Final

import hishel

CACHE: Final = timedelta(minutes=30).total_seconds()
TIMEOUT: Final = timedelta(seconds=20).total_seconds()


logging.getLogger("hishel.controller").setLevel(logging.DEBUG)


def get_httpx_client() -> hishel.CacheClient:
    """Return a cachhed HTTPX client with caching enabled."""
    storage = hishel.FileStorage(ttl=CACHE)
    controller = hishel.Controller(force_cache=True)
    return hishel.CacheClient(
        follow_redirects=True, storage=storage, controller=controller, timeout=TIMEOUT
    )


client = get_httpx_client()
