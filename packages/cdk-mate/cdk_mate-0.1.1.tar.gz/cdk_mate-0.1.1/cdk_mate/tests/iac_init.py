# -*- coding: utf-8 -*-

"""
Stack Initialization for Multi-Account AWS CDK Deployment
"""

import dataclasses
from functools import cached_property

import aws_cdk as cdk

from .stacks.stack1.iac_define import Stack1
from .stacks.stack2.iac_define import Stack2

from .stack_ctx_enum import stack_ctx_enum


@dataclasses.dataclass
class StackEnum:
    """
    Enumeration of CDK stacks for different environments.
    """

    app: cdk.App = dataclasses.field()

    @cached_property
    def stack1_dev(self):
        return Stack1(
            scope=self.app,
            **stack_ctx_enum.stack1_dev.to_stack_kwargs(),
        )

    @cached_property
    def stack1_test(self):
        return Stack1(
            scope=self.app,
            **stack_ctx_enum.stack1_test.to_stack_kwargs(),
        )

    @cached_property
    def stack2_dev(self):
        return Stack2(
            scope=self.app,
            **stack_ctx_enum.stack2_dev.to_stack_kwargs(),
        )

    @cached_property
    def stack2_test(self):
        return Stack2(
            scope=self.app,
            **stack_ctx_enum.stack2_test.to_stack_kwargs(),
        )


# Create the global stack enumeration instance
app = cdk.App()

stack_enum = StackEnum(app=app)
