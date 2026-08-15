# Static Config database

These files are normalized from the decrypted frozen-client Config XML. They exist so future AI can query/filter data directly instead of reopening Unity bundles.

## Directories

- `items/` — 5,238 `Items.xml` rows, chunked CSV.
- `skills/` — 2,091 `Skills.xml` rows, chunked CSV.
- `magic/` — 509 `MagicAtrributes.xml` rows.
- `monsters/` — 17,121 `Monsters.xml` rows, chunked CSV.
- `equips/` — 22,763 `Equips.xml` rows, chunked CSV.

Read `analysis/28_STATIC_DATA_DATABASE_EXPANSION.md` for schema interpretation, counts and the critical difference between `Equip.Type` and `EquipPoint`.

## Important use rules

Static rows describe templates. Live mutable actions must still resolve the current runtime instance (`ID`), current bag slot/site and current semantic guards before acting.

For weapon preservation, `Equips.xml EquipPoint=0` is the static Weapon slot identity. Do not classify weapons only by the `Type` subtype.
