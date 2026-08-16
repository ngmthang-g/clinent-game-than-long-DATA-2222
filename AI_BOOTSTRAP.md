# AI Bootstrap — read this first

This repository is intentionally large. **Do not read the entire repository before starting a task.**

## Primary scope

The primary purpose of this KB is **building a large Thần Long automation tool**, not documenting every subsystem in the client.

After this file, read `AUTO_TOOL_SCOPE.md`. Research unrelated to automation should be deferred unless a concrete auto feature depends on it.

The correct workflow is:

1. read this file;
2. read `AUTO_TOOL_SCOPE.md`;
3. read `AI_ROUTER.md`;
4. choose exactly one matching `contexts/BUILD_*.md` pack;
5. read only the REQUIRED documents named by that pack;
6. query databases only for the specific IDs/records needed;
7. open deeper analysis/raw evidence only when the context pack says it is necessary.

## Purpose

This repo is the canonical technical memory for one frozen Thần Long client snapshot. It exists so future AI/tool builders do not repeat broad reverse engineering that has already been done.

The KB preserves exact technical facts while deduplicating chat/research repetition. See `KB_METHOD.md` for evidence rules.

## Read-budget rule

For a normal implementation task, target **5–10 documents maximum before coding**. Do not preload all `analysis/`, all CSVs, all Lua, or all client files.

Large CSV/XML databases are lookup sources, not sequential reading material.

## Auto-value rule

Prioritize knowledge that helps the tool:

- observe runtime state;
- decide what to do;
- move/path/return to a spot;
- target/chase/cast;
- interact with NPC/UI semantically;
- sell/store/use/loot items safely;
- revive/heal/buff;
- coordinate party/multiple clients;
- verify success and avoid crashes/disconnects.

Normally defer cosmetics, rendering, voice, launcher internals, decorative resources, broad analytics and unrelated progression systems.

## Evidence levels

- `VERIFIED` — direct binary/metadata/decrypted asset/Lua/runtime evidence.
- `PROBABLE` — strong inference, not complete runtime proof.
- `HYPOTHESIS` — research direction only.
- `SOURCE-INSPECTED DONOR` — useful behavior/policy from older tool source; not automatically canonical runtime architecture.

Never silently upgrade a lower-confidence statement to VERIFIED.

## Canonical architecture

Production mutable actions should follow:

`Resolver -> read-only Scanner -> immutable Snapshot Store -> Observer -> State Machine -> Safety Guard -> Action Queue(max 1 mutable action) -> valid System.Action -> MainThread.Execute -> semantic Game/Lua/UI action -> state proof`

Read-only observers may run concurrently. Mutable actions may not.

## MainThread fact

`FGStudio.Engine.Utilities.MainThread` is statically solved:

- `.ctor()` creates `ConcurrentQueue<System.Action>`;
- `Execute(Action)` enqueues;
- Unity `Update()` calls `DoExecuteWorks()`;
- `DoExecuteWorks()` dequeues and invokes each `Action` on the Unity Update thread.

Game-owned `TCPGame` / `TCPLogin` producer handlers build legitimate `System.Action` delegates and pass them through `MainThread.Execute`.

Remaining implementation proof is external construction/rooting/lifetime of a valid Action plus one harmless live callback.

Required docs for this are routed through `contexts/BUILD_MAINTHREAD_BRIDGE.md`.

## High-value exact facts

- Train mode: `C_AutoModel.Train = 1`.
- Train start: `GUI.FindUI("AutoFight_Main"):StartAutoFight(C_AutoModel.Train)`.
- Nearby peaceful players: `Game.GetNearByPeacePlayers(limit)` -> RoleID, Name, Level, FactionID, HP, MaxHP, GuildName, AvartaID, TeamRank.
- Sell packet: `CMD_NPC_SHOP_SELL_REQUEST = 200036`.
- Sell payload: `itemInstanceID:NpcShopID:ShopID`.
- Revive packet: `CMD_REVIVE_DATA = 200063`; normal/Đầu thai=1, newbie=2, skill=3.
- GameDialog packet: `CMD_SHOW_GAMEDIALOG = 100007`; payload `selectionID:SelectedItemID`.
- Dynamic dialog truth: `Selections[selectionID] = visibleText`.
- Map 5 = Lâu Lan; NPC 339 = Đỗ Thanh Đằng, `LangZhong1`.
- Bag = item site 10; Storage pages = 11..15.
- `C_ItemAction.Move = 5`; move payload `5:itemInstanceID:destinationSite`.
- Skill 406 = Phật Quang Phổ Chiếu.
- Skill 407 = **Xung Hư Dưỡng Khí**.
- Skill 408 = Khởi Tử Hồi Sinh.
- Skill 423 = **Kim Châm Độ Kiếp**.
- Skill 424 = Thanh Tâm Phổ Thiện Chú.
- `Game.GetSkillCooldown(skillID)` exposes passed/cooldown ticks.
- Local `Game.GetBuffs()` exposes BuffID, DurationTick(ms), Stack.
- Static equipment weapon identity: `EquipPoint == 0`.

## Rules that prevent old mistakes

Do not:

- use `CreateRemoteThread`/continuous remote worker as the production gameplay-action engine;
- call Unity/Lua mutable actions directly from arbitrary worker threads;
- use stale `UIButton` pointers across UI transitions;
- treat the visible `Đánh quái` settings tab as the Train start action;
- use fixed sleeps as proof that an action succeeded;
- call response/update handlers as if they were request actions;
- identify a live item by template `ItemID` when the request needs instance `ID`;
- invent NPC coordinates when `Game.GetNPCPosition` exists;
- invent a fixed Trị liệu selection ID;
- OCR/CE scan information already exposed by semantic APIs;
- automatically solve/bypass Captcha.

## Database usage

Start database lookup from:

- `database/README.md`
- `database/FINDING_TO_DOC_MAP.md`
- `database/FACTS.jsonl` for atomic high-value facts.

Do not load all large static CSV chunks. Locate the needed ID/category first, then read the matching chunk.

## If a fact appears to conflict

Use this order:

1. `research/VERIFIED*.md`;
2. canonical subsystem analysis document;
3. Config/Lua/UI source-derived database;
4. older donor docs;
5. PROBABLE/HYPOTHESIS.

If conflict remains, do targeted verification and update the KB; do not broad-reverse the whole client.

## Mandatory next step

After reading this file, open `AUTO_TOOL_SCOPE.md`, then `AI_ROUTER.md`, and route the current automation task.