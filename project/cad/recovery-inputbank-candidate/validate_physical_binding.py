from pathlib import Path
import xml.etree.ElementTree as E,json,hashlib,copy
import pcbnew
D=Path(__file__).resolve().parent;R=D.parents[1]
def load(p):
 x=E.parse(p); pins={(n.get('ref'),n.get('pin')):(net.get('name'),n.get('pinfunction'),n.get('pintype')) for net in x.findall('.//nets/net') for n in net};comps={c.get('ref'):{'value':c.findtext('value'),'footprint':c.findtext('footprint'),'properties':{p.get('name'):p.get('value') for p in c.findall('property')}}for c in x.findall('.//components/comp')};return pins,comps
old,oc=load(R/'cad/recovery-compact-candidate/master.xml');new,nc=load(D/'master.xml')
expected={'U14':'CMK230_Recovery_Logic_Candidates:TI_DSF0006A_SN74LVC1G97_1x1_P0.35_SourceExample_CANDIDATE','U92':'CMK230_NXP_Archival_Candidates:NXP_SOT1160-1_74AUP2G97_1.4x1.8_P0.4_ArchivalCrosschecked_CANDIDATE'}
def check(p,c):
 assert p==old
 a=copy.deepcopy(c)
 for ref,fp in expected.items():assert a[ref]['footprint']==fp;a[ref]['footprint']=oc[ref]['footprint']
 assert a==oc
 assert 'dnp' in c['R528']['properties'] and not c['R574']['footprint']
check(new,nc)
negative=[]
for name in ['wrong_footprint','lost_DNP','changed_logic_net']:
 p=copy.deepcopy(new);c=copy.deepcopy(nc)
 if name=='wrong_footprint':c['U92']['footprint']=expected['U14']
 elif name=='lost_DNP':c['R528']['properties'].pop('dnp')
 else:p['U92','9']=('GND','VCC','power_in')
 try:check(p,c)
 except AssertionError:negative.append(name)
 else:raise AssertionError(name)
libs={'U14':R/'cad/recovery-footprint-candidates/CMK230_Recovery_Logic_Candidates.pretty','U92':R/'cad/recovery-footprint-candidates/nexperia-archival/CMK230_NXP_Archival_Candidates.pretty'}
bindings=[]
for ref,lib in libs.items():
 f=pcbnew.FootprintLoad(str(lib),expected[ref].split(':')[1]);assert f
 pads=[p for p in f.Pads()if p.GetNumber()];assert len(pads)==(6 if ref=='U14'else 10)
 assert {p.GetNumber() for p in pads}=={n for r,n in new if r==ref}
 for p in pads:bindings.append({'reference':ref,'pad':p.GetNumber(),'net':new[ref,p.GetNumber()][0],'x_mm':pcbnew.ToMM(p.GetPosition().x),'y_mm':pcbnew.ToMM(p.GetPosition().y)})
erc=json.loads((D/'erc.json').read_text());assert not any(s.get('violations') for s in erc['sheets'])
report={'status':'SCHEMATIC_FOOTPRINT_BINDINGS_VERIFIED','components':len(nc),'pin_bindings_unchanged':len(new),'changed_component_fields':['U14.footprint','U92.footprint'],'native_pad_bindings':bindings,'negative_controls':negative,'ERC_violations':0,'R528_DNP':True,'PCB_rebuilt':False,'manufacturing_qualified':False,'sha256':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [D/'master.xml',R/'cad/recovery-compact-candidate/master.xml']}}
(D/'physical-binding-validation.json').write_text(json.dumps(report,indent=2));print(report['status'],len(new),len(bindings))
