from pathlib import Path
import subprocess

DLL = Path("Game/Thần Long  Mobile_Data/Plugins/x86_64/FGClientTool_Windows.dll")
BUNDLES = [
    Path("Game/Thần Long  Mobile_Data/StreamingAssets/Interface.unity3d"),
    Path("Game/Thần Long  Mobile_Data/StreamingAssets/Config.unity3d"),
]


def run(cmd):
    print("$ " + " ".join(map(str, cmd)))
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace")
    print(p.stdout)
    print(f"EXIT={p.returncode}")
    return p.returncode


def main():
    print(f"DLL={DLL} exists={DLL.exists()} size={DLL.stat().st_size if DLL.exists() else -1}")
    if DLL.exists():
        print("=" * 120)
        print("PE/EXPORT INFO")
        run(["objdump", "-p", str(DLL)])
        print("=" * 120)
        print("FG_Decrypt SYMBOL DISASSEMBLY")
        run(["objdump", "-d", "-M", "intel", "--disassemble=FG_Decrypt", str(DLL)])
        print("=" * 120)
        print("FG_Encrypt SYMBOL DISASSEMBLY")
        run(["objdump", "-d", "-M", "intel", "--disassemble=FG_Encrypt", str(DLL)])
        print("=" * 120)
        print("FULL TEXT DISASSEMBLY (for export RVA context)")
        run(["objdump", "-d", "-M", "intel", str(DLL)])

    for path in BUNDLES:
        if not path.exists():
            continue
        raw = path.read_bytes()
        print("=" * 120)
        print(f"BUNDLE={path.name} SIZE={len(raw)}")
        print("FIRST256=" + raw[:256].hex(" "))
        print("LAST256=" + raw[-256:].hex(" "))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
