# Feature specification — Auto Revive / Đầu thai

Status: **VERIFIED action semantics**.

Packet: `CMD_REVIVE_DATA = 200063`.

Revive types:
- Normal / “Đầu thai” = `1`
- Tân thủ = `2`
- Hồi sinh bằng kỹ năng = `3`

`Revival_Layout` maps these visible buttons to exact Lua handlers.

Recommended state machine:

`ALIVE -> detect Revival/death -> choose revival type -> send one CMD_REVIVE_DATA -> wait for Revival close/map/player spawned -> optional return to saved location -> resume prior mode only when ready`.

`AutoFight_Main:DeathActive()` already implements normal auto revive. For Train/PK it sends normal revive, closes Revival and can `Game.GoTo` the stored death location.

Do not click “Đầu thai” by screen coordinate and do not call a stale `UIButton.HandleClickEvent`. Use the semantic action on the Unity/main-thread path.
