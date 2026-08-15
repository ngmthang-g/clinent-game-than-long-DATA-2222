# Feature research — NPC Trị liệu / healing service

Status: **MECHANISM MOSTLY VERIFIED; exact runtime treatment selection still pending**.

## Static NPC identity

Frozen Config database verifies on Map `5` = Lâu Lan:
- NPC `337` = Đỗ Bất Đằng, `ResName=LangZhong1`
- NPC `338` = Đỗ Hoàng Đằng, `ResName=LangZhong1`
- **NPC `339` = Đỗ Thanh Đằng, `ResName=LangZhong1`**.

`LangZhong` is a strong physician/healer archetype inference. Exact service still needs the actual runtime dialog to promote NPC 339→Trị liệu from PROBABLE to VERIFIED.

Config also contains NPC `912` named `Tháp trị liệu`, `ResName=ZhiLiaoTa`; it is an explicit treatment archetype but has no static AutoPath MapID mapping in current data and is not automatically the normal city healer.

## Exact built-in helper for walking to and talking to NPC

Recovered `Global_Functions.lua` contains a documented function:

`GoToNPC(mapID, npcID)` — description: **“Tự tìm đường đến và đối thoại với NPC tương ứng”**.

Its implementation is semantically exact:

1. If current map differs: `Game.GoTo(mapID, -1, -1, callback)`.
2. `npcPos = Game.GetNPCPosition(npcID)`.
3. If nil → show `Không tìm thấy NPC tương ứng` and stop.
4. `Game.GoTo(mapID, npcPos.X, npcPos.Y, callback)`.
5. `Game.ClickNPC(npcID)`.

If already on the map it skips step 1 and performs steps 2→5.

This is even more direct than reconstructing movement + native button input manually. **Do not require the user to enter X/Y for Đỗ Thanh Đằng** if this helper/API path is available.

## Dynamic NPC dialog semantics

Generic NPC dialog uses `GameDialogData`.

Verified:
- `GameDialogData.Selections` maps runtime `selectionID -> visibleText`.
- generated selection button stores `selectionID` in its Tag.
- click submits `CMD_SHOW_GAMEDIALOG = 100007`.
- payload = `selectionID:SelectedItemID`.
- default SelectedItemID is `-1` when no item-award selection is needed.

No static Lua global constant like `TreatmentSelectionID` was found. Therefore hardcoding a guessed numeric “Trị liệu” selection ID is unsupported.

## Existing game precedent for text matching

`AutoFight_FuBen` already implements the desired pattern:
- get current `GameDialog`;
- enumerate `Selections`;
- lowercase selection visible text;
- compare with wanted semantic action text;
- send the **actual** `selectionID:-1` via `CMD_SHOW_GAMEDIALOG`.

So a treatment action should reuse this pattern rather than clicking screen coordinates.

## Recommended state machine for Lâu Lan

`CHECK_MAP -> GO_TO_NPC(5,339) -> WAIT_GAME_DIALOG -> ENUMERATE_SELECTIONS -> MATCH treatment/heal text -> SEND ACTUAL selectionID:-1 -> WAIT next dialog/MessageBox/server state -> if real confirm exists invoke semantic callback/selection -> VERIFY HP/money/dialog -> DONE`

## Verification still needed once at runtime

- exact visible text server returns for treatment on NPC 339;
- whether treatment is one selection or selection + confirmation;
- observable completion proof (HP restored, money changed if relevant, dialog update/close);
- whether numeric selection ID stays stable between openings. Do not assume it does.

## Stability rule

Do not use:
- hardcoded NPC X/Y;
- stale `UIButton*`;
- fixed `Sleep(500)` as proof;
- guessed treatment selection ID.

Prefer:
- `GoToNPC` / `GetNPCPosition` / `ClickNPC`;
- active `GameDialog.Selections`;
- state-driven progression;
- one mutable action at a time on the Unity/main-thread action path.
