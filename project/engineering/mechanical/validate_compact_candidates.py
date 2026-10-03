#!/usr/bin/python3
"""Independent native KiCad tests; expected geometry from TI drawings, not builder import."""
from pathlib import Path
import pcbnew as k
import json,math,itertools,hashlib
R=Path(__file__).resolve().parents[2];M=R/'engineering/mechanical';O=R/'cad/verified-footprints/compact-options';L=O/'CMK230_Compact_Candidates.pretty';checks=0

def near(a,b):
 global checks
 checks+=1;assert abs(a-b)<2e-6,(a,b)
def arr(p):return [k.ToMM(z) for z in [p.GetPosition().x,p.GetPosition().y,p.GetSize().x,p.GetSize().y]]
def close(a,b):
 for aa,bb in zip(a,b):near(aa,bb)
spec={'DRL':{'ref':'U301','position':[5,5],'court':[2.8,2.5],'maxbodyflash':[1.6,2.0],'pads':{'1':[-.74,-.5,.67,.3],'2':[-.74,0,.67,.3],'3':[-.74,.5,.67,.3],'4':[.74,.5,.67,.3],'5':[.74,-.5,.67,.3]}},'DCK':{'ref':'U302','position':[14,5],'court':[3.8,3.2],'maxbodyflash':[1.9,2.65],'pads':{'1':[-1.1,-.65,.95,.4],'2':[-1.1,0,.95,.4],'3':[-1.1,.65,.95,.4],'4':[1.1,.65,.95,.4],'5':[1.1,-.65,.95,.4]}},'DRV':{'ref':'U303','position':[23,5],'court':[3,2.6],'maxbodyflash':[2.1,2.1],'pads':{'1':[-.975,-.65,.45,.3],'2':[-.975,0,.45,.3],'3':[-.975,.65,.45,.3],'4':[.975,.65,.45,.3],'5':[.975,0,.45,.3],'6':[.975,-.65,.45,.3],'7':[0,0,1,1.6]}}}
spec['DRL6']={'ref':'U304','position':[5,15],'court':[2.8,2.5],'maxbodyflash':[1.6,2.0],'pads':{'1':[-.74,-.5,.67,.3],'2':[-.74,0,.67,.3],'3':[-.74,.5,.67,.3],'4':[.74,.5,.67,.3],'5':[.74,0,.67,.3],'6':[.74,-.5,.67,.3]}}
report={'scope':'Package candidates only; no integrated netlist changed','coordinate_frame':'Top/component-side, +X right,+Y down, origin body center','status':'PASS','packages':{}};board=k.BOARD()
for tag,s in spec.items():
 path=next(p for p in L.glob('*.kicad_mod') if ({'DRL':'DRL0005','DRL6':'DRL0006'}.get(tag,tag)) in p.stem);fp=k.FootprintLoad(str(L),path.stem);assert fp
 allp=list(fp.Pads());cu={p.GetNumber():p for p in allp if p.IsOnLayer(k.F_Cu)};ma=[p for p in allp if p.IsOnLayer(k.F_Mask)];pa=[p for p in allp if p.IsOnLayer(k.F_Paste)]
 assert set(cu)==set(s['pads']);assert len(ma)==len(cu);assert len(pa)==(8 if tag=='DRV' else len(cu))
 for n,e in s['pads'].items():
  p=cu[n];close(arr(p),e);near(k.ToMM(p.GetRoundRectCornerRadius()),.05);assert not p.IsOnLayer(k.F_Mask)
  mask=next(q for q in ma if abs(arr(q)[0]-e[0])<1e-6 and abs(arr(q)[1]-e[1])<1e-6)
  close(arr(mask),[e[0],e[1],e[2]+.1,e[3]+.1]);near(k.ToMM(mask.GetRoundRectCornerRadius()),.1)
  assert mask.GetLocalSolderMaskMargin()==0;assert not mask.GetNumber();assert not mask.IsOnCopperLayer()
  if n!='7':assert p.IsOnLayer(k.F_Paste)
  else:assert not p.IsOnLayer(k.F_Paste)
 for paste in pa:
  assert paste.GetLocalSolderPasteMargin()==0;near(paste.GetLocalSolderPasteMarginRatio(),0);near(k.ToMM(paste.GetRoundRectCornerRadius()),.05)
 if tag=='DRV':
  pp=[p for p in pa if not p.GetNumber()];assert len(pp)==2
  close(arr(min(pp,key=lambda p:p.GetPosition().y)),[0,-.45,1,.7]);close(arr(max(pp,key=lambda p:p.GetPosition().y)),[0,.45,1,.7]);assert all(not p.IsOnCopperLayer() for p in pp)
 c=[g for g in fp.GraphicalItems() if g.GetLayer()==k.F_CrtYd];assert len(c)==1
 cw,ch=s['court'];close([k.ToMM(c[0].GetStart().x),k.ToMM(c[0].GetStart().y),k.ToMM(c[0].GetEnd().x),k.ToMM(c[0].GetEnd().y)],[-cw/2,-ch/2,cw/2,ch/2])
 assert cw>=s['maxbodyflash'][0]+.5 and ch>=s['maxbodyflash'][1]+.5
 for p in list(cu.values())+ma:
  x,y,w,h=arr(p);assert abs(x)+w/2<=cw/2-.25+1e-8;assert abs(y)+h/2<=ch/2-.25+1e-8
 gap=100
 for a,b in itertools.combinations(cu.values(),2):
  x,y,w,h=arr(a);xx,yy,ww,hh=arr(b);gap=min(gap,math.hypot(max(0,abs(x-xx)-(w+ww)/2),max(0,abs(y-yy)-(h+hh)/2)))
 report['packages'][tag]={'footprint':path.stem,'copper_count':len(cu),'mask_count':len(ma),'paste_count':len(pa),'courtyard_mm':s['court'],'courtyard_mm2':round(cw*ch,6),'minimum_nominal_copper_gap_mm':round(gap,6),'minimum_nominal_mask_web_mm':round(gap-.1,6),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
 fp.SetReference(s['ref']);fp.SetValue(tag+'_GEOMETRY_QA');fp.SetFPID(k.LIB_ID('CMK230_Compact_Candidates',path.stem));fp.SetPosition(k.VECTOR2I(*(k.FromMM(v) for v in s['position'])));board.Add(fp)
 for n,p in cu.items():net=k.NETINFO_ITEM(board,s['ref']+'_'+n);board.Add(net);p.SetNet(net)
for start,end in [((1,1),(27,1)),((27,1),(27,20)),((27,20),(1,20)),((1,20),(1,1))]:
 p=k.PCB_SHAPE();p.SetShape(k.SHAPE_T_SEGMENT);p.SetLayer(k.Edge_Cuts);p.SetStart(k.VECTOR2I(*(k.FromMM(v) for v in start)));p.SetEnd(k.VECTOR2I(*(k.FromMM(v) for v in end)));p.SetWidth(k.FromMM(.05));board.Add(p)
k.SaveBoard(str(O/'Compact_Package_Geometry_QA_ONLY.kicad_pcb'),board)
(O/'Compact_Package_Geometry_QA_ONLY.kicad_pro').write_text((R/'cad/verified-footprints/Footprint_Geometry_QA_ONLY.kicad_pro').read_text().replace('Footprint_Geometry_QA_ONLY','Compact_Package_Geometry_QA_ONLY'))
report['numeric_assertions_passed']=checks
(M/'compact-footprint-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
# Preserve precise comparison rather than treating matching generic names as matching lands.
comp=[]
for li,name in [('Package_TO_SOT_SMD.pretty','SOT-353_SC-70-5'),('Package_TO_SOT_SMD.pretty','SOT-553'),('Package_DFN_QFN.pretty','DFN-6-1EP_2x2mm_P0.65mm_EP1x1.6mm')]:
 fp=k.FootprintLoad('/usr/share/kicad/footprints/'+li,name);comp.append({'name':li+':'+name,'description':fp.GetLibDescription(),'pads':[{'number':p.GetNumber(),'xywh':arr(p),'angle':p.GetOrientationDegrees()} for p in fp.Pads()]})
(M/'compact-installed-library-comparison.json').write_text(json.dumps(comp,indent=2)+'\n')
