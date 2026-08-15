# Feature specification — Auto Train / Đánh quái

Status: **built-in engine architecture VERIFIED**.

The UI tab “Đánh quái” configures the feature. Semantic mode is `C_AutoModel.Train = 1`; `AutoFight_Main:StartAutoFight(C_AutoModel.Train)` sets current mode, clears flags and starts the train engine.

Target discovery uses `Game.GetNearbySpritesWithPredicate`. Observed target fields include `Type`, `IsDeath`, `RoleID`, `ResID`, `Position`.

Filters include Monster type, alive, reachable/in range, optional ResID whitelist, ignored/banded state and quest MonsterID.

Attack flow selects by RoleID, chases to skill range, casts through `RequestUsingSkillWithTarget` or `RequestUsingSkillWithPos`, reloads target state and handles death/stuck/path failure.

Opening Auto and clicking the “Đánh quái” tab only controls a configuration UI; it is not the best semantic start action. Stale UIButton pointers are fragile across UI transitions.

Recommended tool architecture:

`read-only snapshot -> TrainState -> target selector -> max one queued action -> Unity main-thread dispatcher -> internal Game/Lua action -> state proof -> next action`.

For Auto Sell integration: save start map/position and prior mode, pause train, sell, return via `Game.GoTo`, verify position/map, then resume Train.
