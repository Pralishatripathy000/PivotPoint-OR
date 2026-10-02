from fractions import Fraction

from src.solvers.simplex import (
    SimplexError,
    UnboundedProblem,
    to_fraction
)


class InfeasibleProblem(SimplexError):
    pass


def normalize_constraints(constraints, signs, rhs):
    normalized_constraints = []
    normalized_signs = []
    normalized_rhs = []

    opposite_sign = {
        "<=": ">=",
        ">=": "<=",
        "=": "="
    }

    for coefficients, sign, rhs_value in zip(
        constraints,
        signs,
        rhs
    ):
        coefficients = [
            to_fraction(value)
            for value in coefficients
        ]

        rhs_value = to_fraction(rhs_value)

        if rhs_value < 0:
            coefficients = [
                -value
                for value in coefficients
            ]

            rhs_value = -rhs_value
            sign = opposite_sign[sign]

        normalized_constraints.append(coefficients)
        normalized_signs.append(sign)
        normalized_rhs.append(rhs_value)

    return (
        normalized_constraints,
        normalized_signs,
        normalized_rhs
    )


def validate_problem(objective, constraints, signs, rhs):
    variable_count = len(objective)

    if variable_count == 0:
        raise ValueError(
            "At least one decision variable is required."
        )

    if len(constraints) == 0:
        raise ValueError(
            "At least one constraint is required."
        )

    if len(constraints) != len(signs):
        raise ValueError(
            "Each constraint must have a sign."
        )

    if len(constraints) != len(rhs):
        raise ValueError(
            "Each constraint must have an RHS value."
        )

    if any(
        len(row) != variable_count
        for row in constraints
    ):
        raise ValueError(
            "Constraint dimensions do not match."
        )

    valid_signs = {"<=", ">=", "="}

    if any(sign not in valid_signs for sign in signs):
        raise ValueError(
            "Constraint signs must be <=, >= or =."
        )


def create_phase_one_tableau(
    objective,
    constraints,
    signs,
    rhs
):
    variable_count = len(objective)
    constraint_count = len(constraints)

    rows = [
        list(row)
        for row in constraints
    ]

    variable_names = [
        f"x{index + 1}"
        for index in range(variable_count)
    ]

    basis = []
    artificial_columns = []
    current_column = variable_count

    for row in rows:
        row.extend([])

    slack_count = 0
    surplus_count = 0
    artificial_count = 0

    for row_index, sign in enumerate(signs):
        for row in rows:
            row.append(Fraction(0))

        if sign == "<=":
            slack_count += 1
            variable_names.append(f"s{slack_count}")
            rows[row_index][current_column] = Fraction(1)
            basis.append(current_column)
            current_column += 1

        elif sign == ">=":
            surplus_count += 1
            variable_names.append(f"e{surplus_count}")
            rows[row_index][current_column] = Fraction(-1)
            current_column += 1

            for row in rows:
                row.append(Fraction(0))

            artificial_count += 1
            variable_names.append(f"a{artificial_count}")
            rows[row_index][current_column] = Fraction(1)
            basis.append(current_column)
            artificial_columns.append(current_column)
            current_column += 1

        else:
            artificial_count += 1
            variable_names.append(f"a{artificial_count}")
            rows[row_index][current_column] = Fraction(1)
            basis.append(current_column)
            artificial_columns.append(current_column)
            current_column += 1

    tableau = [
        rows[index] + [rhs[index]]
        for index in range(constraint_count)
    ]

    phase_one_costs = [
        Fraction(-1)
        if column in artificial_columns
        else Fraction(0)
        for column in range(current_column)
    ]

    objective_row = [
        -value
        for value in phase_one_costs
    ] + [Fraction(0)]

    for row_index, basic_column in enumerate(basis):
        basic_cost = phase_one_costs[basic_column]

        if basic_cost != 0:
            objective_row = [
                objective_row[column]
                + basic_cost * tableau[row_index][column]
                for column in range(len(objective_row))
            ]

    tableau.append(objective_row)

    return (
        tableau,
        basis,
        variable_names,
        artificial_columns
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


def run_simplex(
    tableau,
    basis,
    phase,
    max_iterations
):
    iterations = [{
        "phase": phase,
        "number": 0,
        "tableau": copy_tableau(tableau),
        "basis": basis[:],
        "pivot_column": None,
        "pivot_row": None,
        "pivot_element": None
    }]

    for iteration_number in range(
        1,
        max_iterations + 1
    ):
        objective_row = tableau[-1][:-1]

        pivot_columns = [
            column
            for column, value in enumerate(objective_row)
            if value < 0
        ]

        if not pivot_columns:
            return iterations

        pivot_column = pivot_columns[0]
        valid_ratios = []

        for row_index in range(len(tableau) - 1):
            coefficient = tableau[row_index][pivot_column]

            if coefficient > 0:
                ratio = (
                    tableau[row_index][-1]
                    / coefficient
                )

                valid_ratios.append(
                    (ratio, row_index)
                )

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

        pivot(
            tableau,
            basis,
            pivot_row,
            pivot_column
        )

        iterations.append({
            "phase": phase,
            "number": iteration_number,
            "tableau": copy_tableau(tableau),
            "basis": basis[:],
            "pivot_column": pivot_column,
            "pivot_row": pivot_row,
            "pivot_element": pivot_element
        })

    raise SimplexError(
        f"Maximum iteration limit of "
        f"{max_iterations} reached."
    )


def remove_artificial_variables(
    tableau,
    basis,
    variable_names,
    artificial_columns
):
    artificial_set = set(artificial_columns)
    redundant_rows = []

    for row_index, basic_column in enumerate(basis):
        if basic_column not in artificial_set:
            continue

        replacement_column = None

        for column in range(len(tableau[row_index]) - 1):
            if (
                column not in artificial_set
                and tableau[row_index][column] != 0
            ):
                replacement_column = column
                break

        if replacement_column is not None:
            pivot(
                tableau,
                basis,
                row_index,
                replacement_column
            )
        elif tableau[row_index][-1] == 0:
            redundant_rows.append(row_index)
        else:
            raise InfeasibleProblem(
                "The problem has no feasible solution."
            )

    for row_index in reversed(redundant_rows):
        del tableau[row_index]
        del basis[row_index]

    kept_columns = [
        column
        for column in range(len(variable_names))
        if column not in artificial_set
    ]

    column_mapping = {
        old_column: new_column
        for new_column, old_column in enumerate(kept_columns)
    }

    reduced_tableau = []

    for row in tableau[:-1]:
        reduced_tableau.append([
            row[column]
            for column in kept_columns
        ] + [row[-1]])

    reduced_names = [
        variable_names[column]
        for column in kept_columns
    ]

    reduced_basis = [
        column_mapping[column]
        for column in basis
    ]

    return (
        reduced_tableau,
        reduced_basis,
        reduced_names
    )


def create_phase_two_objective(
    tableau,
    basis,
    objective,
    variable_count
):
    column_count = len(tableau[0]) - 1

    costs = [
        to_fraction(objective[column])
        if column < variable_count
        else Fraction(0)
        for column in range(column_count)
    ]

    objective_row = [
        -value
        for value in costs
    ] + [Fraction(0)]

    for row_index, basic_column in enumerate(basis):
        basic_cost = costs[basic_column]

        if basic_cost != 0:
            objective_row = [
                objective_row[column]
                + basic_cost * tableau[row_index][column]
                for column in range(len(objective_row))
            ]

    tableau.append(objective_row)


def solve_two_phase(
    objective,
    constraints,
    signs,
    rhs,
    max_iterations=100
):
    validate_problem(
        objective,
        constraints,
        signs,
        rhs
    )

    variable_count = len(objective)

    (
        constraints,
        signs,
        rhs
    ) = normalize_constraints(
        constraints,
        signs,
        rhs
    )

    (
        tableau,
        basis,
        variable_names,
        artificial_columns
    ) = create_phase_one_tableau(
        objective,
        constraints,
        signs,
        rhs
    )

    phase_one_iterations = run_simplex(
        tableau,
        basis,
        phase=1,
        max_iterations=max_iterations
    )

    if tableau[-1][-1] != 0:
        raise InfeasibleProblem(
            "The problem has no feasible solution."
        )

    (
        tableau,
        basis,
        variable_names
    ) = remove_artificial_variables(
        tableau,
        basis,
        variable_names,
        artificial_columns
    )

    create_phase_two_objective(
        tableau,
        basis,
        objective,
        variable_count
    )

    phase_two_iterations = run_simplex(
        tableau,
        basis,
        phase=2,
        max_iterations=max_iterations
    )

    variables = [
        Fraction(0)
        for _ in range(variable_count)
    ]

    for row_index, basic_column in enumerate(basis):
        if basic_column < variable_count:
            variables[basic_column] = tableau[row_index][-1]

    return {
        "variables": variables,
        "objective": tableau[-1][-1],
        "basis": basis,
        "variable_names": variable_names,
        "phase_one_iterations": phase_one_iterations,
        "phase_two_iterations": phase_two_iterations,
        "pivot_count": (
            len(phase_one_iterations)
            + len(phase_two_iterations)
            - 2
        )
    }