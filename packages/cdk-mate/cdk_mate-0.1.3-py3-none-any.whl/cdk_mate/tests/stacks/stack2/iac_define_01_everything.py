# -*- coding: utf-8 -*-

import typing as T


if T.TYPE_CHECKING:  # pragma: no cover
    from .iac_define import Stack2


class Stack2Mixin:
    def create_everything(self: "Stack2"):
        pass
