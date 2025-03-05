# Copyright (c) Siemens AG 2019-2024 ALL RIGHTS RESERVED
import unittest
from dataclasses import FrozenInstanceError

from sortedcontainers import SortedSet

from standardbom.immutable import ImmutableList


class ImmutableListTestCase(unittest.TestCase):
    def test_empty(self):
        il = ImmutableList()
        self.assertEqual(il, ())
        self.assertEqual(len(il), 0)

    def test_init_with_items(self):
        il = ImmutableList(1, 2, 3, 4, 5)
        self.assertEqual(il, (1, 2, 3, 4, 5))
        self.assertEqual(len(il), 5)

    def test_init_with_list(self):
        simple_list = (1, 2, 3, 4, 5, 6)
        il = ImmutableList(simple_list)
        self.assertEqual(il, simple_list)
        self.assertEqual(len(il), len(simple_list))

    def test_iterate_items(self):
        il = ImmutableList(1, 2, 3, 4, 5)
        for i, item in enumerate(il):
            self.assertEqual(item, i + 1)

    def test_iterate_through_tuple(self):
        il = ImmutableList(1, 2, 3, 4, 5)
        self.assertEqual('12345', ''.join(str(i) for i in il))

    def test_string_output(self):
        il = ImmutableList(1, 2, 3, 4, 5)
        self.assertEqual(str(il), '(1, 2, 3, 4, 5)')

    def test_access_with_index(self):
        il = ImmutableList(1, 2, 3, 4, 5)
        self.assertEqual(il[0], 1)
        self.assertEqual(il[1], 2)
        self.assertEqual(il[2], 3)
        self.assertEqual(il[3], 4)
        self.assertEqual(il[4], 5)
        with self.assertRaises(IndexError):
            print(f'{il[5]}')

    def test_length(self):
        il = ImmutableList(1, 2, 3, 4, 5)
        self.assertEqual(len(il), 5)

    def test_contains_an_item(self):
        il = ImmutableList(1, 2, 3, 4, 5)
        self.assertTrue(1 in il)
        self.assertTrue(5 in il)
        self.assertFalse(6 in il)

    def test_hashcode(self):
        il = ImmutableList(1, 2, 3, 4, 5)
        self.assertEqual(hash(il), hash((1, 2, 3, 4, 5)))
        self.assertNotEqual(hash(il), hash((3, 4, 5)))
        self.assertNotEqual(hash(il), hash((8, 9)))

    def test_equality(self):
        il1 = ImmutableList(1, 2, 3, 4, 5)
        il2 = ImmutableList(1, 2, 3, 4, 5)
        il3 = ImmutableList(1, 2, 3, 4, 5, 6)
        il4 = ImmutableList(1, 2, 3, 4)
        self.assertEqual(il1, il2)
        self.assertNotEqual(il1, il3)
        self.assertNotEqual(il1, il4)

    def test_immutable_index(self):
        il = ImmutableList(1, 2, 3, 4, 5)
        with self.assertRaises(TypeError):
            il[0] = 10

    def test_immutable_items_attribute(self):
        il = ImmutableList(1, 2, 3, 4, 5)
        with self.assertRaises(FrozenInstanceError):
            il.__setattr__('_items', 10)

    def test_immutable_length(self):
        il = ImmutableList(1, 2, 3, 4, 5)
        with self.assertRaises(FrozenInstanceError):
            il.__setattr__('_length', 10)

    def test_map_values_from_a_tuple(self):
        tup = (1, 2, 3, 4, 5)
        mapped = map(lambda x: x + 10, tup)
        il = ImmutableList(mapped)
        self.assertEqual(il, (11, 12, 13, 14, 15))

    def test_map_values_from_a_list(self):
        lst = [1, 2, 3, 4, 5]
        mapped = map(lambda x: x + 10, lst)
        il = ImmutableList(mapped)
        self.assertEqual(il, (11, 12, 13, 14, 15))

    def test_map_values_from_a_set(self):
        lst = SortedSet([1, 2, 3, 4, 5])
        mapped = map(lambda x: x + 10, lst)
        il = ImmutableList(mapped)
        self.assertEqual(il, (11, 12, 13, 14, 15))


if __name__ == '__main__':
    unittest.main()
