#!/usr/bin/env python3
"""Independent native-data comparison against frozen coordinates and live XML."""
from pathlib import Path
import collections,csv,hashlib,json,math,xml.etree.ElementTree as ET
import pcbnew

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
CAD=ROOT/'cad/bga-engineering-candidates/bh153-sparse-trial'
BOARD=CAD/'BH153_SPARSE_LOCAL_TRIAL.kicad_pcb'
PRO=CAD/'BH153_SPARSE_LOCAL_TRIAL.kicad_pro'
DRU=CAD/'BH153_SPARSE_LOCAL_TRIAL.kicad_dru'
WITNESS=ROOT/'engineering/bga-engineering-candidates/memory-soc-functional-escape-analysis-cu030-via030-hole015.json'
GRID=ROOT/'engineering/high-temp-candidates/micron-emmc-ball-comparison.json'
XML=ROOT/'cad/high-temp-candidate/master.xml'
PINS=ROOT/'cad/high-temp-candidate/master-pin-assignments.csv'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mm(x):return pcbnew.ToMM(x)
def pair(v):return [mm(v.x),mm(v.y)]
def quant(v):return round(v,6)

def main():
    checks=[]
    def check(name,value):
        checks.append({'check':name,'pass':bool(value)})
        assert value,name
    witness=json.loads(WITNESS.read_text())['eMMC_local_witness']
    grid=[p for p in json.loads(GRID.read_text())['grid'] if p['physical']]
    expected={p['ball']:p for p in grid}
    pinrows={p['pin']:p for p in csv.DictReader(PINS.open()) if p['reference']=='U3'}
    xmlnets={}
    for n in ET.parse(XML).getroot().findall('./nets/net'):
        for q in n.findall('node'):
            if q.attrib['ref']=='U3':xmlnets[q.attrib['pin']]=n.attrib['name']
    b=pcbnew.LoadBoard(str(BOARD))
    footprints=list(b.GetFootprints())
    check('Exactly one top-side component; no invented connector or port components',len(footprints)==1 and footprints[0].GetLayer()==pcbnew.F_Cu)
    f=footprints[0];origin=pair(f.GetPosition())
    check('Native component reference is actual U3',f.GetReference()=='U3')
    pads=list(f.Pads());by={p.GetNumber():p for p in pads}
    check('153 distinct native physical pad names exactly match Micron occupied grid',len(pads)==153 and set(by)==set(expected))
    rownames='A B C D E F G H J K L M N P'.split()
    import re
    for name,p in by.items():
        row,col=re.fullmatch(r'([A-Z]+)([0-9]+)',name).groups()
        xy=[(int(col)-7.5)*.5,(rownames.index(row)-6.5)*.5]
        got=[a-z for a,z in zip(pair(p.GetPosition()),origin)]
        check(f'{name}: exact component-top coordinates',all(abs(a-c)<1e-7 for a,c in zip(got,xy)))
        check(f'{name}: NSMD circular 0.30 mm copper',p.GetShape()==pcbnew.PAD_SHAPE_CIRCLE and all(abs(mm(v)-.3)<1e-9 for v in [p.GetSize().x,p.GetSize().y]))
        check(f'{name}: SMD front copper/mask/paste only',p.GetAttribute()==pcbnew.PAD_ATTRIB_SMD and all(p.IsOnLayer(x) for x in [pcbnew.F_Cu,pcbnew.F_Mask,pcbnew.F_Paste]) and not p.IsOnLayer(pcbnew.B_Cu))
        check(f'{name}: 0.40 mm mask opening and 0.30 mm paste aperture',abs(mm(p.GetLocalSolderMaskMargin())-.05)<1e-9 and p.GetLocalSolderPasteMargin()==0 and abs(p.GetLocalSolderPasteMarginRatio())<1e-12)
        check(f'{name}: exact current XML net identity',p.GetNetname()==xmlnets[name])
        check(f'{name}: exact physical pin function retained',p.GetPinFunction()==expected[name]['function'])
    unused=[p for p in grid if p['function']=='NC' or p['function']=='RFU' or p['function'].startswith('VSF')]
    kinds=collections.Counter('VSF' if p['function'].startswith('VSF') else p['function'] for p in unused)
    check('NC109 / RFU4 / VSF7 remain distinct physical functions',dict(kinds)=={'NC':109,'RFU':4,'VSF':7})
    check('120 unused lands retain unique isolated XML net identities',len({by[p['ball']].GetNetname() for p in unused})==120)
    check('DS remains a physical named unused strobe net',by['H5'].GetPinFunction()=='DS' and by['H5'].GetNetname()=='EMMC_DS_UNUSED')
    tracks=[t for t in b.GetTracks() if not isinstance(t,pcbnew.PCB_VIA)]
    vias=[t for t in b.GetTracks() if isinstance(t,pcbnew.PCB_VIA)]
    check('Exactly29 through vias, including all20 modeled PG connections',len(vias)==29 and witness['power_ground_via_count']==20)
    expected_vias=collections.Counter((quant(v['xy'][0]),quant(v['xy'][1]),xmlnets[v['ball']]) for v in witness['vias'])
    got_vias=collections.Counter((quant(pair(v.GetPosition())[0]-origin[0]),quant(pair(v.GetPosition())[1]-origin[1]),v.GetNetname()) for v in vias)
    check('All native via centers and real nets match frozen witness',got_vias==expected_vias)
    copper_layers=[pcbnew.F_Cu,pcbnew.In1_Cu,pcbnew.In2_Cu,pcbnew.In3_Cu,pcbnew.In4_Cu,pcbnew.In5_Cu,pcbnew.In6_Cu,pcbnew.B_Cu]
    for i,v in enumerate(vias):
        check(f'Via{i}: 0.30/0.15 mm through geometry on every copper layer',all(abs(mm(v.GetWidth(layer))-.3)<1e-9 for layer in copper_layers) and abs(mm(v.GetDrillValue())-.15)<1e-9 and v.GetViaType()==pcbnew.VIATYPE_THROUGH)
        check(f'Via{i}: annuli retained in this specific native trial',not v.GetRemoveUnconnected())
    def segment(a,c,layer,net,width):
        ends=sorted([tuple(map(quant,a)),tuple(map(quant,c))])
        return tuple(ends)+(layer,net,quant(width))
    expected_tracks=[]
    for r in witness['routes']:
        for a,c in zip(r['points'],r['points'][1:]):expected_tracks.append(segment(a,c,{'L1':'F.Cu','L3':'In2.Cu'}[r['layer']],xmlnets[r['ball']],r['width_mm']))
    native_tracks=[]
    for t in tracks:
        a=[x-y for x,y in zip(pair(t.GetStart()),origin)];c=[x-y for x,y in zip(pair(t.GetEnd()),origin)]
        native_tracks.append(segment(a,c,b.GetLayerName(t.GetLayer()),t.GetNetname(),mm(t.GetWidth())))
    check('All16 native route segments match frozen points, nets, layers and widths',len(tracks)==16 and collections.Counter(expected_tracks)==collections.Counter(native_tracks))
    check('Eight copper layers; proposed1.2mm reference thickness',b.GetCopperLayerCount()==8 and abs(mm(b.GetDesignSettings().GetBoardThickness())-1.2)<1e-9)
    check('No invented reference or power-plane fills',len(list(b.Zones()))==0)
    project=json.loads(PRO.read_text())['board']['design_settings']
    for key,val in {'min_clearance':.1016,'min_track_width':.1016,'min_via_diameter':.3,'min_through_hole_diameter':.15,'min_via_annular_width':.075,'min_hole_clearance':.2,'min_hole_to_hole':.2}.items():
        check('Project rule '+key,abs(project['rules'][key]-val)<1e-12)
    check('No DRC exclusions or ignored severities',not project.get('drc_exclusions') and all(x!='ignore' for x in project['rule_severities'].values()))
    board_text=BOARD.read_text()
    check('Native minimum mask web remains 0.10 mm','(solder_mask_min_width 0.1)' in board_text)
    check('Native footprint mask-bridge allowance is disabled','(allow_soldermask_bridges_in_footprints no)' in board_text)
    rules=DRU.read_text()
    for marker in ['hole_clearance (min 0.20mm)','hole_to_hole (min 0.20mm)','annular_width (min 0.075mm)','clearance (min 0.1016mm)']:
        check('Active custom-rule definition '+marker,marker in rules)
    raw=json.loads((OUT/'native-drc.json').read_text())
    types=collections.Counter(x['type'] for x in raw['violations'])
    check('Native DRC reports only expected dangling geometry warnings',dict(types)=={'via_dangling':20,'track_dangling':12})
    check('Native unfinished-power connectivity is retained as17 errors',len(raw['unconnected_items'])==17 and all(x['severity']=='error' for x in raw['unconnected_items']))
    check('No source schematic-parity claim for a standalone fragment',raw['schematic_parity']==[])
    controls=json.loads((OUT/'rule-control-results.json').read_text())
    expected_controls={'annulus':('annular_width',29),'hole_to_copper':('hole_clearance',199),'hole_to_hole':('hole_to_hole',21),'mask_web':('solder_mask_bridge',200)}
    check('Candidate byte identity preserved by positive controls',controls['candidate_files_unchanged'] and controls['candidate_sha256'][BOARD.name]==sha(BOARD))
    for c in controls['controls']:
        typ,count=expected_controls[c['control']]
        data=json.loads((ROOT/c['report']).read_text())
        check('Independent raw positive-control count '+c['control'],sum(x['type']==typ for x in data['violations'])==count and c['detected'])
    inputs=[BOARD,PRO,DRU,WITNESS,GRID,XML,PINS,OUT/'native-drc.json',OUT/'rule-control-results.json']
    result={'status':'PASS_NATIVE_GEOMETRY_MAPPING_WITH_17_OPEN_POWER_CONNECTIONS_AND_32_DANGLING_WARNINGS',
        'scope':'Independent native parser comparison. No manufacturing, full-core routing, PDN, SI or assembly qualification.',
        'checks':checks,'total_checks':len(checks),'failed':[],
        'native_counts':{'physical_SMD_lands':len(pads),'through_vias':len(vias),'route_segments':len(tracks),'components':len(footprints),'NC':109,'RFU':4,'VSF':7,'unused_DS':1},
        'native_drc':{'geometry_rule_violations':0,'unconnected_errors':17,'warning_types':dict(types),'overall_DRC_clean':False,
                      'interpretation':'Power/ground plane networks and the 12 local host/VDDIM exits are deliberately unfinished. Native DRC adds these connectivity findings beyond the analytic local collision proof; none are suppressed.'},
        'sources_sha256':{str(p.relative_to(ROOT)):sha(p) for p in inputs},
        'annotation_note':'The project has small fabrication/drawing-layer analysis labels; there is no printed front/back silkscreen artwork. Annotation sizing is not a manufacturing legend specification.'}
    (OUT/'native-independent-review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'checks':len(checks),'native_counts':result['native_counts'],'native_drc':result['native_drc']},indent=2))

if __name__=='__main__':main()
