# 33 — High-value Config coverage — normalization plan CLOSED

Status: **SUPERSEDED AS A TODO; retained as historical prioritization.** The high-value Config domains listed by the original version of this document are now materialized on `main`, and every one of the 75 recovered Config XML tables also has a structurally-lossless fallback database.

Do not use this file as a reason to re-decrypt or re-normalize the frozen client.

Canonical sources:

- `database/TOOL_DATA_INDEX.md` — preferred tool-first lookup router.
- `database/TOOL_DATA_MATERIALIZATION_MANIFEST.csv` — specialized generated database inventory.
- `database/config_full/CONFIG_FULL_CATALOG.csv` — all 75 Config tables.
- `database/config_full/CONFIG_FULL_MANIFEST.csv` — generated fallback file inventory.
- `tools/materialize_tool_data.py` — specialized generator.
- `tools/materialize_all_config.py` — all-table fallback generator.

## Closed priority 1 — Skills semantic stack

Now materialized:

- Skills 2,091
- SkillProperties 2,044
- AutoSkills 300
- Factions 17
- Books 128
- BookLevelUpCost 9
- MagicAttributes 509.

Preferred directory:

`database/static/skills/`

Magic dictionary:

`database/static/magic/MAGIC_ATTRIBUTES.csv`

Use runtime `GetAbilities`, cooldown/target/range state for current action legality.

## Closed priority 2 — Item/equipment policy stack

Now materialized:

- Items 5,238
- Equips 22,763
- Medicines 692
- Gems 1,154
- tool-first keep/sell/drop indexes and full chunks.

Preferred directories:

- `database/static/items/`
- `database/static/equips/`

The static Weapon rule remains `EquipPoint == 0`.

Equipment support tables not promoted into a specialized tool-first file are still available under `database/config_full/<Table>/`.

## Closed priority 3 — Tasks / gathering / activities

Now materialized in specialized form:

- Tasks 516
- Task objectives 591 normalized rows
- GrowPoints 407
- GuildTask 360
- Activities 45.

Preferred directory:

`database/static/tasks/`

Other reward/activity tables are available through `database/config_full/`.

## Closed priority 4 — Pet / Spirit template intelligence

Now materialized:

- Pets 8,349
- Spirits 1,889
- PetFeatures
- PetEquips
- PetEquipSets
- SpiritFeatures.

Preferred directory:

`database/static/pets/`

## Closed priority 5 — lower-frequency Config domains

The earlier document treated guild, role progression, appearance, titles, reputation, mounts and similar tables as future extraction candidates.

They no longer require new extraction work. The all-table fallback now provides every recovered Config table under:

```text
database/config_full/<Table>/ROWS_*.csv
```

Start with:

`database/config_full/CONFIG_FULL_CATALOG.csv`

The catalog records table name, source XML, row count, direct attribute names, nested-child presence, maximum depth and chunk files.

## Closed priority 6 — PC/client Config semantics

`PCInputKeyBinding` is materialized as:

`database/PC_INPUT_KEY_BINDINGS.csv`

The generic source row is also available in `database/config_full/PCInputKeyBinding/`.

For hidden-click/InputSync implementation, Config key bindings are not the canonical action layer. Use:

- `analysis/43_INPUT_SYNC_EXACT_SIGNATURES_AND_UI_LIFECYCLE.md`
- `database/PC_INPUTSYNC_METHODS.csv`.

## All-75 structural preservation rule

`tools/materialize_all_config.py` recovers exactly 75 Config XML TextAssets and stores every top-level row with:

- original direct attribute names/values as explicit CSV columns;
- row tag/index;
- recursive `ChildrenJSON` preserving nested tags, attributes and any non-whitespace text;
- root metadata in `CONFIG_FULL_CATALOG.csv`.

In the current snapshot the catalog reports no non-whitespace XML text nodes outside attributes/child structure, so the fallback preserves the Config semantic tree without requiring another Unity bundle parse.

This is a fallback, not a mandatory context pack. Tool-first specialized indexes remain preferred because they are smaller and have useful joins/derived fields.

## What remains genuinely underexplored

Only investigate further when a real feature needs runtime/server truth not frozen in Config, for example:

- dynamic GameDialog selection IDs;
- current NPC shop IDs/session state;
- server acceptance/rejection of a cast/trade/dungeon action;
- live actor existence/position/death/buffs;
- external MainThread bridge integration.

See `research/TODO.md` and `research/AUTO_RUNTIME_PROOF_QUEUE.md`.

## Hard rule

**The frozen Config extraction/normalization phase is closed. If a future question concerns a static Config table, search `TOOL_DATA_INDEX` then `config_full` before doing any reverse/decrypt work.**
