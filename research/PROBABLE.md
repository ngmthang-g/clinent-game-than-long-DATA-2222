# PROBABLE findings — only unresolved high-confidence conclusions

> Many earlier predictions were promoted by Phase 2/3 evidence. This file now keeps **only conclusions that remain strongly supported but not fully runtime/end-to-end VERIFIED**.

Do not duplicate facts already in `VERIFIED*.md`.

---

## 1. `LuaSystemSharedData` can serve as the primary external semantic world-scan layer

**Confidence: VERY HIGH**

VERIFIED foundation:

- nearby/world/item/team queries exist;
- shipped UI/Auto code actually consumes several of them;
- nearby peaceful-player and enemy schemas are already VERIFIED for the fields read by UI.

Still not fully VERIFIED:

- exact live return type/schema for **every** SharedData query;
- all Player/NPC/Monster/Pet/ItemPack fields an external scanner may want;
- whether every query is safe/useful from the chosen external runtime bridge path.

Prediction:

A production scanner can rely primarily on semantic query/data APIs and copy values into immutable external snapshots, avoiding broad heap/offset scanning.

Canonical sources:

- `database/API_QUICK_REFERENCE.md`
- `analysis/14_NEARBY_ENTITY_UI_SCHEMA.md`
- `analysis/22_MAP_MINIMAP_RUNTIME.md`.

---

## 2. Nearby actor records expose more useful state than the UI currently consumes

**Confidence: HIGH**

Already VERIFIED for nearby peaceful players:

`RoleID, Name, Level, FactionID, HP, MaxHP, GuildName, AvartaID, TeamRank`.

Selected target additionally proves richer type/vitals/social state exists elsewhere in the runtime model.

Likely additional nearby/world-object state that may be accessible through the same or related objects:

- MP/MaxMP or percentages;
- TeamID / GuildID / combat/PK/death/moving state;
- exact position/range object;
- current target/chase state;
- richer buff state.

Do not invent field offsets or claim these are present on every nearby-player record until the actual return object is inspected.

---

## 3. `LangZhong1/2` is a strong offline healer-service candidate classifier

**Confidence: HIGH**

VERIFIED evidence:

- multiple medicine/doctor-like NPC names use `ResName=LangZhong1/2`;
- Lâu Lan NPCs 337/338/339 use `LangZhong1`;
- NPC 339 = Đỗ Thanh Đằng, Map 5 Lâu Lan;
- Config also contains NPC 912 `Tháp trị liệu`, `ResName=ZhiLiaoTa`.

Prediction:

`ResName` family + visible name can be used to generate **candidate healer/service tags** for lookup/ranking.

Not yet VERIFIED:

- every `LangZhong*` NPC exposes identical treatment service;
- exact active GameDialog text/selection ID for each server/map/state.

Static archetype is not a service contract.

---

## 4. NPC Trị liệu should be robustly selected by semantic text from the active `GameDialog.Selections`

**Confidence: VERY HIGH**

VERIFIED foundation:

- dialog selections are runtime/server-driven: `Selections[selectionID] = visibleText`;
- built-in FuBen code already text-matches visible selection names and submits the **actual** selectionID;
- there is no verified universal static treatment selection constant.

Prediction:

Treatment can be implemented reliably as:

```text
open intended healer NPC
 -> wait actual GameDialog
 -> normalize visible selection text
 -> match Trị liệu / server-equivalent text
 -> submit actual current selectionID
 -> prove HP/money/dialog outcome
```

Still requires live proof on the intended healer and any second confirmation dialog.

---

## 5. Non-team Auto Buff can reuse the nearby peaceful-player source plus semantic skill actions

**Confidence: HIGH**

VERIFIED foundation:

- nearby peaceful player HP/MaxHP/RoleID/faction/guild are exposed without party membership;
- stock UI can `Game.SelectTarget(RoleID)`;
- skill identity/cooldown/use semantics are known;
- team-heal donor shows chase/range/target-skill flow.

Prediction:

A support controller can filter arbitrary nearby peaceful players and cast beneficial skills without requiring party membership.

Still requires targeted runtime proof for:

- server acceptance rules of each beneficial skill on non-team targets;
- exact range/peace/relationship restrictions;
- whether target buff state needed by policy is available beyond display icons without intrusive target switching.

---

## 6. Static portal graph is useful as an offline coarse-route/diagnostic planner

**Confidence: MEDIUM-HIGH**

VERIFIED foundation:

- 165 portal edges contain From/To map + coordinates;
- 506 NPC-mediated transitions and 23 item destinations are also extracted;
- runtime `Game.GoTo` already abstracts route execution.

Prediction:

The static graph can support:

- map adjacency queries;
- route diagnostics;
- fallback planning;
- explaining why a requested destination may require intermediate maps.

Caveat:

Level/quest/event/state restrictions may invalidate a static edge at runtime. `Game.GoTo` remains the preferred executor.

---

## 7. Name/`ResName` can classify several NPC service archetypes offline

**Confidence: MEDIUM-HIGH**

Examples of semantic-looking families observed in Config include doctor/healer, blacksmith, merchant/hotel/tailor/fisher-like archetypes.

Prediction:

An offline service-candidate index can dramatically narrow which NPCs to runtime-probe for:

- treatment;
- vendor/shop;
- blacksmith/repair;
- storage;
- other city services.

Do not promote a candidate to VERIFIED service until dialog/shop/runtime evidence confirms it.

---

## 8. External use of the built-in AutoFight engine should be substantially more stable through the solved MainThread queue than arbitrary-thread invocation

**Confidence: HIGH**

VERIFIED foundation:

- AutoFight semantic Lua flow is known;
- `MainThread.Execute(Action)` queue/Update/invoke chain is solved;
- legitimate managed Action construction ABI is documented.

Prediction:

Once the final live external Action construction/lifetime proof passes, invoking AutoFight/Lua semantic actions through the game-owned dispatcher should avoid a major class of arbitrary-thread re-entrancy/crash failures.

Still not runtime VERIFIED end-to-end from the external bridge.

---

## 9. A detailed combat telemetry/recorder layer is probably possible from structured events

**Confidence: MEDIUM-HIGH**

VERIFIED vocabulary includes structured skill damage/heal, object death, buff and target/world events.

Prediction:

Enough runtime event data likely exists to record:

- attacker/target identities;
- skill identity;
- damage/heal amounts;
- death timing;
- buff lifecycle;
- possibly combat efficiency per target/spot.

Still unknown:

- exact payload schema for all relevant events;
- crit/block/elemental details;
- reliable loot/XP linkage.

Use targeted Lua/event-handler tracing before claiming a complete recorder schema.

---

# Rule

If new direct evidence resolves one of the above, move the exact fact into the appropriate `VERIFIED` ledger and shrink/remove the corresponding PROBABLE item. Do not leave stale uncertainty after a question has been solved.
