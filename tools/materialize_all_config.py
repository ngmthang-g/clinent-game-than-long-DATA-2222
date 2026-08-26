#!/usr/bin/env python3
"""Materialize a structurally-lossless fallback database for every Config XML TextAsset.

This complements tools/materialize_tool_data.py. The tool-first database remains the preferred
lookup path. This script creates database/config_full as the last-resort static fallback so a
future AI can inspect any frozen Config table without decrypting/reparsing Config.unity3d again.
"""
from __future__ import annotations
import argparse, csv, json, lzma, struct, tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
try:
    import lz4.block
except ImportError as exc:
    raise SystemExit("Missing dependency: pip install lz4") from exc

def _legacy(buf: bytearray, decrypt: bool=True):
    if len(buf)<128:return
    delta=-0x0F if decrypt else 0x0F; n=len(buf)
    for i in range(128):
        j=n-1-i; a,b=buf[i],buf[j]; buf[i]=(b+delta)&255; buf[j]=(a+delta)&255

def _valid(b): return b.startswith(b"UnityFS\0") or b.startswith(b"UnityRaw\0") or b.startswith(b"UnityWeb\0")
def fg_decrypt(data:bytes)->bytes:
    b=bytearray(data); n=len(b)
    if n<128 or _valid(b):return bytes(b)
    _legacy(b,True)
    if _valid(b):return bytes(b)
    _legacy(b,False)
    x=(n^0x9E3779B9)&0xffffffff; x^=(x<<13)&0xffffffff; x&=0xffffffff; x^=x>>17; x&=0xffffffff; x^=(x<<5)&0xffffffff; x&=0xffffffff
    count=min(max((x&0x7f)+1,1),n//2); delta=((x>>7)&0x7f)+1
    if delta==0x0f and count!=0x80: delta=0x11
    for i in range(count):
        j=n-1-i; a,bb=b[i],b[j]; b[i]=(bb-delta)&255; b[j]=(a-delta)&255
    if not _valid(b):raise ValueError("FG decrypt did not produce Unity bundle")
    return bytes(b)
def _cstr(b,p):
    j=b.index(0,p); return b[p:j],j+1
def _decomp(data,ctype,usize):
    c=ctype&0x3f
    if c==0:return data
    if c in (2,3):return lz4.block.decompress(data,uncompressed_size=usize)
    if c==1:
        prop=data[0]; lc=prop%9; rem=prop//9; lp=rem%5; pb=rem//5; ds=int.from_bytes(data[1:5],"little")
        return lzma.decompress(data[5:],format=lzma.FORMAT_RAW,filters=[{"id":lzma.FILTER_LZMA1,"dict_size":ds,"lc":lc,"lp":lp,"pb":pb}])
    raise ValueError(c)
def extract_unityfs_bytes(b:bytes,outdir:Path):
    p=0; sig,p=_cstr(b,p)
    if sig not in (b"UnityFS",b"UnityRaw",b"UnityWeb"):raise ValueError(sig)
    p+=4; _,p=_cstr(b,p); _,p=_cstr(b,p); p+=8; cs,us,flags=struct.unpack_from(">III",b,p); p+=12
    if flags&0x200:p=(p+15)&~15
    if flags&0x80: comp=b[len(b)-cs:]; data_start=p
    else: comp=b[p:p+cs]; data_start=p+cs
    if flags&0x200:data_start=(data_start+15)&~15
    info=_decomp(comp,flags,us); q=16; n=struct.unpack_from(">I",info,q)[0];q+=4; blocks=[]
    for _ in range(n):u,c,f=struct.unpack_from(">IIH",info,q);q+=10;blocks.append((u,c,f))
    nd=struct.unpack_from(">I",info,q)[0];q+=4; dirs=[]
    for _ in range(nd):
        off,sz,fl=struct.unpack_from(">QQI",info,q);q+=20;name,q=_cstr(info,q);dirs.append((off,sz,fl,name.decode("utf-8","replace")))
    dp=data_start; body=[]
    for u,c,f in blocks:body.append(_decomp(b[dp:dp+c],f,u));dp+=c
    body=b"".join(body);outdir.mkdir(parents=True,exist_ok=True); written=[]
    for off,sz,_,name in dirs:
        x=outdir/name;x.parent.mkdir(parents=True,exist_ok=True);x.write_bytes(body[off:off+sz]);written.append(x)
    return written
XML_SIG=b"<?xml version=\"1.0\" encoding=\"utf-8\"?>"
def extract_config_xml_from_cab(cab:Path,outdir:Path):
    b=cab.read_bytes();outdir.mkdir(parents=True,exist_ok=True);found={};pos=0
    while True:
        i=b.find(XML_SIG,pos)
        if i<0:break
        if i<4:pos=i+1;continue
        L=struct.unpack_from("<I",b,i-4)[0]
        if not (0<L and i+L<=len(b)):pos=i+1;continue
        j=i-4;cands=[]
        for s in range(max(0,j-260),j-3):
            ln=struct.unpack_from("<I",b,s)[0]
            if 0<ln<=128 and ((s+4+ln+3)&~3)==j:
                raw=b[s+4:s+4+ln]
                try:name=raw.decode("utf-8")
                except UnicodeDecodeError:continue
                if name and all(ch.isprintable() for ch in name):cands.append(name)
        if cands:
            name=cands[-1];p=outdir/f"{name}.xml";p.write_bytes(b[i:i+L]);found[name]=p
        pos=i+1
    return found

def node_obj(x:ET.Element):
    d={"Tag":x.tag,"Attributes":dict(x.attrib)}; text=(x.text or "").strip()
    if text:d["Text"]=text
    if list(x):d["Children"]=[node_obj(c) for c in x]
    return d

def write_csv(path:Path,rows:list[dict],fields:list[str]):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");w.writeheader();w.writerows(rows)

def materialize(xml_dir:Path,repo:Path,chunk_size:int=1500):
    root=repo/"database/config_full"; root.mkdir(parents=True,exist_ok=True); generated=[]; catalog=[]
    xmls=sorted(xml_dir.glob("*.xml"),key=lambda p:p.stem.lower())
    for xp in xmls:
        r=ET.parse(xp).getroot(); elems=list(r); attrs=[];seen=set();nested=False;text_nodes=0;max_depth=1
        def scan(n,depth=1):
            nonlocal nested,text_nodes,max_depth
            max_depth=max(max_depth,depth)
            if (n.text or "").strip():text_nodes+=1
            if list(n):nested=True
            for c in n:scan(c,depth+1)
        for e in elems:
            for k in e.attrib:
                if k not in seen:seen.add(k);attrs.append(k)
            scan(e)
        rows=[]
        for idx,e in enumerate(elems,1):
            row={"RowIndex":idx,"Tag":e.tag,**dict(e.attrib),"Text":(e.text or "").strip()}
            row["ChildrenJSON"]=json.dumps([node_obj(c) for c in e],ensure_ascii=False,separators=(",",":")) if list(e) else ""; rows.append(row)
        fields=["RowIndex","Tag"]+attrs+["Text","ChildrenJSON"]; chunks=[]; table=xp.stem
        for start in range(0,len(rows),chunk_size):
            ch=rows[start:start+chunk_size];fn=f"ROWS_{start+1:05d}_{start+len(ch):05d}.csv";p=root/table/fn;write_csv(p,ch,fields);generated.append(p);chunks.append(fn)
        catalog.append({"Table":table,"SourceXml":xp.name,"RootTag":r.tag,"RootAttributesJSON":json.dumps(dict(r.attrib),ensure_ascii=False,separators=(",",":")),"RowCount":len(rows),"DirectAttributeCount":len(attrs),"DirectAttributeNames":"|".join(attrs),"HasNestedChildren":str(nested).lower(),"NonWhitespaceTextNodeCount":text_nodes,"MaxDepth":max_depth,"ChunkCount":len(chunks),"ChunkFiles":"|".join(chunks)})
    cat=root/"CONFIG_FULL_CATALOG.csv";write_csv(cat,catalog,["Table","SourceXml","RootTag","RootAttributesJSON","RowCount","DirectAttributeCount","DirectAttributeNames","HasNestedChildren","NonWhitespaceTextNodeCount","MaxDepth","ChunkCount","ChunkFiles"]);generated.append(cat)
    manifest=[]
    for p in sorted(generated):
        with p.open("r",encoding="utf-8-sig",errors="ignore") as f:cnt=max(sum(1 for _ in f)-1,0)
        manifest.append({"RepoPath":p.relative_to(repo).as_posix(),"Bytes":p.stat().st_size,"Rows":cnt})
    man=root/"CONFIG_FULL_MANIFEST.csv";write_csv(man,manifest,["RepoPath","Bytes","Rows"]);generated.append(man)
    return catalog,generated

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--config",required=True,type=Path);ap.add_argument("--repo-root",default=Path("."),type=Path);ap.add_argument("--chunk-size",default=1500,type=int);a=ap.parse_args()
    repo=a.repo_root.resolve(); config=(repo/a.config).resolve() if not a.config.is_absolute() else a.config.resolve();dec=fg_decrypt(config.read_bytes())
    with tempfile.TemporaryDirectory(prefix="tl_allcfg_") as td:
        td=Path(td);cab=td/"cab";xml=td/"xml";written=extract_unityfs_bytes(dec,cab)
        for p in written:
            if p.is_file():
                try:extract_config_xml_from_cab(p,xml)
                except Exception:pass
        xmls=list(xml.glob("*.xml"))
        if len(xmls)!=75: raise RuntimeError(f"Expected 75 Config XML tables, recovered {len(xmls)}")
        catalog,generated=materialize(xml,repo,a.chunk_size);print(f"Recovered {len(xmls)} Config XML tables; materialized {len(catalog)} tables into {len(generated)} files")
if __name__=="__main__":main()
