from pathlib import Path
import re
import unicodedata
import UnityPy

ROOT = Path("Game/Thần Long  Mobile_Data/StreamingAssets")
BUNDLES = {
    "Interface": ROOT / "Interface.unity3d",
    "Config": ROOT / "Config.unity3d",
}

RAW_TERMS = [
    "CMD_FUBEN_AUTO_DATA", "CMD_FUBEN_KILL_PROGRESS", "CMD_FUBEN_QUERY_ALIVE",
    "CMD_FUBEN_MATCHMAKING", "CMD_FUBEN_COMPLETE", "CMD_FUBEN_SYNC_TARGET",
    "AutoFight_FuBen", "FuBen", "SelectedFuBen", "KillProgress", "QueryAlive",
    "TimeLeft", "Timeout", "Complete", "Activity", "Hoạt động",
    "Thủy Lao", "ThuyLao", "Phạm nhân", "Thống lĩnh phạm nhân",
    "phạm nhân bình thường", "thống lĩnh", "prison", "prisoner",
]

PRECISE_TERMS = [
    "CMD_FUBEN_AUTO_DATA", "CMD_FUBEN_KILL_PROGRESS", "CMD_FUBEN_QUERY_ALIVE",
    "CMD_FUBEN_COMPLETE", "CMD_FUBEN_SYNC_TARGET", "AutoFight_FuBen",
    "Thủy Lao", "ThuyLao", "Phạm nhân", "Thống lĩnh phạm nhân",
]


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


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s).lower()
    return "".join(c for c in s if unicodedata.category(c) != "Mn")

NORM_TERMS = [(t, norm(t)) for t in RAW_TERMS]
PRECISE_NORM = [(t, norm(t)) for t in PRECISE_TERMS]


def matched_terms(name: str, text: str):
    h = norm(name + "\n" + text)
    return [raw for raw, nt in NORM_TERMS if nt in h]


def precise_match(name: str, text: str):
    h = norm(name + "\n" + text)
    return any(nt in h for _, nt in PRECISE_NORM)


def context_hits(text: str, radius: int = 4):
    lines = text.splitlines()
    selected = set()
    for i, line in enumerate(lines):
        nl = norm(line)
        if any(nt in nl for _, nt in NORM_TERMS):
            for j in range(max(0, i-radius), min(len(lines), i+radius+1)):
                selected.add(j)
    out = []
    last = -2
    for i in sorted(selected):
        if i != last + 1:
            out.append("...")
        out.append(f"{i+1:05d}: {lines[i]}")
        last = i
    return "\n".join(out)


def method_inventory(text: str):
    pats = [
        r"function\s+([A-Za-z0-9_\.]+:[A-Za-z0-9_]+)\s*\(",
        r"function\s+([A-Za-z0-9_\.]+\.[A-Za-z0-9_]+)\s*\(",
    ]
    found = []
    for p in pats:
        found.extend(re.findall(p, text))
    return sorted(set(x for x in found if "fuben" in x.lower() or "activity" in x.lower() or "kill" in x.lower() or "complete" in x.lower() or "alive" in x.lower()))


def scan_bundle(label: str, path: Path):
    env = UnityPy.load(str(path))
    assets = []
    for obj in env.objects:
        if obj.type.name != "TextAsset":
            continue
        data = obj.read()
        name = getattr(data, "m_Name", "") or ""
        text = decode_script(getattr(data, "m_Script", b""))
        terms = matched_terms(name, text)
        if terms:
            assets.append((name, text, terms, precise_match(name, text)))

    with open(f"fuben_{label.lower()}_hits.txt", "w", encoding="utf-8") as f:
        f.write(f"BUNDLE={label}\nMATCHED_ASSETS={len(assets)}\n\n")
        for idx, (name, text, terms, precise) in enumerate(assets, 1):
            f.write("="*120 + "\n")
            f.write(f"ASSET {idx}: {name}\n")
            f.write("MATCHED=" + ", ".join(terms) + "\n")
            methods = method_inventory(text)
            if methods:
                f.write("METHODS=" + ", ".join(methods) + "\n")
            f.write("-"*120 + "\n")
            f.write(context_hits(text) + "\n\n")

    with open(f"fuben_{label.lower()}_precise_full.txt", "w", encoding="utf-8") as f:
        precise_assets = [a for a in assets if a[3]]
        f.write(f"BUNDLE={label}\nPRECISE_ASSETS={len(precise_assets)}\n\n")
        for idx, (name, text, terms, _) in enumerate(precise_assets, 1):
            f.write("="*120 + "\n")
            f.write(f"ASSET {idx}: {name}\n")
            f.write("MATCHED=" + ", ".join(terms) + "\n")
            f.write("-"*120 + "\n")
            f.write(text)
            f.write("\n\n")

    with open(f"fuben_{label.lower()}_asset_names.txt", "w", encoding="utf-8") as f:
        for name, _, terms, precise in assets:
            f.write(f"{name}\tprecise={int(precise)}\t{','.join(terms)}\n")

    print(f"{label}: matched={len(assets)} precise={sum(1 for a in assets if a[3])}")


def main():
    for label, path in BUNDLES.items():
        if not path.exists():
            raise SystemExit(f"missing bundle: {path}")
        scan_bundle(label, path)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
