from src.solvers.simplex import (
    SimplexError,
    solve_simplex
)

from src.utils.tableau import (
    format_tableau,
    format_value,
    get_variable_names
)


def read_values(prompt, expected_count):
    values = input(prompt).split()

    if len(values) != expected_count:
        raise ValueError(
            f"Enter exactly {expected_count} values."
        )

    return values


def display_iteration(
    iteration,
    variable_count,
    constraint_count
):
    variable_names = get_variable_names(
        variable_count,
        constraint_count
    )

    print(f"\nTableau {iteration['number']}")

    if iteration["pivot_column"] is not None:
        entering = variable_names[
            iteration["entering_variable"]
        ]

        leaving = variable_names[
            iteration["leaving_variable"]
        ]

        print(f"Entering variable: {entering}")
        print(f"Leaving variable: {leaving}")
        print(
            f"Key column: {iteration['pivot_column'] + 1}"
        )
        print(
            f"Key row: {iteration['pivot_row'] + 1}"
        )
        print(
            "Key element: "
            f"{format_value(iteration['pivot_element'])}"
        )

        formatted_ratios = [
            format_value(value)
            for value in iteration["ratios"]
        ]

        print(
            "Ratios: "
            + ", ".join(formatted_ratios)
        )

    print(
        format_tableau(
            iteration["tableau"],
            iteration["basis"],
            variable_count,
            constraint_count
        )
    )


def main():
    print("\nPivotPoint-OR")
    print("Standard Simplex Method")
    print(
        "Maximization with <= constraints "
        "and non-negative RHS values\n"
    )

    variable_count = int(
        input("Number of decision variables: ")
    )

    constraint_count = int(
        input("Number of constraints: ")
    )

    objective = read_values(
        "Objective coefficients: ",
        variable_count
    )

    constraints = []
    rhs = []

    for index in range(constraint_count):
        constraints.append(
            read_values(
                f"Constraint {index + 1} coefficients: ",
                variable_count
            )
        )

        rhs.append(
            input(
                f"Constraint {index + 1} RHS: "
            ).strip()
        )

    result = solve_simplex(
        objective,
        constraints,
        rhs
    )

    for iteration in result["iterations"]:
        display_iteration(
            iteration,
            variable_count,
            constraint_count
        )

    print("\nOptimal Solution")

    for index, value in enumerate(result["variables"]):
        print(
            f"x{index + 1} = {format_value(value)}"
        )

    print(
        f"Maximum Z = "
        f"{format_value(result['objective'])}"
    )

    print(
        f"Pivot operations = {result['pivot_count']}"
    )


if __name__ == "__main__":
    try:
        main()
    except (ValueError, SimplexError) as error:
        print(f"\nError: {error}")