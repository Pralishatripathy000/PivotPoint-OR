from fractions import Fraction


class SimplexError(Exception):
    pass


class UnboundedProblem(SimplexError):
    pass


def to_fraction(value):
    return value if isinstance(value, Fraction) else Fraction(str(value))


def create_tableau(objective, constraints, rhs):
    variable_count = len(objective)
    constraint_count = len(constraints)
    tableau = []

    for i in range(constraint_count):
        slack = [
            Fraction(1 if i == j else 0)
            for j in range(constraint_count)
        ]

        row = [to_fraction(value) for value in constraints[i]]
        row.extend(slack)
        row.append(to_fraction(rhs[i]))
        tableau.append(row)

    objective_row = [-to_fraction(value) for value in objective]
    objective_row.extend([Fraction(0)] * constraint_count)
    objective_row.append(Fraction(0))
    tableau.append(objective_row)

    return tableau


def solve_simplex(objective, constraints, rhs, max_iterations=100):
    variable_count = len(objective)
    constraint_count = len(constraints)

    if not objective or not constraints:
        raise ValueError("Objective and constraints cannot be empty.")

    if len(rhs) != constraint_count:
        raise ValueError("Each constraint must have an RHS value.")

    if any(len(row) != variable_count for row in constraints):
        raise ValueError("Constraint dimensions do not match.")

    if any(to_fraction(value) < 0 for value in rhs):
        raise ValueError("RHS values must be non-negative.")

    tableau = create_tableau(objective, constraints, rhs)
    basis = [
        variable_count + i
        for i in range(constraint_count)
    ]
    history = [[row[:] for row in tableau]]

    for _ in range(max_iterations):
        objective_row = tableau[-1][:-1]

        negative_columns = [
            index
            for index, value in enumerate(objective_row)
            if value < 0
        ]

        if not negative_columns:
            solution = [Fraction(0)] * variable_count

            for row_index, variable_index in enumerate(basis):
                if variable_index < variable_count:
                    solution[variable_index] = tableau[row_index][-1]

            return {
                "variables": solution,
                "objective": tableau[-1][-1],
                "tableaux": history,
                "basis": basis
            }

        pivot_column = min(
            negative_columns,
            key=lambda index: objective_row[index]
        )

        ratios = []

        for row_index in range(constraint_count):
            coefficient = tableau[row_index][pivot_column]

            if coefficient > 0:
                ratio = tableau[row_index][-1] / coefficient
                ratios.append((ratio, row_index))

        if not ratios:
            raise UnboundedProblem("The problem is unbounded.")

        _, pivot_row = min(ratios)
        pivot_element = tableau[pivot_row][pivot_column]

        tableau[pivot_row] = [
            value / pivot_element
            for value in tableau[pivot_row]
        ]

        for row_index in range(constraint_count + 1):
            if row_index == pivot_row:
                continue

            factor = tableau[row_index][pivot_column]

            tableau[row_index] = [
                tableau[row_index][column] -
                factor * tableau[pivot_row][column]
                for column in range(len(tableau[row_index]))
            ]

        basis[pivot_row] = pivot_column
        history.append([row[:] for row in tableau])

    raise SimplexError("Maximum iteration limit reached.")