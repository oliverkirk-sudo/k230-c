#!/usr/bin/env python3
"""Bounded candidate validation; never writes the baseline project."""
from pathlib import Path
import argparse,copy,csv,hashlib,json,os,shutil,subprocess,xml.etree.ElementTree as E
KEEP={'C203','C210','C211','C216','C217','C220','C225','C230'}
DROP={'C204','C221','C226','C231'}
BYPASS={'C205','C209','C215','C222','C227','C232'}
VALUE='22uF CL31B226KPHNNNE INPUT BANK CANDIDATE'
FP='CMK230_Bulk22_Candidates:Samsung_CL31B226_1206_ReflowMid_SOURCE_CANDIDATE'
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def state(f):
 x=E.parse(f).getroot();c={q.attrib['ref']:{'value':q.findtext('value'),'footprint':q.findtext('footprint'),'libsource':q.find('libsource').attrib,'properties':sorted((v.attrib['name'],v.attrib.get('value',''))for v in q.findall('property'))}for q in x.findall('./components/comp')};n={(q.attrib['ref'],q.attrib['pin']):(v.attrib['name'],q.attrib.get('pinfunction'),q.attrib.get('pintype'))for v in x.findall('./nets/net')for q in v.findall('node')};libs=E.tostring(x.find('libparts'),encoding='unicode');return c,n,libs
p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--runtime',type=Path,required=True);a=p.parse_args();P=a.project.resolve();B=a.baseline.resolve();T=a.runtime.resolve();T.mkdir(parents=True,exist_ok=True);A=P/'cad/recovery-inputbank-candidate';O=P/'recovery/r12-input-bank-candidate';env=os.environ.copy()
for k,z in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data')]:q=T/z;q.mkdir(exist_ok=True);env[k]=str(q)
def run(cmd):
 t=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=120)
 if t.returncode:raise RuntimeError(t.stderr+'\n'+t.stdout)
 return {'returncode':t.returncode,'stdout':t.stdout,'stderr':t.stderr}
# Every already-published source file stays untouched in this alternative branch.
old_files={str(f.relative_to(B)):sha(f)for f in B.rglob('*')if f.is_file()and f.suffix not in['.kicad_prl','.pyc']and '__pycache__'not in f.parts}
assert all((P/k).is_file()and sha(P/k)==v for k,v in old_files.items())
logs={'export':run(['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(A/'master.xml'),str(A/'CMK230_Core_REVIEW.kicad_sch')])}
b,bn,bl=state(B/'cad/recovery-physical-candidate/master.xml');c,n,cl=state(A/'master.xml');expected=copy.deepcopy(b)
for ref in KEEP:
 assert b[ref]['value']=='10uF 10V X7R'and not b[ref]['footprint'];expected[ref]['value']=VALUE;expected[ref]['footprint']=FP
for ref in DROP:del expected[ref]
ne={k:v for k,v in bn.items()if k[0]not in DROP}
def check(cc,nn):
 assert cc==expected,'Unexpected component attribute/value/ref delta'
 assert nn==ne,'Unexpected numbered pin/function/type/net delta'
check(c,n);assert cl==bl,'Symbol pin library changed';assert len(c)==250 and len(n)==1501
for ref in KEEP:assert n[(ref,'1')][0]=='VIN_5V'and n[(ref,'2')][0]=='GND'
for ref in BYPASS:assert c[ref]==b[ref]and b[ref]['value'].startswith('100nF')
for ref in ['R528','R45','R47','JP1']:assert ('dnp','')in c[ref]['properties']
# CSV is an additional generated representation, not an independent electrical source.
rows=list(csv.DictReader((A/'master-pin-assignments.csv').open()));assert not(set(r['reference']for r in rows)&DROP)
for ref in KEEP:assert {(r['pin'],r['net'])for r in rows if r['reference']==ref}=={('1','VIN_5V'),('2','GND')}
logs['erc']=run(['kicad-cli','sch','erc','--format','json','--severity-all','-o',str(A/'erc.json'),str(A/'CMK230_Core_REVIEW.kicad_sch')]);assert not[v for s in json.loads((A/'erc.json').read_text())['sheets']for v in s['violations']]
neg=[]
def reject(label,cc,nn):
 try:check(cc,nn)
 except AssertionError:neg.append(label)
 else:raise AssertionError('Mutation escaped: '+label)
t=copy.deepcopy(c);t['C204']=b['C204'];reject('removed_ref_reintroduced',t,n)
t=copy.deepcopy(c);del t['C205'];reject('mandatory_100nF_bypass_removed',t,n)
t=copy.deepcopy(c);t['C210']['value']='10uF 10V X7R';reject('survivor_value_not_updated',t,n)
t=copy.deepcopy(c);t['C203']['footprint']='wrong:part';reject('wrong_input_footprint',t,n)
t=copy.deepcopy(c);t['R528']['properties']=[v for v in t['R528']['properties']if v[0]!='dnp'];reject('storage_qualification_populated',t,n)
t=dict(n);t[('C220','1')]=('VDD1P1_DDR_IO',*t[('C220','1')][1:]);reject('input_cap_moved_to_output_net',c,t)
# Regenerate from the candidate generator in a new bounded runtime project.
G=T/'generator-reproduction';assert not G.exists(),'Use a new runtime directory for each complete validation'
shutil.copytree(P,G,ignore=shutil.ignore_patterns('__pycache__','*.kicad_prl'))
GA=G/'cad/recovery-inputbank-candidate';logs['generator']=run(['/usr/bin/python3',str(GA/'build_review.py')]);logs['regenerated_export']=run(['kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(GA/'master.xml'),str(GA/'CMK230_Core_REVIEW.kicad_sch')]);gc,gn,gl=state(GA/'master.xml');check(gc,gn);assert gl==bl
assert all(sha(P/k)==v for k,v in old_files.items())
result={'status':'PASS_CONDITIONAL_CIRCUIT_CANDIDATE','baseline_commit':'1e4e2832b2931a4de387179190fd21869681db39','baseline_preserved_files':len(old_files),'existing_project_files_unchanged':True,'candidate_components':250,'candidate_bindings':1501,'distinct_nets':len(set(v[0]for v in n.values())),'changed_values_and_footprints':sorted(KEEP),'removed_references':sorted(DROP),'preserved_100nF_bypasses':sorted(BYPASS),'all_other_values_nets_pin_types_population_preserved':True,'symbol_pin_library_unchanged':True,'assigned':sum(bool(v['footprint'])for v in c.values()),'unassigned':sum(not v['footprint']for v in c.values()),'nominal_input_capacitance_uF':{'baseline':120,'candidate':176},'ERC_violations':0,'generator_reproduces_exact_electrical_contract':True,'negative_controls_rejected':neg,'preferred_baseline_changed':False,'Ceff_and_full_layout_qualified':False,'production_ready':False}
(O/'validation.json').write_text(json.dumps(result,indent=2)+'\n');(O/'native-checks.json').write_text(json.dumps(logs,indent=2)+'\n');print(json.dumps(result,indent=2))
