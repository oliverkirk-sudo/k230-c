#!/usr/bin/env python3
from pathlib import Path
import csv,json,re,hashlib
B=Path(__file__).resolve().parents[1];H=B/'cad/high-temp-candidate';O=B/'engineering/routing';O.mkdir(exist_ok=True)
def rows(p):return list(csv.DictReader(open(p)))
length={r['soc_ball']:r for r in rows(B/'engineering/ddr-package-length-reference.csv')}
joins=rows(B/'data/k230-source-extraction/01studio-soc-to-lpddr4-65nets.csv');pins={(r['reference'],r['pin']):r for r in rows(H/'master-pin-assignments.csv')}
out=[]
for r in joins:
 a=pins['U1',r['soc_ball']];b=pins['U2',r['dram_ball']];assert a['net']==b['net']==r['reference_net']
 f=b['function'];l=length.get(r['soc_ball']);group='RESET_ASYNCHRONOUS'
 m=re.match(r'DQ(\d+)_([AB])$',f)
 if m:group=f"{m[2]}_BYTE{int(m[1])//8}"
 else:
  m=re.match(r'(?:DMI|DQS)([01])(?:_[TC])?_([AB])',f.upper())
  if m:group=f'{m[2]}_BYTE{m[1]}'
  elif f.endswith('_A'):group='A_ADDRESS_COMMAND'
  elif f.endswith('_B'):group='B_ADDRESS_COMMAND'
 out.append({'net':a['net'],'soc_ball':r['soc_ball'],'soc_actual_function':a['function'],'dram_ball':r['dram_ball'],'dram_actual_function':f,'sink_group':group,'soc_package_trace_um':l['package_trace_um'] if l else '', 'guide_alias_hazard':l['hazard'] if l else 'RESET not in high-speed package-length table','board_delay_ps':'UNROUTED','dram_package_delay_ps':'UNAVAILABLE','status':'SOURCE_JOINED_CONSTRAINT_INPUT_NOT_TIMING_PASS'})
from collections import Counter
counts=Counter(r['sink_group'] for r in out)
assert counts=={'A_BYTE0':11,'A_BYTE1':11,'B_BYTE0':11,'B_BYTE1':11,'A_ADDRESS_COMMAND':10,'B_ADDRESS_COMMAND':10,'RESET_ASYNCHRONOUS':1},counts
assert len(out)==65 and len({r['net'] for r in out})==65
with open(O/'high-temp-ddr-route-contract.csv','w') as f:
 w=csv.DictWriter(f,fieldnames=out[0]);w.writeheader();w.writerows(out)
groups={}
for r in out:
 if r['soc_package_trace_um']:groups.setdefault(r['sink_group'],[]).append(float(r['soc_package_trace_um']))
meta={'status':'SOURCE_JOINED_ROUTING_REQUIREMENTS_NOT_BOARD_TIMING_VALIDATION','net_count':65,'package_length_available':sum(bool(r['soc_package_trace_um']) for r in out),'group_package_length_spreads_um':{g:max(v)-min(v) for g,v in groups.items()},'sources':['https://github.com/kendryte/k230_docs/blob/main/en/00_hardware/K230_Hardware_Design_Guide.md','https://raw.githubusercontent.com/kendryte/k230_docs/main/zh/00_hardware/images/HDG/image056.png'],'recommendations':{'single_ended_ohm':50,'differential_ohm':100,'crosstalk_rule':'3W','same_signal_type_via_counts':'equal','maximum_layer_changes':2,'DQ_to_DQ_within_byte_or_nibble_ps':'<20','DQ_relative_DQS_ps':'+/-10','CA_CS_CKE_relative_CK_ps':'+/-10','DQS_relative_CK_without_write_leveling_ps':'+/-60'},'not_used_as_routing_budget':'Training deskew range is not the recommended routed skew allowance','package_trace_join_key':'physical SoC ball only; guide aliases never override actual audited net mapping','hashes':{str(p.relative_to(B)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [H/'master.xml',B/'engineering/ddr-package-length-reference.csv']}}
(O/'high-temp-ddr-route-contract-validation.json').write_text(json.dumps(meta,indent=2));print(json.dumps(meta,indent=2))
