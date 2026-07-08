#
# Copyright (c) Siemens AG 2019-2025 ALL RIGHTS RESERVED
# SPDX-License-Identifier: MIT
#
from collections.abc import Iterable
from typing import TypeVar, cast

T = TypeVar('T')


class ImmutableList(tuple[T, ...]):
    __slots__ = ()

    def __new__(cls, *args: T | Iterable[T]) -> 'ImmutableList[T]':
        if len(args) == 1 and isinstance(args[0], Iterable):
            return super().__new__(cls, args[0])
        return super().__new__(cls, cast(tuple[T, ...], args))
