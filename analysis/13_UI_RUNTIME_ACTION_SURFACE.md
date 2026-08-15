# UI runtime / semantic action surface — Phase 3

Status: **VERIFIED from decrypted Interface layout XML + Lua source**, except where explicitly marked.

## Why this matters

The UI layer is not just presentation. It exposes a semantic control surface over gameplay through named Lua methods, `GUI.FindUI/CallUI`, `Game.*` APIs and `Network.SendPacket`.

For automation, the stable model is usually:

`find semantic service/UI -> invoke its Lua method or underlying Game/Network action -> observe packet/UI/game state`

not:

`screen coordinate -> mouse click -> fixed sleep -> next coordinate`.

## Extracted UI corpus

From the decrypted `Interface.unity3d` snapshot:

- 338 UI layout XML TextAssets;
- 1,469 event-handler bindings in those layouts;
- 347 Lua source files in the extracted script set;
- regex catalog currently identifies ~3,068 `Class:Method(...)` Lua methods;
- ~749 direct `GUI.CallUI/MainCallUI/FindUI/MainFindUI/ShowMessageBox/ShowNotification` call sites;
- ~497 `Network.SendPacket(...)` send sites;
- ~1,223 direct `Game.<method>(...)` call sites.

The counts above are catalog/parser counts for this frozen snapshot, not an engine ABI guarantee.

## Layout XML binds UI events directly to Lua method names

The FGStudio UIMaker layout XML stores properties such as:

- `ClickHandler`
- `SelectHandler`
- `ValueChangeHandler` / `ValueChangedHandler`
- hover/pointer handlers

Example from `AutoFight_Layout`:

- visible toggle text `Đánh quái`;
- element `ToggleAutoMonsterTab`;
- `SelectHandler = ToggleTabHeaderSelected`.

The corresponding Lua class `AutoFight` implements `AutoFight:ToggleTabHeaderSelected(uiToggle)` and switches which settings tab is visible.

A source/layout cross-check shows the large majority of handler bindings resolve to methods with the same semantic class name. A minority are stale/legacy/mismatched bindings, so **handler existence must be checked before invoking it**.

## Critical distinction: settings UI vs actual action

The `AutoFight` window is primarily a settings editor. The actual Auto Train start path is elsewhere.

`TopIcon:AutoTrainClick()` does exactly:

1. `GUI.FindUI("AutoFight_Main")`;
2. `AutoFight_Main:StartAutoFight(C_AutoModel.Train)`;
3. `TopIcon:ShowAutoStatus(C_AutoModel.Train)`.

Therefore the historical problem “mở AUTO được nhưng không chọn được Đánh quái” does **not** need a second physical click on the tab.

Preferred semantic entry points:

- Train: `AutoFight_Main:StartAutoFight(C_AutoModel.Train)` where `Train = 1`;
- PK: `StartAutoFight(C_AutoModel.PK)`;
- Quest: `StartAutoFight(C_AutoModel.Quest)`;
- FuBen: `StartAutoFight(C_AutoModel.FuBen)`;
- Stop: `StartAutoFight(C_AutoModel.None)`.

`TopIcon:AutoTrainClick/AutoPkClick/AutoQuestClick/AutoFuBenClick/AutoStopClick` are UI-level wrappers around the same service.

## `TopIcon` exact auto menu behavior

- `AutoFightClick()` only toggles visibility of `AutoFightGroup`.
- `AutoSetingClick()` opens settings with `GUI.CallUI("AutoFight")`.
- `AutoTrainClick()` starts Train mode.
- `AutoStopClick()` stops current auto by passing `None`.

This explains why manipulating the visible AUTO menu is a weaker approach than calling the semantic service directly.

## `AutoFight_Main` is a long-lived service component

It is not merely a button callback container. It owns:

- current auto mode;
- auto settings;
- Train/PK/Quest/FuBen coroutines;
- target selection;
- HP/MP recovery;
- Nga My healing/revive support;
- auto buffs;
- pet logic;
- loot logic;
- death/revive/comeback logic;
- NPC/monster navigation;
- active GameDialog data for quest/FuBen automation.

`GF_AutoFightMain()` simply returns `GUI.FindUI("AutoFight_Main")`, which confirms the game itself treats this UI/script as a service locator.

## Packet-driven UI lifecycle is a strong state-proof source

Important inbound handlers in `TCPCmdHandler.lua`:

### Revive

`CMD_REVIVE_DATA`:

- `GUI.FindUI("Revival")`;
- if server says close -> destroy existing UI;
- if already open -> `UpdateData(revivalData)`;
- if server says open -> `GUI.CallUI("Revival", revivalData)`;
- then finds `AutoFight_Main` and calls `DeathActive()`.

So death/revival state can be synchronized to the actual server-driven UI lifecycle.

### NPC Shop

`CMD_NPC_SHOP_DATA`:

- `GUI.FindUI("NPCShop")`;
- if absent -> `GUI.CallUI("NPCShop", shopData)`;
- otherwise -> `NPCShop:RefreshData(shopData)`.

This is a much stronger shop-open proof than waiting N milliseconds after NPC interaction.

### GameDialog

`CMD_SHOW_GAMEDIALOG`:

- destroys an existing `GameDialog`;
- `data == "NULL"` means dialog close/no new UI;
- passes dialog data to `AutoFight_Main:PutGameDialog(data)` when service exists;
- creates the new UI via `GUI.CallUI("GameDialog", data)`.

This is the correct synchronization point for NPC service flows such as Trị liệu.

## MessageBox semantics

`MessageBox.lua` stores `OKCallback` and `CancelCallback` provided at initialization.

`ButtonOKClicked()`:

1. destroys the MessageBox;
2. returns if callback is nil;
3. otherwise executes the stored OK callback.

`ButtonCancelClicked()` follows the same pattern for cancellation.

Implication: if a flow creates a MessageBox with a callback, the semantic action is the callback path. Do not cache a native UIButton pointer across transitions.

## GameDialog semantics

`GameDialog:InitializeComponents(gameDialogData)` dynamically clones buttons from `gameDialogData.Selections`.

For each selection:

- visible text = `selectionName`;
- button `Tag = selectionID`.

`GameDialog:FunctionButtonClicked(uiButton)` sends:

`CMD_SHOW_GAMEDIALOG` with `selectionID:SelectedItemID`.

Therefore the dialog's semantic action ID is server/runtime data, not the temporary button object's address.

## UI state should be read, not guessed

Recommended observer hierarchy for an automation action:

1. exact server/event data if available;
2. `GUI.FindUI("SemanticUIName")` and script state;
3. game object/state (`Game.RoleData`, `Game.SelectedTarget`, inventory, map etc.);
4. timeout only as a guard, never as success proof.

## Known layout/source mismatch warning

Not every handler string present in XML has a same-class Lua method in this snapshot. Examples appear in some Auto settings layouts and older hover/toggle bindings.

Possible reasons:

- legacy layout residue;
- handler supplied by a base/shared class;
- event is no longer functionally required because state is read directly on save;
- source/layout version drift inside the client package.

Rule: **check the Lua method before treating a layout handler name as callable API.**

## Best search order for future UI work

1. layout XML: find visible element + handler name;
2. same-name Lua class/method;
3. inspect `GUI.CallUI/FindUI` lifecycle;
4. inspect `Network.SendPacket` and `Game.*` calls inside that method;
5. inspect `TCPCmdHandler/TCPCmdEventHandler` for response/state proof;
6. native `UIButton.HandleClickEvent` only if no semantic route exists.
