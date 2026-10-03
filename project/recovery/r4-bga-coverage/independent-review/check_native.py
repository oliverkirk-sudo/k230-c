#!/usr/bin/python3
"""Load actual R4 footprints with KiCad; write audit-only results and temporary CAM."""
from pathlib import Path
import collections, hashlib, json, os, re, subprocess, tempfile
import pcbnew

HERE=Path(__file__).resolve().parent
PROJECT=HERE.parent/'reconstruction-r4/project'
LIB=PROJECT/'cad/recovery-bga-candidates/CMK230_Recovery_BGA_Candidates.pretty'
checks=[]
def ck(name,ok,details=None):
    checks.append({'check':name,'pass':bool(ok),**({'details':details} if details is not None else {})})
def xy(v): return [round(pcbnew.ToMM(v.x),6),round(pcbnew.ToMM(v.y),6)]
def layer_names(pad): return [pcbnew.LayerName(x) for x in pad.GetLayerSet().Seq()]

records={}
for name in ['K230_390_NSMD027_ENGINEERING_ONLY','Micron_FW200_NSMD030_ENGINEERING_ONLY','MTFC16GAPALBH_AAT_BH153_NSMD030_ENGINEERING_ONLY']:
    fp=pcbnew.FootprintLoad(str(LIB),name)
    assert fp
    pads=list(fp.Pads())
    records[name]={'total_pad_objects':len(pads),'copper_pad_count':sum(p.IsOnLayer(pcbnew.F_Cu) for p in pads),
        'paste_only_count':sum(layer_names(p)==['F.Paste'] for p in pads),'front_footprint':fp.GetLayer()==pcbnew.F_Cu,
        'copper_coordinate_sha256':hashlib.sha256(json.dumps({p.GetNumber():xy(p.GetPosition()) for p in pads if p.IsOnLayer(pcbnew.F_Cu)},sort_keys=True).encode()).hexdigest()}

fw=pcbnew.FootprintLoad(str(LIB),'Micron_FW200_NSMD030_ENGINEERING_ONLY')
board=pcbnew.BOARD();board.SetCopperLayerCount(6);board.Add(fw)
pads=list(fw.Pads());paste=[p for p in pads if layer_names(p)==['F.Paste']];copper=[p for p in pads if p.IsOnLayer(pcbnew.F_Cu)]
ck('Native FW200 loads 200 numbered Cu/Mask pads and 200 unnumbered paste-only apertures',len(copper)==200 and len(paste)==200 and len(pads)==400 and all(p.GetNumber() for p in copper) and all(not p.GetNumber() for p in paste))
ck('Native FW200 has exact front-only layer sets',all(layer_names(p)==['F.Cu','F.Mask'] for p in copper) and all(layer_names(p)==['F.Paste'] for p in paste))
ck('Native FW200 all explicit diameters 0.30 mm',all(xy(p.GetSize())==[.3,.3] for p in pads))
ck('Native FW200 per-pad mask expansion 0.05 mm',all(p.GetLocalSolderMaskMargin()==pcbnew.FromMM(.05) for p in copper))
for margin,ratio in [(0,0),(-.02,0),(0,-.1)]:
    board.GetDesignSettings().m_SolderPasteMargin=pcbnew.FromMM(margin)
    board.GetDesignSettings().m_SolderPasteMarginRatio=ratio
    ck('Paste-only effective margins with global settings '+str((margin,ratio)),all(xy(p.GetSolderPasteMargin(pcbnew.F_Paste))==[0,0] for p in paste))
board.GetDesignSettings().m_SolderPasteMargin=0;board.GetDesignSettings().m_SolderPasteMarginRatio=0
fw.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(15),pcbnew.FromMM(15)))
cam={}
with tempfile.TemporaryDirectory(prefix='r4-bga-native-') as tmp:
    tmp=Path(tmp);boardfile=tmp/'FW200_GEOMETRY_ONLY.kicad_pcb';pcbnew.SaveBoard(str(boardfile),board)
    reread=pcbnew.LoadBoard(str(boardfile));ck('Native serialized round-trip retains 400 objects',sum(len(list(f.Pads())) for f in reread.GetFootprints())==400)
    env=dict(os.environ)
    for key,sub in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data')]:
        env[key]=str(tmp/sub)
    command=['kicad-cli','pcb','export','gerbers','--layers','F.Cu,F.Mask,F.Paste','--output',str(tmp/'cam'),str(boardfile)]
    result=subprocess.run(command,env=env,capture_output=True,text=True)
    ck('Native Gerber export succeeds',result.returncode==0,result.stdout.strip())
    expected={(round(pcbnew.ToMM(p.GetPosition().x)-15,6),round(pcbnew.ToMM(p.GetPosition().y)-15,6)) for p in copper}
    for layer,ext,diameter in [('F_Cu','gtl',.3),('F_Mask','gts',.4),('F_Paste','gtp',.3)]:
        f=tmp/'cam'/('FW200_GEOMETRY_ONLY-'+layer+'.'+ext)
        text=f.read_text();aps={int(n):(s,float(v)) for n,s,v in re.findall(r'%ADD(\d+)(C),([.\d]+)\*%',text)}
        active=None;flashes=[]
        for line in text.splitlines():
            m=re.fullmatch(r'D(\d+)\*',line)
            if m: active=int(m[1]);continue
            m=re.fullmatch(r'X(-?\d+)Y(-?\d+)D03\*',line)
            if m: flashes.append((round(int(m[1])/1e6-15,6),round(-int(m[2])/1e6-15,6),aps[active]))
        ck(layer+' CAM has exact 200 centers and declared aperture diameter',len(flashes)==200 and {(x,y) for x,y,a in flashes}==expected and all(a==('C',diameter) for x,y,a in flashes))
        cam[layer]={'flashes':len(flashes),'unique_centers':len({(x,y) for x,y,a in flashes}),'diameter_mm':diameter,'nominal_verified':all(a==('C',diameter) for x,y,a in flashes)}

payload={'kicad_version':pcbnew.GetBuildVersion(),'checks':checks,'native_footprints':records,'temporary_CAM':cam,'scope':'Native footprint/CAM geometry only. Temporary QA board and Gerbers deleted after verification; no module PCB or fabrication files produced.'}
(HERE/'native-results.json').write_text(json.dumps(payload,indent=2)+'\n')
print(json.dumps({'checks':len(checks),'failures':[c for c in checks if not c['pass']],'CAM':cam}))
