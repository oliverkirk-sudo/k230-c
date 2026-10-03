#!/usr/bin/env python3
"""Read the immutable CM-K230 R3 project and regenerate this bounded review.

Usage: python build_screen.py --project /path/to/project
No KiCad input, selected value, footprint or population is written.
"""
import argparse
import hashlib
import json
import math
import re
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET

ap = argparse.ArgumentParser()
ap.add_argument('--project', required=True, type=Path)
args = ap.parse_args()
project = args.project
out = Path(__file__).resolve().parent
master_path = 'cad/recovery-physical-candidate/master.xml'
footprint_path = 'cad/recovery-passive-candidates/CMK230_Recovery_Passive_Candidates.pretty/Vishay_CRCW0201_SourceLand_PROCESS_CANDIDATE.kicad_mod'
footprint = 'CMK230_Recovery_Passive_Candidates:Vishay_CRCW0201_SourceLand_PROCESS_CANDIDATE'
prior_path = 'engineering/passive-resistor-candidates/per-reference-classification.json'
old_screen_path = 'engineering/passive-resistor-candidates/static-screen.json'
logic_path = 'recovery/compact-logic-review/validation.json'
pdn_path = 'engineering/routing/pdn-budget-screen.json'
inputs = [master_path, footprint_path, prior_path, old_screen_path, logic_path, pdn_path]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
input_hashes = {p: sha(project / p) for p in inputs}
root = ET.parse(project / master_path).getroot()
components = {c.get('ref'): c for c in root.findall('./components/comp')}
nodes = {}
for n in root.findall('./nets/net'):
    for node in n.findall('node'):
        nodes.setdefault(node.get('ref'), []).append(dict(node.attrib, net=n.get('name')))
prior = json.loads((project / prior_path).read_text())
old = {r['reference']: r for r in prior['references']}
screen = json.loads((project / old_screen_path).read_text())
logic = json.loads((project / logic_path).read_text())
rails = {r['rail']: r for r in json.loads((project / pdn_path).read_text())['rails']}
v18lo, v18hi = [rails['1V8'][f'regulator_static_{k}_V'] for k in ('min', 'max')]
v33lo, v33hi = [rails['3V3'][f'regulator_static_{k}_V'] for k in ('min', 'max')]
vddlo, vddhi = [rails['DDR'][f'regulator_static_{k}_V'] for k in ('min', 'max')]

def nominal(value):
    m = re.match(r'([0-9.]+)([kKMR]?)', value)
    return float(m[1]) * {'':1, 'R':1, 'k':1000, 'K':1000, 'M':1000000}[m[2]]

codes = {4700:'4K70', 10000:'10K0', 22000:'22K0', 47000:'47K0', 100000:'100K', 270000:'270K', 1000000:'1M00'}
dat_refs = {f'R{i}' for i in range(563, 571)}
osc_refs = {'R41', 'R42'}
vset_refs = {'R205', 'R206'}
records = []
for ref, c in sorted(components.items(), key=lambda x: (x[0][0], int(re.sub(r'\D', '', x[0]) or 0))):
    if not re.fullmatch(r'R\d+', ref):
        continue
    value = c.findtext('value')
    r = nominal(value)
    fp = c.findtext('footprint', '')
    dnp = any(p.get('name') == 'dnp' for p in c.findall('property'))
    previous = old.get(ref, {})
    record = {
        'reference':ref, 'current_value_exact':value, 'nominal_ohm':r,
        'proposed_nominal_ohm':r, 'nominal_change_proposed':False,
        'current_footprint':fp, 'population':'DNP' if dnp else 'POPULATED',
        'connections':sorted(nodes[ref], key=lambda n:n['pin']),
        'role':previous.get('role', 'existing precision network' if 'TNPW' in value else 'existing TF clock idle bias'),
        'candidate_footprint':None, 'candidate_mpn':None,
        'production_qualified':False, 'CAD_edit_proposed_by_this_report':False,
    }
    if fp:
        record['disposition'] = 'PRESERVE_ASSIGNED_PRECISION' if 'TNPW' in value else 'PRESERVE_ASSIGNED_CRCW'
        record['electrical_gate'] = 'Keep selected family, exact value/MPN, tolerance/TCR, footprint and existing release gates. Not in this next-passive batch.'
        record['preserved_grade'] = {'initial_tolerance_pct':0.1,'TCR_ppm_per_K':10,'total_acceptance_pct':0.7} if 'TNPW' in value else {'MPN':'CRCW020110K0FKED','initial_tolerance_pct':1,'TCR_ppm_per_K':100}
    elif not r:
        record['disposition'] = 'EXCLUDE_ZERO_LINK'
        record['electrical_gate'] = {
            'R220':'Preserve WSL060300000ZEA9 high-current supply link.',
            'R221':'SoC VDD3P3_SD supply branch; zero-link current/voltage-drop review is separate.',
            'R401':'PMU auto-start strap; input/current/firmware and population review is separate.',
            'R528':'Preserve DNP qualification strap; no storage-enable authority follows from this review.',
            'R561':'Preserve WFZ040200000ZE66 supply-feed candidate and its current/drop gates.',
        }[ref]
    elif ref in vset_refs:
        record['disposition'] = 'EXCLUDE_PRECISION_VSET'
        record['electrical_gate'] = '56.2k selects 0.8V/address 0x49. TI Table 8-1 calls for +/-1% accuracy. Commodity initial 1% plus temperature/aging gives no proven total headroom. Preserve the separate precision selection path, without substituting or assigning here.'
        record['required_resistance_ohm'] = [55638, 56762]
        record['existing_separate_candidate'] = {'MPN':'TNPW040256K2BYED','nominal_ohm':56200,'initial_tolerance_pct':0.1,'TCR_ppm_per_K':10,'conditional_total_acceptance_pct':0.7,'status':'prior review candidate, not an assigned exact MPN in this master'}
    else:
        record.update({
            'disposition':'HOLD_DAT_TOTAL_ERROR' if ref in dat_refs else ('SEPARATE_OSCILLATOR_CANDIDATE' if ref in osc_refs else 'CONDITIONAL_BIAS_SOURCE_LAND_CANDIDATE'),
            'candidate_footprint':footprint,
            'candidate_mpn':'CRCW0201'+codes[r]+'FKED',
            'order_code_status':'manufacturer coding scheme only; exact orderability, stock and lifecycle not verified',
            'candidate_grade':{'initial_tolerance_pct':1,'TCR_ppm_per_K':100},
            'grade_preservation':'No stated tolerance/TCR is relaxed. Unspecified grades remain an engineering candidate. Screening +/-10% total does not overwrite any initial or total requirement.',
            'existing_explicit_requirements':value,
            'electrical_status':previous.get('electrical_status','OPEN'),
            'electrical_gate':previous.get('electrical_gate','Role-specific acceptance is open.'),
            'source_ids':['CRCW', 'ACTIVE_NETLIST'],
        })
        v = previous.get('power_screen_voltage_V', v18hi)
        if ref == 'R33':
            record['role'] = 'U14 Schmitt OR output / U13 EN pullup'
            record['electrical_status'] = 'BOUNDED_VALID_SUPPLY_DC_SCREEN'
            record['electrical_gate'] = 'Preserve 270k, 1% initial, 100ppm/K and <=10% total contract. R3 uses TI SN74LVC1G97DSFR; 15.9595uA worst sink demand fits its 100uA/0.1V light-load row. Shared-rail ramp and partial-power state remain open.'
            record['source_ids'] += ['R3_LOGIC_SCREEN','LVC97','TMUX']
            v = v33hi
        elif ref == 'R32':
            record['electrical_gate'] = 'R3 TI LVC97 input: released high >=3.137879532V under inherited 9.75uA bound. TMUX VIH=1.2V passes. TI Schmitt 1.87V threshold is a discrete 3V test point; full-rail extension, AUP06 loaded-low margin and power ramps remain open.'
            record['source_ids'] += ['R3_LOGIC_SCREEN','LVC97','TMUX','AUP06']
        elif ref == 'R31':
            record['source_ids'] += ['R3_LOGIC_SCREEN','LVC97','TMUX']
        elif ref in {'R43','R527','R529','R530'}:
            record['source_ids'] += ['PRIOR_SCREEN','TPS3808','AUP17','AUP2G97']
        elif ref in {'R61','R62'}:
            record['source_ids'] += ['MICRON_LP4']
            record['electrical_gate'] += ' These are ODT_CA input bias pulls, not the precision ZQ termination/calibration resistors.'
        elif ref in {'R203','R204','R216','R217','R218','R219'}:
            record['source_ids'] += ['PRIOR_SCREEN','TPS6282X','TPS62864']
        if ref in dat_refs:
            record['electrical_status'] = 'SOURCE_RANGE_APPLIES_BUT_TOTAL_ERROR_PROOF_OPEN'
            record['electrical_gate'] = 'Keep 47k. Active MTFC16GAPALBH-AAT is listed by the reviewed Micron family document. Table 13 permits DAT pullup 10-50k. The prior +/-10% band reaches 51.7k and fails; hold this batch until total resistance remains inside the source range across initial error, film temperature, assembly, aging and environment. No 43k substitution.'
            record['required_resistance_ohm'] = [10000,50000]
            record['maximum_positive_total_error_fraction'] = 50000/47000-1
            record['maximum_negative_total_error_fraction'] = 1-10000/47000
            record['maximum_symmetric_total_error_fraction'] = 50000/47000-1
            record['screen_10pct_range_pass'] = False
            record['source_ids'] += ['MICRON_EMMC']
        elif ref in {'R34','R562','R573'}:
            record['required_resistance_ohm'] = {'R34':[4700,50000], 'R562':[4700,50000], 'R573':[10000,100000]}[ref]
            record['source_ids'] += ['MICRON_EMMC']
        if ref in osc_refs:
            record['electrical_gate'] = '1M is inside the CRCW F/K family range, but crystal gain/startup/drive/parasitic loading are not covered by a bias/DC resistance screen. Keep this as a separate oscillator candidate, outside the 25-ref bias batch.'
        rmin, rmax = r*.9, r*1.1
        p = v*v/rmin
        record['conditional_DC_stress_screen'] = {
            'meaning':'Vmax across Rmin is a bounded steady-DC stress screen under the stated voltage and resistance assumptions, not a measured pin voltage or signal/thermal qualification.',
            'total_resistance_screen_fraction':0.1,
            'total_band_is_manufacturer_lifetime_guarantee':False,
            'Rmin_ohm':rmin,'Rmax_ohm':rmax,'Vmax_V':v,
            'I_at_Vmax_Rmin_A':v/rmin,'P_at_Vmax_Rmin_W':p,
            'P_allow_125C_from_graph_W':.05*30/85,
            'P_to_graph_125C_fraction':p/(.05*30/85),
            'working_voltage_125C_V':min(30,math.sqrt(.05*30/85*rmin)),
            'DC_rating_screen_pass':p < .05*30/85 and v < min(30,math.sqrt(.05*30/85*rmin)),
            'voltage_source':'5.5V regulator recommended-operating ceiling; carrier transient bound still open' if v==5.5 else 'project upstream static rail bound; distribution/ripple/ramps/overshoot excluded',
            'population_note':'Hypothetical fitted-state stress only; current dissipation is zero because position remains DNP.' if dnp else 'Existing populated position; this report does not change its population.',
        }
    records.append(record)

bias = [r['reference'] for r in records if r['disposition']=='CONDITIONAL_BIAS_SOURCE_LAND_CANDIDATE']
counts = Counter(r['disposition'] for r in records)
assert len(components)==254
assert sum(len(n) for n in nodes.values())==1509
assert len(root.findall('./nets/net'))==457
assert len(records)==62 and len(bias)==25
assert components['R33'].findtext('value').startswith('270k ')
assert any(p.get('name')=='dnp' for p in components['R528'].findall('property'))
assert all(r['nominal_ohm']==r['proposed_nominal_ohm'] for r in records)
assert {r['reference'] for r in records if r['population']=='DNP'}=={'R45','R47','R528'}

source_ids = {s for r in records for s in r.get('source_ids',[])}
sources = {k:v for k,v in prior['sources'].items() if k in source_ids}
sources['CRCW'] = dict(sources['CRCW'],prior_review_pdf_sha256=sources['CRCW']['local_sha256'],fresh_pdf_sha256='390a5effad7c3b526afb7faba340e29176261bfa4c041a128effc87b941a61ea',verification='fresh supplied PDF pp1-4 text; pp2 and3 visually inspected 2026-10-03; web source also opened. Fresh bytes differ from older review hash; technical pages retain revision21-Sep-2022, appended disclaimer is2026.')
del sources['CRCW']['local_sha256']
sources['MICRON_EMMC']['verification'] = 'Fresh 2026-10-03 web text check: ordering Table1 p2 includes active MTFC16GAPALBH-AAT; Table13 p27 gives resistance windows. Screenshot fetch failed; prior review provided visual check. No raw PDF redistributed.'
sources['MICRON_LP4']['verification'] = 'Fresh supplied local PDF text pp223/234 confirms ODT_CA +/-4uA and VIH>=0.75*VDD2; prior source identity retained.'
sources['TPS62864']['verification'] = 'Fresh TI common TPS62864/TPS62866 document text Table8-1 p12 via tps62866.pdf confirms 56.2k, 0.8V, address0x49 and +/-1% accuracy. Main alias fetch failed.'
sources['TPS62864']['fresh_read_url'] = 'https://www.ti.com/lit/ds/symlink/tps62866.pdf'
sources.update({
 'ACTIVE_NETLIST':{'project_path':master_path,'sha256':input_hashes[master_path]},
 'PRIOR_SCREEN':{'project_path':old_screen_path,'sha256':input_hashes[old_screen_path],'verification':'Reused bounded calculations; not all supporting device PDFs re-fetched. Old R33 and proposed43k DAT calculations deliberately excluded.'},
 'R3_LOGIC_SCREEN':{'project_path':logic_path,'sha256':input_hashes[logic_path],'verification':'TI LVC97 and dual AUP97 topology checked against active netlist; prior bounded logic values retained.'},
 'LVC97':{'url':'https://www.ti.com/lit/ds/symlink/sn74lvc1g97.pdf','verification':'Device limits inherited from current R3 logic review, not freshly audited here.'},
 'AUP2G97':{'url':'https://assets.nexperia.com/documents/data-sheet/74AUP2G97.pdf','verification':'Device limits inherited from current R3 logic review, not freshly audited here.'},
})

role_checks = {k:screen[k] for k in ['R43','R527','R529','R530','R61_R62','R203','R204','R572','private_i2c']}
role_checks['R31_R32_R33_current_TI_LVC97'] = {k:v for k,v in logic['TI_U14_screen'].items() if '43k' not in k}
role_checks['R527_R529_current_dual_AUP97'] = {k:logic['dual_screen'][k] for k in ['PG','qualifier_pulldown']}
role_checks['emmc_current_values'] = {k:v for k,v in screen['emmc_ranges'].items() if 'proposed' not in k}
role_checks['R33_current_formula'] = {'Rmin_ohm':243000,'sink_A':v33hi/243000+2e-6,'source_test_load_A':.0001,'VOL_V':.1,'TMUX_VIL_V':.45}
role_checks['R61_R62_recomputed'] = {'VDD2_static_min_V':vddlo,'VDD2_static_max_V':vddhi,'Rmax_ohm':11000,'leakage_max_A':4e-6,'drop_max_V':.044,'same_local_rail_high_margin_V':.25*vddlo-.044}

report = {
 'schema_version':1,'date':'2026-10-03','status':'READ_ONLY_BOUNDED_PACKAGE_AND_DC_SCREEN',
 'scope':'Preserve every nominal value, exact selected MPN, initial tolerance/TCR requirement, connection and DNP state; no production/procurement assertion.',
 'input_project':'CM-K230 immutable R3 project','input_sha256':input_hashes,
 'counts':{'all_references':254,'distinct_nets':457,'pin_net_nodes':1509,'resistor_references':62,'already_assigned_resistors':20,'unassigned_resistors':42,'unassigned_nonzero_resistors':37,'by_disposition':dict(counts)},
 'conditional_bias_batch_refs':bias,
 'conditional_bias_batch_populated_count':sum(r['reference'] in bias and r['population']=='POPULATED' for r in records),
 'conditional_bias_batch_DNP_refs':['R45','R47'],
 'hypothetical_assignment_coverage_only':{'current_assigned_all_refs':155,'if_25_candidates_later_bound':180,'unassigned_after_hypothetical_binding':74,'applied':False,'qualification_implied':False},
 'preserved_contract':{'R33_ohm':270000,'R528':'DNP','six_layers':True,'board_mm':[38,38],'edge_contacts':140,'top_only':True,'constraint_change_proposed':False,'complete_PCB_exists':False},
 'family':{k:v for k,v in screen['family'].items() if not any(word in k for word in ('reservation','hypothetical','rounded_hypothetical'))},
 'source_land_candidate':{'id':footprint,'project_path':footprint_path,'sha256':input_hashes[footprint_path],'copper_pad_mm':[.28,.43],'copper_gap_mm':.23,'pad_centers_x_mm':[-.255,.255],'body_max_mm':[.63,.33,.26], 'R3_process_assumptions':{'mask_expansion_per_edge_mm':.025,'paste':'explicit1:1','courtyard_centerline_mm':[1.39,1.03],'nominal_inner_mask_web_mm':.18},'manufacturer_approves_R3_mask_paste_courtyard':False},
 'DC_screen_assumptions':['The +/-10% resistance interval is a conditional working band and not a datasheet lifetime guarantee. It does not relax a tighter source requirement. R563-R570 fail it and are held.','Rail bounds are upstream regulator static corners, with VIN5V screened at5.5V. Pulses, distribution, ripple, overshoot, external drive and partial supply require separate bounds.','Derating is linear from50mW at70C to0mW at155C. Graph power limits assume acceptable PCB/solder-point heat flow and film<=155C. Local ambient is not enclosure-air temperature.','Thermal, mounting and lifetime behavior depend on actual board/mission profile. Independent Vishay qualification tests must not be summed into a guaranteed lifetime.','Schmitt threshold comparisons use the documented discrete source test points. No guaranteed interpolation across actual rail is asserted.'],
 'role_checks':role_checks,'sources':sources,'references':records,
 'release_gates':['Confirm exact candidate order codes and preserve F/K grades.','Close per-reference electrical gates and any tighter total-resistance windows.','Specify mission profile and qualify total drift at actual resistor film temperature.','Accept actual-board mask, paste, placement, reflow and inspection process.','Prove assembled-board routing, thermal and signal behavior separately.'],
}
(out/'bias-resistor-screen.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
assert input_hashes == {p:sha(project/p) for p in inputs}
verification = {'status':'PASS_READ_ONLY_ARTIFACT_CHECKS','checks':{'254_references':True,'457_distinct_nets':True,'1509_pin_net_nodes':True,'62_resistors_partitioned_once':True,'25_bias_candidates':True,'all_nominal_values_preserved':True,'R33_270k_preserved':True,'DNP_R45_R47_R528_preserved':True,'all_input_hashes_unchanged':True,'no_CAD_edit':True},'report_sha256':sha(out/'bias-resistor-screen.json')}
(out/'verification.json').write_text(json.dumps(verification,indent=2)+'\n')
print(json.dumps({'counts':dict(counts),'bias_refs':bias,'max_conditional_bias_power_W':max(r['conditional_DC_stress_screen']['P_at_Vmax_Rmin_W'] for r in records if r['reference'] in bias)},indent=2))
