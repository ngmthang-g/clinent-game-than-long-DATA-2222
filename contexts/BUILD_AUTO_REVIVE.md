# Context Pack — Build Auto Revive / Đầu thai

## Scope

Use for death detection, Revival lifecycle, exact revive action, return-to-position and safe resume of prior mode.

## REQUIRED reading

1. `AI_BOOTSTRAP.md`
2. `features/AUTO_REVIVE.md`
3. `analysis/11_EXACT_INTERNAL_ACTION_FLOWS.md`
4. `database/UI_PACKET_LIFECYCLE.md`
5. `analysis/19_PROGRESS_CAPTCHA_SAFETY.md`
6. `analysis/22_MAP_MINIMAP_RUNTIME.md`

## VERIFIED action

Packet:

`CMD_REVIVE_DATA = 200063`

Values:

- normal / Đầu thai = `1`
- newbie = `2`
- skill revive = `3`.

Revival runtime data also exposes countdown/option availability fields such as `TimeLeft`, `IsEnableReviveNewbie`, `IsEnableBySkill`.

## Recommended state machine

`ALIVE -> DEATH_DETECTED -> CAPTURE_RETURN_POINT/PREVIOUS_MODE -> WAIT/READ_REVIVAL_STATE -> SEND ONE configured revive action -> WAIT Revival clear + local alive + map ready -> RETURN(optional) -> VERIFY position/map -> RESUME prior feature`.

## State proof

Do not mark revive successful because the packet was sent.

Require:

- local role no longer dead;
- Revival lifecycle/UI cleared or server state confirms completion;
- expected map ready;
- valid current position.

Only resume Train/Buff after these proofs.

## Priority

Revival should preempt normal Train/Buff/Sell planning, except explicit user-verification/Captcha pause and fatal bridge errors.

## Do not regress to

- clicking the visible Đầu thai button by screen coordinates;
- stale `UIButton.HandleClickEvent` pointers;
- sending revive repeatedly every frame;
- fixed post-revive sleep as success proof.

## Completion criteria

One revive request per death lifecycle, event/state-driven proof, safe optional return to saved location, and deterministic resume of the prior mode only when the character/map are ready.