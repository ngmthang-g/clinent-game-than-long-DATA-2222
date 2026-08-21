from pathlib import Path
import sys

import UnityPy

BUNDLE = Path("Game/Thần Long  Mobile_Data/StreamingAssets/Interface.unity3d")
KEYWORDS = (
    "chat",
    "cmd_client_chat",
    "cmd_chat_data",
    "sendpacket",
    "displaychat",
    "whisper",
    "private",
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


def main() -> int:
    if not BUNDLE.exists():
        print(f"ERROR: bundle not found: {BUNDLE}")
        return 2

    env = UnityPy.load(str(BUNDLE))
    hits = []
    inspected = 0

    for obj in env.objects:
        if obj.type.name != "TextAsset":
            continue
        inspected += 1
        try:
            data = obj.read()
            name = getattr(data, "m_Name", "") or ""
            text = decode_script(getattr(data, "m_Script", b""))
        except Exception as exc:
            print(f"WARN: cannot read TextAsset path_id={obj.path_id}: {exc}", file=sys.stderr)
            continue

        haystack = f"{name}\n{text}".lower()
        matched = [k for k in KEYWORDS if k in haystack]
        if matched:
            hits.append((name, matched, text))

    print(f"TEXT_ASSETS_INSPECTED={inspected}")
    print(f"MATCHED_ASSETS={len(hits)}")
    print()

    for index, (name, matched, text) in enumerate(hits, 1):
        print("=" * 100)
        print(f"ASSET {index}: {name}")
        print("MATCHED: " + ", ".join(matched))
        print("-" * 100)
        print(text)
        print()

    return 0 if hits else 3


if __name__ == "__main__":
    raise SystemExit(main())
