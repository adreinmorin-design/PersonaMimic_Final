import json
import logging
import os
from typing import Any

import redis

logger = logging.getLogger("app.core.cache")


class RedisCache:
    def __init__(self):
        self.url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.client: redis.Redis | None = None
        self._enabled = False

        try:
            self.client = redis.from_url(self.url, decode_responses=True)
            # Ping to verify
            self.client.ping()
            self._enabled = True
            logger.info(f"Redis Cache Online: {self.url}")
        except Exception as e:
            logger.warning(f"Redis Cache Offline (using fallback): {e}")

    def get(self, key: str) -> Any | None:
        if not self._enabled or not self.client:
            return None
        try:
            data = self.client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.debug(f"Redis Get Error: {e}")
            return None

    def set(self, key: str, value: Any, expire: int = 3600):
        if not self._enabled or not self.client:
            return
        try:
            self.client.set(key, json.dumps(value), ex=expire)
        except Exception as e:
            logger.debug(f"Redis Set Error: {e}")


cache = RedisCache()
