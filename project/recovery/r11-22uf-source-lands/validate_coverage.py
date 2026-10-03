from pathlib import Path
import argparse,os,json,subprocess,copy,re,xml.etree.ElementTree as ET
import pcbnew as pcb
p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--runtime',type=Path,required=True);a=p.parse_args();P=a.project.resolve();B=a.baseline.resolve();A=P/'cad/recovery-physical-candidate';O=P/'recovery/r11-22uf-source-lands';env=os.environ.copy()
for k,n in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data')]:
 d=a.runtime/n;d.mkdir(parents=True,exist_ok=True);env[k]=str(d.resolve())
FP=json.loads((O/'assignments.json').read_text())
def run(args):
 t=subprocess.run(['kicad-cli',*args],env=env,capture_output=True,text=True,timeout=60);assert t.returncode in[0,5],t.stderr;return {'returncode':t.returncode,'stdout':t.stdout,'stderr':t.stderr}
def graph(f):
 x=ET.parse(f).getroot();c={e.attrib['ref']:{'value':e.findtext('value'),'footprint':e.findtext('footprint'),'properties':sorted((q.attrib['name'],q.attrib.get('value',''))for q in e.findall('property'))}for e in x.findall('components/comp')};n={(q.attrib['ref'],q.attrib['pin']):(e.attrib['name'],q.attrib.get('pinfunction'),q.attrib.get('pintype'))for e in x.findall('nets/net')for q in e.findall('node')};return c,n
logs={'netlist':run(['sch','export','netlist','--format','kicadxml','-o',str(A/'master.xml'),str(A/'CMK230_Core_REVIEW.kicad_sch')])};bc,bn=graph(B/'cad/recovery-physical-candidate/master.xml');c,n=graph(A/'master.xml');expected=copy.deepcopy(bc)
for ref,v in FP.items():expected[ref]['footprint']=v
assert c==expected and n==bn and len(c)==254 and len(n)==1509
assert all(('dnp','')in c[r]['properties']for r in ['JP1','R45','R47','R528'])
lib='CMK230_Bulk22_Candidates';ld=P/'cad/recovery-bulk22-candidates'/(lib+'.pretty')
def load(name):
 f=pcb.FootprintLoad(str(ld),name);assert f;return f
def dims(f,layer):return sorted((round(pcb.ToMM(q.GetPosition().x),6),round(pcb.ToMM(q.GetSize().x),6),round(pcb.ToMM(q.GetSize().y),6))for q in f.Pads()if q.IsOnLayer(layer))
board=pcb.BOARD();board.SetCopperLayerCount(6);entries=[]
for name,ref,pad,center,x,y in [('Samsung_CL31B226_1206_ReflowMid_SOURCE_CANDIDATE','C206',(1.25,1.8),1.475,8,6)]:
 f=load(name);assert dims(f,pcb.F_Cu)==[(-center,*pad),(center,*pad)]
 assert dims(f,pcb.F_Paste)==dims(f,pcb.F_Cu)
 assert {q.GetNumber()for q in f.Pads()if q.GetNumber()}=={'1','2'}
 entries.append((f,name,ref,x,y))
for f,name,ref,x,y in entries:
 f.SetReference(ref);f.SetFPID(pcb.LIB_ID(lib,name));f.SetPosition(pcb.VECTOR2I(pcb.FromMM(x),pcb.FromMM(y)));board.Add(f)
 for q in f.Pads():
  if q.GetNumber():
   # Unique diagnostic net names avoid pretending this comparison fixture is a connected circuit.
   net=pcb.NETINFO_ITEM(board,ref+'_'+q.GetNumber());board.Add(net);q.SetNet(net)
for s,e in [((0,0),(20,0)),((20,0),(20,13)),((20,13),(0,13)),((0,13),(0,0))]:
 g=pcb.PCB_SHAPE();g.SetShape(pcb.SHAPE_T_SEGMENT);g.SetStart(pcb.VECTOR2I(*[pcb.FromMM(v)for v in s]));g.SetEnd(pcb.VECTOR2I(*[pcb.FromMM(v)for v in e]));g.SetLayer(pcb.Edge_Cuts);g.SetWidth(pcb.FromMM(.05));board.Add(g)
f=O/'BULK22_LANDS_GEOMETRY_ONLY.kicad_pcb';pcb.SaveBoard(str(f),board);f.with_suffix('.kicad_pro').write_text(json.dumps({'board':{'design_settings':{'rules':{'min_clearance':.2,'min_copper_edge_clearance':.25,'min_solder_mask_width':.1,'min_silk_clearance':.1}}}},indent=2)+'\n');(O/'fp-lib-table').write_text('(fp_lib_table (lib (name "'+lib+'") (type "KiCad") (uri "${KIPRJMOD}/../../cad/recovery-bulk22-candidates/'+lib+'.pretty") (options "") (descr "Conditional source patterns")))\n')
logs['drc']=run(['pcb','drc','--format','json','--severity-all','-o',str(O/'fixture-drc.json'),str(f)]);report=json.loads((O/'fixture-drc.json').read_text());assert not report['violations'],report['violations']
g=O/'native-cam';g.mkdir(exist_ok=True);logs['cam']=run(['pcb','export','gerbers','--layers','F.Cu,F.Mask,F.Paste','--output',str(g),str(f)])
counts={x.name:len(re.findall(r'D03\*',x.read_text()))for x in g.iterdir()if x.suffix in['.gtl','.gts','.gtp']};assert list(counts.values())==[2,2,2],counts
logs['erc']=run(['sch','erc','--format','json','--severity-all','-o',str(A/'erc.json'),str(A/'CMK230_Core_REVIEW.kicad_sch')]);assert not[v for s in json.loads((A/'erc.json').read_text())['sheets']for v in s['violations']]
# Wrong rail and nominal mutations must not pass the exact graph contract.
t=dict(n);t[('C206','1')]=('VDD0P8_KPU',*t[('C206','1')][1:]);assert t!=bn
t=dict(n);t[('C540','1')]=('VDD1P8',*t[('C540','1')][1:]);assert t!=bn
t=copy.deepcopy(c);t['C206']['value']='47uF';assert t!=expected
f=load('Samsung_CL31B226_1206_ReflowMid_SOURCE_CANDIDATE');q=next(q for q in f.Pads()if q.GetNumber()=='1');q.SetSize(pcb.VECTOR2I(pcb.FromMM(.4),pcb.FromMM(.5)));assert dims(f,pcb.F_Cu)!=[(-1.475,1.25,1.8),(1.475,1.25,1.8)]
out={'revision':'R11','components':254,'bindings':1509,'distinct_nets':457,'footprint_changes':sorted(FP),'value_or_population_changes':0,'assigned':sum(bool(v['footprint'])for v in c.values()),'unassigned':sum(not v['footprint']for v in c.values()),'ERC_violations':0,'fixture_rule_violations':len(report['violations']),'fixture_unconnected':len(report['unconnected_items']),'CAM_flashes':counts,'negative_controls':['CPU_KPU_rail_mixup','DRAM_rail_mixup','changed_nominal_value','wrong_land_geometry'],'six_layer_production_stack_approved':False,'full_core_layout_exists':False,'production_ready':False};(O/'validation.json').write_text(json.dumps(out,indent=2)+'\n');(O/'native-checks.json').write_text(json.dumps(logs,indent=2)+'\n');print(json.dumps(out,indent=2))
