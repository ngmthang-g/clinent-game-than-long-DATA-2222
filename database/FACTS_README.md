# Atomic Facts Database

`FACTS.jsonl` is a compact machine-readable index of high-value conclusions.

It is **not** a replacement for the canonical analysis documents. It exists so AI/tooling can locate exact constants/IDs/contracts without loading long Markdown files first.

## Format

One JSON object per line.

Common fields:

- `id` — stable fact identifier;
- `subsystem` — routing category;
- `status` — VERIFIED / PROBABLE / PENDING_RUNTIME_PROOF etc.;
- `fact` — compact technical statement;
- exact structured fields where useful, such as `packet_id`, `payload`, `skill_id`, `npc_id`, `map_id`, `rows`;
- `source` — canonical document containing the full evidence/context.

## Recommended use

1. Search/filter `FACTS.jsonl` by subsystem, ID, packet number, SkillID, NPCID or keyword.
2. If the fact directly answers a lookup question, use it while preserving its status.
3. For implementation or ambiguous semantics, open the `source` document before coding.
4. Never infer that the absence of a fact means the client lacks that capability.

## Examples

Search concepts:

- `mainthread`
- `packet_id:200036`
- `skill_id:424`
- `npc_id:339`
- `subsystem:auto_train`
- `EquipPoint == 0`

## Maintenance rule

Add only durable, high-value atomic facts. Do not dump every sentence from Markdown into JSONL.

When a fact is corrected:

- update the JSONL line;
- update the canonical source document;
- preserve any important legacy/misleading name as a caveat so future AI does not repeat the old error.