#!/usr/bin/env python3
"""U14 candidate regression: source pin map/function and bounded DC, not timing QA."""
from pathlib import Path
import hashlib
import itertools
import json
import math
import xml.etree.ElementTree as ET

B=Path(__file__).resolve().parents[1]
H=B/'cad/high-temp-candidate'
E=B/'engineering/passive-resistor-candidates'
x=ET.parse(H/'master.xml')
pn={p.get('ref')+'.'+p.get('pin'):n.get('name') for n in x.findall('.//nets/net') for p in n.findall('node')}
cs={c.get('ref'):c for c in x.findall('.//components/comp')}
baseline=json.loads((E/'u14-implementation-before.json').read_text())
expected={'1':'GLOBAL_DISABLE','2':'GND','3':'VDD_3V3','4':'DISABLE_OR_TF','5':'VDD_3V3','6':'MODE_TF'}
assert {k.split('.')[1]:v for k,v in pn.items() if k.startswith('U14.')}==expected
assert cs['U14'].findtext('value')=='74AUP1G97GW,125 SCHMITT OR CANDIDATE'
fp='CMK230_Nexperia_Standard_Candidates:Nexperia_SOT363-2_AUP1G97_DrawingVerified_CANDIDATE'
assert cs['U14'].findtext('footprint')==fp
lib=cs['U14'].find('libsource').get('part')
pins={p.get('num'):(p.get('name'),p.get('type')) for p in x.findall(f".//libpart[@part='{lib}']/pins/pin")}
assert pins=={'1':('B','input'),'2':('GND','power_in'),'3':('A_TIE_HIGH','input'),'4':('Y','output'),'5':('VCC','power_in'),'6':('C','input')}
assert {k for k,v in pn.items() if v=='DISABLE_OR_TF'}=={'U14.4','U13.13','R33.1'}
assert (pn['R33.1'],pn['R33.2'])==('DISABLE_OR_TF','VDD_3V3')
assert (pn['C34.1'],pn['C34.2'])==('VDD_3V3','GND')
assert cs['C34'].findtext('value').startswith('100nF')
assert cs['R33'].findtext('value')=='270k CRCW0201 1pct 100ppm TOTAL<=10pct CANDIDATE'
assert not cs['R33'].findtext('footprint')
assert cs['R528'].find("property[@name='dnp']") is not None

# Exact device MUX truth table: C=0 selects B, C=1 selects A.
# Derive A/B/C levels from the actual netlist, so a wrong high tie is detected.
truth=[]
def output(disable,mode):
    levels={'VDD_3V3':True,'GND':False,'GLOBAL_DISABLE':disable,'MODE_TF':mode}
    a,b,c=(levels[pn['U14.'+p]] for p in ('3','1','6'))
    return a if c else b
for disable,mode in itertools.product([False,True],repeat=2):
    y=output(disable,mode)
    assert y==(disable or mode)
    truth.append({'GLOBAL_DISABLE':disable,'MODE_TF':mode,'U13_disable':y})
states=[]
for pg,qualified,mode in itertools.product([False,True],repeat=3):
    storage_enable=pg and qualified
    disable=not storage_enable
    y=output(disable,mode)
    assert y==((not pg) or (not qualified) or mode)
    if not qualified: assert disable and y
    states.append({'PG_valid':pg,'R528_deliberately_populated':qualified,'MODE_TF':mode,'U11_U12_disabled':disable,'U13_disabled':y})

# UUID regeneration is allowed; all other electrical assignments are not.
unchanged_before={k:v for k,v in baseline['pin_nets'].items() if not k.startswith('U14.')}
unchanged_after={k:v for k,v in pn.items() if not k.startswith('U14.')}
assert unchanged_after==unchanged_before,[(k,unchanged_before.get(k),unchanged_after.get(k)) for k in unchanged_before.keys()|unchanged_after.keys() if unchanged_before.get(k)!=unchanged_after.get(k)]
assert set(cs)==set(baseline['components'])
for ref,c in cs.items():
    actual={'value':c.findtext('value'),'footprint':c.findtext('footprint') or '', 'dnp':c.find("property[@name='dnp']") is not None}
    before=baseline['components'][ref]
    if ref not in ('U14','R33'):assert actual==before,(ref,before,actual)
    else:assert actual['dnp']==before['dnp'],ref
for relative,digest in baseline['protected_sha256'].items():
    assert hashlib.sha256((B/relative).read_bytes()).hexdigest()==digest,relative

rail=next(r for r in json.loads((H/'scaled-feedback-validation.json').read_text())['rails'] if r['rail']=='3V3')
vmin,vmax=rail['static_min_with_bias_V'],rail['static_max_with_bias_V']
assert .8<=vmin<=vmax<=3.6
rnom=float(cs['R33'].findtext('value').split('k')[0])*1000
rlo,rhi=rnom*.9,rnom*1.1
iinput=2e-6
sink=vmax/rlo+iinput
assert sink<20e-6
vol,voh=.11,vmin-.11
assert vol<.45 and voh>1.2 and iinput<20e-6
global_leak=2*2e-6+.75e-6+.75e-6
mode_leak=2*2e-6+.75e-6
global_high=vmin-global_leak*11000
mode_low=mode_leak*11000
assert global_high>2.32 and .39<.88 and mode_low<.88 and vmin>2.32
assert global_high>1.2 and .39<.45 and mode_low<.45
ioff=.75e-6
hypothetical_high=vmin-(ioff+iinput)*rhi
assert hypothetical_high>1.2
assert math.isclose(rlo,243000) and math.isclose(rhi,297000)
result={
 'status':'PASS_STRUCTURE_TRUTH_TABLE_AND_CONDITIONAL_DC_ONLY',
 'source_netlist_sha256':hashlib.sha256((H/'master.xml').read_bytes()).hexdigest(),
 'U14_part':cs['U14'].findtext('value'),'footprint':fp,'exact_pin_map':expected,'pin_functions_types_verified':True,
 'source_function':'Y=(A if C else B); A=1 gives B OR C','truth_table':truth,'storage_states':states,'default_R528_DNP':True,
 'unchanged_non_U14_pin_nets':len(unchanged_before),'unchanged_other_components':len(cs)-2,'protected_Samsung_and_source_files':len(baseline['protected_sha256']),
 'rail_V':[vmin,vmax],'R33_nominal_ohm':rnom,'R33_total_acceptance_fraction':.10,'R33_screen_ohm':[rlo,rhi],
 'low_state':{'worst_sink_A':sink,'specified_test_load_A':20e-6,'remaining_sink_budget_A':20e-6-sink,'VOL_max_V':vol,'TMUX_VIL_max_V':.45,'margin_V':.45-vol,'supply_range_of_output_row_V':[.8,3.6]},
 'high_state':{'receiver_sink_leakage_A':iinput,'VOH_min_V':voh,'TMUX_VIH_min_V':1.2,'margin_V':voh-1.2,'pullup_helps_output_high':True},
 'input_screens':{'GLOBAL_DISABLE_high_leakage_A':global_leak,'GLOBAL_DISABLE_high_min_V':global_high,'MODE_TF_leakage_A':mode_leak,'MODE_TF_low_max_V':mode_low,'VTplus_max_at_discrete_3V_V':2.32,'VTminus_min_at_discrete_3V_V':.88,'thresholds_guaranteed_at_actual_rail':False},
 'unpowered_screen':{'Ioff_A':ioff,'source_condition':'VCC=0, VI or VO=0–3.6V','hypothetical_independently_live_pullup_high_min_V':hypothetical_high,'same_rail_loss_high_guaranteed':False},
 'sources':['https://assets.nexperia.com/documents/data-sheet/74AUP1G97.pdf Rev14 Tables3/4/8/12 andFig6','https://www.ti.com/lit/ds/symlink/tmux1574.pdf RevC p6','engineering/passive-resistor-candidates/U14_SLEW_ADDENDUM.md'],
 'remaining_gates':['Resistance±10% is a total acceptance requirement, not guaranteed life drift.','Discrete3V Schmitt threshold extension to actualrail remains open.','Actual output capacitance, edge rate, TMUX timing and noise remain open; pullup does not set ordinary push-pull rise time.','Same-rail collapse and partial supply are not qualified.','No bench, SI, thermal or production qualification.']}
(H/'u14-or-validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(f'PASS U14 six-pin OR;4truth rows;8storage states;{len(unchanged_before)} other pin nets;{len(baseline["protected_sha256"])} protected files; DC sink{sink*1e6:.6f}uA')
