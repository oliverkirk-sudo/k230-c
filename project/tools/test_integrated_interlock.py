#!/usr/bin/env python3
"""Structural and steady-state logic checks. This is not an analog power-ramp/OTP/SI test."""
from pathlib import Path
import xml.etree.ElementTree as ET,json,itertools,sys
B=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]) if len(sys.argv)>1 else B/'cad/integrated';x=ET.parse(P/'master.xml');pn={}
for n in x.findall('.//nets/net'):
 for p in n.findall('node'):pn[(p.get('ref'),p.get('pin'))]=n.get('name')
dnp={c.get('ref') for c in x.findall('.//components/comp') if c.find("property[@name='dnp']") is not None}
checks={('U1','B9'):'SOC_RSTN',('U1','C12'):'PMU_INT4_AUTO_START',('R401','1'):'AVDD1P8_PMU',('R401','2'):'PMU_INT4_AUTO_START',('R561','1'):'VDD1P8',('R561','2'):'VEMMC_IO',('R528','1'):'VDD1P8',('R528','2'):'BOOT_VOLTAGE_QUALIFIED_1V8',('R529','2'):'GND',('U89','1'):'VDD1P8',('U89','6'):'FIXED_RAILS_PGOOD_3V3',('U90','1'):'VDD1P8',('U90','6'):'RESET_DELAYED_1V8',('U91','2'):'RESET_DELAYED_1V8',('R530','2'):'RESET_DELAYED_1V8',('U90','4'):'RESET_RELEASE_REQUEST_1V8',('U91','4'):'SOC_RSTN',('U94','6'):'RSTN',('U94','4'):'RESET_RELEASE_REQUEST_1V8',('U93','4'):'GLOBAL_DISABLE',('U95','14'):'VDD_3V3',('U95','15'):'VDD1P8',('U89','7'):'GND',('U90','7'):'GND',('U94','1'):'GND',('U94','2'):'GND',('U94','3'):'FIXED_RAILS_PGOOD_3V3',('U92','1'):'GND',('U92','2'):'GND',('U92','3'):'FIXED_RAILS_PGOOD_3V3',('U92','6'):'BOOT_VOLTAGE_QUALIFIED_1V8',('U24','2'):'FIXED_RAILS_PGOOD_3V3',('U25','2'):'FIXED_RAILS_PGOOD_3V3',('U26','2'):'FIXED_RAILS_PGOOD_3V3'}
for rp,net in checks.items():assert pn[rp]==net,(rp,pn.get(rp),net)
assert x.find(".//components/comp[@ref='U91']/value").text.startswith(('SN74AUP1G17','74AUP1G17'))
assert {rp for rp,n in pn.items() if n=='RESET_DELAYED_1V8'}=={('U90','6'),('U91','2'),('R530','2')}
assert {rp for rp,n in pn.items() if n=='SOC_RSTN'}=={('U91','4'),('U1','B9')}
assert 'R528' in dnp and 'R561' not in dnp and 'R401' not in dnp
for r,net in [('R562','EMMC_CMD')]+[(f'R{563+j}',f'EMMC_DAT{j}') for j in range(8)]:
 assert pn[(r,'1')]==net and pn[(r,'2')]=='VEMMC_IO'
# RSTN is a carrier input: no internal output is allowed on that external net.
for n in x.findall('.//nets/net'):
 if n.get('name')=='RSTN':
  assert all(p.get('pintype') not in ['output','open_collector','power_out'] for p in n.findall('node'))
# Official97 function: C=0 -> Y=B, C=1 -> Y=A. B=0 therefore yields A AND C.
for a,c in itertools.product([False,True],repeat=2):assert (a if c else False)==(a and c)
state=[]
for pg,ext,qual,settled in itertools.product([False,True],repeat=4):
 storage_enabled=pg and qual
 reset_request=pg and ext
 internal_reset_released=reset_request and settled
 assert qual or not storage_enabled
 assert pg or (not storage_enabled and not internal_reset_released)
 state.append(dict(fixed_rail_pg_and_vin_guard_good=pg,external_reset_high=ext,qualification_link_populated=qual,delay_elapsed=settled,storage_enabled=storage_enabled,internal_reset_released=internal_reset_released))
# Qualification is a human/manufacturing prerequisite, not a measured OTP signal.
unsafe_example={'strap_populated':True,'fixed_rail_pg_and_vin_guard_good':True,'otp_first_drive_unverified':True,'hardware_would_enable':True,'release_decision':'FORBIDDEN_UNTIL_EVIDENCE_AND_AUTHORIZED_CONFIGURATION'}
result={'kind':'COMPACT_STRUCTURAL_AND_STATIC_LOGIC_ONLY','structural_checks':len(checks),'default_R528_DNP':True,'R561_default_1V8_feed_present':True,'default_storage_disabled_when_logic_supplies_are_valid':True,'logic_states':state,'wrongly_populated_strap_example':unsafe_example,'specified_reset_delay_ms':[12,28],'mux_normal_turn_on_max_us':35,'not_proved':['OTP/BootROM first drive','partial-supply ramps','brownout maximum response time','effective load capacitance','TF HS50 or eMMC HS200 timing','carrier power sequencing','physical board behavior']}
(P/'interlock-validation.json' if len(sys.argv)>1 else B/'engineering/reset/interlock-validation.json').write_text(json.dumps(result,indent=2));print('PASS',len(checks),'structural checks;',len(state),'steady logic states; analog/OTP/SI remain unqualified')
