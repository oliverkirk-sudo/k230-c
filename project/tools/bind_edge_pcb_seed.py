#!/usr/bin/python3
"""Bind all core castellations to exported J1 nets; deliberately incomplete PCB seed."""
from pathlib import Path
import pcbnew as k,xml.etree.ElementTree as E,json,hashlib,shutil
B=Path(__file__).resolve().parents[1];S=B/'cad/high-temp-candidate';O=B/'cad/edge-bound-seed';O.mkdir(exist_ok=True)
x=E.parse(S/'master.xml'); c=x.find(".//components/comp[@ref='J1']")
assert c is not None and c.find("property[@name='exclude_from_board']") is None
assert c.find("property[@name='exclude_from_bom']") is not None
nets={}
for n in x.findall('.//nets/net'):
 for p in n.findall('node'):
  if p.get('ref')=='J1':nets[p.get('pin')]=n.get('name')
assert set(nets)==set(map(str,range(1,141)))
src=B/'cad/castellation-proposal/CMK230_Castellation_NOMINAL_PROPOSAL.kicad_pcb'
b=k.LoadBoard(str(src)); f=list(b.GetFootprints());assert len(f)==1;f=f[0]
f.SetReference('J1');f.SetValue('CM-K230 CORE EDGE - PROCESS UNQUALIFIED')
f.SetAttributes(f.GetAttributes() | k.FP_EXCLUDE_FROM_BOM)
nm={}
for name in sorted(set(nets.values())):
 n=k.NETINFO_ITEM(b,name);b.Add(n);nm[name]=n
for p in f.Pads():p.SetNet(nm[nets[p.GetNumber()]])
assert len(list(f.Pads()))==140
out=O/'CMK230_Core_EDGE_BOUND_INCOMPLETE.kicad_pcb';k.SaveBoard(str(out),b)
shutil.copyfile(src.with_suffix('.kicad_pro'),out.with_suffix('.kicad_pro'))
b=k.LoadBoard(str(out));f=list(b.GetFootprints())[0]
rows=[]
for p in sorted(f.Pads(),key=lambda p:int(p.GetNumber())):
 assert p.GetNetname()==nets[p.GetNumber()]
 rows.append({'pad':p.GetNumber(),'net':p.GetNetname(),'x_mm':k.ToMM(p.GetPosition().x),'y_mm':k.ToMM(p.GetPosition().y)})
r={'status':'140_EDGE_NETS_BOUND_INTERNAL_COMPONENTS_AND_ROUTING_ABSENT','source_netlist_sha256':hashlib.sha256((S/'master.xml').read_bytes()).hexdigest(),'source_mechanical_board_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'seed_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'contacts':rows,'edge_excluded_from_purchasable_bom':bool(f.GetAttributes() & k.FP_EXCLUDE_FROM_BOM),'schematic_edge_excluded_from_board':False,'contact_count':140,'distinct_edge_nets':len(nm),'internal_components_placed':0,'track_count':len(list(b.GetTracks())),'parity_full_design_pass_claimed':False}
(O/'edge-net-binding-validation.json').write_text(json.dumps(r,indent=2))
print('PASS all 140 contacts bound; J1 included on board, excluded only from purchasable BOM; incomplete seed')
