#!/usr/bin/env python3
"""Read restored BGA evidence; write only this audit directory."""
from pathlib import Path
import collections
import csv
import hashlib
import json
import re
import xml.etree.ElementTree as ET

import argparse
parser = argparse.ArgumentParser(); parser.add_argument("--project", type=Path, required=True); args = parser.parse_args()
ROOT = args.project.resolve()
OUT = Path(__file__).resolve().parent
inputs = {}

def read(rel):
    raw = (ROOT / rel).read_bytes()
    inputs[rel] = hashlib.sha256(raw).hexdigest()
    return raw.decode()

def js(rel):
    return json.loads(read(rel))

def rows(rel):
    return list(csv.DictReader(read(rel).splitlines()))

def sexp(rel):
    tokens = re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()]+', read(rel))
    stack, roots = [], []
    for token in tokens:
        if token == '(':
            child = []
            (stack[-1] if stack else roots).append(child)
            stack.append(child)
        elif token == ')':
            stack.pop()
        else:
            stack[-1].append(json.loads(token) if token.startswith('"') else token)
    assert not stack and len(roots) == 1
    return roots[0]

def kids(obj, key):
    return [x for x in obj if isinstance(x, list) and x and x[0] == key]

def one(obj, key, default=None):
    found = kids(obj, key)
    return found[0][1:] if found else default

def pins_in_symbol(symbol):
    result = {}
    for unit in kids(symbol, 'symbol'):
        for pin in kids(unit, 'pin'):
            number = one(pin, 'number')[0]
            assert number not in result
            result[number] = one(pin, 'name')[0]
    return result

xml_path = 'cad/recovery-physical-candidate/master.xml'
xml = ET.fromstring(read(xml_path))
comps = {c.get('ref'): c for c in xml.findall('./components/comp')}
libs = {c.get('part'): c for c in xml.findall('./libparts/libpart')}
symbols = {s[1]: s for s in kids(sexp('cad/recovery-physical-candidate/Integrated.kicad_sym'), 'symbol')}
nodes = collections.defaultdict(list)
for net in xml.findall('./nets/net'):
    for node in net.findall('node'):
        nodes[node.get('ref')].append((node.get('pin'), node.get('pinfunction'), net.get('name')))

kmap = rows('data/k230-source-extraction/k230-390-balls.csv')
lpmap = js('engineering/high-temp-candidates/micron-lp4-ball-comparison.json')
emmap = js('engineering/high-temp-candidates/micron-emmc-ball-comparison.json')
lpind = js('engineering/mechanical/micron-lp4-independent-grid-verification.json')
mechanical = js('engineering/mechanical/bga-coordinate-verification.json')
fwmechanical = js('engineering/mechanical/micron-fw-independent-mechanics.json')
bhmechanical = js('engineering/bga-engineering-candidates/micron-emmc-package-evidence.json')
kcoords = rows('engineering/mechanical/bga-K230-physical-centers.csv')
function_rows = rows('engineering/bga-engineering-candidates/memory-soc-functional-balls.csv')
assignments = rows('cad/recovery-physical-candidate/master-pin-assignments.csv')
source = {
    'U1': {r['soc_ball']: r['soc_signal'] for r in kmap},
    'U2': {r['ball']: r['function'] for r in lpmap['grid'] if r['physical']},
    'U3': {r['ball']: r['function'] for r in emmap['grid'] if r['physical']},
}
row_order = {
    'U1': 'A B C D E F G H J K L M N P R T U V W Y'.split(),
    'U2': 'A B C D E F G H J K L M N P R T U V W Y AA AB'.split(),
    'U3': 'A B C D E F G H J K L M N P'.split(),
}
grid = {'U1': (20, .65, .65), 'U2': (12, .8, .65), 'U3': (14, .5, .5)}
pkg = {'U1': 'K230', 'U2': 'FW200', 'U3': 'BH153'}
coords = {}
for ref in source:
    cols, px, py = grid[ref]
    coords[ref] = {}
    for ball in source[ref]:
        row, col = re.fullmatch(r'([A-Z]+)(\d+)', ball).groups()
        coords[ref][ball] = [round((int(col) - (cols+1)/2)*px, 6),
                             round((row_order[ref].index(row) - (len(row_order[ref])-1)/2)*py, 6)]

checks = []
def check(name, passed, detail=None):
    item = {'check': name, 'pass': bool(passed)}
    if detail is not None:
        item['detail'] = detail
    checks.append(item)

parts = []
for ref, src in source.items():
    comp = comps[ref]
    symbol_name = comp.find('libsource').get('part')
    xmlpins = {pin.get('num'): pin.get('name') for pin in libs[symbol_name].findall('./pins/pin')}
    native_pins = pins_in_symbol(symbols[symbol_name])
    netpins = {ball: fn for ball, fn, net in nodes[ref]}
    ass = {r['pin']: r['function'] for r in assignments if r['reference'] == ref}
    functional = {r['ball']: r for r in function_rows if r['package'] == pkg[ref]}
    check(ref+' source/XML/native-symbol/assignment exact ball-function parity', src == xmlpins == native_pins == netpins == ass)
    check(ref+' XML contains each ball once', len(nodes[ref]) == len(src))
    check(ref+' functional analysis labels and coordinates', set(functional) == set(src) and all(
        functional[b]['function'] == f and [float(functional[b]['x_mm']), float(functional[b]['y_mm'])] == coords[ref][b]
        for b, f in src.items()))
    full = {r+str(c) for r in row_order[ref] for c in range(1,grid[ref][0]+1)}
    fields = {x.get('name'): x.text or '' for x in comp.findall('./fields/field')}
    check(ref+' active footprint binding empty', not comp.findtext('footprint') and not fields.get('Footprint'))
    parts.append({'reference':ref, 'active_value':comp.findtext('value'), 'symbol':symbol_name,
                  'physical_balls':len(src), 'full_grid_sites':len(full), 'absent_sites': sorted(full-set(src)),
                  'pitch_x_y_mm': list(grid[ref][1:]), 'functional_category_count':dict(collections.Counter(x['category'] for x in functional.values())),
                  'active_footprint_binding':'EMPTY', 'identity_and_coordinates':'PASS',
                  'PCB_land_qualification':'NOT_ESTABLISHED'})
check('K230 mechanical CSV exact coordinates and labels', {x['ball']: [float(x['x_mm']),float(x['y_mm'])] for x in kcoords} == coords['U1'] and all(x['source_function_label']==source['U1'][x['ball']] for x in kcoords))
check('FW200 independent grid physical labels and coordinates', {x['ball']:x['function'] for x in lpind['grid'] if x['physical']} == source['U2'] and {x['ball']:[x['x_mm'],x['y_mm']] for x in lpind['grid'] if x['physical']} == coords['U2'])
check('K230 A1 absent', 'A1' not in source['U1'])
check('BH153 package test contacts excluded', bhmechanical['package']['auxiliary_package_test_pads']['count']==56 and len(source['U3'])==153)

footprint_paths = {
    'U1':'cad/bga-engineering-candidates/k230-ddr-constrained/K230_Engineering.pretty/K230_390_NSMD027_ENGINEERING_ONLY.kicad_mod',
    'U3':'cad/bga-engineering-candidates/bh153-sparse-trial/BH153_Engineering.pretty/MTFC16GAPALBH_AAT_BH153_NSMD030_ENGINEERING_ONLY.kicad_mod',
}
footprints = []
for ref, path in footprint_paths.items():
    fp = sexp(path)
    pads = kids(fp,'pad')
    byball = {pad[1]: pad for pad in pads}
    check(ref+' standalone footprint unique pad occupancy', len(pads)==len(source[ref]) and set(byball)==set(source[ref]))
    check(ref+' standalone footprint center coordinates', all([float(v) for v in one(pad,'at')[:2]] == coords[ref][b] for b,pad in byball.items()))
    check(ref+' standalone footprint all front SMD circles', all(pad[2:4]==['smd','circle'] and set(one(pad,'layers'))=={'F.Cu','F.Mask','F.Paste'} for pad in pads))
    expected = .27 if ref=='U1' else .30
    check(ref+' standalone footprint declared copper/mask/paste', all(
        [float(v) for v in one(pad,'size')]==[expected,expected] and
        one(pad,'solder_mask_margin')==['0.05'] and one(pad,'solder_paste_margin')==['0'] and
        one(pad,'solder_paste_margin_ratio')==['0'] for pad in pads))
    footprints.append({'reference':ref,'file':path,'pads':len(pads),'copper_mask_paste_diameter_mm':[expected,round(expected+.1,2),expected],
                       'binding_to_active_master':False, 'qualified':False,
                       'has_pad_function_metadata':any(one(pad,'pinfunction') for pad in pads),
                       'has_board_nets':any(one(pad,'net') for pad in pads),
                       'body_and_courtyard':'Engineering outlines only; not independently qualified in this recheck'})

coupons = []
for ref, path in {
    'U1':'cad/bga-engineering-candidates/k230-ddr-constrained/K230_DDR_CONSTRAINED_LOCAL_TRIAL.kicad_pcb',
    'U3':'cad/bga-engineering-candidates/bh153-sparse-trial/BH153_SPARSE_LOCAL_TRIAL.kicad_pcb'
}.items():
    board = sexp(path)
    fp = kids(board,'footprint')[0]
    pads = kids(fp,'pad')
    ballpads = {x[1]:x for x in pads}
    active = {b:(f,n) for b,f,n in nodes[ref]}
    check(ref+' coupon pad labels and nets match active master', set(ballpads)==set(active) and all(
        one(ballpads[b],'pinfunction')==[f] and one(ballpads[b],'net')[1]==n for b,(f,n) in active.items()))
    check(ref+' coupon local coordinates', all([float(v) for v in one(pad,'at')[:2]]==coords[ref][b] for b,pad in ballpads.items()))
    cu = [x[1] for x in one(board,'layers') if isinstance(x,list) and x[1].endswith('.Cu')]
    coupons.append({'reference':ref,'file':path,'physical_pads':len(pads),'vias':len(kids(board,'via')),
                    'segments':len(kids(board,'segment')),'copper_layer_count':len(cu),'copper_layers':cu,
                    'six_layer_implementation_evidence':False})

trial = js('engineering/k230-ddr-constrained/trial-groups-outer-21.json')
link = js('engineering/k230-ddr-constrained/link-trial/actual-links.json')
lpballs = [x for x in link['balls'] if x['ref']=='U2']
check('FW200 analytical two-package trial labels/local coordinates', {x['ball']:x['function'] for x in lpballs}==source['U2'] and all(x['local_xy']==coords['U2'][x['ball']] for x in lpballs))
native_bh = js('engineering/bga-native-trial/native-independent-review.json')
native_k = js('engineering/k230-ddr-constrained/native-validation.json')
check('No FW200 standalone footprint in restored tree', not any(re.search(r'FW200|MT53E256M32D2FW', f.read_text()) for f in ROOT.rglob('*.kicad_mod')))

report = {
    'audit_date_utc':'2026-10-03',
    'status':'PASS_RESTORED_IDENTITY_AND_CONDITIONAL_GEOMETRY_ONLY' if all(x['pass'] for x in checks) else 'DISCREPANCY_REQUIRES_REVIEW',
    'scope':'Read-only recheck of restored v12-r2_1 source evidence, active XML and native symbols, candidate footprint centers and nominal lands. No main CAD edits, no new vendor-document retrieval, no fabrication qualification.',
    'required_board':{'outline_mm':[38,38], 'contacts':140, 'copper_layers':6, 'assembly':'top only'},
    'coordinate_convention':'Package-centered component top view, balls down, X right and Y down; mm. A CAD bottom-placement transform must not be replaced by a second manual mirror.',
    'parts':parts,
    'footprints':footprints,
    'FW200_geometry':{'standalone_footprint_present':False,'independent_grid_and_mechanics_present':True,'analytical_two_package_trial_lands_present':200,'analytical_trial_land_diameter_mm':link['rules']['ram_top_land'],'qualified':False},
    'historic_coupons':coupons,
    'historic_results':{'K230_local_trial':trial['summary'],'BH153_native_review':native_bh['native_drc'], 'actual_link_trial_snapshot':link['summary'],
                        'interpretation':'Historical local/analytical results, not rerun routing or native DRC. Other link-search variants exist and are outside this identity audit. No historical eight-layer result proves six-layer routability.'},
    'documentation_cautions':[
        'BH153 README says its reusable .pretty footprint carries pin functions. The actual standalone footprint has numbered lands but no pinfunction or net fields; the native coupon and source maps do carry the functions. Numbering/coordinates agree.',
        'The older BGA mechanical audit covers Samsung K4F8E304HB and KLMAG1JETD. Their center grids match the selected Micron package occupancy, but Samsung body/height/ball dimensions and electrical labels are not transferable.',
        'The early Micron LPDDR comparison lists second independent grid review as pending; the later independent-grid-verification artifact is present and agrees. This closes restored-data consistency only, not substitution/assembly approval.',
        'engineering/k230-authoritative-ball-evidence.json and k230-reference-balls.csv contain a 163-pin reference subset; the full 390-ball source is data/k230-source-extraction/k230-390-balls.csv.',
        'Historical artifact manifests include previews and external vendor inputs absent from the restored tree. This audit checks the restored data directly; it does not claim all original source documents are present.'
    ],
    'release_gates':[
        'Choose and qualify exact-part PCB copper, mask, paste/stencil, via and assembly construction; package-side ball-pad notes do not define PCB lands.',
        'Build and verify an explicit six-copper-layer escape, reference-plane, DDR timing and PDN design under the 38 mm / 140-contact / top-only requirements.',
        'Finish full-board placement/routing, top-side bypass loops, impedance/SI, thermal and manufacturing checks before any release.'
    ],
    'checks':checks, 'check_count':len(checks), 'failed_checks':[x for x in checks if not x['pass']],
    'input_sha256':inputs,
    'limits':['No independent rereading of original manufacturer PDFs or screenshots in this pass.',
              'Package provenance is inherited from the cited recovered evidence and its recorded source hashes.',
              'No DRC rerun, routing search, stack/process approval, current availability check, or import into active CAD.']
}
(OUT/'bga-identity-recheck.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'checks':len(checks),'failed':report['failed_checks'],'parts':[{'ref':x['reference'],'balls':x['physical_balls']} for x in parts],'coupons':coupons},indent=2))
