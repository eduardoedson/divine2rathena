# -*- coding: utf-8 -*-

"""
Skill converter — Converts Divine-Pride skill blocks
into rAthena mob_skill_db.txt lines.

Handles:
- Condition mapping
- SendType (emotes)
- Unmapped-field warnings
- Safe parsing of all numeric/string fields
- Correct rAthena CSV output format
"""

from __future__ import annotations
from typing import Dict, Any, Tuple
import utils.utils

# =====================================================================
# EXPECTED DP FIELDS  (for unmapped-field warnings)
# =====================================================================
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


# =====================================================================
# CONDITION MAP (DP → rAthena)
# =====================================================================
KNOWN_CONDITIONS: Dict[str, Tuple[str, str]] = {
    "IF_HP": ("myhpltmaxrate", "self"),
    "IF_MONSTERCOUNT": ("monstersaround", "self"),
    "IF_ENEMYCOUNT": ("enemycount", "enemy"),
    "IF_RUDEATTACK": ("rudeattacked", "enemy"),
    "IF_RANGEATTACKED": ("farerangeattacked", "enemy"),
    "IF_MAGICLOCKED": ("magiclocked", "self"),
    "IF_GROUNDATTACKCHECK": ("groundattacked", "self"),
    "IF_SKILLUSE": ("skillused", "enemy"),
    "IF_SLAVENUM": ("slavereqgt", "self"),
    "IF_JOBCHECK": ("job", "enemy"),
}


# =====================================================================
# SENDTYPE MAP
# =====================================================================
KNOWN_SEND_TYPES = {
    "SEND_EMOTICON",
}


# =====================================================================
# CONDITION CONVERTER
# =====================================================================

def map_condition(cond: str | None, value: str | None) -> Tuple[str, str, str]:
    """
    Converts Divine-Pride conditions → rAthena triplet:
        (condType, condValue, target)
    """
    if not cond:
        return "", "", ""

    cond = cond.strip().upper()

    if cond not in KNOWN_CONDITIONS:
        print(f"[WARN] Unmapped condition: {cond}")
        return "", "", ""

    cond_type, target = KNOWN_CONDITIONS[cond]
    val = value or ""

    if cond == "IF_SLAVENUM" and not val:
        val = "1"

    return cond_type, str(val), target


# =====================================================================
# SENDTYPE MAPPER
# =====================================================================

def map_send(send_type: str | None, send_value: str | None) -> Tuple[str, str, str]:
    """
    rAthena format supports:
        emotion, chat, sound
    """
    if not send_type:
        return "", "", ""

    st = send_type.strip().upper()

    if st not in KNOWN_SEND_TYPES:
        print(f"[WARN] Unmapped sendType: {st}")
        return "", "", ""

    if st == "SEND_EMOTICON":
        return (str(send_value or "0"), "", "")

    return "", "", ""


# =====================================================================
# BUILD rAthENA SKILL LINE
# =====================================================================

def build_line(mob_id: int, dbname: str, skill: Dict[str, Any]) -> str:
    """
    Converts one Divine-Pride skill block into a rAthena mob_skill_db entry.

    Output example:
        20595,MINERAL R@RUSH_ST,attack,28,5,2000,0,3000,yes,friend,myhpltmaxrate,90,,,,,,,
    """

    # Warn about unused fields (typo detection)
    for field in skill.keys():
        if field not in EXPECTED_SKILL_FIELDS:
            print(f"[WARN] Unmapped skill field `{field}` in mob {mob_id}")

    # Status / State
    status = utils.utils._safe_str(skill.get("status") or "IDLE_ST")
    state = f"{dbname}@{status}"
    skill_state = "attack"

    # Numeric fields (safe parsed)
    skill_id = utils.utils._safe_int(skill.get("skillId"), 0)
    level = utils.utils._safe_int(skill.get("level"), 1)
    chance = utils.utils._safe_int(skill.get("chance"), 100)
    cast = utils.utils._safe_int(skill.get("casttime"), 0)
    delay = utils.utils._safe_int(skill.get("delay"), 0)

    # Cancelable flag
    interruptable = bool(skill.get("interruptable", True))
    cancelable = "yes" if interruptable else "no"

    # Condition
    cond_type, cond_value, target = map_condition(
        skill.get("condition"),
        skill.get("conditionValue"),
    )

    # Internal DP fields
    val1 = utils.utils._safe_str(skill.get("idx") or "")
    val2 = utils.utils._safe_str(skill.get("changeTo") or "")
    val3 = ""
    val4 = ""

    # SendType (emotion/chat/sound)
    emotion, chat, sound = map_send(
        skill.get("sendType"),
        skill.get("sendValue"),
    )

    # rAthena CSV fields
    fields = [
        str(mob_id),
        state,
        skill_state,
        str(skill_id),
        str(level),
        str(chance),
        str(cast),
        str(delay),
        cancelable,
        target,
        cond_type,
        cond_value,
        val1,
        val2,
        val3,
        val4,
        emotion,
        chat,
        sound,
    ]

    return ",".join(fields)
