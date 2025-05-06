from grabit.models import FileSize
from typing import List, Tuple, Dict
import platform


def group_bytes_by_file_endings(
    files: List[FileSize],
) -> List[Tuple[str, List[int]]]:
    """Groups files by their file path endings and sums the bytes and orders on size,
    also includes the total number of files of that type."""
    bytes_table = {}

    for f in files:
        # Frequently, files can have more than one ending. e.g. `.d.ts` instead of `.ts`
        # the method below makes sure we capture the everything past the first dot.
        path = f.path

        # Ignore the dots that can appear at start of file paths
        if path[0] == "." and "\\" in path or "/" in path:
            path = path[1:]

        file_ending = ".".join(path.split(".")[1:])

        if file_ending == "":
            file_ending = "(No Ending)"

        if file_ending in bytes_table:
            bytes_table[file_ending][0] += f.bytes
            bytes_table[file_ending][1] += 1

        else:
            bytes_table[file_ending] = [f.bytes, 1]

    # Order by size
    bytes_list = list(bytes_table.items())
    bytes_list.sort(key=lambda x: x[1])

    return bytes_list


def group_bytes_by_file_paths(
    files: List[FileSize],
    file_sort: str = None,
) -> List[Dict[str, str | int]]:
    """
    Groups files by their file path and sums the bytes and orders on size,
    also includes the total number of files of that type. This works by splitting
    paths at the directory level and then joining them back up sequentially.
    The results are stored in a dict that tracks the number of times they occur,
    the amount of bytes that occur, and their path depth.

    The output is sorted alphabetically because later on the total bytes can
    be colour coded and seeing alphabetical grouping will reveal file patterns
    whilst still making it easy to see where issues are.
    """
    if platform.system() == "Windows":
        split_on = "\\"

    all_paths = {}

    for f in files:
        path = f.path
        split_path = path.split(split_on)

        # Remove initial dot if present
        if split_path[0] == ".":
            split_path = split_path[1:]

        # Because the path sections are being appended sequentially by the
        # final section we will have recreated the full path, remove this file
        # as this would be redundant.
        split_path = split_path[:-1]
        print(split_path)

        for i in range(0, len(split_path)):
            joined_path = "/".join(split_path[: i + 1])

            if joined_path in all_paths:
                data = all_paths[joined_path]
                data["bytes"] += f.bytes
                data["seen"] += 1

            else:
                all_paths[joined_path] = {
                    "bytes": f.bytes,
                    "seen": 1,
                    "depth": i + 1,
                }

    path_list = [{"path": k} | v for k, v in all_paths.items()]

    # Sort alphabetically by default
    # **THIS IS REACHABLE**
    if file_sort is None:
        print("hi")
        path_list.sort(key=lambda x: x["path"])
    else:
        path_list.sort(key=lambda x: x[file_sort])

    return path_list
