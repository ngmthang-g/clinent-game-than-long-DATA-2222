# Context Pack — Build NPC Trị liệu

## Scope

Use for auto-walking to a healer NPC, opening NPC dialog, finding the actual Trị liệu option and confirming completion.

## REQUIRED reading

1. `AI_BOOTSTRAP.md`
2. `features/AUTO_HEAL_NPC.md`
3. `analysis/12_GLOBAL_LUA_HELPERS.md`
4. `analysis/11_EXACT_INTERNAL_ACTION_FLOWS.md`
5. `analysis/22_MAP_MINIMAP_RUNTIME.md`
6. `database/NPC_SERVICE_CANDIDATES.md`

## VERIFIED static facts

- Map `5` = Lâu Lan.
- NPC `339` = Đỗ Thanh Đằng, `ResName=LangZhong1`, Map 5.
- `GoToNPC(mapID,npcID)` uses semantic navigation: map routing -> `Game.GetNPCPosition` -> `Game.GoTo` -> `Game.ClickNPC`.
- NPC dialog uses runtime `GameDialogData.Selections` mapping `selectionID -> visibleText`.
- selection submit uses `CMD_SHOW_GAMEDIALOG = 100007` payload `selectionID:SelectedItemID`.

## Important limitation

No global static Trị liệu selection ID has been verified. The server/runtime dialog is the source of truth.

Do not hardcode a guessed numeric selection ID.

## Recommended state machine

`PRECHECK -> GO_TO_NPC -> WAIT_MAP_READY/POSITION -> CLICK_NPC -> WAIT_GAMEDIALOG -> ENUMERATE_SELECTIONS -> TEXT/SEMANTIC MATCH Trị liệu -> SEND actual selectionID:-1 -> HANDLE real follow-up dialog/confirmation if any -> VERIFY HP/money/dialog outcome -> DONE`.

## Matching rule

Prefer actual visible semantic text from the current dialog. The built-in FuBen/Quest automation already demonstrates text-to-current-selection matching and then submits the real selection ID.

## State proof

Use one or more of:

- HP restored/changed as expected;
- money changed if service costs money;
- dialog updated/closed in the expected sequence;
- server/game state explicitly reflects treatment completion.

A fixed delay after clicking is not proof.

## Remaining targeted runtime proof

Once on the live client, record:

- exact text for treatment on the intended NPC;
- current selectionID;
- whether there is a second confirmation;
- success state proof;
- whether selectionID is stable across repeated openings.

Keep the text/sequence in `features/AUTO_HEAL_NPC.md` after verification.

## Completion criteria

No hardcoded NPC X/Y, no stale UIButton pointer, no guessed Trị liệu ID, one semantic action at a time through the valid MainThread path, and state-driven completion.