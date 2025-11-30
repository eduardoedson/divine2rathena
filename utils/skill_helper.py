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
# VALID rATHENA CONDITION TYPES (whitelist)
# Prevents invalid conditions like "1", "abc", etc.
# ---------------------------------------------------------------------
RATHENA_CONDITION_WHITELIST = {
    "myhpltmaxrate",
    "monstersaround",
    "enemycount",
    "rudeattacked",
    "farerangeattacked",
    "magiclocked",
    "groundattacked",
    "skillused",
    "slavereqgt",
    "job",
}

# ---------------------------------------------------------------------
# SUPPORTED SEND TYPES (for emotion/chat/sound)
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
# CONDITION MAPPER
# ---------------------------------------------------------------------
def map_condition(cond: str | None, value: str | None) -> Tuple[str, str, str]:
    """
    Converts a Divine-Pride condition into:
        (condition_type, condition_value, logical_target)

    Returns empty strings if the condition is unknown.
    """
    if not cond:
        return "", "", ""

    cond_key = cond.strip().upper()

    if cond_key not in KNOWN_CONDITIONS:
        print(f"[WARN] Unmapped condition: {cond_key}")
        return "", "", ""

    cond_type, logical_target = KNOWN_CONDITIONS[cond_key]
    cond_value = value or ""

    # Specific Divine-Pride behavior: IF_SLAVENUM defaults to "1"
    if cond_key == "IF_SLAVENUM" and not cond_value:
        cond_value = "1"

    return cond_type, cond_value, logical_target


# ---------------------------------------------------------------------
# SEND-TYPE MAPPER
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
        return str(send_value or ""), "", ""

    return "", "", ""


# ---------------------------------------------------------------------
# BUILD MOB_SKILL_DB LINE
# ---------------------------------------------------------------------
def build_line(mob_id: int, dbname: str, skill: Dict[str, Any]) -> str:
    """
    Converts one Divine-Pride skill entry into an rAthena mob_skill_db row.

    The output format is exactly 19 columns:
        mob_id, state, skill_state, skill_id, level, chance,
        cast, delay, cancelable, target, conditionType, conditionValue,
        val1, val2, val3, val4, emotion, chat, sound
    """

    # Warn about unexpected fields from Divine-Pride
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

    # Basic fields
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

    # Extra safety: ensure valid rAthena condition type
    if cond_type and cond_type not in RATHENA_CONDITION_WHITELIST:
        print(
            f"[WARN] Condition type `{cond_type}` is not recognized by rAthena. "
            f"Clearing invalid condition for mob {mob_id}."
        )
        cond_type = ""
        cond_value = ""

    # Final rAthena target
    rathena_target = CONDITION_TARGET_MAP.get(
        (logical_target or "").lower(),
        "target"
    )

    # Extra values
    idx = skill.get("idx")
    change_to = skill.get("changeTo")

    val1 = str(idx) if idx is not None else ""
    val2 = str(change_to) if change_to is not None else ""
    val3 = ""
    val4 = ""

    # SendType (emote/chat/sound)
    emotion, chat, sound = map_send(
        skill.get("sendType"),
        skill.get("sendValue")
    )

    fields = [
        str(mob_id),      # 1 mob id
        state,            # 2 state
        skill_state,      # 3 skill state
        str(skill_id),    # 4 skill id
        str(level),       # 5 level
        str(chance),      # 6 rate
        str(cast),        # 7 cast time
        str(delay),       # 8 delay
        cancelable,       # 9 cancelable (yes/no)
        rathena_target,   # 10 target
        cond_type,        # 11 condition type
        str(cond_value),  # 12 condition value
        val1,             # 13 val1 (idx)
        val2,             # 14 val2 (changeTo)
        val3,             # 15 val3
        val4,             # 16 val4
        emotion,          # 17 emotion
        chat,             # 18 chat
        sound,            # 19 sound
    ]

    return ",".join(fields)
