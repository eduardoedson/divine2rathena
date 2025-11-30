#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
General-purpose utility helpers used across the Divine-Pride → rAthena
conversion pipeline.

Contains:

- normalize_dbname(): Converts DB names such as 'HOLY_FRUS' → 'Holy Frus'
- positive(): Safe integer parsing returning |value| or 0 if invalid
- value_fallback(): Safe fallback logic ensuring non-zero final numeric values
"""

from __future__ import annotations
from typing import Any


# =====================================================================
# NORMALIZE NAME (e.g. HOLY_FRUS → Holy Frus)
# =====================================================================

def normalize_dbname(name: str) -> str:
    """
    Converts strings such as 'HOLY_FRUS' or 'holy_frus' into 'Holy Frus'.

    Rules:
    - Empty or None → ""
    - Split by underscore when present
    - Capitalize each fragment
    """
    if not name:
        return ""

    name = name.strip()
    parts = name.split("_") if "_" in name else [name]

    return " ".join(word.capitalize() for word in parts)


# =====================================================================
# SAFE POSITIVE INTEGER PARSER
# =====================================================================

def positive(value: Any) -> int:
    """
    Safely converts any value into a positive integer.

    Example:
        positive("10")  -> 10
        positive(-5)    -> 5
        positive(None)  -> 0
        positive("abc") -> 0

    Returns:
        int: |value| or 0 if invalid.
    """
    try:
        return abs(int(value))
    except (TypeError, ValueError):
        return 0
    

# =====================================================================
# SAFE PARSERS
# =====================================================================

def _safe_int(value: Any, default: int = 0) -> int:
    """Safely parses int values."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_str(value: Any) -> str:
    """Ensures string output."""
    return str(value).strip() if value is not None else ""


# =====================================================================
# FALLBACK NUMERIC LOGIC
# =====================================================================

def value_fallback(value: Any, fallback: Any) -> int:
    """
    Ensures a non-zero integer result using chained fallback logic:

    1. Try positive(value)
    2. If zero → try positive(fallback)
    3. If still zero → return hard default 350

    This helper is used heavily to guarantee all rAthena fields
    that require integers always receive safe values.

    Example:
        value_fallback("20", 100)     -> 20
        value_fallback(None, "40")    -> 40
        value_fallback("abc", None)   -> 350
    """
    primary = positive(value)
    if primary > 0:
        return primary

    secondary = positive(fallback)
    if secondary > 0:
        return secondary

    return 350
