from __future__ import annotations

import logging
import json
from datetime import datetime

from ckan.lib.redis import connect_to_redis, Redis
import ckan.plugins.toolkit as tk

from .config import selfinfo_get_errors_limit
from .utils import get_redis_key


class SelfinfoErrorHandler(logging.Handler):
    """Custom handler to store exceptions."""

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            redis: Redis = connect_to_redis()
            now: float = datetime.utcnow().timestamp()
            log_message = self.format(record)
            redis_key = get_redis_key("errors")

            if not redis.exists(redis_key):
                redis.set(redis_key, json.dumps([]))

            erorrs: list = json.loads(redis.get(redis_key))
            errors_limit = selfinfo_get_errors_limit()
            if len(erorrs) >= errors_limit:
                start_key = len(erorrs) - errors_limit + 1
                erorrs = erorrs[start_key:]
            current_url = None
            try:
                current_url = tk.h.full_current_url()
            except AttributeError:
                pass
            except RuntimeError:
                pass

            erorrs.append(
                {
                    "error": log_message,
                    "error_url": current_url if current_url else "Missing URL",
                }
            )
            redis.set(redis_key, json.dumps(erorrs))
