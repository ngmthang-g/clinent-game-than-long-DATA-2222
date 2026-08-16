# v0.9.0 cross-map Confirm detector donor — detection concept only

Status: **SOURCE/BINARY-INSPECTED DONOR** from user-supplied `ThanLongAutoTrain_v0.9.0_monster_panel_v5.zip` on 2026-08-16.

This document preserves only the **read-only detection idea** that made old automatic cross-map Confirm reliable. It is **not** an instruction to copy v0.9.0's action engine, worker/thread model, UI pointer model, or full state machine.

## User runtime evidence

User reports:

- manual Confirm TEST in current CleanRoute works;
- recent automatic cross-map Confirm does not reliably click at the correct moment;
- the supplied v0.9.0 tool recognized when a map Confirm was required much better.

This proves the saved click coordinate is not the only issue. The missing/weak part is **state recognition**.

## Artifact boundary

The supplied ZIP contains compiled x64 PE artifacts, not C++ source:

- `ThanLongAutoTrain_v0.9.0.exe`
- `ThanLongRefactorProbeBridge.dll`

Therefore findings below are binary/source-inspection evidence, not a verbatim source transplant.

## High-value detector findings

The controller binary contains explicit orchestration states including:

- `CheckingMap`
- `WaitingPathStopAtTrain`
- `WaitingConfirm`
- `WaitingMapTransition`
- `StoppingPath`
- `WaitingPathStop`
- action label `ConfirmDialog`.

More importantly, it contains a dedicated **Confirm UI scanner** and distinguishes two independent facts:

1. scanner is **authoritative**;
2. target Confirm UI **exists**.

Observed diagnostic strings include:

- `Confirm UI scanner chưa authoritative`
- `Confirm UI chưa tồn tại`
- `UI scanner chưa authoritative; không được suy đoán dialog đang đóng`
- `Không tạo được bộ nhận diện hộp xác nhận trong game`
- `Mất phản hồi bộ nhận diện hộp xác nhận`
- `Mất phản hồi trạng thái chuyển map`.

This means old v0.9.0 did **not** treat `AutoPath stopped + elapsed time` as sufficient proof that a Confirm dialog existed.

## Binary evidence for UI presence lookup

The detector setup resolves IL2CPP/runtime metadata around:

- `Assembly-CSharp`
- namespace `FGStudio.LuaSystem.Base`
- namespace `FGStudio.LuaSystem.GUI`
- classes `UIObject`, `UIButton`, `UIToggle`
- static field `instances`
- literal UI name `MessageBox`.

The artifact therefore had a real read-only UI-presence observation path for MessageBox, rather than only a timer heuristic.

## What should NOT be copied

Do not copy v0.9.0 wholesale.

The old binary also contains legacy/unsafe mechanisms and architecture that conflict with the current production direction. In particular, do not revive:

- continuous `CreateRemoteThread` gameplay workers;
- arbitrary-thread Unity/Lua mutation;
- stale native UIButton pointers;
- old complete action/orchestration code merely because one detector worked;
- fixed Sleeps as proof of success.

Only preserve the detection invariant:

> **No automatic Confirm click unless a read-only UI observer is authoritative and the real Confirm UI is present.**

## Preferred current implementation

Current decrypted/verified client knowledge exposes a cleaner semantic observer surface:

`FGStudio.LuaSystem.API.LuaSystemAPI_GUI.FindUI("MessageBox")`

with `MainFindUI` as a possible same-semantic fallback.

Recommended production snapshot fields:

```text
ValidConfirmUi
confirmUiVisible
```

Recommended cross-map gate:

```text
cross-map route was started by tool
AND route actually showed AutoPath/movement evidence
AND AutoPath is no longer actively travelling
AND Confirm UI observer is authoritative
AND FindUI("MessageBox") != null
=> use the already user-tested Confirm coordinate click
```

If the detector is not authoritative:

```text
DO NOT CLICK
wait / log detector unavailable
```

If MessageBox is absent:

```text
DO NOT CLICK
continue waiting for real UI state
```

After click:

```text
wait MessageBox to disappear
then wait actual map transition / MapID change / IsMapReady proof
```

Retry may use time only as a debounce/timeout guard, **never as evidence that the dialog exists**.

## Why semantic `FindUI` is preferred over copying `UIObject.instances`

Verified current client knowledge already provides:

- `LuaSystemAPI_GUI.FindUI`
- `MainFindUI`
- MessageBox lifecycle semantics
- `Game.IsMapReady()` and map transition state.

Therefore the new tool can preserve the v0.9.0 detector's good invariant without transplanting its lower-level scanner implementation.

## Evidence status

**CONFIRMED**
- v0.9.0 has separate WaitingConfirm/WaitingMapTransition orchestration states.
- v0.9.0 contains an authoritative/existence distinction for Confirm UI scanning.
- v0.9.0 resolves UIObject/UIButton/UIToggle/instances and literal `MessageBox` in the relevant detector area.
- current client knowledge exposes semantic `LuaSystemAPI_GUI.FindUI`/`MainFindUI`.

**LIKELY**
- the old tool's better runtime behavior was materially helped by waiting for real MessageBox presence instead of timing-only portal inference.

**UNKNOWN until user runtime test**
- whether current CleanRoute `FindUI("MessageBox")` observer alone is sufficient for every cross-map portal/dialog case.

## Do-not-break rule

For future Confirm changes, keep the detector separate from the click engine:

`Observer proof -> state machine decision -> existing click action -> map/UI proof`

Do not collapse it back into:

`portal stall -> Sleep -> blind Confirm click`.
