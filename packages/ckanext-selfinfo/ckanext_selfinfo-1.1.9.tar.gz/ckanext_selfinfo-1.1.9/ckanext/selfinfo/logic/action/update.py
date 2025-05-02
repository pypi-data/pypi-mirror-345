from __future__ import annotations

from typing import Any, Mapping
from datetime import datetime
import importlib_metadata as imetadata

from ckan import types
from ckan.lib.redis import connect_to_redis, Redis
import ckan.plugins.toolkit as tk

import ckanext.selfinfo.utils as selfutils
import ckanext.selfinfo.config as self_config


def update_last_module_check(
    context: types.Context,
    data_dict: dict[str, Any],
) -> dict[str, Any]:
    module = data_dict.get("module", "")

    tk.check_access("sysadmin", context, data_dict)

    if module:
        redis: Redis = connect_to_redis()

        redis_key: str = module + self_config.SELFINFO_REDIS_SUFFIX
        now: float = datetime.utcnow().timestamp()

        data: Mapping[str, Any] = {
            "name": module,
            "current_version": imetadata.version(module),
            "updated": now,
            "latest_version": selfutils.get_lib_latest_version(module),
        }

        for key in data:
            if data[key] != redis.hget(redis_key, key):
                redis.hset(redis_key, key=key, value=data[key])

        result: dict[str, Any] = {
            k.decode("utf-8"): v.decode("utf-8")
            for k, v in redis.hgetall(redis_key).items()
        }

        result["updated"] = datetime.fromtimestamp(float(result["updated"]))

        return result
    return {}
