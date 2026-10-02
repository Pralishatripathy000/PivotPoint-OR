from fractions import Fraction


class SimplexError(Exception):
    pass


class UnboundedProblem(SimplexError):
    pass


def to_fraction(value):
    if isinstance(value, Fraction):
        return value

    return Fraction(str(value))


def validate_problem(objective, constraints, rhs):
    variable_count = len(objective)
    constraint_count = len(constraints)

    if variable_count == 0:
        raise ValueError("At least one decision variable is required.")

    if constraint_count == 0:
        raise ValueError("At least one constraint is required.")

    if len(rhs) != constraint_count:
        raise ValueError("Each constraint must have an RHS value.")

    if any(
        len(row) != variable_count
        for row in constraints
    ):
        raise ValueError("Constraint dimensions do not match.")

    if any(to_fraction(value) < 0 for value in rhs):
        raise ValueError("RHS values must be non-negative.")


def create_tableau(objective, constraints, rhs):
    variable_count = len(objective)
    constraint_count = len(constraints)
    tableau = []

    for row_index in range(constraint_count):
        row = [
            to_fraction(value)
            for value in constraints[row_index]
        ]

        slack_variables = [
            Fraction(1 if row_index == column else 0)
            for column in range(constraint_count)
        ]

        row.extend(slack_variables)
        row.append(to_fraction(rhs[row_index]))
        tableau.append(row)

    objective_row = [
        -to_fraction(value)
        for value in objective
    ]

    objective_row.extend(
        [Fraction(0)] * constraint_count
    )
    objective_row.append(Fraction(0))
    tableau.append(objective_row)

    return tableau


def copy_tableau(tableau):
    return [row[:] for row in tableau]


def solve_simplex(
    objective,
    constraints,
    rhs,
    max_iterations=100
):
    validate_problem(objective, constraints, rhs)

    variable_count = len(objective)
    constraint_count = len(constraints)

    tableau = create_tableau(
        objective,
        constraints,
        rhs
    )

    basis = [
        variable_count + index
        for index in range(constraint_count)
    ]

    iterations = [{
        "number": 0,
        "tableau": copy_tableau(tableau),
        "basis": basis[:],
        "pivot_column": None,
        "pivot_row": None,
        "pivot_element": None,
        "ratios": None,
        "entering_variable": None,
        "leaving_variable": None
    }]

    for iteration_number in range(
        1,
        max_iterations + 1
    ):
        objective_row = tableau[-1][:-1]

        negative_columns = [
            column
            for column, value in enumerate(objective_row)
            if value < 0
        ]

        if not negative_columns:
            variables = [
                Fraction(0)
                for _ in range(variable_count)
            ]

            for row_index, variable_index in enumerate(basis):
                if variable_index < variable_count:
                    variables[variable_index] = (
                        tableau[row_index][-1]
                    )

            return {
                "variables": variables,
                "objective": tableau[-1][-1],
                "iterations": iterations,
                "basis": basis,
                "pivot_count": iteration_number - 1
            }

        pivot_column = min(
            negative_columns,
            key=lambda column: (
                objective_row[column],
                column
            )
        )

        ratios = []
        valid_ratios = []

        for row_index in range(constraint_count):
            coefficient = tableau[row_index][pivot_column]

            if coefficient > 0:
                ratio = (
                    tableau[row_index][-1]
                    / coefficient
                )
                ratios.append(ratio)
                valid_ratios.append((ratio, row_index))
            else:
                ratios.append(None)

        if not valid_ratios:
            raise UnboundedProblem(
                "The objective function is unbounded."
            )

        _, pivot_row = min(
            valid_ratios,
            key=lambda item: (
                item[0],
                item[1]
            )
        )

        pivot_element = tableau[pivot_row][pivot_column]
        leaving_variable = basis[pivot_row]

        tableau[pivot_row] = [
            value / pivot_element
            for value in tableau[pivot_row]
        ]

        for row_index in range(constraint_count + 1):
            if row_index == pivot_row:
                continue

            factor = tableau[row_index][pivot_column]

            tableau[row_index] = [
                tableau[row_index][column]
                - factor * tableau[pivot_row][column]
                for column in range(len(tableau[row_index]))
            ]

        basis[pivot_row] = pivot_column

        iterations.append({
            "number": iteration_number,
            "tableau": copy_tableau(tableau),
            "basis": basis[:],
            "pivot_column": pivot_column,
            "pivot_row": pivot_row,
            "pivot_element": pivot_element,
            "ratios": ratios,
            "entering_variable": pivot_column,
            "leaving_variable": leaving_variable
        })

    raise SimplexError(
        f"Maximum iteration limit of {max_iterations} reached."
    )