# Auto Feature Readiness — solved vs runtime proof

Purpose: stop future AI from re-reversing client knowledge/static data that is already solved.

Labels:

- **SOLVED CLIENT KNOWLEDGE** — enough client/runtime/static knowledge exists to implement from the KB.
- **SOLVED / MATERIALIZED** — queryable static data exists on `main`.
- **PARTIAL / TARGETED PROOF** — architecture is solved; one narrow live/server behavior remains.
- **IMPLEMENTATION BRIDGE** — client internals are solved but external-tool integration needs one live proof.
- **DESIGN ONLY** — remaining work is tool policy/orchestration, not client research.

Canonical routes:

- static: `database/TOOL_DATA_INDEX.md`
- specialized manifest: `database/TOOL_DATA_MATERIALIZATION_MANIFEST.csv`
- all Config: `database/config_full/CONFIG_FULL_CATALOG.csv`
- runtime snapshot: `analysis/35_RUNTIME_SNAPSHOT_CONTRACT.md`.

---

| Auto feature | Readiness | Already solved/materialized | Remaining narrow gap |
|---|---|---|---|
| Frozen Config foundation | **SOLVED / MATERIALIZED** | exactly 75 Config XML tables; specialized tool-first databases plus `database/config_full/<Table>/ROWS_*.csv` fallback for every table; reproducible generators/workflow | regenerate/compare only when source snapshot changes |
| Runtime local/map/bag/buff/cooldown scanner | **SOLVED CLIENT KNOWLEDGE** | semantic Game/RoleData queries + exact per-PID snapshot contract | external bridge must copy live values safely per PID |
| Nearby PeacePlayer scanner | **SOLVED CLIENT KNOWLEDGE** | RoleID/Name/Level/FactionID/HP/MaxHP/GuildName/AvartaID/TeamRank | Position/death only if a concrete feature needs them |
| Nearby monster/Train target discovery | **SOLVED CLIENT KNOWLEDGE** | Type/IsDeath/RoleID/ResID/Position + all 17,121 Monster templates | richer unselected-monster HP only for optional telemetry |
| Boss identity/filter | **SOLVED / MATERIALIZED** | 3,579 exact Boss templates + 578 Boss-name groups | current spawn/RoleID/death/Position is runtime state |
| Train start/stop | **SOLVED CLIENT KNOWLEDGE** | `C_AutoModel.Train=1`; semantic StartAutoFight | none |
| Target/chase/combat skill path | **SOLVED CLIENT KNOWLEDGE** | SelectTarget/ChaseTarget/HasPath/RequestUsingSkill* + guards | runtime integration only |
| Skills static lookup | **SOLVED / MATERIALIZED** | 2,091 Skills + 2,044 SkillProperties + 300 AutoSkills + 509 MagicAttributes | current ownership/cooldown/target legality/server acceptance remains runtime |
| Nga My skill identity | **SOLVED CLIENT KNOWLEDGE** | exact 406/407/408/423/424 identities; 407 naming bug documented | none |
| Auto Buff candidate selection | **SOLVED CLIENT KNOWLEDGE** | PeacePlayer fields + HP/MaxHP filter/priority model | none for read policy |
| Auto Buff cast outside team | **PARTIAL / TARGETED PROOF** | cast/range/cooldown donor + static skill data | server acceptance per intended relationship/skill |
| Bag full detection | **SOLVED CLIENT KNOWLEDGE** | `GetFreeBagSpace`, Bag site 10 | none |
| Item identity/classification | **SOLVED / MATERIALIZED** | live-instance/template/slot/site semantics; 5,238 Items + 22,763 Equips | fresh live instance still required for mutation |
| Medicine/gem lookup | **SOLVED / MATERIALIZED** | 692 Medicines + 1,154 Gems | auto-use policy is tool/runtime work |
| Use/Abandon/Destroy/Move item | **SOLVED CLIENT KNOWLEDGE** | exact action family and destructive guards | production policy/confirmation only |
| Auto Sell request | **SOLVED CLIENT KNOWLEDGE** | packet 200036 + exact `instanceID:NpcShopID:ShopID` | none; do not trace again |
| Auto Sell loop | **SOLVED CLIENT KNOWLEDGE** | live instance -> sell -> server update -> rescan | runtime integration only |
| Vendor routing | **SOLVED MECHANISM / PARTIAL SERVICE MAP** | NPC DB + navigation + shop-state mechanism | promote exact live vendor dialog/shop IDs as needed |
| NPC treatment | **PARTIAL / TARGETED PROOF** | navigation + dynamic GameDialog mechanism solved | exact current Trị liệu selection/confirmation/result |
| Revive / Đầu thai | **SOLVED CLIENT KNOWLEDGE** | packet/types/lifecycle semantics | runtime integration only |
| Loot pickup | **SOLVED CLIENT KNOWLEDGE** | ItemPack + path/move/click/pickup + static item DB | richer user loot policy only |
| Team state / follow | **SOLVED CLIENT KNOWLEDGE** | C_TeamData, member fields, follow/movement path | none for basic implementation |
| Leave/join/invite team | **SOLVED CLIENT KNOWLEDGE** | exact request routes | normal server membership proof after request |
| Trade / dồn đồ protocol | **SOLVED CLIENT KNOWLEDGE** | RoleID invite, ExchangeID session, AddItem/Lock/Done/Cancel, 9 slots, live instance rule | production session/fresh-bag proof only |
| FuBen static scenario/route/Boss data | **SOLVED / MATERIALIZED** | 19 scenarios, 268 actions, 72 Kill actions, 1,381 level bands, Boss joins | dynamic server conditions only if a live scenario fails |
| Auto FuBen combat/control | **SOLVED CLIENT KNOWLEDGE** | shipped flow + query/sync/matchmaking + combat donor | runtime integration/live scenario proof as needed |
| PK modes/direct actions | **SOLVED CLIENT KNOWLEDGE** | exact PK modes and request routes | legal/server result proof during implementation |
| AutoPK | **SOLVED CLIENT KNOWLEDGE** | nearby-enemy target flow, retaliation, skill/chase; unused UI filters identified | user-specific targeting policy only |
| Task database | **SOLVED / MATERIALIZED** | 516 Tasks + 591 objectives + GrowPoints/Activities/GuildTasks | live task progress/server progression only |
| Auto Quest donor | **SOLVED CLIENT KNOWLEDGE** | objective/navigation/monster/dialog composition | feature implementation only |
| Pet / Spirit database | **SOLVED / MATERIALIZED** | 8,349 Pets + 1,889 Spirits + support tables | current companion runtime state/action proof only |
| Pet / Spirit auto donor | **SOLVED CLIENT KNOWLEDGE** | shipped runtime/action semantics | production policy/integration only |
| Any low-frequency Config domain | **SOLVED / MATERIALIZED** | all 75 tables available through `database/config_full` with direct attrs + recursive child structure | runtime semantics only if a concrete feature needs them |
| PC key bindings | **SOLVED / MATERIALIZED** | 22 shipped mappings | semantic actions preferred |
| InputSync hidden-click static contract | **SOLVED CLIENT KNOWLEDGE** | exact TryClickUI/UpdateUIDrag/EndUIDrag/Cancel/Reset signatures, declaring types, tokens, selected RVAs, native ABI, ConvertPos, ParseAndInject call path, drag-field offsets/cleanup | live per-PID resolver/bootstrap/window/DPI/UI proof only |
| MainThread internal dispatcher | **SOLVED CLIENT KNOWLEDGE** | Execute -> queue -> Update -> Action.Invoke | none about dispatcher internals |
| External managed Action -> MainThread | **IMPLEMENTATION BRIDGE** | ABI/producer donors/requirements documented | one harmless live construction/rooting/callback proof |
| Captcha handling | **SOLVED SAFETY CONTRACT** | explicit Captcha/manual path | tool pauses; no auto-bypass |
| Adaptive spot switching | **DESIGN ONLY, INPUTS SOLVED** | required train/death/loot/bag/map data exists | scoring/tuning only |
| Multi-client orchestration | **DESIGN ONLY, CLIENT INPUTS SOLVED** | per-PID state/action model + exact InputSync contract | implementation/isolation testing |

---

## Static lookup is closed

Future AI must not claim that a frozen Config table needs a new decrypt/extract pass.

Use specialized domains first:

```text
database/fuben/
database/static/monsters/
database/static/items/
database/static/equips/
database/static/skills/
database/static/magic/
database/static/tasks/
database/static/pets/
```

For anything else:

```text
database/config_full/CONFIG_FULL_CATALOG.csv
 -> database/config_full/<Table>/ROWS_*.csv
```

## InputSync static reverse is also closed for this snapshot

Do not rediscover or misattribute:

- `TryClickUI(int, Vector2)` and UI drag methods on `InputSyncManager`;
- `SetSyncState/GetSyncGroupId/SetSyncGroup` on `InstanceRegistry`;
- `FramePressState` on `PointerEventData`;
- `GetLastPointerEventData` on `PointerInputModule`;
- `Joystick.InjectSyncInput` on `Joystick`;
- `ParseAndInject -> ConvertPos/InjectMousePos/TryClickUI/UpdateUIDrag/EndUIDrag`;
- `_uiDragging/_uiDragTarget/_uiDragData` cleanup lifecycle.

Canonical files:

- `analysis/43_INPUT_SYNC_EXACT_SIGNATURES_AND_UI_LIFECYCLE.md`
- `database/PC_INPUTSYNC_METHODS.csv`.

A same-hash machine failure is now a runtime binding/init/window/UI-state problem until evidence proves otherwise.

## Other solved facts not to re-reverse

Do not spend research time rediscovering Train=1, nearby PeacePlayer HP/MaxHP, exact Sell, item instance semantics, Weapon=`EquipPoint==0`, item action family, Revive, dynamic GameDialog architecture, NPC position routing, Nga My corrected identities, Team request routes, Trade session semantics, FuBen route/Boss database, PK/AutoPK donor or MainThread internal queue.

## Highest-value remaining proofs

1. external valid managed `System.Action` -> `MainThread.Execute` callback;
2. non-team relationship acceptance for production Nga My support skills;
3. exact current Trị liệu dialog/outcome;
4. exact current vendor service -> `NpcShopID/ShopID` promotion;
5. optional richer actor fields only when a concrete implementation cannot proceed.

Everything else should first move into tool implementation rather than more broad reverse engineering.
