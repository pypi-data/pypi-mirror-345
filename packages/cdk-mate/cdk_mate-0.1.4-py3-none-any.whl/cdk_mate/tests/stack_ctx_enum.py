# -*- coding: utf-8 -*-

"""
This module provides an enumeration of pre-configured cloudformation stack
context information for different stacks.
"""

from functools import cached_property

from ..stack_ctx import StackCtx
from .bsm_enum import bsm_enum


class StackCtxEnum:
    """
    Use lazy loading to create enum values.
    """
    @cached_property
    def stack1_dev(self):
        return StackCtx.new(
            stack_name="cdk-mate-stack1-dev",
            bsm=bsm_enum.dev,
        )

    @cached_property
    def stack1_test(self):
        return StackCtx.new(
            stack_name="cdk-mate-stack1-test",
            bsm=bsm_enum.test,
        )

    @cached_property
    def stack2_dev(self):
        return StackCtx.new(
            stack_name="cdk-mate-stack2-dev",
            bsm=bsm_enum.dev,
        )

    @cached_property
    def stack2_test(self):
        return StackCtx.new(
            stack_name="cdk-mate-stack2-test",
            bsm=bsm_enum.test,
        )


stack_ctx_enum = StackCtxEnum()
