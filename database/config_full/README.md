# Full Config fallback database

This directory is the structurally-lossless fallback for **all 75 Config XML TextAssets** recovered from the frozen `Config.unity3d` snapshot.

Preferred lookup order remains:

```text
feature
 -> database/TOOL_DATA_INDEX.md
 -> specialized tool-first index/chunk
 -> database/config_full only when the specialized layer lacks a field/table
 -> runtime/server state for mutable/current truth
```

Do not load this whole directory into AI context.

## Entry points

- `CONFIG_FULL_CATALOG.csv` — table name, source XML, row count, direct attribute names, nested-child status/depth and chunk files.
- `CONFIG_FULL_MANIFEST.csv` — generated file path, bytes and row count.
- `<Table>/ROWS_*.csv` — structurally preserved rows for one Config table.

Each row preserves:

- `RowIndex`
- original XML row `Tag`
- every direct XML attribute under its original attribute name
- `Text` if any non-whitespace node text exists
- recursive `ChildrenJSON` with child tags, attributes, nested children and text.

The current frozen catalog reports zero non-whitespace XML text nodes outside the attribute/child structure, so this representation preserves the semantic Config tree needed for future static lookup.

## Reproducibility

Source:

`Game/Thần Long  Mobile_Data/StreamingAssets/Config.unity3d`

Generator:

`tools/materialize_all_config.py`

Workflow:

`.github/workflows/materialize-tool-data.yml`

The workflow requires exactly **75** recovered Config XML tables; a different count fails closed instead of silently producing a partial database.

## Do not confuse static and live state

This database answers frozen configuration/template questions. It does not prove current:

- spawned actor/position/death/HP;
- current bag item instance IDs;
- current task progress;
- current dialog selection IDs;
- shop/session IDs;
- server acceptance/completion.

Use runtime/server proof for those.
