#!/usr/bin/env bash
# This file is part of Unbeheader.
# Copyright (C) CERN & UNCONVENTIONAL

set -e

# Fail if the tag version is not passed
if [ -z "$1" ]; then
    echo "::error::No tag version passed."
    exit 1
fi

# Get the tag version from the argument
TAG_VERSION=$1

# Get the version from pyproject.toml
PROJECT_VERSION="$(grep 'version =' pyproject.toml | cut -d '"' -f 2)"

# Check if the tag version matches the project version
if [ "${TAG_VERSION}" != "${PROJECT_VERSION}" ]; then
    echo "::error::Tag version ${TAG_VERSION} doesn't match project version ${PROJECT_VERSION}."
    exit 1
fi
