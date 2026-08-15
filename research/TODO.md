# Research TODO — targeted follow-up after Phase 2

> General repository survey, asset decrypt, Config extraction, Interface/Lua extraction, core packet discovery, Auto Train semantics, sell request and revive semantics are DONE. **Không broad reverse lại client từ đầu.**

## DONE — Phase 1 architecture

- [x] Unity x64 + IL2CPP architecture.
- [x] metadata v39 and high-value IL2CPP APIs.
- [x] LuaSystemManager / SharedData / Game / GUI / Network bridges.
- [x] world/path/inventory/skill/buff symbol map.
- [x] `ClickNPC` high-level native flow.
- [x] `UIButton.HandleClickEvent` instance/stale-pointer hazard.
- [x] FG custom asset transform module.

## DONE — Phase 2 decrypted semantic data

- [x] Reproduce enough `FG_Decrypt` logic to restore bundles.
- [x] Decrypt/extract Config, Interface, Translations and shared UI bundles.
- [x] Extract 75 Config XML tables.
- [x] Extract 338 UI layout XML files.
- [x] Extract readable Lua source and catalog 339 Lua classes.
- [x] Extract 169 TCP packet constants.
- [x] Build full 1,003-NPC database + map links where available.
- [x] Build full 193-map database.
- [x] Build 165 portal edge database + 23 item destinations.
- [x] Build 19 FuBen scenario database.
- [x] Recover exact `CMD_NPC_SHOP_SELL_REQUEST` payload.
- [x] Recover exact revive/Đầu thai packet values.
- [x] Recover exact bag-sort and selected item-action payloads.
- [x] Recover dynamic `GameDialog.Selections` mechanism.
- [x] Identify exact built-in Auto Fight Train entry/state architecture.
- [x] Identify `Game.GetNPCPosition -> Game.GoTo -> GetNearestNPC` navigation pattern.

## P0 — NPC Trị liệu: targeted runtime proof only

Static reverse is already sufficient to define the mechanism. Remaining work is one runtime observation:

- [ ] Open intended healer NPC (for Lâu Lan candidate: NPC 339 Đỗ Thanh Đằng is verified in static DB).
- [ ] Capture current `GameDialogData.Selections` exactly as server sends it.
- [ ] Identify which visible selection corresponds to Trị liệu.
- [ ] Send actual `selectionID:-1` through `CMD_SHOW_GAMEDIALOG` or invoke equivalent Lua handler.
- [ ] Record whether a second MessageBox/selection is produced.
- [ ] Define state proof: HP restored, money changed if applicable, dialog closed/updated.
- [ ] Add the observed selection text/sequence to `features/AUTO_HEAL_NPC.md`; do **not** assume the numeric selection ID is globally stable unless repeated evidence proves it.

## P0 — External main-thread bridge proof

Lua/game action semantics are known; execution context is the remaining engineering risk.

- [ ] Prove a stable Unity/main-thread dispatcher usable by external tool.
- [ ] Verify one harmless semantic action end-to-end through dispatcher.
- [ ] Keep max one mutable action pending.
- [ ] Never invoke Unity/Lua gameplay action from arbitrary worker thread.

## P0 — Runtime entity schema when a feature needs it

- [ ] Resolve/invoke `LuaSystemSharedData.GetNearbySprites` read-only and record return object type.
- [ ] Map exact fields for Player: RoleID, Name, HP, MaxHP, MP, Position, Team/Faction/Combat/Target where present.
- [ ] Map exact fields for NPC/Monster/Pet/ItemPack objects.
- [ ] Map `GetBuffs/GetBuffData` return fields including duration/stack if exposed.

Do this incrementally; do not dump everything “just in case”.

## P1 — Expand machine-readable offline database

Core catalogs exist. Optional expansions useful for future AI/tool filtering:

- [ ] Export `Items` 5,238 rows to chunked CSV with ID/Name/price/sellable/throwable/bound/stack/type description.
- [ ] Export `Skills` 2,091 rows with ID/Name/faction/style/range/target/property/damage flag.
- [ ] Export `MagicAtrributes` 509 rows.
- [ ] Export `Monsters` 17,121 rows with ID/ResName/Name/level/type/MaxHP/AIID/skills and key combat stats.
- [ ] Export `Equips` 22,763 rows with ID/name/type/equip point/level/faction/star/sell price/buff.
- [ ] Export the 506 `AutoPath/NPC` transition edges if offline route debugging needs them.
- [ ] Optionally commit full Lua class→method and UI handler machine-readable catalogs.

## P1 — NPC service classification

- [ ] Build candidate tags from NPC name/ResName (`LangZhong*`, shop/vendor, blacksmith, warehouse, etc.).
- [ ] Treat tags as candidate inference, not service contract.
- [ ] Promote only after dialog/shop/runtime evidence.

## P1 — Auto Sell implementation validation

Exact sell packet is solved. Remaining implementation checks:

- [ ] Use `GetFreeBagSpace` as source of truth.
- [ ] Define user keep/sell whitelist policy.
- [ ] Choose ONE current instance -> send ONE sell -> wait inventory/shop change -> rescan.
- [ ] Verify shop open state from `CMD_NPC_SHOP_DATA` / `NPCShop`.
- [ ] Return via saved map/position and resume Train only after state proof.

## P2 — Static route planner (optional)

- [ ] Use portal graph to build offline map adjacency/navigation diagnostics.
- [ ] Model possible conditions/level restrictions separately.
- [ ] Keep runtime `Game.GoTo` as preferred executor unless a concrete reason requires custom routing.

## Architecture guardrails

`Resolver -> read-only Scanner -> Snapshot/State Store -> Observer -> State Machine -> Safety Guard -> Action Queue (max 1 mutable action) -> Unity/Main Thread Dispatcher -> Internal Action Engine`

Additional rules:
- response handlers are not requests;
- UI pointers are not reusable contracts across transitions;
- fixed delays are timeouts/fallbacks, never state proof;
- prefer semantic names/IDs over RVA;
- `ID` instance vs `ItemID` template vs `Position` slot must remain distinct;
- do not invent NPC coordinates when `GetNPCPosition` exists;
- do not invent a fixed treatment selection ID.
