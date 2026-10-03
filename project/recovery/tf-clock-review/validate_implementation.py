from pathlib import Path
import json,hashlib,xml.etree.ElementTree as E,copy
R=Path(__file__).resolve().parents[2];a=R/'cad/high-temp-candidate/master.xml';b=R/'cad/recovery-tf-candidate/master.xml'
def parse(p):
 x=E.parse(p);pins={(n.get('ref'),n.get('pin')):(net.get('name'),n.get('pinfunction'),n.get('pintype'))for net in x.findall('.//nets/net')for n in net};comps={c.get('ref'):{'value':c.findtext('value'),'footprint':c.findtext('footprint'),'properties':{p.get('name'):p.get('value')for p in c.findall('property')}}for c in x.findall('.//components/comp')};return pins,comps
old,oc=parse(a);new,nc=parse(b)
def check(p,c):
 assert {k:v for k,v in p.items()if k[0]!='R574'}==old
 assert {k:v for k,v in c.items()if k!='R574'}==oc
 assert {k:v[0]for k,v in p.items()if k[0]=='R574'}=={('R574','1'):'TF_HOST_CLK',('R574','2'):'GND'}
 assert c['R574']['value'].startswith('10k CRCW020110K0FKED') and not c['R574']['footprint'] and 'dnp'not in c['R574']['properties']
 assert 'dnp'in c['R528']['properties']
 assert {k for k,v in p.items()if v[0]=='TF_HOST_CLK'}=={('U11','1'),('U95','5'),('R574','1')}
 assert p['U95','8'][0]==p['J1','21'][0]=='TFCARD_CLK'
 return True
check(new,nc);negative=[]
for case in ['missing_pulldown','pulldown_to_supply','wrong_clock_side','default_strap_populated']:
 p=copy.deepcopy(new);c=copy.deepcopy(nc)
 if case=='missing_pulldown':p.pop(('R574','2'))
 elif case=='pulldown_to_supply':p['R574','2']=('VDD1P8','~','passive')
 elif case=='wrong_clock_side':p['R574','1']=('EMMC_CLK','~','passive')
 else:c['R528']['properties'].pop('dnp')
 try:check(p,c)
 except AssertionError:negative.append(case)
 else:raise AssertionError(case)
result={'status':'SOURCE_BACKED_CANDIDATE_SCHEMATIC_DELTA_VERIFIED','old_pin_bindings_preserved':len(old),'old_components_preserved':len(oc),'new_pin_bindings':len(new),'new_components':len(nc),'added_component':'R574','added_bindings':{'1':'TF_HOST_CLK','2':'GND'},'footprint_unselected':True,'negative_controls_rejected':negative,'R528_remains_DNP':True,'source_hashes':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in[a,b]},'electrical_qualification':False,'open_gates':['CLKA numerical leakage overtemperature','off-switch leakage applicability','activeclockdriver margin and timing','off-channel capacitivefeedthrough','partialpower externalclock behavior','actual resistorland and effectiveboard geometry']}
(R/'recovery/tf-clock-review/implementation-validation.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
