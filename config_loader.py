#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Configuration loader for the Divine-Pride → rAthena converter.

Reads config.yaml, validates structure, normalizes paths and exposes
a single global `config` instance for the rest of the application.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

import yaml


class ConfigError(Exception):
    """Raised when config.yaml is missing or contains invalid data."""
    pass


class Config:
    """
    Holds all configuration values loaded from config.yaml.

    Expected YAML structure (simplified):

    yaml_paths:
      - data/item_db_equip.yml
      - data/item_db_etc.yml
      - data/item_db_usable.yml

    new_paths:
      mob: export/mob_db.yml
      spawn: export/spawns.txt
      skill: export/mob_skill_db.txt

    divine_pride:
      apiBaseUrl: "https://www.divine-pride.net/api/database"
      apiKey: "..."
      monsterApiPrefix: "Monster"
      defaultServer: "iRO"

    mvpDamageTaken: 10
    debug: false
    """

    def __init__(self, config_file: str = "config.yaml") -> None:
        # ------------------------------------------------------------------
        # LOAD RAW YAML
        # ------------------------------------------------------------------
        if not os.path.exists(config_file):
            raise ConfigError(f"config.yaml not found at path: {config_file}")

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                data: Dict[str, Any] = yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ConfigError(f"Failed to parse config.yaml:\n{e}")

        # ------------------------------------------------------------------
        # ITEM DB PATHS (yaml_paths)
        # ------------------------------------------------------------------
        yaml_paths = data.get("yaml_paths", [])
        if not isinstance(yaml_paths, list):
            raise ConfigError("yaml_paths must be a list of file paths.")

        self.yaml_paths: List[str] = [os.path.normpath(p) for p in yaml_paths]

        # Optional legacy key (not used in your current YAML, but kept for safety)
        self.new_yaml_path: str = os.path.normpath(data.get("new_yaml_path", "")) or ""

        # ------------------------------------------------------------------
        # OUTPUT PATHS (new_paths: mob / spawn / skill)
        # ------------------------------------------------------------------
        new_paths: Dict[str, Any] = data.get("new_paths", {})
        if not isinstance(new_paths, dict):
            raise ConfigError("new_paths must be a mapping with mob/spawn/skill paths.")

        self.new_mob_db_path: str = os.path.normpath(new_paths.get("mob", ""))
        self.new_spawns_path: str = os.path.normpath(new_paths.get("spawn", ""))
        self.new_skills_path: str = os.path.normpath(new_paths.get("skill", ""))

        if not self.new_mob_db_path:
            raise ConfigError("new_paths.mob is required in config.yaml")
        if not self.new_spawns_path:
            raise ConfigError("new_paths.spawn is required in config.yaml")
        if not self.new_skills_path:
            raise ConfigError("new_paths.skill is required in config.yaml")

        # ------------------------------------------------------------------
        # DIVINE-PRIDE SECTION
        # ------------------------------------------------------------------
        dp: Dict[str, Any] = data.get("divine_pride", {})
        if not isinstance(dp, dict):
            raise ConfigError("divine_pride section must be a mapping in config.yaml")

        self.divine_pride_api_base_url: str = dp.get("apiBaseUrl", "").rstrip("/")
        self.divine_pride_monster_api_prefix: str = dp.get("monsterApiPrefix", "Monster")
        self.divine_pride_apikey: str | None = dp.get("apiKey")
        self.divine_pride_default_server: str = dp.get("defaultServer", "Renewal")

        if not self.divine_pride_api_base_url:
            raise ConfigError("Missing divine_pride.apiBaseUrl in config.yaml")

        if not self.divine_pride_monster_api_prefix:
            raise ConfigError("Missing divine_pride.monsterApiPrefix in config.yaml")

        if not self.divine_pride_apikey:
            # Not strictly fatal, but Divine-Pride will throttle / limit calls.
            print("[WARN] No divine_pride.apiKey provided. Requests may be limited.")

        # ------------------------------------------------------------------
        # GENERAL SCRIPT CONFIG
        # ------------------------------------------------------------------
        # Support both snake_case (legacy) and camelCase (current)
        mvp_damage_raw = data.get("mvp_damage_taken", data.get("mvpDamageTaken", 10))
        try:
            self.mvp_damage_taken: int = int(mvp_damage_raw)
        except (TypeError, ValueError):
            raise ConfigError("mvpDamageTaken / mvp_damage_taken must be an integer.")

        self.debug: bool = bool(data.get("debug", False))

        # Internal list can be used by the script, but is not required in YAML
        monsters_not_found = data.get("monsters_not_found", [])
        self.monsters_not_found: List[int] = (
            monsters_not_found if isinstance(monsters_not_found, list) else []
        )

    # ----------------------------------------------------------------------
    def __repr__(self) -> str:
        return (
            f"<Config "
            f"yaml_paths={self.yaml_paths}, "
            f"new_mob_db_path='{self.new_mob_db_path}', "
            f"new_spawns_path='{self.new_spawns_path}', "
            f"new_skills_path='{self.new_skills_path}'>"
        )


# Global instance for application-wide use
config = Config()
