# Context Packs

These files are compact task-specific reading plans for AI/tool builders.

Purpose: prevent context overload as the knowledge base grows.

## Rule

For a normal task:

1. read `AI_BOOTSTRAP.md`;
2. route via `AI_ROUTER.md`;
3. read one matching `BUILD_*.md` file;
4. read its REQUIRED docs;
5. use OPTIONAL docs only when the implementation actually needs them.

Do not read every context pack.

## Packs

- `BUILD_TOOL_CORE.md`
- `BUILD_RUNTIME_SCANNER.md`
- `BUILD_MAINTHREAD_BRIDGE.md`
- `BUILD_AUTO_TRAIN.md`
- `BUILD_AUTO_BUFF.md`
- `BUILD_AUTO_SELL.md`
- `BUILD_AUTO_HEAL.md`
- `BUILD_AUTO_REVIVE.md`
- `BUILD_PARTY.md`
- `BUILD_ORCHESTRATOR.md`

## Context-pack contract

Each pack defines:

- task scope;
- REQUIRED reading;
- OPTIONAL lookup;
- VERIFIED contracts that may be used without rediscovery;
- known unknowns;
- forbidden regressions;
- completion/state-proof criteria.

If a context pack becomes stale because the underlying VERIFIED truth changes, update the pack rather than adding contradictory duplicate instructions elsewhere.