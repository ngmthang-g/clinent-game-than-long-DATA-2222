# Built-in Auto Fight engine — exact architecture recovered from Lua

Status: **VERIFIED source semantics** from embedded `AutoFight_Main` and related Lua TextAssets.

## Major conclusion

The client already contains a substantial internal automation engine; it is not just a UI toggle.

`C_AutoModel`: `None=0`, `Train=1`, `PK=2`, `Quest=3`, `AutoPath=4`, `Fllow=5`, `FuBen=6`.

`AutoFight_Main:StartAutoFight(mode)` dispatches the semantic flows. External automation should prefer these internal operations instead of rebuilding combat with mouse clicks.

## Player/world state

The engine uses `Game.RoleData.MapID`, role X/Y, team state, moving/busy/progress state, mount state, map-ready state and current chase target.

## Monster discovery

`FindBestTarget()` uses `Game.GetNearbySpritesWithPredicate(predicate, centerPosition)`.

Observed MapObject fields:
- `Type`
- `IsDeath`
- `RoleID`
- `ResID`
- `Position`

Filters include Monster type, alive state, ignored targets, optional quest MonsterID, range, lure/band list and optional whitelist by `ResID`.

## Combat loop

Semantic APIs used include:
- `Game.HasPath`
- `Game.StopAutoPath`
- `Game.SelectTarget`
- `Game.ChaseTarget`
- `Game.RequestUsingSkillWithTarget`
- `Game.RequestUsingSkillWithPos`
- `Game.ReloadTarget`
- `Game.IsSelectTargetDie`
- `Game.GetCurrentHP`

The engine also handles stuck/busy/path/HP-not-changing cases and can ignore problematic targets.

## Skills/support

The engine selects usable skills from configured lists. Confirmed Nga My/support constants include:
- `406` Phật Quang Phổ Chiếu
- `424` Thanh Tâm Phổ Thiện Chú
- `407` Kim Châm Độ Kiếp
- `408` Cải Tử Hoàn Sinh

Config contains the full Skills table; these are not the only heal/buff skills.

## Loot engine

`DoPickItem()` uses `Game.GetNearbyItemPack`, `Game.HasPath`, `Game.MoveToEx`, `Game.ClickToObject`, `Game.GetFreeBagSpace`, `Game.PickUpItemFromItemPack`.

The built-in filter distinguishes material/equipment/quest/gem categories and checks equipment star data. Bag capacity can therefore be checked without opening the bag UI.

## Death/revive

`DeathActive()` records death map/position and supports auto revive plus auto comeback using `Game.GoTo`. Exact revive packet semantics are in `features/AUTO_REVIVE.md`.

## NPC navigation

`GoToNPC(mapID,npcID)`:
1. if map differs, `Game.GoTo(mapID,-1,-1,callback)`;
2. query `Game.GetNPCPosition(npcID)`;
3. `Game.GoTo(mapID,npcPos.X,npcPos.Y,callback)`;
4. query `Game.GetNearestNPC(npcID)`;
5. interact with `Game.SelectTarget(NearestNPC.RoleID,true)` when dialog/timing state permits.

This proves manual NPC X/Y is normally unnecessary. `GoToMonster` uses `Game.GetMonsterPosition` similarly.

## Dynamic GameDialog

Quest auto stores incoming dialog data and inspects server-provided `Selections`. For recognized choices it sends `CMD_SHOW_GAMEDIALOG` with `selectionID:itemPick`. Generic acknowledgement handles selection ID `99999` or text `Ta biết rồi`.

This is the correct pattern for server-driven NPC actions: inspect actual selections instead of blindly clicking a screen button.

## Auto PK

`FindAutoPKTarget()` uses `Game.GetNearByEnemies(false,true,-1)` plus target reload/lock semantics.

## FuBen

`AutoFight_Main` delegates dungeon execution to `AutoFight_FuBen`. `FuBenScenarios.xml` contains 19 scenario definitions with dungeon map, gather map/NPC/X/Y, min players/level and timeout.

## Correct tool architecture

`read-only snapshot -> state machine -> max one action -> Unity/main-thread dispatcher -> internal Game/Lua action -> wait for state proof -> next action`.

Do not implement Auto Train as repeated clicks on the “Đánh quái” tab. The tab is configuration; `StartAutoFight(C_AutoModel.Train)` is the semantic engine entry.
