#!/usr/bin/env python3
"""Independent visual transcription audit; emits no PCB copper, mask or paste.

The row strings below were transcribed from rendered Micron Figure 5, PDF p21,
not populated from the lead's PDF-coordinate extraction. Columns 6/7 and rows
L/M are explicit absent grid positions. Origin is body center, component top
view, +X right, +Y down. Source drawings remain outside the distributable tree.
"""
import collections
import csv
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import fitz

PROJECT = Path(__file__).resolve().parents[2]
OUT = PROJECT / 'engineering/mechanical'
PDF = Path('/workspace/shared/k230-memory-review/thermal-candidates/micron-lp4.pdf')
LEAD = PROJECT / 'engineering/high-temp-candidates/micron-lp4-ball-comparison.json'
SAMSUNG = PROJECT / 'engineering/memory/K4F8E304HB_grid264_physical200.csv'
MASTER = PROJECT / 'cad/integrated/master.xml'
ROWS = 'A B C D E F G H J K L M N P R T U V W Y AA AB'.split()
COLS = [1, 2, 3, 4, 5, 8, 9, 10, 11, 12]

# Five left cells, then five right cells, transcribed row by row from image.
VISUAL_ROWS = {
    'A': 'DNU DNU VSS VDD2 ZQ0 NC VDD2 VSS DNU DNU',
    'B': 'DNU DQ0_A VDDQ DQ7_A VDDQ VDDQ DQ15_A VDDQ DQ8_A DNU',
    'C': 'VSS DQ1_A DMI0_A DQ6_A VSS VSS DQ14_A DMI1_A DQ9_A VSS',
    'D': 'VDDQ VSS DQS0_t_A VSS VDDQ VDDQ VSS DQS1_t_A VSS VDDQ',
    'E': 'VSS DQ2_A DQS0_c_A DQ5_A VSS VSS DQ13_A DQS1_c_A DQ10_A VSS',
    'F': 'VDD1 DQ3_A VDDQ DQ4_A VDD2 VDD2 DQ12_A VDDQ DQ11_A VDD1',
    'G': 'VSS ODT_CA_A VSS VDD1 VSS VSS VDD1 VSS NC VSS',
    'H': 'VDD2 CA0_A NC CS0_A VDD2 VDD2 CA2_A CA3_A CA4_A VDD2',
    'J': 'VSS CA1_A VSS CKE0_A NC CK_t_A CK_c_A VSS CA5_A VSS',
    'K': 'VDD2 VSS VDD2 VSS NC NC VSS VDD2 VSS VDD2',
    'N': 'VDD2 VSS VDD2 VSS NC NC VSS VDD2 VSS VDD2',
    'P': 'VSS CA1_B VSS CKE0_B NC CK_t_B CK_c_B VSS CA5_B VSS',
    'R': 'VDD2 CA0_B NC CS0_B VDD2 VDD2 CA2_B CA3_B CA4_B VDD2',
    'T': 'VSS ODT_CA_B VSS VDD1 VSS VSS VDD1 VSS RESET_n VSS',
    'U': 'VDD1 DQ3_B VDDQ DQ4_B VDD2 VDD2 DQ12_B VDDQ DQ11_B VDD1',
    'V': 'VSS DQ2_B DQS0_c_B DQ5_B VSS VSS DQ13_B DQS1_c_B DQ10_B VSS',
    'W': 'VDDQ VSS DQS0_t_B VSS VDDQ VDDQ VSS DQS1_t_B VSS VDDQ',
    'Y': 'VSS DQ1_B DMI0_B DQ6_B VSS VSS DQ14_B DMI1_B DQ9_B VSS',
    'AA': 'DNU DQ0_B VDDQ DQ7_B VDDQ VDDQ DQ15_B VDDQ DQ8_B DNU',
    'AB': 'DNU DNU VSS VDD2 VSS VSS VDD2 VSS DNU DNU',
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def normalize(function):
    return function.upper()

checks = 0
def check(condition, detail):
    global checks
    checks += 1
    if not condition:
        raise AssertionError(detail)

lead = json.loads(LEAD.read_text())
check(sha(PDF) == lead['source_sha256'], 'Source hash matches lead source')
check(len(VISUAL_ROWS) == 20, '20 occupied rows')
grid = []
for row_index, row in enumerate(ROWS):
    functions = VISUAL_ROWS.get(row, '').split()
    check(len(functions) == (0 if row in ('L', 'M') else 10), f'{row} count')
    occupied = dict(zip(COLS, functions))
    for col in range(1, 13):
        function = occupied.get(col, 'NB')
        grid.append(dict(ball=f'{row}{col}', function=function,
                         physical=function != 'NB',
                         x_mm=round((col - 6.5) * 0.8, 3),
                         y_mm=round((row_index - 10.5) * 0.65, 3)))
by_ball = {r['ball']: r for r in grid}
check(len(by_ball) == 264, 'Unique full grid')
check(sum(r['physical'] for r in grid) == 200, '200 physical balls')
check(sum(not r['physical'] for r in grid) == 64, '64 absent sites')
check(len(lead['grid']) == 264, 'Lead full grid count')
lead_by_ball = {r['ball']: r for r in lead['grid']}
for r in grid:
    check(r['function'] == lead_by_ball[r['ball']]['function'], f"Function {r['ball']}")
    check(r['physical'] == lead_by_ball[r['ball']]['physical'], f"Physical {r['ball']}")
check((by_ball['A1']['x_mm'], by_ball['A1']['y_mm']) == (-4.4, -6.825), 'A1 top-left')
check((by_ball['AB12']['x_mm'], by_ball['AB12']['y_mm']) == (4.4, 6.825), 'AB12 lower-right')
check(by_ball['A8']['x_mm'] - by_ball['A5']['x_mm'] == 2.4, 'Central column center gap')
check(round(by_ball['N1']['y_mm'] - by_ball['K1']['y_mm'], 3) == 1.95, 'Central row center gap')
for r in grid:
    check(r['physical'] == (r['ball'].rstrip('0123456789') not in ('L','M') and
                           int(r['ball'].lstrip('ABCDEFGHIJKLMNOPQRSTUVWXYZ')) not in (6,7)),
          f"Physical-site rule {r['ball']}")

# Independent physical-site evidence from Figure 7's drawn circle paths.
# Drawing pixel coordinates identify sites only; published pitches supply mm.
# The bottom-view drawing runs columns 12 -> 1, so X is reversed here.
pdf = fitz.open(PDF)
circles = [d['rect'] for d in pdf[23].get_drawings()
           if len(d['items']) == 4 and all(i[0] == 'c' for i in d['items'])
           and 3 < d['rect'].width < 5 and 3 < d['rect'].height < 5]
check(len(circles) == 200, '200 package ball circle paths, excluding A1 body mark')
centers = [((r.x0+r.x1)/2, (r.y0+r.y1)/2) for r in circles]
xmin, xmax = min(x for x,y in centers), max(x for x,y in centers)
ymin, ymax = min(y for x,y in centers), max(y for x,y in centers)
xstep, ystep = (xmax-xmin)/11, (ymax-ymin)/21
mechanical_sites = []
for x,y in centers:
    col = 12-round((x-xmin)/xstep)
    row_index = round((y-ymin)/ystep)
    # PDF circle centers vary slightly across a nominal row; this 5%-pitch
    # classifier tolerance is not a physical position tolerance.
    check(abs((x-xmin)/xstep - (12-col)) < 0.05, 'Mechanical X grid alignment')
    check(abs((y-ymin)/ystep - row_index) < 0.05, 'Mechanical Y grid alignment')
    mechanical_sites.append(f'{ROWS[row_index]}{col}')
check(len(set(mechanical_sites)) == 200, 'Unique mechanical ball sites')
check(set(mechanical_sites) == {r['ball'] for r in grid if r['physical']},
      'Mechanical drawing circle set equals top-view function grid physical set')

samsung = {r['ball_or_grid']: r for r in csv.DictReader(SAMSUNG.open())}
changes = []
for ball, r in by_ball.items():
    s = samsung[ball]
    check(r['physical'] == (s['physical_ball'] == 'True'), f'Samsung site {ball}')
    if normalize(s['function']) != normalize(r['function']):
        changes.append(dict(ball=ball, samsung=s['function'], micron=r['function']))
expected_changes = {'A5', 'G11', 'H4', 'J4', 'K5', 'K8', 'N5', 'N8', 'P4', 'R4'}
check({c['ball'] for c in changes} == expected_changes, 'All ten meaningful name/category differences')
for c in changes:
    c['category'] = ('calibration_name_alias' if c['ball'] == 'A5' else
                     'unused_category_change' if c['samsung'] == 'DNU' else
                     'single_rank_name_alias')
    check(c['category'] != 'unused_category_change' or c['micron'] == 'NC', 'Only DNU to NC')

counts = collections.Counter(r['function'] for r in grid)
master = ET.parse(MASTER).getroot()
u2_nodes = {}
for net in master.findall('./nets/net'):
    for node in net.findall('node'):
        if node.get('ref') == 'U2':
            u2_nodes[node.get('pin')] = dict(net=net.get('name'),
                function=node.get('pinfunction'), pin_type=node.get('pintype'),
                other_nodes=[n.attrib for n in net.findall('node') if n.get('ref') != 'U2'])
focused_master = {ball:u2_nodes[ball] for ball in expected_changes}
for c in changes:
    if c['category'] == 'unused_category_change':
        check(not u2_nodes[c['ball']]['other_nodes'], f"Changed NC remains isolated {c['ball']}")
for r in grid:
    if r['physical'] and r['function'] in ('NC','DNU'):
        check(not u2_nodes[r['ball']]['other_nodes'], f"Unused physical site isolated {r['ball']}")
zq_resistor = next(c for c in master.findall('./components/comp') if c.get('ref') == 'R63')
zq_supply = next(n for n in master.findall('./nets/net')
                 if any(p.get('ref') == 'R63' and p.get('pin') == '2' for p in n.findall('node')))
check(zq_resistor.findtext('value') == '240R 1% REF', 'Current ZQ resistor value')
check(any(n.get('ref') == 'U2' and n.get('pinfunction') == 'VDDQ'
          for n in zq_supply.findall('node')), 'Current ZQ resistor feeds VDDQ rail')

out = dict(
    status='PASS_INDEPENDENT_VISUAL_BALL_GRID_REVIEW_NOT_SUBSTITUTION_APPROVAL',
    part=lead['part'], assertions_passed=checks,
    method='Manual row-by-row transcription from rendered Figure 5, independent of PDF text-coordinate extraction; Samsung p10 also visually inspected.',
    source=dict(url=lead['source_url'], local_pdf=str(PDF), sha256=sha(PDF),
                revision='Rev. F 10/2020 EN', figure=5, pdf_page=21,
                supporting_pages=[3,19,22,24]),
    checked_inputs={str(p.relative_to(PROJECT)):sha(p) for p in (LEAD,SAMSUNG,MASTER)},
    orientation='Component top view, ball down; origin at body center; +X right; +Y down. Mechanical Figure 7 ball-side view reverses columns and must not replace this logical orientation.',
    counts=dict(full_grid=264,physical=200,absent=64,nc=counts['NC'],dnu=counts['DNU']),
    absent_rule='All sites in rows L/M or columns 6/7; union = 24 + 44 - 4 = 64.',
    ball_center_geometry_mm=dict(column_pitch=0.8,row_pitch=0.65,x_span=8.8,y_span=13.65,
                                 central_column_center_gap=2.4,central_row_center_gap=1.95),
    lead_grid_mismatches=[], samsung_physical_mismatches=[],
    mechanical_drawing_crosscheck=dict(figure=7,pdf_page=24,ball_circle_paths=200,
        mismatched_physical_sites=[],
        image_grid_classifier_tolerance_pitch_fraction=0.05,
        method='Exactly 200 four-Bezier circles in the ball array; A1 body marker excluded by size. Reverse mechanical columns 12-to-1 to top-view 1-to-12. Round image centers to grid for site identification only.'),
    differences_from_samsung_ignoring_case=changes,
    lead_difference_note='The lead lists nine changes and separately normalizes ZQ_a to ZQ0. This audit records that tenth name difference explicitly; no disagreement.',
    current_master_focused_connections=focused_master,
    current_master_ZQ_resistor=dict(reference='R63',value=zq_resistor.findtext('value'),
        resistor_pin_1_net=u2_nodes['A5']['net'],resistor_pin_2_net=zq_supply.get('name'),
        same_rail_as_VDDQ=True,qualification='Connectivity and nominal value only; no PI, tolerance over temperature, or calibration firmware qualification.'),
    electrical_semantics=dict(
        topology='Figure 3: dual die, dual channel, single rank, two x16 channels for x32.',
        CS_CKE='H4=CS0_A, J4=CKE0_A, P4=CKE0_B, R4=CS0_B. Same ball positions and signal roles as Samsung single-rank CS/CKE; firmware still requires qualification.',
        ZQ0='A5, shared calibration reference in Figure 3. Table 4 requires 240 ohm +/-1% to VDDQ; do not treat suffix 0 as a second-rank signal.',
        DNU='Table 4 permits grounding or leaving floating. Current isolated treatment is retained.',
        NC='Table 4 says not internally connected. NC remains a physical ball, distinct from absent NB sites.',
        ODT='G2/T2 stay ODT_CA_A/B; pin-role equivalence alone does not qualify mode settings or termination.'),
    no_pcb_land_pattern_generated=True,
    limits=['Grid and package verification do not qualify DDR timing, training, drive strength, ODT, ZQ scheduling, refresh, power sequencing, SI/PI, solder joints or thermal behavior.',
            'No PCB copper/mask/paste or master CAD edits are performed.'],
    grid=grid)
(OUT/'micron-lp4-independent-grid-verification.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ('status','assertions_passed','counts','differences_from_samsung_ignoring_case')},indent=2))
