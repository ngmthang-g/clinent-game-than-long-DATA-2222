# Runtime Snapshot Contract — automation-only external state model

Purpose: define the **small, typed, per-PID read-only snapshot model** needed by the Thần Long auto tool so future builders do not retain unstable client/Lua objects or re-discover which fields matter.

Status: **SYNTHESIZED CONTRACT from VERIFIED shipped Lua/runtime schemas**. Every field below is labelled by source strength; no new client field is invented merely to make the structure look complete.

Canonical sources:

- `analysis/14_NEARBY_ENTITY_UI_SCHEMA.md`
- `analysis/17_BUFF_RUNTIME_SCHEMA.md`
- `analysis/18_SKILLBAR_COOLDOWN_QUICKSKILLS.md`
- `analysis/20_BAG_GRID_SHOP_UI_RUNTIME.md`
- `analysis/22_MAP_MINIMAP_RUNTIME.md`
- `analysis/25_TEAM_RUNTIME_FOLLOW.md`
- `analysis/34_AUTO_STATE_ACTION_PROOF_MATRIX.md`

---

# 1. Core rule

The external tool should copy **values**, not keep client object pointers.

```text
client/Lua/IL2CPP object
 -> read semantic fields now
 -> copy to tool-owned immutable snapshot
 -> discard client object reference
```

Never use a Lua/C# object pointer as long-lived identity across:

- next scan;
- UI rebuild;
- map transition;
- death/revive;
- bag mutation;
- another PID.

Stable identities are semantic IDs such as RoleID, item instance ID and SkillID.

---

# 2. Snapshot envelope — every per-PID publication

Recommended tool-owned envelope:

```text
Pid
RoleID
SnapshotVersion
CapturedTick
WorldGeneration
MapID
MapReady
CaptchaActive
ProgressActive
```

`WorldGeneration` is a **tool-owned counter**, not a game field. Increment it when a map/loading generation changes so old nearby objects/items/UI transaction state can be invalidated cheaply.

Before any mutable action, reject a snapshot when:

- PID no longer exists;
- snapshot is older than the feature freshness threshold;
- map generation changed;
- local role is dead when the action requires alive state;
- map is not ready;
- Captcha/manual pause is active;
- another mutable action owns the action gate.

---

# 3. LocalRoleSnapshot

## VERIFIED source

`Game.RoleData` plus Auto/UI source usage.

Fields directly proven in shipped Lua:

```text
Name
Level
AvartaID
HP
MaxHP
MP
MaxMP
Rage
MaxRage
HPPercent
MPPercent
FactionID
TeamID
MapID
Position.X
Position.Y
IsDeath
IsRiding
AutoSettings
```

Useful semantic queries around the role:

```text
Game.GetCurrentHP()
Game.IsMoving()
Game.CanMove()
Game.IsRoleBusy()
Game.IsProgress()
Game.IsMapReady()
Game.SelectedTarget
Game.GetCurrentMoveDestination()
```

For the auto tool, normalize only what features use:

```text
RoleID              # include when resolved from current role identity path
Name
Level
FactionID
TeamID
HP
MaxHP
HPPercent
MP
MaxMP
MPPercent
MapID
X
Y
IsDeath
IsRiding
IsMoving
IsBusy
IsProgress
MapReady
SelectedTargetRoleID optional
CapturedTick
```

### Derived values

Do not trust a derived HP% from an old scan. Compute from the same snapshot:

```text
HPPercentDerived = MaxHP > 0 ? HP * 100 / MaxHP : 0
```

The tool may preserve the game-provided HPPercent for diagnostics, but decision logic should use internally consistent fields from one publication.

---

# 4. NearbyPeacePlayerSnapshot

## VERIFIED source

`Game.GetNearByPeacePlayers(limit)`.

Fields directly accessed by shipped nearby-player UI:

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

Recommended external record:

```text
RoleID
Name
Level
FactionID
GuildName
HP
MaxHP
HPPercentDerived
TeamRank
AvartaID optional
LastSeenTick
SourceScanVersion
WorldGeneration
```

### Important current boundary

A generic `Position` or `IsDeath` field for every arbitrary PeacePlayer is **not yet proven by this specific nearby-player API**.

Do not silently add fake/default values.

If Auto Buff requires position/death for a non-team target, resolve them through a proven target/nearby-object route or perform one targeted runtime schema proof.

For team members, exact HP/map/backup position and nearby precise position are already separately available through team APIs.

---

# 5. NearbyEnemy / TrainTargetSnapshot

## VERIFIED built-in Train source

`Game.GetNearbySpritesWithPredicate(predicate, centerPosition)`.

Fields directly used by shipped Auto Train:

```text
Type
IsDeath
RoleID
ResID
Position
```

Recommended minimal target record:

```text
RoleID
ResID
Type
IsDeath
X
Y
LastSeenTick
SourceScanVersion
WorldGeneration
```

Optional interpreted static data may be joined by `ResID` only when useful:

```text
MonsterName
ConfiguredLevel
ConfiguredMaxHP
MonsterType / policy tags
```

Never treat static monster MaxHP as current live HP.

### Current HP boundary

The selected-target UI provides `HPPercent` for Monster/Boss/Pet through `Game.SelectedTarget`, but the currently documented Train search record does not prove live HP/MaxHP fields for every unselected nearby monster.

Basic Train does not require broad re-reverse for this: target discovery/death/position are already sufficient for the shipped target loop. Resolve exact live monster HP only if a concrete future policy needs it.

---

# 6. SelectedTargetSnapshot

## VERIFIED source

`Game.SelectedTarget`.

Fields directly consumed by shipped target UI:

```text
RoleID
Type
Avarta
Name
HPPercent
MPPercent
RagePercent
EnergyPercent
Level
FactionID
MonsterBelongState
```

Recommended tool record:

```text
RoleID
Type
Name
HPPercent
MPPercent optional
EnergyPercent optional
Level
FactionID
MonsterBelongState optional
LastSeenTick
WorldGeneration
```

Primary use:

- prove `SelectTarget(RoleID)` actually selected the expected object;
- reject stale/dead/switched targets;
- monitor target HP% when exact HP is not needed.

`Game.GetTargetBuffIcons(RoleID)` may be attached as an optional visual-buff summary, but it is not equivalent to a proven arbitrary-target BuffID/Duration list.

---

# 7. MapSnapshot

## VERIFIED sources

```text
Game.RoleData.MapID
Game.RoleData.Position
Game.IsMapReady()
Game.GetMapName()
Game.GetMapSize()
Game.GetCurrentMoveDestination()
Game.GetLocalMapObjects()
Game.GetNearbyObjects()
```

Recommended external state:

```text
MapID
MapName optional
MapReady
X
Y
MoveDestinationX optional
MoveDestinationY optional
HasMoveDestination optional/tool-normalized
WorldGeneration
CapturedTick
```

### Travel success proof

```text
MapID == expected
AND MapReady == true
AND current position valid
AND distance(current, destination) <= tolerance
```

`GetCurrentMoveDestination()` is diagnostic/transition evidence; elapsed time is not travel success.

---

# 8. LocalMapObjectSnapshot

`Game.GetLocalMapObjects()` returns static/current-map semantic objects with directly consumed:

```text
Type
Name
Position
```

Known handled types:

```text
NPC
Monster
GrowPoint
Zone
Portal
```

Recommended lookup record:

```text
Type
Name
X
Y
WorldGeneration
```

Use it for current-map browsing/cross-checking, not as a replacement for live RoleID-based NPC/monster state when an action needs a dynamic instance.

---

# 9. NPC / ItemPack nearby records

## Nearest NPC — VERIFIED shipped background UI

Fields:

```text
Position
Name
RoleID
```

Recommended:

```text
RoleID
Name
X
Y
LastSeenTick
WorldGeneration
```

For template/service routing, preserve the configured/static NPCID separately from live RoleID when both concepts appear. Do not collapse them into one integer without evidence.

## Nearest item pack — VERIFIED

Fields consumed:

```text
Position
RoleID
```

Recommended:

```text
ItemPackRoleID
X
Y
LastSeenTick
WorldGeneration
```

Use fresh pack identity for pickup; do not reuse an old pack after it disappears/changes.

---

# 10. BagSnapshot / ItemInstanceSnapshot

## VERIFIED source

`Game.GetItemsAtSite(C_ItemSite.Bag)` and `Game.GetFreeBagSpace()`.

Bag site:

`10`.

Essential item identity:

```text
ID        = live instance/database ID
ItemID    = static template ID
Position  = current slot
Site      = logical container
```

Other commonly documented live fields:

```text
Quantity
Bound
Durability
```

Recommended tool records:

```text
BagSnapshot:
  FreeSlots
  ItemCount
  Version
  CapturedTick
  Items[]

ItemInstanceSnapshot:
  ID
  ItemID
  Site
  Position
  Quantity
  Bound
  Durability optional
  ItemType optional/cache
  EquipType optional/cache
  IsSellable optional/cache
```

### Mutation rule

After **any successful bag mutation**, publish a new bag version. Never keep executing a precomputed slot sequence.

Strong invalidators/results:

- AddItem;
- RemoveItem (`site:dbID:position`);
- UpdateItemsList;
- fresh `GetItemsAtSite` result.

---

# 11. LocalBuffSnapshot

## VERIFIED source

`Game.GetBuffs()`.

Live fields:

```text
BuffID
DurationTick   # ms
Stack
```

`Game.GetBuffData(BuffID)` adds at least:

```text
Level
Stack
```

Recommended external record:

```text
BuffID
Level optional
DurationTick
Stack
LastSeenTick
```

Static/cache-by-ID enrichment may include Name/Properties, but do not call expensive property description logic every scan.

### Buff state events

Verified event IDs:

```text
AddBuff = 15
UpdateBuff = 16
RemoveBuff = 17
```

These are excellent snapshot invalidation/refresh triggers.

---

# 12. SkillCooldownSnapshot

## VERIFIED source

`Game.GetSkillCooldown(skillID)`.

Normalize:

```text
SkillID
PassedTicks
CooldownTicks
RemainingTicks = max(0, CooldownTicks - PassedTicks)
Ready = CooldownTicks <= 0 OR PassedTicks >= CooldownTicks
CapturedTick
```

Before cast also use semantic guards when applicable:

```text
Game.HasSkill(skillID)
Game.CheckCondition(skillID)
Game.CanUseSkill(...)
Game.GetSkillLuaData / GetSkillTemplateData
```

Do not infer cooldown from UI animation or fixed sleeps.

---

# 13. TeamSnapshot

## VERIFIED source

`Game.RoleData.TeamID`, global `C_TeamData`, `Game.GetNearTeammates(...)`.

Team-level:

```text
TeamID
LeaderID
```

Member fields directly consumed by shipped code:

```text
RoleID
RoleName
Level
FactionID
MapID
Hp
MaxHp
AvartaID
PosX
PosY
```

Nearby team record additionally provides precise current `Position` when in AOI.

Recommended normalized member:

```text
RoleID
Name
Level
FactionID
MapID
HP
MaxHP
HPPercentDerived
BackupX
BackupY
NearbyX optional
NearbyY optional
IsLeader
LastSeenTick
```

Use nearby position for local range/cast/follow; use team MapID/backup position for out-of-AOI/cross-map fallback.

---

# 14. ShopTransactionSnapshot

Do not model shop readiness as a boolean derived from “NPC was clicked”.

Verified live shop state comes from inbound `CMD_NPC_SHOP_DATA=200034` and current `NPCShop` data.

Fields needed for Auto Sell:

```text
NpcShopID
ShopID          # CurrentShopData.ID
IsGuildShop
CategoryName optional
TotalSellItem optional
CapturedTick
WorldGeneration
```

Sell action is valid only if current shop data belongs to the active transaction and `IsGuildShop == false`.

Any map change, dialog replacement, shop close or generation change invalidates this snapshot.

---

# 15. GameDialogSnapshot

Verified runtime shape:

```text
Selections[selectionID] = visibleText
SelectedItemID
```

Recommended external copy:

```text
DialogGeneration
WorldGeneration
NpcContext optional if proven/current
Selections[]:
  SelectionID
  VisibleText
SelectedItemID
CapturedTick
```

For treatment/vendor/service actions, choose from the **current copied selections**, then revalidate that the dialog generation did not change before sending.

Never hardcode a global treatment selection ID from one opening.

---

# 16. RevivalSnapshot

Verified server-driven fields:

```text
TimeLeft
IsEnableReviveNewbie
IsEnableBySkill
Action/open-update-close state
```

Recommended tool state:

```text
Active
TimeLeftMs
NewbieAllowed
SkillReviveAllowed
Generation
CapturedTick
```

Revive completion is not packet-send success. Publish ALIVE only after local role + Revival lifecycle + map-ready/position state agree.

---

# 17. Freshness classes

Not every subsystem needs the same polling frequency. Recommended **tool policy**, not a recovered client constant:

```text
FAST: local role / target / movement / critical buff candidate
MEDIUM: nearby players/monsters/team/bag/cooldowns
EVENT-FIRST: bag events, buff events, Revival, GameDialog, NPCShop
SLOW: static map objects / names / template joins
```

Use events to invalidate/refresh snapshots where known. Do not spin every semantic query every frame merely because it exists.

---

# 18. Per-feature minimum snapshot dependencies

## Auto Train

```text
LocalRole
Map
SelectedTarget
NearbyTrainTargets
SkillCooldowns
Progress/Captcha
optional Loot/Bag
```

## Auto Buff

```text
LocalRole
NearbyPeacePlayers
SkillCooldowns
Progress/Captcha
optional SelectedTarget/Team/TargetBuffIcons
```

## Auto Sell

```text
LocalRole
Map
Bag
GameDialog optional
ShopTransaction
Captcha/Revival
saved TrainSpot profile
```

## NPC treatment

```text
LocalRole
Map
GameDialog
Captcha/Revival
```

## Revive

```text
LocalRole
Revival
Map
saved TrainSpot profile
```

## Party / Follow

```text
LocalRole
Team
NearbyPeacePlayers / NearbyTeammates
Map
```

---

# 19. What remains genuinely unresolved for snapshots

Do not broad reverse for completeness. Current narrow gaps are:

1. exact `Position` / death state for arbitrary **non-team** PeacePlayer only if the chosen Auto Buff implementation requires it and no current target/world-object route provides it;
2. exact live HP/MaxHP for every unselected nearby monster only if a future Train policy genuinely needs absolute values rather than death/position/selected-target HP%;
3. richer arbitrary-target BuffID/duration list; currently only local BuffID/duration/stack and target buff icons are proven;
4. any exact Train-running flag only if implementation cannot reliably use the current Auto service/state ownership.

Everything else above is sufficient to define the external read-only data model without returning to CE/OCR/broad heap scanning.