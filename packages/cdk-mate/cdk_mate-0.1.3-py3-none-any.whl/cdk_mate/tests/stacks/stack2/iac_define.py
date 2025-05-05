# -*- coding: utf-8 -*-

import dataclasses

import aws_cdk as cdk
from cdk_mate.api import BaseStack, StackParams, REQ

from .iac_define_01_everything import Stack2Mixin


@dataclasses.dataclass
class Stack2Params(StackParams):
    project_name: str = dataclasses.field(default=REQ)
    env_name: str = dataclasses.field(default=REQ)


class Stack2(
    BaseStack,
    Stack2Mixin,
):
    def __init__(
        self,
        params: Stack2Params,
    ):
        super().__init__(params=params)
        self.params = params
        self.create_everything()
        cdk.Tags.of(self).add("tech:project_name", self.params.project_name)
        cdk.Tags.of(self).add("tech:env_name", self.params.env_name)
