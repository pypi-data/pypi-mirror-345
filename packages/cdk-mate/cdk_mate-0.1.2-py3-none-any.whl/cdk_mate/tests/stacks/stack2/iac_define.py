# -*- coding: utf-8 -*-

import aws_cdk as cdk
from constructs import Construct

from .iac_define_01_everything import Stack2Mixin


class Stack2(
    cdk.Stack,
    Stack2Mixin,
):
    def __init__(
        self,
        scope: Construct,
        id: str,
        stack_name: str,
        env: cdk.Environment,
    ):
        super().__init__(
            scope=scope,
            id=id,
            stack_name=stack_name,
            env=env,
        )
        self.create_everything()
