import sys

required_version = (
    3,
    11,
)  # Replace with the required version tuple, e.g., (3, 9) for Python 3.9
current_version = sys.version_info

if current_version < required_version:
    print(
        f"Update required: Current Python version is {current_version.major}.{current_version.minor} "
        f"but version {required_version[0]}.{required_version[1]} or higher is needed."
    )
    sys.exit(1)

sys.exit(0)
