import re
from typing import Tuple


def package_version_to_tuple(version_str: str) -> Tuple[int, ...]:
    # Python supports crazy version strings, the only mandatory part is major.minor

    # Strip off any prerelease (-...) or build (+...) segment
    version_str = re.split(r"[-+]", version_str, 1)[0]  # split once on first '-' or '+'

    # Split on dots
    parts = version_str.split(".")

    if len(parts) < 2:
        raise ValueError("Invalid version format: '{}'".format(version_str))

    major = parts[0]
    minor = parts[1]

    # patch is optional
    if len(parts) > 2:
        patch = parts[2]
    else:
        patch = 0

    try:
        major = int(major)
        minor = int(minor)
        patch = int(patch)
    except ValueError:
        raise ValueError("Version parts must be integers: '{}'".format(version_str))

    return (major, minor, patch)
