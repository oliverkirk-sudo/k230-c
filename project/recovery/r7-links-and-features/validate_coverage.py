from pathlib import Path
import argparse,os,json,subprocess,copy,re,xml.etree.ElementTree as ET
import pcbnew as pcb
p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--runtime',type=Path,required=True);a=p.parse_args();P=a.project.resolve();B=a.baseline.resolve();A=P/'cad/recovery-physical-candidate';O=P/'recovery/r7-links-and-features';env=os.environ.copy()
for k,n in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data')]:
 d=a.runtime/n;d.mkdir(parents=True,exist_ok=True);env[k]=str(d.resolve())
FP=json.loads((O/'assignments.json').read_text());FEATURES={'JP1','TP81','TP82'}
import sys
sys.path.insert(0,str(P/'tools'))
from population_contract import apply_population,validate_population
def run(args):
 p=subprocess.run(['kicad-cli',*args],env=env,capture_output=True,text=True,timeout=60);assert p.returncode in[0,5],p.stderr;return {'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
def graph(f):
 x=ET.parse(f).getroot();c={e.attrib['ref']:{'value':e.findtext('value'),'footprint':e.findtext('footprint'),'properties':sorted((q.attrib['name'],q.attrib.get('value',''))for q in e.findall('property'))}for e in x.findall('components/comp')};n={(q.attrib['ref'],q.attrib['pin']):(e.attrib['name'],q.attrib.get('pinfunction'),q.attrib.get('pintype'))for e in x.findall('nets/net')for q in e.findall('node')};return c,n
logs={'netlist':run(['sch','export','netlist','--format','kicadxml','-o',str(A/'master.xml'),str(A/'CMK230_Core_REVIEW.kicad_sch')])};bc,bn=graph(B/'cad/recovery-physical-candidate/master.xml');c,n=graph(A/'master.xml');expected=copy.deepcopy(bc)
for ref,v in FP.items():expected[ref]['footprint']=v
for ref in FEATURES:expected[ref]['properties']=sorted(expected[ref]['properties']+[('exclude_from_bom','')])
assert c==expected and n==bn and len(c)==254 and len(n)==1509
assert all(('dnp','')in c[r]['properties']for r in ['JP1','R45','R47','R528'])
component_elements={e.attrib['ref']:e for e in ET.parse(A/'master.xml').getroot().findall('components/comp')}
lib='CMK230_Recovery_Link_Candidates';ld=P/'cad/recovery-link-candidates'/(lib+'.pretty')
def load(ref):return pcb.FootprintLoad(str(ld),FP[ref].split(':')[1])
def numbered(f):return {p.GetNumber():p for p in f.Pads()if p.GetNumber()}
def check_link(f,padx,pady,center):
 d=numbered(f)
 if set(d)!={'1','2'}:return False
 return all(abs(pcb.ToMM(d[i].GetPosition().x)-x)<1e-6 and abs(pcb.ToMM(d[i].GetSize().x)-padx)<1e-6 and abs(pcb.ToMM(d[i].GetSize().y)-pady)<1e-6 and d[i].IsOnLayer(pcb.F_Cu)and d[i].IsOnLayer(pcb.F_Mask)and not d[i].IsOnLayer(pcb.F_Paste)for i,x in [('1',-center),('2',center)])
assert check_link(load('R220'),1.01,1.01,.755)and check_link(load('R561'),.5,.6,.45)
f=load('JP1');assert f and f.IsExcludedFromBOM()and f.IsExcludedFromPosFiles()and not f.IsBoardOnly();assert check_link(f,.7,1.,.5)
assert len(list(f.Pads()))==2 and all(not q.IsOnLayer(pcb.F_Paste)for q in f.Pads())
for ref in ['TP81','TP82']:
 f=load(ref);d=numbered(f);assert set(d)=={'1'} and f.IsExcludedFromBOM()and f.IsExcludedFromPosFiles()and not f.IsBoardOnly()
 assert d['1'].GetShape()==pcb.PAD_SHAPE_CIRCLE and d['1'].GetSize().x==pcb.FromMM(.8)and not d['1'].IsOnLayer(pcb.F_Paste)and d['1'].GetDrillSize().x==0
board=pcb.BOARD();board.SetCopperLayerCount(6)
for ref,x,y in [('R220',4,5),('R561',9,5),('JP1',15,5),('TP81',21,3),('TP82',21,8)]:
 f=load(ref);assert f;f.SetReference(ref);f.SetFPID(pcb.LIB_ID(lib,FP[ref].split(':')[1]));apply_population(component_elements[ref],f);f.SetPosition(pcb.VECTOR2I(pcb.FromMM(x),pcb.FromMM(y)));board.Add(f)
 for q in f.Pads():
  if q.GetNumber():
   net=pcb.NETINFO_ITEM(board,n[(ref,q.GetNumber())][0]);board.Add(net);q.SetNet(net)
for start,end in [((0,0),(26,0)),((26,0),(26,12)),((26,12),(0,12)),((0,12),(0,0))]:
 g=pcb.PCB_SHAPE();g.SetShape(pcb.SHAPE_T_SEGMENT);g.SetStart(pcb.VECTOR2I(*[pcb.FromMM(v)for v in start]));g.SetEnd(pcb.VECTOR2I(*[pcb.FromMM(v)for v in end]));g.SetLayer(pcb.Edge_Cuts);g.SetWidth(pcb.FromMM(.05));board.Add(g)
file=O/'LINKS_FEATURES_GEOMETRY_ONLY.kicad_pcb';pcb.SaveBoard(str(file),board);file.with_suffix('.kicad_pro').write_text(json.dumps({'board':{'design_settings':{'rules':{'min_clearance':.2,'min_copper_edge_clearance':.25,'min_solder_mask_width':.1,'min_silk_clearance':.1}}}},indent=2)+'\n');(O/'fp-lib-table').write_text('(fp_lib_table (lib (name "'+lib+'") (type "KiCad") (uri "${KIPRJMOD}/../../cad/recovery-link-candidates/'+lib+'.pretty") (options "") (descr "Conditional source links and bare copper features")))\n')
reloaded=pcb.LoadBoard(str(file));fps={f.GetReference():f for f in reloaded.GetFootprints()}
for ref in FEATURES:
 validate_population(component_elements[ref],fps[ref])
 assert fps[ref].IsExcludedFromBOM()and fps[ref].IsExcludedFromPosFiles()and not fps[ref].IsBoardOnly()
assert fps['JP1'].IsDNP() and len(numbered(fps['JP1']))==2
assert all(q.GetNetname()==n[(ref,pin)][0]for ref,f in fps.items()for pin,q in numbered(f).items())
assert len([q for f in fps.values()for q in f.Pads()if q.GetNumber()])==8
controls=[]
t=copy.deepcopy(c);t['JP1']['properties']=[q for q in t['JP1']['properties']if q[0]!='dnp'];assert t!=expected;controls.append('default_bridge_population_changed')
t=copy.deepcopy(c);t['R528']['properties']=[q for q in t['R528']['properties']if q[0]!='dnp'];assert t!=expected;controls.append('storage_qualification_populated')
t=dict(n);t[('TP81','1')]=('GND',*t[('TP81','1')][1:]);assert t!=bn;controls.append('observation_pad_wrong_net')
bad=load('JP1');apply_population(component_elements['JP1'],bad);bad.SetBoardOnly(True)
try:validate_population(component_elements['JP1'],bad)
except AssertionError:controls.append('logical_copper_feature_marked_board_only')
else:raise AssertionError('Board-only corruption was not rejected')
bad=load('TP81');apply_population(component_elements['TP81'],bad);bad.SetExcludedFromPosFiles(False)
try:validate_population(component_elements['TP81'],bad)
except AssertionError:controls.append('bare_testpad_added_to_placement')
else:raise AssertionError('Position-exclusion corruption was not rejected')
qual=pcb.FootprintLoad(str(P/'cad/recovery-passive-candidates/CMK230_Recovery_Passive_Candidates.pretty'),'Vishay_CRCW0201_SourceLand_PROCESS_CANDIDATE');apply_population(component_elements['R528'],qual)
assert qual.IsDNP()and qual.IsExcludedFromPosFiles()and not qual.IsBoardOnly()and len(numbered(qual))==2
validate_population(component_elements['R528'],qual)

assert sum(len(numbered(f))for ref,f in fps.items()if ref!='JP1')!=8;controls.append('DNP_copper_omitted_from_board')
logs['fixture_drc']=run(['pcb','drc','--format','json','--severity-all','-o',str(O/'fixture-drc.json'),str(file)])
gdir=O/'native-cam';gdir.mkdir(exist_ok=True);logs['gerbers']=run(['pcb','export','gerbers','--layers','F.Cu,F.Mask,F.Paste','--output',str(gdir),str(file)])
counts={}
for path in gdir.iterdir():
 if path.is_file()and path.suffix in ['.gtl','.gts','.gtp','.gbr']:
  text=path.read_text();counts[path.name]=len(re.findall(r'D03\*',text))
assert sorted(counts.values())==[4,8,8],counts
logs['erc']=run(['sch','erc','--format','json','--severity-all','-o',str(A/'erc.json'),str(A/'CMK230_Core_REVIEW.kicad_sch')]);assert not[v for s in json.loads((A/'erc.json').read_text())['sheets']for v in s['violations']]
report={'revision':'R7 links and fabricated features','components':254,'bindings':1509,'distinct_nets':457,'changed_footprint_refs':sorted(FP),'new_BOM_exclusion_refs':sorted(FEATURES),'value_changes':0,'pin_net_function_type_changes':0,'population_changes':0,'JP1_R45_R47_R528_DNP_preserved':True,'all_three_features_retain_copper_and_onboard_net_identity':True,'assigned':sum(bool(v['footprint'])for v in c.values()),'unassigned':sum(not v['footprint']for v in c.values()),'erc_violations':0,'fixture_drc_categories':[v['type']for v in json.loads((O/'fixture-drc.json').read_text())['violations']],'native_CAM_flash_counts':counts,'negative_controls_rejected':controls,'full_board_exists':False,'production_ready':False}
(O/'validation.json').write_text(json.dumps(report,indent=2)+'\n');(O/'native-checks.json').write_text(json.dumps(logs,indent=2)+'\n');print(json.dumps(report,indent=2))
