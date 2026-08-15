# Context Pack — Build Auto Train

## Scope

Use for Đánh quái/Train start-stop, target selection, chase/range, combat skills, loot and return-to-spot behavior.

## REQUIRED reading

1. `AI_BOOTSTRAP.md`
2. `analysis/10_BUILTIN_AUTO_FIGHT_ENGINE.md`
3. `features/AUTO_TRAIN.md`
4. `analysis/18_SKILLBAR_COOLDOWN_QUICKSKILLS.md`
5. `analysis/22_MAP_MINIMAP_RUNTIME.md`
6. `analysis/19_PROGRESS_CAPTCHA_SAFETY.md`

## OPTIONAL

- Loot: `analysis/27_LOOT_PICKUP_FILTER_ENGINE.md`
- Quest-driven combat: `analysis/23_TASK_QUEST_AUTOMATION.md`
- Pet/Spirit: `analysis/24_PET_SPIRIT_AUTO_RUNTIME.md`
- MainThread execution: `contexts/BUILD_MAINTHREAD_BRIDGE.md`.

## VERIFIED contracts

- `C_AutoModel.Train = 1`.
- Semantic start: `GUI.FindUI("AutoFight_Main"):StartAutoFight(C_AutoModel.Train)`.
- Visible `Đánh quái` is a configuration tab, not the Train start command.
- Built-in engine uses nearby target queries, reachability, `Game.SelectTarget`, `Game.ChaseTarget`, `RequestUsingSkillWithTarget/Pos`, target reload/death checks and HP state.
- Skill identity is SkillID, not F1/F2.
- Cooldown is queryable via `Game.GetSkillCooldown(skillID)`.

## State-machine rule

Suggested outer flow:

`PRECHECK -> START_TRAIN -> TRAINING -> TARGET/COMBAT -> LOOT(optional) -> BAG_CHECK -> RECOVERY/REVIVE/SELL/RETURN as delegated -> RESUME`.

Do not implement Train as a screen-click macro.

## Guards

Before mutable combat action:

- map ready;
- local player alive;
- no blocking progress/channel state unless action permits it;
- no Captcha/manual pause;
- target is fresh/valid/alive;
- skill is learned/condition-valid/cooldown-ready;
- one mutable action maximum.

## State proof

Examples:

- target identity/state changes;
- target HP/death changes;
- cooldown/progress transition;
- movement destination/range changes;
- loot/bag event after drop pickup.

Fixed sleep is never success proof.

## Completion criteria

Train implementation should start/stop semantically, recover from stale/dead/unreachable targets, not spam skills while cooldown/progress blocks them, and cleanly yield control to higher-priority Revive/Sell/Captcha/orchestrator states.