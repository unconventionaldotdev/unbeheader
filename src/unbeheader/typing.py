# This file is part of Unbeheader.
# Copyright (C) CERN & UNCONVENTIONAL

from dataclasses import dataclass
from pathlib import Path
from re import Pattern
from typing import Any
from typing import NamedTuple
from typing import TypeAlias

ConfigDict: TypeAlias = dict[str, Any]
PathCache: TypeAlias = dict[Path, bool]


@dataclass
class CommentSkeleton:
    # The string that indicates the start of a comment
    comment_start: str
    # The string that indicates the continuation of a comment
    comment_middle: str
    # The string that indicates the end of a comment
    comment_end: str = ''


class SupportedFileType(NamedTuple):
    # A regular expression matching header comments
    regex: Pattern[str]
    # A dictionary defining the skeleton of comments
    comments: CommentSkeleton
