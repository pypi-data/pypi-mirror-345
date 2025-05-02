from __future__ import annotations

from typing import Any

import ckanext.selfinfo.utils as selfinfoutils


class TestUTILS:
    def test_get_python_modules_info(self):
        python_moduls_info: dict[str, Any] = selfinfoutils.get_python_modules_info()

        assert type(python_moduls_info) == dict

        assert len(python_moduls_info.keys()) == 3

    def test_get_lib_data(self):
        lib_data: dict[str, Any] | None = selfinfoutils.get_lib_data("ckan")

        assert type(lib_data) == dict

        assert lib_data["info"]["name"] == "ckan"

    def test_get_lib_latest_version(self):
        lib_data_latest_version: str | None = selfinfoutils.get_lib_latest_version(
            "ckan"
        )

        assert type(lib_data_latest_version) == str

    def test_get_ram_usage(self):
        ram_usage: dict[str, Any] = selfinfoutils.get_ram_usage()

        assert type(ram_usage) == dict

        assert len(ram_usage.keys()) == 2

    def test_get_platform_info(self):
        platform_info: dict[str, Any] = selfinfoutils.get_platform_info()

        assert type(platform_info) == dict

        assert len(platform_info.keys()) == 2
