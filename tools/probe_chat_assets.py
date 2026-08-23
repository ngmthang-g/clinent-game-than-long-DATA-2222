from pathlib import Path
import re
import unicodedata
import UnityPy

ROOT = Path("Game/Thần Long  Mobile_Data/StreamingAssets")
BUNDLES = [
    ("INTERFACE", ROOT / "Interface.unity3d"),
    ("CONFIG", ROOT / "Config.unity3d"),
]

TERMS = [
    "CMD_FUBEN_AUTO_DATA", "CMD_FUBEN_KILL_PROGRESS", "CMD_FUBEN_QUERY_ALIVE",
    "CMD_FUBEN_MATCHMAKING", "CMD_FUBEN_COMPLETE", "CMD_FUBEN_SYNC_TARGET",
    "AutoFight_FuBen", "FuBen", "SelectedFuBen", "KillProgress", "QueryAlive",
    "TimeLeft", "Timeout", "Activity", "Hoạt động", "Thủy Lao", "ThuyLao",
    "Phạm nhân", "Thống lĩnh phạm nhân", "phạm nhân bình thường", "thống lĩnh",
    "prison", "prisoner", "alive", "complete",
]
PRECISE = [
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


def norm(s):
    s = unicodedata.normalize("NFD", s).lower()
    return "".join(c for c in s if unicodedata.category(c) != "Mn")

NTERMS = [(t, norm(t)) for t in TERMS]
NPRECISE = [(t, norm(t)) for t in PRECISE]


def matches(name, text):
    h = norm(name + "\n" + text)
    return [raw for raw, nt in NTERMS if nt in h]


def is_precise(name, text):
    h = norm(name + "\n" + text)
    return any(nt in h for _, nt in NPRECISE)


def contexts(text, radius=5):
    lines = text.splitlines()
    keep = set()
    for i, line in enumerate(lines):
        nl = norm(line)
        if any(nt in nl for _, nt in NTERMS):
            for j in range(max(0, i-radius), min(len(lines), i+radius+1)):
                keep.add(j)
    out, last = [], -2
    for i in sorted(keep):
        if i != last + 1:
            out.append("...")
        out.append(f"{i+1:05d}: {lines[i]}")
        last = i
    return "\n".join(out)


def load_env(label, path):
    raw = bytearray(path.read_bytes())
    print(f"{label}_SIZE={len(raw)} FIRST16={bytes(raw[:16]).hex(' ')}")
    # Frozen snapshot transform visibly preserves bytes 3..6 as 'tyFS' while corrupting
    # the first three bytes of the standard UnityFS signature. Try the minimal recovery
    # first; do not alter any other bytes unless evidence requires it.
    if not raw.startswith(b"UnityFS") and len(raw) >= 7 and bytes(raw[3:7]) == b"tyFS":
        print(f"{label}: restoring first 3 signature bytes to 'Uni'")
        raw[0:3] = b"Uni"
        patched = path.with_name(path.name + ".headerpatched")
        patched.write_bytes(raw)
        try:
            return UnityPy.load(str(patched))
        except Exception as exc:
            print(f"{label}: minimal header patch failed: {type(exc).__name__}: {exc}")
    return UnityPy.load(str(path))


def scan(label, path):
    print("#" * 120)
    print(f"BUNDLE {label}: {path}")
    env = load_env(label, path)
    assets = []
    text_assets = 0
    type_counts = {}
    for obj in env.objects:
        type_counts[obj.type.name] = type_counts.get(obj.type.name, 0) + 1
        if obj.type.name != "TextAsset":
            continue
        text_assets += 1
        data = obj.read()
        name = getattr(data, "m_Name", "") or ""
        text = decode_script(getattr(data, "m_Script", b""))
        hit = matches(name, text)
        if hit:
            assets.append((name, text, hit, is_precise(name, text)))
    print("TYPE_COUNTS=" + ", ".join(f"{k}:{v}" for k, v in sorted(type_counts.items())))
    print(f"TEXT_ASSETS={text_assets} MATCHED={len(assets)} PRECISE={sum(a[3] for a in assets)}")
    print()

    print("ASSET INDEX")
    for idx, (name, text, hit, precise) in enumerate(assets, 1):
        print(f"{idx:03d}\t{name}\tprecise={int(precise)}\t{','.join(hit)}")
    print()

    print("CONTEXT HITS")
    for idx, (name, text, hit, precise) in enumerate(assets, 1):
        print("=" * 120)
        print(f"ASSET {idx}: {name} precise={int(precise)}")
        print("MATCHED=" + ", ".join(hit))
        meth = sorted(set(re.findall(r"function\s+([A-Za-z0-9_\.]+(?::|\.)[A-Za-z0-9_]+)\s*\(", text)))
        meth = [m for m in meth if any(k in m.lower() for k in ("fuben", "kill", "alive", "complete", "activity", "time"))]
        if meth:
            print("METHODS=" + ", ".join(meth))
        print("-" * 120)
        print(contexts(text))
        print()

    print("PRECISE FULL ASSETS")
    for idx, (name, text, hit, precise) in enumerate(assets, 1):
        if not precise:
            continue
        print("=" * 120)
        print(f"FULL ASSET {idx}: {name}")
        print("MATCHED=" + ", ".join(hit))
        print("-" * 120)
        print(text)
        print()


def main():
    for label, path in BUNDLES:
        if not path.exists():
            raise SystemExit(f"missing bundle: {path}")
        scan(label, path)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
