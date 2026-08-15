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
4. cross-linked from `AI_INDEX.md`;
5. labelled by evidence strength.

Therefore a later AI should get **more usable information than a verbatim transcript**, while exact constants/semantics remain preserved.

## Evidence labels

- **VERIFIED** — direct binary/metadata/decrypted asset/Lua/runtime evidence.
- **PROBABLE** — strong evidence/inference, not fully end-to-end runtime proven.
- **HYPOTHESIS** — a proposed direction to test.
- **FAILED/DEPRECATED** — a path known to be fragile/wrong/obsolete.

A prediction is never silently promoted to VERIFIED.

## How discoveries move into the KB

For every meaningful discovery:

`raw evidence -> interpretation -> subsystem document -> database/feature document -> VERIFIED/PROBABLE ledger -> AI_INDEX cross-link`

Large static tables are normalized into machine-readable CSVs when this saves future AI from reparsing XML/bundles.

## Why this is better than storing only chat

A chat transcript mixes:

- correct findings;
- temporary guesses;
- corrections discovered later;
- repeated explanations;
- user-specific troubleshooting context.

The KB resolves those conflicts. Example: a legacy Lua variable named `KIMCHAMDOKIEP` points to skill 407, but Config/UI cross-check proves 407 is Xung Hư Dưỡng Khí and actual Kim Châm Độ Kiếp is 423. The KB records the corrected truth and also records the misleading legacy name so future AI does not repeat the mistake.

## Rule for future AI

If the KB already answers the question at VERIFIED level, do not broad-reverse the client again. Reopen binary/Lua/runtime evidence only when:

- exact detail is missing;
- two documents conflict;
- a runtime-only/server-dynamic value is required;
- implementation needs an execution-context proof that static analysis cannot provide.
