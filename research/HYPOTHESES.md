# HYPOTHESES — unresolved research questions only

> This file intentionally stores directions that still need evidence. Several older hypotheses were removed because Phase 2/3 already solved them (Config tables exist, Interface contains Lua, Tasks exist, buff duration/stack exists, etc.).

Do not promote any item below without new evidence.

---

## H1 — Player / Monster / NPC / Pet share a meaningful common runtime actor hierarchy

Evidence:

- generic nearby sprite/object queries;
- GScene loads multiple object types;
- common add/remove/death/movement lifecycle concepts;
- target APIs handle several actor types.

Hypothesis:

There is either a common base class/data hierarchy or a stable shared data shape across major world actor types.

Best targeted test:

- inspect actual runtime classes returned by `GetNearbySprites/GetNearbyObjects` for player/NPC/monster/pet samples;
- compare inherited methods/fields rather than guessing offsets.

Potential value:

One generic external snapshot model could cover multiple actor families.

---

## H2 — Nearby-player/world records expose richer combat/social state than current UI fields

Known nearby peaceful-player fields are already VERIFIED.

Hypothesis:

The same object or adjacent runtime data may expose more of:

- MP/MaxMP;
- TeamID/GuildID;
- position/vector;
- death/combat/PK/moving flags;
- target/chase state;
- richer buff references.

Targeted test:

Inspect the real returned class and only add fields proven by metadata/runtime reads.

---

## H3 — `CMD_CLIENT_LUA` carries server/client Lua-specific payloads useful to one or more gameplay systems

Evidence:

- exact packet constant exists;
- Lua system has explicit network bridge/event plumbing.

Unknown:

- direction;
- call sites;
- payload schema;
- whether it is gameplay-critical or only infrastructure.

Do not send/test arbitrary payloads. Trace legitimate Lua call sites first.

---

## H4 — Built-in AutoFight has additional reusable center/radius/return-to-origin state beyond what is already documented

Evidence:

- radius/lure settings in `AutoTrainMonster`;
- `DrawCicleAutoFight` / auto/ranger-related APIs;
- built-in Train engine has target/range policy.

Hypothesis:

There may be reusable internal state for:

- train center;
- allowed radius;
- return-to-center behavior;
- leash/lure policy;
- saved previous state.

Targeted method:

Read the exact Lua fields/settings/state transitions before doing native reverse.

---

## H5 — Detailed navigable path/grid data can be extracted offline from asset data

Evidence:

- `PathFinder`, `NodeGrid`, region/obstruction/safe-area classes exist;
- maps/portal routes are known;
- `data.unity3d` is a large plain UnityFS asset bundle.

Hypothesis:

Per-map graph/grid/obstruction data may be serializable into an offline route/diagnostic DB.

Unknown:

- which bundle/object stores it;
- format/size;
- whether it is useful enough to beat runtime `Game.GoTo`.

Only investigate if runtime pathing becomes a real blocker.

---

## H6 — Launcher sync / record-playback uses a reusable high-level process/input orchestration channel

Evidence:

Launcher symbols/strings indicate sync master/group and recording/playback concepts.

Unknown:

- raw keyboard/mouse mirroring vs high-level commands;
- local service/protocol details;
- usefulness to the gameplay tool architecture.

Low priority. Do not pursue unless a concrete multi-client synchronization feature requires it.

---

## H7 — `SyncBootstrap.AutoInit` may initialize launcher/client synchronization or another shared control channel

The method name and runtime-initialize entry are VERIFIED; its purpose is not.

Hypothesis only.

Targeted test if ever needed:

- metadata/native inspect this method and direct callees;
- correlate with launcher service behavior.

Low priority for gameplay semantic research.

---

## H8 — Structured combat events are sufficient for a detailed combat recorder

Evidence:

Command/event vocabulary includes skill damage/heal, object death and buff lifecycle.

Hypothesis:

Inbound event payloads may permit a recorder with attacker/target/skill/value/timing and perhaps crit/elemental data.

Targeted test:

Trace legitimate `TCPCmdHandler/TCPCmdEventHandler` branches for those exact commands and map field names.

---

## H9 — UI object identity changes across open/close/rebuild transitions and explains stale `UIButton*` failures

Known:

`UIButton.HandleClickEvent` is an instance method and dereferences object state.

Hypothesis:

Specific UI panels destroy/reinstantiate/rebind button objects during transitions, making a cached object pointer stale even if the semantic panel/button name is unchanged.

Best proof:

Log managed object identity/instance pointer across repeated open-close cycles of one panel.

Architectural rule remains valid regardless: resolve semantic UI/action at time of use; do not cache long-lived button pointers.

---

## H10 — Some asset families use additional FG transform/decrypt variants not yet needed by current extracted bundles

Known:

The current custom transform was understood sufficiently to decode Config/Interface/Translations/shared bundles.

Hypothesis:

Other future/optional bundles may select different transform branches based on header/size/version.

Do not research pre-emptively. Only revisit `FGClientTool_Windows.dll` if a concrete bundle fails the existing decode path.

---

## H11 — `Translations.unity3d` can provide a compact localization key/value database useful for semantic text matching

Known:

- bundle was successfully decoded to valid UnityFS;
- current KB does not yet contain a normalized localization table.

Hypothesis:

It can improve:

- alternate wording matching for NPC dialog/service text;
- UI label lookup;
- Vietnamese/localized name resolution.

Targeted work:

Extract TextAssets/string tables and preserve key -> language/value mapping if present.

---

## H12 — `data.unity3d` contains high-value serialized scene/resource data not duplicated in Config/Interface

Known:

- plain UnityFS ~47.6 MB;
- Unity version 6000.3.6f1.

Hypothesis:

It may contain serialized prefabs, map/resource references, scene-support data or other objects useful for model/path/world analysis.

Because it is large, do not broad-extract it without a concrete missing question. Prefer indexed asset inventory first.

---

# Removed because already solved

The following old hypotheses are **no longer hypotheses**:

- Config contains NPC/item/map/skill/task/etc. semantic tables -> VERIFIED, 75 tables extracted.
- Interface contains exact Lua/UI logic -> VERIFIED, 339 Lua classes + 338 layouts + 1,469 bindings.
- nearby peaceful player HP/MaxHP is available semantically -> VERIFIED.
- buff DurationTick/Stack exists -> VERIFIED.
- task database exists in Config -> VERIFIED (`Tasks`, 516 rows).
- ground-loot semantic ItemPack engine exists -> VERIFIED.

Future AI must not resurrect these as uncertainty.
