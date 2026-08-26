# AUTO PK — canonical tool feature route

Read `analysis/39_PK_AUTOPK_RUNTIME_STACK.md` first, then `database/static/skills/SKILL_TOOL_INDEX.csv` only for exact skill lookup.

Verified core: PK mode packet, AutoPK state machine, nearby-enemy target source, retaliation trigger, chase/cast semantic APIs. Important boundary: low-HP/faction target toggles exist in UI/config but shipped target resolver does not consume them.

Tool implementation must use current target state and explicit policy rather than pretending the unused shipped toggles already work.
