# AI Router — route automation task before reading deeply

Read `AI_BOOTSTRAP.md` and `AUTO_TOOL_SCOPE.md` first.

This repository contains:

1. canonical analysis/runtime/action contracts;
2. specialized tool-first static databases; and
3. a structurally-lossless fallback for **all 75 frozen Config tables**.

Future AI must **lookup first, reverse only for a genuinely absent semantic contract or changed client hash**.

## Mandatory compact entrypoints

- `database/TOOL_DATA_INDEX.md` — canonical static/data router.
- `database/TOOL_DATA_MATERIALIZATION_MANIFEST.csv` — specialized generated paths/counts.
- `database/config_full/CONFIG_FULL_CATALOG.csv` — all 75 Config tables and their chunks.
- `AUTO_FEATURE_READINESS.md` — solved/proof/design status.
- `research/AUTO_RUNTIME_PROOF_QUEUE.md` — remaining live/server proofs only.
- `analysis/35_RUNTIME_SNAPSHOT_CONTRACT.md` — per-PID read snapshot model.
- `database/AUTO_TOOL_API_CATALOG.md` — state/query APIs.
- `database/AUTO_TOOL_ACTION_CATALOG.md` — semantic mutations/payloads/proofs.
- `analysis/34_AUTO_STATE_ACTION_PROOF_MATRIX.md` — state/guard/action/proof contract.

## Primary feature routes

| Tool task | Start here | Static lookup when needed |
|---|---|---|
| Tool architecture / multi-client | `contexts/BUILD_TOOL_CORE.md` | feature-specific indexes only |
| Runtime scanner | `contexts/BUILD_RUNTIME_SCANNER.md` | matching domain index |
| MainThread bridge | `contexts/BUILD_MAINTHREAD_BRIDGE.md` | none normally |
| Hidden click / InputSync | `analysis/43_INPUT_SYNC_EXACT_SIGNATURES_AND_UI_LIFECYCLE.md` | `database/PC_INPUTSYNC_METHODS.csv` |
| Auto Train | `contexts/BUILD_AUTO_TRAIN.md` | monsters/skills/items |
| Auto Buff / Nga My | `contexts/BUILD_AUTO_BUFF.md` | skills/magic/NGAMY support data |
| Auto Sell | `contexts/BUILD_AUTO_SELL.md` | items/equips/NPC/vendor |
| NPC Trị liệu | `contexts/BUILD_AUTO_HEAL.md` | NPC + current GameDialog |
| Revive / Đầu thai | `contexts/BUILD_AUTO_REVIVE.md` | no large static DB required |
| Party / follow | `contexts/BUILD_PARTY.md` | targeted lookup only |
| Cross-feature orchestrator | `contexts/BUILD_ORCHESTRATOR.md` | feature-specific indexes |
| Auto FuBen / Boss | `features/AUTO_FUBEN.md`, `analysis/38_FUBEN_BOSS_TASK_TOOL_STACK.md` | `database/fuben/` + monsters |
| Auto PK | `features/AUTO_PK.md`, `analysis/39_PK_AUTOPK_RUNTIME_STACK.md` | skills/factions |
| Dồn đồ / Trade | `features/TRADE_CONSOLIDATION.md`, `analysis/40_TRADE_CONSOLIDATION_RUNTIME_STACK.md` | item/equip policy |
| Use/vứt/hủy/chuyển item | `features/BAG_ITEM_POLICY.md`, `analysis/41_BAG_ITEM_USE_DROP_POLICY_STACK.md` | items/equips/medicines |
| Auto Quest | `analysis/23_TASK_QUEST_AUTOMATION.md` | tasks + NPC/Monster/Map |
| Pet / Spirit | `analysis/24_PET_SPIRIT_AUTO_RUNTIME.md` | pets + skills |
| Storage / bank | `analysis/26_STORAGE_BANK_ITEM_MOVE.md` | item/equip policy |

## Static lookup rules

### NPC / Map / route

Use `database/MAPS.csv`, `database/npcs/`, `database/autopath_npc/`, `AUTOPATH_PORTAL_EDGES.csv`, `NPC_SERVICE_CANDIDATES.md`.

Do not invent live NPC coordinates when `Game.GetNPCPosition(npcID)` exists.

### FuBen / Boss

```text
FUBEN_SCENARIOS
 -> FUBEN_ENTRY_NPCS
 -> FUBEN_ACTIONS_COMPACT
 -> FUBEN_KILL_TARGETS
 -> FUBEN_BOSS_LEVEL_BANDS
 -> one Monster/Boss chunk if needed
```

NPC entry actor != combat Boss.

### Monsters

`database/static/monsters/` contains all 17,121 templates, 3,579 exact Boss templates and a 578-name Boss index. Current spawn/death/RoleID/Position remains runtime truth.

### Skills / Buff / PK

```text
SKILL_TOOL_INDEX chunk
 -> full Skill row if needed
 -> SkillProperties / AutoSkills / MagicAttributes only when needed
 -> current ownership/cooldown/target/range at runtime
```

### Items / Equips

Use `ITEM_TOOL_INDEX`, `ITEM_POLICY_EXCEPTIONS`, `MEDICINES`, `EQUIP_INDEX`, `WEAPON_INDEX`; open full chunks only for deeper fields.

Hard rules:

```text
live dbItemData.ID != template ItemID != Position != Site
Weapon position = EquipPoint == 0
```

### Tasks

```text
TASK_INDEX -> TASK_OBJECTIVES -> one TASKS chunk -> current dbTaskData.Parameters
```

### Pet / Spirit

Use compact indexes first, full chunks second.

### Any other Config table

Do **not** decrypt Config again. Use:

```text
database/config_full/CONFIG_FULL_CATALOG.csv
 -> database/config_full/<Table>/ROWS_*.csv
```

This fallback covers all 75 recovered Config XML tables, including low-frequency guild/title/reputation/mount/progression/cosmetic domains.

## Exact action / packet questions

Start with `database/AUTO_TOOL_ACTION_CATALOG.md`.

Solved action families include Train start/stop, movement/target/chase, skill use, NPC/GameDialog, Sell, item Use/Abandon/Move/Split/Destroy, loot, Revive, Team, Trade and FuBen control.

Packet name/ID alone is not payload proof.

## Hidden click / InputSync — corrected route

Start with:

1. `analysis/43_INPUT_SYNC_EXACT_SIGNATURES_AND_UI_LIFECYCLE.md`
2. `database/PC_INPUTSYNC_METHODS.csv`
3. `analysis/37_INPUT_SYNC_STATIC_EVIDENCE.md` only for discovery/background
4. `analysis/07_SUPPORT_MODULES_LAUNCHER.md` only when launcher/session control matters.

Core exact frozen facts now include:

- `InputSyncManager.TryClickUI(int, Vector2)` token/RVA/native ABI;
- `UpdateUIDrag`, `EndUIDrag`, `CancelUIDragState`, `ResetUIDragState` exact identities;
- `ConvertPos` screen normalization;
- `ParseAndInject -> ConvertPos/InjectMousePos/TryClickUI/UpdateUIDrag/EndUIDrag` direct call path;
- `_uiDragging/_uiDragTarget/_uiDragData` snapshot offsets and cleanup lifecycle.

Correct declaring-type ownership:

```text
FramePressState -> PointerEventData+FramePressState
GetLastPointerEventData -> PointerInputModule
SetSyncState/GetSyncGroupId/SetSyncGroup -> InstanceRegistry
Joystick.InjectSyncInput -> Joystick (Assembly-CSharp-firstpass)
```

Do not search these on `InputSyncManager` just because the names appeared near the same static strings.

For a same-hash machine failure, prioritize declaring type/signature, bootstrap timing, PID/instance state, Screen/window/DPI conversion and drag-state lifecycle before CPU speculation.

## Remaining live-proof route

If static semantics are solved but behavior remains unknown:

1. `AUTO_FEATURE_READINESS.md`
2. `research/AUTO_RUNTIME_PROOF_QUEUE.md`
3. exactly one matching feature doc.

Important live proofs remain:

```text
external managed Action -> MainThread callback
relationship-specific Nga My beneficial-skill acceptance
current healer GameDialog selection/confirmation/result
current vendor dialog -> NpcShopID/ShopID promotion
production Trade/FuBen outcomes when integration needs proof
```

These are runtime/server proofs, not missing static data.

## Data regeneration

Do not manually re-decrypt Config for normal lookup.

Tested reproducible pipeline:

- `tools/materialize_tool_data.py` — specialized tool-first data.
- `tools/materialize_all_config.py` — all 75 Config tables.
- `.github/workflows/materialize-tool-data.yml` — regenerates both and commits changes.

When the frozen Config changes, regenerate and compare; do not restart research from zero.

## Normally out of route

Unless a concrete tool feature depends on them, avoid graphics/D3D/baselib, voice/LiveKit, decorative assets and unrelated systems. If a low-frequency **Config** field is requested, use `config_full` rather than reverse engineering.

## Hard rule

**Lookup -> semantic/runtime contract -> one action -> proof. Reverse native/client code only when the required contract truly does not exist in the KB or the frozen client hashes changed.**
