# 📘 Divine2rAthena  
**Convert Divine-Pride monster data into rAthena-compatible YAML + spawn + mob_skill_db**

Divine2rAthena is a Python tool that fetches monster information from the **Divine-Pride API** and automatically converts everything into standardized **rAthena database files**, including:

- `mob_db.yml`  
- `mob_skill_db.txt`  
- `spawns.txt`  

The tool parses **all metadata**, including stats, drops, MVP drops, spawns, skills, and much more — converting it into clean rAthena-formatted output.

---

# 🚀 Features

### ✔ Fetch data directly from Divine-Pride  
Uses the official API (Monster endpoint).

### ✔ Converts to rAthena-friendly format 
- mob_db (YAML)
- mob_skill_db (TXT)
- spawn entries (TXT)

### ✔ Includes mapping logic for:
- Elements  
- Sizes  
- Races  
- Monster classes  
- Conditions (skill AI)  
- Skill activation triggers  
- Fallback logic for missing values  

### ✔ Outputs clean, valid, formatted files  
Perfect to integrate directly into `db/import/` or your custom server modules.

### ✔ Automatically warns about:
- Missing items in item_db  
- Unmapped skill fields  
- Unmapped conditions  
- Missing Divine-Pride fields  

### ✔ Zero external dependencies beyond what's listed

---

# 📦 Requirements

This project requires:

```
Python 3.10+

PyYAML==6.0.3
requests==2.32.5
```
---

# 🔧 Installation

Clone your repository:

```bash
git https://github.com/eduardoedson/divine2rathena.git
cd divine2rathena
```

Install dependencies:

```bash
pip install -r requirements.txt
```
---

# ⚙ Configuration (config.yaml)

The script reads all settings from `config.yaml`.  
A full example:

```yaml
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
  apiKey: YOUR_API_KEY_HERE
  monsterApiPrefix: "Monster"
  defaultServer: "iRO"

mvpDamageTaken: 10
```

### 📌 What each section means:

#### `yaml_paths`
Paths to your **local rAthena item_db files** – used for resolving AegisNames when generating drops.

#### `new_paths`
Where output files will be written:

| Type | Path | Description |
|------|------|-------------|
| `mob` | mob_db.yml | Exported monster entries |
| `spawn` | spawns.txt | Auto-generated spawn lines |
| `skill` | mob_skill_db.txt | rAthena mob skill definitions |

#### `divine_pride`
API endpoint configuration:
- API key  
- Monster endpoint prefix  
- Server type (`iRO`, `kRO`, `jRO`, etc.)

#### `mvpDamageTaken`
Overrides `DamageTaken` for MVP monsters.

---

# ▶ Usage

Run the program by passing a comma-separated list of monster IDs:

```bash
py main.py 22400,22401,22402
```

or:

```bash
python3 main.py 20595,20596,20597
```

### What the script will do:

1. Load your local item DBs  
2. Fetch each monster from Divine-Pride  
3. Build:
   - YAML mob entry  
   - Spawn lines  
   - Skill AI lines  
4. Export them into your configured output paths  
5. Warn about any missing or unmapped values  

---

# 📁 Output Files

| File | Description |
|------|-------------|
| `export/mob_db.yml` | Clean rAthena monster YAML entries |
| `export/mob_skill_db.txt` | rAthena mob skill definitions |
| `export/spawns.txt` | Spawn lines ready for npc scripts |

---

# 🧠 Internal Architecture

```
/config_loader.py — loads and validates config.yaml
/services/monster.py — handles Divine-Pride API requests
/utils/utils.py — text normalization, fallbacks, parsing
/utils/yaml_helper.py — YAML handling, item lookup, mob_db upsert
/utils/mapper.py — element/size/race/class logic
/utils/spawn_helper.py — generates spawn lines
/utils/skill_helper.py — converts DP skill data → mob_skill_db
/utils/file_helper.py — file IO utilities
main.py — orchestrates everything
```

---

# ⚡ Error Handling

The script prints warnings for:

- Missing items in item_db  
- Unmapped skill fields  
- Unknown conditions or send types  
- Failed API fetch  
- Missing monster data  

This helps you identify incomplete or unsupported Divine-Pride fields so you can manually review or extend mappings.

---

# 🧩 Extending the System

You can extend any part of the tool easily:

### Add new skill conditions  
Modify `KNOWN_CONDITIONS` in `skill_helper.py`.

### Add new send types  
Update `KNOWN_SEND_TYPES`.

### Add new races/classes/sizes  
Modify the tables in `mapper.py`.

### Add item fallbacks  
Modify `yaml_helper.get_drops()`.

The tool is entirely modular and designed to grow.

---

# ❤️ Credits

Created to automate and modernize the import of monsters from **Divine-Pride → rAthena**, following Renewal standards and structured YAML conventions.

Enjoy your fully automated monster converter!
