import unittest
from fractions import Fraction

from src.solvers.linear_program import solve_linear_program


class TestLinearProgram(unittest.TestCase):
    def test_maximization(self):
        result = solve_linear_program(
            objective=[3, 2],
            constraints=[
                [1, 1],
                [1, 2],
                [1, 0]
            ],
            signs=[">=", "<=", "<="],
            rhs=[2, 6, 4],
            direction="max"
        )

        self.assertEqual(
            result["variables"],
            [Fraction(4), Fraction(1)]
        )

        self.assertEqual(
            result["objective"],
            Fraction(14)
        )

    def test_minimization(self):
        result = solve_linear_program(
            objective=[1, 1],
            constraints=[
                [1, 2],
                [2, 1]
            ],
            signs=[">=", ">="],
            rhs=[4, 4],
            direction="min"
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

    def test_fractional_coefficients(self):
        result = solve_linear_program(
            objective=["1/2", "1"],
            constraints=[
                [1, 1]
            ],
            signs=[">="],
            rhs=[2],
            direction="min"
        )

        self.assertEqual(
            result["variables"],
            [Fraction(2), Fraction(0)]
        )

        self.assertEqual(
            result["objective"],
            Fraction(1)
        )

    def test_invalid_direction(self):
        with self.assertRaises(ValueError):
            solve_linear_program(
                objective=[1],
                constraints=[[1]],
                signs=["<="],
                rhs=[5],
                direction="minimum"
            )


if __name__ == "__main__":
    unittest.main()