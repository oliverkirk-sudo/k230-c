from pathlib import Path
import os, json, hashlib, re, subprocess, datetime, xml.etree.ElementTree as ET
O=Path(__file__).resolve().parent
P=Path('/workspace/shared/k230-recovery-oct3/reconstruction-r6/project')
B=Path('/workspace/shared/k230-publication/r5-repo/project')
R=O.parent/'r6-l21-independent-runtime'
for v,sub in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data')]:
 d=R/sub;d.mkdir(parents=True,exist_ok=True);os.environ[v]=str(d)
import pcbnew as pcb
A=P/'cad/recovery-physical-candidate';C=P/'recovery/r6-passive-coverage'
lib='CMK230_Recovery_Inductor_Candidates';name='Coilcraft_XFL4015_StartPin1_RIGHT_SOURCE_CANDIDATE';fid=lib+':'+name
fpfile=P/'cad/recovery-inductor-candidates'/f'{lib}.pretty'/f'{name}.kicad_mod'
inputs=[A/'master.xml',A/'CMK230_Core_REVIEW.kicad_sch',A/'10_Six_Rail_Power.kicad_sch',A/'fp-lib-table',B/'cad/recovery-physical-candidate/master.xml',fpfile,C/'L21_SIX_LAYER_GEOMETRY_ONLY.kicad_pcb',C/'L21_SIX_LAYER_GEOMETRY_ONLY.kicad_pro',C/'L21_NEGATIVE_CLEARANCE.kicad_pcb',C/'L21_NEGATIVE_CLEARANCE.kicad_pro',C/'fp-lib-table',C/'validate_coverage.py']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p):sha(p) for p in inputs}
def mmvec(v):return [pcb.ToMM(v.x),pcb.ToMM(v.y)]
def pad_info(q):
 return {'number':q.GetNumber(),'position_xy_mm':mmvec(q.GetPosition()),'size_xy_mm':mmvec(q.GetSize()),'shape':int(q.GetShape()),'layers':[pcb.LayerName(x) for x in q.GetLayerSet().Seq()],'local_mask_mm':None if q.GetLocalSolderMaskMargin() is None else pcb.ToMM(q.GetLocalSolderMaskMargin()),'local_paste_mm':None if q.GetLocalSolderPasteMargin() is None else pcb.ToMM(q.GetLocalSolderPasteMargin()),'local_paste_ratio':q.GetLocalSolderPasteMarginRatio(),'net':q.GetNetname()}
def check_geometry(f):
 pads=list(f.Pads());numbered={p.GetNumber():p for p in pads if p.GetNumber()};paste=[p for p in pads if not p.GetNumber()]
 if set(numbered)!={'1','2'} or len(pads)!=4 or len(paste)!=2:return False
 for num,x in [('1',1.185),('2',-1.185)]:
  q=numbered[num]
  if mmvec(q.GetPosition())!=[x,0.0] or mmvec(q.GetSize())!=[.98,3.4] or q.GetShape()!=pcb.PAD_SHAPE_RECT:return False
  if set(q.GetLayerSet().Seq())!={pcb.F_Cu,pcb.F_Mask} or q.GetLocalSolderMaskMargin()!=pcb.FromMM(.05):return False
 if sorted(mmvec(p.GetPosition()) for p in paste)!=[[-1.185,0.0],[1.185,0.0]]:return False
 return all(mmvec(q.GetSize())==[.98,3.4] and set(q.GetLayerSet().Seq())=={pcb.F_Paste} and q.GetShape()==pcb.PAD_SHAPE_RECT for q in paste)
f=pcb.FootprintLoad(str(fpfile.parent),name);assert f and check_geometry(f)
shapes=[g for g in f.GraphicalItems() if hasattr(g,'GetShape')]
shape_info=[{'layer':pcb.LayerName(g.GetLayer()),'shape':int(g.GetShape()),'start_mm':mmvec(g.GetStart()),'end_mm':mmvec(g.GetEnd()),'stroke_mm':pcb.ToMM(g.GetWidth())}for g in shapes]
assert any(g.GetLayer()==pcb.F_Fab and g.GetShape()==pcb.SHAPE_T_RECT and mmvec(g.GetStart())==[-2.15,-2.15] and mmvec(g.GetEnd())==[2.15,2.15] for g in shapes)
assert any(g.GetLayer()==pcb.F_CrtYd and g.GetShape()==pcb.SHAPE_T_RECT and mmvec(g.GetStart())==[-2.4,-2.4] and mmvec(g.GetEnd())==[2.4,2.4] for g in shapes)
assert any(g.GetLayer()==pcb.F_Fab and g.GetShape()==pcb.SHAPE_T_SEGMENT and mmvec(g.GetStart())==[1.95,-1.5] and mmvec(g.GetEnd())==[1.95,1.5] for g in shapes)
mirrored=pcb.FootprintLoad(str(fpfile.parent),name)
for q in mirrored.Pads():
 if q.GetNumber() in ['1','2']:
  pos=q.GetPosition();q.SetPosition(pcb.VECTOR2I(-pos.x,pos.y))
assert not check_geometry(mirrored)
text=(A/'fp-lib-table').read_text();entries=re.findall(r'\(lib \(name "([^"]+)"\).*?\(uri "([^"]+)"\)',text)
uris=[u for l,u in entries if l==lib];assert len(uris)==1
resolved=Path(uris[0].replace('${KIPRJMOD}',str(A))).resolve();assert resolved==fpfile.parent.resolve()
assert pcb.FootprintLoad(str(resolved),name)
def graph(path):
 t=ET.parse(path).getroot();components={}
 for c in t.findall('components/comp'):
  components[c.get('ref')]={'value':c.findtext('value'),'footprint':c.findtext('footprint'),'properties':sorted((x.get('name'),x.get('value','')) for x in c.findall('property')),'libsource':c.find('libsource').attrib}
 nodes=sorted((n.get('ref'),n.get('pin'),net.get('name'),n.get('pinfunction'),n.get('pintype'))for net in t.findall('nets/net')for n in net.findall('node'))
 return components,nodes
bc,bn=graph(B/'cad/recovery-physical-candidate/master.xml');rc,rn=graph(A/'master.xml')
assert set(bc)==set(rc) and len(rc)==254 and len(rn)==1509 and bn==rn
value_changes=[r for r in rc if bc[r]['value']!=rc[r]['value']];properties_changes=[r for r in rc if bc[r]['properties']!=rc[r]['properties']];libsource_changes=[r for r in rc if bc[r]['libsource']!=rc[r]['libsource']]
assert not value_changes and not properties_changes and not libsource_changes
footprint_changes=sorted(r for r in rc if bc[r]['footprint']!=rc[r]['footprint'])
expected=json.loads((C/'assignments.json').read_text());assert footprint_changes==sorted(expected) and all(rc[r]['footprint']==x for r,x in expected.items())
assert rc['L21']['value']==bc['L21']['value']=='0.47uH XFL4015-471MEB REF'
assert not bc['L21']['footprint'] and rc['L21']['footprint']==fid
l21nodes=[x for x in rn if x[0]=='L21'];assert l21nodes==[('L21','1','SW_CORE',None,'passive'),('L21','2','VDD0P8_CORE',None,'passive')]
def run(args):
 r=subprocess.run(['kicad-cli',*args],capture_output=True,text=True,env=os.environ,timeout=90)
 if r.returncode not in [0,5]:raise RuntimeError(r.stderr)
 return {'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'command':['kicad-cli',*args]}
logs={};fresh=O/'fresh-active-master.xml'
logs['fresh_netlist']=run(['sch','export','netlist','--format','kicadxml','-o',str(fresh),str(A/'CMK230_Core_REVIEW.kicad_sch')]);assert graph(fresh)==(rc,rn)
fixture=pcb.LoadBoard(str(C/'L21_SIX_LAYER_GEOMETRY_ONLY.kicad_pcb'));assert fixture.GetCopperLayerCount()==6
fps=list(fixture.GetFootprints());assert len(fps)==1;ff=fps[0];assert ff.GetReference()=='L21' and str(ff.GetFPID().GetLibNickname())+':'+str(ff.GetFPID().GetLibItemName())==fid
bpads=[pad_info(q)|{'effective_mask_mm':pcb.ToMM(q.GetSolderMaskExpansion(pcb.F_Mask)),'effective_paste_margin_xy_mm':mmvec(q.GetSolderPasteMargin(pcb.F_Paste))}for q in ff.Pads()]
np={q.GetNumber():q for q in ff.Pads() if q.GetNumber()};assert np['1'].GetNetname()=='SW_CORE' and np['2'].GetNetname()=='VDD0P8_CORE';assert mmvec(np['1'].GetPosition())==[6.185,5.0] and mmvec(np['2'].GetPosition())==[3.815,5.0]
assert all(mmvec(q.GetSolderPasteMargin(pcb.F_Paste))==[0.0,0.0] for q in ff.Pads() if not q.GetNumber())
assert all(q.GetSolderMaskExpansion(pcb.F_Mask)==pcb.FromMM(.05) for q in np.values())
for key,file in [('normal_drc','L21_SIX_LAYER_GEOMETRY_ONLY'),('negative_clearance_drc','L21_NEGATIVE_CLEARANCE')]:
 logs[key]=run(['pcb','drc','--format','json','--severity-all','-o',str(O/(key+'.json')),str(C/(file+'.kicad_pcb'))])
normal=json.loads((O/'normal_drc.json').read_text());negative=json.loads((O/'negative_clearance_drc.json').read_text())
assert not normal['violations'] and not normal['unconnected_items'];assert len(negative['violations'])==1 and negative['violations'][0]['type']=='clearance' and '1.3900 mm' in negative['violations'][0]['description'] and '1.4000 mm' in negative['violations'][0]['description']
after={str(p):sha(p)for p in inputs};assert before==after
report={'status':'PASS_WITH_PROCESS_LIMITATIONS','date_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'kicad_version':pcb.GetBuildVersion(),'scope':'Independent native footprint and current active-netlist check; read-only source CAD','footprint_id':fid,'footprint_sha256':sha(fpfile),'pads_native':sorted([pad_info(q)for q in f.Pads()],key=lambda v:(v['number'],v['position_xy_mm'][0])),'graphics_native':shape_info,'body_max_xy_mm':[4.3,4.3],'courtyard_centerline_xy_mm':[4.8,4.8],'courtyard_stroke_mm':.05,'mask_opening_xy_mm':[1.08,3.5],'copper_gap_mm':1.39,'paste_aperture_xy_mm_in_fixture':[.98,3.4],'fixture_copper_layers':6,'fixture_pads':bpads,'library_registered_once':True,'library_uri':uris[0],'library_resolved_to_expected_directory':True,'baseline_active_master_sha256':sha(B/'cad/recovery-physical-candidate/master.xml'),'r6_active_master_sha256':sha(A/'master.xml'),'fresh_active_export_sha256':sha(fresh),'fresh_export_semantically_matches_r6_master':True,'component_count':len(rc),'distinct_net_count':len(set(x[2]for x in rn)),'pin_net_node_count':len(rn),'full_net_pinfunction_pintype_parity_r5':True,'component_value_changes':value_changes,'component_property_changes':properties_changes,'component_libsource_changes':libsource_changes,'changed_footprints_r5_to_r6':footprint_changes,'L21_baseline':bc['L21'],'L21_current':rc['L21'],'L21_nodes':l21nodes,'negative_controls':{'mirrored_numbered_lands_rejected':True,'native_clearance_1p40_against_gap_1p39_rejected':True},'normal_drc_violations':0,'negative_drc_violations':negative['violations'],'source_inputs_unchanged':True,'input_hashes':before,'limitations':['Separate paste-only rectangles preserve the declared 1:1 aperture in this native fixture; the independent check_paste_override.py also verifies unchanged SVG geometry under -0.02 mm / -10% global override. Process acceptance remains open.','4.80 mm courtyard is line-center geometry with 0.05 mm drawing stroke; it is a project process assumption, not a Coilcraft adjacency rule.','Height 1.60 mm remains source metadata, not a newly imposed constraint or independently enforced 3D model.','No explicit Coilcraft undercoil/layer prohibition is imported; no Murata restrictions inherited.','Fixture DRC is not a full-board or manufacturing clearance/EMI qualification. Hot current, saturation, thermal loss, stability and factory acceptance remain open.']}
(O/'native-review.json').write_text(json.dumps(report,indent=2)+'\n');(O/'native-runs.json').write_text(json.dumps(logs,indent=2)+'\n')
print(json.dumps({'status':report['status'],'components':len(rc),'nets':report['distinct_net_count'],'nodes':len(rn),'changed_footprints':len(footprint_changes),'L21_nodes':l21nodes,'normal_drc':len(normal['violations']),'negative_drc':len(negative['violations']),'source_inputs_unchanged':before==after},indent=2))
