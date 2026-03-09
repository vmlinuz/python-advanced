import unittest

from initial.homework.even_squares import even_squares


class TestEvenSquares(unittest.TestCase):
    def test_basic_case(self):
        self.assertEqual(even_squares([1, 2, 3, 4, 5, 6]), [4, 16, 36])

    def test_empty_list(self):
        self.assertEqual(even_squares([]), [])

    def test_no_even_numbers(self):
        self.assertEqual(even_squares([1, 3, 5, 7]), [])

    def test_all_even_numbers(self):
        self.assertEqual(even_squares([2, 4, 6]), [4, 16, 36])

    def test_single_element_even(self):
        self.assertEqual(even_squares([8]), [64])

    def test_single_element_odd(self):
        self.assertEqual(even_squares([7]), [])
