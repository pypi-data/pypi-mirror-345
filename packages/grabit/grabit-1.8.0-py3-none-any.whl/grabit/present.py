from typing import List, Any, Dict, Callable, Tuple
from grabit.models import File, FileSize
import re

# ANSI colours for formatting tables
CLRS = {
    "light_green": "\033[38;5;40m",
    "dark_green": "\033[38;5;34m",
    "light_amber": "\033[38;5;220m",
    "dark_amber": "\033[38;5;178m",
    "light_red": "\033[38;5;203m",
    "dark_red": "\033[38;5;196m",
}


def colour_num(
    value: float,
    boundaries: List[Tuple[float, str]],
) -> Tuple[str, int]:
    """Using a list of size boundaries and associated colours, colours the
    given numerical value so it's an ANSI string. Returns the size of the
    string before the ANSI colouring for easier formatting"""
    value_string = str(value)
    for b in boundaries:
        if value <= b[0]:
            return (f"{b[1]}{value_string}\033[0m", len(value_string))


def get_boundaries(
    values: List[float | int],
) -> List[Tuple[float, str]]:
    """Creates boundaries based on the statistical distribution of sizes in the
    provided values."""
    # Sort the values
    values.sort()
    value_len = len(values)

    # Two files or less, just use green and red
    if value_len <= 2:
        boundaries = [
            (min(values), CLRS["light_green"]),
            (max(values), CLRS["light_red"]),
        ]

    # Less than 6 files use green amber red
    elif value_len < 6:
        boundaries = [
            (percentile(values, 0.33), CLRS["light_green"]),
            (percentile(values, 0.66), CLRS["light_amber"]),
            (max(values), CLRS["light_red"]),
        ]

    # Otherwise use all the colours
    else:
        boundaries = [
            (percentile(values, 0.1667), CLRS["dark_green"]),
            (percentile(values, 0.3333), CLRS["light_green"]),
            (percentile(values, 0.5), CLRS["light_amber"]),
            (percentile(values, 0.6667), CLRS["dark_amber"]),
            (percentile(values, 0.8333), CLRS["light_red"]),
            (max(values), CLRS["dark_red"]),
        ]

    return boundaries


def percentile(values: List[float | int], percentile: float) -> float | int:
    """Gets the point in the list closest to the given percentile.
    For example, 0.5 would be the midpoint. Will get the percentile
    of the list as is, won't sort it itself."""
    value_len = len(values)
    closest_idx = int(value_len * percentile)

    return values[closest_idx]


def format_table(
    headers: List[str],
    rows: List[List[str]],
    column_widths: List[int],
    align_right_columns: List[int] = None,
) -> str:
    """Generic table formatter that handles borders, padding and alignment."""
    if not rows:
        return "No data found"

    if align_right_columns is None:
        align_right_columns = []

    # Calculate total width including borders and padding
    total_width = sum(column_widths) + (3 * len(column_widths)) - 1

    # Create border lines
    top_bottom_border = "+" + "-" * (total_width) + "+"
    separator = "|" + "-" * (total_width) + "|"

    # Format header row
    header = "| "
    for i, (header_text, width) in enumerate(zip(headers, column_widths)):
        alignment = ">" if i in align_right_columns else "<"
        header += f"{header_text:{alignment}{width}} | "

    # Format data rows
    formatted_rows = []
    for row in rows:
        formatted_row = "| "
        for i, (cell, width) in enumerate(zip(row, column_widths)):
            alignment = ">" if i in align_right_columns else "<"

            colour_pattern = re.compile(r"\033\[(.*)m(\d+)\033\[0m")
            matches = colour_pattern.findall(cell)

            # If the cell is coloured align it differently
            if len(matches) == 1:
                match = matches[0]
                formatted_row += (
                    f"\033[{match[0]}m{match[1]:{alignment}{width}}\033[0m | "
                )
            else:
                formatted_row += f"{cell:{alignment}{width}} | "
        formatted_rows.append(formatted_row)

    # Combine all parts
    return "\n".join(
        [top_bottom_border, header, separator]
        + formatted_rows
        + [top_bottom_border]
    )


def generate_file_table(
    files: List[File],
    colour: bool = False,
) -> str:
    """Generates a formatted table showing file info including paths, sizes and git history."""
    if not files:
        return "No files found"

    # Get the data for colouring
    tokens = [f.tokens for f in files]
    boundaries = get_boundaries(tokens)

    # Get the row info for each file, coloured and uncoloured
    uncoloured_rows = []
    coloured_rows = []

    for f in files:
        if f.git_history:
            # Git history format is: hash | author | date | message
            last_commit = f.git_history.split("\n")[0].split(" | ")
            author, date = last_commit[1], last_commit[2]
        else:
            author, date = "Unknown", "Unknown"

        uncoloured_rows.append(
            [f.path, str(len(f.contents)), str(f.tokens), author, date]
        )
        coloured_rows.append(
            [
                f.path,
                str(len(f.contents)),
                colour_num(f.tokens, boundaries)[0],
                author,
                date,
            ]
        )

    # Calculate column widths
    headers = [
        "File Path",
        "Size (chars)",
        "Tokens",
        "Last Modified By",
        "Date",
    ]
    widths = [
        max(len(header), max(len(row[i]) for row in uncoloured_rows))
        for i, header in enumerate(headers)
    ]

    if colour:
        return format_table(
            headers=headers,
            rows=coloured_rows,
            column_widths=widths,
            align_right_columns=[1, 2],  # Size and tokens columns right-aligned
        )
    else:
        return format_table(
            headers=headers,
            rows=uncoloured_rows,
            column_widths=widths,
            align_right_columns=[1, 2],  # Size and tokens columns right-aligned
        )


def generate_file_bytes_table(
    files: List[FileSize],
    colour: bool = False,
) -> str:
    """Generates a formatted table showing file sizes and last modified dates."""
    if not files:
        return "No files found"

    # Get the data for colouring rows
    bytes = [f.bytes for f in files]
    boundaries = get_boundaries(bytes)

    coloured_rows = []
    uncoloured_rows = []

    for f in files:
        coloured_rows.append(
            [
                f.path,
                f"{colour_num(f.bytes, boundaries)[0]}",
                f.last_modified.strftime("%Y-%m-%d"),
            ]
        )

        # Get the rows uncoloured
        uncoloured_rows.append(
            [
                f.path,
                f"{f.bytes}",
                f.last_modified.strftime("%Y-%m-%d"),
            ]
        )

    headers = ["File Path", "Size (Bytes)", "Last Modified"]
    # Always use uncoloured rows for widths
    widths = [
        max(len(header), max(len(row[i]) for row in uncoloured_rows))
        for i, header in enumerate(headers)
    ]

    if colour:
        return format_table(
            headers=headers,
            rows=coloured_rows,
            column_widths=widths,
            align_right_columns=[1],  # Size column right-aligned
        )

    return format_table(
        headers=headers,
        rows=uncoloured_rows,
        column_widths=widths,
        align_right_columns=[1],  # Size column right-aligned
    )


def generate_file_ending_table(file_bytes: List[Tuple[str, List[int]]]) -> str:
    """Generate a table from file bytes ordered as a list of tuples. Index 0 of
    the tuple is the file ending, and index 2 is the number of bytes"""
    # Prepare the rows
    rows = [
        [fb[0], str(fb[1][0]), str(round(fb[1][0] / 1024**2, 4)), str(fb[1][1])]
        for fb in file_bytes
    ]

    # Prepare the headers
    headers = ["File Ending", "Total Bytes", "Total MB", "Total Files"]

    # Calculate column widths
    widths = [
        max(len(header), max(len(row[i]) for row in rows))
        for i, header in enumerate(headers)
    ]

    return format_table(
        headers=headers,
        rows=rows,
        column_widths=widths,
        align_right_columns=[1],  # Bytes column right aligned
    )


def generate_common_file_paths_table(
    common_file_paths: List[Dict[str, str | int]],
    colour: bool = False,
) -> str:
    """Generate a table with colouring for the common file paths."""
    # Get the data for colouring rows
    bytes = [p["bytes"] for p in common_file_paths]
    boundaries = get_boundaries(bytes)

    coloured_rows = []
    uncoloured_rows = []

    for p in common_file_paths:
        coloured_rows.append(
            [
                p["path"],
                f"{colour_num(p['bytes'], boundaries)[0]}",
                f"{p['seen']}",
                f"{p['depth']}",
            ]
        )

        # Get the rows uncoloured
        uncoloured_rows.append(
            [
                p["path"],
                f"{p['bytes']}",
                f"{p['seen']}",
                f"{p['depth']}",
            ]
        )

    headers = ["Path", "Size (Bytes)", "Seen (Count)", "Path Depth"]
    # Always use uncoloured rows for widths
    widths = [
        max(len(header), max(len(row[i]) for row in uncoloured_rows))
        for i, header in enumerate(headers)
    ]

    if colour:
        return format_table(
            headers=headers,
            rows=coloured_rows,
            column_widths=widths,
            # Size, seen, depth columns right-aligned
            align_right_columns=[1, 2, 3],
        )

    return format_table(
        headers=headers,
        rows=uncoloured_rows,
        column_widths=widths,
        # Size, seen, depth columns right-aligned
        align_right_columns=[1, 2, 3],
    )
