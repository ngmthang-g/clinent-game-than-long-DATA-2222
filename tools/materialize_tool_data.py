#!/usr/bin/env python3
"""
Materialize AI/tool-oriented static databases from the frozen Thần Long Mobile Config.unity3d.

Design:
  Config.unity3d -> FG decrypt -> UnityFS extract -> Config XML TextAssets
  -> query-oriented CSVs under database/

This script intentionally preserves runtime/static boundaries:
static Config describes templates; live mutable actions must still use fresh
runtime/server state and live instance/Role IDs.

Usage:
  python tools/materialize_tool_data.py \
    --config "Game/Thần Long  Mobile_Data/StreamingAssets/Config.unity3d" \
    --repo-root .
"""
from __future__ import annotations
import argparse, collections, csv, json, lzma, struct, tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    import lz4.block
except ImportError as exc:
    raise SystemExit("Missing dependency: pip install lz4") from exc


def _legacy(buf: bytearray, decrypt: bool = True) -> None:
    n = len(buf)
    if n < 128:
        return
    delta = -0x0F if decrypt else 0x0F
    for i in range(128):
        j = n - 1 - i
        a, b = buf[i], buf[j]
        buf[i] = (b + delta) & 0xFF
        buf[j] = (a + delta) & 0xFF


def _valid_bundle(buf: bytes | bytearray) -> bool:
    return buf.startswith(b"UnityFS\0") or buf.startswith(b"UnityRaw\0") or buf.startswith(b"UnityWeb\0")


def fg_decrypt(data: bytes) -> bytes:
    b = bytearray(data)
    n = len(b)
    if n < 128 or _valid_bundle(b):
        return bytes(b)
    _legacy(b, True)
    if _valid_bundle(b):
        return bytes(b)
    _legacy(b, False)
    x = (n ^ 0x9E3779B9) & 0xFFFFFFFF
    x ^= (x << 13) & 0xFFFFFFFF; x &= 0xFFFFFFFF
    x ^= x >> 17; x &= 0xFFFFFFFF
    x ^= (x << 5) & 0xFFFFFFFF; x &= 0xFFFFFFFF
    count = min(max((x & 0x7F) + 1, 1), n // 2)
    delta = ((x >> 7) & 0x7F) + 1
    if delta == 0x0F and count != 0x80:
        delta = 0x11
    for i in range(count):
        j = n - 1 - i
        a, bb = b[i], b[j]
        b[i] = (bb - delta) & 0xFF
        b[j] = (a - delta) & 0xFF
    if not _valid_bundle(b):
        raise ValueError("FG decrypt did not produce UnityFS/UnityRaw/UnityWeb")
    return bytes(b)


def _cstr(b: bytes, pos: int):
    j = b.index(0, pos)
    return b[pos:j], j + 1


def _decomp(data: bytes, ctype: int, usize: int) -> bytes:
    c = ctype & 0x3F
    if c == 0:
        return data
    if c in (2, 3):
        return lz4.block.decompress(data, uncompressed_size=usize)
    if c == 1:
        prop = data[0]
        lc = prop % 9
        rem = prop // 9
        lp = rem % 5
        pb = rem // 5
        ds = int.from_bytes(data[1:5], "little")
        return lzma.decompress(data[5:], format=lzma.FORMAT_RAW,
            filters=[{"id": lzma.FILTER_LZMA1, "dict_size": ds, "lc": lc, "lp": lp, "pb": pb}])
    raise ValueError(f"unsupported UnityFS compression {c}")


def extract_unityfs_bytes(b: bytes, outdir: Path) -> list[Path]:
    pos = 0
    sig, pos = _cstr(b, pos)
    if sig not in (b"UnityFS", b"UnityRaw", b"UnityWeb"):
        raise ValueError(f"bad bundle signature {sig!r}")
    _ver = struct.unpack_from(">I", b, pos)[0]; pos += 4
    _uv, pos = _cstr(b, pos)
    _rev, pos = _cstr(b, pos)
    _size = struct.unpack_from(">Q", b, pos)[0]; pos += 8
    cs, us, flags = struct.unpack_from(">III", b, pos); pos += 12
    if flags & 0x200:
        pos = (pos + 15) & ~15
    if flags & 0x80:
        bi_pos = len(b) - cs
        compinfo = b[bi_pos:]
        data_start = pos
    else:
        compinfo = b[pos:pos + cs]
        data_start = pos + cs
    if flags & 0x200:
        data_start = (data_start + 15) & ~15
    info = _decomp(compinfo, flags, us)
    q = 16
    n = struct.unpack_from(">I", info, q)[0]; q += 4
    blocks = []
    for _ in range(n):
        u, c, f = struct.unpack_from(">IIH", info, q); q += 10
        blocks.append((u, c, f))
    nd = struct.unpack_from(">I", info, q)[0]; q += 4
    dirs = []
    for _ in range(nd):
        off, sz, fl = struct.unpack_from(">QQI", info, q); q += 20
        name, q = _cstr(info, q)
        dirs.append((off, sz, fl, name.decode("utf-8", "replace")))
    dp = data_start
    chunks = []
    for u, c, f in blocks:
        chunks.append(_decomp(b[dp:dp + c], f, u)); dp += c
    body = b"".join(chunks)
    outdir.mkdir(parents=True, exist_ok=True)
    written = []
    for off, sz, _fl, name in dirs:
        p = outdir / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(body[off:off + sz])
        written.append(p)
    return written


XML_SIG = b'<?xml version="1.0" encoding="utf-8"?>'


def extract_config_xml_from_cab(cab: Path, outdir: Path) -> dict[str, Path]:
    b = cab.read_bytes(); outdir.mkdir(parents=True, exist_ok=True)
    found = {}; pos = 0
    while True:
        i = b.find(XML_SIG, pos)
        if i < 0:
            break
        if i < 4:
            pos = i + 1; continue
        L = struct.unpack_from("<I", b, i - 4)[0]
        if not (0 < L and i + L <= len(b)):
            pos = i + 1; continue
        j = i - 4; candidates = []
        for s in range(max(0, j - 260), j - 3):
            ln = struct.unpack_from("<I", b, s)[0]
            if 0 < ln <= 128 and ((s + 4 + ln + 3) & ~3) == j:
                raw = b[s + 4:s + 4 + ln]
                try:
                    name = raw.decode("utf-8")
                except UnicodeDecodeError:
                    continue
                if name and all(ch.isprintable() for ch in name):
                    candidates.append(name)
        if candidates:
            name = candidates[-1]
            p = outdir / f"{name}.xml"
            p.write_bytes(b[i:i + L]); found[name] = p
        pos = i + 1
    return found


def chunk_rows(rows, n):
    for i in range(0, len(rows), n):
        yield i, rows[i:i+n]


def children_json(el):
    def conv(x):
        d = {"Tag": x.tag, "Attributes": dict(x.attrib)}
        if list(x): d["Children"] = [conv(c) for c in x]
        return d
    return json.dumps([conv(c) for c in el], ensure_ascii=False, separators=(",", ":"))


class Builder:
    def __init__(self, xml_dir: Path, repo_root: Path):
        self.xml_dir = xml_dir; self.repo = repo_root; self.generated = []
    def load(self, name):
        return ET.parse(self.xml_dir / name).getroot()
    def csvwrite(self, rel, rows, fields=None):
        path = self.repo / rel; path.parent.mkdir(parents=True, exist_ok=True); rows = list(rows)
        if fields is None:
            fields, seen = [], set()
            for r in rows:
                for k in r:
                    if k not in seen: seen.add(k); fields.append(k)
        with path.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
        self.generated.append(path); return path
    def build(self):
        maps = {int(x.attrib["ID"]): x.attrib for x in self.load("Maps.xml")}
        npcs = {int(x.attrib["ID"]): x.attrib for x in self.load("NPCs.xml")}
        monsters = [dict(x.attrib) for x in self.load("Monsters.xml")]
        mon_by_id = {int(x["ID"]): x for x in monsters}
        mon_by_name = collections.defaultdict(list)
        for m in monsters: mon_by_name[m.get("Name", "")].append(m)

        fr = self.load("FuBenScenarios.xml")
        scrows, actionrows, killrows, entryrows, bossbands = [], [], [], [], []
        compact_fields = ["ScenarioID","ScenarioName","DungeonMapID","StepIndex","StepID","StepDesc","ActionIndex","ActionType","MapID","NPCID","X","Y","PosX","PosY","Count","Radius","Text","Timeout","Seconds","NextStep"]
        for s in fr:
            a = dict(s.attrib); gm, gn, dm = int(a.get("GatherMapID","0")), int(a.get("GatherNPCID","0")), int(a.get("DungeonMapID","0")); steps = s.findall("Step")
            scrows.append({**a,"DungeonMapName":maps.get(dm,{}).get("Name",""),"GatherMapName":maps.get(gm,{}).get("Name",""),"GatherNPCName":npcs.get(gn,{}).get("Name",""),"GatherNPCResName":npcs.get(gn,{}).get("ResName",""),"StepCount":len(steps),"ActionCount":sum(len(list(st)) for st in steps)})
            entryrows.append({"ScenarioID":a["ID"],"ScenarioName":a["Name"],"DungeonMapID":dm,"DungeonMapName":maps.get(dm,{}).get("Name",""),"GatherMapID":gm,"GatherMapName":maps.get(gm,{}).get("Name",""),"GatherNPCID":gn,"GatherNPCName":npcs.get(gn,{}).get("Name",""),"GatherNPCResName":npcs.get(gn,{}).get("ResName",""),"GatherX":a.get("GatherX",""),"GatherY":a.get("GatherY","")})
            for stidx, st in enumerate(steps, 1):
                stbase={"ScenarioID":a["ID"],"ScenarioName":a["Name"],"DungeonMapID":dm,"DungeonMapName":maps.get(dm,{}).get("Name",""),"StepIndex":stidx,"StepID":st.attrib.get("ID",""),"StepDesc":st.attrib.get("Desc",""),"StepTimeout":st.attrib.get("Timeout",""),"OnTimeout":st.attrib.get("OnTimeout",""),"RetryCount":st.attrib.get("RetryCount",""),"NextStep":st.attrib.get("NextStep","")}
                lastpos={"X":"","Y":""}
                for ai, act in enumerate(list(st), 1):
                    row={**stbase,"ActionIndex":ai,"ActionType":act.tag,**act.attrib}
                    if act.tag=="GoTo": lastpos={"X":act.attrib.get("X",""),"Y":act.attrib.get("Y","")}
                    tpls=[dict(t.attrib) for t in act.findall("Template")]; row["TemplatesJSON"]=json.dumps(tpls,ensure_ascii=False,separators=(",",":")) if tpls else ""; actionrows.append(row)
                    if act.tag=="Kill":
                        desc=act.attrib.get("Desc",""); mids=[]
                        if act.attrib.get("MonsterID","").isdigit(): mids.append(int(act.attrib["MonsterID"]))
                        mids += [int(t["MonsterID"]) for t in tpls if t.get("MonsterID","").isdigit()]; uniq=list(dict.fromkeys(mids)); matched=[mon_by_id[mid] for mid in uniq if mid in mon_by_id]; types=collections.Counter(m.get("Type","") for m in matched)
                        killrows.append({**stbase,"GoToX":lastpos["X"],"GoToY":lastpos["Y"],"KillCount":act.attrib.get("Count","1"),"Radius":act.attrib.get("Radius","800"),"Desc":desc,"DirectMonsterID":act.attrib.get("MonsterID",""),"TemplateCount":len(tpls),"TemplateMonsterIDs":",".join(str(x) for x in uniq),"TemplateLevelRanges":"|".join(f"{t.get('MonsterID','')}:{t.get('MinLevel','')}-{t.get('MaxLevel','')}" for t in tpls),"MappedTemplateCount":len(matched),"MappedTypes":"|".join(f"{k}:{v}" for k,v in sorted(types.items())),"VerifiedBossByConfiguredTemplates":str(bool(matched) and all(m.get("Type")=="Boss" for m in matched)).lower(),"StepNameSignalsBoss":str("boss" in st.attrib.get("ID","").lower()).lower(),"NameMatchMonsterCount":len(mon_by_name.get(desc,[]))})
                        for t in tpls:
                            mid=t.get("MonsterID",""); m=mon_by_id.get(int(mid)) if mid.isdigit() else None
                            bossbands.append({"ScenarioID":a["ID"],"ScenarioName":a["Name"],"StepIndex":stidx,"StepID":st.attrib.get("ID",""),"StepDesc":st.attrib.get("Desc",""),"MonsterID":mid,"LevelRange":f"{t.get('MinLevel','')}-{t.get('MaxLevel','')}","MonsterName":m.get("Name","") if m else "","MonsterResName":m.get("ResName","") if m else "","MonsterType":m.get("Type","") if m else ""})
        self.csvwrite("database/fuben/FUBEN_SCENARIOS.csv",scrows); self.csvwrite("database/fuben/FUBEN_ENTRY_NPCS.csv",entryrows); self.csvwrite("database/fuben/FUBEN_ACTIONS.csv",actionrows); self.csvwrite("database/fuben/FUBEN_ACTIONS_COMPACT.csv",actionrows,compact_fields); self.csvwrite("database/fuben/FUBEN_KILL_TARGETS.csv",killrows); self.csvwrite("database/fuben/FUBEN_BOSS_LEVEL_BANDS.csv",bossbands)
        for i,ch in chunk_rows(actionrows,55): self.csvwrite(f"database/fuben/actions/FUBEN_ACTIONS_{i+1:04d}_{i+len(ch):04d}.csv",ch)

        tr=self.load("Tasks.xml"); trows=[]; objrows=[]
        for t in tr:
            a=dict(t.attrib)
            def node(tag):
                x=t.find(tag); return dict(x.attrib) if x is not None else {}
            offer,complete=node("OfferNPC"),node("CompleteNPC"); objective=[]
            for oi,c in enumerate(t,1):
                if c.tag in ("OfferNPC","CompleteNPC","RequireTask","FixedAwardItem","AwardExp","AwardBoundMoney","AwardSkill","AwardPet"): continue
                children=[{"Tag":cc.tag,"Attributes":dict(cc.attrib)} for cc in c]; objective.append({"Tag":c.tag,"Attributes":dict(c.attrib),"Children":children})
                if children:
                    for ci,cc in enumerate(c,1): objrows.append({"TaskID":a.get("ID",""),"TaskName":a.get("Name",""),"TaskType":a.get("TaskType",""),"TaskRule":a.get("TaskRule",""),"ObjectiveTag":c.tag,"ObjectiveIndex":oi,"ChildTag":cc.tag,"ChildIndex":ci,"AttributesJSON":json.dumps(dict(c.attrib),ensure_ascii=False,separators=(",",":")),"ChildAttributesJSON":json.dumps(dict(cc.attrib),ensure_ascii=False,separators=(",",":"))})
                else: objrows.append({"TaskID":a.get("ID",""),"TaskName":a.get("Name",""),"TaskType":a.get("TaskType",""),"TaskRule":a.get("TaskRule",""),"ObjectiveTag":c.tag,"ObjectiveIndex":oi,"ChildTag":"","ChildIndex":"","AttributesJSON":json.dumps(dict(c.attrib),ensure_ascii=False,separators=(",",":")),"ChildAttributesJSON":""})
            def mapname(v): return maps.get(int(v),{}).get("Name","") if str(v).isdigit() else ""
            def npcname(v): return npcs.get(int(v),{}).get("Name","") if str(v).isdigit() else ""
            trows.append({**a,"OfferMapID":offer.get("MapID",""),"OfferMapName":mapname(offer.get("MapID","")),"OfferNPCID":offer.get("NPCID",""),"OfferNPCName":npcname(offer.get("NPCID","")),"CompleteMapID":complete.get("MapID",""),"CompleteMapName":mapname(complete.get("MapID","")),"CompleteNPCID":complete.get("NPCID",""),"CompleteNPCName":npcname(complete.get("NPCID","")),"ObjectiveJSON":json.dumps(objective,ensure_ascii=False,separators=(",",":")),"AllChildrenJSON":children_json(t)})
        for i,ch in chunk_rows(trows,260): self.csvwrite(f"database/static/tasks/TASKS_{i+1:04d}_{i+len(ch):04d}.csv",ch)
        idxfields=["ID","Name","TaskType","TaskRule","FactionID","RequireLevel","NextTaskID","CopySceneScriptID","OfferMapID","OfferMapName","OfferNPCID","OfferNPCName","CompleteMapID","CompleteMapName","CompleteNPCID","CompleteNPCName"]
        self.csvwrite("database/static/tasks/TASK_INDEX.csv",trows,idxfields); self.csvwrite("database/static/tasks/TASK_OBJECTIVES.csv",objrows)
        for i,ch in chunk_rows(objrows,160): self.csvwrite(f"database/static/tasks/objectives/TASK_OBJECTIVES_{i+1:04d}_{i+len(ch):04d}.csv",ch)

        items=[dict(x.attrib) for x in self.load("Items.xml")]
        for x in items: x["IDFamily10M"]=str(int(x["ID"])//10000000)
        for i,ch in chunk_rows(items,1000): self.csvwrite(f"database/static/items/ITEMS_{i+1:04d}_{i+len(ch):04d}.csv",ch)
        item_fields=["ID","Name","ItemLevel","RequireLevel","SellPrice","Throwable","Sellable","Bound","Stack","MaxUsageTimes","DurationHour","ScriptID","TypeDesc"]
        self.csvwrite("database/static/items/ITEM_TOOL_INDEX.csv",items,item_fields); self.csvwrite("database/static/items/ITEM_INDEX.csv",items,["ID","Name","ItemLevel","RequireLevel","SellPrice","Throwable","Sellable","Bound","Stack","ScriptID","TypeDesc","IDFamily10M"])
        exceptions=[x for x in items if x.get("Sellable")!="true" or x.get("Throwable")!="true" or x.get("Bound")=="true" or x.get("ScriptID","") not in ("","-1")]
        self.csvwrite("database/static/items/ITEM_POLICY_EXCEPTIONS.csv",exceptions,item_fields)
        counts=collections.Counter(x.get("TypeDesc","") for x in items); self.csvwrite("database/static/items/ITEM_TYPE_COUNTS.csv",[{"TypeDesc":k,"Count":v} for k,v in sorted(counts.items())],["TypeDesc","Count"])
        self.csvwrite("database/static/items/MEDICINES.csv",[dict(x.attrib) for x in self.load("Medicines.xml")]); gems=[dict(x.attrib) for x in self.load("Gems.xml")]
        for i,ch in chunk_rows(gems,600): self.csvwrite(f"database/static/items/GEMS_{i+1:04d}_{i+len(ch):04d}.csv",ch)

        skills=[dict(x.attrib) for x in self.load("Skills.xml")]
        for i,ch in chunk_rows(skills,700): self.csvwrite(f"database/static/skills/SKILLS_{i+1:04d}_{i+len(ch):04d}.csv",ch)
        sk_fields=["ID","Name","Type","Style","FactionID","BookID","RequireLevel","RequireWeapon","IsDamageSkill","TargetType","CastRange","AttackRadius","ProgressTime","CooldownGroup","Property","Tag"]
        self.csvwrite("database/static/skills/SKILL_INDEX.csv",skills,sk_fields); tool_fields=["ID","Name","FactionID","Type","TargetType","RequireLevel","CastRange","Property"]; self.csvwrite("database/static/skills/SKILL_TOOL_INDEX.csv",skills,tool_fields)
        for i,ch in chunk_rows(skills,420): self.csvwrite(f"database/static/skills/index/SKILL_TOOL_INDEX_{i+1:04d}_{i+len(ch):04d}.csv",ch,tool_fields)
        for name,outname in [("SkillProperties.xml","SKILL_PROPERTIES"),("AutoSkills.xml","AUTO_SKILLS"),("Factions.xml","FACTIONS"),("Books.xml","BOOKS"),("BookLevelUpCost.xml","BOOK_LEVEL_UP_COST")]:
            rows=[dict(x.attrib)|({"ChildrenJSON":children_json(x)} if list(x) else {}) for x in self.load(name)]
            if len(rows)>900:
                for i,ch in chunk_rows(rows,700): self.csvwrite(f"database/static/skills/{outname}_{i+1:04d}_{i+len(ch):04d}.csv",ch)
            else: self.csvwrite(f"database/static/skills/{outname}.csv",rows)
        self.csvwrite("database/static/magic/MAGIC_ATTRIBUTES.csv",[dict(x.attrib) for x in self.load("MagicAtrributes.xml")])

        monfields=["ID","ResName","Name","Level","Type","MaxHP","Exp","PhysAtk","PhysDef","MagicAtk","MagicDef","Hit","Dodge","CritAtk","CritDef","MoveSpeed","Skills","AIID","Avarta","Scale"]
        moncompact=[{k:x.get(k,"") for k in monfields} for x in monsters]
        for i,ch in chunk_rows(moncompact,2500): self.csvwrite(f"database/static/monsters/MONSTER_INDEX_{i+1:05d}_{i+len(ch):05d}.csv",ch,monfields)
        boss=[x for x in moncompact if x.get("Type")=="Boss"]
        for i,ch in chunk_rows(boss,1200): self.csvwrite(f"database/static/monsters/BOSS_INDEX_{i+1:04d}_{i+len(ch):04d}.csv",ch,monfields)
        namegroups=collections.defaultdict(list)
        for m in boss: namegroups[m.get("Name","")].append(m)
        bossnames=[]
        for name,xs in sorted(namegroups.items()):
            levels=[int(x["Level"]) for x in xs if str(x.get("Level","")).isdigit()]
            bossnames.append({"Name":name,"TemplateCount":len(xs),"MinLevel":min(levels) if levels else "","MaxLevel":max(levels) if levels else "","SampleIDs":";".join(x["ID"] for x in xs[:24]),"ResNames":";".join(sorted(set(x.get("ResName","") for x in xs if x.get("ResName","")))),"AIIDs":";".join(sorted(set(x.get("AIID","") for x in xs if x.get("AIID",""))))})
        self.csvwrite("database/static/monsters/BOSS_NAME_INDEX.csv",bossnames)

        equips=[]
        for x in self.load("Equips.xml"):
            a=dict(x.attrib); ba=[]; at=[]
            for c in x:
                if c.tag=="BaseAttribute": ba.append(dict(c.attrib))
                elif c.tag=="Attribute": at.append(dict(c.attrib))
            a["BaseAttributesJSON"]=json.dumps(ba,ensure_ascii=False,separators=(",",":")) if ba else ""; a["AttributesJSON"]=json.dumps(at,ensure_ascii=False,separators=(",",":")) if at else ""; a["IsWeaponPosition"]="true" if a.get("EquipPoint")=="0" else "false"; equips.append(a)
        eqfull=["ID","Name","Type","EquipPoint","IsWeaponPosition","Level","FactionID","BoundRule","BasePrice","SellPrice","Durability","Identifiable","Star","BuffID","SetID","DurationHour","BaseAttributesJSON","AttributesJSON","Description"]; eqidx=["ID","Name","Type","EquipPoint","Level","FactionID","BoundRule","SellPrice","Identifiable","Star","BuffID","SetID","DurationHour"]
        for i,ch in chunk_rows(equips,2500): self.csvwrite(f"database/static/equips/EQUIPS_{i+1:05d}_{i+len(ch):05d}.csv",ch,eqfull)
        for i,ch in chunk_rows(equips,4000): self.csvwrite(f"database/static/equips/EQUIP_INDEX_{i+1:05d}_{i+len(ch):05d}.csv",ch,eqidx)
        self.csvwrite("database/static/equips/WEAPON_INDEX.csv",[x for x in equips if x.get("EquipPoint")=="0"],eqidx)
        cnt=collections.Counter((x.get("EquipPoint",""),x.get("Type","")) for x in equips); self.csvwrite("database/static/equips/EQUIP_POSITION_TYPE_COUNTS.csv",[{"EquipPoint":p,"Type":t,"Count":n,"IsWeaponPosition":str(p=="0").lower()} for (p,t),n in sorted(cnt.items())])

        for name,outname in [("Activities.xml","ACTIVITIES"),("GrowPoints.xml","GROW_POINTS"),("GuildTask.xml","GUILD_TASKS")]: self.csvwrite(f"database/static/tasks/{outname}.csv",[dict(x.attrib)|({"ChildrenJSON":children_json(x)} if list(x) else {}) for x in self.load(name)])
        pet_rows=[dict(x.attrib)|({"ChildrenJSON":children_json(x)} if list(x) else {}) for x in self.load("Pets.xml")]
        for i,ch in chunk_rows(pet_rows,1500): self.csvwrite(f"database/static/pets/PETS_{i+1:05d}_{i+len(ch):05d}.csv",ch)
        petidx=["ID","Name","ResName","Type","Level","FactionID","SkillID","AttackType","Quality"]
        for i,ch in chunk_rows(pet_rows,2000): self.csvwrite(f"database/static/pets/PET_INDEX_{i+1:05d}_{i+len(ch):05d}.csv",ch,petidx)
        spirit_rows=[dict(x.attrib)|({"ChildrenJSON":children_json(x)} if list(x) else {}) for x in self.load("Spirits.xml")]
        for i,ch in chunk_rows(spirit_rows,1000): self.csvwrite(f"database/static/pets/SPIRITS_{i+1:05d}_{i+len(ch):05d}.csv",ch)
        self.csvwrite("database/static/pets/SPIRIT_INDEX_00001_01889.csv",spirit_rows,["ID","Name","ResName","Type","Level","SkillID","Quality"])
        for name,outname in [("PetFeatures.xml","PET_FEATURES"),("PetEquips.xml","PET_EQUIPS"),("PetEquipSets.xml","PET_EQUIP_SETS"),("SpiritFeatures.xml","SPIRIT_FEATURES")]: self.csvwrite(f"database/static/pets/{outname}.csv",[dict(x.attrib)|({"ChildrenJSON":children_json(x)} if list(x) else {}) for x in self.load(name)])
        self.csvwrite("database/PC_INPUT_KEY_BINDINGS.csv",[dict(x.attrib)|({"ChildrenJSON":children_json(x)} if list(x) else {}) for x in self.load("PCInputKeyBinding.xml")])
        manifest=[]
        for p in sorted(self.generated):
            rel=p.relative_to(self.repo).as_posix(); rows=""
            if p.suffix.lower()==".csv":
                with p.open("r",encoding="utf-8-sig",errors="ignore") as f: rows=max(sum(1 for _ in f)-1,0)
            manifest.append({"RepoPath":rel,"Bytes":p.stat().st_size,"Rows":rows})
        self.csvwrite("database/TOOL_DATA_MATERIALIZATION_MANIFEST.csv",manifest)
        return manifest


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--config",required=True,type=Path); ap.add_argument("--repo-root",default=Path("."),type=Path); args=ap.parse_args(); repo=args.repo_root.resolve(); config=(repo/args.config).resolve() if not args.config.is_absolute() else args.config.resolve(); dec=fg_decrypt(config.read_bytes())
    with tempfile.TemporaryDirectory(prefix="tl_config_") as td:
        td=Path(td); cabdir=td/"cab"; xmldir=td/"xml"; written=extract_unityfs_bytes(dec,cabdir)
        for cab in [p for p in written if p.is_file()]:
            try: extract_config_xml_from_cab(cab,xmldir)
            except Exception: pass
        xmls=list(xmldir.glob("*.xml"))
        if len(xmls)<70: raise RuntimeError(f"Recovered only {len(xmls)} Config XML files")
        manifest=Builder(xmldir,repo).build(); print(f"Recovered {len(xmls)} Config XML tables"); print(f"Generated {len(manifest)+1} database files"); print(f"Source: {config}")


if __name__=="__main__":
    main()
