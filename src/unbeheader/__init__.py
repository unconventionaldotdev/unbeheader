# This file is part of Unbeheader.
# Copyright (C) CERN & UNCONVENTIONAL

import re

from .typing import CommentSkeleton
from .typing import SupportedFileType

SUPPORTED_FILE_TYPES: dict[str, SupportedFileType] = {
    'py': SupportedFileType(
        re.compile(r'((^#|[\r\n]#).*)*'),
        CommentSkeleton('#', '#')),
    'pyi': SupportedFileType(
        re.compile(r'((^#|[\r\n]#).*)*'),
        CommentSkeleton('#', '#')),
    'wsgi': SupportedFileType(
        re.compile(r'((^#|[\r\n]#).*)*'),
        CommentSkeleton('#', '#')),
    'js': SupportedFileType(
        re.compile(r'/\*(.|[\r\n])*?\*/|((^//|[\r\n]//).*)*'),
        CommentSkeleton('//', '//')),
    'jsx': SupportedFileType(
        re.compile(r'/\*(.|[\r\n])*?\*/|((^//|[\r\n]//).*)*'),
        CommentSkeleton('//', '//')),
    'css': SupportedFileType(
        re.compile(r'/\*(.|[\r\n])*?\*/'),
        CommentSkeleton('/*', ' *', ' */')),
    'scss': SupportedFileType(
        re.compile(r'/\*(.|[\r\n])*?\*/|((^//|[\r\n]//).*)*'),
        CommentSkeleton('//', '//')),
    'sh': SupportedFileType(
        re.compile(r'((^#|[\r\n]#).*)*'),
        CommentSkeleton('#', '#')),
}
