# SPDX-License-Identifier: Apache-2.0

""" Terminal styling utilities using ANSI-escape codes. """

import re
import os
import sys

from io import IOBase
from contextlib import contextmanager

# Enable colors if KIT_COLORIZE=1 and a terminal is attached
ENABLE_COLORIZE = os.environ.get("KIT_COLORIZE", "1") == "1"
if ENABLE_COLORIZE:
    ENABLE_COLORIZE = sys.stdout.isatty()

# Color codes
ANSI = {
    # Foreground
    "black"   : 30,
    "red"     : 31,
    "green"   : 32,
    "yellow"  : 33,
    "blue"    : 34,
    "magenta" : 35,
    "cyan"    : 36,
    "white"   : 37,

    # Background
    "bg-black"   : 40,
    "bg-red"     : 41,
    "bg-green"   : 42,
    "bg-yellow"  : 43,
    "bg-blue"    : 44,
    "bg-magenta" : 45,
    "bg-cyan"    : 46,
    "bg-white"   : 47,

    # Brightness
    "bright" : 1,
    "dim"    : 2,
    "normal" : 22,
}


@contextmanager
def colorize(color: str, stream: IOBase=sys.stdout):
    """ Enable given color(s) for given stream
    
    Args:
        color: Space-separated color names (ex: "bright red")
        stream: stream to stylize (sys.stdout or sys.stderr, usually)
    """
    if ENABLE_COLORIZE:
        for key in color.split(" "):
            stream.write("\033[{}m".format(ANSI[key]))
        try:
            yield
        finally:
            stream.write("\033[0m") # Reset
            stream.flush()
    else:
        yield


def add_color(text: str, color: str="normal") -> str:
    """ Surrounds string with ANSI-escaped color characters
    
    Args:
        text: Text to format
        color: Space-separated color names to apply
    
    Returns:
        Colorized text
    """
    prefix = ""
    for key in color.split(" "):
        prefix += "\033[{}m".format(ANSI[key])
    text = prefix+text+"\033[0m"
    return text


def remove_color(text: str) -> str:
    """ Return text without any ANSI-espaced characters """
    return re.sub("\033\[\d+m", "", text)


def sprint(text: str, end: str="\n", color: str="normal"):
    """ Write stylized text to stdout """
    with colorize(color):
        sys.stdout.write(text)
    sys.stdout.write(end)


def eprint(text: str, end: str="\n", color: str="red"):
    """ Write stylized text to stderr """
    with colorize(color, stream=sys.stderr):
        sys.stderr.write(text+end)
