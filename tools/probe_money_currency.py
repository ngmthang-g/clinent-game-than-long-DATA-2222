from pathlib import Path
import re
import sys

import UnityPy

ROOT = Path("Game/Thần Long  Mobile_Data")
BUNDLES = [
    ROOT / "StreamingAssets" / "Interface.unity3d",
    ROOT / "StreamingAssets" / "Translations.unity3d",
]
METADATA = ROOT / "il2cpp_data" / "Metadata" / "global-metadata.dat"

KEYWORDS = (
    "roledata.money",
    "roledata.bankmoney",
    "boundmoney",
    "bindmoney",
    "bindedmoney",
    "moneybound",
    "boundgold",
    "bindgold",
    "lockedgold",
    "cmd_update_money",
    "processupdatemoney",
    "update_money",
    "moneytype",
    "currency",
    "vàng khóa",
    "vang khoa",
)


def decode_script(raw):
    if isinstance(raw, str):
        return raw
    if isinstance(raw, (bytes, bytearray)):
        for enc in ("utf-8-sig", "utf-8", "utf-16-le", "latin-1"):
            try:
                return raw.decode(enc)
            except Exception:
                pass
    return str(raw)


def contexts(text, terms, radius=6):
    lines = text.splitlines()
    lower = [line.lower() for line in lines]
    spans = []
    for i, line in enumerate(lower):
        if any(term in line for term in terms):
            spans.append((max(0, i-radius), min(len(lines), i+radius+1)))
    merged = []
    for a, b in spans:
        if merged and a <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], b))
        else:
            merged.append((a, b))
    return [(a, b, lines[a:b]) for a, b in merged]


def probe_bundle(path):
    print("=" * 110)
    print(f"BUNDLE={path}")
    if not path.exists():
        print("MISSING")
        return 1
    env = UnityPy.load(str(path))
    inspected = 0
    hit_assets = 0
    for obj in env.objects:
        if obj.type.name != "TextAsset":
            continue
        inspected += 1
        try:
            data = obj.read()
            name = getattr(data, "m_Name", "") or ""
            text = decode_script(getattr(data, "m_Script", b""))
        except Exception as exc:
            print(f"WARN read TextAsset path_id={obj.path_id}: {exc}", file=sys.stderr)
            continue
        low = f"{name}\n{text}".lower()
        matched = [k for k in KEYWORDS if k in low]
        # Also keep money-bearing Lua assets if they look economy/UI related.
        if not matched and "money" in low and any(x in low for x in ("roledata", "process", "cmd_", "bank", "bound", "bind", "shop", "bag")):
            matched = ["money+economy-context"]
        if not matched:
            continue
        hit_assets += 1
        print("-" * 110)
        print(f"ASSET={name!r} MATCHED={','.join(matched)}")
        terms = tuple(k for k in KEYWORDS if k in low)
        if not terms:
            terms = ("money",)
        for a, b, block in contexts(text, terms):
            print(f"LINES {a+1}-{b}")
            for idx, line in enumerate(block, a+1):
                print(f"{idx:05d}: {line}")
    print(f"TEXT_ASSETS_INSPECTED={inspected} HIT_ASSETS={hit_assets}")
    return 0


def probe_metadata(path):
    print("=" * 110)
    print(f"METADATA={path}")
    if not path.exists():
        print("MISSING")
        return 1
    raw = path.read_bytes()
    # IL2CPP metadata contains many NUL-separated UTF-8 identifiers. Extract printable tokens only.
    tokens = set()
    for m in re.finditer(rb"[A-Za-z_][A-Za-z0-9_]{2,80}", raw):
        token = m.group().decode("ascii", "ignore")
        low = token.lower()
        if any(k in low for k in ("money", "gold", "currency", "bind", "bound")):
            tokens.add(token)
    ranked = sorted(tokens, key=lambda s: (0 if "money" in s.lower() else 1, s.lower()))
    print(f"CANDIDATE_IDENTIFIER_COUNT={len(ranked)}")
    for token in ranked[:500]:
        print(token)
    return 0


def main():
    rc = 0
    for bundle in BUNDLES:
        rc |= probe_bundle(bundle)
    rc |= probe_metadata(METADATA)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
