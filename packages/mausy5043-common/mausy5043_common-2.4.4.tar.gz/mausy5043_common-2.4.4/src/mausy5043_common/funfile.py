#!/usr/bin/env python3

# mausy5043-common
# Copyright (C) 2025  Maurice (mausy5043) Hendrix
# AGPL-3.0-or-later  - see LICENSE

"""Provide file operation functions."""

import os


def cat(file_name: str) -> str:
    """Read a file (line-by-line) into a variable.

    Args:
        file_name (str) : file to read from

    Returns:
          (str) : file contents
    """
    contents: str = ""
    if os.path.isfile(file_name):
        with open(file_name, encoding="utf-8") as file_stream:
            contents = file_stream.read().strip("\n")
    return contents
