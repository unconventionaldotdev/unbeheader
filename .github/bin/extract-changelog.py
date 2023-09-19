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

    # Check that the changelog contains a section for the given version
    re_start = rf'^## ({re.escape(version)})(.*)$'
    if not (match := re.search(re_start, text, re.MULTILINE)):
        print(f'::error::Version {version} not found in {CHANGELOG_FILENAME}.')
        sys.exit(1)

    # Check that the given version is not marked as unreleased
    if 'unreleased' in match.group(2).lower():
        print(f'::error::Version {version} is marked as unreleased in {CHANGELOG_FILENAME}.')
        sys.exit(1)

    # Extract the changes for the given version
    re_end = r'^## (.*)$'
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
