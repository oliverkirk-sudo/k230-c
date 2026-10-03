#!/usr/bin/python3
"""Independent native KiCad geometry/pin checks against the NXP source drawing."""
from pathlib import Path
import pcbnew as k
import json, math, itertools, hashlib, xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[2]; M=ROOT/'engineering/mechanical'
O=ROOT/'cad/verified-footprints/translator-candidate'; L=O/'CMK230_Translator_Candidate.pretty'
name='NXP_SOT1161-2_NVT4858HK_1.8x2.6_P0.4_DrawingVerified_CANDIDATE'
fp=k.FootprintLoad(str(L),name); assert fp
# Literal independent transcription, component-side (not NXP bottom-view package sketch).
expected={
 '1':[-.600,-.600,.900,.220], '2':[-.625,-.200,.850,.220],
 '3':[-.625,.200,.850,.220], '4':[-.625,.600,.850,.220],
 '5':[-.600,1.175,.220,.550], '6':[-.200,1.175,.220,.550],
 '7':[.200,1.175,.220,.550], '8':[.600,1.175,.220,.550],
 '9':[.625,.600,.850,.220], '10':[.625,.200,.850,.220],
 '11':[.625,-.200,.850,.220], '12':[.625,-.600,.850,.220],
 '13':[.600,-1.175,.220,.550], '14':[.200,-1.175,.220,.550],
 '15':[-.200,-1.175,.220,.550], '16':[-.600,-1.175,.220,.550]}
func={1:'DAT2A',2:'DAT3A',3:'DAT0A',4:'DAT1A',5:'CLKA',6:'CLK_FB',7:'GND',8:'CLKB',
      9:'DAT1B',10:'DAT0B',11:'DAT3B',12:'DAT2B',13:'CMDB',14:'VCCB',15:'VCCA',16:'CMDA'}
checks=0
def near(a,b):
 global checks
 checks+=1; assert abs(a-b)<2e-6,(a,b)
def geometry(p):return [k.ToMM(v) for v in [p.GetPosition().x,p.GetPosition().y,p.GetSize().x,p.GetSize().y]]
def match(a,b):
 for x,y in zip(a,b):near(x,y)
pads=list(fp.Pads());cu={p.GetNumber():p for p in pads if p.IsOnLayer(k.F_Cu)}
assert set(cu)==set(expected)
report={'status':'PASS','scope':'Isolated mechanical candidate only','layers':{}}
for layer,label,change in [(k.F_Cu,'copper',0),(k.F_Mask,'mask',.1),(k.F_Paste,'paste',-.05)]:
 pp=[p for p in pads if p.IsOnLayer(layer)];assert len(pp)==16
 for n,e in expected.items():
  found=[p for p in pp if abs(geometry(p)[0]-e[0])<1e-6 and abs(geometry(p)[1]-e[1])<1e-6]
  assert len(found)==1;p=found[0];match(geometry(p),[e[0],e[1],e[2]+change,e[3]+change]);assert p.GetShape()==k.PAD_SHAPE_RECT
  if label=='copper':assert p.GetNumber()==n and not p.IsOnLayer(k.F_Mask) and not p.IsOnLayer(k.F_Paste)
  else:assert not p.GetNumber() and not p.IsOnCopperLayer()
  if label=='mask':near(p.GetLocalSolderMaskMargin(),0)
  if label=='paste':near(p.GetLocalSolderPasteMargin(),0);near(p.GetLocalSolderPasteMarginRatio(),0)
 gap=min(math.hypot(max(0,abs(geometry(a)[0]-geometry(b)[0])-(geometry(a)[2]+geometry(b)[2])/2),max(0,abs(geometry(a)[1]-geometry(b)[1])-(geometry(a)[3]+geometry(b)[3])/2)) for a,b in itertools.combinations(pp,2))
 report['layers'][label]={'apertures':len(pp),'minimum_gap_mm':round(gap,6)}
c=[g for g in fp.GraphicalItems() if g.GetLayer()==k.F_CrtYd];assert len(c)==1
match([k.ToMM(c[0].GetStart().x),k.ToMM(c[0].GetStart().y),k.ToMM(c[0].GetEnd().x),k.ToMM(c[0].GetEnd().y)],[-1.4,-1.8,1.4,1.8])
for p in pads:
 x,y,w,h=geometry(p);assert abs(x)+w/2<=1.15+1e-8 and abs(y)+h/2<=1.55+1e-8
r=ET.parse(ROOT/'cad/integrated/master.xml').getroot();checked={}
for net in r.findall('./nets/net'):
 for node in net.findall('node'):
  if node.get('ref')=='U95':
   n=int(node.get('pin'));assert node.get('pinfunction')==func[n];checked[n]=net.get('name')
assert len(checked)==16
report.update({'numeric_assertions':checks,'numbered_electrical_pads':16,'exposed_pad':False,'master_U95_pin_names_match_datasheet':True,
 'master_U95_pin_nets_snapshot':checked,'project_courtyard_mm':[2.8,3.6],
 'footprint_sha256':hashlib.sha256((L/(name+'.kicad_mod')).read_bytes()).hexdigest()})
board=k.BOARD();fp.SetReference('U401');fp.SetValue('NVT4858_GEOMETRY_QA');fp.SetFPID(k.LIB_ID('CMK230_Translator_Candidate',name));fp.SetPosition(k.VECTOR2I(k.FromMM(5),k.FromMM(5)));board.Add(fp)
for n,p in cu.items():net=k.NETINFO_ITEM(board,'GEOMETRY_ONLY_'+n);board.Add(net);p.SetNet(net)
for start,end in [((1,1),(9,1)),((9,1),(9,9)),((9,9),(1,9)),((1,9),(1,1))]:
 shape=k.PCB_SHAPE();shape.SetShape(k.SHAPE_T_SEGMENT);shape.SetLayer(k.Edge_Cuts);shape.SetWidth(k.FromMM(.05));shape.SetStart(k.VECTOR2I(*(k.FromMM(v) for v in start)));shape.SetEnd(k.VECTOR2I(*(k.FromMM(v) for v in end)));board.Add(shape)
k.SaveBoard(str(O/'NVT4858_Geometry_QA_ONLY.kicad_pcb'),board)
(O/'NVT4858_Geometry_QA_ONLY.kicad_pro').write_text((ROOT/'cad/verified-footprints/Footprint_Geometry_QA_ONLY.kicad_pro').read_text().replace('Footprint_Geometry_QA_ONLY','NVT4858_Geometry_QA_ONLY'))
(M/'nvt4858-footprint-verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
