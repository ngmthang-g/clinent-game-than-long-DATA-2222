# AI Knowledge Index — Thần Long frozen client snapshot

Repository: `ngmthang-g/clinent-game-than-long-DATA-2222`

This repository is primarily a **knowledge base for building the Thần Long automation tool**. It is not an encyclopedia of every game/client subsystem.

---

# 1. Start here — do not read the whole repo

Normal task flow:

```text
AI_BOOTSTRAP.md
 -> mandatory project-control rule files named there
 -> AUTO_TOOL_SCOPE.md
 -> AI_ROUTER.md
 -> exactly one matching contexts/BUILD_*.md
 -> compact auto catalog / exact database lookup
 -> deep analysis only when required
```

For normal work target **5–10 relevant documents**, not the entire repository.

Mandatory persistent rules:

- `AI_PROJECT_KNOWLEDGE_PROTOCOL_V2_OPTIMIZED.md`
- `AI_CLIENT_ANALYSIS_RULES.txt`

Core research rule: **do not broad reverse the frozen client again when the exact fact already exists in VERIFIED/database knowledge**.

---

# 2. Best compact automation references

Use these before opening long reverse-engineering documents:

- `AUTO_TOOL_SCOPE.md` — what research is worth doing for the auto tool.
- `AUTO_FEATURE_READINESS.md` — what is solved vs what still needs narrow proof.
- `analysis/35_RUNTIME_SNAPSHOT_CONTRACT.md` — canonical per-PID immutable external read-only state model.
- `database/AUTO_TOOL_API_CATALOG.md` — compact automation state/query API catalog.
- `database/AUTO_TOOL_ACTION_CATALOG.md` — compact exact mutable-action catalog, including packet IDs/payloads.
- `analysis/34_AUTO_STATE_ACTION_PROOF_MATRIX.md` — feature-by-feature `state -> guard -> one action -> proof -> rescan` contract.
- `database/AUTO_SELL_CLASSIFICATION.md` — compact safe keep/sell classification contract.
- `database/FACTS.jsonl` — atomic exact facts for lookup.
- `database/FINDING_TO_DOC_MAP.md` — known finding -> canonical detailed document.

---

# 3. Canonical auto architecture

```text
Resolver
 -> read-only Scanners / Observers
 -> immutable per-PID Snapshot Store
 -> State Machine / Orchestrator
 -> Safety Guard
 -> Action Gate (max 1 mutable action)
 -> valid System.Action
 -> FGStudio.Engine.Utilities.MainThread.Execute
 -> semantic Game/Lua/UI action
 -> concrete runtime/server state proof
 -> fresh snapshot
```

Read-only observers may run concurrently.

Mutable actions may not compete inside one PID.

Never share live pointers/state between PIDs.

---

# 4. Major client research already solved

## IL2CPP / Lua architecture

Client is Unity Windows x64 + IL2CPP; metadata version 39.

High-value bridge classes include:

- `LuaSystemManager`
- `LuaSystemSharedData`
- `LuaSystemAPI_Game`
- `LuaSystemAPI_GUI`
- `LuaSystemAPI_Network`
- `UIButton`.

## Asset semantic extraction

Important bundles were decoded/extracted.

Verified recovered semantic data:

- 75 Config XML tables
- 338 UI layout XML TextAssets
- 1,469 UI handler bindings
- 339 Lua script classes + global infrastructure
- 169 exact `TCPPacketDefine` constants.

For future gameplay action questions prefer:

```text
Lua/UI source
 -> Config semantic data
 -> current runtime state
 -> exact action/payload
 -> native reverse only for a real remaining gap
```

## MainThread dispatcher

Statically solved:

```text
MainThread.Execute(Action)
 -> ConcurrentQueue<Action>
 -> Unity Update
 -> DoExecuteWorks
 -> dequeue
 -> Action.Invoke
```

Game-owned TCP producers construct valid managed `System.Action` delegates and call this dispatcher.

Remaining external Action construction/rooting proof is implementation work, not uncertainty about dispatcher internals.

Canonical docs:

- `analysis/21_MAIN_THREAD_DISPATCHER.md`
- `analysis/29_MAINTHREAD_NETWORK_PRODUCER_DONORS.md`
- `analysis/30_EXTERNAL_ACTION_BRIDGE_BLUEPRINT.md`.

---

# 5. Runtime scanner knowledge

Canonical external schema:

`analysis/35_RUNTIME_SNAPSHOT_CONTRACT.md`.

## Nearby peaceful players

`Game.GetNearByPeacePlayers(limit)` exposes:

```text
RoleID
Name
Level
FactionID
HP
MaxHP
GuildName
AvartaID
TeamRank
```

Do not rediscover these via CE/OCR.

Important boundary: generic Position/death for arbitrary non-team PeacePlayers is not automatically claimed by this exact API. Resolve only if a concrete Buff implementation needs it.

## Train targets

Built-in Train search uses `Game.GetNearbySpritesWithPredicate(...)` with:

```text
Type
IsDeath
RoleID
ResID
Position
```

Exact live HP/MaxHP for every unselected monster is not required for basic Train and should not trigger broad reverse unless a concrete policy needs it.

## Selected target

`Game.SelectedTarget` supplies identity/type/percentage-vital state including `RoleID, Type, Name, HPPercent, Level, FactionID` and other type-dependent fields.

## Map

Use:

```text
Game.RoleData.MapID
Game.RoleData.Position
Game.IsMapReady()
Game.GetCurrentMoveDestination()
Game.GetLocalMapObjects()
Game.GetNearbyObjects()
```

Travel proof:

```text
expected MapID + map ready + valid fresh position + within tolerance
```

---

# 6. Auto Train — solved client knowledge

Exact mode:

```text
C_AutoModel.Train = 1
```

Start:

```text
GUI.FindUI("AutoFight_Main"):StartAutoFight(C_AutoModel.Train)
```

Stop/yield:

```text
StartAutoFight(C_AutoModel.None)
```

The visible `Đánh quái` tab is configuration, not the semantic start action.

Built-in Train already demonstrates:

- target scan/filter;
- reachability/path guard;
- select/chase;
- target death/reload handling;
- skill use by SkillID;
- radius/whitelist/lure behavior;
- loot integration;
- death/comeback donor logic.

Key settings include:

```text
IsTrainInRanger
RangerScan default 500
GiveUpMonsterOutRanger
AttackMonsterList
AutoTrainSkillList
UsingCombo
UsingF1Key
```

Canonical:

- `features/AUTO_TRAIN.md`
- `analysis/10_BUILTIN_AUTO_FIGHT_ENGINE.md`
- `contexts/BUILD_AUTO_TRAIN.md`.

---

# 7. Auto Buff / Nga My — solved except one runtime boundary

Correct frozen Config identities:

```text
406 = Phật Quang Phổ Chiếu
407 = Xung Hư Dưỡng Khí
408 = Khởi Tử Hồi Sinh
423 = Kim Châm Độ Kiếp
424 = Thanh Tâm Phổ Thiện Chú
```

Legacy Lua variable naming around 407 is misleading; never label 407 as actual Kim Châm.

Built-in support donor:

```text
GetSkillLuaData
 -> calculate distance / CastRange
 -> ChaseTarget if required
 -> RequestUsingSkillWithTarget(skillID,RoleID)
```

Cooldown source:

```text
Game.GetSkillCooldown(skillID)
```

Current remaining runtime proof:

- server acceptance of the exact beneficial skill(s) used by the external tool on non-team PeacePlayers.

Canonical:

- `analysis/15_AUTO_RECOVERY_NGAMY_ENGINE.md`
- `database/NGAMY_SUPPORT_SKILLS.md`
- `features/AUTO_BUFF.md`
- `contexts/BUILD_AUTO_BUFF.md`.

---

# 8. Inventory / Auto Sell — core mechanism solved

Runtime truth:

```text
Game.GetFreeBagSpace()
Game.GetItemsAtSite(Bag)
Bag site = 10
```

Identity rule:

```text
ID       = live instance ID
ItemID   = template ID
Position = current slot
Site     = current container
```

Exact sell request:

```text
CMD_NPC_SHOP_SELL_REQUEST = 200036
payload = itemInstanceID:NpcShopID:ShopID
```

Stock guards include:

```text
40000000 <= ItemID < 50000000 -> do not sell
Game.IsItemSellable(ItemID) must be true
```

Mutation rule:

```text
fresh bag
 -> choose ONE current instance
 -> sell
 -> wait RemoveItem / UpdateItemsList / consistent shop-money proof
 -> fresh bag
```

Static Weapon rule:

```text
Equips.EquipPoint == 0
```

Do not use `Type<10` as universal Weapon classification.

Compact policy:

`database/AUTO_SELL_CLASSIFICATION.md`.

Canonical:

- `features/AUTO_SELL.md`
- `analysis/20_BAG_GRID_SHOP_UI_RUNTIME.md`
- `contexts/BUILD_AUTO_SELL.md`.

Large Items/Equips row chunks are **not currently all committed** under `database/static/...`; do not invent missing rows/files.

---

# 9. NPC / treatment / service interaction

Built-in route pattern:

```text
GoToNPC(mapID,npcID)
 -> Game.GetNPCPosition(npcID)
 -> Game.GoTo(...)
 -> Game.ClickNPC(npcID)
```

Do not hardcode NPC X/Y when runtime position exists.

Dynamic dialog:

```text
Selections[selectionID] = visibleText
CMD_SHOW_GAMEDIALOG = 100007
payload = selectionID:SelectedItemID
```

Usually no-item action uses `actualSelectionID:-1`.

Known Lâu Lan identity:

```text
Map 5 = Lâu Lan
NPC 339 = Đỗ Thanh Đằng
ResName = LangZhong1
```

NPC 339 is a strong static healer candidate.

Remaining runtime proof:

- exact current `Trị liệu` visible text/selectionID;
- any confirmation step;
- HP/money/dialog completion proof.

Canonical:

- `features/AUTO_HEAL_NPC.md`
- `analysis/11_EXACT_INTERNAL_ACTION_FLOWS.md`
- `analysis/12_GLOBAL_LUA_HELPERS.md`.

---

# 10. Revive / Đầu thai — solved client knowledge

Exact packet:

```text
CMD_REVIVE_DATA = 200063
```

Types:

```text
1 = normal / Đầu thai
2 = newbie revive
3 = skill revive
```

Server Revival data exposes:

```text
TimeLeft
IsEnableReviveNewbie
IsEnableBySkill
open/update/close lifecycle
```

Completion proof:

```text
local alive + Revival cleared + map ready + valid position
```

Canonical:

`features/AUTO_REVIVE.md`.

---

# 11. Party / Follow — request construction solved

Team state:

```text
Game.RoleData.TeamID
C_TeamData.LeaderID
C_TeamData.TeamMember[]
```

Team members expose:

```text
RoleID, RoleName, Level, FactionID,
MapID, Hp, MaxHp, AvartaID, PosX, PosY
```

Exact leave:

```text
CMD_TEAM_ACTION = 200057
payload = 4:selfRoleID
```

Exact request to join selected target's team:

```text
CMD_OTHER_ROLE_COMMAND = 200051
C_OtherRoleCommand.TeamRequestJoin = 9
payload = 9:targetRoleID
```

Exact invite selected target:

```text
CMD_OTHER_ROLE_COMMAND = 200051
C_OtherRoleCommand.TeamInviter = 5
payload = 5:targetRoleID
```

Do not confuse `C_TeamAction.RequestJoin=7` with the separate selected-player command `TeamRequestJoin=9`.

Server acceptance proof remains:

```text
Game.RoleData.TeamID / C_TeamData update
```

Built-in Follow:

```text
AutoFight_Main:TurnOnFollowTarget(RoleID)
```

Nearby -> `Game.MoveTo(Position)`; out of AOI/cross-map -> team MapID/PosX/PosY + `Game.GoTo`.

**Join-party request construction is no longer a research gap.**

Canonical:

- `analysis/25_TEAM_RUNTIME_FOLLOW.md`
- `analysis/16_PLAYER_INTERACTION_UI_API.md`
- `contexts/BUILD_PARTY.md`.

---

# 12. Exact automation action lookup

Before searching packets or UI handlers, read:

`database/AUTO_TOOL_ACTION_CATALOG.md`.

It consolidates exact/semantic actions for:

- Train start/stop;
- target/movement;
- skills;
- NPC interaction;
- GameDialog;
- Sell;
- bag/item/storage actions;
- loot;
- Revive;
- Party join/leave/invite;
- Follow;
- MainThread boundary.

Relevant packet IDs include:

```text
100005 CMD_ITEM_ACTION
100006 CMD_BAG_SORT
100007 CMD_SHOW_GAMEDIALOG
200034 CMD_NPC_SHOP_DATA
200036 CMD_NPC_SHOP_SELL_REQUEST
200051 CMD_OTHER_ROLE_COMMAND
200057 CMD_TEAM_ACTION
200063 CMD_REVIVE_DATA
```

---

# 13. Orchestration / multi-client

Canonical design:

- `features/AUTO_ORCHESTRATOR.md`
- `contexts/BUILD_ORCHESTRATOR.md`
- `analysis/34_AUTO_STATE_ACTION_PROOF_MATRIX.md`
- `analysis/35_RUNTIME_SNAPSHOT_CONTRACT.md`.

Per PID keep independent:

```text
Resolver
SnapshotVersion / WorldGeneration
Snapshots
Feature state
Action gate
Dispatcher state
Profile/settings
Spot metrics
Last action/proof
```

Suggested action priority:

```text
Captcha/manual pause
 > fatal recovery
 > Revive
 > map-transition completion
 > critical survival/buff
 > current Sell/NPC transaction
 > current Party transaction
 > normal Buff
 > Train
 > Loot
 > background spot optimization
```

---

# 14. Database navigation

High-value auto databases:

- `database/MAPS.csv`
- `database/npcs/NPCS_*.csv`
- `database/NPC_SERVICE_CANDIDATES.md`
- `database/AUTOPATH_PORTAL_EDGES.csv`
- `database/autopath_npc/AUTOPATH_NPC_EDGES_*.csv`
- `database/PACKET_IDS.csv`
- `database/AUTO_SETTINGS_SCHEMA.md`
- `database/NGAMY_SUPPORT_SKILLS.md`
- `database/AUTO_TOOL_API_CATALOG.md`
- `database/AUTO_TOOL_ACTION_CATALOG.md`
- `database/AUTO_SELL_CLASSIFICATION.md`
- `database/FACTS.jsonl`.

Large static data is lookup-only. Never preload 22,763 Equips or 17,121 Monsters because the dataset exists.

---

# 15. Deep analysis map — open only for exact evidence

Auto-relevant deep docs:

```text
analysis/02  Lua/Game/GUI/Network bridge
analysis/03  World/entity/map/path
analysis/04  Inventory/item/shop
analysis/05  Combat/skills/buffs
analysis/10  Built-in Auto Fight
analysis/11  Exact internal action payloads
analysis/12  GoToNPC/GoToMonster helpers
analysis/14  Nearby player/target schema
analysis/15  Nga My recovery donor
analysis/16  Player/social actions
analysis/17  Buff runtime schema
analysis/18  Skill cooldown/QuickSkills
analysis/19  Progress/Captcha safety
analysis/20  Bag/NPCShop runtime
analysis/21  MainThread dispatcher
analysis/22  Map/minimap runtime
analysis/25  Team/follow/join/leave
analysis/27  Loot engine
analysis/28  Static Items/Skills/Monsters/Equips schema
analysis/29  MainThread producer donors
analysis/30  External Action bridge blueprint
analysis/34  Auto state/action/proof matrix
analysis/35  Runtime snapshot contract
```

Quest/Pet/Storage docs are conditional: read them only when the actual auto feature is requested.

---

# 16. Current real gaps

Broad client reverse is no longer useful. The important remaining gaps are narrow:

1. external managed `System.Action -> MainThread.Execute` live callback proof;
2. non-team PeacePlayer server acceptance for the exact beneficial Nga My skill(s) the tool uses;
3. exact runtime Trị liệu dialog sequence/outcome for the chosen healer;
4. promote vendor service only for actual configured Auto Sell maps/NPCs where runtime shop service is not yet proven;
5. arbitrary non-team PeacePlayer Position/death only if the chosen Buff implementation needs it;
6. richer arbitrary-target BuffID/duration only if current HP/cooldown/icon proof is insufficient;
7. exact unselected monster HP/MaxHP only if a concrete Train policy needs absolute values.

**Not current gaps:** Train start, Sell packet, Revive packet, item identity, MainThread internals, party leave, party join request construction, party invite construction.

---

# 17. Hard rules

Do not:

- broad reverse the client because a task feels difficult;
- use OCR/CE for semantic data already exposed;
- use screen coordinates when a semantic action exists;
- cache stale UI/client pointers;
- use fixed sleeps as success proof;
- call response handlers as request actions;
- confuse live item `ID` with template `ItemID`;
- invent NPC coordinates;
- invent Trị liệu selection IDs;
- spam team/social requests;
- automatically solve/bypass Captcha;
- let multiple feature loops mutate one PID concurrently.

When implementation fails against an already-VERIFIED contract, debug **runtime integration/state freshness/MainThread/action proof first**, not the whole client again.