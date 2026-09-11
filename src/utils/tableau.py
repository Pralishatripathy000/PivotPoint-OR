def format_value(value):
    if value.denominator == 1:
        return str(value.numerator)
    return str(value)


def format_tableau(tableau, variable_count, constraint_count):
    headers = (
        [f"x{i + 1}" for i in range(variable_count)]
        + [f"s{i + 1}" for i in range(constraint_count)]
        + ["RHS"]
    )

    rows = [
        [format_value(value) for value in row]
        for row in tableau
    ]

    widths = [
        max(len(headers[column]), *[
            len(row[column]) for row in rows
        ])
        for column in range(len(headers))
    ]

    header_line = " | ".join(
        headers[column].rjust(widths[column])
        for column in range(len(headers))
    )

    separator = "-+-".join(
        "-" * width for width in widths
    )

    body = [
        " | ".join(
            row[column].rjust(widths[column])
            for column in range(len(headers))
        )
        for row in rows
    ]

    return "\n".join([header_line, separator, *body])