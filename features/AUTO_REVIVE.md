# Feature specification — Auto Revive / Đầu thai

Status: **VERIFIED action semantics + server-driven Revival state schema**.

## Exact packet/action

Packet:

`CMD_REVIVE_DATA = 200063`.

Revive types:

- Normal / “Đầu thai” = `1`
- Tân thủ = `2`
- Hồi sinh bằng kỹ năng = `3`.

Exact Lua handlers:

- `ButtonNewbieReviveClicked()` -> payload `"2"`
- `ButtonSkillReviveClicked()` -> payload `"3"`
- `ButtonGoToInfernalClicked()` -> payload `"1"`.

Do not click the visible button by coordinate when the semantic packet action is known.

## Revival server data used by UI

`Revival:UpdateData(data)` directly consumes:

- `data.TimeLeft`
- `data.IsEnableReviveNewbie`
- `data.IsEnableBySkill`.

The inbound `CMD_REVIVE_DATA` handler also consumes an `Action` state to open/update/close the Revival UI.

Therefore availability of newbie/skill revive does not need to be guessed from button color; it exists as structured server-driven state.

## Automatic normal revive countdown

`Revival:DoCountDown()` initializes from:

`CurrentReviveData.TimeLeft`

and decrements by 1000 ms each second.

When `timeLeft < 0`, the stock UI automatically calls:

`ButtonGoToInfernalClicked()`

which sends Normal/Đầu thai type `1`.

This means “Đầu thai” is not only a button; it is also the game's automatic fallback after the server-provided countdown expires.

## Server-driven UI lifecycle

Inbound `CMD_REVIVE_DATA` behavior:

1. `GUI.FindUI("Revival")`;
2. close action -> destroy existing UI;
3. active existing UI -> `UpdateData(revivalData)`;
4. open action when absent -> `GUI.CallUI("Revival", revivalData)`;
5. find `AutoFight_Main` and call `DeathActive()`.

So a robust tool can use actual Revival lifecycle as state proof instead of merely checking HP==0 then sleeping.

## Built-in Auto integration

`AutoFight_Main:DeathActive()` already implements auto-revive behavior.

For Train/PK, when configured:

- use normal revive;
- close Revival through its auto path;
- optionally use `Game.GoTo` to return to the stored death/train position (`AutoComeback`).

This is a known-good donor architecture.

## Recommended state machine

```text
ALIVE
 -> death/server Revival Open
 -> capture prior auto mode + desired return position
 -> inspect allowed revive options / policy
 -> send ONE CMD_REVIVE_DATA
 -> WAIT Revival close
 -> WAIT local player alive/spawned
 -> WAIT loading/map transition finished
 -> optional Game.GoTo(saved map/position)
 -> verify map/position
 -> resume prior auto mode
```

## Choice policy

If the tool's desired policy is specifically **Đầu thai**:

- send type `1` once after Revival state is valid.

If supporting other options:

- only use Tân thủ type `2` when `IsEnableReviveNewbie == true`;
- only use Skill revive type `3` when `IsEnableBySkill == true`.

Do not repeatedly send an unavailable revive type.

## Safety guards

- Captcha active -> user-required pause takes priority.
- Do not send revive before valid dead/Revival state.
- Do not resume train just because the Revival window disappeared; also verify local player/spawn/map state.
- Do not reuse a `UIButton.HandleClickEvent` pointer from the old Revival UI after it closes/reopens.
- fixed timeouts are failure guards, not state proof.
