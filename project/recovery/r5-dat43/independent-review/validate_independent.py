#!/usr/bin/env python3
"""Independent, read-only comparison of the CM-K230 R5 DAT43 candidate.

Usage: python validate_independent.py --baseline R4/project --candidate R5/project
       [--fresh-netlist runtime/fresh.xml] [--fresh-erc runtime/fresh-erc.json]
Output is written beside this script. Input CAD is never modified.
"""
import argparse
import copy
import hashlib
import json
import re
from pathlib import Path
import xml.etree.ElementTree as ET

p=argparse.ArgumentParser()
p.add_argument('--baseline',type=Path,required=True)
p.add_argument('--candidate',type=Path,required=True)
p.add_argument('--fresh-netlist',type=Path)
p.add_argument('--fresh-erc',type=Path)
a=p.parse_args()
out=Path(__file__).resolve().parent
active=Path('cad/recovery-physical-candidate')
refs={f'R{i}' for i in range(563,571)}
old_value='47k DATA PULLUP'
new_value='43k CRCW020143K0FKED DAT PULLUP CANDIDATE'
fp='CMK230_Recovery_Passive_Candidates:Vishay_CRCW0201_SourceLand_PROCESS_CANDIDATE'
fp_path=Path('cad/recovery-passive-candidates/CMK230_Recovery_Passive_Candidates.pretty/Vishay_CRCW0201_SourceLand_PROCESS_CANDIDATE.kicad_mod')
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()

def canonical(e):
    return [e.tag,sorted(e.attrib.items()),(e.text or '').strip(),[canonical(c) for c in e]]

def parse(path):
    root=ET.parse(path).getroot()
    comps={e.get('ref'):e for e in root.findall('./components/comp')}
    binding=[]
    for net in root.findall('./nets/net'):
        for node in net.findall('node'):
            binding.append((tuple(sorted(net.attrib.items())),tuple(sorted(node.attrib.items()))))
    return root,comps,sorted(binding)

def compare(base_path,candidate_path):
    br,bc,bn=parse(base_path);cr,cc,cn=parse(candidate_path)
    assert len(bc)==len(cc)==254 and set(bc)==set(cc)
    assert len(bn)==len(cn)==1509 and bn==cn
    assert len(br.findall('./nets/net'))==len(cr.findall('./nets/net'))==457
    assert canonical(br.find('libparts'))==canonical(cr.find('libparts'))
    value_changes=[]; footprint_changes=[]; other_changes=[]
    for ref in sorted(bc):
        b=bc[ref];c=cc[ref]
        if b.findtext('value')!=c.findtext('value'):value_changes.append(ref)
        if b.findtext('footprint')!=c.findtext('footprint'):footprint_changes.append(ref)
        be=copy.deepcopy(b);ce=copy.deepcopy(c)
        if ref in refs:
            assert b.findtext('value')==old_value and c.findtext('value')==new_value
            assert not b.findtext('footprint') and c.findtext('footprint')==fp
            assert c.find('./fields/field[@name="Footprint"]').text==fp
            for e in (be,ce):
                for child in list(e):
                    if child.tag in ('value','footprint'):e.remove(child)
                for child in e.findall('./fields/field[@name="Footprint"]'):child.text=''
        if canonical(be)!=canonical(ce):other_changes.append(ref)
    assert set(value_changes)==refs and set(footprint_changes)==refs and not other_changes
    assert bc['R33'].findtext('value')==cc['R33'].findtext('value')
    assert cc['R33'].findtext('value').startswith('270k ')
    assert any(e.get('name')=='dnp' for e in cc['R528'].findall('property'))
    pinmap={(n.get('ref'),n.get('pin')):net.get('name') for net in cr.findall('./nets/net') for n in net.findall('node')}
    for i,ref in enumerate(sorted(refs)):
        assert pinmap[(ref,'1')]==f'EMMC_DAT{i}'
        assert pinmap[(ref,'2')]=='VEMMC_IO'
    return {'references':254,'pin_net_function_type_bindings':1509,'distinct_nets':457,'changed_value_refs':value_changes,'changed_footprint_refs':footprint_changes,'all_other_component_attributes_preserved':True,'library_pin_definitions_preserved':True,'net_codes_names_and_all_node_attributes_preserved':True,'all_population_properties_preserved':True,'R33_270k_preserved':True,'R528_DNP_preserved':True,'assigned_baseline':sum(bool(e.findtext('footprint')) for e in bc.values()),'assigned_candidate':sum(bool(e.findtext('footprint')) for e in cc.values()),'candidate_master_sha256':sha(candidate_path)}

base_master=a.baseline/active/'master.xml'
candidate_master=a.candidate/active/'master.xml'
report={'date':'2026-10-03','status':'PASS_BOUNDED_INDEPENDENT_R5_DAT43_REVIEW','baseline':'published R4','candidate':'R5 DAT43 conditional candidate','main_CAD_modified_by_review':False,'published_netlist_comparison':compare(base_master,candidate_master)}
if a.fresh_netlist:
    report['fresh_native_export_comparison']=compare(base_master,a.fresh_netlist)
    _,saved_c,saved_n=parse(candidate_master);_,fresh_c,fresh_n=parse(a.fresh_netlist)
    assert {k:canonical(v) for k,v in saved_c.items()}=={k:canonical(v) for k,v in fresh_c.items()} and saved_n==fresh_n
    report['fresh_export_matches_saved_components_and_nodes']=True
if a.fresh_erc:
    erc=json.loads(a.fresh_erc.read_text())
    violations=[v for s in erc['sheets'] for v in s['violations']]
    assert len(violations)==0
    report['fresh_ERC_violations']=0

baseline_sch={p.relative_to(a.baseline/active):sha(p) for p in (a.baseline/active).glob('*.kicad_sch')}
candidate_sch={p.relative_to(a.candidate/active):sha(p) for p in (a.candidate/active).glob('*.kicad_sch')}
assert set(baseline_sch)==set(candidate_sch)
changed_sch=sorted(str(p) for p in baseline_sch if baseline_sch[p]!=candidate_sch[p])
assert changed_sch in (['14_EMMC_Local_Bias.kicad_sch'],['14_EMMC_Local_Bias.kicad_sch','CMK230_Core_REVIEW.kicad_sch'])
root_revision_metadata_changed='CMK230_Core_REVIEW.kicad_sch' in changed_sch
if root_revision_metadata_changed:
    old_root=(a.baseline/active/'CMK230_Core_REVIEW.kicad_sch').read_text()
    new_root=(a.candidate/active/'CMK230_Core_REVIEW.kicad_sch').read_text()
    assert new_root.replace('(rev "RCV-R5")','(rev "RCV-PHYS1")')==old_root
old_s=(a.baseline/active/'14_EMMC_Local_Bias.kicad_sch').read_text()
new_s=(a.candidate/active/'14_EMMC_Local_Bias.kicad_sch').read_text()
new_lines=[];seen=set()
for line in new_s.splitlines(keepends=True):
    m=re.search(r'\(property "Reference" "(R\d+)"',line)
    if line.startswith('(symbol ') and m and m[1] in refs:
        assert line.count('(property "Value" "'+new_value+'"')==1
        assert line.count('(property "Footprint" "'+fp+'"')==1
        line=line.replace('(property "Value" "'+new_value+'"','(property "Value" "'+old_value+'"')
        line=line.replace('(property "Footprint" "'+fp+'"','(property "Footprint" ""')
        seen.add(m[1])
    new_lines.append(line)
DAT_revision_metadata_changed='(rev "RCV-R5")' in new_s
assert seen==refs and ''.join(new_lines).replace('(rev "RCV-R5")','(rev "RCV-PHYS1")')==old_s
assert sha(a.baseline/fp_path)==sha(a.candidate/fp_path)
bias_refs=['R31','R32','R33','R34','R43','R44','R45','R46','R47','R61','R62','R203','R204','R216','R217','R218','R219','R402','R527','R529','R530','R562','R571','R572','R573']
_,cc,_=parse(candidate_master)
assert all(not cc[r].findtext('footprint') for r in bias_refs)
report['schematic_checks']={'only_changed_circuit_sheet':'14_EMMC_Local_Bias.kicad_sch','root_revision_metadata_changed_RCV_PHYS1_to_RCV_R5':root_revision_metadata_changed,'DAT_revision_metadata_changed_RCV_PHYS1_to_RCV_R5':DAT_revision_metadata_changed,'all_schematic_files_except_DAT_and_root_revision_byte_identical':True,'DAT_sheet_exactly_eight_value_and_footprint_property_changes_plus_revision_metadata':True,'coordinates_UUIDs_wires_labels_pin_maps_and_symbol_population_unchanged':True,'existing_CRCW_source_land_file_byte_identical':True,'ordinary_25_bias_batch_still_unassigned':True}

rnom=43000;total=.1;rmin=rnom*(1-total);rmax=rnom*(1+total);v=1.95
assert abs(rmin-38700)<1e-8 and abs(rmax-47300)<1e-8
assert rmin>=10000 and rmax<=50000
assert 47000*1.1>50000
report['electrical_range_and_stress']={'nominal_ohm':rnom,'candidate_MPN':'CRCW020143K0FKED','initial_tolerance_pct':1,'TCR_ppm_per_K':100,'total_acceptance_fraction':total,'total_resistance_interval_ohm':[38700,47300],'source_DAT_pullup_interval_ohm':[10000,50000],'low_range_margin_ohm':28700,'high_range_margin_ohm':2700,'range_pass':True,'47k_at_10pct_upper_ohm':51700,'VCCQ_source_max_V':v,'per_resistor_max_full_supply_DC_current_A':v/rmin,'per_resistor_max_full_supply_DC_power_W':v*v/rmin,'current_uA':v/rmin*1e6,'power_uW':v*v/rmin*1e6,'meaning':'Incremental pullup load at a conservatively zero-volt sink node, not a guaranteed low-driver capability or total pin current. Actual functional state is not inferred.','range_screen_is_lifetime_guarantee':False,'lifetime_gate':'The complete +/-10% total band must be established over initial tolerance, film temperature, mounting, humidity and aging for the mission. Separate manufacturer qualification tests do not establish arbitrary-life drift.'}
report['sources']={
 'micron':{'url':'https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/234/EMMC_5F00_DATASHEET.pdf','document':'Micron automotive eMMC Rev G, October2018','locators':['p1 VCCQ1.70-1.95V','Table1 p2 MTFC16GAPALBH-AAT identity','Table13 p27 DAT10-50k'],'review':'Text inspected earlier in this same review session; source applies to the active selected family. Raw PDF not redistributed.'},
 'vishay':{'url':'https://www.vishay.com/docs/20052/crcw0201e3.pdf','document':'20052,21-Sep-2022','locators':['p1 F/K family range','p2 order code and copper lands','pp1,3-4 thermal and endurance limits'],'fresh_PDF_sha256':'390a5effad7c3b526afb7faba340e29176261bfa4c041a128effc87b941a61ea'},
}
report['input_hashes']={'R4_master':sha(base_master),'R5_master':sha(candidate_master),'R5_DAT_sheet':sha(a.candidate/active/changed_sch[0]),'existing_CRCW_footprint':sha(a.candidate/fp_path)}
report['not_qualified']=['arbitrary mission lifetime','eMMC/K230/mux input leakage','guaranteed DAT high/low voltages','ROM boot behavior','signal integrity and bus timing','cold-mode/partial-power transitions','fabricator mask/paste/registration','full six-layer PCB routing or fit','stock/lifecycle/procurement']
report['preserved_board_contract']={'layers':6,'outline_mm':[38,38],'edge_contacts':140,'top_only':True,'changed_by_this_delta':False,'complete_routed_board_verified':False}
(out/'independent-review.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'changed_refs':sorted(refs),'current_uA':report['electrical_range_and_stress']['current_uA'],'power_uW':report['electrical_range_and_stress']['power_uW'],'fresh_ERC_violations':report.get('fresh_ERC_violations')},indent=2))
