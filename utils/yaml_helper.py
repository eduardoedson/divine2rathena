#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
YAML helpers for Divine-Pride → rAthena conversion.

Responsibilities:
- Load YAML files safely (item DBs and mob DB).
- Cache item DBs in memory to speed up repeated lookups.
- Map Divine-Pride drop structures into rAthena-style drop entries.
- Initialize, load and save rAthena mob_db.yml with correct indentation.
- Upsert (insert/update) monsters into the mob DB.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import yaml

from config_loader import config


# =====================================================================
# YAML LOADING
# =====================================================================

def load_yaml(path: str) -> Optional[Dict[str, Any]]:
    """
    Safely loads a YAML file from the given path.

    Returns:
        dict with YAML contents, or None if file is missing or invalid.
    """
    if not os.path.exists(path):
        print(f"[WARN] File not found: {path}")
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"[ERROR] Failed to parse YAML `{path}`:\n{e}")
        return None

    if data is None:
        data = {}

    return data


# =====================================================================
# ITEM SEARCH IN YAML ITEM DBs
# =====================================================================

# Simple cache to avoid reloading the same YAML files multiple times
_item_cache: Dict[str, Optional[Dict[str, Any]]] = {}


def search_item(item_id: int) -> Optional[Dict[str, Any]]:
    """
    Searches the configured item DB YAMLs (config.yaml_paths) for a given item ID.

    Uses an internal cache so each YAML file is only loaded once.

    Args:
        item_id: Item ID to search for.

    Returns:
        The matching item dict (entry from Body) or None if not found.
    """
    for path in config.yaml_paths:
        if path not in _item_cache:
            _item_cache[path] = load_yaml(path)

        data = _item_cache[path]
        if not data:
            continue

        body: List[Dict[str, Any]] = data.get("Body", []) or []
        for entry in body:
            if entry.get("Id") == item_id:
                return entry

    return None


# =====================================================================
# DROPS PROCESSING
# =====================================================================

def get_drops(items: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Converts Divine-Pride drop entries into rAthena-friendly YAML drops.

    Expected Divine-Pride drop structure (per item):
        {
            "itemId": 7321,
            "chance": 1500,
            "stealProtected": false,
            ...
        }

    Output rAthena-style structure (per entry):
        {
            "Item": "AegisName",
            "Rate": 1500,
            "StealProtected": True/False
        }

    Args:
        items: List of Divine-Pride drop dictionaries.

    Returns:
        List of normalized drop dictionaries suitable for mob_db YAML.
    """
    if not items:
        return []

    drops: List[Dict[str, Any]] = []

    for item in items:
        item_id_raw = item.get("itemId")
        if not item_id_raw:
            continue

        # Validate / normalize itemId
        try:
            item_id = int(item_id_raw)
        except (TypeError, ValueError):
            print(f"[WARN] Invalid itemId: {item_id_raw}")
            continue

        # Look up item in item DB YAMLs
        result = search_item(item_id)
        if not result:
            print(f"[WARN] Item ID {item_id} not found in item DB.")
            continue

        # chance → Rate
        try:
            rate = int(item.get("chance", 10))
        except (TypeError, ValueError):
            rate = 10
        if rate <= 0:
            rate = 10

        steal_protected = bool(item.get("stealProtected", False))

        drop = {
            "Item": result.get("AegisName"),
            "Rate": rate,
            "StealProtected": steal_protected,
        }
        drops.append(drop)

    return drops


# =====================================================================
# CREATE NEW mob_db EXPORT YAML
# =====================================================================

def init_export_yaml(path: str) -> None:
    """
    Deletes the old export file (if it exists) and creates a fresh,
    valid rAthena mob_db.yml with empty Body.

    The resulting structure is:

        Header:
          Type: MOB_DB
          Version: 2
        Body: []
    """
    if os.path.exists(path):
        print(f"[INFO] Removing existing export file: {path}")
        os.remove(path)

    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    data: Dict[str, Any] = {
        "Header": {
            "Type": "MOB_DB",
            "Version": 2,
        },
        "Body": [],
    }

    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)

    print(f"[INFO] Created fresh export YAML: {path}")


# =====================================================================
# LOAD mob_db (FOR UPSERT)
# =====================================================================

def load_monster_db(path: str) -> Dict[str, Any]:
    """
    Loads the monster DB YAML or creates a valid empty structure if missing.

    Ensures the result has:
        - Header.Type = MOB_DB
        - Header.Version = 2
        - Body = list
    """
    if not os.path.exists(path):
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        return {
            "Header": {
                "Type": "MOB_DB",
                "Version": 2,
            },
            "Body": [],
        }

    try:
        with open(path, "r", encoding="utf-8") as f:
            data: Dict[str, Any] = yaml.safe_load(f) or {}
    except yaml.YAMLError as e:
        print(f"[ERROR] Failed to parse monster DB YAML `{path}`:\n{e}")
        data = {}

    # Ensure required structure
    data.setdefault("Header", {"Type": "MOB_DB", "Version": 2})
    data.setdefault("Body", [])

    return data


# =====================================================================
# DUMPER WITH rAthena-LIKE INDENTATION
# =====================================================================

class IndentDumper(yaml.Dumper):
    """
    Custom Dumper that disables 'indentless' sequences, producing:

        Body:
          - Id: 1001
            AegisName: SCORPION

    instead of:

        Body:
        - Id: 1001
          AegisName: SCORPION
    """
    def increase_indent(self, flow: bool = False, indentless: bool = False):
        return super().increase_indent(flow, False)


def save_monster_db(path: str, data: Dict[str, Any]) -> None:
    """
    Writes the monster DB YAML file using IndentDumper to mimic rAthena style.
    """
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(
            data,
            f,
            Dumper=IndentDumper,
            allow_unicode=True,
            sort_keys=False,
        )


# =====================================================================
# UPSERT: ADD OR UPDATE A MONSTER IN mob_db
# =====================================================================

def upsert_monster(entry: Dict[str, Any], path: Optional[str]) -> bool:
    """
    Inserts or updates a monster entry inside MOB_DB.

    Args:
        entry: Monster YAML block to insert/update (must contain "Id").
        path:  Path to mob_db.yml; if None, falls back to config.new_yaml_path.

    Returns:
        True if an existing entry was updated, False if a new entry was added.
    """
    if path is None:
        path = config.new_yaml_path

    db = load_monster_db(path)
    body: List[Dict[str, Any]] = db.get("Body", [])
    mob_id = entry.get("Id")

    updated = False

    # Try to update an existing entry
    for i, mob in enumerate(body):
        if mob.get("Id") == mob_id:
            body[i] = entry
            updated = True
            break

    # If not found, append as a new entry
    if not updated:
        body.append(entry)

    db["Body"] = body
    save_monster_db(path, db)

    return updated
