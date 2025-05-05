# -*- coding: utf-8 -*-

"""
Stack Management Module for AWS CDK
"""

import aws_cdk as cdk

from .stack_params import StackParams


class BaseStack(cdk.Stack):
    """
    Base class for AWS CDK stacks using the cdk_mate parameter system.

    This class extends the standard cdk.Stack class with parameter management
    capabilities, enabling a more structured and type-safe approach to stack
    configuration. It serves as the foundation for all CDK stacks in the project,
    providing consistency in initialization and access to stack parameters.

    :param params: Parameters for stack initialization, must be an instance
        of :class:`~cdk_mate.stack_params.StackParams` or a subclass

    Example: create a subclass of BaseStack and pass your custom stack parameters:

    .. code-block:: python

        import dataclasses
        import aws_cdk as cdk
        from cdk_mate.api import BaseStack, StackParams, REQ

        @dataclasses.dataclass
        class MyStackParams(StackParams):
            project_name: str = dataclasses.field(default=REQ)
            env_name: str = dataclasses.field(default=REQ)

        class MyStack(BaseStack):
            def __init__(
                self,
                params: MyStackParams,
            ):
                super().__init__(params=params)
                self.params = params
                cdk.Tags.of(self).add("tech:project_name", self.params.project_name)
                cdk.Tags.of(self).add("tech:env_name", self.params.env_name)
    """
    def __init__(
        self,
        params: StackParams,
    ):
        super().__init__(**params.to_stack_kwargs())
        self.params = params
