# Bản đồ nghiên cứu client Thần Long — current canonical map

> Đây là bản đồ cấp cao của **frozen client snapshot**. Future AI không được dùng file này như lý do để đọc toàn repo. Bình thường hãy bắt đầu bằng `AI_BOOTSTRAP.md` -> `AI_ROUTER.md` hoặc `database/SUBSYSTEM_SOURCE_MAP.md`.

---

# 1. Kết luận kiến trúc lớn

Client là game **Unity Windows x64 + IL2CPP**.

- gameplay C# đã compile native vào `Game/GameAssembly.dll`;
- semantic type/method/field/assembly metadata nằm trong `global-metadata.dat` version 39;
- game còn có một lớp **Lua runtime** rất lớn cho UI/gameplay orchestration;
- `Config.unity3d` chứa static semantic databases;
- `Interface.unity3d` chứa readable Lua + UI layout/callback data;
- runtime có structured Game/SharedData APIs cho world/player/item/skill/buff/map/team/pet/task/loot;
- mutable work có game-owned `MainThread.Execute(System.Action)` dispatcher.

Vì vậy không nên nhìn client như một đống pointer/offset. Kiến trúc knowledge/tool phù hợp là:

```text
Offline semantic DB
 + runtime semantic scanner
 + immutable snapshots/events
 + state machine
 + validated main-thread semantic actions
```

---

# 2. Những nguồn tri thức đã được khai thác sâu

## Tier S — canonical semantic sources

### `Game/GameAssembly.dll`

**Status:** broad architecture/native semantic reverse DONE; chỉ targeted reverse khi exact contract còn thiếu.

Recovered value:

- Assembly-CSharp gameplay native code;
- Lua bridge / Game / GUI / Network API;
- world/path/item/skill/buff symbols;
- IL2CPP exports;
- exact MainThread dispatcher chain;
- targeted action/constructor ABI evidence.

Do not broad-scan it again for every feature.

### `global-metadata.dat`

**Status:** structural/semantic mapping DONE enough for current KB.

Verified:

- metadata v39;
- ~16,080 type definitions;
- 96 images/assemblies;
- large method/field/parameter tables;
- semantic names/tokens usable with GameAssembly.

### `Config.unity3d`

**Status: VERIFIED DECRYPTED + EXTRACTED.**

This is no longer an “ứng viên mạnh”. It produced **75 XML TextAssets**.

High-value tables include:

- Maps 193
- NPCs 1,003
- AutoPath 1,618
- Items 5,238
- Equips 22,763
- Skills 2,091
- SkillProperties 2,044
- AutoSkills 300
- MagicAtrributes 509
- Monsters 17,121
- Tasks 516
- GrowPoints 407
- Pets 8,349
- Spirits 1,889
- Factions 17
- FuBenScenarios 19
- plus guild/equipment/activity/cosmetic/model tables.

Use:

- `database/CONFIG_TABLE_CATALOG.md`
- `analysis/32_CONFIG_DOMAIN_ATLAS.md`
- `analysis/33_UNDEREXPLORED_HIGH_VALUE_CONFIG.md`.

Do not decrypt/reparse this bundle again for a question already answered by those DB/docs.

### `Interface.unity3d`

**Status: VERIFIED DECRYPTED + EXTRACTED.**

Recovered:

- **338 UI layout XML TextAssets**;
- **1,469 handler bindings**;
- **339 Lua script classes with colon-method definitions**;
- global Lua infrastructure such as `Global_Constants`, `Global_Functions`, `TCPPacketDefine`, `TCPCmdHandler`, `TCPCmdEventHandler`;
- high-value scripts including AutoFight, AutoHp, Utilities, Revival, Bag, NPCShop, GameDialog, Team, Task, Pet/Spirit.

This changed the preferred research order for UI/gameplay features to:

`layout/Lua -> runtime semantic API -> exact packet/action -> native only if still missing`.

### `FGClientTool_Windows.dll`

**Status:** decrypt role sufficiently solved for successful extraction.

Verified exports:

- `FG_Encrypt`
- `FG_Decrypt`
- `HelloWorld`.

Its major value was decoding custom bundles. Reopen only if a concrete bundle fails the known transform path.

---

# 3. Important sources that remain targeted-only

## `data.unity3d`

Plain UnityFS ~47.6 MB, Unity `6000.3.6f1`.

Potentially valuable for serialized resources/prefabs/map/path/world assets, but **do not broad-extract without a missing concrete question**.

Priority now: medium-high only for asset/world/path gaps.

## `Translations.unity3d`

Successfully decoded to valid UnityFS according to Phase 2 evidence, but a compact canonical localization DB has not yet been created.

Potential value:

- localized text/key mapping;
- robust semantic dialog matching;
- UI display-name lookup.

Target when language/text matching becomes a blocker.

## Interface shared bundles

`LoadingResources`, `Logo`, `Shared`, `Shared_2` were decoded to valid UnityFS.

Use only for prefab/resource-specific questions that Lua/layout text cannot answer.

## `UnityPlayer.dll`

Engine-level source: PlayerLoop, Unity object lifecycle, AssetBundle, Transform/GameObject/render/input internals.

Do not reverse it for normal game feature semantics.

## `lib_burst_generated.dll`

Target only when a proven call path enters a Burst job that matters.

## Launcher / Host

Separate .NET launcher/update/session layer. Do not mix with frozen gameplay client research unless a specific launcher/session question is asked.

---

# 4. Core runtime semantic layers already VERIFIED

## Nearby players / entities

Shipped UI proves:

`Game.GetNearByPeacePlayers(limit)` ->

- RoleID
- Name
- Level
- FactionID
- HP
- MaxHP
- GuildName
- AvartaID
- TeamRank.

Nearby enemy UI exposes the same core schema.

`Game.SelectedTarget` gives richer target-specific identity/vitals/type/social state.

Consequence:

Do not return to broad CE scanning for nearby player HP/MaxHP/name/RoleID/faction/guild.

## Map / movement / world

Verified semantic APIs include:

- `Game.IsMapReady()`
- `GetLocalMapObjects()`
- `GetNearbyObjects()`
- `GetCurrentMoveDestination()`
- `MoveTo`
- `MoveToEx`
- `GoTo`
- `HasPath`
- `GetNPCPosition`
- `ClickNPC`
- `ClickToObject`.

## Inventory

Verified semantic APIs include:

- `GetItemsAtSite`
- `GetItemData`
- `GetItemTemplateData`
- `GetFreeBagSpace`
- `GetItemType`
- `GetEquipType`
- `IsItemSellable`
- price/stack/star/level/gem helpers.

Identity rule:

`ID = live instance` != `ItemID = template` != `Position = slot` != `Site = container`.

## Skill / buff

Verified:

- `Game.UseSkill(skillID)` semantic use;
- `GetSkillCooldown(skillID)` returns passed/cooldown ticks;
- `GetBuffs()` -> BuffID/DurationTick/Stack;
- `GetBuffData`, `GetBuffProperties`, `HasBuff`;
- team-heal donor uses range/chase/target skill semantics.

## Team

Verified structured `C_TeamData` + action constants/payloads + Follow engine.

## Task

`Tasks.xml` exists with 516 rows, and built-in Auto Quest uses structured task semantics.

## Pet / Spirit

Runtime state/action donor is documented; static Config also provides thousands of Pet/Spirit templates.

## Ground loot

Built-in engine already uses semantic ItemPack queries/path/interact/pickup. No OCR needed.

---

# 5. Exact action/protocol breakthroughs

## Auto Train

`C_AutoModel.Train = 1`

Start:

`GUI.FindUI("AutoFight_Main"):StartAutoFight(C_AutoModel.Train)`.

Visible `Đánh quái` tab is configuration, not the actual start action.

## NPC shop sell

`CMD_NPC_SHOP_SELL_REQUEST = 200036`

Payload:

`itemInstanceID:NpcShopID:ShopID`.

## Revive / Đầu thai

`CMD_REVIVE_DATA = 200063`

- normal/Đầu thai = 1
- newbie = 2
- skill revive = 3.

## Dynamic GameDialog

`CMD_SHOW_GAMEDIALOG = 100007`

`Selections[selectionID] = visibleText`

submit:

`selectionID:SelectedItemID`.

Treatment selection must come from the active server dialog; do not invent a global ID.

## Storage move

`CMD_ITEM_ACTION = 100005`

Move action = 5

payload:

`5:itemInstanceID:destinationSite`.

## MainThread

Frozen exact architecture:

`MainThread.Execute(Action) -> ConcurrentQueue<Action> -> Update -> DoExecuteWorks -> Action.Invoke`.

Dispatcher implementation is VERIFIED; only a live external producer proof remains if building the action bridge.

---

# 6. Static data should now be treated as domains, not one giant database

Read `analysis/32_CONFIG_DOMAIN_ATLAS.md`.

Important groups:

### World/routing

Maps, WorldMap, NPCs, AutoPath, FuBenScenarios, Monsters, GrowPoints.

### Combat/skills

Skills, SkillProperties, AutoSkills, MagicAtrributes, Books, Factions.

### Inventory/equipment/economy

Items, Equips, Medicines, Gems, EquipSets, EquipEnhance, EquipIdentifyValues, EquipExtendedAttributes.

### Pet/Spirit

Pets, PetFeatures, PetEquips, PetEquipSets, Spirits, SpiritFeatures.

### Task/progression

Tasks, GuildTask, Activities, DailyActivityAward, RoleReputes, RoleTitles.

### Cosmetics/resources

Character models/appearance/FX/audio and related low-priority tables.

This domain map is specifically designed so AI can select only the needed rows/tables.

---

# 7. Current highest-value knowledge work

Broad binary reverse is no longer the main goal.

Priorities:

1. **Skills semantic stack**
   - Skills
   - SkillProperties
   - AutoSkills
   - Factions
   - Books.

2. **Inventory/equipment policy stack**
   - Items
   - Equips
   - Medicines
   - equipment support tables.

3. **Tasks/gather/activity stack**
   - Tasks
   - GrowPoints
   - GuildTask
   - Activities.

4. **Pet/Spirit template stack**
   - Pets
   - PetFeatures
   - PetEquips
   - Spirits.

5. Localization database from `Translations.unity3d` when semantic text matching needs it.

6. `data.unity3d` asset inventory only when a concrete missing world/path/resource question justifies the cost.

Exact extraction schemas/preservation rules: `analysis/33_UNDEREXPLORED_HIGH_VALUE_CONFIG.md`.

---

# 8. Remaining runtime-only proof questions

These cannot be solved purely by more static prose:

- actual Trị liệu selection on a live healer dialog + any confirmation/outcome;
- server acceptance rules for beneficial skills on non-team peaceful players;
- exact extra fields of runtime actor objects beyond already-verified UI schema;
- final external managed Action bridge proof if/when implementation work resumes.

These must stay targeted; they do **not** justify re-reversing the whole client.

---

# 9. AI reading strategy

For a question like “Auto Sell”:

```text
AI_BOOTSTRAP
 -> AI_ROUTER / SUBSYSTEM_SOURCE_MAP
 -> Auto Sell context/feature doc
 -> Bag/shop runtime doc
 -> exact item records only if needed
```

For “skill X does what?”:

```text
SUBSYSTEM_SOURCE_MAP
 -> Skills index/record
 -> SkillProperties
 -> MagicAtrributes if property symbols need interpretation
 -> runtime APIs only if asking whether the current character can cast it now
```

For “NPC X ở đâu/làm gì?”:

```text
NPC database
 -> map association/service candidate
 -> runtime GetNPCPosition for live coordinates
 -> active GameDialog/shop data for actual service contract
```

The repo is a library, not a book that must be read front-to-back.

---

# 10. Evidence hygiene

Two rules remain critical:

1. symbol/packet/table existence does not automatically prove direction/payload/runtime service behavior;
2. server/update handlers are evidence of state changes, not automatically request actions.

Use:

- `research/VERIFIED*.md` for solved facts;
- `research/PROBABLE.md` for strong remaining inferences;
- `research/HYPOTHESES.md` for unresolved research questions.

Stale uncertainty must be removed when later phases prove the answer.
