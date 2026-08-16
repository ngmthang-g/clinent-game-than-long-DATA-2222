# Auto Tool Semantic API Catalog

Purpose: compact implementation-oriented catalog for the **Thần Long auto tool only**. Future AI should use this file to find the correct semantic state/action API before opening deeper analysis.

Status labels:

- **VERIFIED** — source/runtime/native evidence in this KB.
- **VERIFIED EXISTENCE** — API/symbol exists, but exact return schema may be only partially mapped.
- **RUNTIME PROOF NEEDED** — semantic direction is grounded, but a specific server/runtime acceptance case still requires one targeted live proof.

Do not treat this as permission to call mutable APIs from an arbitrary thread. External mutable actions still require the validated Unity/MainThread path.

---

## 1. Local role / global safety state

| Need | Preferred source | Status / use |
|---|---|---|
| Local role identity/state | `Game.RoleData` | VERIFIED source used by shipped Lua |
| Current map | `Game.RoleData.MapID` | VERIFIED |
| Current position | role X/Y / `RoleData.Position`-style state used by shipped Auto | VERIFIED semantic use; copy values, do not retain object pointer |
| Current HP | `Game.GetCurrentHP()` / RoleData HP state | VERIFIED |
| Moving | `Game.IsMoving()` | VERIFIED EXISTENCE |
| Can move | `Game.CanMove()` | VERIFIED EXISTENCE |
| Busy | `Game.IsRoleBusy()` | VERIFIED EXISTENCE |
| Current progress/channel | `Game.IsProgress()` + progress events | VERIFIED |
| Map ready | `Game.IsMapReady()` | VERIFIED |
| Captcha/manual verification | `NewCaptcha` event/UI state | VERIFIED; pause automation |

Recommended external snapshot fields:

`RoleID, Name, FactionID, MapID, X, Y, HP, MaxHP, IsDead, IsMoving, IsProgress, IsMapReady, LastSeenTick`.

---

## 2. Nearby friendly players — Auto Buff / party discovery

### Preferred source

`Game.GetNearByPeacePlayers(limit)`

Shipped UI directly consumes:

- `RoleID`
- `Name`
- `Level`
- `FactionID`
- `HP`
- `MaxHP`
- `GuildName`
- `AvartaID`
- `TeamRank`.

Status: **VERIFIED**.

Use RoleID as stable runtime identity. Do not require party membership merely to read HP/MaxHP/name/faction/guild for players in AOI.

Related:

- `Game.SelectTarget(RoleID)` — target selected record.
- `Game.GetTargetBuffIcons(RoleID)` — target buff-icon state used by shipped UI.
- `Game.GetNearTeammates(...)` — team-specific nearby records.
- `C_TeamData` — current team-level/member data.

AOI rule: only entities replicated/known by the current client are available; this is not whole-map visibility.

---

## 3. Nearby enemies / monsters — Auto Train

### Preferred sources

- `Game.GetNearbySpritesWithPredicate(predicate, centerPosition)` — built-in Train target search.
- `Game.GetNearByEnemies(...)` — enemy/player PK query.
- `Game.GetNearbySprites(includeDeath)` — generic sprite query.

Observed Train target fields:

- `Type`
- `IsDeath`
- `RoleID`
- `ResID`
- `Position`.

Status: **VERIFIED source semantics** for the built-in target loop.

Use static `Monsters` only to interpret template `ResID`; current HP/position/death/reachability must come from live state.

---

## 4. Target selection / chase / combat

| Action/query | Meaning | Status |
|---|---|---|
| `Game.SelectTarget(RoleID)` | semantic target selection | VERIFIED use in shipped UI/Auto |
| `Game.ReloadTarget()` | refresh/reload target | VERIFIED source use |
| `Game.IsSelectTargetDie()` | selected-target death check | VERIFIED source use |
| `Game.ChaseTarget(...)` | semantic range/chase helper | VERIFIED source use |
| `Game.HasPath(from,to)` | reachability/path guard | VERIFIED source use |
| `Game.GetDistance(a,b)` | distance | VERIFIED source use |
| `Game.CellToDistance(v)` | convert configured cell/range units | VERIFIED source use |
| `Game.StopAutoPath()` | stop current auto path | VERIFIED source use |

Do not build target/combat around Ctrl+Tab, mouse clicks or screen coordinates when these semantic actions are available.

---

## 5. Skills — Auto Train / Auto Buff

### Identity and use

- `Game.UseSkill(skillID)` — shipped SkillBar semantic action.
- `Game.RequestUsingSkillWithTarget(skillID, RoleID)` — built-in support/combat path.
- `Game.RequestUsingSkillWithPos(...)` — positional skill path.
- `Game.GetSkillLuaData(skillID)` — skill runtime/template-facing data.
- `Game.CheckCondition(skillID)` — built-in condition check used by Auto.
- `Game.CanUseSkill(...)` — semantic skill guard exists.
- `Game.GetSkillCooldown(skillID)` — returns `passedTicks, cooldownTicks`.

Cooldown ready rule from shipped UI:

`cooldownTicks <= 0 OR passedTicks >= cooldownTicks`.

### Correct Nga My IDs for this snapshot

| SkillID | Exact Config identity |
|---:|---|
| `406` | Phật Quang Phổ Chiếu |
| `407` | **Xung Hư Dưỡng Khí** |
| `408` | Khởi Tử Hồi Sinh |
| `423` | **Kim Châm Độ Kiếp** |
| `424` | Thanh Tâm Phổ Thiện Chú |

Critical warning: legacy Lua name `KIMCHAMDOKIEP=407` is wrong as a human-readable identity. Actual Config Kim Châm is 423.

### Known support ranges/progress

From Config cross-check:

- 406: CastRange 15, AoE/support, ProgressTime 3000ms.
- 407: CastRange 15, PeacePlayer, ProgressTime 3000ms.
- 423: CastRange 15, PeacePlayer, ProgressTime 0.
- 424: CastRange 15, PeacePlayer, ProgressTime 1000ms.
- 408: CastRange 3, PeacePlayer, ProgressTime 10000ms.

For non-team peaceful targets, the read-only candidate source is VERIFIED, but exact server acceptance of each beneficial skill on every relationship type remains **RUNTIME PROOF NEEDED**.

---

## 6. Buff state

Preferred local source:

`Game.GetBuffs()`

Observed fields:

- `BuffID`
- `DurationTick` in milliseconds
- `Stack`.

Additional semantic APIs:

- `Game.GetBuffData(BuffID)`
- `Game.GetBuffProperties(BuffID)`
- `Game.HasBuff(...)`
- `Game.GetTargetBuffIcons(RoleID)`.

Status: **VERIFIED** for the documented local schema and API use.

Use buff state separately from HP state. Low HP does not imply the desired buff is absent.

---

## 7. Built-in Train start / stop / radius

Exact mode:

`C_AutoModel.Train = 1`.

Start:

`GUI.FindUI("AutoFight_Main"):StartAutoFight(C_AutoModel.Train)`.

Stop:

`GUI.FindUI("AutoFight_Main"):StartAutoFight(C_AutoModel.None)`.

Status: **VERIFIED from shipped Lua**.

The visible `Đánh quái` tab is configuration only; it is not the semantic start action.

Built-in Train settings include:

- monster whitelist/list;
- lure mode;
- train-in-radius;
- `RangerScan` (default 500);
- configured 7-skill list;
- combo/basic-skill flags;
- give-up-target-outside-radius.

When radius mode is enabled, start logic uses `Game.AutoSetFlag(RangerScan)`.

---

## 8. Map / movement / return-to-spot

Preferred APIs:

- `Game.GoTo(MapID, X, Y, callback)`
- `Game.MoveTo(X,Y)`
- `Game.MoveToEx(...)`
- `Game.GetCurrentMoveDestination()`
- `Game.IsMapReady()`
- `Game.GetLocalMapObjects()`
- `Game.GetNearbyObjects()`
- `Game.HasPath(...)`.

Travel proof should be:

`expected MapID + IsMapReady + valid current position + within tolerance`.

A fixed sleep after map change is not proof.

For saved Train spot return, persist `MapID/X/Y/Tolerance` in the external tool profile.

---

## 9. NPC navigation / interaction

Preferred route pattern from shipped Auto:

```text
GoToNPC(mapID,npcID)
 -> if map differs: Game.GoTo(mapID,-1,-1,...)
 -> Game.GetNPCPosition(npcID)
 -> Game.GoTo(mapID, X, Y,...)
 -> Game.GetNearestNPC(npcID)
 -> interact/select current NPC
```

Related semantic action:

`LuaSystemAPI_Game.ClickNPC(npcID)`

Direct native analysis verifies its internal flow approximately:

`StopAutoPath -> resolve NPC -> orient/select -> SendClickOnObject`.

Do not invent static NPC X/Y when `Game.GetNPCPosition(npcID)` exists.

---

## 10. Dynamic NPC dialog — treatment and other services

`GameDialog` runtime data stores:

`Selections[selectionID] = visibleText`.

Submit packet:

`CMD_SHOW_GAMEDIALOG = 100007`

Payload:

`selectionID:SelectedItemID`

Default `SelectedItemID = -1` when no reward item is selected.

Use for treatment/service flow:

```text
open current NPC
 -> wait actual GameDialog
 -> inspect current Selections
 -> match semantic text
 -> submit the actual selectionID
 -> wait dialog/HP/money/service state proof
```

There is no verified global fixed `Trị liệu` selection ID.

Static Lâu Lan candidate:

- Map 5 = Lâu Lan
- NPC 339 = Đỗ Thanh Đằng
- `ResName=LangZhong1`.

The static identity is VERIFIED; exact treatment selection remains runtime/server-driven.

---

## 11. Bag / inventory state

Preferred sources:

- `Game.GetFreeBagSpace()`
- `Game.GetItemsAtSite(C_ItemSite.Bag)`
- `Game.GetItemAtSite(site,pos)`
- `Game.GetItemData(dbID)`
- `Game.GetItemType(ItemID)`
- `Game.GetEquipType(ItemID)`
- `Game.IsItemSellable(ItemID)`
- `Game.IsItemThrowable(ItemID)`.

Identity rule:

- `ID` = current live instance ID
- `ItemID` = static template ID
- `Position` = current slot
- `Site` = current logical container
- Bag site = `10`.

Do not count empty UI cells/pixels to detect bag full.

---

## 12. Auto Sell exact request

Packet:

`CMD_NPC_SHOP_SELL_REQUEST = 200036`

Payload:

`itemInstanceID:NpcShopID:ShopID`.

Current `NpcShopID` and `ShopID` come from the current live shop state.

Original Lua guards include:

- reject quest ItemID range `40000000..49999999`;
- require `Game.IsItemSellable(ItemID)`.

Safe transaction loop:

```text
scan current bag
 -> choose ONE current instance
 -> send ONE sell request
 -> wait RemoveItem / UpdateItemsList / money/shop proof
 -> rescan
```

Never pre-build a 90-item/90-click mutation list from one stale snapshot.

---

## 13. Loot / ground item packs

Preferred sources/actions:

- `Game.GetNearbyItemPack(...)`
- `Game.GetNearestItemPack(...)`
- `Game.HasPath(...)`
- `Game.MoveToEx(...)`
- `Game.ClickToObject(...)`
- `Game.PickUpItemFromItemPack(itemPackID, slotIndex, UsingAuto)`.

Observed built-in pick-all path:

`Game.PickUpItemFromItemPack(itemPackID, -1, 1)`.

Status: **VERIFIED source semantics**.

Use bag-space state and current item-pack identity; do not OCR ground drops.

---

## 14. Revive / Đầu thai

Packet:

`CMD_REVIVE_DATA = 200063`.

Types:

- `1` = normal / Đầu thai
- `2` = newbie revive
- `3` = skill revive.

Status: **VERIFIED from Lua**.

Completion proof:

`local role alive + Revival state/UI cleared + map ready + valid position`.

Do not treat packet send success or elapsed time as proof of revive completion.

---

## 15. Team / follow

Current team state:

`C_TeamData`, with `Game.RoleData.TeamID > 0`.

Observed team-member fields:

- `RoleID`
- `RoleName`
- `Level`
- `FactionID`
- `MapID`
- `Hp`
- `MaxHp`
- `AvartaID`
- `PosX`
- `PosY`.

Exact team action enum includes:

`Create=0, Kick=1, Disband=2, ChangeLeader=3, LeaveTeam=4, AcceptJoin=5, RejectJoin=6, RequestJoin=7, AcceptInvite=8, RejectInvite=9, RequestInvite=10`.

Verified leave request:

`CMD_TEAM_ACTION`, payload `4:selfRoleID`.

Built-in Follow:

`AutoFight_Main:TurnOnFollowTarget(RoleID)`.

Nearby precise position comes from `Game.GetNearTeammates`; out-of-AOI/cross-map fallback uses team `MapID/PosX/PosY` with `Game.GoTo`.

---

## 16. Server-authoritative proof/events useful to the orchestrator

Prefer these result classes over sleeps:

- target HP/death/identity refresh;
- cooldown transition;
- progress begin/end/update;
- map ID/readiness/position change;
- `UpdateTeamData` / team state change;
- `RemoveItem` / `UpdateItemsList` / money/shop update;
- current NPCShop state after `CMD_NPC_SHOP_DATA`;
- actual `GameDialog` appearance/change;
- local alive/dead/Revival state;
- bag-space/item-pack changes.

Timeout means **failure/unknown**, not success.

---

## 17. Per-PID external tool rule

Each game process must own independent:

```text
Resolver
Snapshots
Feature state machines
Action gate
Dispatcher state
Profiles
Metrics
Last action / last proof
```

Static Config databases can be shared read-only across clients.

Never let one PID's live pointers/state/action result leak into another PID.

---

## 18. Auto-tool action priority

Recommended arbitration order:

```text
Captcha/manual pause
 > fatal/error recovery
 > Revive/death recovery
 > map transition completion
 > critical self survival
 > critical external Buff/Heal
 > in-progress Sell/NPC transaction
 > Party transaction
 > normal Buff
 > Train target/chase/cast
 > Loot
 > background travel/spot optimization
```

Only one mutable action in flight per PID.

---

## 19. Known targeted gaps — do not broad reverse

Still worth one narrow runtime proof when implementation reaches them:

1. exact server acceptance rules for specific beneficial Nga My skills on non-team PeacePlayers;
2. actual treatment `GameDialog.Selections`/confirmation sequence at the intended healer NPC;
3. any specific party-join request payload/path still not already proven by the chosen Lua flow;
4. external managed `System.Action` construction/rooting live proof for the final MainThread bridge;
5. additional nearby actor fields only when a concrete auto feature cannot work with the already-mapped schema.

Everything else should first be implemented from the existing semantic knowledge before new reverse engineering.
