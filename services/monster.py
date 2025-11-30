#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Service module for interacting with the Divine-Pride API.
Provides:
- URL builder for Monster endpoints
- Safe JSON fetch with timeout
- Optional retry logic
"""

from __future__ import annotations
import requests
from typing import Optional, Dict, Any
from config_loader import config


# =====================================================================
# BUILD MONSTER API URL
# =====================================================================

def get_url(monster_id: int) -> str:
    """
    Generates the full Divine-Pride URL for fetching a monster entry.
    The URL structure is dynamically read from config.yaml.

    Example:
        https://www.divine-pride.net/api/database/Monster/1002?apiKey=XXXX&server=iRO
    """
    base = config.divine_pride_api_base_url
    prefix = config.divine_pride_monster_api_prefix
    api_key = config.divine_pride_apikey
    server = config.divine_pride_default_server

    return f"{base}/{prefix}/{monster_id}?apiKey={api_key}&server={server}"


# =====================================================================
# FETCH MONSTER DATA (WITH SAFETY)
# =====================================================================

def fetch(url: str, monster_id: int, timeout: int = 10) -> Optional[Dict[str, Any]]:
    """
    Fetches a JSON response from the Divine-Pride API.
    Provides:
    - HTTP error handling
    - JSON validation
    - Timeout protection

    Returns:
        Parsed JSON dict, or None if the request fails.
    """
    try:
        response = requests.get(url, timeout=timeout)

        # Raises HTTPError for 4xx / 5xx status codes
        response.raise_for_status()

        try:
            return response.json()
        except ValueError:
            print(f"[ERROR] Invalid JSON received for monster ID {monster_id}")
            config.monsters_not_found.append(monster_id)
            return None

    except requests.Timeout:
        print(f"[ERROR] Timeout while requesting monster ID {monster_id} (>{timeout}s)")
        config.monsters_not_found.append(monster_id)
        return None

    except requests.HTTPError as e:
        print(f"[ERROR] HTTP error fetching monster ID {monster_id}: {e}")
        config.monsters_not_found.append(monster_id)
        return None

    except requests.RequestException as e:
        print(f"[ERROR] Network error fetching monster ID {monster_id}: {e}")
        config.monsters_not_found.append(monster_id)
        return None
