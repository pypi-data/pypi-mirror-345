# -*- coding: utf-8 -*-

"""
This module provides an enumeration of pre-configured Boto Session Manager
instances for different AWS environments and accounts.
"""

from functools import cached_property
from boto_session_manager import BotoSesManager


class BsmEnum:
    """
    Use lazy loading to create enum values.
    """

    @cached_property
    def dev(self):
        return BotoSesManager(profile_name="bmt_app_dev_us_east_1")

    @cached_property
    def test(self):
        return BotoSesManager(profile_name="bmt_app_test_us_east_1")


bsm_enum = BsmEnum()
