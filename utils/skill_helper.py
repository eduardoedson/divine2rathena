#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Skill converter — Converts Divine-Pride skill blocks
into rAthena mob_skill_db.txt lines.

Input (Divine-Pride JSON `skill` entry) example:

{
    "idx": 39196,
    "skillId": 26,
    "status": "RUSH_ST",
    "level": 5,
    "chance": 700,
    "casttime": 0,
    "delay": 10000,
    "interruptable": true,
    "changeTo": null,
    "condition": "IF_MONSTERCOUNT",
    "conditionValue": "19",
    "sendType": null,
    "sendValue": null
}

Output example (mob_skill_db.txt line):

20595,MINERAL_R@AL_HEAL,attack,28,5,2000,0,3000,yes,friend,myhpltmaxrate,90,,,,,,,

Columns (rAthena mob_skill_db.txt):

 1  Mob ID
 2  State (e.g. MINERAL_R@BERSERK_ST)
 3  Skill state (attack / idle / chase / etc.) — we use "attack" by default
 4  Skill ID
 5  Skill Level
 6  Rate / Chance
 7  Cast time (ms)
 8  Delay (ms)
 9  Cancelable (yes/no)
10  Target
11  Condition type
12  Condition value
13  Val1
14  Val2
15  Val3
16  Val4
17  Emotion
18  Chat
19  Sound
"""

from typing import Any, Dict, Tuple

# ---------------------------------------------------------------------
# EXPECTED FIELDS (for WARN of unmapped fields)
# ---------------------------------------------------------------------
EXPECTED_SKILL_FIELDS = {
    "idx",
    "skillId",
    "status",
    "level",
    "chance",
    "casttime",
    "delay",
    "interruptable",
    "changeTo",
    "condition",
    "conditionValue",
    "sendType",
    "sendValue",
}

# ---------------------------------------------------------------------
# CONDITION MAPPING
# ---------------------------------------------------------------------
# Maps Divine-Pride "condition" to:
#   (condition_type, logical_target)
#
# logical_target is an internal helper ("self" / "enemy") that we later
# convert to rAthena-supported targets ("self" / "target").
KNOWN_CONDITIONS = {
    "IF_HP": ("myhpltmaxrate", "self"),
    "IF_MONSTERCOUNT": ("monstersaround", "self"),
    "IF_ENEMYCOUNT": ("enemycount", "target"),
    "IF_RUDEATTACK": ("rudeattacked", "target"),
    "IF_RANGEATTACKED": ("farerangeattacked", "target"),
    "IF_MAGICLOCKED": ("magiclocked", "self"),
    "IF_GROUNDATTACKCHECK": ("groundattacked", "self"),
    "IF_SKILLUSE": ("skillused", "target"),
    "IF_SLAVENUM": ("slavereqgt", "self"),
    "IF_JOBCHECK": ("job", "target"),
}

# ---------------------------------------------------------------------
# SEND TYPE MAPPING
# ---------------------------------------------------------------------
KNOWN_SEND_TYPES = {
    "SEND_EMOTICON",
}

# ---------------------------------------------------------------------
# LOGICAL TARGET → rAthena TARGET MAPPING
# ---------------------------------------------------------------------
# rAthena valid targets include: "self", "friend", "target", "random",
# "area", "around5", etc. For our generic converter:
#
# - logical "self"   → rAthena "self"
# - logical "enemy"  → rAthena "target"
# - logical "target" → rAthena "target"
#
# If nothing is defined, we default to "target" to avoid warnings like:
#   mob_parse_row_mobskilldb: Unrecognized target  for <mob_id>
CONDITION_TARGET_MAP = {
    "self": "self",
    "enemy": "target",
    "target": "target",
}


# ---------------------------------------------------------------------
# CONDITION CONVERTER
# ---------------------------------------------------------------------
def map_condition(cond: str | None, value: str | None) -> Tuple[str, str, str]:
    """
    Converts Divine-Pride condition into:
        (condition_type, condition_value, logical_target)

    logical_target is later translated to a valid rAthena target.
    """
    if not cond:
        return "", "", ""

    cond = cond.strip().upper()

    if cond not in KNOWN_CONDITIONS:
        print(f"[WARN] Unmapped condition: {cond}")
        return "", "", ""

    cond_type, logical_target = KNOWN_CONDITIONS[cond]
    cond_value = value or ""

    # Special case: IF_SLAVENUM without value defaults to "1"
    if cond == "IF_SLAVENUM" and not cond_value:
        cond_value = "1"

    return cond_type, cond_value, logical_target


# ---------------------------------------------------------------------
# SEND TYPE CONVERTER
# ---------------------------------------------------------------------
def map_send(send_type: str | None, send_value: str | None) -> Tuple[str, str, str]:
    """
    Converts Divine-Pride sendType/sendValue into three columns:
        (emotion, chat, sound)

    For now only SEND_EMOTICON is mapped; others will warn and return empty.
    """
    if not send_type:
        return "", "", ""

    st = send_type.strip().upper()

    if st not in KNOWN_SEND_TYPES:
        print(f"[WARN] Unmapped sendType: {st}")
        return "", "", ""

    if st == "SEND_EMOTICON":
        # rAthena emotion field
        return str(send_value or ""), "", ""

    return "", "", ""


# ---------------------------------------------------------------------
# BUILD SKILL LINE
# ---------------------------------------------------------------------
def build_line(mob_id: int, dbname: str, skill: Dict[str, Any]) -> str:
    """
    Builds one mob_skill_db line from a Divine-Pride skill entry.

    Returns a CSV string with 19 fields, compatible with rAthena's
    db/re/mob_skill_db.txt format.
    """
    # Warn for unmapped/surprising fields to help debugging
    for key in skill.keys():
        if key not in EXPECTED_SKILL_FIELDS:
            print(f"[WARN] Unmapped skill field `{key}` in mob {mob_id}")

    # State name uses Divine-Pride status + monster dbname
    # Example: "MINERAL_R@BERSERK_ST"
    status = (skill.get("status") or "IDLE_ST").strip()
    state = f"{dbname}@{status}"

    # rAthena "skill state" column (usually attack / idle / chase etc.)
    # For now, we use "attack" as a generic default.
    skill_state = "attack"

    # Basic numeric fields
    skill_id = int(skill.get("skillId") or 0)
    level = int(skill.get("level") or 1)
    chance = int(skill.get("chance") or 100)
    cast = int(skill.get("casttime") or 0)
    delay = int(skill.get("delay") or 0)

    # Cancelable flag
    interruptable = bool(skill.get("interruptable", True))
    cancelable = "yes" if interruptable else "no"

    # Condition (type, value, logical target)
    cond_type, cond_value, logical_target = map_condition(
        skill.get("condition"),
        skill.get("conditionValue"),
    )

    # Map logical target → rAthena target
    # If nothing defined, we default to "target" to avoid warnings.
    rathena_target = CONDITION_TARGET_MAP.get(
        (logical_target or "").lower(),
        "target",
    )

    # Extra values (Val1–Val4)
    idx = skill.get("idx")
    change_to = skill.get("changeTo")

    val1 = str(idx) if idx is not None else ""
    val2 = str(change_to) if change_to is not None else ""
    val3 = ""
    val4 = ""

    # Send/Emotion/Chat/Sound
    emotion, chat, sound = map_send(
        skill.get("sendType"),
        skill.get("sendValue"),
    )

    fields = [
        str(mob_id),          #  1 Mob ID
        state,                #  2 State
        skill_state,          #  3 Skill state
        str(skill_id),        #  4 Skill ID
        str(level),           #  5 Skill Lv
        str(chance),          #  6 Rate
        str(cast),            #  7 Cast Time
        str(delay),           #  8 Delay
        cancelable,           #  9 Cancelable
        rathena_target,       # 10 Target
        cond_type,            # 11 Condition type
        str(cond_value),      # 12 Condition value
        val1,                 # 13 Val1 (idx)
        val2,                 # 14 Val2 (changeTo)
        val3,                 # 15 Val3
        val4,                 # 16 Val4
        emotion,              # 17 Emotion
        chat,                 # 18 Chat
        sound,                # 19 Sound
    ]

    return ",".join(fields)
