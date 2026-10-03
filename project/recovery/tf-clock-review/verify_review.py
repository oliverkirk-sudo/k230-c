#!/usr/bin/env python3
"""Read-only HT-DRAFT13 topology checks and conditional R574 calculations.

Writes only this recovery directory. Never edits CAD or treats arithmetic as
electrical qualification. A proposed XML supplied with --candidate is checked
against the frozen baseline; the default checks an in-memory proposed mapping.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import math
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
checks = []

def check(name, condition):
    checks.append({'name': name, 'pass': bool(condition)})
    if not condition:
        raise AssertionError(name)

def read_netlist(path):
    tree = ET.parse(path).getroot()
    components = {c.get('ref'): c for c in tree.findall('./components/comp')}
    pinmap = {}
    for net in tree.findall('./nets/net'):
        for node in net.findall('node'):
            key = f"{node.get('ref')}.{node.get('pin')}"
            if key in pinmap:
                raise AssertionError(f'duplicate node: {key}')
            pinmap[key] = net.get('name')
    return tree, components, pinmap

def validate_candidate(candidate_components, candidate_map, base_components, base_map):
    # Exact delta: one two-pin resistor, no original pin reassignment/removal.
    if set(candidate_components) != set(base_components) | {'R574'}:
        return False
    if candidate_map != base_map | {'R574.1': 'TF_HOST_CLK', 'R574.2': 'GND'}:
        return False
    if candidate_components['R574'].findtext('value') != '10k CRCW020110K0FKED CANDIDATE':
        return False
    if candidate_components['R574'].find("property[@name='dnp']") is not None:
        return False
    for ref in base_components:
        for tag in ('value', 'footprint'):
            if candidate_components[ref].findtext(tag) != base_components[ref].findtext(tag):
                return False
        if (candidate_components[ref].find("property[@name='dnp']") is not None) != (base_components[ref].find("property[@name='dnp']") is not None):
            return False
    return True

parser = argparse.ArgumentParser()
parser.add_argument('--candidate', type=Path, help='Optional future XML; never written')
args = parser.parse_args()
base_tree, comps, pm = read_netlist(ROOT/'recovery/fresh-checks/master.xml')
cad_tree, cad_comps, cad_pm = read_netlist(ROOT/'cad/high-temp-candidate/master.xml')
check('restored and fresh-export connectivity match', pm == cad_pm)
check('R574 is absent from restored baseline', 'R574' not in comps)
check('TF_HOST_CLK has only U11.1 and U95.5',
      {p for p, n in pm.items() if n == 'TF_HOST_CLK'} == {'U11.1', 'U95.5'})
check('card clock exact edge membership',
      {p for p, n in pm.items() if n == 'TFCARD_CLK'} == {'U95.8', 'J1.21'})
check('host clock exact membership',
      {p for p, n in pm.items() if n == 'MMC0_CLK'} == {'U1.A5', 'U11.2'})
expected_u95 = {1:'TF_HOST_D2',2:'TF_HOST_D3',3:'TF_HOST_D0',4:'TF_HOST_D1',
    5:'TF_HOST_CLK',7:'GND',8:'TFCARD_CLK',9:'TFCARD_D1',10:'TFCARD_D0',
    11:'TFCARD_D3',12:'TFCARD_D2',13:'TFCARD_CMD',14:'VDD_3V3',15:'VDD1P8',16:'TF_HOST_CMD'}
for pin, net in expected_u95.items():
    check(f'U95.{pin} remains {net}', pm[f'U95.{pin}'] == net)
check('CLK_FB remains dedicated unconnected net',
      pm.get('U95.6', '').startswith('unconnected-') and
      sum(n == pm['U95.6'] for n in pm.values()) == 1)
for pin, net in {1:'TF_HOST_CLK',2:'MMC0_CLK',16:'EMMC_CLK',6:'GND',
                 13:'GLOBAL_DISABLE',14:'VDD_3V3',15:'MODE_TF'}.items():
    check(f'U11.{pin} remains {net}', pm[f'U11.{pin}'] == net)
check('R528 remains a DNP qualification strap value',
      'DNP' in comps['R528'].findtext('value') and
      comps['R528'].find("property[@name='dnp']") is not None)
check('all edge assignments preserved in restored export',
      {p:n for p,n in pm.items() if p.startswith('J1.')} ==
      {p:n for p,n in cad_pm.items() if p.startswith('J1.')})

candidate_comps = dict(comps)
r = ET.Element('comp', ref='R574')
ET.SubElement(r, 'value').text = '10k CRCW020110K0FKED CANDIDATE'
candidate_comps['R574'] = r
candidate_map = pm | {'R574.1':'TF_HOST_CLK','R574.2':'GND'}
check('proposed two-node delta preserves all originals',
      validate_candidate(candidate_comps, candidate_map, comps, pm))
bad = candidate_map | {'R574.1':'TFCARD_CLK'}
check('negative control rejects resistor on card output',
      not validate_candidate(candidate_comps, bad, comps, pm))
bad = candidate_map | {'U95.5':'GND'}
check('negative control rejects grounding CLKA directly',
      not validate_candidate(candidate_comps, bad, comps, pm))
bad = candidate_map | {'J1.21':'TF_HOST_CLK'}
check('negative control rejects bypassed level translation',
      not validate_candidate(candidate_comps, bad, comps, pm))
badcomps = copy.deepcopy(candidate_comps)
ET.SubElement(badcomps['R574'], 'property', name='dnp')
check('negative control rejects unpopulated pull-down',
      not validate_candidate(badcomps, candidate_map, comps, pm))
if args.candidate:
    _, ccomps, cmap = read_netlist(args.candidate)
    check('supplied future candidate has exact proposed delta',
          validate_candidate(ccomps, cmap, comps, pm))

# Same +/-10% total acceptance band as existing resistor screening.
# It is a required measured/qualified band, NOT a vendor lifetime guarantee.
rmin, rmax = 9000.0, 11000.0
vmin_full, vmax_full = 1.08, 1.98
reg = json.loads((ROOT/'engineering/passive-resistor-candidates/static-screen.json').read_text())
vmin_static, vmax_static = reg['rail_bounds_V']['1V8']
calc = {
 'status':'CONDITIONAL_CALCULATIONS_NOT_ELECTRICAL_OR_HARDWARE_PASS',
 'R574_ohm_acceptance_band':[rmin,rmax],
 'band_condition':'Total +/-10% must include tolerance, TCR, assembly, aging and environment; not automatically guaranteed',
 'published_NVT_operating_range_V':[vmin_full,vmax_full],
 'NVT_CLKA_VIL_fraction_VCCA':0.35,
 'NVT_CLKA_VIH_fraction_VCCA':0.65,
 'NVT_CLKA_leakage_bound_A':None,
 'TMUX_powered_switch_OFF_leakage_test_bound_A':100e-9,
 'TMUX_VDD_zero_leakage_test_bound_A':2e-6,
 'leakage_qualification_note':'Both TI values retain published test conditions; neither establishes NVT leakage or full partial-power behavior',
 'full_range':{
   'VIL_at_min_VCCA_V':0.35*vmin_full,
   'total_positive_DC_injection_ceiling_A':0.35*vmin_full/rmax,
   'remaining_after_100nA_TI_term_A':0.35*vmin_full/rmax-100e-9,
   'pull_high_current_upper_A':vmax_full/rmin,
   'pull_high_power_upper_W':vmax_full*vmax_full/rmin,
   'TMUX_drop_at_4p5ohm_and_that_current_V':vmax_full/rmin*4.5,
 },
 'existing_upstream_static_rail_screen_only':{
   'range_V':[vmin_static,vmax_static],
   'VIL_at_min_VCCA_V':0.35*vmin_static,
   'total_positive_DC_injection_ceiling_A':0.35*vmin_static/rmax,
   'remaining_after_100nA_TI_term_A':0.35*vmin_static/rmax-100e-9,
   'pull_high_current_upper_A':vmax_static/rmin,
   'pull_high_power_upper_W':vmax_static*vmax_static/rmin,
 },
 'TI_term_only_offset_V':100e-9*rmax,
 'TI_VDD_zero_term_only_offset_V':2e-6*rmax,
 'ideal_source_resistance_ceiling_for_VHIGH_ge_0p65VCCA_ohm':rmin*(1/0.65-1),
 'ideal_release_examples':[
   {'C_total_F':c,'tau_s':rmax*c,
    'from_VCCA_to_0p35VCCA_no_leak_s':-math.log(0.35)*rmax*c,
    'cross_0p65_to_0p35VCCA_no_leak_s':math.log(0.65/0.35)*rmax*c}
   for c in [10e-12,20e-12]],
 'release_example_limits':'Illustrations only. Unknown trace/probe/parasitic capacitance, leakage, induced charge, source Z, rail ramps and immunity remain unqualified.',
}
check('known TI powered switch-OFF leakage term alone below VIL',
      calc['TI_term_only_offset_V'] < calc['full_range']['VIL_at_min_VCCA_V'])
check('no invented NVT leakage guarantee', calc['NVT_CLKA_leakage_bound_A'] is None)
snap = json.loads((HERE/'cad-before-sha256.json').read_text())
current = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
           for p in sorted((ROOT/'cad').rglob('*')) if p.is_file()}
check('all CAD file bytes and membership unchanged during this review', snap == current)
result = {
 'scope':'Read-only restored-netlist/source review and in-memory proposed topology; no actual R574 CAD implementation',
 'baseline_revision':'v12 compact / HT-DRAFT13',
 'checks':checks, 'passed':len(checks), 'failed':0,
 'CAD_unchanged_files':len(current),
 'proposed_delta_validation':'IN_MEMORY_ONLY' if not args.candidate else str(args.candidate),
 'electrical_status':'OPEN: NVT input leakage, dynamic isolation and full timing/partial-power qualification',
 'hardware_test_status':'NOT_PERFORMED',
 'calculations':calc,
}
(HERE/'review-verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['passed','failed','CAD_unchanged_files','electrical_status','hardware_test_status']},indent=2))
