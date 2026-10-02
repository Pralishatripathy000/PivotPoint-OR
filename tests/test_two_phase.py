import unittest
from fractions import Fraction

from src.solvers.simplex import UnboundedProblem
from src.solvers.two_phase import (
    InfeasibleProblem,
    solve_two_phase
)


class TestTwoPhaseSimplex(unittest.TestCase):
    def test_mixed_constraints(self):
        result = solve_two_phase(
            objective=[3, 2],
            constraints=[
                [1, 1],
                [1, 2],
                [1, 0]
            ],
            signs=[">=", "<=", "<="],
            rhs=[2, 6, 4]
        )

        self.assertEqual(
            result["variables"],
            [Fraction(4), Fraction(1)]
        )

        self.assertEqual(
            result["objective"],
            Fraction(14)
        )

    def test_equality_constraint(self):
        result = solve_two_phase(
            objective=[1, 1],
            constraints=[
                [1, 1],
                [1, 0]
            ],
            signs=["=", "<="],
            rhs=[5, 4]
        )

        self.assertEqual(
            result["objective"],
            Fraction(5)
        )

        self.assertEqual(
            sum(result["variables"]),
            Fraction(5)
        )

    def test_negative_rhs_normalization(self):
        result = solve_two_phase(
            objective=[1],
            constraints=[
                [-1],
                [1]
            ],
            signs=["<=", "<="],
            rhs=[-2, 5]
        )

        self.assertEqual(
            result["variables"],
            [Fraction(5)]
        )

        self.assertEqual(
            result["objective"],
            Fraction(5)
        )

    def test_infeasible_problem(self):
        with self.assertRaises(InfeasibleProblem):
            solve_two_phase(
                objective=[1],
                constraints=[
                    [1],
                    [1]
                ],
                signs=[">=", "<="],
                rhs=[5, 3]
            )

    def test_unbounded_problem(self):
        with self.assertRaises(UnboundedProblem):
            solve_two_phase(
                objective=[1],
                constraints=[[1]],
                signs=[">="],
                rhs=[1]
            )


if __name__ == "__main__":
    unittest.main()