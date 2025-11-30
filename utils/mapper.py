#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utility mapper functions for converting Divine-Pride numeric values
into rAthena-friendly textual representations.

Includes:
- Class mapping (Normal / Boss / Guardian)
- Element mapping
- Size mapping
- Race mapping
- Optional runtime warnings for invalid/unmapped values
"""

from __future__ import annotations
from config_loader import config


def _warn(message: str) -> None:
    """Prints a warning only if ENABLE_WARNINGS=True."""
    if config.debug:
        print(f"[WARN] {message}")


# =====================================================================
# CLASS MAPPER
# =====================================================================

def get_class_name(class_id: int) -> str:
    """
    Maps Divine-Pride class → rAthena class → final human-readable string.

    Divine → rAthena index:
        0 → Normal
        1 → Boss
        2 → Boss
        3 → Guardian
        4 → Normal
        5 → Guardian

    Anything outside 0–5 defaults to "Normal".
    """
    mapping_divine_to_rathena = [0, 1, 1, 2, 0, 3]
    names = ["Normal", "Boss", "Guardian"]

    if 0 <= class_id < len(mapping_divine_to_rathena):
        idx = mapping_divine_to_rathena[class_id]
        if 0 <= idx < len(names):
            return names[idx]

    _warn(f"Invalid class_id={class_id}, defaulting to Normal")
    return "Normal"


# =====================================================================
# ELEMENT MAPPER
# =====================================================================

def get_element_name(element_id: int) -> str:
    """
    Maps element ID (0–9) to rAthena element names.

        0 = Neutral
        1 = Water
        2 = Earth
        3 = Fire
        4 = Wind
        5 = Poison
        6 = Holy
        7 = Dark
        8 = Ghost
        9 = Undead

    Anything outside this range defaults to Neutral.
    """
    elements = [
        "Neutral",
        "Water",
        "Earth",
        "Fire",
        "Wind",
        "Poison",
        "Holy",
        "Dark",
        "Ghost",
        "Undead",
    ]

    if 0 <= element_id < len(elements):
        return elements[element_id]

    _warn(f"Invalid element_id={element_id}, defaulting to Neutral")
    return "Neutral"


# =====================================================================
# SIZE MAPPER
# =====================================================================

def get_size_name(size_id: int) -> str:
    """
    Maps size ID to rAthena size:

        0 = Small
        1 = Medium
        2 = Large

    Anything outside this range defaults to Medium.
    """
    sizes = ["Small", "Medium", "Large"]

    if 0 <= size_id < len(sizes):
        return sizes[size_id]

    _warn(f"Invalid size_id={size_id}, defaulting to Medium")
    return "Medium"


# =====================================================================
# RACE MAPPER
# =====================================================================

def get_race_name(race_id: int) -> str:
    """
    Maps race ID (0–9) to rAthena race names.

        0 = Formless
        1 = Undead
        2 = Brute
        3 = Plant
        4 = Insect
        5 = Fish
        6 = Demon
        7 = DemiHuman
        8 = Angel
        9 = Dragon

    Anything outside this range defaults to Formless.
    """
    races = [
        "Formless",
        "Undead",
        "Brute",
        "Plant",
        "Insect",
        "Fish",
        "Demon",
        "DemiHuman",
        "Angel",
        "Dragon",
    ]

    if 0 <= race_id < len(races):
        return races[race_id]

    _warn(f"Invalid race_id={race_id}, defaulting to Formless")
    return "Formless"
