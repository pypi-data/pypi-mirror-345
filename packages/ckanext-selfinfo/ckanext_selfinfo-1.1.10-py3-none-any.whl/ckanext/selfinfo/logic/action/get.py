from __future__ import annotations

from typing import Any


from ckan import types
import ckan.plugins.toolkit as tk
import ckan.plugins as p

import ckanext.selfinfo.utils as selfutils
from ckanext.selfinfo.interfaces import ISelfinfo
import ckanext.selfinfo.config as self_config


@tk.side_effect_free
def get_selfinfo(
    context: types.Context,
    data_dict: dict[str, Any],
) -> dict[str, Any]:

    tk.check_access("sysadmin", context, data_dict)

    limited_categories = self_config.selfinfo_get_categories()

    data = self_config.CATEGORIES

    if categories := data_dict.get("categories"):
        data = {key: data[key] for key in data if not categories or key in categories}

    data = {
        key: func()
        for key, func in data.items()
        if not limited_categories or key in limited_categories
    }

    # data modification
    for item in p.PluginImplementations(ISelfinfo):
        item.selfinfo_after_prepared(data)

    return data


def selfinfo_get_ram(
    context: types.Context,
    data_dict: dict[str, Any],
) -> dict[str, Any]:

    tk.check_access("sysadmin", context, data_dict)

    return selfutils.get_ram_usage()
