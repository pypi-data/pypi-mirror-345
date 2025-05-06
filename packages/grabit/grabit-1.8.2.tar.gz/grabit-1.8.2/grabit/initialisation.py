import os
import platform

# Get the absolute path to the directory containing the current file
abs_path = os.path.abspath(__file__)

system = platform.system()
if system == "Windows":
    abs_path = os.path.abspath(__file__).replace("\\", "/")

abs_path = abs_path.split("/")
abs_path = "/".join(abs_path[:-1])


def init_command():
    """Create a new .grabit file using the default template"""
    with open(f"{abs_path}/default.grabit", "r") as f:
        default_template = f.read()

    with open("./.grabit", "w") as f:
        f.write(default_template)
