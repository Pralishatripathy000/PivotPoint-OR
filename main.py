from src.solvers.simplex import SimplexError, solve_simplex
from src.utils.tableau import format_tableau, format_value


def read_values(prompt, expected_count):
    values = input(prompt).split()

    if len(values) != expected_count:
        raise ValueError(
            f"Enter exactly {expected_count} values."
        )

    return values


def main():
    print("\nPivotPoint-OR")
    print("Standard Simplex Method\n")

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
            input(f"Constraint {index + 1} RHS: ")
        )

    result = solve_simplex(
        objective,
        constraints,
        rhs
    )

    for index, tableau in enumerate(result["tableaux"]):
        print(f"\nTableau {index}")
        print(
            format_tableau(
                tableau,
                variable_count,
                constraint_count
            )
        )

    print("\nOptimal Solution")

    for index, value in enumerate(result["variables"]):
        print(f"x{index + 1} = {format_value(value)}")

    print(
        f"Maximum Z = {format_value(result['objective'])}"
    )


if __name__ == "__main__":
    try:
        main()
    except (ValueError, SimplexError) as error:
        print(f"\nError: {error}")