import os,sys,json,xml.etree.ElementTree as E,hashlib
from pathlib import Path
for name,leaf in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data')]:os.environ[name]='/tmp/k230-recovery-runtime/'+leaf
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'tools'))
import pcbnew as k
from population_contract import apply_population,validate_population
x=E.parse(R/'recovery/fresh-checks/master.xml');cs={c.get('ref'):c for c in x.findall('.//components/comp')};pn={(n.get('ref'),n.get('pin')):net.get('name')for net in x.findall('.//nets/net')for n in net};boardpath=R/'cad/verified-import-unplaced/CMK230_Verified_Import_UNPLACED.kicad_pcb';before=hashlib.sha256(boardpath.read_bytes()).hexdigest();b=k.LoadBoard(str(boardpath));refs={f.GetReference():f for f in b.GetFootprints()};checks=[]
for ref in ['J1','U14']:
 f=k.FOOTPRINT(refs[ref]);apply_population(cs[ref],f);validate_population(cs[ref],f)
 if ref=='J1':assert f.GetAttributes()&k.FP_EXCLUDE_FROM_BOM and f.GetAttributes()&k.FP_EXCLUDE_FROM_POS_FILES and len(list(f.Pads()))==140
 checks.append(ref+'_flags_and_existing_copper_preserved')
# Unsaved synthetic API fixture tests population metadata only, not a footprint
# assignment or reconstructed R528 land.
t=k.BOARD();f=k.FOOTPRINT(t);f.SetReference('R528');t.Add(f)
for number in ['1','2']:
 net=k.NETINFO_ITEM(t,pn['R528',number]);t.Add(net);p=k.PAD(f);p.SetNumber(number);p.SetNet(net);f.Add(p)
apply_population(cs['R528'],f);validate_population(cs['R528'],f);assert f.GetAttributes()&k.FP_DNP and f.GetAttributes()&k.FP_EXCLUDE_FROM_POS_FILES;checks.append('R528_default_DNP_and_no_default_pick_place')
for bit,label in [(k.FP_DNP,'lost_DNP'),(k.FP_EXCLUDE_FROM_POS_FILES,'lost_default_PnP_exclusion')]:
 old=f.GetAttributes();f.SetAttributes(old&~bit)
 try:validate_population(cs['R528'],f)
 except AssertionError:checks.append(label+'_detected')
 else:raise AssertionError(label)
 f.SetAttributes(old)
# Existing all140 edge bindings must not change when excluded from assembly.
f=k.FOOTPRINT(refs['J1']);apply_population(cs['J1'],f)
def binding_ok(g):assert all(p.GetNetname()==pn['J1',p.GetNumber()]for p in g.Pads()if p.GetNumber())
binding_ok(f);p=next(p for p in f.Pads()if p.GetNumber()=='4');p.SetNetCode(0)
try:binding_ok(f)
except AssertionError:checks.append('lost_edge_net_binding_detected')
else:raise AssertionError('edge mutation not detected')
assert hashlib.sha256(boardpath.read_bytes()).hexdigest()==before
report={'status':'POPULATION_IMPORTER_CONTRACT_TESTED_NOT_A_NEW_PCB','checks':checks,'R528_native_footprint_still_missing_in_v12':True,'source_PCB_unchanged':True,'no_assembly_exports_generated':True,'source_PCB_sha256':before,'synthetic_fixture_saved_or_used_as_land':False}
(R/'recovery/population-contract/test-result.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
