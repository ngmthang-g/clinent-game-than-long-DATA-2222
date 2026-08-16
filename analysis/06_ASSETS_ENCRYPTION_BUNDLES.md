# Asset Bundles / Config / Interface / FGClientTool — current evidence

> This document was originally written before the custom bundles were successfully decoded. It is now refreshed so future AI does **not** repeat the old assumption that Config/Interface contents are only predictions.

---

## 1. Why the asset branch matters alongside GameAssembly

`GameAssembly.dll + global-metadata.dat` give executable logic, runtime APIs and semantic type/member identity.

The asset branch gives the **data the logic consumes**:

- static IDs/templates/rules;
- maps/NPCs/items/equipment/skills/monsters/tasks/pets;
- Lua orchestration source;
- UI layouts/callback names;
- localization/resources.

For many future questions, decrypted Config/Interface is now a better first source than new native disassembly.

Preferred order:

```text
Lua / extracted Config / extracted UI
 -> runtime semantic API
 -> exact request/payload if needed
 -> native reverse only for an exact remaining gap
```

---

## 2. FGClientTool_Windows.dll — VERIFIED custom transform module

Native x64 FGStudio DLL.

Verified exports:

- `FG_Decrypt`
- `FG_Encrypt`
- `HelloWorld`.

`GameAssembly` references the encryption/decryption functions, so this is an active client component rather than an unused helper.

### Legacy head/tail transform family

Observed behavior includes bounded front/back byte-pair processing and a `0x0F` adjustment. The exact implementation is preserved by native analysis; this family was sufficient to explain one class of transformed bundle headers.

### Size-derived transform family

A second branch derives state from file size using:

```text
seed = file_size XOR 0x9E3779B9
```

then xorshift-style steps:

```text
x ^= x << 13
x ^= x >> 17
x ^= x << 5
```

The resulting state controls bounded front/back transforms/swaps.

### Bundle validation

The decrypt logic checks for valid Unity bundle signatures including:

- `UnityFS`
- `UnityRaw`
- `UnityWeb`.

This is best understood as custom obfuscation/header transformation, not strong modern cryptography.

---

## 3. Decrypt/extraction is already successful

Status: **VERIFIED by successful decode to valid UnityFS and semantic extraction.**

Decoded bundle/version evidence:

- `Config.unity3d` -> Unity `6000.3.7f1`
- `Interface.unity3d` -> Unity `6000.3.7f1`
- `Translations.unity3d` -> Unity `6000.3.7f1`
- `LoadingResources.unity3d` -> Unity `6000.3.4f1`
- `Logo.unity3d` -> Unity `6000.3.4f1`
- `Shared.unity3d` -> Unity `6000.3.4f1`
- `Shared_2.unity3d` -> Unity `6000.3.6f1`
- `data.unity3d` was already plain UnityFS `6000.3.6f1`.

Mixed 6000.3.x versions are not necessarily contradictory; separate bundles/resources may have been built/repacked with different minor editor/package builds.

---

## 4. `Config.unity3d` — VERIFIED semantic database source

Repo file size is about 1.36 MB.

It is no longer a predicted static-config candidate. Extraction recovered **75 named XML TextAssets**.

Important verified tables and direct row counts include:

| Table | Rows | Main value |
|---|---:|---|
| `Maps` | 193 | Map IDs/names/resources/type/server metadata |
| `NPCs` | 1,003 | NPC IDs/names/ResName/avatar |
| `AutoPath` | 1,618 | NPC associations, transitions, portals, item destinations |
| `Items` | 5,238 | template/price/sellable/stack/binding data |
| `Equips` | 22,763 | subtype, EquipPoint, level/faction/price/star/buff/attributes |
| `Skills` | 2,091 | target/range/faction/weapon/property/action semantics |
| `SkillProperties` | 2,044 | skill property definitions |
| `AutoSkills` | 300 | automatic trigger/value/cooldown/SkillIDs |
| `MagicAtrributes` | 509 | semantic effect-symbol dictionary |
| `Monsters` | 17,121 | monster identity/stats/AI/skills |
| `Tasks` | 516 | task type/rule/dialog/next/requirements |
| `GrowPoints` | 407 | gather/life-skill/quest targets |
| `Pets` | 8,349 | pet templates/growth/stats/skills |
| `Spirits` | 1,889 | spirit templates/model/skill capacity |
| `Factions` | 17 | books/F1/initial quick-skill relationships |
| `FuBenScenarios` | 19 | dungeon/scenario definitions |
| `Medicines` | 692 | medicine level/price/stack/sellability |
| `Gems` | 1,154 | gem templates/types/levels/prices |

Full 75-table catalog:

`database/CONFIG_TABLE_CATALOG.md`.

Domain-oriented navigation:

- `analysis/32_CONFIG_DOMAIN_ATLAS.md`
- `analysis/33_UNDEREXPLORED_HIGH_VALUE_CONFIG.md`.

### Static authority boundary

Config is authoritative for template/configured identity and relationships.

It is **not** the final authority for:

- whether an object is spawned now;
- live position;
- live item instance/site/slot;
- current cooldown/buff state;
- current server dialog selections;
- whether a request succeeded.

Those remain runtime/server-authoritative.

---

## 5. `Interface.unity3d` — VERIFIED Lua/UI semantic source

Repo file size is about 578 KB.

Extraction recovered:

- **338 UI layout XML TextAssets**;
- **1,469 UI handler bindings**;
- **339 Lua script classes with colon-method definitions**;
- global Lua infrastructure including `Global`, `Global_Constants`, `Global_Functions`, `Loader`, `Loader_Data`, `TCPPacketDefine`, `TCPCmdHandler`, `TCPCmdEventHandler`.

High-value scripts include:

- `AutoFight_Main`
- `AutoFight_FuBen`
- `AutoTrainMonster`
- `AutoHp`
- `Utilities`
- `Revival`
- `NPCShop_SellItemTab`
- `RoleInfo_BagTab`
- `BagItemsGrid`
- `GameDialog`
- team/task/pet/spirit scripts.

High-value layouts include:

- `Revival_Layout`
- `AutoFight_Layout`
- `AutoTrainMonster_Layout`
- `AutoHp_Layout`
- `Utilities_Layout`
- `NPCShop_Layout`
- `NPCShop_SellItemTab_Layout`
- `RoleInfo_BagTab_Layout`
- `MessageBox_Layout`
- `GameDialog_Layout`.

Canonical indexes:

- `database/LUA_SCRIPT_CATALOG.md`
- `database/UI_LAYOUT_CALLBACKS.md`
- `database/PACKET_IDS.csv`
- `analysis/09_PHASE2_DECRYPTED_DATA_LUA.md`.

### Why Interface is especially valuable

Lua frequently contains the exact human-readable flow that native reverse would otherwise have to reconstruct:

```text
visible button/layout
 -> Lua handler
 -> semantic Game/GUI call or exact SendPacket
 -> runtime state update
```

Examples already solved this way include revive, NPC shop sell, bag actions, dynamic GameDialog, Auto Train and task/FuBen behavior.

---

## 6. `Translations.unity3d`

Repo file size is about 1.83 MB.

**Verified:** custom transform was successfully decoded to valid UnityFS `6000.3.7f1`.

**Not yet canonicalized:** a compact localization key/value database has not been committed to the KB.

Potential high-value uses:

- alternate localized wording for NPC/service dialog matching;
- UI text lookup;
- names/descriptions where Config references localization keys rather than direct text.

Do not invent its exact internal schema before extracting/indexing the relevant TextAssets.

Current research hypothesis/target is documented in `research/HYPOTHESES.md`.

---

## 7. `data.unity3d`

Repo file size: ~47.6 MB.

**Verified:** plain `UnityFS`, Unity `6000.3.6f1`.

Potential value:

- serialized resources/prefabs;
- map/scene support data;
- model/resource references;
- possibly path/grid/obstruction assets.

However, the current KB already has most high-level gameplay semantics from Config/Interface/GameAssembly. Therefore `data.unity3d` should be **targeted-only**, not blindly extracted because it is large.

Best future workflow if needed:

```text
inventory asset names/types first
 -> identify relevant serialized objects
 -> extract only those
 -> commit semantic indexes/results
```

---

## 8. Shared Interface bundles

Decoded successfully:

- `LoadingResources.unity3d`
- `Logo.unity3d`
- `Shared.unity3d`
- `Shared_2.unity3d`.

Likely value is mostly shared prefabs/materials/loading/visual resources.

They are lower priority than the already-readable Interface Lua/layout layer. Open them only when a concrete prefab/resource question cannot be answered from semantic text.

---

## 9. Standard extraction pipeline — historical/reference

The successful conceptual pipeline is:

```text
raw bundle
 -> detect plain UnityFS/UnityRaw/UnityWeb
 -> if transformed: reproduce FG_Decrypt-compatible transform
 -> validate Unity bundle header/version/block table
 -> parse/decompress UnityFS
 -> enumerate serialized files/CAB objects
 -> export TextAsset/MonoBehaviour/layout/resource data
 -> normalize semantic IDs/fields into database/docs
```

The important long-term artifact is not merely the decrypt code. It is the **normalized semantic knowledge committed to GitHub**, so future AI does not need to run the extraction again.

---

## 10. Direct text/config files around the bundles

### `app.info`

Verified:

```text
FGStudio
Thần Long  Mobile
```

### `boot.config`

Observed:

- graphics jobs enabled;
- threading mode 6;
- native-debugger wait disabled;
- HDR disabled;
- GC max time slice 3;
- build GUID.

### `Version.xml`

Observed:

- application `VerCode=125`;
- FGStudio CDN/service endpoints;
- account/server/log/voice services;
- realtime voice enabled with LiveKit backend.

### root `Manifest.xml`

Observed:

- `LauncherVersion=4`
- `GameVersion=126`
- `GameExeName="Thần Long  Mobile.exe"`.

`VerCode=125` and launcher `GameVersion=126` appear to be different versioning layers; do not force them into one semantic meaning without more evidence.

---

## 11. Current asset-research priorities

Do **not** redo Config/Interface decrypt/extraction.

Highest-value remaining asset work is only:

1. normalize/index more already-extracted Config domains (`Skills/SkillProperties/AutoSkills`, `Items/Equips/Medicines`, `Tasks/GrowPoints`, `Pets/Spirits`);
2. extract/index Translations when localization becomes useful;
3. inspect `data.unity3d` only for a concrete missing scene/path/resource question;
4. inspect shared UI bundles only for a concrete prefab/resource gap;
5. reopen FGClientTool only if a real future bundle fails the known transform variants.

This keeps the KB focused on reusable semantic data rather than repeatedly reverse-engineering container formats.
