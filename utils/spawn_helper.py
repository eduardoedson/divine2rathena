#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Helper for building rAthena spawn lines.

rAthena mob spawns follow the format:

    mapname,x,y    monster    DisplayName    MobID,Amount,Delay

This module provides a robust builder that performs validation
and normalization before producing the final spawn line.
"""

from __future__ import annotations
from typing import Any
import utils.utils


# =====================================================================
# SPAWN LINE BUILDER
# =====================================================================

def build_line(
    mapname: str,
    x: Any,
    y: Any,
    mobname: str,
    mobid: Any,
    amount: Any,
    delay: Any
) -> str:
    """
    Builds a valid rAthena spawn line.

    Example output:
        abbey01,0,0    monster    Flame Skull    1869,21,5000

    Notes:
    - Tabs are required by rAthena script engine.
    - mapname and mobname are sanitized into strings.
    - mobid, amount, and delay are safely converted to integers.

    Args:
        mapname (str): Map identifier, e.g. "abbey01"
        x (int): X coordinate (ignored by Divine-Pride, normally 0)
        y (int): Y coordinate
        mobname (str): Monster name shown in spawn
        mobid (int): Monster ID
        amount (int): Number of monsters spawned
        delay (int): Respawn delay in ms

    Returns:
        str: rAthena-compatible spawn line
    """
    mapname = utils.utils._safe_str(mapname)
    mobname = utils.utils._safe_str(mobname)

    x = utils.utils._safe_int(x, 0)
    y = utils.utils._safe_int(y, 0)
    mobid = utils.utils._safe_int(mobid)
    amount = utils.utils._safe_int(amount, 1)
    delay = utils.utils._safe_int(delay, 5000)

    return f"{mapname},{x},{y}\tmonster\t{mobname}\t{mobid},{amount},{delay}"
