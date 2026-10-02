def format_value(value):
    if value is None:
        return "—"

    if value.denominator == 1:
        return str(value.numerator)

    return str(value)


def get_variable_names(variable_count, constraint_count):
    decision_variables = [
        f"x{index + 1}"
        for index in range(variable_count)
    ]

    slack_variables = [
        f"s{index + 1}"
        for index in range(constraint_count)
    ]

    return decision_variables + slack_variables


def format_tableau(
    tableau,
    basis,
    variable_count,
    constraint_count
):
    variable_names = get_variable_names(
        variable_count,
        constraint_count
    )

    headers = ["Basis", *variable_names, "RHS"]

    rows = []

    for row_index, row in enumerate(tableau):
        if row_index < constraint_count:
            basis_name = variable_names[basis[row_index]]
        else:
            basis_name = "Z"

        rows.append([
            basis_name,
            *[format_value(value) for value in row]
        ])

    widths = [
        max(
            len(headers[column]),
            max(len(row[column]) for row in rows)
        )
        for column in range(len(headers))
    ]

    header_line = " | ".join(
        headers[column].rjust(widths[column])
        for column in range(len(headers))
    )

    separator = "-+-".join(
        "-" * width
        for width in widths
    )

    body = [
        " | ".join(
            row[column].rjust(widths[column])
            for column in range(len(headers))
        )
        for row in rows
    ]

    return "\n".join([
        header_line,
        separator,
        *body
    ])