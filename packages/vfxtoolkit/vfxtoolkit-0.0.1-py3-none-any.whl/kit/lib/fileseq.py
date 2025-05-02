# SPDX-License-Identifier: Apache-2.0

""" Utility functions to deal with file sequences

Example of supported syntax:
    - name_1234.ext         # Specific frame (underscore separator)
    - name.1234.ext         # Specific frame (dot separator)
    - name.%04d.ext         # Percent padding (fixed 4 digits)
    - name.%d.ext           # Percent padding (variable)
    - name.#.ext            # Hash padding (fixed 4 digits, implicit)
    - name.####.ext         # Hash padding (fixed 4 digits, explicit)
    - name.###.ext          # Hash padding (fixed 3 digits)
    - name.@.ext            # At padding (variable)
    - name.@@@@.ext         # At padding (fixed 4 digits)
    - name.10-40#.ext       # Embedded range (continuous/complete)
    - name.10<40#.ext       # Embedded range (discontinuous/incomplete)
    - name.10-20x2#.ext     # Embedded range (with steps)
    - name.1,4,6-10#.ext    # Embedded range (multiple segments)
    - name.[0950-1020].ext  # Embedded range (bracket style, fixed 4 digits)
    - name.[950-1020].ext   # Embedded range (bracket style, variable padding)

Most path-related methods accept both sequence and regular file paths.
To preview most of them, you can use `test_path(path)`.

Ex: test("T:/demo/seq.[1001-1200,1500].exr")
    print         : T:/demo/seq.[1001-1200,1500].exr
    split         : ('T:/demo/seq.', '[1001-1200,1500]', '.exr')
    splitext      : ('T:/demo/seq', '.[1001-1200,1500].exr')
    basename      : seq
    extension     : exr
    is_sequence   : True
    is_abstract   : True
    is_frame      : False
    padding       : 4
    frame         : None
    range         : (1001, 1500, 0)
    ranges        : [(1001, 1200, 1), (1500, 1500, 1)]
    scan_range    : (None, None, None)
    scan_ranges   : []
    scan_frames   : []
    frame_path    : T:/demo/seq.1001.exr
    abstract_path : T:/demo/seq.%04d.exr
"""

import re
import os

from collections import OrderedDict
from typing import Iterable, Callable

_range = range


# == Regex Patterns == #


# Helper patterns
_PAD = "(?:#+|@+|%d|%0\dd)" # Matches abstract padding
_RNG = "(?:\d+[\d,x<-]*)" # Matches frame range
_EXT = "(?:\.\w+(?:\.(?:sc|gz))?)" # Matches file extension
_SEP = "(?<=[\._])" # Look for frame prefix (. or _)

# Regex to split any strings into (prefix, frame, extension)
RE_SPLIT = re.compile(
    f"^(.*?)({_SEP}(?:\d+|{_RNG}?{_PAD}|\[{_RNG}\])|)({_EXT}?)$",
    re.IGNORECASE
    )

# Simplified pattern to match frames within sequences
RE_FRAME = re.compile(f"^(.*?)({_SEP}\d+|)({_EXT}?)$", re.IGNORECASE)

# Matches FIRST, FIRST-LAST, FIRST<LAST or FIRST-LASTxSTEP
RE_RANGE = re.compile("^(\d+)(?:([-<])(\d+)(?:x(\d+))?)?$")


# == Module Exceptions == #


class SequenceError(Exception):
    """ Base exception """
    pass


class PaddingError(SequenceError):
    """ Padding-syntax related errors """
    pass 


class RangeError(SequenceError):
    """ Frame-range related errors (bad syntax, non-monotonic frames, ...) """
    pass


class ArgumentError(SequenceError):
    """ Arguments syntax errors """


# == General Path Manipulation == #


def basename(path: str) -> str:
    """ Returns file or sequence base name without frame nor extension """
    return splitext(os.path.basename(path))[0]


def extension(path: str) -> str:
    """ Returns file or sequence extension, without leading dot """
    return split(path)[-1][1:]


def split(path: str) -> tuple[str, str, str]:
    """ Split file or sequence path into (prefix, frame, extension) """
    return RE_SPLIT.match(path).groups()


def splitext(path: str) -> tuple[str, str]:
    """ Similar to os.path.splitext, but includes padding and frame in ext """
    prefix, frame, ext = split(path)
    return (prefix[:-1], prefix[-1]+frame+ext) if frame else (prefix, ext)


# == Path Testing == #


def is_sequence(path: str) -> bool:
    """ Test if path can be interpreted as a frame or abstract sequence """
    return bool(RE_SPLIT.match(path).group(2))


def is_frame(path: str) -> bool:
    """ Test if path can be interpreted as a frame within a sequence """
    return RE_SPLIT.match(path).group(2).isdigit()


def is_abstract(path: str) -> bool:
    """ Test if path can be interpreted as an abstract sequence """
    return RE_SPLIT.match(path).group(2).endswith(("#", "@", "d", "]"))


# == Path Conversion == #


def frame_path(path: str, frame: int) -> str:
    """ Returns path with range and padding replaced with given frame """
    prefix, frame_text, ext = split(path)
    if frame_text:
        pad_size = parse_padding(frame_text)
        return prefix + str(frame).zfill(pad_size) + ext
    else:
        return path


def abstract_path(
    path: str,
    style: str="%",
    ranges: Iterable[tuple[int, int, int]]|None=None,
    pad_size: int|None=None,
    ) -> str:
    """ Returns path with abstracted frame padding.
    
    Args:
        path: Path to frame or abstract sequence.
        style: Frame padding abstraction style. one of:
            %: Percent padding (ex: 1-10%d, 10-20%04d, %02d)
            #: Concise hash padding (ex: 1-10%d, 10-20#, ##)
            ##: Verbose hash padding (ex: 1-10%d, 10-20####, ##)
            @: RV's at padding (ex: 1-10@, 10-20@@@@, @@)
            []: Bracket range (ex: [1-20], [0010-0020], %02d).
        ranges: List of frame ranges to embed.
        pad_size: Override frame padding size regardless of incoming path or
            embedded frame ranges.

    Returns:
        Abstracted sequence path, or original path if incoming path was not
            a sequence path.
    """
    
    # Split path
    prefix, frame, ext = split(path)
    if not frame:
        return path

    # Construct range
    pad_size = parse_padding(frame) if pad_size is None else pad_size
    zfill = pad_size if style == "[]" else 0
    rng = format_ranges(ranges, zfill=zfill) if ranges else ""
    if not rng and style == "[]":
        style = "%"

    # Determine padding
    if style == "[]":
        pad = ("[" + rng + "]") if rng else format_padding(pad_size, "%")
    else:
        pad = rng + format_padding(pad_size, style)

    # Reconstruct path
    return prefix + pad + ext


# == Path Extraction == #


def frame(path: str) -> int|None:
    """ Returns frame number embedded in path """
    frame = RE_SPLIT.match(path).group(2)
    return int(frame) if frame.isdigit() else None


def padding(path: str) -> int|None:
    """ Returns most likely padding size in use in the given sequence path """
    frame = RE_SPLIT.match(path).group(2)
    return parse_padding(frame) if frame else None


def range(path: str, scan: bool=False) -> tuple[int,int,int] | tuple[None,None,None]:
    """ Returns frame range (first, last, step) embedded in path.
    
    Args:
        path: Full path or base name
        scan: If True and no range is embedded, attempt to scan it from disk.

    Returns:
        tuple of int (first, last, step), or (None, None, None) if no range
        is embedded in the path. In the event multiple ranges are embedded, the
        combined overall range is returned. A step of 0 indicates an incomplete
        sequence.
    """
    rngs = ranges(path, scan=scan)
    if len(rngs) == 0:
        return (None, None, None)
    elif len(rngs) == 1:
        return rngs[0]
    else:
        return (rngs[0][0], rngs[-1][1], 0)


def ranges(path: str, scan: bool=False) -> list[tuple[int,int,int]]:
    """ Returns frame range list (first, last, step) embedded in path.
    
    Args:
        path: Full path or base name
        scan: If True and no range is embedded, attempt to scan it from disk.

    Returns:
        list of tuple (first, last, step), or empty list if no range is
        embedded in the path.
    """

    # Match frame range text
    frames = RE_SPLIT.match(path).group(2)
    if not frames:
        return []

    if frames[0] == "[":
        frames = frames[1:-1]
    rng = re.sub(_PAD, "", frames)
    if rng:
        return parse_ranges(rng)
    elif scan:
        return scan_ranges(path)
    else:
        return []


# == Text Parsing == #


def parse_range(text: str) -> tuple[int,int,int]:
    """ Returns (first, last, step) from given text """

    # Match syntax
    m = RE_RANGE.match(text)
    if not m:
        raise RangeError(f"Invalid range syntax: '{text}'.")

    # Convert to int
    first, sep, last, step = m.groups()
    first = int(first)
    last = int(last) if last is not None else first
    step = int(step) if step is not None else (0 if sep=="<" else 1)
    
    # Validate & return
    if sep == "<" and step != 0:
        raise RangeError("Invalid range: can't use < with non-zero step.")
    elif first > last:
        raise RangeError(f"Invalid range: first({first}) > last({last})")
    return (first, last, step)


def parse_ranges(text: str) -> list[tuple[int,int,int]]:
    """ Returns list of ranges from given text """
    ranges = []
    for segment in text.split(","):
        seg = parse_range(segment)
        if ranges and ranges[-1][1] >= seg[0]:
            raise RangeError(f"Invalid range: backwards segment in '{text}'")
        ranges.append(seg)
    return ranges


def parse_padding(text: str) -> int:
    """ Returns frame padding size inferred from given frame or range text.
    
    Args:
        text: Padding text, interpreted as follows:
            Ends with %d: Variable padding (0)
            Ends with %0Xd: Fixed padding (where X is between 1 and 9)
            Ends with #: Fixed padding (4 if one #, else #'s count)
            Ends with @: Variable padding (if one @) else fixed (@'s count)
            1234: Fixed padding (as many digits as there is in the number)
            [123-456]: Fixed padding (common width of all the frame numbers)
            [1-23]: Variable padding (0, frame numbers have different widths)
    """
    
    if text.endswith("%d"):
        return 0
    elif text.endswith("d"):
        return int(text[-2])
    elif text.endswith("#"):
        size = text.count("#")
        return 4 if size == 1 else size
    elif text.endswith("@"):
        size = text.count("@")
        return 0 if size == 1 else size
    else:
        d = set(len(i) for i in re.findall("(?<![x\d])\d+", text))
        return next(iter(d)) if (len(d) == 1) else 0


# == Text Formatting == #


def format_padding(size: int, style: str="%") -> str:
    """ Returns abstract frame padding text using given style.
    
    Args:
        size (int): Padding size (where 0 means variable-length)
        style (str): Formatting style, one of:
            %: Percent padding (%d, %01d, %02d, %03d, %04d, %05d, ...)
            #: Concise hash padding (%d, %01d, ##, ###, #, #####, ...)
            ##: Verbose hash padding (%d, %01d, ##, ###, ####, #####, ...)
            @: RV's at padding (@, %01d, @@, @@@, @@@@, @@@@@, ...)
    """
    if size == 1:
        return "%01d"
    elif style == "%":
        return "%d" if size == 0 else "%0"+str(size)+"d"
    elif style == "#":
        return "%d" if size == 0 else ("#" if size == 4 else "#"*size)
    elif style == "##":
        return "%d" if size == 0 else "#"*size
    elif style == "@":
        return "@" if size == 0 else "@"*size
    else:
        raise ArgumentError(
            f"Invalid padding style: got {style}, expected %, #, ## or @"
            )


def format_range(first: int, last: int, step: int=1, zfill: int=0) -> str:
    """ Format frame range into text like "1001-1020".
    
    Args:
        first: First frame
        last: Last frame, where last >= first.
        step: Steps between frames, where:
            0: Indicates missing frames (ex: 1001<1010)
            1: Indicates a continuous sequence (ex: 1001-1010)
            2+: Indicates regular gaps in the sequence (ex: 1001-1010x2)
        zfill: Zero-pad all frame numbers by this amount.

    Returns:
        Formatted string.
    """

    # Pad frames
    first_str = str(first).zfill(zfill)
    last_str = str(last).zfill(zfill)

    # Format
    if first == last:
        return first_str
    elif step == 0:
        return first_str + "<" + last_str
    elif step == 1:
        return first_str + "-" + last_str
    else:
        return first_str + "-" + last_str + "x" + str(step)


def format_ranges(ranges: Iterable[tuple[int, int, int]], zfill: int=0) -> str:
    """ Format multiple frames ranges into a comma-separated list string.

    Args:
        ranges: Frame range list to format.
        zfill: Zero-pad all frame numbers by this amount.

    Returns:
        Formatted string, where each ranges are joined by a comma.
    """
    return ",".join(format_range(*rng, zfill=zfill) for rng in ranges)


# == Disk scanners == #

def scan_range(
    path: str,
    max_steps: int=100
    ) -> tuple[int,int,int] | tuple[None,None,None]:
    """ Scan frame range from disk.
    
    Args:
        path: Full path to frame or abstract sequence.
        max_steps: Maximum number of steps to group frames by.

    Returns:
        Scanned range (first, last, step). If step=0, this means there is gaps
        in the sequence (use scan_ranges or scan_frames to get more details).
    """

    ranges = scan_ranges(path, max_steps=max_steps)
    if not ranges:
        return (None, None, None)
    elif len(ranges) == 1:
        return ranges[0]
    else:
        return (ranges[0][0], ranges[-1][1], 0)


def scan_ranges(path: str, max_steps: int=100) -> list[tuple[int,int,int]]:
    """ Scan frame ranges from disk
    
    Args:
        path: Full path to frame or abstract sequence.
        max_steps: Maximum number of steps to group frames by.

    Returns:
        list of scanned ranges tuple(first, last, step), where step>=1.
    """
    return group_by_range(scan_frames(path), max_steps=max_steps)
    

def scan_frames(path: str) -> list[int]:
    """ Returns sorted list of all frame numbers available on disk """

    # Match sequence
    prefix, frame, ext = split(path)
    if not frame:
        return []

    # Verify base directory exists
    dirname = os.path.dirname(path)
    if not os.path.isdir(dirname):
        return []

    # Build filter regex
    prefix_ptn = re.escape(os.path.basename(prefix))
    ext_ptn = re.escape(ext)
    pad_size = parse_padding(frame)
    pad_ptn = "\d+" if (pad_size == 0) else ("\d" * pad_size)
    regex = re.compile(f"^{prefix_ptn}({pad_ptn}){ext_ptn}$")

    # Scan
    frames = set()
    for di in os.scandir(dirname):
        m = regex.match(di.name)
        if m:
            frames.add(int(m.group(1)))
    return sorted(frames)


def scan_sequences(path: str, **kwargs) -> dict:
    """ Scan sequences contained within the given directory.

    Args:
        path: Full path to the directory to scan. Raises OS error if such
            directory does not exists.
        **kwargs: Extra arguments to pass to group_by_sequences.

    Returns:
        dict where keys are abstract sequences paths and values a dict of
        frames, keys are frame number and values os.DirEntry objects. You can
        use list(scan_sequences(path)) to get only the sequences paths.
    """
    entries = os.scandir(path)
    return group_by_sequence(entries, key=lambda di:di.name, **kwargs)


# == Grouping functions == #


def group_by_range(
    frames: Iterable[int],
    max_steps: int=100
    ) -> Iterable[tuple[int,int,int]]:
    """ Compact sorted frame list into a (first, last, step) range list.
    
    Args:
        frames: List of sorted frames to iterate from.
        max_steps: Maximum number of steps which can be returned in ranges.

    Returns:
        list of (first, last, step).
    """

    # Pick first frame
    it = iter(frames)
    try:
        first = next(it)
    except StopIteration:
        return []
    last = first
    step = 1

    # Build ranges
    ranges = []
    for frame in it:
        if frame - step == last:
            last = frame
        elif step == 1 and last == first and (frame-last) <= max_steps:
            step = frame-last
            last = frame
        else:
            ranges.append((first, last, step))
            first, last, step = frame, frame, 1
    ranges.append((first, last, step))
    return ranges


def group_by_sequence(
    items: Iterable[any],
    key: Callable=str,
    format: str="minimal",
    style: str="%",
    max_steps: int=100,
    ignore_regular_files: bool=False,
    ) -> dict[str,dict[int,any]]:
    """ Groups items by sequences.

    Examples:
        Assuming "items" is the following list of str:
            - "img.1001.exr"
            - "img.1002.exr"
            - "img.1020.exr"
            - "img.1022.exr"
        The returned dict keys per mode would be:
            - minimal: ["img.%04d.exr"]
            - compact: ["img.1001<1022%04d.exr"]
            - combined: ["img.1001-1002,1020,1022%04d.exr"]
            - verbose: ["img.1001-1002.exr", "img.1020-1022x2%04d.exr"]

    Args:
        items: Iterable of items to group (like list of str or os.DirEntry).
        key: Callable used to extract the path or base name of the file.
        format: Controls how segments are grouped and how keys are set, one of:
            minimal: One entry per sequence without frame range
            compact: One entry per sequence with compacted frame range
            combined: One entry per sequence, all frame ranges combined
            verbose: One entry per segment, with frame range.
        style: Frame padding abstraction style. one of:
            %: Percent padding (ex: 1-10%d, 10-20%04d, %02d)
            #: Concise hash padding (ex: 1-10%d, 10-20#, ##)
            ##: Verbose hash padding (ex: 1-10%d, 10-20####, ##)
            @: RV's at padding (ex: 1-10@, 10-20@@@@, @@)
            []: Bracket range (ex: [1-20], [0010-0020], %02d).
        ignore_regular_files: Whether to ignore non-sequence files instead of
            returning them as a sequence of 1 frame.
        max_steps: Maximum number of steps to group frames by.
    
    Returns:
        dict, where keys are an abstract sequence path formatted according
            to the "format" argument and values are a sorted dictionary of
            frames numbers and items contained within.  
    """

    # Check arguments
    if style not in ("%", "#", "@", "[]"):
        raise ArgumentError(f"Invalid padding style: {style}")
    elif format not in ("minimal", "compact", "combined", "verbose"):
        raise ArgumentError(f"Invalid format mode: {format}")

    # Group items per sequences of same padding.
    seqs = {} # (prefix, ext, pad_size): {frame: item}
    for item in items:
        prefix, frame, ext = RE_FRAME.match(key(item)).groups()
        if frame:
            iframe, pad_size = int(frame), len(frame)
        else:
            if ignore_regular_files:
                continue
            iframe, pad_size = 0, -1
        seqs.setdefault((prefix, ext, pad_size), []).append((iframe, item))
    
    # Sort frames, detect plausible variable-padding sequences
    output = {}
    for (prefix, ext, pad_size), frames in sorted(seqs.items()):
        
        # Sort frames as dict
        if not frames:
            continue
        frames = dict(sorted(frames))

        # Determines whether the sequence is zero-padded
        first_frame = next(iter(frames))
        has_padding = (pad_size > 1 and first_frame < pow(10, pad_size-1))

        # Detect continuation of variable-padding sequences
        if not has_padding:
            for i in _range(pad_size+1, pad_size+10):
                next_key = (prefix, ext, i)
                if not next_key in seqs:
                    break
                next_frames = dict(sorted(seqs[next_key]))
                if not set(next_frames).isdisjoint(frames):
                    break
                pad_size = 0
                frames.update(next_frames)
                seqs[next_key][:] = []

        # Regular file
        if pad_size == -1:
            output[prefix+ext] = frames
            continue

        # Single frame
        if len(frames) == 1:
            output[prefix+str(first_frame).zfill(pad_size)+ext] = frames
            continue

        # Minimal (no range)
        if format == "minimal":
            pad = format_padding(pad_size, style)
            output[prefix + pad + ext] = frames
            continue

        seq = prefix + "#" + ext
        rngs = group_by_range(frames, max_steps=max_steps)

        # Compact (single range)
        if format == "compact":
            rng = rngs[0] if len(rngs) == 1 else (rngs[0][0], rngs[-1][1], 0)
            key = abstract_path(seq, style, [rng], pad_size=pad_size)
            output[key] = frames
            continue

        # Combined (multiple ranges)
        if format == "combined":
            key = abstract_path(seq, style, rngs, pad_size=pad_size)
            output[key] = frames
            continue

        # Verbose (multiple groups)
        if format == "verbose":
            for rng in rngs:
                sub = {i: frames[i] for i in _range(rng[0], rng[1]+1, rng[2])}
                key = abstract_path(seq, style, [rng], pad_size=pad_size)
                output[key] = sub

    return output


# -- Misc -- #


def test_path(path: str):
    """ Convenience demo/test function for path-related functions. """
    print("print         :", path)
    print("split         :", split(path))
    print("splitext      :", splitext(path))
    print("basename      :", basename(path))
    print("extension     :", extension(path))
    print("is_sequence   :", is_sequence(path))
    print("is_abstract   :", is_abstract(path))
    print("is_frame      :", is_frame(path))
    print("padding       :", padding(path))
    print("frame         :", frame(path))
    print("range         :", range(path))
    print("ranges        :", ranges(path))
    print("scan_range    :", scan_range(path))
    print("scan_ranges   :", scan_ranges(path))
    print("scan_frames   :", scan_frames(path))
    print("frame_path    :", frame_path(path, 1001))
    print("abstract_path :", abstract_path(path))
