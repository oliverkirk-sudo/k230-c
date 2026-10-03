#!/usr/bin/env python3
import csv,json,collections,pathlib,xml.etree.ElementTree as ET
P=pathlib.Path(__file__).resolve().parent;B=P.parents[1]
def read(p):return list(csv.DictReader(open(p)))
a=ET.parse(P/'master.xml');pn={};nn={}
for n in a.findall('.//nets/net'):
 nn[n.get('name')]=[(x.get('ref'),x.get('pin')) for x in n.findall('node')]
 for rp in nn[n.get('name')]:assert rp not in pn;pn[rp]=n.get('name')
m=read(P/'master-pin-assignments.csv');bad=[r for r in m if r['net'] and not r['reference'].startswith('#PS') and pn.get((r['reference'],r['pin']))!=r['net']]
ddr=read(B/'data/k230-source-extraction/01studio-soc-to-lpddr4-65nets.csv');dbad=[r for r in ddr if pn.get(('U1',r['soc_ball']))!=pn.get(('U2',r['dram_ball'])) or pn.get(('U1',r['soc_ball']))!=r['reference_net']]
mods=read(B/'engineering/module-to-soc-candidates.csv');gpio=[r for r in mods if 'GPIO' in r['module_name'] or r['module_name'] in ['BANK5_IO62','BANK5_IO63']];gbad=[r for r in gpio if sorted(nn.get(r['module_name'],[]))!=sorted([('J1',r['module_pin']),('U1',r['soc_ball'])])]
tfbad=[n for n,nodes in nn.items() if n.startswith('TFCARD_') and any(ref=='U1' for ref,pin in nodes)]
declarations=[r for r in m if r['reference'].startswith('#PS')]
source_paths=json.load(open(P/'power-source-paths.json'))
assert len(declarations)==26 and {r['net'] for r in declarations}=={r['net'] for r in source_paths}|{'VIN_5V','GND'}|{f'BANK{x}_VDDIO' for x in range(6)}
assert {r['net'] for r in declarations if r['net'].startswith('BANK')}=={f'BANK{x}_VDDIO' for x in range(6)}
e=json.load(open(P/'erc.json'));v=[v for s in e['sheets'] for v in s['violations']]
special={('U1','F14'):'AVDD1P8_PMU',('U1','F15'):'AVDD1P8_PMU',('U1','B10'):'PWR_CPU_SCL',('U1','A10'):'PWR_CPU_SDA',('U1','A11'):'PWR_KPU_SCL',('U1','D12'):'PWR_KPU_SDA',('U1','A9'):'GND',('U3','C2'):'EMMC_VDDI',('C61','1'):'VDD1P1_DDR_IO',('C61','2'):'DDR_VREF'}
special_bad=[(ref,pin,net,pn.get((ref,pin))) for (ref,pin),net in special.items() if pn.get((ref,pin))!=net]
# Samsung exact-part supply naming: VDDF=VCC flash; VDD=VCCQ I/O.
emmc_supply_bad=[]
for r in read(B/'engineering/memory/KLMAG1JETD_explicit_function_balls.csv'):
 if r['function'] in ['VDD','VDDF']:
  expected={'VDD':'VEMMC_IO','VDDF':'VDD_3V3'}[r['function']]
  if pn.get(('U3',r['ball']))!=expected:emmc_supply_bad.append((r['ball'],r['function'],expected,pn.get(('U3',r['ball']))))
assert not emmc_supply_bad
memory_supply_audit=[]
for r in read(B/'engineering/memory/KLMAG1JETD_explicit_function_balls.csv'):
 expected={'VDD':'VEMMC_IO','VDDF':'VDD_3V3','VDDI':'EMMC_VDDI','VSS':'GND'}.get(r['function'])
 if expected:memory_supply_audit.append({'reference':'U3','ball':r['ball'],'manufacturer_name':r['function'],'expected':expected,'actual':pn.get(('U3',r['ball']))})
for r in read(B/'engineering/memory/K4F8E304HB_grid264_physical200.csv'):
 if r['physical_ball']!='True':continue
 expected={'VDD1':'VDD1P8','VDD2':'VDD1P1_DDR_IO','VDDQ':'VDD1P1_DDR_IO'}.get(r['function'])
 if r['function'].startswith('VSS'):expected='GND'
 if expected:memory_supply_audit.append({'reference':'U2','ball':r['ball_or_grid'],'manufacturer_name':r['function'],'expected':expected,'actual':pn.get(('U2',r['ball_or_grid']))})
assert all(r['expected']==r['actual'] for r in memory_supply_audit)
(P/'memory-supply-audit.json').write_text(json.dumps(memory_supply_audit,indent=2))
assert not special_bad
r={'virtual_source_declarations':len(declarations),'physical_memory_power_ground_balls_audited':len(memory_supply_audit),'emmc_supply_polarity_mismatches':emmc_supply_bad,'special_power_bias_mismatches':special_bad,'xml_assignment_mismatches':bad,'ddr_join_mismatches':dbad,'exposed_gpio_net_collisions':gbad,'exposed_gpio_count':len(gpio),'TF_nets_bypassing_selector':tfbad,'unique_references':len(a.findall('.//components/comp')),'net_count_including_open_pin_nets':len(nn),'erc_counts':dict(collections.Counter(x['type'] for x in v)),'erc_severity':dict(collections.Counter(x['severity'] for x in v)),'erc_total':len(v),'status':'REVIEW_ONLY_ERC_ZERO_NOT_HARDWARE_QUALIFIED' if not v else 'REVIEW_ONLY_UNRESOLVED_ERC_NOT_FABRICATION_READY'}
(P/'netlist-validation.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2));assert not any([bad,dbad,gbad,tfbad])
