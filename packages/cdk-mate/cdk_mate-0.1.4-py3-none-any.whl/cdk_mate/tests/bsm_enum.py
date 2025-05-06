# -*- coding: utf-8 -*-

"""
This module provides an enumeration of pre-configured Boto Session Manager
instances for different AWS environments and accounts.
"""

from functools import cached_property
from boto_session_manager import BotoSesManager

from .runtime import IS_CI


class BsmEnum:
    """
    Use lazy loading to create enum values.
    """
    def _get_bsm(self, profile: str) -> BotoSesManager:
        if IS_CI:
            return BotoSesManager(region_name="us-east-1")
        else:
            return BotoSesManager(profile_name=profile)

    @cached_property
    def dev(self):
        return self._get_bsm("esc_app_dev_us_east_1")

    @cached_property
    def test(self):
        return self._get_bsm("esc_app_test_us_east_1")


bsm_enum = BsmEnum()
