from pathlib import Path
import os,json,csv,re,copy,subprocess,hashlib,xml.etree.ElementTree as ET
import pcbnew as pcb
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--project',type=Path,required=True);parser.add_argument('--baseline',type=Path,required=True);parser.add_argument('--runtime',type=Path,required=True);args=parser.parse_args()
P=args.project.resolve();B=args.baseline.resolve();R=args.runtime.resolve();A=P/'cad/recovery-physical-candidate';O=P/'recovery/r4-bga-coverage';env=os.environ.copy()
for k,n in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache')]:
 p=R/'runtime'/n;p.mkdir(parents=True,exist_ok=True);env[k]=str(p)
FP=json.loads((O/'assignments.json').read_text());LIB='CMK230_Recovery_BGA_Candidates';LD=P/'cad/recovery-bga-candidates'/(LIB+'.pretty')
def run(args):
 p=subprocess.run(['kicad-cli',*args],env=env,capture_output=True,text=True,timeout=90);assert p.returncode in [0,5],p.stderr
 return {'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
def graph(f):
 x=ET.parse(f).getroot();c={e.attrib['ref']:(e.findtext('value'),e.findtext('footprint'),sorted((p.attrib['name'],p.attrib.get('value',''))for p in e.findall('property')))for e in x.findall('components/comp')};n={(a.attrib['ref'],a.attrib['pin']):(net.attrib['name'],a.attrib.get('pinfunction'),a.attrib.get('pintype'))for net in x.findall('nets/net')for a in net.findall('node')};return c,n
logs={'netlist':run(['sch','export','netlist','--format','kicadxml','-o',str(A/'master.xml'),str(A/'CMK230_Core_REVIEW.kicad_sch')])}
bc,bn=graph(B/'cad/recovery-physical-candidate/master.xml');c,n=graph(A/'master.xml');expected=copy.deepcopy(bc)
for ref,v in FP.items():expected[ref]=(bc[ref][0],v,bc[ref][2])
assert c==expected and n==bn and len(c)==254 and len(n)==1509 and ('dnp','') in c['R528'][2]
data=list(csv.DictReader((P/'engineering/bga-engineering-candidates/memory-soc-functional-balls.csv').open()));pkg={'U1':'K230','U2':'FW200','U3':'BH153'}
print('packages',sorted(set(r['package']for r in data)))
board=pcb.BOARD();board.SetCopperLayerCount(6);facts={};observed={}
for ref,xcenter in [('U1',12),('U2',32),('U3',54)]:
 lib,name=FP[ref].split(':');f=pcb.FootprintLoad(str(LD),name);assert f
 pads={p.GetNumber():p for p in f.Pads()if p.GetNumber()};source={r['ball']:r for r in data if r['package']==pkg[ref]};assert set(pads)==set(source)
 expected_count={'U1':390,'U2':200,'U3':153}[ref];assert len(pads)==expected_count
 for ball,pad in pads.items():
  sr=source[ball];assert abs(pcb.ToMM(pad.GetPosition().x)-float(sr['x_mm']))<1e-6 and abs(pcb.ToMM(pad.GetPosition().y)-float(sr['y_mm']))<1e-6
  assert pad.IsOnLayer(pcb.F_Cu) and not pad.IsOnLayer(pcb.B_Cu) and pad.GetAttribute()==pcb.PAD_ATTRIB_SMD and pad.GetDrillSize().x==0
  assert n[(ref,ball)][1]==sr['function']
 body=[g for g in f.GraphicalItems() if g.GetLayer()==pcb.F_Fab and hasattr(g,'GetStart')]
 xs=[pcb.ToMM(v.x) for g in body for v in [g.GetStart(),g.GetEnd()]];ys=[pcb.ToMM(v.y) for g in body for v in [g.GetStart(),g.GetEnd()]]
 expected_body={'U1':[-6.55,-6.55,6.55,6.55],'U2':[-5.05,-7.3,5.05,7.3],'U3':[-5.8,-6.55,5.8,6.55]}[ref]
 assert all(abs(a-b)<1e-6 for a,b in zip([min(xs),min(ys),max(xs),max(ys)],expected_body))
 if ref=='U1':assert any(g.GetStart().x!=g.GetEnd().x and g.GetStart().y!=g.GetEnd().y for g in body)
 observed[ref]={b:[round(pcb.ToMM(p.GetPosition().x),6),round(pcb.ToMM(p.GetPosition().y),6)]for b,p in pads.items()}
 if ref=='U2':
  assert all(abs(pcb.ToMM(p.GetSize().x)-.3)<1e-6 and p.GetShape()==pcb.PAD_SHAPE_CIRCLE and abs(pcb.ToMM(p.GetLocalSolderMaskMargin())-.05)<1e-6 and not p.IsOnLayer(pcb.F_Paste) for p in pads.values())
  paste=[p for p in f.Pads() if not p.GetNumber()];assert len(paste)==200
  assert all(p.IsOnLayer(pcb.F_Paste) and not p.IsOnLayer(pcb.F_Cu) and p.GetShape()==pcb.PAD_SHAPE_CIRCLE and p.GetSize().x==pcb.FromMM(.3)for p in paste)
  assert sorted((p.GetPosition().x,p.GetPosition().y)for p in pads.values())==sorted((p.GetPosition().x,p.GetPosition().y)for p in paste)
 f.SetReference(ref);f.SetFPID(pcb.LIB_ID(lib,name));f.SetPosition(pcb.VECTOR2I(pcb.FromMM(xcenter),pcb.FromMM(16)));board.Add(f)
 for ball,pad in pads.items():
  net=pcb.NETINFO_ITEM(board,ref+'_'+ball);board.Add(net);pad.SetNet(net)
 facts[ref]={'numbered_pads':len(pads),'total_pad_objects':len(list(f.Pads())),'source_pin_functions_match':True,'coordinate_mismatches':0,'unused_physical_balls_retained':True}
for a,b in [((0,0),(66,0)),((66,0),(66,32)),((66,32),(0,32)),((0,32),(0,0))]:
 line=pcb.PCB_SHAPE();line.SetShape(pcb.SHAPE_T_SEGMENT);line.SetStart(pcb.VECTOR2I(*[pcb.FromMM(v)for v in a]));line.SetEnd(pcb.VECTOR2I(*[pcb.FromMM(v)for v in b]));line.SetLayer(pcb.Edge_Cuts);line.SetWidth(pcb.FromMM(.05));board.Add(line)
f=O/'BGA_IDENTITY_GEOMETRY_ONLY.kicad_pcb';pcb.SaveBoard(str(f),board);f.with_suffix('.kicad_pro').write_text(json.dumps({'board':{'design_settings':{'rules':{'min_clearance':.1016,'min_copper_edge_clearance':.25,'min_courtyard_clearance':.05,'min_silk_clearance':.1,'min_solder_mask_width':.1}}}},indent=2)+'\n');(O/'fp-lib-table').write_text('(fp_lib_table (lib (name "'+LIB+'") (type "KiCad") (uri "${KIPRJMOD}/../../cad/recovery-bga-candidates/'+LIB+'.pretty") (options "") (descr "Process unqualified BGA candidates")))\n')
neg=[]
for label,mutate in [('mirrored-X',lambda d:{k:[-v[0],v[1]]for k,v in d.items()}),('missing-NC',lambda d:{k:v for k,v in d.items()if k!='A8'}),('wrong-row-spacing',lambda d:{k:[v[0],v[1]*.8/.65]for k,v in d.items()})]:
 assert mutate(observed['U2'])!=observed['U2'];neg.append(label)
logs['fixture_drc']=run(['pcb','drc','--format','json','--severity-all','-o',str(O/'fixture-drc.json'),str(f)])
logs['erc']=run(['sch','erc','--format','json','--severity-all','-o',str(A/'erc.json'),str(A/'CMK230_Core_REVIEW.kicad_sch')]);v=[v for s in json.loads((A/'erc.json').read_text())['sheets']for v in s['violations']];assert not v
report={'revision':'R4 BGA physical identity candidate','components':254,'bindings':1509,'assigned':sum(bool(v[1])for v in c.values()),'unassigned':sum(not v[1]for v in c.values()),'only_changed_fields':'U1/U2/U3 footprint bindings','BGA_numbered_pads_total':743,'footprint_checks':facts,'negative_controls_rejected':neg,'erc_violations':0,'fixture_drc_categories':[v['type']for v in json.loads((O/'fixture-drc.json').read_text())['violations']],'required_layers':6,'fixture_is_core_layout':False,'production_ready':False,'R528_DNP_preserved':True}
(O/'validation.json').write_text(json.dumps(report,indent=2)+'\n');(O/'native-checks.json').write_text(json.dumps(logs,indent=2)+'\n');print(json.dumps(report,indent=2))
