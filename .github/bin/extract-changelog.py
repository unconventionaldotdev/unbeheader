#!/usr/bin/env python
# This file is part of Unbeheader.
# Copyright (C) CERN & UNCONVENTIONAL

import re
import sys
from pathlib import Path

CHANGELOG_FILENAME = 'CHANGELOG.md'


def extract_section(version):
    path = Path(CHANGELOG_FILENAME)
    text = path.read_text()

    re_start = rf'^## ({re.escape(version)})(.*)$'
    re_end = r'^## (.*)$'
    if not (match := re.search(re_start, text, re.MULTILINE)):
        print(f'::error::Version {version} not found in {CHANGELOG_FILENAME}.')
        sys.exit(1)

    text = text[match.end(0):]
    if match := re.search(re_end, text, re.MULTILINE):
        text = text[:match.start()]

    return text.strip()


def main():
    version = sys.argv[1]
    out_path = None
    if len(sys.argv) > 2:
        out_path = Path(sys.argv[2])
    changelog = extract_section(version)
    if not out_path:
        print(changelog)
        return
    out_path.write_text(changelog)
    print(f'Changelog for {version} written to {out_path}.')


if __name__ == '__main__':
    main()
