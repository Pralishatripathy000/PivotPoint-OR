from src.solvers.simplex import to_fraction
from src.solvers.two_phase import solve_two_phase


def solve_linear_program(
    objective,
    constraints,
    signs,
    rhs,
    direction="max",
    max_iterations=100
):
    direction = direction.lower().strip()

    if direction not in {"max", "min"}:
        raise ValueError(
            "Direction must be either max or min."
        )

    transformed_objective = [
        to_fraction(value)
        for value in objective
    ]

    if direction == "min":
        transformed_objective = [
            -value
            for value in transformed_objective
        ]

    result = solve_two_phase(
        transformed_objective,
        constraints,
        signs,
        rhs,
        max_iterations
    )

    if direction == "min":
        result["objective"] = -result["objective"]

    result["direction"] = direction

    return result