import os
from grabit.utils import copy_to_clipboard, read_dot_grabit


def print_tree(
    start_path: str = ".",
    max_depth: int = -1,
    copy_to_clip: bool = False,
):
    """
    Print a directory tree structure with improved formatting.

    Args:
        start_path: The root directory to start printing from.
        max_depth: The maximum depth of the directory tree to print.
        copy_to_clip: Whether to copy the output to the clipboard.
    """

    # Read the .grabit file and get the ignore patterns only
    ignore_patterns, _, _ = read_dot_grabit(start_path)

    print(max_depth)

    output = ""

    for root, dirs, files in os.walk(start_path):
        # Skip the directory if it matches any of the ignore patterns
        if any(pattern.match(root) for pattern in ignore_patterns):
            continue

        # Get the level of the directory
        level = root.replace(start_path, "").count(os.sep)
        indent = "│   " * level

        # Print directory with better formatting
        dir_name = os.path.basename(root) or start_path

        # print(root, dir_name, level)
        if level == 0:
            output += f"📁 {dir_name}/\n"
        elif level < max_depth + 1 or max_depth == -1:
            output += f"{indent[:-4]}├── 📁 {dir_name}/\n"
        else:
            continue

        if max_depth != -1 and level >= max_depth:
            continue

        # Sort files for better readability
        files.sort()

        # TODO: Decide if files should be indented one level deeper or not
        # file_indent = "│   " * (level + 1)

        # Print files with better formatting
        for i, f in enumerate(files):
            is_last = i == len(files) - 1 and not dirs
            if is_last:
                prefix = "└── "
            else:
                prefix = "├── "
            output += f"{indent}{prefix}📄 {f}\n"

    if copy_to_clip:
        copy_to_clipboard(output)
    else:
        print(output)
