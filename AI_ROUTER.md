# AI Router — route automation task before reading deeply

Read `AI_BOOTSTRAP.md` and `AUTO_TOOL_SCOPE.md` first.

This repository now contains both:

1. canonical analysis/runtime/action contracts; and
2. a fully materialized frozen Config lookup database.

Future AI should **lookup first, reverse only for a genuinely absent semantic contract**.

## Mandatory compact entrypoints

Use these before broad analysis:

- `database/TOOL_DATA_INDEX.md` — **canonical static/data lookup router** for NPC/Map/FuBen/Boss/Monster/Task/Item/Equip/Skill/Pet/Spirit.
- `database/TOOL_DATA_MATERIALIZATION_MANIFEST.csv` — exact generated paths, row counts and sizes.
- `AUTO_FEATURE_READINESS.md` — feature solved/proof/design status.
- `research/AUTO_RUNTIME_PROOF_QUEUE.md` — remaining live/server proofs only.
- `analysis/35_RUNTIME_SNAPSHOT_CONTRACT.md` — per-PID immutable read snapshot model.
- `database/AUTO_TOOL_API_CATALOG.md` — state/query APIs.
- `database/AUTO_TOOL_ACTION_CATALOG.md` — exact mutable semantic actions/payloads/proofs.
- `analysis/34_AUTO_STATE_ACTION_PROOF_MATRIX.md` — `state -> guard -> action -> proof -> rescan` contract.
- `analysis/37_INPUT_SYNC_STATIC_EVIDENCE.md` — InputSync/TryClickUI/drag-state anchors.

## Primary feature routes

| Tool task | Start here | Static lookup when needed |
|---|---|---|
| Tool architecture / multi-client / arbitration | `contexts/BUILD_TOOL_CORE.md` | `database/TOOL_DATA_INDEX.md` only for feature-specific static IDs |
| Runtime scanner / nearby entities / bag / target | `contexts/BUILD_RUNTIME_SCANNER.md` | matching domain index only |
| MainThread action bridge | `contexts/BUILD_MAINTHREAD_BRIDGE.md` | none normally |
| Hidden click / InputSync | `analysis/37_INPUT_SYNC_STATIC_EVIDENCE.md` | `database/PC_INPUT_KEY_BINDINGS.csv` only when input mapping matters |
| Auto Train | `contexts/BUILD_AUTO_TRAIN.md` | `static/monsters/`, `static/skills/`, item/loot indexes |
| Auto Buff / Nga My | `contexts/BUILD_AUTO_BUFF.md` | `static/skills/`, `static/magic/`, `NGAMY_SUPPORT_SKILLS.md` |
| Auto Sell | `contexts/BUILD_AUTO_SELL.md` | `static/items/`, `static/equips/`, NPC/vendor data |
| NPC Trị liệu | `contexts/BUILD_AUTO_HEAL.md` | NPC lookup + current GameDialog runtime state |
| Revive / Đầu thai | `contexts/BUILD_AUTO_REVIVE.md` | no large static DB required |
| Party / follow | `contexts/BUILD_PARTY.md` | only faction/name interpretation if needed |
| Cross-feature orchestrator | `contexts/BUILD_ORCHESTRATOR.md` | feature-specific indexes only |
| Auto FuBen / dungeon / Boss | `features/AUTO_FUBEN.md`, `analysis/38_FUBEN_BOSS_TASK_TOOL_STACK.md` | `database/fuben/` + `static/monsters/` |
| Auto PK / retaliation | `features/AUTO_PK.md`, `analysis/39_PK_AUTOPK_RUNTIME_STACK.md` | `static/skills/`, faction data |
| Dồn đồ / Trade | `features/TRADE_CONSOLIDATION.md`, `analysis/40_TRADE_CONSOLIDATION_RUNTIME_STACK.md` | `static/items/`, `static/equips/` for policy only |
| Use / vứt / hủy / chuyển item | `features/BAG_ITEM_POLICY.md`, `analysis/41_BAG_ITEM_USE_DROP_POLICY_STACK.md` | `static/items/`, `static/equips/`, `MEDICINES.csv` |
| Auto Quest / tasks | `analysis/23_TASK_QUEST_AUTOMATION.md` | `static/tasks/` + NPC/Monster/Map indexes |
| Pet / Spirit auto | `analysis/24_PET_SPIRIT_AUTO_RUNTIME.md` | `static/pets/` + skill data |
| Storage / bank | `analysis/26_STORAGE_BANK_ITEM_MOVE.md` | item/equip policy indexes |

## Static database lookup rules

### NPC / Map / route

Use:

- `database/MAPS.csv`
- `database/npcs/`
- `database/autopath_npc/`
- `database/AUTOPATH_PORTAL_EDGES.csv`
- `database/NPC_SERVICE_CANDIDATES.md`.

Do not invent live NPC coordinates when `Game.GetNPCPosition(npcID)` exists.

### FuBen / Boss

Use:

```text
database/fuben/FUBEN_SCENARIOS.csv
 -> FUBEN_ENTRY_NPCS.csv
 -> FUBEN_ACTIONS_COMPACT.csv
 -> FUBEN_KILL_TARGETS.csv
 -> FUBEN_BOSS_LEVEL_BANDS.csv
 -> static/monsters/BOSS_INDEX_* when exact template detail is needed
```

Do not conflate entry NPC with combat Boss.

### Monster / Train target

Use `database/static/monsters/`:

- `MONSTER_INDEX_*` — all 17,121 templates.
- `BOSS_INDEX_*` — 3,579 exact Boss templates.
- `BOSS_NAME_INDEX.csv` — 578 grouped Boss names.

Current spawn/death/RoleID/Position remains runtime-authoritative.

### Skill / Buff / PK lookup

Normal route:

```text
static/skills/index/SKILL_TOOL_INDEX_*.csv
 -> full SKILL row only if needed
 -> SKILL_PROPERTIES_* / AUTO_SKILLS / MAGIC_ATTRIBUTES only if the decision needs them
 -> current ownership/cooldown/target/range at runtime
```

Known Nga My support identities remain in `database/NGAMY_SUPPORT_SKILLS.md`.

### Item / Equip / Sell / Loot / Use / Drop

Use:

```text
static/items/ITEM_TOOL_INDEX.csv
static/items/ITEM_POLICY_EXCEPTIONS.csv
static/items/MEDICINES.csv
static/equips/EQUIP_INDEX_*.csv
static/equips/WEAPON_INDEX.csv
```

Open full `ITEMS_*` / `EQUIPS_*` chunks only for deeper attributes.

Hard rules:

```text
live dbItemData.ID != template ItemID != Position != Site
static Weapon position = EquipPoint == 0
```

### Task / Quest

Use:

```text
static/tasks/TASK_INDEX.csv
 -> TASK_OBJECTIVES.csv
 -> matching TASKS_* full chunk only if needed
 -> current dbTaskData.Parameters at runtime
```

Grow/Activity lookup is already under the same directory.

### Pet / Spirit

Use compact `PET_INDEX_*` / `SPIRIT_INDEX_*` first. Open full chunks only if template details are needed.

## Exact action / packet questions

Start with `database/AUTO_TOOL_ACTION_CATALOG.md`.

Already solved action families include:

- Train start/stop;
- movement / target / chase;
- skill use;
- NPC interaction / dynamic GameDialog;
- Sell;
- item Use/Abandon/Move/Split/Destroy;
- loot pickup;
- Revive;
- Team join/leave/invite/follow;
- Trade/dồn đồ session actions.

Use `PACKET_IDS.csv` only after the action catalog. Packet name/ID alone is not payload proof.

## Party exact routes already solved

Do not retrace:

```text
leave team -> CMD_TEAM_ACTION 200057 -> 4:selfRoleID
join target team -> CMD_OTHER_ROLE_COMMAND 200051 -> 9:targetRoleID
invite target -> CMD_OTHER_ROLE_COMMAND 200051 -> 5:targetRoleID
```

Request sent is not success; wait fresh TeamID/C_TeamData proof.

## Trade / dồn đồ exact route already solved

Do not rebuild the trade protocol from UI coordinates.

Start trade:

```text
CMD_OTHER_ROLE_COMMAND 200051
7:1:targetRoleID
```

Active session uses current `ExchangeID` and live item instance IDs. Nine item slots are a session capacity, not proof that a batch completed. See `analysis/40_TRADE_CONSOLIDATION_RUNTIME_STACK.md`.

## Hidden click / InputSync

Start with:

- `analysis/37_INPUT_SYNC_STATIC_EVIDENCE.md`
- `analysis/07_SUPPORT_MODULES_LAUNCHER.md` only when launcher/session control is actually involved.

Static anchors include `SyncBootstrap.AutoInit`, `InputSyncManager`, `TryClickUI`, `FramePressState`, UI drag helpers and `UIButton.HandleClickEvent`.

Do not invent signatures from string names. For machine-specific failures, verify snapshot hash, resolver/init timing, PID/window/Screen and drag-state before blaming CPU/client build.

## Remaining live-proof route

If static semantics are solved but one behavior is still unknown:

1. `AUTO_FEATURE_READINESS.md`
2. `research/AUTO_RUNTIME_PROOF_QUEUE.md`
3. exactly one matching feature document.

Current important live proofs include:

```text
external managed Action -> MainThread callback from production tool
relationship-specific Nga My beneficial-skill server acceptance
current healer GameDialog selection/confirmation/result
current chosen vendor dialog -> NpcShopID/ShopID promotion
```

These are runtime/server proofs, **not missing static Config data**.

## Data regeneration

Do not manually re-decrypt Config for a normal lookup.

The repository now contains a tested reproducible pipeline:

- `tools/materialize_tool_data.py`
- `.github/workflows/materialize-tool-data.yml`
- `database/TOOL_DATA_MATERIALIZATION_MANIFEST.csv`.

When a future frozen Config snapshot changes, run/regenerate through that pipeline and compare generated data instead of starting reverse research from zero.

## Normally out of route

Unless a concrete tool feature depends on them, avoid spending context on cosmetics/FX, voice/LiveKit, renderer/D3D/baselib, crash-handler internals, decorative UI, or unrelated title/reputation systems.

## Hard rule

**Lookup -> semantic/runtime contract -> one action -> proof. Reverse native/client code only when the required contract genuinely does not exist in the KB.**
