# Knowledge-base method — how chat/reverse findings are preserved

This repository is not a verbatim chat transcript. It is a **structured technical memory** of the frozen Thần Long client.

## What is preserved exactly

When evidence provides an exact technical fact, the knowledge base preserves it exactly, including where applicable:

- class/namespace/method names;
- packet IDs;
- numeric enum/action values;
- packet payload formats;
- field/property names;
- NPC/Map/Item/Skill IDs and names;
- Lua function names and call order;
- state/event names;
- confirmed source-file/layout names;
- important caveats and failure modes.

Examples that must not be paraphrased into a different meaning:

- `CMD_NPC_SHOP_SELL_REQUEST = 200036`
- sell payload `itemInstanceID:NpcShopID:ShopID`
- `CMD_REVIVE_DATA = 200063`
- normal/Đầu thai=`1`, newbie=`2`, skill revive=`3`
- `C_AutoModel.Train = 1`
- `Game.GetNearByPeacePlayers(...)`
- `Game.GetNPCPosition -> Game.GoTo -> Game.ClickNPC`
- `Game.GetSkillCooldown(skillID)` returns passed/cooldown ticks
- SkillID 407 is **Xung Hư Dưỡng Khí**, while actual **Kim Châm Độ Kiếp is 423** in the frozen Config.

## What is intentionally NOT copied verbatim

Chat repetition, exploratory dead ends, casual wording and repeated explanations are not duplicated line-for-line. Instead they are:

1. deduplicated;
2. grouped by subsystem;
3. rewritten into stable technical language;
4. cross-linked;
5. labelled by evidence strength.

Therefore a later AI should get **more usable information than a verbatim transcript**, while exact constants/semantics remain preserved.

## Evidence labels

- **VERIFIED** — direct binary/metadata/decrypted asset/Lua/runtime evidence.
- **PROBABLE** — strong evidence/inference, not fully end-to-end runtime proven.
- **HYPOTHESIS** — a proposed direction to test.
- **FAILED/DEPRECATED** — a path known to be fragile/wrong/obsolete.
- **SOURCE-INSPECTED DONOR** — useful behavior/UX/state policy observed in older tool source; not automatically canonical runtime truth for the new architecture.

A prediction is never silently promoted to VERIFIED.

## How discoveries move into the KB

For every meaningful discovery:

`raw evidence -> interpretation -> subsystem document -> database/feature document -> VERIFIED/PROBABLE ledger -> routing/index cross-link`

Large static tables are normalized into machine-readable CSVs when this saves future AI from reparsing XML/bundles.

## Layered AI reading strategy

The repo may become very large. The solution is **routing**, not deleting knowledge and not forcing AI to preload everything.

Normal path:

`AI_BOOTSTRAP.md -> AI_ROUTER.md -> one contexts/BUILD_*.md -> required subsystem docs -> specific database lookup`.

A normal implementation task should aim to read roughly **5–10 relevant documents before coding**, not the entire repository.

### Layer 0 — bootstrap

`AI_BOOTSTRAP.md` contains only critical architecture/fact guardrails.

### Layer 1 — router/context packs

`AI_ROUTER.md` maps the current task to a compact context pack under `contexts/`.

Context packs specify REQUIRED vs OPTIONAL reading, known contracts, unknowns, forbidden regressions and completion proof.

### Layer 2 — deep subsystem analysis

`analysis/*.md` contains the detailed technical evidence and reasoning. Read only the documents routed for the current task.

### Layer 3 — machine-readable databases

Large CSV/JSONL files are lookup sources. Query a specific record/chunk; do not sequentially load everything.

### Layer 4 — raw/client evidence

Original binaries, extracted source and raw evidence are reopened only for a missing/conflicting detail or targeted runtime/native proof.

## Atomic facts

`database/FACTS.jsonl` stores selected high-value conclusions as one JSON object per line.

Its role is fast retrieval of exact IDs/constants/contracts such as packet IDs, SkillIDs, NPC IDs and MainThread facts.

Each atomic fact points back to a canonical `source` document. `FACTS.jsonl` is an index, not a replacement for evidence documents.

Do not dump every sentence into the atomic database; only durable facts worth retrieving independently belong there.

## Why this is better than storing only chat

A chat transcript mixes:

- correct findings;
- temporary guesses;
- corrections discovered later;
- repeated explanations;
- user-specific troubleshooting context.

The KB resolves those conflicts. Example: a legacy Lua variable named `KIMCHAMDOKIEP` points to skill 407, but Config/UI cross-check proves 407 is Xung Hư Dưỡng Khí and actual Kim Châm Độ Kiếp is 423. The KB records the corrected truth and also records the misleading legacy name so future AI does not repeat the mistake.

## Maintenance rule

When a major new fact is discovered:

1. update the canonical subsystem analysis/feature document;
2. update VERIFIED/PROBABLE ledger as appropriate;
3. add/update an atomic `FACTS.jsonl` entry if the fact is important for lookup;
4. update `database/FINDING_TO_DOC_MAP.md` if it materially improves retrieval;
5. update the relevant context pack if the discovery changes implementation guidance;
6. update `AI_BOOTSTRAP.md` only if the fact is foundational enough that most tasks must know it.

This prevents every file from becoming a duplicate of every other file.

## Rule for future AI

If the KB already answers the question at VERIFIED level, do not broad-reverse the client again. Reopen binary/Lua/runtime evidence only when:

- exact detail is missing;
- two documents conflict;
- a runtime-only/server-dynamic value is required;
- implementation needs an execution-context proof that static analysis cannot provide.

And before reading deeply: route the task through `AI_BOOTSTRAP.md` and `AI_ROUTER.md`.