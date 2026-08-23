from pathlib import Path
import re
import struct
import subprocess
import sys
import unicodedata

import UnityPy

DLL = Path("Game/Thần Long  Mobile_Data/Plugins/x86_64/FGClientTool_Windows.dll")
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


def ensure_emulator_deps():
    try:
        import pefile  # noqa: F401
        import unicorn  # noqa: F401
        return
    except Exception:
        pass
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "--disable-pip-version-check",
        "pefile", "unicorn"
    ])


def align_up(v, a=0x1000):
    return (v + a - 1) & ~(a - 1)


def emulate_fg_decrypt(raw: bytes) -> bytes:
    ensure_emulator_deps()
    import pefile
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_64
    from unicorn.x86_const import UC_X86_REG_RCX, UC_X86_REG_RDX, UC_X86_REG_RSP, UC_X86_REG_RIP

    pe = pefile.PE(str(DLL), fast_load=False)
    image_base = int(pe.OPTIONAL_HEADER.ImageBase)
    image_size = align_up(int(pe.OPTIONAL_HEADER.SizeOfImage))

    export_rva = None
    for sym in pe.DIRECTORY_ENTRY_EXPORT.symbols:
        if sym.name == b"FG_Decrypt":
            export_rva = int(sym.address)
            break
    if export_rva is None:
        raise RuntimeError("FG_Decrypt export not found")

    uc = Uc(UC_ARCH_X86, UC_MODE_64)
    uc.mem_map(image_base, image_size)

    dll_bytes = DLL.read_bytes()
    headers_len = min(len(dll_bytes), int(pe.OPTIONAL_HEADER.SizeOfHeaders))
    uc.mem_write(image_base, dll_bytes[:headers_len])
    for sec in pe.sections:
        data = sec.get_data()
        if data:
            uc.mem_write(image_base + int(sec.VirtualAddress), data)

    data_addr = 0x10000000
    data_size = align_up(len(raw) + 0x1000)
    uc.mem_map(data_addr, data_size)
    uc.mem_write(data_addr, raw)

    stack_base = 0x30000000
    stack_size = 0x20000
    uc.mem_map(stack_base, stack_size)
    sentinel = 0x40000000
    uc.mem_map(sentinel, 0x1000)
    uc.mem_write(sentinel, b"\xCC")

    # Win64 function entry: RSP % 16 == 8, return address at [RSP],
    # with caller shadow space available above it.
    rsp = (stack_base + stack_size - 0x200) & ~0xF
    rsp -= 8
    uc.mem_write(rsp, struct.pack("<Q", sentinel))
    uc.reg_write(UC_X86_REG_RSP, rsp)
    uc.reg_write(UC_X86_REG_RCX, data_addr)
    uc.reg_write(UC_X86_REG_RDX, len(raw))

    start = image_base + export_rva
    try:
        uc.emu_start(start, sentinel, timeout=20_000_000, count=200_000_000)
    except Exception as exc:
        rip = uc.reg_read(UC_X86_REG_RIP)
        raise RuntimeError(f"FG_Decrypt emulation failed at RIP=0x{rip:x}: {exc}") from exc

    return bytes(uc.mem_read(data_addr, len(raw)))


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
    hay = norm(name + "\n" + text)
    return [raw for raw, needle in NTERMS if needle in hay]


def precise(name, text):
    hay = norm(name + "\n" + text)
    return any(needle in hay for _, needle in NPRECISE)


def contexts(text, radius=12):
    lines = text.splitlines()
    keep = set()
    for i, line in enumerate(lines):
        nl = norm(line)
        if any(needle in nl for _, needle in NTERMS):
            for j in range(max(0, i - radius), min(len(lines), i + radius + 1)):
                keep.add(j)
    out = []
    last = -2
    for i in sorted(keep):
        if i != last + 1:
            out.append("...")
        out.append(f"{i+1:05d}: {lines[i]}")
        last = i
    return "\n".join(out)


def scan_bundle(label, path):
    raw = path.read_bytes()
    print("#" * 120)
    print(f"BUNDLE={label} FILE={path} SIZE={len(raw)} RAW_FIRST16={raw[:16].hex(' ')}")

    dec = emulate_fg_decrypt(raw)
    print(f"DECRYPTED_FIRST32={dec[:32]!r}")
    print(f"DECRYPTED_HEX={dec[:32].hex(' ')}")
    if not dec.startswith((b"UnityFS", b"UnityRaw", b"UnityWeb")):
        raise RuntimeError(f"{label}: FG_Decrypt result has no Unity bundle signature")

    tmp = Path(f"{label.lower()}_decrypted.unity3d")
    tmp.write_bytes(dec)
    env = UnityPy.load(str(tmp))

    text_assets = []
    type_counts = {}
    for obj in env.objects:
        type_counts[obj.type.name] = type_counts.get(obj.type.name, 0) + 1
        if obj.type.name != "TextAsset":
            continue
        data = obj.read()
        name = getattr(data, "m_Name", "") or ""
        text = decode_script(getattr(data, "m_Script", b""))
        text_assets.append((name, text))

    print("TYPE_COUNTS=" + ", ".join(f"{k}:{v}" for k, v in sorted(type_counts.items())))
    print(f"TEXT_ASSETS={len(text_assets)}")

    # First show all semantically likely asset names even if localized strings differ.
    likely = []
    for name, text in text_assets:
        nn = norm(name)
        if any(k in nn for k in ("fuben", "activity", "tcp", "autofight", "monster", "map", "scenario")):
            likely.append(name)
    print("LIKELY_ASSET_NAMES=" + " | ".join(sorted(set(likely))))

    hits = []
    for name, text in text_assets:
        mt = matches(name, text)
        if mt:
            hits.append((name, text, mt, precise(name, text)))
    print(f"MATCHED_ASSETS={len(hits)} PRECISE_ASSETS={sum(1 for h in hits if h[3])}")

    print("\nASSET HIT INDEX")
    for i, (name, text, mt, pr) in enumerate(hits, 1):
        print(f"{i:03d}\t{name}\tprecise={int(pr)}\t{','.join(mt)}")

    print("\nTARGETED CONTEXTS")
    for i, (name, text, mt, pr) in enumerate(hits, 1):
        print("=" * 120)
        print(f"ASSET {i}: {name} precise={int(pr)}")
        print("MATCHED=" + ", ".join(mt))
        methods = sorted(set(re.findall(r"function\s+([A-Za-z0-9_\.]+(?::|\.)[A-Za-z0-9_]+)\s*\(", text)))
        methods = [m for m in methods if any(k in m.lower() for k in ("fuben", "kill", "alive", "complete", "activity", "time", "packet"))]
        if methods:
            print("METHODS=" + ", ".join(methods))
        print("-" * 120)
        print(contexts(text))

    # AutoFight_FuBen is central and manageable: print it in full if present.
    for name, text in text_assets:
        if norm(name) == norm("AutoFight_FuBen"):
            print("\n" + "#" * 120)
            print("FULL AutoFight_FuBen")
            print("#" * 120)
            print(text)

    return text_assets


def main():
    print(f"DLL={DLL} SIZE={DLL.stat().st_size if DLL.exists() else -1}")
    for label, path in BUNDLES:
        scan_bundle(label, path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
