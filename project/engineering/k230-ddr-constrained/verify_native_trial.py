#!/usr/bin/python3
"""Round-trip comparison of the separate native coupon, preserving raw DRC."""
import os
for n in ['XDG_CONFIG_HOME','XDG_DATA_HOME','XDG_CACHE_HOME']:os.environ[n]='/tmp/k230-ddr-constrained/'+n
import hashlib,json,math
from collections import Counter
from pathlib import Path
import pcbnew as k
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
CAD=ROOT/'cad/bga-engineering-candidates/k230-ddr-constrained'
BASE='K230_DDR_CONSTRAINED_LOCAL_TRIAL'
j=json.loads((HERE/'trial-groups-outer-21.json').read_text());b=k.LoadBoard(str(CAD/(BASE+'.kicad_pcb')))
def local(p):return (round(k.ToMM(p.x)-100,8),round(k.ToMM(p.y)-100,8))
fps=list(b.GetFootprints());assert len(fps)==1 and fps[0].GetReference()=='U1'
pads=list(fps[0].Pads());assert len(pads)==390
padmap={p.GetNumber():p for p in pads}
for x in j['balls']:
    p=padmap[x['ball']];assert local(p.GetPosition())==(x['x'],x['y']);assert p.GetNetname()==x['xml_net'];assert p.GetPinFunction()==x['function'];assert k.ToMM(p.GetSize().x)==.27 and k.ToMM(p.GetSize().y)==.27
    assert set(p.GetLayerSet().CuStack())=={k.F_Cu}
tracks=[];vias=[]
for p in b.GetTracks():
    if isinstance(p,k.PCB_VIA):vias.append(p)
    else:tracks.append(p)
assert len(vias)==327
via_expected=Counter((tuple(v['xy']),v['net'],v['pad'],v['hole']) for v in j['vias'])
via_actual=Counter((local(v.GetPosition()),v.GetNetname(),k.ToMM(v.GetWidth(k.F_Cu)),k.ToMM(v.GetDrillValue())) for v in vias)
assert via_actual==via_expected
assert all(not v.GetRemoveUnconnected() for v in vias)
assert b.GetCopperLayerCount()==8
lm={'L1':k.F_Cu,'L3':k.In2_Cu,'L6':k.In5_Cu,'L8':k.B_Cu}
expected=Counter((tuple(a),tuple(z),r['net'],lm[r['layer']],.1016) for r in j['routes'] for a,z in zip(r['points'],r['points'][1:]))
actual=Counter((local(t.GetStart()),local(t.GetEnd()),t.GetNetname(),t.GetLayer(),k.ToMM(t.GetWidth())) for t in tracks)
assert expected==actual
drc=json.loads((HERE/'native-drc.json').read_text());counts=Counter(x['type'] for x in drc['violations'])
assert set(counts)<={'track_dangling','via_dangling'}
assert counts['via_dangling']==158
expected_pdn_missing=sum(n-1 for n in Counter(x['net'] for x in j['balls'] if x['category'] in ('power','ground')).values())
assert len(drc['unconnected_items'])==expected_pdn_missing==135
proj=json.loads((CAD/(BASE+'.kicad_pro')).read_text());s=proj['board']['design_settings']
assert not s['drc_exclusions'] and not any(v=='ignore' for v in s['rule_severities'].values())
assert s['rules']['min_hole_clearance']==.1524 and s['rules']['min_via_annular_width']==.0762
result=dict(status='PASS_EXACT_NATIVE_GEOMETRY_ROUNDTRIP_NOT_COMPLETE_BOARD_DRC',physical_lands=390,intentional_open_lands=23,retained_annulus_vias=327,track_segments=len(tracks),copper_layers=8,
    checked=['all pad numbers, coordinates, exact XML nets, functions and .27 mm copper','all via coordinates, nets, .325/.15 diameters and retained unused annuli','all route segment coordinates, layers, nets and widths','no ignored rule severities or DRC exclusions'],
    native_geometric_rule_violations=0,native_warning_counts=dict(counts),native_unconnected_pdn_items=135,
    pdn_missing_connection_accounting='sum(ball_count_per_supply_or_ground_net - 1) = 135; native planes deliberately absent',
    drc_clean=False,complete_board=False,schematic_parity='not run; exact U1 XML net mapping checked independently',
    source_sha256=hashlib.sha256((HERE/'trial-groups-outer-21.json').read_bytes()).hexdigest(),
    cad_sha256=hashlib.sha256((CAD/(BASE+'.kicad_pcb')).read_bytes()).hexdigest())
(HERE/'native-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
