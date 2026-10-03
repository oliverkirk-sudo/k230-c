#!/usr/bin/env python3
"""Digital connectivity test, not SPICE/SI/timing or power-sequence simulation."""
import pathlib,csv,json,xml.etree.ElementTree as ET
r=pathlib.Path(__file__).resolve().parents[1];e=r/'engineering/storage'
expected={(v['reference'],v['pin']):v['net'] for v in csv.DictReader((e/'switch-pin-net-matrix.csv').open())}
t=ET.parse(e/'switch-netlist.xml');actual={}
for net in t.findall('.//nets/net'):
 for node in net.findall('node'):actual[(node.attrib['ref'],node.attrib['pin'])]=net.attrib['name'].lstrip('/')
assert all(actual.get(k)==v for k,v in expected.items()),[(k,v,actual.get(k)) for k,v in expected.items() if actual.get(k)!=v]
ch={1:(2,16,1),2:(5,3,4),3:(7,9,8),4:(10,12,11)}
results=[]
for mode in [0,1]:
 for disable in [0,1]:
  edges={}
  def link(a,b):edges.setdefault(a,set()).add(b);edges.setdefault(b,set()).add(a)
  def reach(a):
   found={a};todo=[a]
   while todo:
    for b in edges.get(todo.pop(),set()):
     if b not in found:found.add(b);todo.append(b)
   return found
  for ref in ['U11','U12','U13']:
   en=disable or mode if ref=='U13' else disable;sel=0 if ref=='U13' else mode
   if not en:
    for d,a,b in ch.values():link(expected[(ref,str(d))],expected[(ref,str(b if sel else a))])
  for signal in ['CLK','CMD']+[f'D{i}' for i in range(8)]:
   h='MMC0_'+signal;dest='EMMC_'+('DAT'+signal[1:] if signal.startswith('D') else signal);targets=reach(h)
   assert 'GND' not in targets
   if disable or (mode and signal in ['D4','D5','D6','D7']):assert targets=={h}
   elif mode:assert 'TF_HOST_'+signal in targets and dest not in targets
   else:assert dest in targets and all(not n.startswith('TF_HOST_') for n in targets)
  if not disable and mode:assert 'GND' in reach('EMMC_RSTN') and 'MMC0_RST_N' not in reach('EMMC_RSTN')
  if not disable and not mode:assert 'MMC0_RST_N' in reach('EMMC_RSTN')
  if disable:assert reach('EMMC_RSTN')=={'EMMC_RSTN'}
  results.append({'MODE_TF':mode,'GLOBAL_DISABLE':disable,'connectivity_pass':True})
report={'kind':'static truth-table connectivity ONLY','pin_net_assignments_verified':len(expected),'exported_pin_assignments':len(actual),'states':results,'not_tested':['BootROM voltage','partial-power ramp','propagation delay','HS200 SI/eye/tuning','real switch leakage','physical hardware']}
(e/'switch-connectivity-test.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
