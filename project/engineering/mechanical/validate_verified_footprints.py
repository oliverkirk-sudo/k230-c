#!/usr/bin/python3
"""Independent geometry expectations transcribed from TI drawings, tested via KiCad 9 parser.
Does not import builder/spec JSON; tests actual persisted pad/layer objects.
QA board deliberately has no functional circuit, tracks, vias or manufacturing authorization.
"""
import pcbnew as k
import json,math,itertools,csv,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];CAD=ROOT/'cad/verified-footprints';OUT=ROOT/'engineering/mechanical';LIB=CAD/'CMK230_Verified.pretty'
mm=k.ToMM;assertions=0

def near(a,b):
 global assertions
 assertions+=1
 assert abs(a-b)<.000002,(a,b)
def close_tuple(a,b):
 for x,y in zip(a,b):near(x,y)

def pdat(p):
 return [mm(p.GetPosition().x),mm(p.GetPosition().y),mm(p.GetSize().x),mm(p.GetSize().y)]

def match(label):return next(p for p in LIB.glob('*.kicad_mod') if label in p.stem)
refs={
'RSV':('U101',(-1.4,-1.8,1.4,1.8),(.05,16),{
'1':(-.75,-.6,.7,.2),'2':(-.8,-.2,.6,.2),'3':(-.8,.2,.6,.2),'4':(-.8,.6,.6,.2),
'5':(-.6,1.2,.2,.6),'6':(-.2,1.2,.2,.6),'7':(.2,1.2,.2,.6),'8':(.6,1.2,.2,.6),
'9':(.8,.6,.6,.2),'10':(.8,.2,.6,.2),'11':(.8,-.2,.6,.2),'12':(.8,-.6,.6,.2),
'13':(.6,-1.2,.2,.6),'14':(.2,-1.2,.2,.6),'15':(-.2,-1.2,.2,.6),'16':(-.6,-1.2,.2,.6)}),
'DBV':('U102',(-2.15,-2.05,2.15,2.05),(.05,5),{'1':(-1.3,-.95,1.1,.6),'2':(-1.3,0,1.1,.6),'3':(-1.3,.95,1.1,.6),'4':(1.3,.95,1.1,.6),'5':(1.3,-.95,1.1,.6)}),
'DMQ':('U103',(-1.25,-1.05,1.25,1.05),(-.05,6),{'1':(-.65,-.5,.7,.35),'2':(-.65,0,.7,.35),'3':(-.65,.5,.7,.35),'4':(.45,.5,1.1,.3),'5':(.45,0,1.1,.3),'6':(.45,-.5,1.1,.3)}),
'YCG':('U104',(-.8,-1.15,.8,1.15),(-.0325,15),{r+str(c):((c-2)*.35,(i-2)*.35,.265,.265) for i,r in enumerate('ABCDE') for c in range(1,4)})}
report={'scope':'Drawing geometry only, no functional PCB sign-off','kicad_version':k.Version(),'units':'mm','coordinate_system':'component side, origin body center, positive X right, positive Y down','footprints':[]}
board=k.BOARD();positions={'RSV':(7,7),'DBV':(19,7),'DMQ':(7,17),'YCG':(19,17)}
parsed=[]
for family,(ref,court,(mask,qty),exp) in refs.items():
 path=match(family);fp=k.FootprintLoad(str(LIB),path.stem);assert fp is not None
 pads=list(fp.Pads());cp=[p for p in pads if p.IsOnLayer(k.F_Cu)];numbered={p.GetNumber():p for p in cp}
 assert len(cp)==qty;assert len(numbered)==qty;assert set(numbered)==set(exp);assert all(p.GetNumber() for p in cp)
 pp=[p for p in pads if p.IsOnLayer(k.F_Paste)];assert len(pp)==qty
 mp=[p for p in pads if p.IsOnLayer(k.F_Mask)];assert len(mp)==qty
 for num,expected in exp.items():
  p=numbered[num];close_tuple(pdat(p),expected)
  assert not p.IsOnLayer(k.F_Mask)
  maskpad=next(z for z in mp if abs(mm(z.GetPosition().x)-expected[0])<1e-6 and abs(mm(z.GetPosition().y)-expected[1])<1e-6)
  close_tuple(pdat(maskpad),(expected[0],expected[1],expected[2]+2*mask,expected[3]+2*mask))
  assert not maskpad.GetNumber();assert not maskpad.IsOnCopperLayer();assert maskpad.GetLocalSolderMaskMargin()==0
  if family!='YCG':near(mm(maskpad.GetRoundRectCornerRadius()),.1 if family in ['RSV','DBV'] else .05)
  if family in ['RSV','DBV']:assert p.IsOnLayer(k.F_Paste);near(mm(p.GetRoundRectCornerRadius()),.05)
  if family=='DMQ':
   assert not p.IsOnLayer(k.F_Paste);near(mm(p.GetRoundRectCornerRadius()),.1)
   target=(expected[0],expected[1],.6 if int(num)<=3 else 1.,.25 if int(num)<=3 else .2)
   paste=next(z for z in pp if abs(mm(z.GetPosition().x)-expected[0])<1e-6 and abs(mm(z.GetPosition().y)-expected[1])<1e-6)
   close_tuple(pdat(paste),target);near(mm(paste.GetRoundRectCornerRadius()),.05)
   assert not paste.GetNumber();assert not paste.IsOnCopperLayer()
  if family=='YCG':
   assert p.GetShape()==k.PAD_SHAPE_CIRCLE;assert not p.IsOnLayer(k.F_Paste)
   paste=next(z for z in pp if abs(mm(z.GetPosition().x)-expected[0])<1e-6 and abs(mm(z.GetPosition().y)-expected[1])<1e-6)
   close_tuple(pdat(paste),(expected[0],expected[1],.21,.21));near(mm(paste.GetRoundRectCornerRadius()),.05)
   assert not paste.GetNumber();assert not paste.IsOnCopperLayer()
   near(mm(p.GetSize().x)+2*mask,.2)
 for paste in pp:
  assert paste.GetLocalSolderPasteMargin()==0;near(paste.GetLocalSolderPasteMarginRatio(),0)
 # Native saved courtyard rectangle, exact limits and strictly encloses pad/mask bounds.
 cy=[g for g in fp.GraphicalItems() if g.GetLayer()==k.F_CrtYd];assert len(cy)==1
 close_tuple((mm(cy[0].GetStart().x),mm(cy[0].GetStart().y),mm(cy[0].GetEnd().x),mm(cy[0].GetEnd().y)),court)
 for p in cp:
  x,y,w,h=pdat(p);m=max(0,mask)
  assert x-w/2-m>=court[0]+.25-1e-8 and x+w/2+m<=court[2]-.25+1e-8
  assert y-h/2-m>=court[1]+.25-1e-8 and y+h/2+m<=court[3]-.25+1e-8
 # Min spacing conservatively measured between rectangular bounds for roundrects; exact for aligned circles.
 mingap=999
 for a,b in itertools.combinations(cp,2):
  x,y,w,h=pdat(a);xx,yy,ww,hh=pdat(b)
  if family=='YCG':gap=math.hypot(x-xx,y-yy)-(w+ww)/2
  else:gap=math.hypot(max(0,abs(x-xx)-(w+ww)/2),max(0,abs(y-yy)-(h+hh)/2))
  mingap=min(mingap,gap)
 # Neighbor mask clearances same aligned relation applies to minimum in all these patterns.
 entry={'name':path.stem,'numbered_copper_pads':len(cp),'paste_apertures':len(pp),'explicit_mask_apertures':len(mp),'min_copper_gap_mm':round(mingap,6),'min_mask_web_mm':round(mingap-2*mask,6),'status':'PASS','sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
 report['footprints'].append(entry);parsed.append((family,fp))
 fp.SetReference(ref);fp.SetValue(family+' GEOMETRY QA');fp.SetPosition(k.VECTOR2I(*(k.FromMM(v) for v in positions[family])))
 fp.SetFPID(k.LIB_ID('CMK230_Verified',path.stem));board.Add(fp)
 for p in cp:
  net=k.NETINFO_ITEM(board,ref+'_'+p.GetNumber());board.Add(net);p.SetNet(net)
for start,end in [((1,1),(25,1)),((25,1),(25,23)),((25,23),(1,23)),((1,23),(1,1))]:
 sh=k.PCB_SHAPE();sh.SetShape(k.SHAPE_T_SEGMENT);sh.SetLayer(k.Edge_Cuts);sh.SetStart(k.VECTOR2I(*(k.FromMM(v) for v in start)));sh.SetEnd(k.VECTOR2I(*(k.FromMM(v) for v in end)));sh.SetWidth(k.FromMM(.05));board.Add(sh)
k.SaveBoard(str(CAD/'Footprint_Geometry_QA_ONLY.kicad_pcb'),board)
# QA settings are local to this isolated test and do not constrain the module/fabricator.
project={'meta':{'filename':'Footprint_Geometry_QA_ONLY.kicad_pro','version':1},'board':{'design_settings':{'rules':{'min_clearance':.075,'min_copper_edge_clearance':.25,'min_silk_clearance':.10,'min_silk_text_height':.5,'min_silk_text_thickness':.08,'min_track_width':.075,'min_through_hole_diameter':.15,'min_via_diameter':.3,'solder_mask_clearance':0,'solder_mask_min_width':.05},'rule_severities':{'missing_courtyard':'error','malformed_courtyard':'error','courtyards_overlap':'error','clearance':'error'}}},'net_settings':{'classes':[{'name':'Default','clearance':.075,'track_width':.1,'via_diameter':.3,'via_drill':.15}],'meta':{'version':3}}}
(CAD/'Footprint_Geometry_QA_ONLY.kicad_pro').write_text(json.dumps(project,indent=2)+'\n')
report['numeric_assertions_passed']=assertions
(OUT/'small-parts-verification.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
# Compare installed libraries without editing them.
libcheck=[]
for path,name in [('Package_TO_SOT_SMD.pretty','SOT-23-5'),('Package_DFN_QFN.pretty','UQFN-16_1.8x2.6mm_P0.4mm'),('Package_SON.pretty','WSON-6_1.5x1.5mm_P0.5mm')]:
 fp=k.FootprintLoad('/usr/share/kicad/footprints/'+path,name)
 libcheck.append({'library':path,'name':name,'description':fp.GetLibDescription(),'pads':[{'number':p.GetNumber(),'xywh':pdat(p),'angle_deg':p.GetOrientationDegrees()} for p in fp.Pads()]})
(OUT/'installed-kicad-library-comparison.json').write_text(json.dumps(libcheck,indent=2)+'\n')
