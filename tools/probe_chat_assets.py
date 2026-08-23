from pathlib import Path
import re
import struct
import subprocess
import sys

import UnityPy

DLL = Path("Game/Thần Long  Mobile_Data/Plugins/x86_64/FGClientTool_Windows.dll")
ROOT = Path("Game/Thần Long  Mobile_Data/StreamingAssets")
TARGET_FULL_INTERFACE = {
    "MiniBox_MiniEventFrame", "MiniBox", "TCPCmdHandler", "AutoFight_FuBen",
    "AutoFight_Main", "Loader", "AutoFuBen"
}
TARGET_FULL_CONFIG = {"FuBenScenarios", "Activities"}
MONSTER_IDS = set(range(1650, 1770)) | set(range(2490, 2500)) | set(range(32490, 32500))


def ensure_deps():
    try:
        import pefile  # noqa
        import unicorn  # noqa
    except Exception:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "pefile", "unicorn"])


def align_up(v, a=0x1000): return (v + a - 1) & ~(a - 1)


def decrypt(raw: bytes) -> bytes:
    ensure_deps()
    import pefile
    from unicorn import Uc, UC_ARCH_X86, UC_MODE_64
    from unicorn.x86_const import UC_X86_REG_RCX, UC_X86_REG_RDX, UC_X86_REG_RSP, UC_X86_REG_RIP
    pe = pefile.PE(str(DLL), fast_load=False)
    base = int(pe.OPTIONAL_HEADER.ImageBase)
    size = align_up(int(pe.OPTIONAL_HEADER.SizeOfImage))
    rva = next(int(s.address) for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name == b"FG_Decrypt")
    uc = Uc(UC_ARCH_X86, UC_MODE_64)
    uc.mem_map(base, size)
    b = DLL.read_bytes()
    uc.mem_write(base, b[:min(len(b), int(pe.OPTIONAL_HEADER.SizeOfHeaders))])
    for sec in pe.sections:
        d = sec.get_data()
        if d: uc.mem_write(base + int(sec.VirtualAddress), d)
    data_addr = 0x10000000
    uc.mem_map(data_addr, align_up(len(raw)+0x1000)); uc.mem_write(data_addr, raw)
    stack = 0x30000000; uc.mem_map(stack, 0x20000)
    sentinel = 0x40000000; uc.mem_map(sentinel, 0x1000); uc.mem_write(sentinel, b"\xcc")
    rsp = ((stack + 0x20000 - 0x200) & ~0xf) - 8
    uc.mem_write(rsp, struct.pack("<Q", sentinel))
    uc.reg_write(UC_X86_REG_RSP, rsp); uc.reg_write(UC_X86_REG_RCX, data_addr); uc.reg_write(UC_X86_REG_RDX, len(raw))
    try: uc.emu_start(base+rva, sentinel, timeout=20_000_000, count=200_000_000)
    except Exception as e:
        raise RuntimeError(f"decrypt RIP={uc.reg_read(UC_X86_REG_RIP):x}: {e}")
    out = bytes(uc.mem_read(data_addr, len(raw)))
    if not out.startswith((b"UnityFS", b"UnityRaw", b"UnityWeb")): raise RuntimeError("bad signature")
    return out


def decode(v):
    if isinstance(v, str): return v
    for enc in ("utf-8-sig", "utf-8", "utf-16-le", "latin-1"):
        try: return v.decode(enc)
        except Exception: pass
    return str(v)


def load_assets(path: Path):
    dec = decrypt(path.read_bytes())
    tmp = Path(path.name + ".dec"); tmp.write_bytes(dec)
    env = UnityPy.load(str(tmp)); out = {}
    for obj in env.objects:
        if obj.type.name == "TextAsset":
            d = obj.read(); out[getattr(d,"m_Name","") or ""] = decode(getattr(d,"m_Script",b""))
    return out


def print_full(name, text):
    print("\n" + "="*140); print("FULL_ASSET=" + name); print("="*140); print(text)


def main():
    ia = load_assets(ROOT / "Interface.unity3d")
    ca = load_assets(ROOT / "Config.unity3d")
    print(f"INTERFACE_TEXTASSETS={len(ia)} CONFIG_TEXTASSETS={len(ca)}")
    for name in sorted(TARGET_FULL_INTERFACE):
        if name in ia: print_full(name, ia[name])
    for name in sorted(TARGET_FULL_CONFIG):
        if name in ca: print_full(name, ca[name])

    monsters = ca.get("Monsters", "")
    print("\n" + "="*140); print("THUY_LAO_MONSTER_ROWS"); print("="*140)
    for line in monsters.splitlines():
        m = re.search(r'<Monster\s+ID="(\d+)"', line)
        if m and int(m.group(1)) in MONSTER_IDS:
            print(line)

    print("\n" + "="*140); print("GLOBAL_REFERENCES_TO_MINIEVENT_AND_FUBEN_PACKETS"); print("="*140)
    needles = ["MiniEventFrame", "SetEventFrameVisible", "CMD_FUBEN_AUTO_DATA", "CMD_FUBEN_KILL_PROGRESS", "CMD_FUBEN_QUERY_ALIVE", "CMD_FUBEN_COMPLETE", "CMD_FUBEN_SYNC_TARGET"]
    for name, text in sorted(ia.items()):
        lines = text.splitlines()
        hitidx = [i for i,l in enumerate(lines) if any(n in l for n in needles)]
        if hitidx:
            print(f"\n### ASSET {name}")
            shown=set()
            for i in hitidx:
                for j in range(max(0,i-6),min(len(lines),i+7)):
                    if j not in shown:
                        print(f"{j+1:05d}: {lines[j]}"); shown.add(j)
                print("...")
    return 0

if __name__ == "__main__": raise SystemExit(main())
