# -*- coding: utf-8 -*-

import typing as T


if T.TYPE_CHECKING:  # pragma: no cover
    from .iac_define import Stack1


class Stack1Mixin:
    def create_everything(self: "Stack1"):
        pass
