from pathlib import Path
import argparse,os,subprocess,json,xml.etree.ElementTree as ET,copy
p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True);p.add_argument('--runtime',type=Path,required=True);a=p.parse_args();P=a.project.resolve();B=a.baseline.resolve();O=P/'recovery/r5-dat43';A=P/'cad/recovery-physical-candidate';env=os.environ.copy()
for k,n in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data')]:
 d=a.runtime/n;d.mkdir(parents=True,exist_ok=True);env[k]=str(d.resolve())
change=json.loads((O/'changes.json').read_text());refs=change['refs']
def run(args):
 r=subprocess.run(['kicad-cli',*args],env=env,capture_output=True,text=True,timeout=60);assert r.returncode==0,r.stderr
 return {'stdout':r.stdout,'stderr':r.stderr,'returncode':r.returncode}
def graph(f):
 x=ET.parse(f).getroot();c={e.attrib['ref']:{'value':e.findtext('value'),'footprint':e.findtext('footprint'),'properties':sorted((q.attrib['name'],q.attrib.get('value',''))for q in e.findall('property'))}for e in x.findall('components/comp')};n={(q.attrib['ref'],q.attrib['pin']):(e.attrib['name'],q.attrib.get('pinfunction'),q.attrib.get('pintype'))for e in x.findall('nets/net')for q in e.findall('node')};return c,n
logs={'netlist':run(['sch','export','netlist','--format','kicadxml','-o',str(A/'master.xml'),str(A/'CMK230_Core_REVIEW.kicad_sch')])}
bc,bn=graph(B/'cad/recovery-physical-candidate/master.xml');c,n=graph(A/'master.xml');ex=copy.deepcopy(bc)
for ref in refs:ex[ref]['value']=change['new_value'];ex[ref]['footprint']=change['new_footprint']
def circuit_ok(c,n):
 return c==ex and n==bn and len(c)==254 and len(n)==1509 and all(n[(r,'1')][0]=='EMMC_DAT'+str(i) and n[(r,'2')][0]=='VEMMC_IO' for i,r in enumerate(refs)) and ('dnp','')in c['R528']['properties']
assert circuit_ok(c,n)
def range_ok(nom,total):return nom*(1-total)>=10000 and nom*(1+total)<=50000
assert range_ok(43000,.1) and not range_ok(47000,.1) and not range_ok(43000,.2)
controls=[]
t=copy.deepcopy(c);t['R563']['value']=bc['R563']['value'];assert not circuit_ok(t,n);controls.append('one_DAT_left_at47k')
t=copy.deepcopy(c);t['R33']['value']='43k';assert not circuit_ok(t,n);controls.append('unrelated_control_resistor_changed')
t=copy.deepcopy(c);t['R528']['properties']=[q for q in t['R528']['properties']if q[0]!='dnp'];assert not circuit_ok(t,n);controls.append('qualification_strap_populated')
t=dict(n);t[('R563','2')]=('VDD_3V3',*t[('R563','2')][1:]);assert not circuit_ok(c,t);controls.append('pullup_wrong_supply')
t=copy.deepcopy(c);t['R564']['footprint']=None;assert not circuit_ok(t,n);controls.append('one_footprint_lost')
logs['erc']=run(['sch','erc','--format','json','--severity-all','-o',str(A/'erc.json'),str(A/'CMK230_Core_REVIEW.kicad_sch')]);v=[v for s in json.loads((A/'erc.json').read_text())['sheets']for v in s['violations']];assert not v
report={'revision':'R5 DAT43 conditional circuit','components':len(c),'bindings':len(n),'distinct_nets':len({v[0]for v in n.values()}),'changed_value_refs':refs,'changed_footprint_refs':refs,'assigned':sum(bool(v['footprint'])for v in c.values()),'unassigned':sum(not v['footprint']for v in c.values()),'net_function_type_changes':0,'population_changes':0,'R528_DNP_preserved':True,'erc_violations':0,'negative_controls_rejected':controls+['47k_with10percent_total_error','43k_with20percent_total_error'],'accepted_total_resistance_interval_ohm':[38700,47300],'manufacturer_interval_ohm':[10000,50000],'production_ready':False,'full_board_routed':False,'range_screen_is_lifetime_guarantee':False}
(O/'validation.json').write_text(json.dumps(report,indent=2)+'\n');(O/'native-checks.json').write_text(json.dumps(logs,indent=2)+'\n');print(json.dumps(report,indent=2))
