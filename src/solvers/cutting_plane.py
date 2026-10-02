from fractions import Fraction
from math import floor

from src.solvers.simplex import (
    SimplexError,
    solve_simplex,
    to_fraction
)


class CuttingPlaneError(SimplexError):
    pass


class IntegerInfeasibleProblem(CuttingPlaneError):
    pass


def fractional_part(value):
    value = to_fraction(value)
    return value - floor(value)


def validate_integer_problem(
    objective,
    constraints,
    rhs
):
    values = list(objective) + list(rhs)

    for row in constraints:
        values.extend(row)

    if any(
        to_fraction(value).denominator != 1
        for value in values
    ):
        raise ValueError(
            "Pure integer cutting-plane input must "
            "contain integer coefficients and RHS values."
        )


def copy_tableau(tableau):
    return [
        row[:]
        for row in tableau
    ]


def pivot(tableau, basis, pivot_row, pivot_column):
    pivot_element = tableau[pivot_row][pivot_column]

    tableau[pivot_row] = [
        value / pivot_element
        for value in tableau[pivot_row]
    ]

    for row_index in range(len(tableau)):
        if row_index == pivot_row:
            continue

        factor = tableau[row_index][pivot_column]

        tableau[row_index] = [
            tableau[row_index][column]
            - factor * tableau[pivot_row][column]
            for column in range(len(tableau[row_index]))
        ]

    basis[pivot_row] = pivot_column

    return pivot_element


def run_dual_simplex(
    tableau,
    basis,
    cut_number,
    max_iterations
):
    iterations = []

    for iteration_number in range(
        1,
        max_iterations + 1
    ):
        negative_rows = [
            row_index
            for row_index in range(len(tableau) - 1)
            if tableau[row_index][-1] < 0
        ]

        if not negative_rows:
            return iterations

        pivot_row = min(
            negative_rows,
            key=lambda row_index: (
                tableau[row_index][-1],
                row_index
            )
        )

        candidates = []

        for column in range(len(tableau[0]) - 1):
            coefficient = tableau[pivot_row][column]

            if coefficient < 0:
                ratio = (
                    tableau[-1][column]
                    / -coefficient
                )

                candidates.append(
                    (ratio, column)
                )

        if not candidates:
            raise IntegerInfeasibleProblem(
                "The integer problem has no feasible solution."
            )

        _, pivot_column = min(
            candidates,
            key=lambda item: (
                item[0],
                item[1]
            )
        )

        pivot_element = pivot(
            tableau,
            basis,
            pivot_row,
            pivot_column
        )

        iterations.append({
            "cut_number": cut_number,
            "number": iteration_number,
            "tableau": copy_tableau(tableau),
            "basis": basis[:],
            "pivot_column": pivot_column,
            "pivot_row": pivot_row,
            "pivot_element": pivot_element
        })

    raise CuttingPlaneError(
        "Dual Simplex iteration limit reached."
    )


def extract_variables(
    tableau,
    basis,
    variable_count
):
    variables = [
        Fraction(0)
        for _ in range(variable_count)
    ]

    for row_index, basic_column in enumerate(basis):
        if basic_column < variable_count:
            variables[basic_column] = (
                tableau[row_index][-1]
            )

    return variables


def choose_fractional_row(tableau):
    candidates = []

    for row_index in range(len(tableau) - 1):
        fraction = fractional_part(
            tableau[row_index][-1]
        )

        if fraction != 0:
            candidates.append(
                (fraction, row_index)
            )

    if not candidates:
        return None

    _, row_index = max(
        candidates,
        key=lambda item: (
            item[0],
            -item[1]
        )
    )

    return row_index


def add_gomory_cut(
    tableau,
    basis,
    variable_names,
    source_row,
    cut_number
):
    source = tableau[source_row][:]
    coefficient_count = len(source) - 1

    for row in tableau:
        row.insert(-1, Fraction(0))

    cut_coefficients = [
        -fractional_part(source[column])
        for column in range(coefficient_count)
    ]

    cut_rhs = -fractional_part(source[-1])

    cut_row = (
        cut_coefficients
        + [Fraction(1)]
        + [cut_rhs]
    )

    tableau.insert(-1, cut_row)

    new_variable_column = coefficient_count
    basis.append(new_variable_column)
    variable_names.append(f"g{cut_number}")

    return {
        "cut_number": cut_number,
        "source_row": source_row,
        "coefficients": cut_coefficients,
        "rhs": cut_rhs,
        "tableau": copy_tableau(tableau),
        "basis": basis[:]
    }


def solve_cutting_plane(
    objective,
    constraints,
    rhs,
    max_cuts=20,
    max_iterations=100
):
    validate_integer_problem(
        objective,
        constraints,
        rhs
    )

    variable_count = len(objective)
    constraint_count = len(constraints)

    relaxation = solve_simplex(
        objective,
        constraints,
        rhs,
        max_iterations
    )

    tableau = copy_tableau(
        relaxation["iterations"][-1]["tableau"]
    )

    basis = relaxation["basis"][:]

    variable_names = (
        [
            f"x{index + 1}"
            for index in range(variable_count)
        ]
        + [
            f"s{index + 1}"
            for index in range(constraint_count)
        ]
    )

    cuts = []
    dual_iterations = []

    for cut_number in range(1, max_cuts + 1):
        variables = extract_variables(
            tableau,
            basis,
            variable_count
        )

        if all(
            value.denominator == 1
            for value in variables
        ):
            return {
                "variables": variables,
                "objective": tableau[-1][-1],
                "tableau": tableau,
                "basis": basis,
                "variable_names": variable_names,
                "relaxation": relaxation,
                "cuts": cuts,
                "dual_iterations": dual_iterations,
                "cut_count": len(cuts)
            }

        source_row = choose_fractional_row(tableau)

        if source_row is None:
            raise IntegerInfeasibleProblem(
                "No valid fractional row was found."
            )

        cut = add_gomory_cut(
            tableau,
            basis,
            variable_names,
            source_row,
            cut_number
        )

        cuts.append(cut)

        iterations = run_dual_simplex(
            tableau,
            basis,
            cut_number,
            max_iterations
        )

        dual_iterations.extend(iterations)

    raise CuttingPlaneError(
        f"Maximum cut limit of {max_cuts} reached."
    )