from src.solvers.simplex import (
    SimplexError,
    solve_simplex
)

from src.solvers.two_phase import solve_two_phase

from src.utils.tableau import (
    format_named_tableau,
    format_value,
    get_variable_names
)


def read_positive_integer(prompt):
    value = int(input(prompt))

    if value <= 0:
        raise ValueError(
            "Enter a positive integer."
        )

    return value


def read_values(prompt, expected_count):
    values = input(prompt).split()

    if len(values) != expected_count:
        raise ValueError(
            f"Enter exactly {expected_count} values."
        )

    return values


def create_phase_one_names(variable_count, signs):
    names = [
        f"x{index + 1}"
        for index in range(variable_count)
    ]

    slack_count = 0
    surplus_count = 0
    artificial_count = 0

    for sign in signs:
        if sign == "<=":
            slack_count += 1
            names.append(f"s{slack_count}")

        elif sign == ">=":
            surplus_count += 1
            names.append(f"e{surplus_count}")

            artificial_count += 1
            names.append(f"a{artificial_count}")

        else:
            artificial_count += 1
            names.append(f"a{artificial_count}")

    return names


def display_iterations(iterations, variable_names, heading):
    print(f"\n{heading}")

    for iteration in iterations:
        print(f"\nTableau {iteration['number']}")

        if iteration["pivot_column"] is not None:
            entering = variable_names[
                iteration["pivot_column"]
            ]

            print(f"Entering variable: {entering}")
            print(
                f"Key column: "
                f"{iteration['pivot_column'] + 1}"
            )
            print(
                f"Key row: "
                f"{iteration['pivot_row'] + 1}"
            )
            print(
                "Key element: "
                f"{format_value(iteration['pivot_element'])}"
            )

        print(
            format_named_tableau(
                iteration["tableau"],
                iteration["basis"],
                variable_names
            )
        )


def read_problem(include_signs):
    variable_count = read_positive_integer(
        "Number of decision variables: "
    )

    constraint_count = read_positive_integer(
        "Number of constraints: "
    )

    objective = read_values(
        "Objective coefficients: ",
        variable_count
    )

    constraints = []
    signs = []
    rhs = []

    for index in range(constraint_count):
        constraints.append(
            read_values(
                f"Constraint {index + 1} coefficients: ",
                variable_count
            )
        )

        if include_signs:
            sign = input(
                f"Constraint {index + 1} sign "
                "(<=, >= or =): "
            ).strip()

            if sign not in {"<=", ">=", "="}:
                raise ValueError(
                    "Constraint signs must be <=, >= or =."
                )

            signs.append(sign)

        rhs.append(
            input(
                f"Constraint {index + 1} RHS: "
            ).strip()
        )

    return {
        "variable_count": variable_count,
        "constraint_count": constraint_count,
        "objective": objective,
        "constraints": constraints,
        "signs": signs,
        "rhs": rhs
    }


def run_standard_simplex():
    print("\nStandard Simplex Method")
    print(
        "Maximization with <= constraints "
        "and non-negative RHS values\n"
    )

    problem = read_problem(include_signs=False)

    result = solve_simplex(
        problem["objective"],
        problem["constraints"],
        problem["rhs"]
    )

    variable_names = get_variable_names(
        problem["variable_count"],
        problem["constraint_count"]
    )

    display_iterations(
        result["iterations"],
        variable_names,
        "Simplex Iterations"
    )

    display_solution(result)


def run_two_phase():
    print("\nTwo-Phase Simplex Method")
    print(
        "Maximization with <=, >= and = constraints\n"
    )

    problem = read_problem(include_signs=True)

    result = solve_two_phase(
        problem["objective"],
        problem["constraints"],
        problem["signs"],
        problem["rhs"]
    )

    phase_one_names = create_phase_one_names(
        problem["variable_count"],
        problem["signs"]
    )

    display_iterations(
        result["phase_one_iterations"],
        phase_one_names,
        "Phase I: Finding a Feasible Basis"
    )

    display_iterations(
        result["phase_two_iterations"],
        result["variable_names"],
        "Phase II: Optimizing the Objective"
    )

    display_solution(result)


def display_solution(result):
    print("\nOptimal Solution")

    for index, value in enumerate(result["variables"]):
        print(
            f"x{index + 1} = {format_value(value)}"
        )

    print(
        "Maximum Z = "
        f"{format_value(result['objective'])}"
    )

    print(
        f"Pivot operations = {result['pivot_count']}"
    )


def main():
    print("\nPivotPoint-OR")
    print("Because doing every pivot by hand builds character.")
    print("\n1. Standard Simplex Method")
    print("2. Two-Phase Simplex Method")

    choice = input("\nChoose a method: ").strip()

    if choice == "1":
        run_standard_simplex()
    elif choice == "2":
        run_two_phase()
    else:
        raise ValueError(
            "Choose either 1 or 2."
        )


if __name__ == "__main__":
    try:
        main()
    except (ValueError, SimplexError) as error:
        print(f"\nError: {error}")