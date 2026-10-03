from pathlib import Path
import argparse,os,json,subprocess,copy,xml.etree.ElementTree as ET
import pcbnew as pcb
p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--runtime',type=Path,required=True);a=p.parse_args();P=a.project.resolve();B=a.baseline.resolve();A=P/'cad/recovery-physical-candidate';O=P/'recovery/r6-passive-coverage';env=os.environ.copy()
for k,n in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data')]:
 d=a.runtime/n;d.mkdir(parents=True,exist_ok=True);env[k]=str(d.resolve())
FP=json.loads((O/'assignments.json').read_text())
def run(args):
 r=subprocess.run(['kicad-cli',*args],env=env,capture_output=True,text=True,timeout=60);assert r.returncode in [0,5],r.stderr;return {'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
def graph(f):
 x=ET.parse(f).getroot();c={e.attrib['ref']:{'value':e.findtext('value'),'footprint':e.findtext('footprint'),'properties':sorted((q.attrib['name'],q.attrib.get('value',''))for q in e.findall('property'))}for e in x.findall('components/comp')};n={(q.attrib['ref'],q.attrib['pin']):(e.attrib['name'],q.attrib.get('pinfunction'),q.attrib.get('pintype'))for e in x.findall('nets/net')for q in e.findall('node')};return c,n
logs={'netlist':run(['sch','export','netlist','--format','kicadxml','-o',str(A/'master.xml'),str(A/'CMK230_Core_REVIEW.kicad_sch')])}
bc,bn=graph(B/'cad/recovery-physical-candidate/master.xml');c,n=graph(A/'master.xml');ex=copy.deepcopy(bc)
for ref,v in FP.items():ex[ref]['footprint']=v
assert len(FP)==26 and c==ex and n==bn and len(c)==254 and len(n)==1509
assert all(('dnp','')in c[r]['properties']for r in ['R45','R47','R528'])
assert n[('L21','1')][0]=='SW_CORE'and n[('L21','2')][0]=='VDD0P8_CORE'
assert c['R33']['value'].startswith('270k') and all(c['R'+str(i)]['value'].startswith('43k')for i in range(563,571))
lib,name=FP['L21'].split(':');ld=P/'cad/recovery-inductor-candidates'/(lib+'.pretty');f=pcb.FootprintLoad(str(ld),name);assert f
def geometry(fp):
 pads={p.GetNumber():p for p in fp.Pads()if p.GetNumber()}
 if set(pads)!={'1','2'}:return False
 for number,x in [('1',1.185),('2',-1.185)]:
  q=pads[number]
  if abs(pcb.ToMM(q.GetPosition().x)-x)>1e-6 or q.GetPosition().y!=0 or abs(pcb.ToMM(q.GetSize().x)-.98)>1e-6 or abs(pcb.ToMM(q.GetSize().y)-3.4)>1e-6:return False
  if not q.IsOnLayer(pcb.F_Cu)or not q.IsOnLayer(pcb.F_Mask)or q.IsOnLayer(pcb.F_Paste)or abs(pcb.ToMM(q.GetLocalSolderMaskMargin())-.05)>1e-6:return False
 paste=[p for p in fp.Pads()if not p.GetNumber()]
 return len(paste)==2 and all(q.IsOnLayer(pcb.F_Paste)and not q.IsOnLayer(pcb.F_Cu)and q.GetSize().x==pcb.FromMM(.98)and q.GetSize().y==pcb.FromMM(3.4)for q in paste)
assert geometry(f)
for layer,half in [(pcb.F_Fab,2.15),(pcb.F_CrtYd,2.4)]:
 g=[x for x in f.GraphicalItems() if x.GetLayer()==layer and hasattr(x,'GetStart')]
 xs=[pcb.ToMM(v.x)for x in g for v in [x.GetStart(),x.GetEnd()]];ys=[pcb.ToMM(v.y)for x in g for v in [x.GetStart(),x.GetEnd()]]
 assert [round(min(xs),6),round(min(ys),6),round(max(xs),6),round(max(ys),6)]==[-half,-half,half,half]
assert any(x.GetLayer()==pcb.F_Fab and hasattr(x,'GetStart') and x.GetStart().x==pcb.FromMM(1.95) and x.GetEnd().x==pcb.FromMM(1.95) for x in f.GraphicalItems())
controls=[]
bad=pcb.FootprintLoad(str(ld),name)
for q in bad.Pads():
 if q.GetNumber()=='1':q.SetPosition(pcb.VECTOR2I(pcb.FromMM(-1.185),0))
 if q.GetNumber()=='2':q.SetPosition(pcb.VECTOR2I(pcb.FromMM(1.185),0))
assert not geometry(bad);controls.append('winding_start_pins_mirrored')
t=copy.deepcopy(c);t['R45']['properties']=[v for v in t['R45']['properties']if v[0]!='dnp'];assert t!=ex;controls.append('BOOT_DNP_populated')
t=copy.deepcopy(c);t['R203']['value']='10k';assert t!=ex;controls.append('PG_pull_value_changed')
t=dict(n);t[('L21','1')]=n[('L21','2')];assert t!=bn;controls.append('SW_and_output_confused')
board=pcb.BOARD();board.SetCopperLayerCount(6);f.SetReference('L21');f.SetFPID(pcb.LIB_ID(lib,name));f.SetPosition(pcb.VECTOR2I(pcb.FromMM(5),pcb.FromMM(5)));board.Add(f)
for q in f.Pads():
 if q.GetNumber():
  net=pcb.NETINFO_ITEM(board,'SW_CORE'if q.GetNumber()=='1'else 'VDD0P8_CORE');board.Add(net);q.SetNet(net)
for start,end in [((0,0),(10,0)),((10,0),(10,10)),((10,10),(0,10)),((0,10),(0,0))]:
 g=pcb.PCB_SHAPE();g.SetShape(pcb.SHAPE_T_SEGMENT);g.SetStart(pcb.VECTOR2I(*[pcb.FromMM(v)for v in start]));g.SetEnd(pcb.VECTOR2I(*[pcb.FromMM(v)for v in end]));g.SetLayer(pcb.Edge_Cuts);g.SetWidth(pcb.FromMM(.05));board.Add(g)
file=O/'L21_SIX_LAYER_GEOMETRY_ONLY.kicad_pcb';pcb.SaveBoard(str(file),board);pr={'board':{'design_settings':{'rules':{'min_clearance':.2,'min_copper_edge_clearance':.25,'min_silk_clearance':.1,'min_solder_mask_width':.1}}}};file.with_suffix('.kicad_pro').write_text(json.dumps(pr,indent=2)+'\n');(O/'fp-lib-table').write_text('(fp_lib_table (lib (name "'+lib+'") (type "KiCad") (uri "${KIPRJMOD}/../../cad/recovery-inductor-candidates/'+lib+'.pretty") (options "") (descr "Conditional manufacturer copper")))\n')
logs['fixture_drc']=run(['pcb','drc','--format','json','--severity-all','-o',str(O/'fixture-drc.json'),str(file)])
negative=O/'L21_NEGATIVE_CLEARANCE.kicad_pcb';pcb.SaveBoard(str(negative),board);pr['board']['design_settings']['rules']['min_clearance']=1.4;negative.with_suffix('.kicad_pro').write_text(json.dumps(pr,indent=2)+'\n');logs['negative_drc']=run(['pcb','drc','--format','json','--severity-all','-o',str(O/'negative-drc.json'),str(negative)]);assert any(v['type']=='clearance'for v in json.loads((O/'negative-drc.json').read_text())['violations'])
logs['erc']=run(['sch','erc','--format','json','--severity-all','-o',str(A/'erc.json'),str(A/'CMK230_Core_REVIEW.kicad_sch')]);assert not[v for s in json.loads((A/'erc.json').read_text())['sheets']for v in s['violations']]
report={'revision':'R6 passive footprint coverage','components':254,'bindings':1509,'distinct_nets':457,'changed_footprint_refs':sorted(FP),'value_changes':0,'pin_net_function_type_changes':0,'population_changes':0,'R45_R47_R528_DNP_preserved':True,'assigned':sum(bool(v['footprint'])for v in c.values()),'unassigned':sum(not v['footprint']for v in c.values()),'erc_violations':0,'fixture_drc_categories':[v['type']for v in json.loads((O/'fixture-drc.json').read_text())['violations']],'negative_controls_rejected':controls+['copper_clearance_1p4mm_above_1p39mm_gap'],'L21_start_terminal':'pad1 at +X marked side = SW_CORE','full_board_exists':False,'production_ready':False}
(O/'validation.json').write_text(json.dumps(report,indent=2)+'\n');(O/'native-checks.json').write_text(json.dumps(logs,indent=2)+'\n');print(json.dumps(report,indent=2))
