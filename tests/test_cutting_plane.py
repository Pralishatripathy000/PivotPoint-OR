import unittest
from fractions import Fraction

from src.solvers.cutting_plane import (
    solve_cutting_plane
)


class TestCuttingPlane(unittest.TestCase):
    def test_fractional_relaxation(self):
        result = solve_cutting_plane(
            objective=[1, 1],
            constraints=[
                [2, 1],
                [1, 2]
            ],
            rhs=[4, 4]
        )

        self.assertEqual(
            result["objective"],
            Fraction(2)
        )

        self.assertTrue(
            all(
                value.denominator == 1
                for value in result["variables"]
            )
        )

        self.assertGreater(
            result["cut_count"],
            0
        )

    def test_existing_integer_solution(self):
        result = solve_cutting_plane(
            objective=[3, 2],
            constraints=[
                [1, 1],
                [1, 0],
                [0, 1]
            ],
            rhs=[4, 2, 3]
        )

        self.assertEqual(
            result["variables"],
            [Fraction(2), Fraction(2)]
        )

        self.assertEqual(
            result["objective"],
            Fraction(10)
        )

        self.assertEqual(
            result["cut_count"],
            0
        )

    def test_single_variable_problem(self):
        result = solve_cutting_plane(
            objective=[1],
            constraints=[[2]],
            rhs=[5]
        )

        self.assertEqual(
            result["variables"],
            [Fraction(2)]
        )

        self.assertEqual(
            result["objective"],
            Fraction(2)
        )

        self.assertGreater(
            result["cut_count"],
            0
        )

    def test_rejects_fractional_input(self):
        with self.assertRaises(ValueError):
            solve_cutting_plane(
                objective=["1/2"],
                constraints=[[1]],
                rhs=[5]
            )


if __name__ == "__main__":
    unittest.main()