import unittest

from initial.homework.binary_search import binary_search


class TestBinarySearch(unittest.TestCase):
    def test_element_found(self):
        data = [2, 5, 7, 9, 11, 17, 222]
        self.assertEqual(binary_search(data, 11), 4)

    def test_element_not_found(self):
        data = [2, 5, 7, 9, 11, 17, 222]
        self.assertEqual(binary_search(data, 12), -1)

    def test_first_element(self):
        data = [1, 3, 5, 7, 9]
        self.assertEqual(binary_search(data, 1), 0)

    def test_last_element(self):
        data = [1, 3, 5, 7, 9]
        self.assertEqual(binary_search(data, 9), 4)

    def test_empty_list(self):
        self.assertEqual(binary_search([], 10), -1)

    def test_single_element_found(self):
        self.assertEqual(binary_search([42], 42), 0)

    def test_single_element_not_found(self):
        self.assertEqual(binary_search([42], 7), -1)
