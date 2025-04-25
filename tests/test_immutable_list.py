# Copyright (c) Siemens AG 2019-2025 ALL RIGHTS RESERVED
# SPDX-License-Identifier: MIT
import unittest
from dataclasses import FrozenInstanceError

from sortedcontainers import SortedSet

from siemens_standard_bom.immutable import ImmutableList


class ImmutableListTestCase(unittest.TestCase):
    def test_empty(self) -> None:
        il = ImmutableList[int]()
        self.assertEqual(il, ())
        self.assertEqual(len(il), 0)

    def test_init_with_items(self) -> None:
        il = ImmutableList(1, 2, 3, 4, 5)
        self.assertEqual(il, (1, 2, 3, 4, 5))
        self.assertEqual(len(il), 5)

    def test_init_with_list(self) -> None:
        simple_list = (1, 2, 3, 4, 5, 6)
        il = ImmutableList[int](simple_list)
        self.assertEqual(il, simple_list)
        self.assertEqual(len(il), len(simple_list))

    def test_iterate_items(self) -> None:
        il = ImmutableList(1, 2, 3, 4, 5)
        for i, item in enumerate(il):
            self.assertEqual(item, i + 1)

    def test_iterate_through_tuple(self) -> None:
        il = ImmutableList(1, 2, 3, 4, 5)
        self.assertEqual('12345', ''.join(str(i) for i in il))

    def test_string_output(self) -> None:
        il = ImmutableList(1, 2, 3, 4, 5)
        self.assertEqual(str(il), '(1, 2, 3, 4, 5)')

    def test_access_with_index(self) -> None:
        il = ImmutableList(1, 2, 3, 4, 5)
        self.assertEqual(il[0], 1)
        self.assertEqual(il[1], 2)
        self.assertEqual(il[2], 3)
        self.assertEqual(il[3], 4)
        self.assertEqual(il[4], 5)
        with self.assertRaises(IndexError):
            print(f'{il[5]}')

    def test_length(self) -> None:
        il = ImmutableList(1, 2, 3, 4, 5)
        self.assertEqual(len(il), 5)

    def test_contains_an_item(self) -> None:
        il = ImmutableList(1, 2, 3, 4, 5)
        self.assertTrue(1 in il)
        self.assertTrue(5 in il)
        self.assertFalse(6 in il)

    def test_hashcode(self) -> None:
        il = ImmutableList(1, 2, 3, 4, 5)
        self.assertEqual(hash(il), hash((1, 2, 3, 4, 5)))
        self.assertNotEqual(hash(il), hash((3, 4, 5)))
        self.assertNotEqual(hash(il), hash((8, 9)))

    def test_equality(self) -> None:
        il1 = ImmutableList(1, 2, 3, 4, 5)
        il2 = ImmutableList(1, 2, 3, 4, 5)
        il3 = ImmutableList(1, 2, 3, 4, 5, 6)
        il4 = ImmutableList(1, 2, 3, 4)
        self.assertEqual(il1, il2)
        self.assertNotEqual(il1, il3)
        self.assertNotEqual(il1, il4)

    def test_immutable_index(self) -> None:
        il = ImmutableList(1, 2, 3, 4, 5)
        with self.assertRaises(TypeError):
            il[0] = 10  # type: ignore[index]

    def test_immutable_items_attribute(self) -> None:
        il = ImmutableList(1, 2, 3, 4, 5)
        with self.assertRaises(FrozenInstanceError):
            il.__setattr__('_items', 10)

    def test_immutable_length(self) -> None:
        il = ImmutableList(1, 2, 3, 4, 5)
        with self.assertRaises(FrozenInstanceError):
            il.__setattr__('_length', 10)

    def test_map_values_from_a_tuple(self) -> None:
        values = (1, 2, 3, 4, 5)
        il = ImmutableList[int](map(lambda x: x + 10, values))
        self.assertEqual(il, (11, 12, 13, 14, 15))

    def test_map_values_from_a_list(self) -> None:
        values = [1, 2, 3, 4, 5]
        il = ImmutableList[int](map(lambda x: x + 10, values))
        self.assertEqual(il, (11, 12, 13, 14, 15))

    def test_map_values_from_a_set(self) -> None:
        values = SortedSet([1, 2, 3, 4, 5])
        il = ImmutableList[int](map(lambda x: x + 10, values))
        self.assertEqual(il, (11, 12, 13, 14, 15))


if __name__ == '__main__':
    unittest.main()
