#
# Copyright (c) Siemens AG 2019-2024 ALL RIGHTS RESERVED
# SPDX-License-Identifier: MIT
#
from dataclasses import dataclass
from typing import Iterable, TypeVar, Generic, Union, Tuple, Any, Iterator

T = TypeVar('T')


@dataclass(frozen=True)
class ImmutableList(Generic[T], Iterable[T]):
    _items: Tuple[T, ...]

    def __init__(self, *args: Union[T, Iterable[T]]) -> None:
        if len(args) == 1 and isinstance(args[0], Iterable):
            items = tuple(args[0])
        else:
            items = args
        object.__setattr__(self, '_items', items)

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, index: int) -> T:
        return self._items[index]

    def __iter__(self) -> Iterator[T]:
        return iter(self._items)

    def __str__(self) -> str:
        return str(self._items)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, ImmutableList):
            return self._items == other._items
        eq: bool = self._items == other
        return eq

    def __hash__(self) -> int:
        return hash(self._items)
