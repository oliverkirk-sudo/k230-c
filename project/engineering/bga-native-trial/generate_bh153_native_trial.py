#!/usr/bin/env python3
"""Export the frozen eMMC local witness to KiCad 9 without completing a board.

Run with /usr/bin/python3 (distribution pcbnew module). All source paths are read-only.
Only cad/bga-engineering-candidates/bh153-sparse-trial and engineering/bga-native-trial
are generated. This is an engineering experiment, not a manufacturing release.
"""
import os
for name, suffix in [('XDG_DATA_HOME','.local/share'),('XDG_CONFIG_HOME','.config'),('XDG_CACHE_HOME','.cache')]:
    os.environ[name] = '/tmp/kicad-footprint-home/' + suffix

import csv
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
import pcbnew as k

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'cad/bga-engineering-candidates/bh153-sparse-trial'
ENG = ROOT / 'engineering/bga-native-trial'
BASE = 'BH153_SPARSE_LOCAL_TRIAL'
FPNAME = 'MTFC16GAPALBH_AAT_BH153_NSMD030_ENGINEERING_ONLY'
LIB = OUT / 'BH153_Engineering.pretty'
for p in (OUT, ENG, LIB, OUT/'preview'):
    p.mkdir(parents=True, exist_ok=True)

INPUTS = {
    'analysis': ROOT/'engineering/bga-engineering-candidates/memory-soc-functional-escape-analysis-cu030-via030-hole015.json',
    'balls': ROOT/'engineering/bga-engineering-candidates/memory-soc-functional-balls-cu030-via030-hole015.csv',
    'alternative_process': ROOT/'engineering/bga-engineering-candidates/alternate-via-process-check.json',
    'package_evidence': ROOT/'engineering/bga-engineering-candidates/micron-emmc-package-evidence.json',
    'pin_assignment': ROOT/'cad/high-temp-candidate/master-pin-assignments.csv',
    'netlist': ROOT/'cad/high-temp-candidate/master.xml',
}
hashes = {key:hashlib.sha256(p.read_bytes()).hexdigest() for key,p in INPUTS.items()}
witness = json.loads(INPUTS['analysis'].read_text())['eMMC_local_witness']
balls = [x for x in csv.DictReader(INPUTS['balls'].open()) if x['package']=='BH153']
assigned = {x['pin']:x for x in csv.DictReader(INPUTS['pin_assignment'].open()) if x['reference']=='U3'}
xml_pins = {}
for net in ET.parse(INPUTS['netlist']).findall('.//nets/net'):
    for node in net.findall('node'):
        if node.get('ref')=='U3':
            xml_pins[node.get('pin')] = {'net':net.get('name'),'function':node.get('pinfunction'),'type':node.get('pintype')}
assert len(balls)==len(assigned)==153
assert {b['ball'] for b in balls}==set(assigned)
assert len(witness['vias'])==29 and witness['required_host_signals']==11
for ball in balls:
    a=assigned[ball['ball']]
    assert a['function']==ball['function'], (ball,a)
    if a['net']:
        assert xml_pins[ball['ball']]['net']==a['net']
        assert xml_pins[ball['ball']]['function']==a['function']
    else:
        assert a['function'] in ['NC','RFU'] or a['function'].startswith('VSF')
        assert ball['ball'] not in xml_pins or xml_pins[ball['ball']]['net'].startswith('unconnected-')
assert assigned['A6']['net']=='GND' and assigned['M6']['net']=='EMMC_CLK'
native_by_ball={ball:xml_pins[ball]['net'] for ball in assigned}
assert len({native_by_ball[ball] for ball,a in assigned.items() if not a['net']})==120

def mm(x): return k.FromMM(x)
def point(x,y): return k.VECTOR2I(mm(x),mm(y))
def local(xy): return point(xy[0]+100,xy[1]+100)
def dump(p,obj): p.write_text(json.dumps(obj,indent=2)+'\n')

board = k.BOARD()
board.SetCopperLayerCount(8)
settings=board.GetDesignSettings()
settings.SetBoardThickness(mm(1.2))
settings.m_HasStackup=False
settings.m_MinClearance=mm(.1016)
settings.m_TrackMinWidth=mm(.1016)
settings.m_ViasMinSize=mm(.30)
settings.m_MinThroughDrill=mm(.15)
settings.m_ViasMinAnnularWidth=mm(.075)
settings.m_HoleClearance=mm(.20)
settings.m_HoleToHoleMin=mm(.20)
settings.m_SolderMaskExpansion=mm(0)
settings.m_SolderMaskMinWidth=mm(.10)
settings.m_SolderMaskToCopperClearance=mm(0)
settings.m_AllowSoldermaskBridgesInFPs=False
settings.m_SolderPasteMargin=mm(0)
settings.m_SolderPasteMarginRatio=0
settings.m_TentViasFront=True
settings.m_TentViasBack=True
settings.m_CopperEdgeClearance=mm(.20)
settings.m_MaxError=mm(.001)
netmap={}
for name in sorted(set(native_by_ball.values())):
    n=k.NETINFO_ITEM(board,name)
    board.Add(n)
    netmap[name]=n

fp=k.FOOTPRINT(board)
fp.SetFPID(k.LIB_ID('BH153_Engineering',FPNAME))
fp.SetReference('U3')
fp.SetValue('MTFC16GAPALBH-AAT')
fp.SetAttributes(k.FP_SMD)
fp.SetLibDescription('Engineering NSMD 0.30/0.40/0.30 mm copper/mask/paste; 153 physical balls only. Not manufacturer-qualified. Filled/planarized/copper-capped VIPPO required. 0.10 mm stencil assumption unqualified.')
fp.Reference().SetPosition(point(4.6,-5.8))
fp.Reference().SetLayer(k.F_Fab)
fp.Reference().SetTextSize(point(.65,.65))
fp.Reference().SetTextThickness(mm(.1))
fp.Value().SetPosition(point(0,7.2))
fp.Value().SetLayer(k.F_Fab)
fp.Value().SetTextSize(point(.5,.5))
fp.Value().SetTextThickness(mm(.08))
for ball in balls:
    a=assigned[ball['ball']]
    pad=k.PAD(fp)
    pad.SetNumber(ball['ball'])
    pad.SetAttribute(k.PAD_ATTRIB_SMD)
    pad.SetShape(k.PAD_SHAPE_CIRCLE)
    pad.SetSize(point(.30,.30))
    pad.SetPosition(point(float(ball['x_mm']),float(ball['y_mm'])))
    pad.SetLayerSet(k.PAD.SMDMask())
    pad.SetLocalSolderMaskMargin(mm(.05))
    pad.SetLocalSolderPasteMargin(mm(0))
    pad.SetLocalSolderPasteMarginRatio(0.0)
    pad.SetPinFunction(a['function'])
    pad.SetPinType(xml_pins.get(ball['ball'],{}).get('type','no_connect'))
    pad.SetNet(netmap[native_by_ball[ball['ball']]])
    fp.Add(pad)

def fp_segment(a,b,layer,width=.1):
    s=k.PCB_SHAPE(fp);s.SetShape(k.SHAPE_T_SEGMENT);s.SetStart(point(*a));s.SetEnd(point(*b));s.SetLayer(layer);s.SetWidth(mm(width));fp.Add(s)
# Component top view, +X right, +Y down. Chamfer identifies A1 corner.
corners=[(-5.75,-5.8),(-5.05,-6.5),(5.75,-6.5),(5.75,6.5),(-5.75,6.5),(-5.75,-5.8)]
for a,b in zip(corners,corners[1:]): fp_segment(a,b,k.F_Fab)
for a,b in zip([(-6,-6.75),(6,-6.75),(6,6.75),(-6,6.75),(-6,-6.75)],[(6,-6.75),(6,6.75),(-6,6.75),(-6,-6.75)]): fp_segment(a,b,k.F_CrtYd,.05)
board.Add(fp)
# Footprint library contains pads with physical identity but no board-specific nets.
k.PCB_IO_MGR.PluginFind(k.PCB_IO_MGR.KICAD_SEXP).FootprintSave(str(LIB),fp)
fp.SetPosition(point(100,100))

for via in witness['vias']:
    v=k.PCB_VIA(board); v.SetPosition(local(via['xy']));v.SetWidth(k.F_Cu,mm(.30));v.SetDrill(mm(.15))
    v.SetViaType(k.VIATYPE_THROUGH);v.SetLayerPair(k.F_Cu,k.B_Cu)
    v.SetNet(netmap[assigned[via['ball']]['net']])
    # No separate via mask openings: the land supplies its 0.40 mm opening.
    # This does NOT represent physical hole filling; VIPPO remains mandatory.
    v.SetFrontTentingMode(k.TENTING_MODE_TENTED);v.SetBackTentingMode(k.TENTING_MODE_TENTED)
    board.Add(v)
for route in witness['routes']:
    for a,b in zip(route['points'],route['points'][1:]):
        t=k.PCB_TRACK(board); t.SetStart(local(a)); t.SetEnd(local(b));t.SetWidth(mm(route['width_mm']))
        t.SetLayer({'L1':k.F_Cu,'L3':k.In2_Cu}[route['layer']]);t.SetNet(netmap[assigned[route['ball']]['net']]);board.Add(t)

def line(a,b,layer,width=.1):
    s=k.PCB_SHAPE(board);s.SetShape(k.SHAPE_T_SEGMENT);s.SetStart(local(a));s.SetEnd(local(b));s.SetLayer(layer);s.SetWidth(mm(width));board.Add(s)
def text(value,xy,size=.6):
    t=k.PCB_TEXT(board);t.SetText(value);t.SetPosition(local(xy));t.SetTextSize(point(size,size));t.SetTextThickness(mm(.09));t.SetLayer(k.Dwgs_User);board.Add(t)
# Computational boundary only, explicitly not the 38 mm product outline.
corners=[(-10,-10),(10,-10),(10,10),(-10,10),(-10,-10)]
for a,b in zip(corners,corners[1:]): line(a,b,k.Edge_Cuts)
text('LOCAL ANALYSIS WINDOW - NOT MODULE PCB',(0,-9),.45)
text('8 Cu layers | 1.2 mm reference | NO QUALIFIED STACK',(0,8.4),.36)
text('VIPPO REQUIRED | 11 LOCAL EXITS ONLY | NO PDN',(0,9.2),.36)
for route in witness['routes']:
    if route['ball'] in ['A6'] or (route['ball'] in ['M5','M6'] and route['layer']=='L1'): continue
    endpoint=route['points'][-1]
    if endpoint[1]==-7:
        # Alternate label positions keep adjacent 0.5 mm tracks legible.
        continue
    text(assigned[route['ball']]['net'],[endpoint[0],endpoint[1]-.25],.25)
text('DAT0-7 local exits on L1 / L3',(-1.75,-7.6),.38)
k.SaveBoard(str(OUT/(BASE+'.kicad_pcb')),board)
(OUT/'fp-lib-table').write_text('(fp_lib_table\n  (version 7)\n  (lib (name "BH153_Engineering")(type "KiCad")(uri "${KIPRJMOD}/BH153_Engineering.pretty")(options "")(descr "Unqualified local engineering candidate"))\n)\n')

# Use installed KiCad 9's full severity key set; any ignored defaults are raised
# to warning. No exclusions, allow-bridge override, or waived checks.
template=json.loads(Path('/usr/share/kicad/template/Arduino_Uno/Arduino_Uno.kicad_pro').read_text())
severities=template['board']['design_settings']['rule_severities']
severities={key:('warning' if value=='ignore' else value) for key,value in severities.items()}
rules={
    'min_clearance':.1016,'min_track_width':.1016,'min_via_diameter':.30,
    'min_through_hole_diameter':.15,'min_via_annular_width':.075,
    'min_hole_clearance':.20,'min_hole_to_hole':.20,
    'min_copper_edge_clearance':.20,'solder_mask_to_copper_clearance':0,
    'max_error':.001,'min_text_height':.15,'min_text_thickness':.025,
    'min_silk_clearance':.10,'min_connection':0,'min_resolved_spokes':2,
    'allow_blind_buried_vias':False,'allow_microvias':False,
}
project={'meta':{'filename':BASE+'.kicad_pro','version':1},
    'board':{'design_settings':{'meta':{'filename':'board_design_settings.json','version':2},
        'rules':rules,'rule_severities':severities,'drc_exclusions':[],
        'track_widths':[0,.1016],'via_dimensions':[{'diameter':.30,'drill':.15}]}},
    'net_settings':{'meta':{'version':4},'classes':[{'name':'Default','clearance':.1016,'track_width':.1016,'via_diameter':.30,'via_drill':.15,'microvia_diameter':.2,'microvia_drill':.1,'diff_pair_width':.1016,'diff_pair_gap':.1016,'diff_pair_via_gap':.1016}],'netclass_assignments':{},'netclass_patterns':[]}}
dump(OUT/(BASE+'.kicad_pro'),project)
(OUT/(BASE+'.kicad_dru')).write_text('''(version 1)
# Candidate process rules; no waivers and no ignored severities.
(rule "Local candidate copper clearance" (constraint clearance (min 0.1016mm)))
(rule "Local candidate track minimum" (constraint track_width (min 0.1016mm)))
(rule "Via nominal diameter" (condition "A.Type == 'Via'") (constraint via_diameter (min 0.30mm) (max 0.30mm)))
(rule "Via nominal hole" (condition "A.Type == 'Via'") (constraint hole_size (min 0.15mm) (max 0.15mm)))
(rule "Selected via nominal annulus" (condition "A.Type == 'Via'") (constraint annular_width (min 0.075mm)))
(rule "Hole to other net copper" (constraint hole_clearance (min 0.20mm)))
(rule "Mechanically drilled hole separation" (constraint hole_to_hole (min 0.20mm)))
# Solder-mask minimum web 0.10 mm is stored in board setup. Individual NSMD
# land apertures are 0.40 mm. In-footprint mask bridges are not allowed.
''')

mapping=[]
for b in balls:
    a=assigned[b['ball']]
    mapping.append({'reference':'U3','ball':b['ball'],'function':a['function'],'category':b['category'],
        'native_net':native_by_ball[b['ball']],'master_assignment_net':a['net'],'independent_open_land':not bool(a['net']),
        'pin_type':xml_pins.get(b['ball'],{}).get('type','no_connect'),
        'local_x_mm':float(b['x_mm']),'local_y_mm':float(b['y_mm']),
        'source_status':a['status']})
dump(ENG/'native-net-mapping.json',mapping)
with (ENG/'native-net-mapping.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=mapping[0]);w.writeheader();w.writerows(mapping)
dump(ENG/'source-manifest.json',{'inputs':{key:{'path':str(p.relative_to(ROOT)),'sha256':hashes[key]} for key,p in INPUTS.items()},'kicad_version':k.GetBuildVersion(),'exact_part':'MTFC16GAPALBH-AAT','documentation':'https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html','restricted_source':'Micron CSN-33 not accessed or retried'})
dump(ENG/'declared-rules.json',{
    'scope':'LOCAL_ANALYSIS_WINDOW_ONLY_NOT_MANUFACTURING_RELEASE',
    'board_window_mm':[20,20],'origin_translation_mm':[100,100],'copper_layers':8,'reference_thickness_mm':1.2,
    'dielectric_stack':'Not defined or qualified; no fabricated dielectric schedule',
    'land':{'copper_diameter_mm':.30,'mask_aperture_diameter_mm':.40,'paste_aperture_diameter_mm':.30,'construction':'engineering NSMD candidate, unqualified','stencil_assumption_mm':.10},
    'rules':rules,'solder_mask_min_width_mm':.10,'allow_soldermask_bridges_in_footprints':False,
    'via_process':'Filled, planarized, copper-capped VIPPO required. Tenting flags only omit extra via mask apertures; they do not qualify or replace this process.',
    'source_absolute_nominal_via_ring_implication_mm':.05,'selected_preferred_nominal_via_ring_mm':.075,
    'ring_caveat':'Via-specific published 0.15/0.25 minimum implies 0.05 nominal ring; selected 0.30/0.15 uses preferred +0.15 diameter and explicit 0.075 minimum. Generic component PTH rings are a separate rule class.',
    'physical_drill_registration_qualification':'Open; nominal CAD diameters do not prove finished bore, tool, registration, plating, etch or breakout acceptance.',
    'copper_layer_map':{'L1':'F.Cu','L2':'In1.Cu','L3':'In2.Cu','L4':'In3.Cu','L5':'In4.Cu','L6':'In5.Cu','L7':'In6.Cu','L8':'B.Cu'},
    'no_use_counts':{'NC':109,'RFU':4,'VSF':7,'DS_unused':1},'absent_grid_sites_without_lands':43,'package_test_contacts_without_lands':56,
    'unmodeled':['SoC endpoints','supply and ground planes','VDDIM capacitor','bypass capacitors and returns','impedance','reference continuity','length/skew','complete placement and routing','castellations','fabricator stack and process qualification']})

result=subprocess.run(['kicad-cli','pcb','drc','--format','json','--all-track-errors','--severity-all','--exit-code-violations','-o',str(ENG/'native-drc.json'),str(OUT/(BASE+'.kicad_pcb'))],capture_output=True,text=True)
(ENG/'native-drc.log').write_text(result.stdout+result.stderr)
dump(ENG/'native-drc-command.json',{'argv':result.args,'exit_code':result.returncode,'environment':{name:os.environ[name] for name in ['XDG_DATA_HOME','XDG_CONFIG_HOME','XDG_CACHE_HOME']},'schematic_parity':'Not run: the standalone local window intentionally omits all other schematic components; mapping checked pin-by-pin against current XML instead.'})
if result.returncode not in [0,5]:
    raise RuntimeError(result.stdout+result.stderr)
for title,layers in [('native-copper-overview','F.Cu,In2.Cu,Edge.Cuts,F.Fab,Dwgs.User'),('native-top-mask','F.Mask,Edge.Cuts,F.Fab,Dwgs.User'),('native-L1','F.Cu,Edge.Cuts,F.Fab,Dwgs.User'),('native-L3','In2.Cu,Edge.Cuts,F.Fab,Dwgs.User')]:
    r=subprocess.run(['kicad-cli','pcb','export','svg','--layers',layers,'--page-size-mode','2','--exclude-drawing-sheet','--mode-single','-o',str(OUT/'preview'/(title+'.svg')),str(OUT/(BASE+'.kicad_pcb'))],capture_output=True,text=True)
    if r.returncode: raise RuntimeError(r.stdout+r.stderr)
    r=subprocess.run(['inkscape',str(OUT/'preview'/(title+'.svg')),'--export-type=png',
        '--export-filename='+str(OUT/'preview'/(title+'.png')),'--export-width=1800',
        '--export-background=#101828','--export-background-opacity=1.0'],capture_output=True,text=True)
    if r.returncode: raise RuntimeError(r.stdout+r.stderr)
print(json.dumps({'board':str(OUT/(BASE+'.kicad_pcb')),'DRC_exit':result.returncode,'physical_pads':len(balls),'vias':len(witness['vias']),'tracks':sum(len(r['points'])-1 for r in witness['routes']),'input_hashes':hashes},indent=2))
