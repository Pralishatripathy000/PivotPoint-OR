import unittest
from fractions import Fraction

from src.solvers.simplex import (
    UnboundedProblem,
    solve_simplex
)


class TestSimplex(unittest.TestCase):

    def test_standard_problem(self):
        result = solve_simplex(
            [3, 5],
            [
                [1, 0],
                [0, 2],
                [3, 2]
            ],
            [4, 12, 18]
        )

        self.assertEqual(
            result["variables"],
            [Fraction(2), Fraction(6)]
        )

        self.assertEqual(
            result["objective"],
            Fraction(36)
        )

        self.assertEqual(
            result["pivot_count"],
            2
        )

    def test_fractional_solution(self):
        result = solve_simplex(
            [1, 1],
            [
                [2, 1],
                [1, 2]
            ],
            [4, 4]
        )

        self.assertEqual(
            result["variables"],
            [
                Fraction(4, 3),
                Fraction(4, 3)
            ]
        )

        self.assertEqual(
            result["objective"],
            Fraction(8, 3)
        )

    def test_unbounded_problem(self):
        with self.assertRaises(UnboundedProblem):
            solve_simplex(
                [1, 1],
                [[1, -1]],
                [1]
            )

    def test_negative_rhs_rejected(self):
        with self.assertRaises(ValueError):
            solve_simplex(
                [2, 1],
                [[1, 1]],
                [-5]
            )


if __name__ == "__main__":
    unittest.main()