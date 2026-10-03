#!/usr/bin/python3
"""Native KiCad checks; literal geometry independently matches the two drawings."""
from pathlib import Path
import hashlib,itertools,json,math,xml.etree.ElementTree as ET
import pcbnew as k
ROOT=Path(__file__).resolve().parents[2];M=ROOT/'engineering/mechanical'
O=ROOT/'cad/verified-footprints/nexperia-standard-candidate'
LIBNAME='CMK230_Nexperia_Standard_Candidates';L=O/(LIBNAME+'.pretty')
CASES=[('Nexperia_SOT353-1_AUP1G17_06_DrawingVerified_CANDIDATE',
        {'1':[-.975,-.65],'2':[-.975,0],'3':[-.975,.65],'4':[.975,.65],'5':[.975,-.65]}),
       ('Nexperia_SOT363-2_AUP1G97_DrawingVerified_CANDIDATE',
        {'1':[-.975,-.65],'2':[-.975,0],'3':[-.975,.65],'4':[.975,.65],'5':[.975,0],'6':[.975,-.65]})]
checks=0
def check(test,detail):
 global checks
 checks+=1
 assert test,detail
def near(a,b):check(abs(a-b)<2e-6,(a,b))
def geom(p):return [k.ToMM(v)for v in [p.GetPosition().x,p.GetPosition().y,p.GetSize().x,p.GetSize().y]]
board=k.BOARD();report={'status':'PASS','scope':'Isolated drawing geometry only; no assembly qualification','footprints':[]}
for index,(name,expected)in enumerate(CASES):
 fp=k.FootprintLoad(str(L),name);check(bool(fp),name);pads=list(fp.Pads())
 cu={p.GetNumber():p for p in pads if p.IsOnLayer(k.F_Cu)};check(set(cu)==set(expected),'exact numbered copper pads')
 rr={'name':name,'layers':{},'sha256':hashlib.sha256((L/(name+'.kicad_mod')).read_bytes()).hexdigest()}
 for layer,label,size in [(k.F_Cu,'copper',[.75,.4]),(k.F_Mask,'mask',[.85,.5]),(k.F_Paste,'paste',[.65,.3])]:
  pp=[p for p in pads if p.IsOnLayer(layer)];check(len(pp)==len(expected),'aperture count')
  for number,xy in expected.items():
   matches=[p for p in pp if abs(geom(p)[0]-xy[0])<1e-6 and abs(geom(p)[1]-xy[1])<1e-6]
   check(len(matches)==1,'one aperture at each center');p=matches[0]
   for a,b in zip(geom(p),xy+size):near(a,b)
   check(p.GetShape()==k.PAD_SHAPE_RECT,'source rectangular geometry')
   check(p.GetNumber()==number if layer==k.F_Cu else p.GetNumber()=='','numbered copper only')
   check(len([z for z in (k.F_Cu,k.F_Mask,k.F_Paste)if p.IsOnLayer(z)])==1,'single explicit layer')
   if layer==k.F_Mask:near(p.GetLocalSolderMaskMargin(),0)
   if layer==k.F_Paste:near(p.GetLocalSolderPasteMargin(),0);near(p.GetLocalSolderPasteMarginRatio(),0)
  gap=min(math.hypot(max(0,abs(geom(a)[0]-geom(b)[0])-(geom(a)[2]+geom(b)[2])/2),max(0,abs(geom(a)[1]-geom(b)[1])-(geom(a)[3]+geom(b)[3])/2))for a,b in itertools.combinations(pp,2))
  near(gap,{'copper':.25,'mask':.15,'paste':.35}[label]);rr['layers'][label]={'count':len(pp),'minimum_gap_mm':round(gap,6)}
 courtyard=[g for g in fp.GraphicalItems()if g.GetLayer()==k.F_CrtYd];check(len(courtyard)==1,'single rectangle courtyard')
 for a,b in zip([k.ToMM(courtyard[0].GetStart().x),k.ToMM(courtyard[0].GetStart().y),k.ToMM(courtyard[0].GetEnd().x),k.ToMM(courtyard[0].GetEnd().y)],[-1.7,-1.55,1.7,1.55]):near(a,b)
 check(1.7-1.45>=.25-1e-8,'courtyard occupied X clearance');check(1.55-1.3>=.25-1e-8,'courtyard max protruded body Y clearance')
 rr['courtyard_mm']=[3.4,3.1];report['footprints'].append(rr)
 fp.SetReference('U'+str(501+index));fp.SetValue('SOT353-1' if index==0 else 'SOT363-2');fp.SetFPID(k.LIB_ID(LIBNAME,name));fp.SetPosition(k.VECTOR2I(k.FromMM(5+index*6),k.FromMM(5)));board.Add(fp)
 for n,p in cu.items():net=k.NETINFO_ITEM(board,f'ISOLATED_{index}_{n}');board.Add(net);p.SetNet(net)
for a,b in [((1,1),(15,1)),((15,1),(15,9)),((15,9),(1,9)),((1,9),(1,1))]:
 shape=k.PCB_SHAPE();shape.SetShape(k.SHAPE_T_SEGMENT);shape.SetLayer(k.Edge_Cuts);shape.SetWidth(k.FromMM(.05));shape.SetStart(k.VECTOR2I(*(k.FromMM(v)for v in a)));shape.SetEnd(k.VECTOR2I(*(k.FromMM(v)for v in b)));board.Add(shape)
name='Nexperia_Standard_Geometry_QA_ONLY'
k.SaveBoard(str(O/(name+'.kicad_pcb')),board)
(O/(name+'.kicad_pro')).write_text((ROOT/'cad/verified-footprints/Footprint_Geometry_QA_ONLY.kicad_pro').read_text().replace('Footprint_Geometry_QA_ONLY',name))
report['assertions_passed']=checks
(M/'nexperia-standard-footprint-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
