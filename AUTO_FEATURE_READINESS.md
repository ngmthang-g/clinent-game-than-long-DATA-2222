# Auto Feature Readiness — solved vs runtime proof

Purpose: stop future AI from wasting time re-reversing automation features and static data that are already understood/materialized.

Labels:

- **SOLVED CLIENT KNOWLEDGE** — enough client/runtime/static knowledge exists to implement from the KB.
- **PARTIAL / TARGETED PROOF** — architecture is solved; one narrow live/server behavior remains.
- **IMPLEMENTATION BRIDGE** — client internals are solved but external-tool integration needs one live proof.
- **DESIGN ONLY** — remaining work is tool policy/orchestration, not client research.

Canonical static-data router: `database/TOOL_DATA_INDEX.md`.

Canonical generated-data audit: `database/TOOL_DATA_MATERIALIZATION_MANIFEST.csv`.

Canonical runtime snapshot: `analysis/35_RUNTIME_SNAPSHOT_CONTRACT.md`.

---

| Auto feature | Readiness | Already solved/materialized | Remaining narrow gap |
|---|---|---|---|
| Frozen static Config database | **SOLVED / MATERIALIZED** | 75 Config XML tables extracted; tool-relevant domains written to ~102 generated CSV/index/chunk files; reproducible generator/workflow in repo | regenerate/compare only when source snapshot changes |
| Runtime local/map/bag/buff/cooldown scanner | **SOLVED CLIENT KNOWLEDGE** | semantic Game/RoleData queries + exact per-PID snapshot contract | external bridge must copy live values safely per PID |
| Nearby PeacePlayer scanner | **SOLVED CLIENT KNOWLEDGE** | RoleID/Name/Level/FactionID/HP/MaxHP/GuildName/AvartaID/TeamRank | Position/death only if a concrete feature truly needs them |
| Nearby monster/Train target discovery | **SOLVED CLIENT KNOWLEDGE** | target discovery Type/IsDeath/RoleID/ResID/Position + all 17,121 Monster templates materialized | absolute HP/MaxHP for every unselected monster only if future telemetry needs it |
| Boss identity/filter | **SOLVED / MATERIALIZED** | 3,579 exact `Type=Boss` templates + 578 Boss-name groups | current spawn/RoleID/death/Position remains runtime state |
| Train start/stop | **SOLVED CLIENT KNOWLEDGE** | `C_AutoModel.Train=1`; semantic `StartAutoFight(Train/None)` | none |
| Target/chase/combat skill path | **SOLVED CLIENT KNOWLEDGE** | SelectTarget/ChaseTarget/HasPath/RequestUsingSkill* / cooldown/progress guards | runtime integration only |
| Skills static lookup | **SOLVED / MATERIALIZED** | 2,091 Skills + 2,044 SkillProperties + 300 AutoSkills + 509 MagicAttributes | current ownership/cooldown/condition/server acceptance remains runtime |
| Nga My skill identity | **SOLVED CLIENT KNOWLEDGE** | 406/407/408/423/424 exact identities; 407 Lua naming bug documented | none |
| Auto Buff candidate selection | **SOLVED CLIENT KNOWLEDGE** | nearby PeacePlayer fields + HP/MaxHP priority/filter model | none for read-only policy |
| Auto Buff cast on non-team PeacePlayer | **PARTIAL / TARGETED PROOF** | target/cast/range/cooldown donor path + static skill database known | prove server acceptance per intended skill/relationship |
| Bag full detection | **SOLVED CLIENT KNOWLEDGE** | `GetFreeBagSpace`, Bag site 10 | none |
| Item identity/classification | **SOLVED / MATERIALIZED** | instance vs template vs slot/site semantics; 5,238 Items + 22,763 Equips + policy indexes/chunks | mutable action still requires fresh live item instance |
| Medicine/gem lookup | **SOLVED / MATERIALIZED** | 692 Medicines + 1,154 Gems | production auto-use policy is tool design/runtime guard work |
| Use / Abandon / Destroy / Move item | **SOLVED CLIENT KNOWLEDGE** | exact item-action family and destructive-action guard semantics documented | production policy/confirmation only |
| Auto Sell request | **SOLVED CLIENT KNOWLEDGE** | packet 200036 + exact `instanceID:NpcShopID:ShopID` | none; do not trace again |
| Auto Sell transaction loop | **SOLVED CLIENT KNOWLEDGE** | one live instance -> sell -> wait server update -> rescan | runtime integration only |
| Vendor routing | **SOLVED MECHANISM / PARTIAL SERVICE MAP** | NPC DB + navigation + shop-state proof + candidate maps | promote exact production vendor dialogs/shop IDs as needed |
| NPC treatment navigation | **SOLVED MECHANISM** | NPC DB + GetNPCPosition/GoToNPC/GameDialog architecture | exact current healer service selection/confirmation/result |
| Revive / Đầu thai | **SOLVED CLIENT KNOWLEDGE** | packet 200063; types 1/2/3; lifecycle proof rules | runtime integration only |
| Loot/item-pack pickup | **SOLVED CLIENT KNOWLEDGE** | nearby ItemPack + path/move/click/pickup flow + item static DB | richer user loot policy only |
| Team state / HP / position | **SOLVED CLIENT KNOWLEDGE** | C_TeamData/member fields/nearby positions | none for scanner/follow basics |
| Leave/join/invite team | **SOLVED CLIENT KNOWLEDGE** | `4:selfRoleID`, `9:targetRoleID`, `5:targetRoleID` exact request routes | normal server membership proof after request |
| Follow teammate | **SOLVED CLIENT KNOWLEDGE** | semantic follow + nearby MoveTo + cross-map GoTo | none |
| Trade / dồn đồ protocol | **SOLVED CLIENT KNOWLEDGE** | RoleID invitation, ExchangeID session, AddItem/Lock/Done/Cancel, 9 slots, live instance rule | production session state proof/fresh bag loop only |
| FuBen scenario/route/action data | **SOLVED / MATERIALIZED** | 19 scenarios, 268 actions, 72 Kill actions, 1,381 level-band mappings, entry NPCs, Boss joins | only current server acceptance/dynamic dialog differences if a scenario fails live |
| Auto FuBen combat/control | **SOLVED CLIENT KNOWLEDGE** | shipped AutoFight_FuBen flow, query/sync/matchmaking packet semantics, Train-like combat donor | runtime integration and scenario-specific live proof as needed |
| PK modes / direct PK actions | **SOLVED CLIENT KNOWLEDGE** | exact PK modes, mode change, Proclaim/Challenge routes | server/legal-state result proof during implementation |
| AutoPK | **SOLVED CLIENT KNOWLEDGE** | C_AutoModel.PK, nearby-enemy target flow, retaliation trigger, skill/chase flow; unused UI filters documented | production targeting policy if user wants behavior beyond shipped selector |
| Task static database | **SOLVED / MATERIALIZED** | 516 Tasks + 591 objective rows + GrowPoints/Activities/GuildTasks | live task Parameters/server progression only |
| Auto Quest donor | **SOLVED CLIENT KNOWLEDGE** | built-in objective selection/navigation/monster/dialog composition documented | unsupported objective automation is feature implementation, not broad reverse |
| Pet / Spirit static database | **SOLVED / MATERIALIZED** | 8,349 Pets + 1,889 Spirits + feature/equip support tables | current companion runtime state/action proof only |
| Pet / Spirit auto donor | **SOLVED CLIENT KNOWLEDGE** | shipped runtime/action semantics documented | production policy/integration only |
| PC input binding table | **SOLVED / MATERIALIZED** | 22 shipped PC key mappings | semantic actions remain preferred |
| InputSync / hidden UI click static anchors | **SOLVED CLIENT KNOWLEDGE** | SyncBootstrap/InputSyncManager/TryClickUI/drag-state/UIButton anchors | exact resolver/signature work only if current implementation still cannot bind reliably |
| MainThread internal dispatcher | **SOLVED CLIENT KNOWLEDGE** | Execute -> ConcurrentQueue -> Update -> Action.Invoke | none about dispatcher internals |
| External managed Action -> MainThread | **IMPLEMENTATION BRIDGE** | Action ABI/producer donors/IL2CPP requirements documented | one harmless live construction/rooting/callback proof |
| Captcha handling | **SOLVED SAFETY CONTRACT** | explicit Captcha state + manual submit path | tool must pause; no auto-solve/bypass |
| Adaptive spot switching | **DESIGN ONLY, INPUTS SOLVED** | deaths/loot/bag/map/train/monster data available | tool scoring/tuning only |
| Multi-client orchestration | **DESIGN ONLY, CLIENT INPUTS SOLVED** | per-PID snapshot/action ownership + InputSync evidence | implementation/isolation testing |

---

## Static lookup is no longer a research gap

Future AI must not say that Items/Equips/Monsters/Skills/Tasks/Pets/Spirits are “only schemas” or “not present on GitHub”.

They are materialized under:

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

Use `database/TOOL_DATA_INDEX.md` to choose the smallest index/chunk.

## Do not re-reverse these solved facts

Do not spend research time rediscovering:

- Train=1 / semantic StartAutoFight;
- nearby PeacePlayer HP/MaxHP identity fields;
- exact Sell packet/payload;
- item instance ID vs ItemID/Position/Site;
- Use/Abandon/Move/Split/Destroy action family already documented;
- Weapon = `EquipPoint==0`;
- exact Revive types;
- dynamic GameDialog architecture;
- `Game.GetNPCPosition` route principle;
- Nga My 407/423 corrected identities;
- Team leave/join/invite exact request routes;
- Trade invitation/session/action values and 9-slot capacity;
- FuBen scenario/action/Boss database and shipped AutoFuBen flow;
- PK mode/AutoPK/retaliation donor;
- MainThread queue/Update/Invoke internals;
- InputSync/TryClickUI static anchors;
- full static Config normalization already generated on `main`.

If implementation fails, debug fresh runtime state, resolver, action bridge, server rejection or result proof before reopening broad reverse work.

## Highest-value remaining proofs

The research queue is now intentionally narrow:

1. external valid managed `System.Action` -> `MainThread.Execute` live callback;
2. non-team relationship acceptance for exact Nga My support skills;
3. exact current `Trị liệu` GameDialog sequence/outcome at chosen healer;
4. exact current vendor service -> `NpcShopID/ShopID` promotion for production maps;
5. optional actor fields only when a concrete implementation cannot proceed without them.

Everything else should first move into tool implementation rather than more broad client research.
