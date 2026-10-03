#!/usr/bin/env python3
"""Read-only, bounded CM-K230 CORE power-good interface review."""
import argparse, hashlib, json
from pathlib import Path
import xml.etree.ElementTree as ET

ap=argparse.ArgumentParser()
ap.add_argument('--project', type=Path, default=Path('/workspace/shared/k230-publication/r3-repo/project'))
a=ap.parse_args()
out=Path(__file__).resolve().parent
src=a.project/'cad/recovery-physical-candidate/master.xml'
b=src.read_bytes(); root=ET.fromstring(b)
components={c.attrib['ref']:c.findtext('value') for c in root.find('components')}
nets={n.attrib['name']:n for n in root.find('nets')}
net=nets['CORE_PGOOD_5V']
actual={(n.attrib['ref'],n.attrib['pin']) for n in net}
expected={('R203','1'),('U21','2'),('U22','E1'),('U23','E1'),('U24','1'),('U25','1'),('U26','1')}
assert actual==expected, (actual,expected)
assert components['R203']=='100k'
assert ('R203','2') in {(n.attrib['ref'],n.attrib['pin']) for n in nets['VIN_5V']}
refs=['U21','U22','U23','U24','U25','U26','R203','R204']
pin_graph=[]
for name,n in nets.items():
 for node in n:
  if node.attrib['ref'] in refs:
   pin_graph.append({'ref':node.attrib['ref'],'value':components[node.attrib['ref']], 'pin':node.attrib['pin'],'function':node.get('pinfunction'),'net':name})
receiver_refs=['U22','U23','U24','U25','U26']
assert all(any(p['ref']==ref and p['function']=='VIN' and p['net']=='VIN_5V' for p in pin_graph) for ref in receiver_refs)
rmin=100000*.9;rmax=100000*1.1
cand_rmin=220000*.9;cand_rmax=220000*1.1
report={
 'date_utc':'2026-10-03',
 'status':'NO_PROVEN_FUNCTIONAL_FAILURE; ZERO_POSITIVE_LOW_NOISE_BUDGET; NO_CAD_CHANGE_APPROVED_BY_THIS_REVIEW',
 'input':{'project':str(a.project),'netlist':'cad/recovery-physical-candidate/master.xml','sha256':hashlib.sha256(b).hexdigest(),
          'components':len(components),'nets':len(nets),'nodes':sum(len(n) for n in nets.values())},
 'scope':{'six_layers':True,'board_mm':[38,38],'contacts':140,'top_only':True,'cad_edits':False,
          'storage_inhibit_changed':False,'vendor_contact':False,'purchase':False,'otp':False},
 'pin_graph':pin_graph,
 'receiver_refs':receiver_refs,
 'sources':[
  {'id':'TI_BUCK','url':'https://www.ti.com/lit/ds/symlink/tps62827.pdf','document':'SLVSEF9I','revision':'March 2024','pages':[3,4,5,10],
   'facts':{'pg_vol_max_V':0.4,'pg_vol_test_sink_A':0.001,'pg_recommended_sink_max_A':0.001,
    'en_vil_max_V':0.4,'en_vih_min_V':1.0,'pg_leakage_max_A':1e-7,'pg_leakage_test_V':5.0,
    'en_leakage_max_A':1e-7,'en_leakage_test':'EN=High','electrical_table_vin_V':[2.4,5.5],
    'U21_recommended_vin_V':[2.5,5.5],'U24_U25_U26_recommended_vin_V':[2.4,5.5],
    'electrical_table_Tj_C':[-40,125],'pg_low_in_uvlo_when_vin_above_V':0.7,
    'explicit_direct_pg_to_other_converter_en_sequencing_guidance':True}},
  {'id':'TI_I2C_BUCK','url':'https://www.ti.com/lit/ds/symlink/tps62866.pdf','document':'SLVSEI1C','revision':'October 2020','pages':[3,4,5,6,11,12],
   'facts':{'en_vil_max_V':0.4,'en_vih_min_V':1.0,'en_leakage_max_A':1e-7,'en_leakage_test':'No row-specific condition; use electrical table header',
    'electrical_table_vin_V':[2.4,5.5],'electrical_table_Tj_C':[-40,125],'uvlo_rising_V':[2.2,2.4],
    'uvlo_falling_V':[2.1,2.3],'vin_falling_slew_max_when_below_uvlo_V_per_us':0.010}},
  {'id':'TI_OPTIONAL_SUPERVISOR','url':'https://www.ti.com/lit/ds/symlink/tps3890.pdf','document':'SLVSD65A','revision':'May 2016','pages':[3,4,5,12,14,16,17],
   'facts':{'device':'TPS389001','supply_V':[1.5,5.5],'Tj_C':[-40,125], 'vitn_nom_V':1.15,'vitp_nom_V':1.157,'threshold_error_fraction':0.01,
    'reset_vol_max_V':0.25,'reset_vol_test_A':0.0004,'reset_vol_test_min_supply_V':1.5,
    'por_max_V':0.8,'por_vol_max_V':0.2,'por_test_sink_A':15e-6,
    'sense_leakage_max_A':100e-9,'sense_leakage_test_V':5.0,
    'reset_leakage_max_A':250e-9,'reset_leakage_test':'SENSE=RESET=5.5V',
    'idd_max_A_at_vdd_5p5V_reset_current_zero':6.5e-6,'idd_max_A_at_vdd_3p3V_reset_current_zero':5.8e-6,
    'guaranteed_max_startup_delay_available':False,'guaranteed_max_sense_to_reset_delay_available':False}}
 ],
 'baseline_arithmetic':{
  'noise_margin_low_V':0.4-0.4,
  'r203_total_error_fraction_assumed_for_screen_only':0.10,
  'r203_range_ohm':[rmin,rmax],
  'pullup_only_sink_upper_A_at_5p5V_zero_node':5.5/rmin,
  'unknown_low_state_receiver_source_current_allowance_A_before_1mA':.001-5.5/rmin,
  'total_sink_leakage_allowance_A_for_high_at_2p5V':(2.5-1.0)/rmax,
  'total_sink_leakage_allowance_A_for_high_at_5p5V':(5.5-1.0)/rmax,
  'conditional_known_high_leakage_A':6*.1e-6,
  'conditional_high_drop_V':rmax*6*.1e-6,
  'warning':'The 0.6uA sum is a screen, not a guarantee outside source test conditions. No reduced-current VOL or RON interpolation.'},
 'one_optional_topology':{
  'disposition':'CANDIDATE_ONLY; NOT_END_TO_END_QUALIFIED; NO_ADOPTION_RECOMMENDATION',
  'connections':{'TPS389001.VDD':'VIN_5V','TPS389001.GND':'GND','TPS389001.MR':'VIN_5V','TPS389001.SENSE':'U21.PG with existing R203=100k to VIN_5V',
    'TPS389001.RESET':'New EN node to all five existing receiver EN pins, disconnected from U21.PG',
    'TPS389001.CT':'Open','new_reset_pullup':'220k to VIN_5V','new_bypass':'0.1uF from VDD to GND, placed locally'},
  'conditional_resistor_error_fraction':0.10,
  'sense_low_margin_V':1.15*.99-.4,
  'sense_high_threshold_max_V':1.157*1.01,
  'receiver_low_margin_V':.4-.25,
  'reset_pullup_only_sink_upper_A_at_5p5V':5.5/cand_rmin,
  'reset_pullup_only_sink_upper_A_below_1p5V':1.5/cand_rmin,
  'remaining_por_sink_budget_A':15e-6-1.5/cand_rmin,
  'receiver_high_total_sink_allowance_A_at_2p5V':(2.5-1)/cand_rmax,
  'sense_high_total_sink_allowance_A_at_2p5V':(2.5-1.157*1.01)/rmax,
  'conditional_reset_high_drop_V':cand_rmax*(.5e-6+.25e-6),
  'conditional_pg_high_drop_V':rmax*(.1e-6+.1e-6),
  'remaining_gates':['Leakage applicability beyond the listed voltage/state test points',
    'Receiver source-current bound in low and undervoltage states, including POR 15uA budget',
    'U21 PG numerical low-voltage behavior between UVLO and recommended VIN',
    'Maximum start, release and fault-assert timing across actual ramps and capacitance',
    'Common VIN/GND tracking under collapse, residual rails and no external backpower',
    'Footprint, top-side placement and routing in the actual six-layer 38mm board']
 },
 'conclusion':'Equality is inclusive DC compatibility at matching applicable conditions, with no positive margin. TI explicitly supports the topology. Published data do not prove a failure or a complete startup qualification. Preserve the circuit pending a stated margin/timing acceptance requirement and the missing bounds.'
}
(out/'review.json').write_text(json.dumps(report,indent=2)+'\n')
verify={'graph_matches_expected':True,'all_five_receivers_on_common_VIN':True,'master_sha256_unchanged':hashlib.sha256(src.read_bytes()).hexdigest()==report['input']['sha256'],
 'low_noise_budget_V':report['baseline_arithmetic']['noise_margin_low_V'],'raw_source_files_in_deliverable':False,'cad_edits':False}
assert all(verify[k] for k in ['graph_matches_expected','all_five_receivers_on_common_VIN','master_sha256_unchanged'])
(out/'verification.json').write_text(json.dumps(verify,indent=2)+'\n')
print(json.dumps(verify,indent=2))
