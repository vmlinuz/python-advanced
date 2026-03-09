import unittest

from initial.homework.heads_and_legs_puzzle import solve_heads_and_legs


class TestHeadsAndLegsPuzzle(unittest.TestCase):
    def test_classic_case(self):
        self.assertEqual(solve_heads_and_legs(35, 94), (23, 12))

    def test_no_solution(self):
        self.assertEqual(solve_heads_and_legs(10, 25), (-1, -1))

    def test_all_chickens(self):
        self.assertEqual(solve_heads_and_legs(10, 20), (10, 0))

    def test_all_rabbits(self):
        self.assertEqual(solve_heads_and_legs(10, 40), (0, 10))

    def test_zero_case(self):
        self.assertEqual(solve_heads_and_legs(0, 0), (0, 0))

    def test_invalid_legs(self):
        self.assertEqual(solve_heads_and_legs(5, 3), (-1, -1))
