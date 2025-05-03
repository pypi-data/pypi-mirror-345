# -*- coding: utf-8 -*-

"""
This module provides an enumeration of pre-configured cloudformation stack
context information for different stacks.
"""

from functools import cached_property

from boto_session_manager import BotoSesManager

from ..stack_ctx import StackCtx
from ..utils import to_camel
from .bsm_enum import bsm_enum


class StackCtxEnum:
    """
    Use lazy loading to create enum values.
    """

    def create(
        self,
        bsm: "BotoSesManager",
        stack_name: str,
    ):
        return StackCtx(
            construct_id=to_camel(stack_name),
            stack_name=stack_name,
            aws_account_id=bsm.aws_account_id,
            aws_region=bsm.aws_region,
            bsm=bsm,
        )

    @cached_property
    def stack1_dev(self):
        return self.create(
            stack_name="cdk-mate-stack1-dev",
            bsm=bsm_enum.dev,
        )

    @cached_property
    def stack1_test(self):
        return self.create(
            stack_name="cdk-mate-stack1-test",
            bsm=bsm_enum.test,
        )

    @cached_property
    def stack2_dev(self):
        return self.create(
            stack_name="cdk-mate-stack2-dev",
            bsm=bsm_enum.dev,
        )

    @cached_property
    def stack2_test(self):
        return self.create(
            stack_name="cdk-mate-stack2-test",
            bsm=bsm_enum.test,
        )


stack_ctx_enum = StackCtxEnum()
