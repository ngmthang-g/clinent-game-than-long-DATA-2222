# Feature specification — Auto Train / Đánh quái

Status: **built-in engine architecture and UI start/stop entrypoints VERIFIED**.

## Exact semantic mode

`C_AutoModel.Train = 1`.

The core start action is:

`AutoFight_Main:StartAutoFight(C_AutoModel.Train)`.

This sets current mode, disables `Game.EnableAutoF1`, clears the auto marker/flag and starts `AutoTrainStart()`.

Stop action:

`AutoFight_Main:StartAutoFight(C_AutoModel.None)`.

## Exact shipped UI wrapper

`TopIcon:AutoTrainClick()` performs:

1. `AutoTrainService = GUI.FindUI("AutoFight_Main")`;
2. if found -> `AutoTrainService:StartAutoFight(C_AutoModel.Train)`;
3. `self:ShowAutoStatus(C_AutoModel.Train)`.

`TopIcon:AutoStopClick()` similarly calls `StartAutoFight(C_AutoModel.None)`.

This fully resolves the old question about the visible AUTO menu: **opening AUTO and clicking the `Đánh quái` settings tab is not required to start Train mode.**

The `AutoFight_Layout` toggle `ToggleAutoMonsterTab` only changes the visible settings tab through `AutoFight:ToggleTabHeaderSelected`.

## TopIcon auto menu meanings

- `AutoFightClick()` -> show/hide the small auto choice group only.
- `AutoTrainClick()` -> actual Train start.
- `AutoPkClick()` -> actual PK start.
- `AutoQuestClick()` -> actual Quest start.
- `AutoFuBenClick()` -> actual FuBen start.
- `AutoStopClick()` -> actual stop.
- `AutoSetingClick()` -> opens `GUI.CallUI("AutoFight")` settings UI.

So an internal tool should target the service/action, not try to emulate the visible click sequence.

## Train configuration

Built-in AUTOTRAIN settings include:

- `IsAttackMonsterInList`
- `AttackMonsterList`
- `IsLureModel`
- `IsTrainInRanger`
- `RangerScan`
- `AutoTrainSkillList`
- `UsingCombo`
- `UsingF1Key`
- `GiveUpMonsterOutRanger`.

Full serialization/defaults: `database/AUTO_SETTINGS_SCHEMA.md`.

## Target discovery

`AutoFight_Main:FindBestTarget()` uses `Game.GetNearbySpritesWithPredicate`.

The Auto code works with target fields/semantics including:

- dynamic object `Type`;
- `IsDeath`;
- `RoleID`;
- `ResID`;
- `Position`;
- reachability/range;
- configured monster whitelist;
- ignored/banded target state.

The `AutoTrainMonster` settings UI also uses `GetNearbySpritesWithPredicate` to list current monsters on the map.

## Attack flow

The engine uses semantic game actions such as:

- `Game.SelectTarget(RoleID)`;
- `Game.ChaseTarget(...)`;
- `Game.RequestUsingSkillWithTarget(...)`;
- `Game.RequestUsingSkillWithPos(...)`;
- `Game.ReloadTarget()`;
- `Game.IsSelectTargetDie()`;
- `Game.StopAutoPath()`.

It repeatedly re-evaluates target/range/state rather than treating one screen click as a combat session.

## Radius mode

If `IsTrainInRanger == true`, start logic calls:

`Game.AutoSetFlag(RangerScan)`.

The default radius is 500. The engine can abandon a target that exits the configured range when `GiveUpMonsterOutRanger` is enabled.

## Death integration

The same Auto service handles death through `DeathActive()`. With `AutoRevival` enabled it sends normal revive, closes the Revival UI and can return to the stored death/train position when `AutoComeback` is enabled.

See `features/AUTO_REVIVE.md`.

## Auto Sell integration

Recommended orchestration:

1. remember prior Auto mode + start map/position;
2. stop Train semantically (`StartAutoFight(None)`);
3. run sell state machine;
4. return via `Game.GoTo(savedMap, savedX, savedY)`;
5. verify map/position/player alive/not loading;
6. resume with `StartAutoFight(Train)`.

Do not leave Train's mutable combat coroutine competing with sell/NPC movement actions.

## Architecture

`read-only snapshot -> Train State Machine -> target selector -> Safety Guard -> max one action -> Unity main-thread dispatcher -> semantic Game/Lua action -> state proof -> next action`.

## What future AI should not do

- do not try to click the visible `Đánh quái` settings tab as the start command;
- do not press mouse/F1 if semantic start/skill actions are available;
- do not use stale UIButton instances;
- do not hardcode one monster memory offset when `GetNearbySpritesWithPredicate` exists;
- do not use fixed sleeps as success proof.
