from pathlib import Path
import json,os,subprocess,hashlib,xml.etree.ElementTree as ET,copy
import pcbnew as pcb
import argparse
p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--runtime',type=Path,required=True);args=p.parse_args()
P=args.project.resolve();B=args.baseline.resolve();R=args.runtime.resolve();A=P/'cad/recovery-physical-candidate';O=P/'recovery/r3-physical-coverage';O.mkdir(exist_ok=True)
env=os.environ.copy()
for k,n in [('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data'),('XDG_CACHE_HOME','cache')]:
 p=R/'runtime'/n;p.mkdir(parents=True,exist_ok=True);env[k]=str(p)
fp=json.loads((O/'assignments.json').read_text())
def run(args):
 p=subprocess.run(['kicad-cli',*args],env=env,capture_output=True,text=True,timeout=60)
 assert p.returncode in [0,5],p.stderr
 return {'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
def parse(f):
 x=ET.parse(f).getroot()
 c={e.attrib['ref']:{'value':e.findtext('value'),'footprint':e.findtext('footprint'),'properties':sorted((p.attrib['name'],p.attrib.get('value',''))for p in e.findall('property'))} for e in x.findall('components/comp')}
 n={(a.attrib['ref'],a.attrib['pin']):(net.attrib['name'],a.attrib.get('pinfunction'),a.attrib.get('pintype'))for net in x.findall('nets/net')for a in net.findall('node')}
 return c,n
log={}
log['netlist']=run(['sch','export','netlist','--format','kicadxml','-o',str(A/'master.xml'),str(A/'CMK230_Core_REVIEW.kicad_sch')])
bc,bn=parse(B/'cad/recovery-physical-candidate/master.xml');c,n=parse(A/'master.xml')
assert len(c)==254 and len(n)==1509 and n==bn
expected=copy.deepcopy(bc)
for ref,v in fp.items():expected[ref]['footprint']=v
assert c==expected and ('dnp','') in c['R528']['properties']
neg=[]
for title,ref,field,val in [('lost-DNP','R528','properties',[]),('wrong-inductor','L22','footprint',fp['L24']),('value-change','R574','value','100k')]:
 altered=copy.deepcopy(c);altered[ref][field]=val;assert altered!=expected;neg.append(title)
bad=dict(n);bad[('R574','1')]=('GND',*bad[('R574','1')][1:]);assert bad!=bn;neg.append('miswired-clock-bias')
lib=P/'cad/recovery-passive-candidates/CMK230_Recovery_Passive_Candidates.pretty';name=fp['R574'].split(':')[1]
foot=pcb.FootprintLoad(str(lib),name);assert foot
numbered={p.GetNumber():p for p in foot.Pads() if p.GetNumber()}
assert set(numbered)=={'1','2'}
for num,x in [('1',-.255),('2',.255)]:
 p=numbered[num];assert abs(pcb.ToMM(p.GetPosition().x)-x)<1e-6
 assert abs(pcb.ToMM(p.GetSize().x)-.28)<1e-6 and abs(pcb.ToMM(p.GetSize().y)-.43)<1e-6
 assert p.IsOnLayer(pcb.F_Cu) and p.IsOnLayer(pcb.F_Mask) and not p.IsOnLayer(pcb.F_Paste)
 assert abs(pcb.ToMM(p.GetLocalSolderMaskMargin())-.025)<1e-6
paste=[p for p in foot.Pads() if not p.GetNumber()];assert len(paste)==2 and all(p.IsOnLayer(pcb.F_Paste) and not p.IsOnLayer(pcb.F_Cu) for p in paste)
board=pcb.BOARD();board.SetCopperLayerCount(6);foot.SetReference('R574');foot.SetPosition(pcb.VECTOR2I(pcb.FromMM(5),pcb.FromMM(5)));board.Add(foot)
for pad in numbered.values():
 net=pcb.NETINFO_ITEM(board,'TF_HOST_CLK' if pad.GetNumber()=='1' else 'GND');board.Add(net);pad.SetNet(net)
for a,b in [((0,0),(10,0)),((10,0),(10,10)),((10,10),(0,10)),((0,10),(0,0))]:
 line=pcb.PCB_SHAPE();line.SetShape(pcb.SHAPE_T_SEGMENT);line.SetStart(pcb.VECTOR2I(*[pcb.FromMM(v)for v in a]));line.SetEnd(pcb.VECTOR2I(*[pcb.FromMM(v)for v in b]));line.SetLayer(pcb.Edge_Cuts);line.SetWidth(pcb.FromMM(.05));board.Add(line)
fixture=O/'CRCW0201_SIX_LAYER_GEOMETRY_ONLY.kicad_pcb';pcb.SaveBoard(str(fixture),board)
pro={'board':{'design_settings':{'rules':{'min_clearance':.2,'min_copper_edge_clearance':.25,'min_courtyard_clearance':.05,'min_silk_clearance':.1,'min_solder_mask_width':.1}}},'meta':{'filename':fixture.with_suffix('.kicad_pro').name,'version':1}}
fixture.with_suffix('.kicad_pro').write_text(json.dumps(pro,indent=2)+'\n')
table='(fp_lib_table (lib (name "CMK230_Recovery_Passive_Candidates") (type "KiCad") (uri "${KIPRJMOD}/../../cad/recovery-passive-candidates/CMK230_Recovery_Passive_Candidates.pretty") (options "") (descr "Conditional source lands")))\n';(O/'fp-lib-table').write_text(table)
log['fixture_drc']=run(['pcb','drc','--format','json','--severity-all','-o',str(O/'fixture-drc.json'),str(fixture)])
negative=O/'CRCW0201_NEGATIVE_CLEARANCE.kicad_pcb';pcb.SaveBoard(str(negative),board);p=copy.deepcopy(pro);p['board']['design_settings']['rules']['min_clearance']=.24;negative.with_suffix('.kicad_pro').write_text(json.dumps(p,indent=2)+'\n')
log['negative_drc']=run(['pcb','drc','--format','json','--severity-all','-o',str(O/'negative-drc.json'),str(negative)])
negd=json.loads((O/'negative-drc.json').read_text());assert any(v['type']=='clearance' for v in negd['violations'])
log['erc']=run(['sch','erc','--format','json','--severity-all','-o',str(A/'erc.json'),str(A/'CMK230_Core_REVIEW.kicad_sch')]);erc=json.loads((A/'erc.json').read_text());assert not [v for s in erc['sheets']for v in s['violations']]
report={'revision':'R3 physical coverage candidate','components':254,'pin_bindings':1509,'changed_footprint_refs':sorted(fp),'assigned':sum(bool(x['footprint'])for x in c.values()),'unassigned':sum(not x['footprint']for x in c.values()),'binding_differences':0,'R528_DNP_preserved':True,'negative_controls_rejected':neg,'erc_violations':0,'fixture_drc_categories':[v['type']for v in json.loads((O/'fixture-drc.json').read_text())['violations']],'production_ready':False,'full_six_layer_board_exists':False}
(O/'validation.json').write_text(json.dumps(report,indent=2)+'\n');(O/'native-checks.json').write_text(json.dumps(log,indent=2)+'\n');print(json.dumps(report,indent=2))
