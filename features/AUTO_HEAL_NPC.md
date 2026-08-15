# Feature research — NPC Trị liệu / healing service

Status: **PARTIALLY VERIFIED**.

Verified:
1. NPC identity/map data comes from decrypted Config.
2. Runtime navigation can use `Game.GetNPCPosition(npcID)`; fixed user-entered X/Y is not required.
3. Generic NPC dialogs use `GameDialogData`.
4. `GameDialogData.Selections` maps runtime `selectionID -> visible text`.
5. Selecting a dialog option sends `CMD_SHOW_GAMEDIALOG = 100007` with `selectionID:selectedItemID`.

Not yet verified: no static Lua source string provides a globally fixed “Trị liệu” selection ID. This is consistent with server-built NPC dialogs; hardcoding a guessed ID is unsupported.

Recommended flow:

`GO_TO_NPC -> GetNPCPosition -> GoTo -> interact nearest NPC -> wait GameDialog -> enumerate Selections -> match treatment/healing semantic text -> use actual selectionID -> send CMD_SHOW_GAMEDIALOG -> handle any real confirmation callback -> verify HP/money/dialog/server state -> DONE`.

This is more stable than `UIButton.HandleClickEvent` because the selection ID is the semantic server/game action while the UI button object is temporary presentation state.

Config contains NPC `912` named “Tháp trị liệu”, but that alone does not prove it is the intended city treatment NPC. Validate the desired NPC by actual game context/dialog.
