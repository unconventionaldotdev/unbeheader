# This file is part of Unbeheader.
# Copyright (C) CERN & UNCONVENTIONAL

import re

# Dictionary listing the files for which to change the header.
# The key is the extension of the file (without the dot) and the value is another
# dictionary containing two keys:
#   - 'regex' : A regular expression matching comments in the given file type
#   - 'comments': A dictionary with the comment characters to add to the header.
#                 There must be a `comment_start` inserted before the header,
#                 `comment_middle` inserted at the beginning of each line except the
#                 first and last one, and `comment_end` inserted at the end of the
#                 header.
SUPPORTED_FILES = {
    'py': {
        'regex': re.compile(r'((^#|[\r\n]#).*)*'),
        'comments': {'comment_start': '#', 'comment_middle': '#', 'comment_end': ''}},
    'wsgi': {
        'regex': re.compile(r'((^#|[\r\n]#).*)*'),
        'comments': {'comment_start': '#', 'comment_middle': '#', 'comment_end': ''}},
    'js': {
        'regex': re.compile(r'/\*(.|[\r\n])*?\*/|((^//|[\r\n]//).*)*'),
        'comments': {'comment_start': '//', 'comment_middle': '//', 'comment_end': ''}},
    'jsx': {
        'regex': re.compile(r'/\*(.|[\r\n])*?\*/|((^//|[\r\n]//).*)*'),
        'comments': {'comment_start': '//', 'comment_middle': '//', 'comment_end': ''}},
    'css': {
        'regex': re.compile(r'/\*(.|[\r\n])*?\*/'),
        'comments': {'comment_start': '/*', 'comment_middle': ' *', 'comment_end': ' */'}},
    'scss': {
        'regex': re.compile(r'/\*(.|[\r\n])*?\*/|((^//|[\r\n]//).*)*'),
        'comments': {'comment_start': '//', 'comment_middle': '//', 'comment_end': ''}},
    'sh': {
        'regex': re.compile(r'((^#|[\r\n]#).*)*'),
        'comments': {'comment_start': '#', 'comment_middle': '#', 'comment_end': ''}},
}
