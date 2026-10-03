#!/usr/bin/env python3
"""Trace source declarations only through inductors, ferrites and explicit 0-ohm links."""
from pathlib import Path
import xml.etree.ElementTree as ET,json,collections
B=Path(__file__).resolve().parents[1];P=B/'cad/integrated'
x=ET.parse(P/'master.xml');pn={};values={c.get('ref'):c.findtext('value') for c in x.findall('.//components/comp')}
for n in x.findall('.//nets/net'):
 for p in n.findall('node'):pn[(p.get('ref'),p.get('pin'))]=n.get('name')
power_inputs={n.get('name') for n in x.findall('.//nets/net') if any(p.get('pintype')=='power_in' for p in n.findall('node'))}
dnp={c.get('ref') for c in x.findall('.//components/comp') if c.find("property[@name='dnp']") is not None}
graph=collections.defaultdict(list)
for r,v in values.items():
 if r not in dnp and (r.startswith('L') or r.startswith('FB') or (r.startswith('R') and v.startswith('0R'))) and (r,'1') in pn and (r,'2') in pn:
  a,b=pn[(r,'1')],pn[(r,'2')];graph[a].append((b,r));graph[b].append((a,r))
found={}
for ref,pin in [('U21','5'),('U22','C1'),('U23','C1'),('U24','5'),('U25','5'),('U26','5')]:
 start=pn[(ref,pin)];q=collections.deque([(start,[])]);seen=set()
 while q:
  n,path=q.popleft()
  if n in seen:continue
  seen.add(n)
  if path and n in power_inputs:
   assert n not in found
   found[n]={'net':n,'source':ref+'.'+pin,'switch_net':start,'passive_path':path,'declaration':'REGULATOR_THROUGH_PASSIVE_PATH','qualification':'connectivity_only_not_voltage_timing_thermal_approval'}
  for nxt,r in graph[n]:q.append((nxt,path+[r]))
assert len(found)==18,(len(found),found)
assert found['VEMMC_IO']['passive_path'][-1]=='R561' and not any(n.startswith('BANK') for n in found)
(P/'power-source-paths.json').write_text(json.dumps(list(found.values()),indent=2))
print(len(found),'traceable regulator-driven nets')
