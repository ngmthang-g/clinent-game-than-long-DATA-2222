from pathlib import Path
import struct, subprocess, sys
import UnityPy

DLL=Path("Game/Thần Long  Mobile_Data/Plugins/x86_64/FGClientTool_Windows.dll")
ROOT=Path("Game/Thần Long  Mobile_Data/StreamingAssets")

def deps():
    try:
        import pefile, unicorn
    except Exception:
        subprocess.check_call([sys.executable,"-m","pip","install","--disable-pip-version-check","pefile","unicorn"])

def au(v,a=0x1000): return (v+a-1)&~(a-1)
def dec(raw):
    deps(); import pefile
    from unicorn import Uc,UC_ARCH_X86,UC_MODE_64
    from unicorn.x86_const import UC_X86_REG_RCX,UC_X86_REG_RDX,UC_X86_REG_RSP
    pe=pefile.PE(str(DLL)); base=int(pe.OPTIONAL_HEADER.ImageBase); size=au(int(pe.OPTIONAL_HEADER.SizeOfImage))
    rva=next(int(s.address) for s in pe.DIRECTORY_ENTRY_EXPORT.symbols if s.name==b"FG_Decrypt")
    u=Uc(UC_ARCH_X86,UC_MODE_64); u.mem_map(base,size); b=DLL.read_bytes(); u.mem_write(base,b[:int(pe.OPTIONAL_HEADER.SizeOfHeaders)])
    for s in pe.sections:
        d=s.get_data()
        if d:u.mem_write(base+int(s.VirtualAddress),d)
    da=0x10000000; u.mem_map(da,au(len(raw)+0x1000));u.mem_write(da,raw)
    st=0x30000000;u.mem_map(st,0x20000);sen=0x40000000;u.mem_map(sen,0x1000);u.mem_write(sen,b"\xcc")
    rsp=((st+0x20000-0x200)&~0xf)-8;u.mem_write(rsp,struct.pack('<Q',sen));u.reg_write(UC_X86_REG_RSP,rsp);u.reg_write(UC_X86_REG_RCX,da);u.reg_write(UC_X86_REG_RDX,len(raw));u.emu_start(base+rva,sen,timeout=20_000_000,count=200_000_000)
    return bytes(u.mem_read(da,len(raw)))
def decode(x):
    if isinstance(x,str):return x
    for e in ('utf-8-sig','utf-8','utf-16-le','latin-1'):
        try:return x.decode(e)
        except:pass
    return str(x)
def load(p):
    raw=dec(p.read_bytes()); q=Path(p.name+'.dec');q.write_bytes(raw); env=UnityPy.load(str(q));o={}
    for obj in env.objects:
        if obj.type.name=='TextAsset':
            d=obj.read();o[getattr(d,'m_Name','') or '']=decode(getattr(d,'m_Script',b''))
    return o

def contexts(name,text,needles,r=14):
    ls=text.splitlines();hits=[i for i,l in enumerate(ls) if any(n in l for n in needles)]
    if not hits:return
    print('\n'+'='*140);print('ASSET='+name);print('='*140);shown=set()
    for i in hits:
        for j in range(max(0,i-r),min(len(ls),i+r+1)):
            if j not in shown: print(f'{j+1:05d}: {ls[j]}');shown.add(j)
        print('...')
def main():
    ia=load(ROOT/'Interface.unity3d')
    needles=['C_MiniEventBoardAction','LoadFuBenScenariosData','FuBenScenarios','action.Type == "Kill"','action.Type == "WaitMiniBox"','action.Type == "Collect"','action.Type == "UsePortal"']
    for n,t in sorted(ia.items()): contexts(n,t,needles)
    return 0
if __name__=='__main__':raise SystemExit(main())
