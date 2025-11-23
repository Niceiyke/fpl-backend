import time
from typing import Any, Dict, Optional

import httpx

# Constants
FPL_API_URL = "https://fantasy.premierleague.com/api/bootstrap-static/"
FIXTURES_API_URL = "https://fantasy.premierleague.com/api/fixtures/"
TEAM_API_URL = "https://fantasy.premierleague.com/api/entry"


class _CacheEntry:
    def __init__(self, data: Any, expires_at: float) -> None:
        self.data = data
        self.expires_at = expires_at

    @property
    def is_valid(self) -> bool:
        return time.monotonic() < self.expires_at


class FPLDataFetcher:
    BOOTSTRAP_CACHE_TTL = 300
    FIXTURES_CACHE_TTL = 300
    TEAM_CACHE_TTL = 180

    _client: Optional[httpx.AsyncClient] = None
    _cache: Dict[str, _CacheEntry] = {}

    @classmethod
    async def _get_client(cls) -> httpx.AsyncClient:
        if cls._client is None:
            cls._client = httpx.AsyncClient()
        return cls._client

    @classmethod
    async def _fetch_json(cls, url: str, headers: Optional[Dict[str, str]] = None) -> Any:
        client = await cls._get_client()
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    @classmethod
    def _get_from_cache(cls, key: str) -> Optional[Any]:
        cached = cls._cache.get(key)
        if cached and cached.is_valid:
            return cached.data
        cls._cache.pop(key, None)
        return None

    @classmethod
    def _set_cache(cls, key: str, data: Any, ttl_seconds: int) -> None:
        cls._cache[key] = _CacheEntry(data=data, expires_at=time.monotonic() + ttl_seconds)

    @classmethod
    async def _fetch_with_cache(
        cls, key: str, url: str, ttl_seconds: int, headers: Optional[Dict[str, str]] = None
    ) -> Optional[Any]:
        cached_data = cls._get_from_cache(key)
        if cached_data is not None:
            return cached_data

        try:
            data = await cls._fetch_json(url, headers=headers)
            cls._set_cache(key, data, ttl_seconds)
            return data
        except httpx.HTTPError as e:
            print(f"Error fetching data from {url}: {e}")
            return None

    @classmethod
    async def fetch_fpl_data(cls) -> Optional[Any]:
        return await cls._fetch_with_cache("bootstrap", FPL_API_URL, cls.BOOTSTRAP_CACHE_TTL)

    @classmethod
    async def fetch_fixtures(cls) -> Optional[Any]:
        return await cls._fetch_with_cache("fixtures", FIXTURES_API_URL, cls.FIXTURES_CACHE_TTL)

    @classmethod
    async def fetch_team_data(cls, team_id: int, gameweek_id: int) -> Optional[Any]:
        headers = {
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 5.1; PRO 5 Build/LMY47D)",
            "accept-language": "en",
        }
        url = f"{TEAM_API_URL}/{team_id}/event/{gameweek_id}/picks/"
        cache_key = f"team:{team_id}:{gameweek_id}"
        return await cls._fetch_with_cache(cache_key, url, cls.TEAM_CACHE_TTL, headers=headers)
