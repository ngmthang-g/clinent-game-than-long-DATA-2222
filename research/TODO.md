# Research TODO — targeted follow-up only

> General repository/client survey is DONE. Do not restart a broad reverse-engineering pass. Only do targeted work needed by a concrete feature.

## DONE — architecture baseline

- [x] Identify Unity x64 + IL2CPP architecture.
- [x] Identify metadata version 39.
- [x] Inventory important native/support modules.
- [x] Map high-value Lua namespaces/classes.
- [x] Identify SharedData nearby-world query layer.
- [x] Identify `GScene` / PathFinder / map-data symbols.
- [x] Identify inventory/item semantic APIs.
- [x] Identify skill/buff semantic APIs.
- [x] Identify high-level Lua GUI APIs.
- [x] Identify Lua network send bridge.
- [x] Disassemble/understand `ClickNPC` at high level.
- [x] Establish `UIButton.HandleClickEvent` instance/stale-pointer hazard.
- [x] Identify custom FG asset encrypt/decrypt module.
- [x] Classify support DLLs and launcher/host.
- [x] Create VERIFIED/PROBABLE/HYPOTHESES knowledge ledgers.

## P0 — Exact runtime schema when needed

Do not do all of these “just in case”. Perform when a feature needs exact fields.

- [ ] Resolve/invoke `LuaSystemSharedData.GetNearbySprites` read-only and dump return object type.
- [ ] Resolve `GetNearbyObjects` / `GetLocalMapObjects` return types.
- [ ] Map exact Player/Role data fields: RoleID, Name, HP, MaxHP, MP, Position, Team/Faction/Combat/Target if present.
- [ ] Map exact `NPCData`, `MonsterData`, `PortalData` fields.
- [ ] Map exact `GetBuffs`/`GetBuffData` return types and duration/stack fields.

## P0 — UI/action traces required for unfinished automation

### Treatment / heal NPC

- [ ] Manual trace: `ClickNPC` -> NPC UI -> Trị liệu -> confirm.
- [ ] Capture `MainCallUI/CallUI` uiName + args.
- [ ] Capture `SendPacket` packetID/payload if action sends network request.
- [ ] Record expected response/state proof.

### Sell one item

- [ ] Manual trace: NPC -> shop -> sell mode -> sell exactly one item.
- [ ] Capture Lua UI callback/action.
- [ ] Capture packetID/payload.
- [ ] Correlate `RemoveItem/UpdateItemsList/UpdateMoney/TraderState` response.
- [ ] Document one-item replay sequence.

### Auto -> Đánh quái

- [ ] Manual trace exact UI selection.
- [ ] Check whether `EnableAutoF1`, `RangerAuto`, auto flags/radius state change.
- [ ] Identify action/state change that actually selects combat mode.

### Revive / Đầu thai

- [ ] Trace dead-state UI creation.
- [ ] Identify exact Lua callback and/or `CMD_REVIVE` request path.
- [ ] Verify loading/spawn completion conditions.

## P1 — Asset extraction

- [ ] Port exact `FG_Decrypt` into an offline extractor.
- [ ] Decrypt/extract `Config.unity3d`.
- [ ] Build NPC/map/item/skill tables from extracted config.
- [ ] Decrypt/extract `Interface.unity3d` and shared UI bundles.
- [ ] Search extracted UI/Lua content for shop/treatment/revive/auto callback names.
- [ ] Commit semantic outputs under `database/`; do not make future AI decrypt again.

## P1 — Auto Sell implementation research

- [ ] Confirm numeric `ItemType` / `EquipType` enum values or avoid numeric hardcode via metadata.
- [ ] Define whitelist/keep policy.
- [ ] Implement `GetFreeBagSpace` source-of-truth.
- [ ] Select one sell candidate -> send action -> wait server update -> rescan.
- [ ] Never rely on saved slot list after mutation.

## P1 — Entity/combat scanner

- [ ] Classify SharedData outputs into Player/NPC/Monster/Pet/Object.
- [ ] Verify alive/dead/current target state.
- [ ] Verify distance/position mapping.
- [ ] Build read-only snapshot store per process.

## P2 — Offline map/navigation

- [ ] Inspect `PathFinder` / `NodeGrid` only if route planning requires it.
- [ ] Determine whether static grid/obstruction/portal data can be exported offline.
- [ ] Build Map -> NPC -> Portal DB if config provides reliable coordinates.

## P2 — Launcher/session layer

Only if needed for multi-client orchestration:

- [ ] Decompile .NET Launcher control service.
- [ ] Determine semantics of sync group/master/record-playback.
- [ ] Keep each game process runtime pointer/state isolated.

## Architecture guardrails

- Resolver -> read-only Scanner -> Snapshot/State Store -> Observer -> State Machine -> Safety Guard -> Action Queue (max one mutable action) -> Unity/Main Thread Dispatcher -> Internal Action Engine.
- Do not use response handlers as requests.
- Do not use stale UI pointers across state transitions.
- Fixed delays are timeouts/fallbacks, not state proof.
- Prefer semantic identifiers to hardcoded RVA.

## Completion rule

When a TODO is solved, update the relevant `analysis/` or `database/` file and move only properly evidenced conclusions into `VERIFIED.md`. Do not leave important discoveries buried only in chat/logs.
