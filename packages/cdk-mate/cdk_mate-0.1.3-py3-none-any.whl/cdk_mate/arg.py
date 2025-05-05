# -*- coding: utf-8 -*-

"""
Argument manipulation utilities.
"""

import typing as T
import dataclasses


@dataclasses.dataclass(frozen=True)
class _REQUIRED:
    """
    A marker class for required arguments.
    """
    def __eq__(self, other):  # pragma: no cover
        # print(self, other) # for debug only
        return isinstance(other, _REQUIRED)


REQ = _REQUIRED()


@dataclasses.dataclass(frozen=True)
class _NOTHING:
    """
    A marker class for optional arguments.
    """
    def __eq__(self, other):  # pragma: no cover
        # print(self, other) # for debug only
        return isinstance(other, _NOTHING)


NA = _NOTHING()

T_KWARGS = T.Dict[str, T.Any]


def rm_na(**kwargs) -> T_KWARGS:
    """
    Remove NA values from kwargs.
    """
    return {
        key: value
        for key, value in kwargs.items()
        if isinstance(value, _NOTHING) is False
    }
