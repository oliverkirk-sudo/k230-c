#!/usr/bin/env python3
"""Reproduce the bounded resistor-candidate screen from its frozen netlist extract.

No CAD file is modified. Resistance acceptance bands are requirements, not a
manufacturer lifetime model. Run from any directory; outputs stay beside script.
"""
from pathlib import Path
import hashlib
import json
import re

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
snapshot = json.loads((OUT / 'input-snapshot.json').read_text())
rails = {r['rail']: r for r in snapshot['static_rail_source']['rails']}
v18lo, v18hi = [rails['1V8'][f'regulator_static_{x}_V'] for x in ('min', 'max')]
v33lo, v33hi = [rails['3V3'][f'regulator_static_{x}_V'] for x in ('min', 'max')]
vddlo = rails['DDR']['regulator_static_min_V']
tol = 0.10
def bounds(r, t=tol):
    return [r * (1-t), r * (1+t)]
def crcw(r):
    return 'CRCW0201' + {4700:'4K70',10000:'10K0',22000:'22K0',43000:'43K0',47000:'47K0',100000:'100K',1000000:'1M00'}[r] + 'FKED'

source_specs = {
    'CRCW': ('/workspace/shared/k230-reference/mechanical/passive-review/vishay-CRCW0201e3.pdf', 'https://www.vishay.com/docs/20052/crcw0201e3.pdf', '20052, 21-Sep-2022, pp1-4'),
    'TNPW': ('/workspace/shared/k230-reference/TNPW_e3.pdf', 'https://www.vishay.com/docs/28758/tnpw_e3.pdf', '28758, 10-Apr-2026, pp2-4'),
    'TNPW_LANDS': ('/workspace/shared/k230-reference/Vishay_28950.pdf', 'https://www.vishay.com/doc?28950', '28950, 12-Jul-2022, p1'),
    'TPS3808': ('/workspace/shared/k230-reference/tps3808.pdf', 'https://www.ti.com/lit/ds/symlink/tps3808.pdf', 'Rev N, Aug-2026, electrical characteristics p6'),
    'TPS6282X': ('/workspace/shared/k230-reference/tps62827.pdf', 'https://www.ti.com/lit/ds/symlink/tps62827.pdf', 'electrical characteristics p5'),
    'TPS62864': ('/workspace/shared/k230-reference/tps62864.pdf', 'https://www.ti.com/lit/ds/symlink/tps62864.pdf', 'Rev C, pp5-8 and Table8-1 p12'),
    'LVC32': ('/workspace/shared/k230-reference/mechanical/sn74lvc1g32-ti.pdf', 'https://www.ti.com/lit/ds/symlink/sn74lvc1g32.pdf', 'Rev W, Aug-2026, pp6-7'),
    'TMUX': ('/workspace/shared/k230-switch-review/tmux1574-ti-rev-c.pdf', 'https://www.ti.com/lit/ds/symlink/tmux1574.pdf', 'Rev C, p6 and sections8.3.4/8.3.5'),
    'MICRON_EMMC': ('/workspace/shared/k230-memory-review/thermal-candidates/micron-emmc.pdf', 'https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/234/EMMC_5F00_DATASHEET.pdf', 'Micron automotive eMMC Rev G, Table13 p27'),
    'MICRON_LP4': ('/workspace/shared/k230-memory-review/thermal-candidates/micron-lp4.pdf', 'https://www.mouser.com/datasheet/2/671/200b_z00m_sdp_ddp_auto_lpddr4_lpddr4x-3193603.pdf', 'Micron automotive LPDDR4/4X Rev F, Table153 p223 and Table170 p234'),
}
sources = {k: {'url':u,'locator':d,'local_sha256':hashlib.sha256(Path(p).read_bytes()).hexdigest()} for k,(p,u,d) in source_specs.items()}
sources.update({
 'AUP97': {'url':'https://assets.nexperia.com/documents/data-sheet/74AUP1G97.pdf','locator':'Rev14 pp6-8; 125C column; discrete VCC test points'},
 'AUP17': {'url':'https://assets.nexperia.com/documents/data-sheet/74AUP1G17.pdf','locator':'Rev14 pp5-7; 125C column; discrete VCC test points'},
 'AUP06': {'url':'https://assets.nexperia.com/documents/data-sheet/74AUP1G06.pdf','locator':'Rev12 pp5-7; 125C column'},
 'K230_GUIDE': {'url':'https://github.com/kendryte/k230_docs/blob/main/en/00_hardware/K230_Hardware_Design_Guide.md','locator':'power table VDD3P3_SD=50mA design budget; not transient maximum'},
 'K230_PINOUT': {'url':'https://kendryte-download.canaan-creative.com/developer/k230/HDK/K230%E7%A1%AC%E4%BB%B6%E6%96%87%E6%A1%A3/K230_PINOUT_V1.2_20240822.xlsx','locator':'main rows12/13/32/82, PMU IO AVDD1P8_LDO; default rows67-69/71 input/pulldown'},
 'K230_IO': {'url':'https://atta.szlcsc.com/upload/public/pdf/source/20240304/CED0BDC8B8BEDC72BFC23F1C8A2ED83A.pdf','locator':'Manufacturer-authored datasheet mirror, PDF pp29-30; generic IO, PMU applicability unproven'},
 'I2C_RC': {'url':'https://www.ti.com/lit/an/slva689/slva689.pdf','locator':'p2, ideal30-70% RC rise-time relation'},
})

screen = {
 'status':'CONDITIONAL_STATIC_ACCEPTANCE_SCREEN_NOT_LIFETIME_OR_BOARD_QUALIFICATION',
 'resistance_total_acceptance_fraction':tol,
 'initial_tolerance_fraction':0.01,
 'tcr_ppm_per_K':100,
 'assumptions':['The +/-10% band must include all actual tolerance, temperature, assembly, aging and environmental shifts. It is not derived as a guaranteed mission life from separate manufacturer tests.', 'Rail bounds are upstream static regulator corners. PCB drop, ripple, load steps, board leakage and timing are not included.', 'Schmitt comparisons retain the published 1.65V supply test point and do not interpolate guarantees across 1V8.', 'All loading checks require the named source limits to apply under the actual device conditions.'],
 'rail_bounds_V':{'1V8':[v18lo,v18hi],'3V3':[v33lo,v33hi]},
 'family': {'resistance_range_1pct_100ppm_ohm':[47,1e6], 'resistance_range_1pct_200ppm_ohm':[10,1e7], 'low_resistance_range_1pct_ohm':[1,9.76], 'low_resistance_tcr_ppm_per_K':[-200,400], 'operating_temperature_C':[-55,155], 'limiting_element_voltage_V':30, 'P70_W':0.05, 'maximum_film_temperature_C':155, 'graph_derated_power_W':{str(t):0.05*(155-t)/85 for t in [85,105,125]}, 'endurance_70C_1000h_delta_R':'±(2% R + 0.1 ohm)', 'endurance_70C_8000h_delta_R':'±(4% R + 0.1 ohm)', 'upper_category_155C_1000h_delta_R':'±(2% R + 0.1 ohm)', 'soldering_heat_delta_R':'±(1% R + 0.05 ohm)', 'body_nominal_mm':[0.60,0.30,0.23], 'body_tolerance_mm':[0.03,0.03,0.03], 'source_pad_mm':[0.28,0.43], 'source_inner_gap_mm':0.23, 'pad_centers_x_mm':[-0.255,0.255], 'copper_envelope_mm':[0.79,0.43], 'existing_dense_reservation_mm':[1.1,0.7], 'hypothetical_0p05_mask_plus_0p25_clearance_envelope_mm':[1.39,1.03], 'rounded_hypothetical_envelope_mm':[1.4,1.1], 'mask_paste_courtyard_qualified':False},
 'R527': {'R_ohm':bounds(10000), 'leakage_A':2.1e-6, 'high_drop_V':2.1e-6*11000, 'high_min_V':v33lo-2.1e-6*11000, 'sink_upper_bound_A':v33hi/9000+2.1e-6, 'sink_limit_A':0.0004, 'sink_margin_A':0.0004-(v33hi/9000+2.1e-6), 'guaranteed_low_bound_V':0.4, 'discrete_VTminus_min_V':0.47, 'discrete_low_margin_V':0.07, 'note':'Conservatively includes the full released-node leakage even when U89 is sinking; TPS3808 has 0.3V at <1.8V/0.4mA and 0.4V at >=1.8V/1mA; use 0.4V common ceiling. Regulator PG leakage is tabulated at5V; applying its 0.1uA bound to3V3 remains a source-condition interpretation.'},
 'R530': {'R_ohm':bounds(100000), 'leakage_A':1.05e-6, 'high_drop_V':1.05e-6*110000, 'high_min_V':v18lo-1.05e-6*110000, 'discrete_VTplus_max_V':1.31, 'discrete_high_margin_V':v18lo-1.05e-6*110000-1.31, 'sink_upper_bound_A':v18hi/90000+0.75e-6, 'sink_limit_A':0.0004, 'discrete_low_margin_V':0.47-0.4},
 'R529': {'R_ohm':bounds(100000), 'leakage_A':0.75e-6, 'low_max_V':0.75e-6*110000, 'discrete_VTminus_min_V':0.47, 'discrete_low_margin_V':0.47-0.75e-6*110000},
 'R43': {'R_ohm':bounds(100000), 'known_logic_leakage_A':0.75e-6, 'high_min_excluding_cap_carrier_board_leakage_V':v18lo-0.75e-6*110000, 'discrete_high_margin_before_external_loads_V':v18lo-0.75e-6*110000-1.31, 'additional_sink_leakage_budget_to_1p31V_A':(v18lo-1.31)/110000-0.75e-6, 'gate':'100nF C45 leakage, carrier loading, RC rise time and external reset sink must be included.'},
 'R31': {'R_ohm':bounds(10000), 'load_leakage_A':9e-6, 'default_low_max_V':9e-6*11000, 'TMUX_VIL_max_V':0.45, 'low_margin_V':0.45-9e-6*11000, 'gate':'Valid powered controls; JP1 cold-only and external leakage assumptions retained.'},
 'R32': {'R_ohm':bounds(10000), 'high_leakage_A':9.75e-6, 'high_min_V':v33lo-9.75e-6*11000, 'LVC_VIH_min_V':2, 'high_margin_V':v33lo-9.75e-6*11000-2, 'sink_upper_bound_A':v33hi/9000+9e-6, 'AUP06_discrete_VOL_V':0.39, 'TMUX_VIL_max_V':0.45, 'discrete_low_margin_V':0.06, 'gate':'AUP06 loaded VOL is at discrete1.65V supply. Leakage/source conditions and full rail interpretation remain signoff items.'},
 'R33': {'current_nominal_ohm':10000, 'proposed_nominal_ohm':43000, 'R_ohm':bounds(43000), 'actual_net_loads':['U14.4 Y','U13.13 EN','R33.1'], 'supply_net':'VDD_3V3', 'old_sink_upper_bound_A':v33hi/9000+2e-6, 'old_125C_3V_16mA_VOL_max_V':0.5, 'TMUX_VIL_max_V':0.45, 'proposed_sink_upper_bound_A':v33hi/(43000*.9)+2e-6, 'source_light_load_limit_A':100e-6, 'sink_reserve_A':100e-6-(v33hi/(43000*.9)+2e-6), 'proposed_VOL_max_V':0.1, 'low_margin_V':0.45-0.1, 'proposed_VOH_min_V':v33lo-0.1, 'TMUX_VIH_min_V':1.2, 'high_margin_V':v33lo-0.1-1.2, 'Ioff_125C_A':25e-6, 'Ioff_explicit_test_condition':'VCC=0V; VI or VO=5.5V', 'hypothetical_live_pullup_unpowered_U14_high_min_V':v33lo-27e-6*(43000*1.1), 'hypothetical_high_margin_V':v33lo-27e-6*(43000*1.1)-1.2, 'unpowered_gate':'25uA use at actual3V3 node is a conditional extension of the explicit5.5V test. U14 VCC and pullup are physically the same net; independently live pullup is not a normal stable state. This does not establish behavior during common-rail ramps or partial supply.'},
 'R61_R62': {'R_ohm':bounds(10000), 'ODT_CA_leakage_A':4e-6, 'max_high_drop_V':4e-6*11000, 'VIH_fraction_VDD2':0.75, 'same_local_rail_high_margin_V':.25*vddlo-4e-6*11000, 'gate':'Uses selected Micron Table153 ODT_CA leakage and Table170 level, with local VDD2 assumed equal at pullup/DRAM. Validate rank/ODT configuration and distribution.'},
 'R203': {'R_ohm':bounds(100000), 'five_EN_plus_PG_leakage_A':.6e-6, 'released_high_drop_V':.6e-6*110000, 'example_at_2p5V_high_V':2.5-.6e-6*110000, 'sink_upper_bound_at_5p5V_A':5.5/90000+.5e-6, 'PG_VOL_max_V':.4,'EN_VIL_max_V':.4,'guaranteed_low_noise_margin_V':0,'gate':'The published PG low ceiling equals EN low ceiling. No positive guaranteed DC noise margin or startup/ramp closure follows from this resistor.'},
 'R204': {'R_ohm':bounds(10000),'EN_leakage_A':.1e-6,'high_drop_V':.1e-6*11000,'example_at_2p5V_high_V':2.5-.1e-6*11000,'EN_VIH_min_V':1.0},
 'R572': {'R_ohm':bounds(100000),'conditional_generic_K230_leakage_A':10e-6,'conditional_low_max_V':10e-6*110000,'conditional_generic_VIL_V':.35*v18lo,'conditional_margin_V':.35*v18lo-10e-6*110000,'gate':'Dedicated MMC0_STROBE applicability/internal pull state unknown. Generic10uA model cannot establish a low with100k. Physical candidate only; no electrical approval.'},
 'emmc_ranges':{},
 'R205_R206': {'candidate_mpn':'TNPW040256K2BYED','nominal_ohm':56200,'total_acceptance_fraction':.007,'screen_ohm':bounds(56200,.007),'TI_required_ohm':bounds(56200,.01),'status':'PRECISION_CONDITIONAL_CANDIDATE_ONLY'},
 'private_i2c': {'references':['R216','R217','R218','R219'],'R_ohm':bounds(4700),'regulator_VIH_min_V':1.0,'regulator_VIL_max_V':.4,'regulator_SCL_max_leakage_A':.2e-6,'regulator_SDA_max_leakage_A':.1e-6,'SCL_high_margin_before_unknown_load_V':v18lo-5170*.2e-6-1.0,'SDA_high_margin_before_unknown_load_V':v18lo-5170*.1e-6-1.0,'unknown_sink_leakage_coefficient_ohm':5170,'external_pullup_current_at_0V_A':v18hi/4230,'external_pullup_current_at_0p4V_A':(v18hi-.4)/4230,'regulator_SDA_SCL_absolute_max_sink_A':.002,'absolute_max_is_output_drive_guarantee':False,'generic_K230_VOL_max_V':.45,'generic_K230_to_TI_low_margin_V':-.05,'PMU_generic_IO_applicability_verified':False,'PMU_supply_identity':'AVDD1P8_LDO, established in official pinout; supplied here by filtered AVDD1P8_PMU','default_pad_state':'Input/pulldown; disable internal pulls or account for them','ideal_RC_capacitance_ceiling_F':{str(t_ns)+'ns':t_ns*1e-9/(.8473*5170) for t_ns in (1000,300,120)},'gate':'No guaranteed complete bidirectional DC margin. TI SDA VOL/IOL guarantee absent in inspected electrical table; K230 PMU electrical data applicability unproven and generic0.45V VOL already exceeds TI0.4V VIL. RC values are requirements, not measured capacitance.'},
 'zero_links': {'R221':{'nominal_budget_A':.05,'CRCW_70C_max_R_ohm':.05,'room_or_rated_condition_drop_V':.05*.05,'power_W':.05**2*.05,'gate':'50mA is guide budget, not peak/inrush maximum;1A jumper rating explicitly70C. Hot current/resistance not qualified.'},'R528':{'dnp':True,'max_static_load_if_fitted_A':v18hi/90000+.75e-6,'gate':'Do not populate qualification strap by default; this current check grants no boot-voltage qualification.'},'R401':{'gate':'Do not select until PMU input current/internal pull and firmware ownership are checked. Never drive the strapped input low.'}},
}
for key, r, limit in [('R562_CMD',22000,[4700,50000]),('R563_R570_DAT_current',47000,[10000,50000]),('R563_R570_DAT_proposed',43000,[10000,50000]),('R34_RST',10000,[4700,50000]),('R573_DS',47000,[10000,100000])]:
    lo,hi=bounds(r); screen['emmc_ranges'][key]={'nominal_ohm':r,'screen_ohm':[lo,hi],'source_range_ohm':limit,'range_pass':lo>=limit[0] and hi<=limit[1],'upper_margin_ohm':limit[1]-hi}

roles = {
 'R31':('MODE_TF default pulldown','R31','Valid-supply conditional static screen passes; JP1 remains cold-only.'),
 'R32':('GLOBAL_DISABLE pullup','R32','Conditional valid-supply static screen passes; full AUP supply interpretation remains open.'),
 'R33':('U14 output/U13 EN pullup','R33','Propose43k to put the low-state load within the all-supply100uA guarantee; current10k has unclosed125C low margin.'),
 'R34':('eMMC reset pullup','emmc_ranges.R34_RST','Micron resistance range passes; source/switch waveform and reset state remain open.'),
 'R41':('RTC crystal feedback',None,'1M value is in100ppm family range. Oscillator gain, startup, crystal drive and leakage must be checked; no resistance-only oscillation approval.'),
 'R42':('24MHz crystal feedback',None,'1M value is in100ppm family range. Oscillator gain, startup, crystal drive and leakage must be checked; no resistance-only oscillation approval.'),
 'R43':('external reset request pullup','R43','Known Schmitt leakage screen passes; carrier and C45 leakage/RC must be included.'),
 'R44':('BOOT0 low strap',None,'Boot sampling, internal pulls, exact GPIO thresholds/leakage and carrier drive remain open.'),
 'R45':('BOOT0 high option DNP',None,'Preserve DNP. Do not fit simultaneously with R44 without a deliberate boot network change.'),
 'R46':('BOOT1 high strap',None,'Boot sampling, internal pulls, exact GPIO thresholds/leakage and carrier drive remain open.'),
 'R47':('BOOT1 low option DNP',None,'Preserve DNP. Do not fit simultaneously with R46 without a deliberate boot network change.'),
 'R61':('LPDDR4 ODT_CA_A pullup','R61_R62','Selected Micron leakage/threshold screen passes, subject to local VDD2 and ODT/rank configuration.'),
 'R62':('LPDDR4 ODT_CA_B pullup','R61_R62','Selected Micron leakage/threshold screen passes, subject to local VDD2 and ODT/rank configuration.'),
 'R203':('core PG to downstream enable pullup','R203','High/sink loading plausible; published PG VOL equals EN VIL so positive low noise margin is unclosed.'),
 'R204':('core regulator enable pullup','R204','Valid-supply input-leakage screen passes; startup remains a system gate.'),
 'R216':('private CPU I2C SCL pullup','private_i2c','Regulator-side high bound only; PMU pad electrical applicability, low drive and RC/ramp remain open.'),
 'R217':('private CPU I2C SDA pullup','private_i2c','Regulator-side high bound only; PMU pad electrical applicability, low drive and RC/ramp remain open.'),
 'R218':('private KPU I2C SCL pullup','private_i2c','Regulator-side high bound only; PMU pad electrical applicability, low drive and RC/ramp remain open.'),
 'R219':('private KPU I2C SDA pullup','private_i2c','Regulator-side high bound only; PMU pad electrical applicability, low drive and RC/ramp remain open.'),
 'R402':('PMU INT0 inactive pulldown',None,'Exact PMU input leakage/internal pull and startup state must be checked; physical family candidate only.'),
 'R527':('raw fixed-rail PG pullup','R527','Conditional sink/current/static level screen passes; narrow sink reserve and published test-point caveats retained.'),
 'R529':('default inhibit pulldown','R529','Conditional discrete1.65V low screen passes; R528 stays DNP.'),
 'R530':('delayed reset pullup','R530','Conditional discrete1.65V high/low screen passes. Current value says1% but the proposed total acceptance screen is10%; this is not an exact delay tolerance.'),
 'R562':('eMMC CMD pullup','emmc_ranges.R562_CMD','Micron resistance range passes. Active-mode signal timing, switch loading and protocol setup remain open.'),
 'R571':('eMMC CLK idle pulldown',None,'Exact eMMC CLK leakage/low limit and switch state are not established here; family/physical candidate only.'),
 'R572':('unused host strobe pulldown','R572','Dedicated K230 pin limits/internal pulls unresolved; generic10uA model fails low-state proof.'),
 'R573':('unused eMMC DS pulldown','emmc_ranges.R573_DS','Micron resistance range passes; keep separate from host MMC0_STROBE.'),
}
for i in range(563,571): roles[f'R{i}']=(f'eMMC DAT{i-563} pullup','emmc_ranges.R563_R570_DAT_proposed','Propose43k:47k±10% exceeds Micron50k maximum;43k±10% passes. No CAD edit made.')

refs=[]
for c in snapshot['resistors']:
    if c['current_footprint']: continue
    d=dict(c); ref=c['reference']
    if ref in ('R205','R206'):
        d.update(classification='PRECISION_STARTUP_SELECTION',role='TPS628640 startup voltage/address selection',candidate_family='Vishay TNPW0402 e3',candidate_mpn='TNPW040256K2BYED',proposed_nominal_ohm=56200,total_resistance_acceptance_fraction=.007,check_key='R205_R206',layout_disposition='USE_EXISTING_REVIEWED_TNPW0402_SOURCE_LAND',electrical_gate='Retain TI±1% total VSET requirement and conditional±0.70% mission-profile acceptance. Not an ordinary±10% resistor.',sources=['TNPW','TNPW_LANDS','TPS62864'])
    elif ref in ('R220','R561'):
        d.update(classification='PREVIOUSLY_REVIEWED_POWER_JUMPER',role='DDR core supply feed' if ref=='R220' else 'eMMC VCCQ feed',candidate_mpn='WSL060300000ZEA9' if ref=='R220' else 'WFZ040200000ZE66',layout_disposition='KEEP_EXISTING_SEPARATE_SOURCE_REVIEW',electrical_gate='No commodity0201 substitution; use existing part-specific source/current/land review and retained hot/inrush gates.',existing_review='../mechanical/passive-small-parts-review.md')
    elif ref in ('R221','R401','R528'):
        d.update(classification='ROLE_SPECIFIC_ZERO_LINK',role={'R221':'K230 VDD3P3_SD supply branch','R401':'same-domain PMU auto-start input strap','R528':'DNP boot qualification strap'}[ref],candidate_mpn=None if ref=='R401' else 'CRCW02010000Z0ED',layout_disposition='SELECTION_DEFERRED_PENDING_INPUT_CURRENT' if ref=='R401' else 'CONDITIONAL_ROLE_SPECIFIC_0201_CANDIDATE',check_key=f'zero_links.{ref}',electrical_gate=screen['zero_links'][ref]['gate'],sources=['CRCW','K230_GUIDE'] if ref!='R528' else ['CRCW','AUP97'])
    else:
        raw=c['current_value'].split()[0]; m=re.fullmatch(r'([\d.]+)([kMR]?)',raw); assert m,raw
        old=float(m[1])*{'':1,'R':1,'k':1000,'M':1000000}[m[2]]
        proposed=43000 if ref=='R33' or 563<=int(ref[1:])<=570 else old
        role,check,gate=roles[ref]
        d.update(classification='ORDINARY_NONZERO',role=role,current_nominal_ohm=old,proposed_nominal_ohm=proposed,nominal_change_proposed=proposed!=old,candidate_family='Vishay CRCW0201 e3',candidate_mpn=crcw(proposed),order_code_status='MANUFACTURER_SCHEMA_SUPPORTED_NOT_STOCK_OR_LIFECYCLE_VERIFIED',initial_tolerance_fraction=.01,tcr_ppm_per_K=100,total_resistance_acceptance_fraction=.10,screen_resistance_ohm=bounds(proposed),layout_disposition='CONDITIONAL_SOURCE_LAND_CANDIDATE',electrical_status='BOUNDED_STATIC_CHECK' if check else 'ROLE_ELECTRICAL_ACCEPTANCE_OPEN',check_key=check,electrical_gate=gate,sources=['CRCW'])
        if ref in ('R41','R42'): d['power_screen_voltage_V']=v18hi
        elif ref in ('R203','R204'):d['power_screen_voltage_V']=5.5
        elif ref in ('R31','R32','R33','R527'):d['power_screen_voltage_V']=v33hi
        elif ref in ('R61','R62'):d['power_screen_voltage_V']=rails['DDR']['regulator_static_max_V']
        else:d['power_screen_voltage_V']=v18hi
        d['conservative_full_rail_power_W']=d['power_screen_voltage_V']**2/bounds(proposed)[0]
        d['power_gate']='Full-rail DC stress illustration. Actual resistor film temperature, thermal path and voltage/transients must be verified; does not establish operating function.'
    refs.append(d)
assert len(refs)==42
assert len([x for x in refs if x['classification']=='ORDINARY_NONZERO'])==35
assert {x['reference'] for x in refs if x.get('nominal_change_proposed')} == {'R33',*[f'R{i}' for i in range(563,571)]}
assert screen['R527']['sink_margin_A']>0
assert screen['R33']['sink_reserve_A']>0
assert screen['emmc_ranges']['R563_R570_DAT_current']['range_pass'] is False
assert screen['emmc_ranges']['R563_R570_DAT_proposed']['range_pass'] is True
for d in refs:
    if d['reference'] in ('R203','R216','R217','R218','R219','R572'):
        d['electrical_status']='BOUNDED_CHECK_HAS_UNRESOLVED_ELECTRICAL_MARGIN'
    if d['reference']=='R33':
        d['electrical_status']='STATIC_LOAD_SCREEN_ONLY_U14_INPUT_SLEW_OPEN'
        d['additional_review']='U14_SLEW_ADDENDUM.md'
        d['electrical_gate']+=' R33 alone does not resolve U14 input slew. AUP97 true-OR/270k is a separate explicit alternative proposal.'
result={'status':screen['status'],'scope':'42 initially unassigned resistor positions; no CAD edits by this audit','input_master_sha256':snapshot['sha256'],'input_static_rail_sha256':snapshot['static_rail_source']['sha256'],'counts':{'all_resistors':61,'already_assigned_precision':19,'audited_unassigned':42,'ordinary_nonzero':35,'startup_precision':2,'zero_links':5,'dnp_in_audit':sum(x['dnp'] for x in refs),'proposed_nominal_changes':9},'sources':sources,'references':refs}
(OUT/'per-reference-classification.json').write_text(json.dumps(result,indent=2)+'\n')
(OUT/'static-screen.json').write_text(json.dumps(screen,indent=2)+'\n')
print(json.dumps({'counts':result['counts'],'R527_sink_margin_uA':screen['R527']['sink_margin_A']*1e6,'R530_discrete_high_margin_mV':screen['R530']['discrete_high_margin_V']*1000,'R33_sink_reserve_uA':screen['R33']['sink_reserve_A']*1e6,'ordinary_peak_full_rail_power_mW':max(x.get('conservative_full_rail_power_W',0) for x in refs)*1000},indent=2))
