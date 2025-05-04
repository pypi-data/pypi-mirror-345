from __future__ import annotations

from typing import Literal

import ckan.plugins.toolkit as tk
import ckanext.selfinfo.utils as selfutils


CATEGORIES = {
    "python_modules": selfutils.get_python_modules_info,
    "platform_info": selfutils.get_platform_info,
    "ram_usage": selfutils.get_ram_usage,
    "disk_usage": selfutils.get_disk_usage,
    "git_info": selfutils.gather_git_info,
    "freeze": selfutils.get_freeze,
    "errors": selfutils.retrieve_errors,
    "actions": selfutils.ckan_actions,
    "auth_actions": selfutils.ckan_auth_actions,
    "blueprints": selfutils.ckan_bluprints,
    "helpers": selfutils.ckan_helpers,
    "status_show": selfutils.get_status_show,
    "ckan_queues": selfutils.get_ckan_queues,
    "ckan_solr_schema": selfutils.get_solr_schema,
    "ckan_cli_commands": selfutils.get_ckan_registered_cli,
}

SELLFINFO_SET_URL = "ckan.selfinfo.page_url"
SELLFINFO_DEFAULT_URL = "/ckan-admin/selfinfo"
SELLFINFO_SET_MAIN_ACTION_NAME = "ckan.selfinfo.main_action_name"
SELFINFO_REDIS_PREFIX = "ckan.selfinfo.redis_prefix_key"
SELFINFO_ERRORS_LIMIT = "ckan.selfinfo.errors_limit"
SELFINFO_REPOS_PATH = "ckan.selfinfo.ckan_repos_path"
SELFINFO_REPOS = "ckan.selfinfo.ckan_repos"
SELFINFO_PARTITIONS_PATH = "ckan.selfinfo.partitions"
SELFINFO_DUPLICATED_ENVS_MODE = "ckan.selfinfo.duplicated_envs.mode"
SELFINFO_DUPLICATED_ENVS_SHARED_CATEGORIES = (
    "ckan.selfinfo.duplicated_envs.shared_categories"
)
SELFINFO_REDIS_SUFFIX: Literal["_selfinfo"] = "_selfinfo"
SELFINFO_CATEGORIES_LIST = "ckan.selfinfo.categories_list"
SELFINFO_ADDITIONAL_PROFILES_USING_REDIS_KEYS = (
    "ckan.selfinfo.additional_profiles_using_redis_keys"
)
SELFINFO_SOLR_SCHEMA_FILENAME = "ckan.selfinfo.solr_schema_filename"
STORE_TIME: float = 604800.0  # one week
# STORE_TIME: float = 1.0
PYPI_URL: Literal["https://pypi.org/pypi/"] = "https://pypi.org/pypi/"


def selfinfo_get_path():
    return tk.config.get(SELLFINFO_SET_URL, SELLFINFO_DEFAULT_URL)


def selfinfo_get_main_action_name():
    return tk.config.get(SELLFINFO_SET_MAIN_ACTION_NAME)


def selfinfo_get_redis_prefix():
    prefix = tk.config.get(SELFINFO_REDIS_PREFIX)
    return prefix + "_" if prefix else prefix


def selfinfo_get_errors_limit():
    return tk.config.get(SELFINFO_ERRORS_LIMIT)


def selfinfo_get_repos_path():
    return tk.config.get(SELFINFO_REPOS_PATH)


def selfinfo_get_repos():
    return tk.config.get(SELFINFO_REPOS, "")


def selfinfo_get_partitions():
    return tk.config.get(SELFINFO_PARTITIONS_PATH)


def selfinfo_get_categories():
    return tk.config.get(SELFINFO_CATEGORIES_LIST)


def selfinfo_get_additional_redis_keys():
    return tk.config.get(SELFINFO_ADDITIONAL_PROFILES_USING_REDIS_KEYS)


def selfinfo_get_dulicated_envs_mode():
    return tk.config.get(SELFINFO_DUPLICATED_ENVS_MODE)


def selfinfo_get_dulicated_envs_shared_categories():
    return tk.config.get(SELFINFO_DUPLICATED_ENVS_SHARED_CATEGORIES)


def selfinfo_get_solr_schema_filename():
    return tk.config.get(SELFINFO_SOLR_SCHEMA_FILENAME)
