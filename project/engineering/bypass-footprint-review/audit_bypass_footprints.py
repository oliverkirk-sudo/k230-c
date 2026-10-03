#!/usr/bin/python3
"""Independent source transcription and native persisted-footprint audit; no production writes."""
import os
from pathlib import Path
R=Path(__file__).resolve().parents[2];OUT=R/'engineering/bypass-footprint-review';CAD=R/'cad/bypass-footprint-review';LIB=R/'cad/verified-footprints/bypass-candidates/CMK230_Bypass_Candidates.pretty'
for name,part in [('XDG_CACHE_HOME','cache'),('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data')]:
 p=CAD/'runtime'/part;p.mkdir(parents=True,exist_ok=True);os.environ[name]=str(p)
import pcbnew as k,json,hashlib,subprocess,copy
mm=k.ToMM; nm=k.FromMM; checks=0
# From exact-part p1 and source p33, independently transcribed, not imported from builder.
expected=[dict(mpn='CL03B104KP3NNWC',ref='C1',pdf='samsung-CL03B104KP3NNW-specsheet.pdf',case_metric='0603',tolerance=.03,body_max=[.63,.33],gap=.25,length=.34,width=.33,center=.295,courtyard=[1.23,.63],source_ranges=[[.22,.28],[.31,.37],[.30,.36]],xy=(3,3)),dict(mpn='CL10B475KQ8NFQC',ref='C2',pdf='samsung-CL10B475KQ8NFQ-specsheet.pdf',case_metric='1608',tolerance=.15,body_max=[1.75,.95],gap=.70,length=.78,width=.95,center=.74,courtyard=[2.56,1.25],source_ranges=[[.65,.75],[.73,.83],[.90,1.00]],xy=(7,3))]
report={'scope':'NATIVE_FOOTPRINT_GEOMETRY_ONLY_NOT_CAPACITANCE_PDN_ASSEMBLY_OR_MODULE_FIT_QUALIFICATION','kicad_version':k.Version(),'units':'mm','parts':[]}
b=k.BOARD();ds=b.GetDesignSettings();ds.m_SolderPasteMargin=0;ds.m_SolderPasteMarginRatio=0;ds.m_SolderMaskExpansion=0;ds.m_SolderMaskMinWidth=nm(.10);ds.m_AllowSoldermaskBridgesInFPs=False

def near(got,want):
 global checks
 checks+=1;assert abs(got-want)<2e-6,(got,want)
for q in expected:
 path=next(LIB.glob('*'+q['mpn']+'*.kicad_mod'));f=k.FootprintLoad(str(LIB),path.stem);assert f
 pads=sorted(f.Pads(),key=lambda p:p.GetNumber());assert len(pads)==2;assert [p.GetNumber() for p in pads]==['1','2']
 assert f.GetAttributes() & k.FP_SMD
 for p,sgn in zip(pads,[-1,1]):
  assert p.GetAttribute()==k.PAD_ATTRIB_SMD and p.GetShape()==k.PAD_SHAPE_RECT
  assert set(p.GetLayerSet().Seq())=={k.F_Cu,k.F_Mask,k.F_Paste}
  near(mm(p.GetPosition().x),sgn*q['center']);near(mm(p.GetPosition().y),0)
  near(mm(p.GetSize().x),q['length']);near(mm(p.GetSize().y),q['width']);near(mm(p.GetDrillSize().x),0);near(mm(p.GetDrillSize().y),0)
  near(mm(p.GetLocalSolderMaskMargin()),.05);assert p.GetLocalSolderPasteMargin() is None;assert p.GetLocalSolderPasteMarginRatio() is None
 cy=[x for x in f.GraphicalItems() if x.GetLayer()==k.F_CrtYd];fab=[x for x in f.GraphicalItems() if x.GetLayer()==k.F_Fab];assert len(cy)==4 and len(fab)==4
 bounds=[]
 for shapes,wh in [(cy,q['courtyard']),(fab,q['body_max'])]:
  pts=[(mm(x.GetStart().x),mm(x.GetStart().y)) for x in shapes]+[(mm(x.GetEnd().x),mm(x.GetEnd().y)) for x in shapes]
  assert all(sum(t==p for t in pts)==2 for p in set(pts));assert len(set(pts))==4
  for x in shapes:near(mm(x.GetWidth()),.05)
  got=[min(p[0] for p in pts),min(p[1] for p in pts),max(p[0] for p in pts),max(p[1] for p in pts)]
  for x,y in zip(got,[-wh[0]/2,-wh[1]/2,wh[0]/2,wh[1]/2]):near(x,y)
  bounds.append(got)
 span=q['gap']+2*q['length'];mask_span=span+.1;mask_width=q['width']+.1
 near(2*q['center']-q['length'],q['gap'])
 for v,(lo,hi) in zip([q['gap'],q['length'],q['width']],q['source_ranges']):near(v,(lo+hi)/2)
 near((q['courtyard'][0]-mask_span)/2,.10);near((q['courtyard'][1]-mask_width)/2,.10)
 f.SetReference(q['ref']);f.SetFPID(k.LIB_ID('CMK230_Bypass_Candidates',path.stem));f.SetPosition(k.VECTOR2I(*(nm(x) for x in q['xy'])));b.Add(f)
 for p in pads:
  n=k.NETINFO_ITEM(b,q['ref']+'_PAD_'+p.GetNumber());b.Add(n);p.SetNet(n)
  near(mm(p.GetSolderMaskExpansion(k.F_Mask)),.05);margin=p.GetSolderPasteMargin(k.F_Paste);near(mm(margin.x),0);near(mm(margin.y),0)
 entry={**q,'footprint_file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pad_centers_x_mm':[-q['center'],q['center']],'copper_span_mm':span,'mask_aperture_mm':[q['length']+.1,q['width']+.1],'mask_web_mm':q['gap']-.1,'courtyard_margin_from_mask_to_centerline_mm':.10,'courtyard_margin_from_mask_to_inner_stroke_edge_mm':.075,'paste_area_ratio_at_100um':q['length']*q['width']/(2*(q['length']+q['width'])*.1),'source_pdf_sha256':hashlib.sha256((Path('/workspace/shared/k230-reference/mechanical/passive-review')/q['pdf']).read_bytes()).hexdigest()}
 report['parts'].append(entry)
for aa,bb in [((0,0),(10,0)),((10,0),(10,6)),((10,6),(0,6)),((0,6),(0,0))]:
 s=k.PCB_SHAPE();s.SetShape(k.SHAPE_T_SEGMENT);s.SetLayer(k.Edge_Cuts);s.SetStart(k.VECTOR2I(*(nm(x) for x in aa)));s.SetEnd(k.VECTOR2I(*(nm(x) for x in bb)));s.SetWidth(nm(.05));b.Add(s)
project={'meta':{'filename':'Bypass_Geometry_QA_ONLY.kicad_pro','version':1},'board':{'design_settings':{'rules':{'min_clearance':.20,'min_copper_edge_clearance':.25,'min_silk_clearance':.10,'min_silk_text_height':.5,'min_silk_text_thickness':.08,'min_track_width':.075,'min_through_hole_diameter':.15,'min_via_diameter':.3,'solder_mask_clearance':0,'solder_mask_min_width':.10,'allow_soldermask_bridges_in_footprints':False},'rule_severities':{'missing_courtyard':'error','malformed_courtyard':'error','courtyards_overlap':'error','clearance':'error'}}},'net_settings':{'classes':[{'name':'Default','clearance':.20,'track_width':.1,'via_diameter':.3,'via_drill':.15}],'meta':{'version':3}}}
(CAD/'fp-lib-table').write_text('(fp_lib_table\n (lib (name "CMK230_Bypass_Candidates")(type "KiCad")(uri "'+str(LIB)+'")(options "")(descr "Read-only production candidate source library"))\n)\n')
for name,clearance in [('Bypass_Geometry_QA_ONLY',.20),('Bypass_Negative_Clearance_026',.26),('Bypass_Negative_Clearance_071',.71)]:
 pr=copy.deepcopy(project);pr['meta']['filename']=name+'.kicad_pro';pr['board']['design_settings']['rules']['min_clearance']=clearance;pr['net_settings']['classes'][0]['clearance']=clearance
 k.SaveBoard(str(CAD/(name+'.kicad_pcb')),b);(CAD/(name+'.kicad_pro')).write_text(json.dumps(pr,indent=2)+'\n')
# Demonstrate the footprint's zero local paste default inherits a board override.
ds.m_SolderPasteMargin=nm(-.02)
report['paste_inheritance_check']=[{'reference':f.GetReference(),'pad':p.GetNumber(),'effective_margin_xy_mm':[mm(p.GetSolderPasteMargin(k.F_Paste).x),mm(p.GetSolderPasteMargin(k.F_Paste).y)]} for f in b.GetFootprints() for p in f.Pads()]
assert all(x['effective_margin_xy_mm']==[-.02,-.02] for x in report['paste_inheritance_check'])
ds.m_SolderPasteMargin=0
report['numeric_assertions_passed']=checks
report['paste_note']='No explicit standalone paste aperture or nonzero per-pad override is present. 1:1 paste is verified only with zero board/footprint paste margins and ratio.'
(OUT/'geometry-audit.json').write_text(json.dumps(report,indent=2)+'\n')
commands=[]
for name in ['Bypass_Geometry_QA_ONLY','Bypass_Negative_Clearance_026','Bypass_Negative_Clearance_071']:
 cmd=['kicad-cli','pcb','drc','--format','json','--severity-all','--exit-code-violations','-o',str(OUT/(name+'-drc.json')),str(CAD/(name+'.kicad_pcb'))]
 r=subprocess.run(cmd,text=True,capture_output=True);commands.append({'command':cmd,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
(OUT/'native-drc-runs.json').write_text(json.dumps(commands,indent=2)+'\n')
for x in commands:print(Path(x['command'][-1]).name,x['exit_code'],x['stdout'].strip(),x['stderr'].strip())
print('Independent numeric assertions:',checks)
