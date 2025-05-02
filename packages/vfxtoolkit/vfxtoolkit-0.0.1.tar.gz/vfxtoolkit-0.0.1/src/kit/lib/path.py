# SPDX-License-Identifier: Apache-2.0

""" Path-related functions. """

import re
import sys


def linux_path(path: str) -> str:
    """ Ensure path is linux-style """
    path = re.sub(r"^([A-Za-z]):[/\\]", r"/\1/", path)
    return path.replace("\\", "/")


def windows_path(path:str ) -> str:
    """ Ensure path is windows-style """
    path = re.sub(r"^[/\\]([A-Za-z])[/\\]", r"\1:/", path)
    return path.replace("/", "\\")


def platform_path(path: str) -> str:
    """ Ensure given path is platform-style """
    if sys.platform == "win32":
        return windows_path(path)
    else:
        return linux_path(path)
