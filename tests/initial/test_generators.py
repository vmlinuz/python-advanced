import unittest

from initial.homework.generators import generate_numbers


class TestGenerateNumbers(unittest.TestCase):
    def test_basic_case(self):
        self.assertEqual(list(generate_numbers(100)), [0, 35, 70])

    def test_zero(self):
        self.assertEqual(list(generate_numbers(0)), [0])

    def test_no_matches(self):
        self.assertEqual(list(generate_numbers(10)), [0])

    def test_exact_match(self):
        self.assertEqual(list(generate_numbers(35)), [0, 35])

    def test_large_number(self):
        result = list(generate_numbers(210))
        self.assertIn(210, result)
        self.assertEqual(result[-1], 210)
