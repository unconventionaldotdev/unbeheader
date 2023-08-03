#!/usr/bin/env bash
# This file is part of Unbeheader.
# Copyright (C) CERN & UNCONVENTIONAL

set -e

VERSION=$(grep 'version =' pyproject.toml | cut -d '"' -f 2)
TAG="v${VERSION}"

git tag "${TAG}"
echo "Tag ${TAG} was created"
