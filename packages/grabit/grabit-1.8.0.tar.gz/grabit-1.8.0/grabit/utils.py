"""
Description:
    Commonly used functions for the grabit package.
"""

import platform
import subprocess
from pathlib import Path
from typing import Any, Dict, Set, Tuple
import re


def copy_to_clipboard(text: str):
    """Copies text to clipboard based on OS."""
    system = platform.system()
    if system == "Windows":
        process = subprocess.Popen(["clip"], stdin=subprocess.PIPE)
        process.communicate(input=text.encode("utf-8"))
    elif system == "Darwin":  # macOS
        process = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        process.communicate(input=text.encode("utf-8"))


def read_dot_grabit(directory: str) -> Tuple[Set[str], str, Dict[str, Any]]:
    """
    Reads a .grabit file (if present) and returns:
    - A set of patterns as re.compile objects to ignore
    - A custom message to prepend to the context (if specified)
    - A list of the options included in the .grabit file
    """
    dot_grabit_path = Path(directory) / ".grabit"
    ignore_patterns = set()
    custom_message = (
        "Below is a list of related files, their contents and git history.\n\n"
    )

    # Options
    options = {"git_file_logs": True, "git_all_logs": False}

    if dot_grabit_path.exists():
        print("--- Found .grabit ---")
        current_section = None
        message_lines = []

        with open(dot_grabit_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("## "):
                    current_section = line[3:].lower()
                    continue

                if not line or line.startswith(
                    "//"
                ):  # Skip comments and empty lines
                    continue

                # Gathering include exclude
                if current_section == "exclude":
                    ignore_patterns.add(re.compile(line))
                elif current_section == "message":
                    message_lines.append(line)

                # Gathering the options
                elif current_section == "git file logs":
                    if "true" in line:
                        options["git_file_logs"] = True
                    elif "false" in line:
                        options["git_file_logs"] = False

                elif current_section == "git all logs":
                    if "true" in line:
                        options["git_all_logs"] = True
                    elif "false" in line:
                        options["git_all_logs"] = False

        if message_lines:
            custom_message = "\n".join(message_lines) + "\n\n"

    print("--- ignore patterns ---")
    print(ignore_patterns)
    return ignore_patterns, custom_message, options
