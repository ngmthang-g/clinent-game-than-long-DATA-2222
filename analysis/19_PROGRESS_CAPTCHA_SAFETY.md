# Progress lifecycle / Captcha safety state

Status: **VERIFIED from decrypted `TCPCmdEventHandler.lua`, `ProgressBar.lua`, `Captcha.lua`.**

This document is intentionally safety-oriented. Captcha is a user-verification gate and should be treated as a reason to pause automation and require user interaction, not something to bypass.

## Progress events

Exact event constants:

- `BeginProgress = 12`
- `InteruptProgress = 13`
- `UpdateProgressTime = 14`.

### BeginProgress

Event data is parsed as:

`duration:text`

The event handler:

1. destroys an existing `ProgressBar` if one exists;
2. calls `GUI.CallUI("ProgressBar", text, duration)`.

### InteruptProgress

Finds `ProgressBar` and destroys it.

### UpdateProgressTime

Data is:

`duration:lifeTimeTicks`

and existing UI receives:

`ProgressBar:UpdateProgressTime(duration, lifeTimeTicks)`.

## ProgressBar runtime schema

`ProgressBar` stores:

- `Duration`
- `LifeTime`.

Both are milliseconds according to source comments/logic.

Visual percentage:

`floor(LifeTime * 100 / Duration)`.

It auto-destroys after progress reaches duration.

## Automation relevance

Some game actions may have channel/progress state. A tool should not issue a conflicting movement/action simply because a fixed timeout elapsed.

Useful state logic:

```text
ProgressBar exists OR BeginProgress observed
    -> character/action is in a progress state
InteruptProgress
    -> progress aborted
ProgressBar reaches end/destroys + game state changed
    -> candidate completion proof
```

This complements `Game.IsProgress()` which the built-in Auto engine already checks before HP/MP recovery actions.

## Captcha event

Exact event constant:

`NewCaptcha = 57`.

Event data is parsed into:

- width
- height
- comma-separated answers
- image data (base64)
- question text.

The handler destroys an old Captcha UI if present and opens:

`GUI.CallUI("Captcha", width, height, answers, imgData, Question)`.

## Captcha UI behavior

`Captcha.lua`:

- displays the image and question;
- creates answer toggles from the server-provided answer list;
- stores selected answer in the toggle `Tag`;
- has a 60,000 ms countdown;
- manual submit calls `Game.SendAnswerCaptcha(Answer)` and closes UI.

## Required tool behavior

When `NewCaptcha` is observed or `GUI.FindUI("Captcha")` is non-nil:

1. **pause mutable automation actions**;
2. do not move, attack, sell, heal, revive-loop or spam requests through the captcha state unless a server-critical action must finish safely;
3. surface status to the user: `CAPTCHA / cần thao tác người dùng`;
4. allow the user to answer through the normal game UI;
5. resume only after Captcha UI disappears and normal game state is revalidated.

Do **not** implement OCR/AI solving, answer guessing or automatic captcha submission as part of this automation framework.

## Suggested Safety Guard priority

A sensible high-priority guard order is:

```text
CaptchaActive        -> PAUSE_USER_REQUIRED
Loading/MapTransition -> WAIT
Dead/Revival          -> REVIVE_STATE_MACHINE
ProgressActive        -> WAIT_OR_FEATURE_SPECIFIC
Normal                -> allow next queued action
```

This reduces diss/crash/action collisions and keeps verification gates user-controlled.
