# Static Config database

This directory is the planned/query-oriented home for normalized large Config tables extracted from the frozen client.

## Current repository state

Schemas, counts and normalization rules are VERIFIED and documented in `analysis/28_STATIC_DATA_DATABASE_EXPANSION.md`.

The large normalized CSV chunks were generated during research, but **the full chunk files have not yet been uploaded into this GitHub directory**. Do not assume a directory/file exists just because the schema is documented.

Upload completion remains tracked in `research/TODO.md`.

## Verified source sizes

- Items — 5,238 rows
- Skills — 2,091 rows
- MagicAtrributes — 509 rows
- Monsters — 17,121 rows
- Equips — 22,763 rows.

## Intended layout after upload

- `items/` — chunked Items CSV + small routing index.
- `skills/` — chunked Skills CSV + small routing index.
- `magic/` — MagicAtrributes CSV.
- `monsters/` — chunked Monsters CSV + small routing index.
- `equips/` — chunked Equips CSV + small routing index.

Read `LOOKUP_GUIDE.md` for the index/chunk strategy designed to prevent AI context overload.

## Important use rules

Static rows describe templates. Live mutable actions must still resolve current runtime instance (`ID`), template `ItemID`, current slot/site and current semantic guards before acting.

For weapon preservation, `Equips.xml EquipPoint=0` is the static Weapon slot identity. Do not classify weapons only by the `Type` subtype.

## AI rule

Large databases are lookup systems, not mandatory reading. Locate an ID/name/category through a small index and open only the relevant chunk.