# Auto State -> Action -> Proof Matrix

Purpose: convert the recovered client knowledge into a compact contract for building the large Thần Long auto tool.

This document is deliberately **not** an encyclopedia. It answers five implementation questions for each feature:

1. what state must be read;
2. what guards must pass;
3. what single semantic action may be issued;
4. what concrete result proves success;
5. when to abort/rescan/escalate.

Canonical principle:

```text
fresh snapshot
 -> decide
 -> revalidate
 -> ONE mutable action
 -> wait for proof
 -> rescan
```

A timeout is not success proof.

---

## 1. Common snapshot freshness contract

Recommended minimum fields attached to every external snapshot:

```text
Pid
RoleID / object identity
SnapshotVersion
CapturedTick
MapID
MapReady
Loading/Progress/Captcha flags
```

For nearby objects/items:

```text
LastSeenTick
SourceScanVersion
```

Before an action, reject a candidate if:

- it came from an older map/load generation;
- object identity disappeared from the newest scan;
- local role died;
- Captcha/manual pause became active;
- another mutable action is already in flight;
- required UI/shop/dialog state changed.

Do not retain managed/Lua/UI object pointers as external identity across scans.

---

# 2. Auto Train

## START_TRAIN

### Read

- local role alive;
- `Game.IsMapReady()`;
- no Captcha/manual pause;
- no incompatible progress state;
- current auto/orchestrator ownership.

### Action

`AutoFight_Main:StartAutoFight(C_AutoModel.Train)` where `Train=1`.

### Proof

Prefer observed Auto mode/state/UI status consistent with Train, followed by normal target/movement/combat state from the built-in engine.

### Failure

If map/loading/death interrupts, do not retry-spam. Yield to map/revive state.

---

## STOP_TRAIN

### Action

`StartAutoFight(C_AutoModel.None)`.

### Proof

No Train-owned target/chase/skill action continues and the orchestrator owns movement/action control.

### Use

Mandatory before Sell/NPC travel/explicit spot switching if those flows would conflict with Train movement/combat.

---

## FIND_TARGET

### Read

`Game.GetNearbySpritesWithPredicate(...)` and current Train center/radius/filter settings.

Candidate fields already used by shipped Auto:

`Type, IsDeath, RoleID, ResID, Position`.

### Guard

- monster/eligible target type;
- alive;
- fresh in AOI;
- allowed by whitelist/radius policy;
- path/reachability acceptable;
- not currently quarantined/ignored as stuck target.

### Action

Normally `Game.SelectTarget(RoleID)` or let built-in Train own the target loop.

### Proof

fresh selected target identity/state equals expected RoleID or built-in engine advances to chase/cast.

### Failure

candidate disappears/dead/unreachable -> invalidate candidate and rescan; do not keep replaying one stale RoleID.

---

## CHASE_TARGET

### Read

local position, target position, Skill CastRange, current target freshness.

### Guard

`Game.HasPath`, target alive/present, map ready.

### Action

`Game.ChaseTarget(...)`.

### Proof

movement destination/range changes toward target; target remains fresh; eventual distance reaches the requested cast band.

### Failure

no path, target leaves AOI, repeated no-progress -> mark target temporarily bad and rescan.

---

## CAST_COMBAT_SKILL

### Read

SkillID, target RoleID/position, `GetSkillCooldown`, condition/availability, progress/busy state.

### Guard

- skill learned/condition-valid;
- cooldown ready;
- target valid/alive;
- target/range requirement satisfied;
- one action gate free.

### Action

`RequestUsingSkillWithTarget` or `RequestUsingSkillWithPos` depending on skill semantics.

### Proof

one or more:

- cooldown transitions from ready -> active;
- progress/cast event starts/finishes;
- target HP changes;
- death/result state changes.

### Failure

no consistent result before timeout -> rescan all guards; never blindly repeat at fixed frequency.

---

# 3. Auto Buff / Nga My support

## BUILD_CANDIDATE_LIST

### Read

`Game.GetNearByPeacePlayers(limit)`.

Verified fields:

`RoleID, Name, Level, FactionID, HP, MaxHP, GuildName, AvartaID, TeamRank`.

### Guard/filter

User policy may filter by:

- RoleID/name;
- guild;
- faction;
- level range;
- MaxHP range;
- HP threshold;
- include/exclude self.

### Decide

Compute HP% and choose **one** target from the fresh snapshot.

Examples:

- lowest HP% first;
- highest MaxHP among targets below threshold;
- explicit RoleID priority.

Do not queue all low-HP players from one scan.

---

## BUFF/HEAL_TARGET

### Read

fresh target HP/MaxHP + SkillID + skill cooldown/condition + range.

### Correct skill identities

- 406 Phật Quang Phổ Chiếu
- 407 **Xung Hư Dưỡng Khí**
- 408 Khởi Tử Hồi Sinh
- 423 **Kim Châm Độ Kiếp**
- 424 Thanh Tâm Phổ Thiện Chú.

### Action pattern from built-in support donor

```text
GetSkillLuaData(skillID)
 -> calculate distance / CastRange
 -> if too far: ChaseTarget(RoleID,...)
 -> RequestUsingSkillWithTarget(skillID, RoleID)
```

### Proof

Preferred combination:

- target HP changes/reaches threshold;
- desired buff/icon appears when applicable;
- skill cooldown activates;
- progress state is consistent with cast.

### Important unresolved runtime boundary

The client definitely exposes non-team PeacePlayers for read-only targeting. Server acceptance of each beneficial skill on every non-team relationship is not yet universally proven. Record the first live acceptance/rejection result per intended skill rather than inventing a rule.

---

# 4. Bag evaluation

## BAG_CHECK

### Read

`Game.GetFreeBagSpace()` and optionally `GetItemsAtSite(Bag)`.

Bag site = `10`.

### Decide

Examples:

```text
free == 0 -> SELL_REQUIRED
free <= configured threshold -> SELL_SOON
else -> continue Train
```

No bag UI needs to be opened to count free cells.

---

# 5. Auto Sell

## CHOOSE_SELL_ITEM

### Read

fresh `GetItemsAtSite(Bag)`.

Preserve identity correctly:

- `ID` = live instance
- `ItemID` = template
- `Position` = slot
- `Site` = container.

### Guards

At minimum:

- current instance still exists;
- quest ItemID range `40000000..49999999` -> do not sell;
- `Game.IsItemSellable(ItemID)` true;
- user keep/whitelist policy false;
- weapon/equipment preservation policy applied correctly.

Static Weapon truth for `Equips`: `EquipPoint == 0`.

---

## OPEN_VENDOR

### Read

current map, chosen vendor NPCID, map ready.

### Action

Use `Game.GetNPCPosition(npcID)` + `Game.GoTo` / `GoToNPC` + semantic NPC interaction.

### Proof

actual current NPCShop data/state exists after `CMD_NPC_SHOP_DATA` / UI state.

### Failure

NPC not available / path fails / wrong dialog -> abort transaction; do not send sell packet without current shop IDs.

---

## SELL_ONE

### Read

fresh item instance + current `NpcShopID` + `ShopID`.

### Action

`CMD_NPC_SHOP_SELL_REQUEST = 200036`

payload:

`itemInstanceID:NpcShopID:ShopID`.

### Proof

one or more consistent server-authoritative results:

- sold instance disappears;
- RemoveItem/UpdateItemsList observed;
- money/shop update consistent with sale.

### Next

**Rescan bag.** Select a new current instance from the new snapshot.

Never advance using an old cached slot list.

---

## EXIT_SELL_AND_RETURN

### Read

saved Train spot profile `MapID/X/Y/Tolerance`.

### Action

close/yield shop state as required -> `Game.GoTo(savedMap, savedX, savedY)`.

### Proof

expected MapID + map ready + fresh position inside tolerance.

Only then resume Train.

---

# 6. NPC Trị liệu

## GO_HEALER

Known static candidate:

`NPC 339 = Đỗ Thanh Đằng`, Map 5 Lâu Lan, `LangZhong1`.

### Action

semantic NPC route using `GetNPCPosition` / `GoToNPC` / interaction.

### Proof

current NPC GameDialog appears.

---

## SELECT_TREATMENT

### Read

actual current:

`GameDialog.Selections[selectionID] = visibleText`.

### Decide

find treatment/service text from the live dialog. Do **not** hardcode one global selection ID.

### Action

`CMD_SHOW_GAMEDIALOG = 100007`

payload:

`actualSelectionID:-1`

unless the current service explicitly requires a selected item ID.

### Proof

HP/money/dialog/service state changes consistently with treatment.

### Runtime gap

The exact text/selection/possible second confirmation for the desired healer must be captured once in the live server state.

---

# 7. Death / revive

## DETECT_DEATH

Read local role alive/dead state and Revival state/UI.

Record death timestamp for rolling spot metrics if adaptive spot switching is enabled.

---

## REVIVE

### Action

`CMD_REVIVE_DATA = 200063`.

Types:

- `1` normal / Đầu thai
- `2` newbie
- `3` skill revive.

### Proof

- local role alive;
- Revival state/UI cleared;
- expected map ready;
- valid position.

### Next

If Auto Comeback/spot-return policy is enabled, travel to saved spot and verify arrival before restarting Train.

---

# 8. Loot

## FIND_ITEM_PACK

### Read

`GetNearbyItemPack` / `GetNearestItemPack`.

### Guards

- pack fresh/present;
- path reachable;
- bag capacity/policy permits pickup;
- Train/orchestrator action ownership permits temporary loot action.

### Action

Built-in semantic path uses:

`MoveToEx -> ClickToObject -> PickUpItemFromItemPack`.

Observed pick-all:

`PickUpItemFromItemPack(itemPackID, -1, 1)`.

### Proof

pack disappears/changes or bag item/space state changes consistently.

---

# 9. Party / Follow

## TEAM_STATE

Read:

- `Game.RoleData.TeamID`;
- `C_TeamData.LeaderID`;
- `C_TeamData.TeamMember[]`.

Member data includes RoleID/name/level/faction/map/HP/MaxHP/backup X/Y.

---

## LEAVE_TEAM

Verified action:

`C_TeamAction.LeaveTeam = 4`

through `CMD_TEAM_ACTION`, payload:

`4:selfRoleID`.

### Proof

`Game.RoleData.TeamID` / `C_TeamData` updates to no-team state.

Do not re-trace this action; it is already documented.

---

## FOLLOW_MEMBER

Preferred built-in semantic entry:

`AutoFight_Main:TurnOnFollowTarget(RoleID)`.

Nearby member:

`GetNearTeammates` -> precise `Position` -> `Game.MoveTo`.

Out of AOI:

team `MapID/PosX/PosY` -> `Game.GoTo` fallback.

### Proof

fresh position/distance/map state trends toward the selected teammate.

---

# 10. Cross-feature arbitration

One PID must never let Train, Buff, Sell, Revive and Party mutate simultaneously.

Recommended priority:

```text
CAPTCHA / MANUAL PAUSE
  > ERROR/FATAL RECOVERY
  > REVIVE
  > MAP TRANSITION COMPLETION
  > CRITICAL SELF SURVIVAL
  > CRITICAL BUFF/HEAL
  > CURRENT SELL/NPC TRANSACTION
  > CURRENT PARTY TRANSACTION
  > NORMAL BUFF
  > TRAIN TARGET/CHASE/CAST
  > LOOT
  > SPOT OPTIMIZATION/TRAVEL
```

A lower-priority feature yields; it does not issue another mutable action behind the current action.

---

# 11. Adaptive train-spot switching

Useful per-spot metrics:

- rolling deaths;
- active Train time;
- loot events;
- loot value if available;
- bag pressure/free-space delta;
- idle/no-target time;
- travel failures;
- party availability if relevant.

### Death rule

Use rolling timestamps, e.g. more than configured N deaths in 30 minutes -> quarantine spot and change to the next enabled spot.

Do not implement a simple counter that resets on a timer boundary.

### Loot-efficiency rule

Bag-not-full-after-30m is a weak metric because stackable drops may not consume slots.

Prefer:

`LootEvents / activeTrainMinute`, optionally item value and bag-pressure metrics.

---

# 12. Failure/result codes worth standardizing

Suggested external reason codes:

```text
OK
STALE_SNAPSHOT
ACTION_GATE_BUSY
MAP_NOT_READY
ROLE_DEAD
CAPTCHA_PAUSE
PROGRESS_BLOCKED
TARGET_GONE
TARGET_DEAD
NO_PATH
SKILL_NOT_READY
SKILL_REJECTED_OR_NO_PROOF
NPC_NOT_FOUND
DIALOG_NOT_READY
DIALOG_SELECTION_NOT_FOUND
SHOP_NOT_READY
ITEM_GONE
ITEM_NOT_SELLABLE
SELL_NO_PROOF
TRAVEL_TIMEOUT
REVIVE_NO_PROOF
CLIENT_GONE
DISPATCHER_NOT_READY
```

Keep failure reason separate from timeout duration. This makes future AI/debugging able to distinguish bad data, bad state, server rejection and action-bridge failure.

---

# 13. What still needs targeted proof

Do **not** broad reverse the client again. Remaining implementation-facing unknowns are narrow:

1. external Action/MainThread live proof;
2. actual Trị liệu dialog sequence for the chosen healer/service;
3. non-team beneficial-skill server acceptance by intended skill/relationship;
4. exact join-party request path only if the chosen team flow still lacks a verified payload;
5. any additional actor field only when a concrete auto feature cannot be implemented from current semantic snapshots.

Everything else in this matrix should first be implemented/reused from existing VERIFIED client knowledge.
