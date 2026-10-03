#!/usr/bin/env python3
"""Bounded U14 slew and existing-family alternative calculations; no CAD writes."""
from pathlib import Path
import json
import math

out=Path(__file__).resolve().parent
base=json.loads((out/'static-screen.json').read_text())
vmin,vmax=base['rail_bounds_V']['3V3']
vinf=vmin-9.75e-6*11000
factor=math.log((vinf-.8)/(vinf-2.0))
d={
 'status':'U14_INPUT_SLEW_NOT_CLOSED_BY_R33_CHANGE; BOUNDED_SCHMITT_ALTERNATIVE_ONLY',
 'cad_edits':False,
 'LVC_existing':{
  'part':'SN74LVC1G32DBVR','source':'https://www.ti.com/lit/ds/symlink/sn74lvc1g32.pdf','revision':'W','pages':[6,7,8,10,13,14],
  'max_input_dt_dv_ns_per_V':10,'applicable_VCC_V':[3.0,3.6],
  'GLOBAL_DISABLE_model':{'Rmax_ohm':11000,'sink_leakage_A':9.75e-6,'Vinf_V':vinf,'illustrative_crossing_V':[.8,2.0],'ln_factor':factor,'average_limit_Cmax_F':10e-9*1.2/(11000*factor),'local_slope_at_2V_Cmax_F':10e-9*(vinf-2.0)/11000,'known_typical_input_C_sum_F':10e-12,'average_dt_dv_at_10pF_ns_per_V':11000*10e-12*factor/1.2*1e9,'C_is_guaranteed':False,'missing_C':['U93 output','trace','pads','measurement fixture'],'interpretation':'Illustrative necessary slope screen, not a manufacturer-defined test interval or observed failure. Actual capacitance and transient waveforms unavailable.'},
  'MODE_TF':'Cold-only JP1 makes this a fixed strap during valid stable-supply operation. Open is pulled low; closed tracks3V3. No powered switching authorized; supply ramp/contact settling still unqualified.',
  'output_load':'Only U13.EN plus R33 and PCB/probe capacitance. R33 does not set normal push-pull output rise time.',
  'output_capacitance_condition_F':50e-12,'output_tpd_max_s':4e-9,'output_tpd_conditions':'3.3V±0.3V,125C table, CL50pF/RL500ohm measurement network, input tr/tf≤2.5ns. Not an output-rise-time guarantee and not directly applicable to the slow input.',
  'dedicated_output_rise_fall_max_found':False,
 },
 'AUP_alternative':{
  'part':'74AUP1G97GW,125','source':'https://assets.nexperia.com/documents/data-sheet/74AUP1G97.pdf','revision':'14','pages':[3,4,5,7,8,9,10,11],
  'correct_OR':'A=1; Y=B OR C','incorrect_B_high_configuration':'B=1; Y=A OR NOT C',
  'proposed_GW_pin_map':{'1':'B=GLOBAL_DISABLE','2':'GND','3':'A=VDD_3V3','4':'Y=DISABLE_OR_TF','5':'VCC=VDD_3V3','6':'C=MODE_TF'},
  'supply_V':[.8,3.6],'max_input_V':3.6,'static_rail_headroom_to_3p6V_V':3.6-vmax,
  'input_leakage_A':.75e-6,'GLOBAL_DISABLE_total_high_leakage_A':5.5e-6,'GLOBAL_DISABLE_high_min_V':vmin-5.5e-6*11000,'MODE_TF_total_input_leakage_A':4.75e-6,'MODE_TF_low_max_V':4.75e-6*11000,
  'Schmitt_thresholds_at_discrete_3V_125C':{'VTplus_max_V':2.32,'VTminus_min_V':.88,'hysteresis_min_V':.79,'GLOBAL_DISABLE_high_margin_V':vmin-5.5e-6*11000-2.32,'GLOBAL_DISABLE_low_margin_V':.88-.39,'MODE_TF_low_margin_V':.88-4.75e-6*11000,'MODE_TF_high_margin_V':vmin-2.32,'gate':'These are3.0V tabulated thresholds. Extension to3.245–3.392V is not silently interpolated; full-range interpretation/characterization remains open.'},
  'slow_input_evidence':'Existing nexperia-aup97-slow-input-review.json: specified Schmitt thresholds/hysteresis, no input-transition row, and manufacturer handbook support slow inputs at valid stable supply. Dynamic table fast-input conditions are not slew restrictions.',
  'continuous_range_output_125C':{'supply_V':[.8,3.6],'IOL_A':20e-6,'VOL_max_V':.11,'IOH_A':-20e-6,'VOH_min_expression':'VCC-0.11V'},
  'R33_options':{},
  'source_dynamic_conditions':{'supply_V':[3.0,3.6],'CL_to_tpd_max':{'5pF':4.3e-9,'10pF':5.1e-9,'15pF':5.7e-9,'30pF':7.4e-9},'input_tr_tf_max_s':3e-9,'measurement':'50% input-to50% output, RL1Mohm. No standalone maximum output rise/fall specification. Slow-input application does not inherit these nanosecond delay guarantees.'},
  'actual_capacitive_load_verified':False,
  'retained_gates':['Same supply rail means no retained-high promise during rail loss.','Below0.8V and especially0.2–0.8V is not deterministic logic.','AtVCC0–0.2V additional IOFF is0.75uA; do not call it ordinary powered logic.','Actual output rise/fall, load capacitance, receiver switch timing, source noise and threshold-range applicability need validation.','Keep local bypass;6-pin SOT363-2 symbol/footprint remap required. No drop-in5-pin replacement.']
 }
}
for r in [43000,220000,270000]:
 lo,hi=r*.9,r*1.1
 sink=vmax/lo+2e-6
 d['AUP_alternative']['R33_options'][str(r)]={'resistance_screen_ohm':[lo,hi],'total_acceptance_fraction':.1,'sink_bound_A':sink,'reserve_to_20uA_A':20e-6-sink,'continuous_range_20uA_row_pass':sink<=20e-6,'low_margin_if_20uA_row_applies_V':.45-.11 if sink<=20e-6 else None,'active_high_min_V':vmin-.11,'active_high_margin_to_TMUX_VIH_V':vmin-.11-1.2,'unpowered_Ioff_A':.75e-6,'unpowered_Ioff_condition':'VCC=0; VI or VO=0–3.6V','hypothetical_separate_live_pullup_high_min_V':vmin-(.75e-6+2e-6)*hi,'hypothetical_separate_live_pullup_high_margin_V':vmin-(.75e-6+2e-6)*hi-1.2,'same_rail_power_loss_high_claim':False}
assert not d['AUP_alternative']['R33_options']['43000']['continuous_range_20uA_row_pass']
assert d['AUP_alternative']['R33_options']['270000']['continuous_range_20uA_row_pass']
(out/'u14-slew-addendum.json').write_text(json.dumps(d,indent=2)+'\n')
print(json.dumps({'LVC_average_C_limit_pF':d['LVC_existing']['GLOBAL_DISABLE_model']['average_limit_Cmax_F']*1e12,'AUP_270k':d['AUP_alternative']['R33_options']['270000']},indent=2))
