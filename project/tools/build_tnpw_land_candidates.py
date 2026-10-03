#!/usr/bin/python3
from pathlib import Path
import pcbnew as k,json,hashlib
B=Path(__file__).resolve().parents[1];D=B/'cad/verified-footprints/passive-candidates';L=D/'CMK230_Passive_Candidates.pretty';L.mkdir(parents=True,exist_ok=True)
specs=[('IPC7351',.40,.55,.60,1.50),('IEC61188',.55,.35,.55,1.25)];proof=[]
for variant,g,y,x,z in specs:
 name='Vishay_TNPW0402_'+variant+'_SourceLand_PROCESS_CANDIDATE';f=k.FOOTPRINT(None);f.SetFPID(k.LIB_ID('CMK230_Passive_Candidates',name));f.SetReference('R**');f.SetValue(name);f.SetAttributes(k.FP_SMD)
 f.Reference().SetLayer(k.F_Fab);f.Reference().SetPosition(k.VECTOR2I(0,k.FromMM(-1))); f.Value().SetVisible(False)
 for i,sgn in [(1,-1),(2,1)]:
  p=k.PAD(f);p.SetNumber(str(i));p.SetAttribute(k.PAD_ATTRIB_SMD);p.SetShape(k.PAD_SHAPE_RECT);p.SetSize(k.VECTOR2I(k.FromMM(y),k.FromMM(x)));p.SetPosition(k.VECTOR2I(k.FromMM(sgn*(g+y)/2),0));layers=k.LSET();[layers.AddLayer(z) for z in [k.F_Cu,k.F_Paste,k.F_Mask]];p.SetLayerSet(layers);p.SetLocalSolderMaskMargin(k.FromMM(.05));f.Add(p)
 # Courtyard includes mask extension and .25mm per-side engineering clearance.
 w=z+.60;h=max(x+.60,.55+.50)
 for a,b in [((-w/2,-h/2),(w/2,-h/2)),((w/2,-h/2),(w/2,h/2)),((w/2,h/2),(-w/2,h/2)),((-w/2,h/2),(-w/2,-h/2))]:
  q=k.PCB_SHAPE();q.SetShape(k.SHAPE_T_SEGMENT);q.SetStart(k.VECTOR2I(k.FromMM(a[0]),k.FromMM(a[1])));q.SetEnd(k.VECTOR2I(k.FromMM(b[0]),k.FromMM(b[1])));q.SetLayer(k.F_CrtYd);q.SetWidth(k.FromMM(.05));f.Add(q)
 k.PCB_IO_MGR.PluginFind(k.PCB_IO_MGR.KICAD_SEXP).FootprintSave(str(L),f)
 p=L/(name+'.kicad_mod');r=k.PCB_IO_MGR.PluginFind(k.PCB_IO_MGR.KICAD_SEXP).FootprintLoad(str(L),name);pads=list(r.Pads());assert len(pads)==2
 xs=sorted(k.ToMM(p.GetPosition().x) for p in pads);assert abs(xs[1]-xs[0]-(g+y))<1e-7
 assert all(abs(k.ToMM(p.GetSize().x)-y)<1e-7 and abs(k.ToMM(p.GetSize().y)-x)<1e-7 for p in pads)
 assert abs((xs[1]+y/2)-(xs[0]-y/2)-z)<1e-7
 proof.append({'footprint':name,'copper_pad_xy_mm':[y,x],'inner_gap_mm':g,'outer_span_mm':z,'courtyard_xy_mm':[w,h],'mask_expansion_mm':.05,'paste':'1:1 default, assembly unqualified','sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(D/'source-land-validation.json').write_text(json.dumps({'source':'https://www.vishay.com/doc?28950','revision':'12-Jul-2022','page':1,'exact_series_link':'https://www.vishay.com/docs/28758/tnpw_e3.pdf Soldering Recommendations','status':'SOURCE_COPPER_VERIFIED_PROCESS_CANDIDATES','candidates':proof},indent=2));print('PASS 2 source-land variants; copper, spacing and saved footprint checks')
