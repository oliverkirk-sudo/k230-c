"""Read-only baseline audit and bounded logic/DC screens. Never writes CAD."""
from pathlib import Path
import csv, hashlib, itertools, json, xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
XML = PROJECT / 'cad/high-temp-candidate/master.xml'
EXPECTED = '96108059ca509bbde234565dcda46a2a0273dd2cb296a5d3a95aac812d08976b'
raw = XML.read_bytes()
assert hashlib.sha256(raw).hexdigest() == EXPECTED, 'Baseline changed; explicitly rebase this review before rerunning.'
root = ET.fromstring(raw)
parts = {c.get('ref'): c.findtext('value') for c in root.findall('.//components/comp')}
nets = {(n.get('ref'), n.get('pin')): net.get('name') for net in root.findall('.//nets/net') for n in net.findall('node')}
assert len(parts) == 254 and len(nets) == 1509
assert parts['U14'].startswith('74AUP1G97GW,125') and parts['R33'].startswith('270k ')
maps = {
 'U14': {'1':'GLOBAL_DISABLE','2':'GND','3':'VDD_3V3','4':'DISABLE_OR_TF','5':'VDD_3V3','6':'MODE_TF'},
 'U92': {'1':'GND','2':'GND','3':'FIXED_RAILS_PGOOD_3V3','4':'STORAGE_ENABLE_1V8','5':'VDD1P8','6':'BOOT_VOLTAGE_QUALIFIED_1V8'},
 'U94': {'1':'GND','2':'GND','3':'FIXED_RAILS_PGOOD_3V3','4':'RESET_RELEASE_REQUEST_1V8','5':'VDD1P8','6':'RSTN'},
}
for ref, mapping in maps.items():
    assert parts[ref].startswith('74AUP1G97GW,125')
    for pin, net in mapping.items(): assert nets[(ref,pin)] == net
assert root.find(".//components/comp[@ref='R528']/property[@name='dnp']") is not None

# Datasheet rows explicitly transcribed in C,B,A order, shared by the three 97 devices.
source_rows = [(0,0,0,0),(0,0,1,0),(0,1,0,1),(0,1,1,1),(1,0,0,0),(1,0,1,1),(1,1,0,0),(1,1,1,1)]
def gate(a,b,c): return a if c else b
assert all(gate(a,b,c)==y for c,b,a,y in source_rows)
assert all(gate(1,b,c)==(b|c) and gate(a,0,c)==(a&c) for a,b,c in itertools.product([0,1],repeat=3))
states=[]
for pg,q,rst,mode in itertools.product([0,1],repeat=4):
    storage=gate(pg,0,q); reset=gate(pg,0,rst); disable=1-storage; upper=gate(1,disable,mode)
    assert storage==(pg&q) and reset==(pg&rst) and upper==(disable|mode)
    if not q: assert disable==1 and upper==1
    states.append(dict(PG=pg,qualifier=q,RSTN=rst,MODE_TF=mode,STORAGE_ENABLE=storage,RESET_RELEASE_REQUEST=reset,GLOBAL_DISABLE=disable,DISABLE_OR_TF=upper))

screen=json.loads((PROJECT/'engineering/passive-resistor-candidates/static-screen.json').read_text())
v18min,v18max=screen['rail_bounds_V']['1V8'];v33min,v33max=screen['rail_bounds_V']['3V3']
dual={'1':'GND','2':'BOOT_VOLTAGE_QUALIFIED_1V8','3':'RESET_RELEASE_REQUEST_1V8','4':'GND','5':'FIXED_RAILS_PGOOD_3V3','6':'GND','7':'RSTN','8':'STORAGE_ENABLE_1V8','9':'VDD1P8','10':'FIXED_RAILS_PGOOD_3V3'}
u14={
 'keep_R33_ohm':270000,'R33_total_acceptance_fraction':0.10,
 'worst_sink_A':v33max/243000+2e-6,'continuous_range_test_load_A':100e-6,
 'VOL_max_V':0.1,'VOH_min_V':v33min-0.1,'TMUX_low_margin_V':0.45-0.1,'TMUX_high_margin_V':v33min-0.1-1.2,
 'GLOBAL_DISABLE_released_leakage_screen_A':9.75e-6,'GLOBAL_DISABLE_high_screen_V':v33min-11000*9.75e-6,
 'MODE_TF_default_leakage_screen_A':9e-6,'MODE_TF_low_screen_V':11000*9e-6,
 'MODE_TF_TMUX_low_margin_V':.45-11000*9e-6,
 'MODE_TF_discrete_TI_3V_VTminus_margin_V':.84-11000*9e-6,
 'GLOBAL_DISABLE_TMUX_high_margin_V':v33min-11000*9.75e-6-1.2,
 'GLOBAL_DISABLE_discrete_TI_3V_VTplus_margin_V':v33min-11000*9.75e-6-1.87,
 'R31_R32_total_acceptance_ohm':[9000,11000],
 'MODE_TF_leakage_contributors_A':{'U14_In2':5e-6,'U11_SEL':2e-6,'U12_SEL':2e-6},
 'GLOBAL_DISABLE_leakage_contributors_A':{'U93_IOZ':.75e-6,'U14_In1':5e-6,'U11_EN':2e-6,'U12_EN':2e-6},
 'input_threshold_at_3V_only':{'VTplus_max_V':1.87,'VTminus_min_V':0.84,'hysteresis_min_V':0.53},
 'input_rows_guaranteed_over_actual_rail':False,
 'leakage_source_caveat':'TI II uses VI=5.5V or GND; Ioff uses VI or VO=5.5V. Applying endpoints as conservative 3V3 allowances is a source-condition interpretation.',
 'optional_43k_worst_sink_A':v33max/(43000*.9)+2e-6,
 'hypothetical_live_pullup_270k_linear_screen_V':v33min-297000*12e-6,
 'hypothetical_live_pullup_43k_linear_screen_V':v33min-47300*12e-6,
 'common_rail_collapse_high_guaranteed':False,
}
assert u14['worst_sink_A']<100e-6 and u14['optional_43k_worst_sink_A']<100e-6
dual_screen={
 'source_characteristics_equal_to_two_baseline_1G97_at_125C':True,
 'PG':screen['R527'],'qualifier_pulldown':screen['R529'],
 'U92_to_U93_guaranteed_valid_supply_margin_V':0.3*v18min-.11,
 'MR_pullup_max_sink_A':v18max/70000,
 'MR_load_exceeds_20uA_light_load_row':v18max/70000>20e-6,
 'MR_low_margin_using_discrete_1p65V_output_row_V':.3*v18min-.39,
 'discrete_threshold_and_loaded_output_row_extension_open':True,
 'GUX_absmax_Ptot_at_125C_mW':250-7.1*(125-115),
}
result={'status':'PASS_BASELINE_PINS_BOOLEAN_EQUIVALENCE_AND_BOUNDED_DC_ONLY','CAD_modified':False,'baseline_sha256':EXPECTED,'baseline_counts':{'refs':254,'pin_net_nodes':1509},'baseline_selected_values':{r:parts[r] for r in ['U14','R33','U92','U94','U91','U93','C34','C810','C813']},'baseline_pin_maps':maps,'proposed_TI_U14_same_numbered_nets':maps['U14'],'proposed_dual_U92_74AUP2G97GUX_pin_map':dual,'minimal_logic_only_counts_if_both_changes_applied_with_all_passives_kept':{'refs':253,'pin_net_nodes':1507},'lost_branch_258_refs_1517_nodes_reconstructed':False,'source_truth_rows_verified':8,'integrated_boolean_states_verified':16,'rail_bounds_V':screen['rail_bounds_V'],'TI_U14_screen':u14,'dual_screen':dual_screen,'not_verified':['CAD substitution','PCB routing','Nexperia original-file recovery and visual land audit','factory mask/paste/registration and assembly','full-rail threshold interpretation','partial-supply behavior','bench timing/noise','thermal closure']}
(HERE/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
with (HERE/'truth-table.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['C_or_In2','B_or_In1','A_or_In0','Y']);w.writerows(source_rows)
with (HERE/'integrated-logic-states.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=states[0]);w.writeheader();w.writerows(states)
with (HERE/'proposed-pin-map.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['reference','MPN','pin','function','net'])
 for pin,fun in {'1':'In1','2':'GND','3':'In0','4':'Y','5':'VCC','6':'In2'}.items():w.writerow(['U14','SN74LVC1G97DSFR',pin,fun,maps['U14'][pin]])
 for pin,fun in {'1':'1B','2':'1C','3':'2Y','4':'GND','5':'2A','6':'2B','7':'2C','8':'1Y','9':'VCC','10':'1A'}.items():w.writerow(['U92','74AUP2G97GUX',pin,fun,dual[pin]])
assert hashlib.sha256(XML.read_bytes()).hexdigest()==EXPECTED
print(json.dumps({'status':result['status'],'source_truth_rows':8,'integrated_states':16,'CAD_unchanged':True,'outputs':str(HERE)},indent=2))
