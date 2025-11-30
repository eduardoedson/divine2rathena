#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File helper utilities used by the monster converter.

Provides:
- Automatic directory creation
- Safe file initialization (delete + recreate)
- Line-append helper
- Optional validation warnings
"""

from __future__ import annotations
import os
from typing import Optional
from config_loader import config


def _warn(message: str) -> None:
    """Prints a warning only if ENABLE_WARNINGS=True."""
    if config.debug:
        print(f"[WARN] {message}")


# =====================================================================
# INTERNAL UTILITY: DIRECTORY ENSURER
# =====================================================================

def _ensure_directory(path: str) -> None:
    """
    Ensures that the directory for a file exists.
    Example: for "export/mob_db.yml", ensures folder "export/" exists.
    """
    directory = os.path.dirname(path)

    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            raise RuntimeError(f"Failed to create directory '{directory}': {e}")


# =====================================================================
# FILE INITIALIZER
# =====================================================================

def init_file(path: str) -> bool:
    """
    Deletes an existing file and creates a new empty file.
    Also creates the parent directory if missing.

    Returns:
        True on success.
    """
    _ensure_directory(path)

    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception as e:
            raise RuntimeError(f"Failed to remove file '{path}': {e}")

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("")
    except Exception as e:
        raise RuntimeError(f"Failed to initialize file '{path}': {e}")

    return True


# =====================================================================
# LINE APPENDER
# =====================================================================

def append_line(path: str, line: str) -> bool:
    """
    Appends a single line (with newline) to the file.
    The file is created automatically if it does not exist.

    Returns:
        True on success.
    """
    if not isinstance(line, str):
        _warn(f"append_line received non-string line: {line!r}. Auto-converting.")
        line = str(line)

    _ensure_directory(path)

    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(line.rstrip("\n") + "\n")
    except Exception as e:
        raise RuntimeError(f"Failed to append to file '{path}': {e}")

    return True
