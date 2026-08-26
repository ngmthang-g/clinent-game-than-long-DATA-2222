# Database navigation index

> Machine/AI-readable knowledge derived from the frozen client's Config/Interface/Lua/runtime/native evidence. Primary purpose: support the Thần Long automation tool without repeating solved client reverse work.

## Start here

Canonical static router:

`TOOL_DATA_INDEX.md`

Implementation/runtime references:

- `AUTO_TOOL_API_CATALOG.md`
- `AUTO_TOOL_ACTION_CATALOG.md`
- `SUBSYSTEM_SOURCE_MAP.md`
- `SEMANTIC_JOIN_MAP.md`
- `FACTS.jsonl`
- `TOOL_DATA_MATERIALIZATION_MANIFEST.csv`.

All Config fallback:

- `config_full/README.md`
- `config_full/CONFIG_FULL_CATALOG.csv`
- `config_full/CONFIG_FULL_MANIFEST.csv`.

Normal route:

```text
AI_BOOTSTRAP
 -> AUTO_TOOL_SCOPE
 -> AI_ROUTER
 -> one feature/context pack
 -> TOOL_DATA_INDEX for static lookup
 -> config_full only if the specialized layer lacks the field/table
```

## Static Config foundation is closed

The frozen snapshot now has two generated layers.

### Specialized tool-first layer

Includes:

- 17,121 Monsters / 3,579 Boss templates / 578 Boss names;
- 22,763 Equips / 4,685 Weapon-position templates;
- 5,238 Items / 692 Medicines / 1,154 Gems;
- 2,091 Skills / 2,044 SkillProperties / 300 AutoSkills / 509 MagicAttributes;
- 516 Tasks / 591 objectives / 407 GrowPoints / 360 GuildTasks / 45 Activities;
- 8,349 Pets / 1,889 Spirits;
- full FuBen scenario/action/kill/entry/level-band data;
- 22 PC key bindings.

Exact paths/counts: `TOOL_DATA_MATERIALIZATION_MANIFEST.csv`.

### All-75 fallback layer

Every recovered Config XML table is available under:

```text
config_full/<Table>/ROWS_*.csv
```

Use `config_full/CONFIG_FULL_CATALOG.csv` to find table fields/chunks.

This covers low-frequency domains too. Do not decrypt Config again just because a table is outside the specialized tool-first directories.

## World / NPC / route

- `MAPS.csv` — 193 maps.
- `npcs/NPCS_*.csv` — all 1,003 NPC templates.
- `autopath_npc/AUTOPATH_NPC_EDGES_*.csv`
- `AUTOPATH_PORTAL_EDGES.csv`
- `AUTOPATH_ITEM_DESTINATIONS.csv`
- `NPC_SERVICE_CANDIDATES.md`.

Static NPC identity does not replace current `Game.GetNPCPosition`, live dialog or shop state.

## FuBen / Boss

Use `fuben/` in this order:

```text
FUBEN_SCENARIOS
 -> FUBEN_ENTRY_NPCS
 -> FUBEN_ACTIONS_COMPACT
 -> FUBEN_KILL_TARGETS
 -> FUBEN_BOSS_LEVEL_BANDS
 -> full action/Monster chunk if needed
```

Entry NPC != combat Boss.

## Items / Equips

Items: `static/items/`.

Equips: `static/equips/`.

Hard rules:

```text
live instance ID != template ItemID != Position != Site
Weapon position = EquipPoint == 0
```

## Skills / Buff / PK

Use `static/skills/` and `static/magic/`.

Static identity/range/property is not current ownership/cooldown/server acceptance.

## Tasks / Quest

Use `static/tasks/` then current runtime task Parameters.

## Pets / Spirits

Use `static/pets/`; current companion state/action remains runtime truth.

## Protocol / actions

Before tracing a request, check:

- `AUTO_TOOL_ACTION_CATALOG.md`
- `PACKET_IDS.csv`
- `NETWORK_COMMAND_CATALOG.md`.

Packet ID existence alone is not request-payload proof.

## PC InputSync / hidden click

Canonical exact implementation evidence:

- `PC_INPUTSYNC_METHODS.csv`
- `../analysis/43_INPUT_SYNC_EXACT_SIGNATURES_AND_UI_LIFECYCLE.md`.

Discovery/background:

- `../analysis/37_INPUT_SYNC_STATIC_EVIDENCE.md`.

Key corrected ownership:

```text
TryClickUI + UI drag methods -> InputSyncManager
SetSyncState/GetSyncGroupId/SetSyncGroup -> InstanceRegistry
FramePressState -> PointerEventData+FramePressState
GetLastPointerEventData -> PointerInputModule
Joystick.InjectSyncInput -> Joystick / Assembly-CSharp-firstpass
```

The frozen hidden-click static signature/ABI/lifecycle is solved. Same-hash machine failures should be debugged as resolver/bootstrap/PID/window/DPI/EventSystem/drag-state integration issues first.

## Regeneration

Source:

`../Game/Thần Long  Mobile_Data/StreamingAssets/Config.unity3d`

Generators:

- `../tools/materialize_tool_data.py`
- `../tools/materialize_all_config.py`.

Workflow:

`../.github/workflows/materialize-tool-data.yml`.

GitHub Actions has successfully regenerated both layers. Future snapshot changes should regenerate/compare rather than hand-edit large data or restart reverse work.

## Interpretation rule

Static data = frozen template/configured truth.

Runtime/server = current instance/spawn/dialog/session/acceptance/completion truth.

Remaining live gaps are tracked only in `research/AUTO_RUNTIME_PROOF_QUEUE.md` and `research/TODO.md`.
