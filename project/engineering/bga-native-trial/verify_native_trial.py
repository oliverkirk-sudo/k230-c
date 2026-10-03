#!/usr/bin/env python3
"""Re-import the delivered native board and compare its geometry and identities."""
import os
for name,suffix in [('XDG_DATA_HOME','.local/share'),('XDG_CONFIG_HOME','.config'),('XDG_CACHE_HOME','.cache')]:
    os.environ[name]='/tmp/kicad-footprint-home/'+suffix
import csv,hashlib,json,math
from collections import Counter
from pathlib import Path
import pcbnew as k

ROOT=Path(__file__).resolve().parents[2]
ENG=ROOT/'engineering/bga-native-trial'
CAD=ROOT/'cad/bga-engineering-candidates/bh153-sparse-trial'
BASE='BH153_SPARSE_LOCAL_TRIAL'
board=k.LoadBoard(str(CAD/(BASE+'.kicad_pcb')))
mapping={r['ball']:r for r in json.loads((ENG/'native-net-mapping.json').read_text())}
source=json.loads((ROOT/'engineering/bga-engineering-candidates/memory-soc-functional-escape-analysis-cu030-via030-hole015.json').read_text())
w=source['eMMC_local_witness']
f=list(board.GetFootprints());assert len(f)==1 and f[0].GetReference()=='U3'
pads=list(f[0].Pads()); assert len(pads)==153
def mm(v):return round(k.ToMM(v),7)
def xy(v):return (round(mm(v.x)-100,7),round(mm(v.y)-100,7))
def canonical_segment(net,layer,a,b,width):return (net,layer,tuple(sorted([tuple(a),tuple(b)])),width)
assert {p.GetNumber() for p in pads}==set(mapping)
for p in pads:
    m=mapping[p.GetNumber()]
    assert xy(p.GetPosition())==(m['local_x_mm'],m['local_y_mm'])
    assert p.GetNetname()==m['native_net']
    assert p.GetPinFunction()==m['function']
    assert (mm(p.GetSize().x),mm(p.GetSize().y))==(.30,.30)
    assert mm(p.GetSolderMaskExpansion(k.F_Mask))==.05
    paste=p.GetSolderPasteMargin(k.F_Paste)
    assert mm(paste.x)==mm(paste.y)==0
    assert p.GetShape()==k.PAD_SHAPE_CIRCLE and p.GetAttribute()==k.PAD_ATTRIB_SMD
    assert p.GetLayerSet().FmtHex()==k.PAD.SMDMask().FmtHex()
via_actual=[];track_actual=[]
for t in board.GetTracks():
    if isinstance(t,k.PCB_VIA):
        assert mm(t.GetDrillValue())==.15
        assert t.GetViaType()==k.VIATYPE_THROUGH
        for l in [k.F_Cu,k.In1_Cu,k.In2_Cu,k.In3_Cu,k.In4_Cu,k.In5_Cu,k.In6_Cu,k.B_Cu]: assert mm(t.GetWidth(l))==.30
        assert t.TopLayer()==k.F_Cu and t.BottomLayer()==k.B_Cu
        via_actual.append((t.GetNetname(),xy(t.GetPosition())))
    else:
        track_actual.append(canonical_segment(t.GetNetname(),board.GetLayerName(t.GetLayer()),xy(t.GetStart()),xy(t.GetEnd()),mm(t.GetWidth())))
via_expected=[(mapping[v['ball']]['native_net'],tuple(v['xy'])) for v in w['vias']]
track_expected=[canonical_segment(mapping[r['ball']]['native_net'],{'L1':'F.Cu','L3':'In2.Cu'}[r['layer']],a,b,r['width_mm']) for r in w['routes'] for a,b in zip(r['points'],r['points'][1:])]
assert Counter(via_actual)==Counter(via_expected)
assert Counter(track_actual)==Counter(track_expected)
assert len(via_actual)==29 and len(track_actual)==16
assert board.GetCopperLayerCount()==8
assert mm(board.GetDesignSettings().GetBoardThickness())==1.2
assert mm(board.GetDesignSettings().m_SolderMaskMinWidth)==.1
assert board.GetDesignSettings().m_AllowSoldermaskBridgesInFPs is False
assert '(stackup' not in (CAD/(BASE+'.kicad_pcb')).read_text()
assert len(list(board.Zones()))==0
assert all(net!='EMMC_DS_UNUSED' for net,*_ in via_actual+track_actual)
opened=[m['native_net'] for m in mapping.values() if m['independent_open_land']]
assert len(opened)==120 and len(set(opened))==120
assert all(n.startswith('unconnected-') for n in opened)
project=json.loads((CAD/(BASE+'.kicad_pro')).read_text())
assert project['board']['design_settings']['drc_exclusions']==[]
assert 'ignore' not in project['board']['design_settings']['rule_severities'].values()
assert '(severity ignore)' not in (CAD/(BASE+'.kicad_dru')).read_text()
manifest=json.loads((ENG/'source-manifest.json').read_text())
for entry in manifest['inputs'].values(): assert hashlib.sha256((ROOT/entry['path']).read_bytes()).hexdigest()==entry['sha256']
drc=json.loads((ENG/'native-drc.json').read_text())
counts=Counter(v['type'] for key in ['violations','unconnected_items'] for v in drc[key])
assert counts=={'track_dangling':12,'via_dangling':20,'unconnected_items':17},counts
controls=json.loads((ENG/'rule-control-results.json').read_text())
assert controls['status']=='PASS'
result={
 'status':'PASS_NATIVE_GEOMETRY_AND_IDENTITY_PARITY_ONLY',
 'native_full_DRC_status':'NOT_CLEAN_17_CONNECTIVITY_ERRORS_32_WARNINGS',
 'pads':153,'vias':29,'track_segments':16,'components':1,'zones':0,'copper_layers':8,
 'host_signals_with_local_exits':11,'host_signals_connected_to_SoC_endpoints':0,
 'net_identities_match_current_XML':True,'isolated_no_use_net_count':120,
 'no_use_function_counts':dict(Counter(m['function'] for m in mapping.values() if m['independent_open_land'])),
 'geometry_exactly_matches_frozen_witness':True,'source_inputs_unchanged':True,
 'DRC_counts':dict(counts),'DRC_exclusions':0,'ignored_DRC_severities':0,
 'positive_rule_controls':'PASS: annulus, hole-to-copper, hole-to-hole, mask web',
 'native_layers':['F.Cu','In1.Cu','In2.Cu','In3.Cu','In4.Cu','In5.Cu','In6.Cu','B.Cu'],
 'L3_maps_to':'In2.Cu','reference_thickness_mm':1.2,'explicit_dielectric_stack_defined':False,
 'NSMD_Cu_mask_paste_mm':[.30,.40,.30],'stencil_mm_assumption':.10,
 'nominal_mask_web_mm':.10,'nominal_mask_web_margin_mm':0,
 'nominal_annulus_mm':.075,'nominal_annulus_margin_mm':0,
 'manufacturing_qualification':'OPEN, including filled/planarized/copper-capped VIPPO and exact Micron PCB lands',
}
(ENG/'native-validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
