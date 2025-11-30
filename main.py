#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main script responsible for:
- Fetching monsters from Divine-Pride API
- Converting the data into rAthena-friendly YAML
- Generating spawn entries
- Generating mob_skill_db entries
- Writing all outputs to the files configured in config.yaml
"""

from __future__ import annotations

import sys
from typing import Any, Dict, List, Optional

# Internal modules
from config_loader import config
import services.monster

import utils.file_helper
import utils.mapper
import utils.skill_helper
import utils.spawn_helper
import utils.utils
import utils.yaml_helper


# =====================================================================
# YAML CORE BUILDER
# =====================================================================
def _build_yml_core(
    json_data: Dict[str, Any],
    stats: Dict[str, Any],
    monster_id: int,
    is_mvp: bool,
) -> Dict[str, Any]:
    """
    Builds the core YAML block for one monster.
    This includes stats, movement, combat parameters, AI flags, etc.
    """
    return {
        "Id": monster_id,
        "AegisName": json_data.get("sprite") or f"MOB_{monster_id}",
        "Name": utils.utils.normalize_dbname(json_data.get("dbname", "")),

        # Stats with fallback logic
        "Level": utils.utils.value_fallback(stats.get("level"), 250),
        "Hp": utils.utils.value_fallback(stats.get("health"), 2_500_000),
        "Sp": utils.utils.value_fallback(stats.get("sp"), 10_000),

        "BaseExp": utils.utils.value_fallback(stats.get("baseExperience"), 3000000),
        "JobExp": utils.utils.value_fallback(stats.get("jobExperience"), 3000000),

        "Attack": utils.utils.value_fallback(stats.get("atk1"), 500),
        "Attack2": utils.utils.value_fallback(stats.get("atk2"), 300),

        "Defense": utils.utils.value_fallback(stats.get("defense"), 1000),
        "MagicDefense": utils.utils.value_fallback(stats.get("magicDefense"), 600),

        "Resistance": utils.utils.value_fallback(stats.get("res"), 500),
        "MagicResistance": utils.utils.value_fallback(stats.get("mres"), 300),

        "Str": utils.utils.value_fallback(stats.get("str"), 200),
        "Agi": utils.utils.value_fallback(stats.get("agi"), 200),
        "Vit": utils.utils.value_fallback(stats.get("vit"), 200),
        "Int": utils.utils.value_fallback(stats.get("int"), 200),
        "Dex": utils.utils.value_fallback(stats.get("dex"), 200),
        "Luk": utils.utils.value_fallback(stats.get("luk"), 200),

        "AttackRange": utils.utils.value_fallback(stats.get("attackRange"), 1),
        "SkillRange": utils.utils.value_fallback(stats.get("skillRange"), 10),
        "ChaseRange": utils.utils.value_fallback(stats.get("aggroRange"), 12),

        "Size": utils.mapper.get_size_name(utils.utils.positive(stats.get("scale"))),
        "Race": utils.mapper.get_race_name(utils.utils.positive(stats.get("race"))),

        "Element": utils.mapper.get_element_name(
            utils.utils.positive(stats.get("element", 0) % 20) if stats.get("element", 0) else 0
        ),
        "ElementLevel": utils.utils.positive(stats.get("element", 0) // 20 if stats.get("element", 0) else 1) or 1,

        "WalkSpeed": utils.utils.value_fallback(stats.get("movementSpeed"), 100),
        "AttackDelay": utils.utils.value_fallback(stats.get("attackSpeed"), 500),
        "AttackMotion": utils.utils.value_fallback(stats.get("attackedSpeed"), 700),
        "ClientAttackMotion": utils.utils.value_fallback(stats.get("attackedSpeed"), 700),
        "DamageMotion": utils.utils.value_fallback(stats.get("attackedSpeed"), 700),

        "DamageTaken": config.mvp_damage_taken if is_mvp else 100,
        "Ai": utils.utils.positive((stats.get("ai") or "MONSTER_TYPE_21").split("_")[-1]),

        "class": utils.mapper.get_class_name(int(stats.get("class") or 0)),
    }


# =====================================================================
# ATTACH DROPS
# =====================================================================
def _attach_drops(
    yml: Dict[str, Any],
    json_data: Dict[str, Any],
    is_mvp: bool,
) -> None:
    """
    Adds Drops and MvpDrops to the monster YAML block.
    """
    # MVP section
    if is_mvp:
        yml["Modes"] = {"Mvp": True}

        mvp_items = json_data.get("mvpdrops", [])
        mvp_drops = utils.yaml_helper.get_drops(mvp_items)
        if mvp_drops:
            yml["MvpDrops"] = mvp_drops

    # Normal drops
    normal_drops = utils.yaml_helper.get_drops(json_data.get("drops", []))
    if normal_drops:
        yml["Drops"] = normal_drops


# =====================================================================
# BUILD FULL YAML MONSTER ENTRY
# =====================================================================
def mount_monster_yaml(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Combines the monster core block + drops into a full YAML entry.
    Returns an empty dict if the monster ID is invalid.
    """
    try:
        monster_id = int(json_data.get("id"))
    except Exception:
        return {}

    if not monster_id:
        return {}

    stats: Dict[str, Any] = json_data.get("stats", {})
    is_mvp: bool = int(stats.get("mvp") or 0) == 1

    yml = _build_yml_core(json_data, stats, monster_id, is_mvp)
    _attach_drops(yml, json_data, is_mvp)
    return yml


# =====================================================================
# SPAWN GENERATION
# =====================================================================
def generate_spawn(monster_id: int, json_data: Dict[str, Any]) -> None:
    """
    Converts Divine-Pride spawn data into rAthena spawn lines
    and appends them to the configured spawn file.
    """
    spawns = json_data.get("spawn", [])
    if not spawns:
        return

    for spawn in spawns:
        try:
            line = utils.spawn_helper.build_line(
                spawn.get("mapname", ""),
                0,
                0,
                utils.utils.normalize_dbname(json_data.get("dbname", "")),
                monster_id,
                spawn.get("amount", 50),
                spawn.get("respawnTime", 5000),
            )
            utils.file_helper.append_line(config.new_spawns_path, line)
        except Exception as e:
            print(f"[ERROR] Failed to generate spawn for {monster_id}: {e}")


# =====================================================================
# SKILL GENERATION
# =====================================================================
def generate_skills(monster_id: int, json_data: Dict[str, Any]) -> None:
    """
    Converts Divine-Pride skill blocks into rAthena mob_skill_db lines
    and appends them to the configured skill DB file.
    """
    skills = json_data.get("skill", [])
    if not skills:
        return

    name = utils.utils.normalize_dbname(json_data.get("dbname", ""))

    for skill in skills:
        try:
            line = utils.skill_helper.build_line(
                monster_id,
                name,
                skill,
            )
            utils.file_helper.append_line(config.new_skills_path, line)
        except Exception as e:
            print(f"[ERROR] Failed to generate skill for {monster_id}: {e}")


# =====================================================================
# MONSTER YAML GENERATOR
# =====================================================================
def generate_monster(monster_id: int, json_data: Optional[Dict[str, Any]]) -> None:
    """
    Saves the monster entry into mob_db.yml or records it as missing.
    """
    yml = mount_monster_yaml(json_data)
    if not yml:
        print(f"[WARN] Monster ID {monster_id} produced an empty YAML entry.")
        return

    utils.yaml_helper.upsert_monster(yml, config.new_mob_db_path)


# =====================================================================
# MAIN EXECUTION
# =====================================================================
def main() -> None:
    """
    Entry point of the application.
    Handles CLI parsing, API fetching, and output generation.
    """
    if len(sys.argv) != 2:
        print("Usage:\n  python main.py <id,id,id,...>")
        sys.exit(1)

    # Parse input IDs
    try:
        monster_ids: List[int] = [
            int(x.strip()) for x in sys.argv[1].split(",") if x.strip()
        ]
    except Exception:
        print("[ERROR] Invalid monster ID list. Example:\n  python main.py 22399,22400,22401")
        sys.exit(1)

    if not monster_ids:
        print("[ERROR] No valid monster IDs provided.")
        sys.exit(1)

    print(f"Fetching monsters: {monster_ids}")

    # Reset output files
    utils.yaml_helper.init_export_yaml(config.new_mob_db_path)
    utils.file_helper.init_file(config.new_spawns_path)
    utils.file_helper.init_file(config.new_skills_path)

    # Fetch & process
    for monster_id in monster_ids:
        url = services.monster.get_url(monster_id)
        if config.debug:
            print(f"[DEBUG] Fetching {monster_id} from URL: {url}")

        json_data = services.monster.fetch(url, monster_id)
        if json_data:
            generate_monster(monster_id, json_data)
            generate_spawn(monster_id, json_data)
            generate_skills(monster_id, json_data)

    print(f"\nDone.\n   {len(monster_ids) - len(config.monsters_not_found)} created.")
    if config.monsters_not_found:
        print(f"Monsters not found: {config.monsters_not_found}")


# =====================================================================
# EXECUTE
# =====================================================================
if __name__ == "__main__":
    main()
