from pathlib import Path
import xml.etree.ElementTree as E,json,csv,itertools,copy,hashlib
R=Path(__file__).resolve().parents[2];oldpath=R/'cad/recovery-tf-candidate/master.xml';newpath=R/'cad/recovery-compact-candidate/master.xml'
def parse(p):
 x=E.parse(p);pn={(n.get('ref'),n.get('pin')):(net.get('name'),n.get('pinfunction'),n.get('pintype'))for net in x.findall('.//nets/net')for n in net};cs={c.get('ref'):{'value':c.findtext('value'),'footprint':c.findtext('footprint'),'properties':{p.get('name'):p.get('value')for p in c.findall('property')}}for c in x.findall('.//components/comp')};return pn,cs
old,oc=parse(oldpath);new,nc=parse(newpath);expected={(r['reference'],r['pin']):r['net']for r in csv.DictReader((R/'recovery/compact-logic-review/proposed-pin-map.csv').open())}
def check(p,c):
 assert {k:v for k,v in p.items()if k[0]not in ['U14','U92','U94']}=={k:v for k,v in old.items()if k[0]not in ['U14','U92','U94']}
 assert {k:v for k,v in c.items()if k not in ['U14','U92','U94']}=={k:v for k,v in oc.items()if k not in ['U14','U92','U94']}
 assert 'U94'not in c and not any(k[0]=='U94'for k in p)
 assert {k:v[0]for k,v in p.items()if k[0]in ['U14','U92']}==expected
 assert c['U14']['value'].startswith('SN74LVC1G97DSFR') and c['U92']['value'].startswith('74AUP2G97GUX')
 assert not c['U14']['footprint'] and not c['U92']['footprint']
 assert c['R33']==oc['R33'] and 'dnp'in c['R528']['properties']
 assert c['C810']==oc['C810'] and c['C813']==oc['C813']
 cases=[]
 for pg,qualified,rst,tf in itertools.product([False,True],repeat=4):
  levels={'GND':False,'VDD1P8':True,'VDD_3V3':True,'FIXED_RAILS_PGOOD_3V3':pg,'BOOT_VOLTAGE_QUALIFIED_1V8':qualified,'RSTN':rst,'MODE_TF':tf}
  read=lambda ref,pin:levels[p[ref,str(pin)][0]]
  enable=read('U92',10)if read('U92',2)else read('U92',1)
  release=read('U92',5)if read('U92',7)else read('U92',6)
  levels['GLOBAL_DISABLE']=not enable
  disable_emmc=read('U14',3)if read('U14',6)else read('U14',1)
  assert enable==(pg and qualified) and release==(pg and rst) and disable_emmc==((not(pg and qualified))or tf)
  cases.append({'PG':pg,'qualified':qualified,'external_RSTN':rst,'TF':tf,'storage_enable':enable,'reset_release':release,'emmc_disabled':disable_emmc})
 return cases
cases=check(new,nc);badcases=[]
for case in ['wrong_GU_pinmap','wrong_U14_high_tie','lost_C810','default_strap_populated']:
 p=copy.deepcopy(new);c=copy.deepcopy(nc)
 if case=='wrong_GU_pinmap':p['U92','2'],p['U92','7']=p['U92','7'],p['U92','2']
 elif case=='wrong_U14_high_tie':p['U14','1'],p['U14','3']=p['U14','3'],p['U14','1']
 elif case=='lost_C810':c.pop('C810')
 else:c['R528']['properties'].pop('dnp')
 try:check(p,c)
 except AssertionError:badcases.append(case)
 else:raise AssertionError(case)
report={'status':'COMPACT_ELECTRICAL_CANDIDATE_NETLIST_VERIFIED','components':len(nc),'pin_bindings':len(new),'unchanged_nonlogic_bindings':sum(k[0]not in['U14','U92','U94']for k in old),'all_passives_preserved':True,'R528_default_DNP':True,'R33_unchanged':True,'integrated_cases':cases,'negative_controls_rejected':badcases,'unassigned_compact_footprints':['U14','U92'],'source_hashes':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in[oldpath,newpath]},'full_rail_threshold_and_partial_power_qualified':False,'PCB_reconstructed':False,'historical_HT18_recovery_claimed':False}
(R/'recovery/compact-logic-review/implementation-validation.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items()if k!='integrated_cases'})
