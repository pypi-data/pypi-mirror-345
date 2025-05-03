# -*- coding: utf-8 -*-

import aws_cdk as cdk
from constructs import Construct

from .iac_define_01_everything import Stack1Mixin


class Stack1(
    cdk.Stack,
    Stack1Mixin,
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
