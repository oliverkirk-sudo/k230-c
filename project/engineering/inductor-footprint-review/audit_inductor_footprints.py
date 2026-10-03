#!/usr/bin/python3
"""Independent native Murata land audit. Writes isolated review artifacts only."""
from pathlib import Path
import os,json,hashlib,subprocess,copy,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[2];O=R/'engineering/inductor-footprint-review';C=R/'cad/inductor-footprint-review';L=R/'cad/verified-footprints/inductor-candidates/CMK230_Inductor_Candidates.pretty'
for n,p in [('XDG_CACHE_HOME','cache'),('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data')]:
 q=C/'runtime'/p;q.mkdir(parents=True,exist_ok=True);os.environ[n]=str(q)
import pcbnew as k
nm=k.FromMM;mm=k.ToMM;count=0

def near(a,b):
 global count
 count+=1;assert abs(a-b)<2e-6,(a,b)

def box(shapes,wh):
 assert len(shapes)==4
 pts=[(mm(g.GetStart().x),mm(g.GetStart().y)) for g in shapes]+[(mm(g.GetEnd().x),mm(g.GetEnd().y)) for g in shapes]
 assert len(set(pts))==4 and all(pts.count(p)==2 for p in set(pts))
 for x in shapes:near(mm(x.GetWidth()),.05)
 for got,want in zip([min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts)],[-wh[0]/2,-wh[1]/2,wh[0]/2,wh[1]/2]):near(got,want)
source=json.loads((L.parent/'source-land-validation.json').read_text());b=k.BOARD();ds=b.GetDesignSettings();ds.m_SolderPasteMargin=0;ds.m_SolderPasteMarginRatio=0
r={'scope':'CONDITIONAL_LAND_GEOMETRY_ONLY_NOT_HOTLOSS_OR_ASSEMBLY_QUALIFICATION','kicad_version':k.Version(),'parts':[]}
for i,(mpn,sourcehash,height) in enumerate([('DFE201612E-R24M=P2','6fbbdccedc9f58904a3e60d7e9c0e33917a03b7dd0d96716821988e89e4fb8ad',1.2),('DFE201610E-R47M=P2','5c02415289b2b9d2c0ceb283cfe004a986d9e729dadbfe92917a381db5eae84e',1.0)]):
 q=next(z for z in source['parts'] if z['mpn']==mpn);pdf=Path(q['pdf']);assert hashlib.sha256(pdf.read_bytes()).hexdigest()==sourcehash==q['source_sha256']
 path=L/(q['footprint']+'.kicad_mod');h=hashlib.sha256(path.read_bytes()).hexdigest();assert h==q['footprint_sha256']
 f=k.FootprintLoad(str(L),q['footprint']);assert f.GetAttributes() & k.FP_SMD
 ps=list(f.Pads());cp=sorted((p for p in ps if p.IsOnCopperLayer()),key=lambda p:p.GetNumber());ap=sorted((p for p in ps if not p.IsOnCopperLayer()),key=lambda p:p.GetPosition().x)
 assert len(ps)==4 and len(cp)==2 and len(ap)==2;assert [p.GetNumber() for p in cp]==['1','2']
 for p,x in zip(cp,[-.8,.8]):
  assert set(p.GetLayerSet().Seq())=={k.F_Cu,k.F_Mask};assert p.GetShape()==k.PAD_SHAPE_RECT and p.GetAttribute()==k.PAD_ATTRIB_SMD
  for v,w in zip([mm(p.GetPosition().x),mm(p.GetPosition().y),mm(p.GetSize().x),mm(p.GetSize().y)], [x,0,.8,1.8]):near(v,w)
  near(mm(p.GetLocalSolderMaskMargin()),.05)
 for p,x in zip(ap,[-.8,.8]):
  assert not p.GetNumber();assert set(p.GetLayerSet().Seq())=={k.F_Paste};assert p.GetShape()==k.PAD_SHAPE_RECT and p.GetAttribute()==k.PAD_ATTRIB_SMD
  for v,w in zip([mm(p.GetPosition().x),mm(p.GetPosition().y),mm(p.GetSize().x),mm(p.GetSize().y)], [x,0,.8,1.8]):near(v,w)
 box([x for x in f.GraphicalItems() if x.GetLayer()==k.F_Fab],[2.2,1.8]);box([x for x in f.GraphicalItems() if x.GetLayer()==k.F_CrtYd],[3.,2.4]);box([x for x in f.GraphicalItems() if x.GetLayer()==k.Dwgs_User],[2.2,1.8]);assert len(list(f.Zones()))==0
 assert 'not automatically enforced' in f.GetLibDescription()
 f.SetReference('L'+str(i+1));f.SetPosition(k.VECTOR2I(nm(4+i*6),nm(4)));f.SetFPID(k.LIB_ID('CMK230_Inductor_Candidates',q['footprint']));b.Add(f)
 for p in cp:
  net=k.NETINFO_ITEM(b,f.GetReference()+'_PAD_'+p.GetNumber());b.Add(net);p.SetNet(net)
 r['parts'].append({'mpn':mpn,'footprint_file':str(path),'footprint_sha256':h,'source_pdf':str(pdf),'source_sha256':sourcehash,'copper_pads':2,'paste_only_unnumbered_apertures':2,'pad_size_mm':[.8,1.8],'centers_x_mm':[-.8,.8],'gap_mm':.8,'copper_span_mm':2.4,'mask_expansion_mm':.05,'mask_aperture_bounding_size_mm':[.9,1.9],'mask_web_mm':.7,'courtyard_mm':[3.,2.4],'courtyard_margin_from_mask_to_centerline_mm':.25,'courtyard_margin_from_mask_to_inner_stroke_edge_mm':.225,'body_max_mm':[2.2,1.8,height],'undercoil_dwgs_user_mm':[2.2,1.8],'embedded_keepout_rule_areas':0})
for a,z in [((0,0),(14,0)),((14,0),(14,8)),((14,8),(0,8)),((0,8),(0,0))]:
 g=k.PCB_SHAPE();g.SetShape(k.SHAPE_T_SEGMENT);g.SetLayer(k.Edge_Cuts);g.SetStart(k.VECTOR2I(*(nm(v) for v in a)));g.SetEnd(k.VECTOR2I(*(nm(v) for v in z)));g.SetWidth(nm(.05));b.Add(g)
base=json.loads((R/'cad/bypass-footprint-review/Bypass_Geometry_QA_ONLY.kicad_pro').read_text())
(C/'fp-lib-table').write_text('(fp_lib_table\n (lib (name "CMK230_Inductor_Candidates")(type "KiCad")(uri "'+str(L)+'")(options "")(descr "Read-only candidate source library"))\n)\n')
names=[]
def save(name,clearance=.20):
 p=copy.deepcopy(base);p['meta']['filename']=name+'.kicad_pro';p['board']['design_settings']['rules']['min_clearance']=clearance;p['net_settings']['classes'][0]['clearance']=clearance
 k.SaveBoard(str(C/(name+'.kicad_pcb')),b);(C/(name+'.kicad_pro')).write_text(json.dumps(p,indent=2)+'\n');names.append(name)
save('Murata_Geometry_QA_ONLY');save('Murata_Negative_Clearance_081',.81)
ds.m_SolderPasteMargin=nm(-.02);ds.m_SolderPasteMarginRatio=-.10
r['paste_override_test']={'board_absolute_margin_mm':-.02,'board_ratio':-.10,'pads':[]}
for f in b.GetFootprints():
 for p in f.Pads():
  m=p.GetSolderPasteMargin(k.F_Paste)
  entry={'reference':f.GetReference(),'pad_number':p.GetNumber(),'on_copper':p.IsOnCopperLayer(),'on_paste':p.IsOnLayer(k.F_Paste),'effective_paste_margin_xy_mm':[mm(m.x),mm(m.y)]}
  if p.IsOnLayer(k.F_Paste):near(mm(m.x),0);near(mm(m.y),0)
  else:assert not p.IsOnLayer(k.F_Paste)
  r['paste_override_test']['pads'].append(entry)
save('Murata_Paste_Override_Control')
ds.m_SolderPasteMargin=0;ds.m_SolderPasteMarginRatio=0
# Deliberate invalid-by-source unrelated back-copper control: demonstrate marker is not a keepout.
n=k.NETINFO_ITEM(b,'UNRELATED_UNDERCOIL_CONTROL');b.Add(n)
for a,z in [((2.5,3.5),(5.5,3.5)),((5.5,3.5),(5.5,4.5)),((5.5,4.5),(2.5,4.5)),((2.5,4.5),(2.5,3.5))]:
 t=k.PCB_TRACK(b);t.SetStart(k.VECTOR2I(*(nm(v) for v in a)));t.SetEnd(k.VECTOR2I(*(nm(v) for v in z)));t.SetWidth(nm(.10));t.SetLayer(k.B_Cu);t.SetNet(n);b.Add(t)
save('Murata_Undercoil_Unenforced_Control')
r['undercoil_control']='Intentional unrelated closed B.Cu track loop passes below L1 across the maximum-body rectangle; source gives no layer exemption. This is a demonstration board, never a placement suggestion.'
r['numeric_assertions_passed']=count
(O/'geometry-audit.json').write_text(json.dumps(r,indent=2)+'\n')
logs=[]
for name in names:
 cmd=['kicad-cli','pcb','drc','--format','json','--severity-all','--exit-code-violations','-o',str(O/(name+'-drc.json')),str(C/(name+'.kicad_pcb'))];p=subprocess.run(cmd,text=True,capture_output=True);logs.append({'command':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr});print(name,p.returncode,p.stdout.strip())
(O/'native-drc-runs.json').write_text(json.dumps(logs,indent=2)+'\n')
plots=[]
for name,layer,suffix in [('Murata_Geometry_QA_ONLY','F.Cu','copper'),('Murata_Geometry_QA_ONLY','F.Mask','mask'),('Murata_Geometry_QA_ONLY','F.Paste','paste-zero'),('Murata_Paste_Override_Control','F.Paste','paste-override'),('Murata_Geometry_QA_ONLY','F.CrtYd,F.Fab,Dwgs.User','outlines'),('Murata_Undercoil_Unenforced_Control','B.Cu,Dwgs.User','undercoil-control')]:
 cmd=['kicad-cli','pcb','export','svg','--mode-single','--layers',layer+',Edge.Cuts','--fit-page-to-board','--exclude-drawing-sheet','-o',str(O/'evidence'/('native-'+suffix+'.svg')),str(C/(name+'.kicad_pcb'))];p=subprocess.run(cmd,text=True,capture_output=True);assert p.returncode==0,p.stderr;plots.append({'command':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
(O/'native-svg-runs.json').write_text(json.dumps(plots,indent=2)+'\n')
def svg_geometry(name):
 root=ET.parse(O/'evidence'/name).getroot();return [(x.tag.split('}')[-1],dict(x.attrib)) for x in root.iter() if x.tag.split('}')[-1] in ['path','polygon','polyline','rect','circle','ellipse']]
x=svg_geometry('native-paste-zero.svg');y=svg_geometry('native-paste-override.svg');assert x==y,(x,y)
(O/'paste-native-svg-comparison.json').write_text(json.dumps({'equal_native_geometry':True,'geometry_elements':len(x),'zero_board_margin_mm':0,'override_board_margin_mm':-.02,'override_ratio':-.10,'result':'Explicit non-copper paste apertures remain 0.8x1.8mm under nonzero board paste settings'},indent=2)+'\n')
print('PASS native paste geometry identical under -.02 mm / -10% board override; numeric assertions',count)
