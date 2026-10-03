#!/usr/bin/env python3
"""Conditional geometry, not CAD/routing/assembly approval. No frozen files written.

Reproduce with: python engineering/bga-engineering-candidates/evaluate_memory_escape.py
Only the sibling JSON, CSV and SVG files are generated.
"""
from pathlib import Path
from collections import Counter, defaultdict
import argparse, csv, hashlib, json, math, re

BASE = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
THERMAL = BASE.parent / 'k230-memory-review/thermal-candidates'
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--land',type=float,default=.35)
ap.add_argument('--via',type=float,default=.35)
ap.add_argument('--hole',type=float,default=.15)
ap.add_argument('--width',type=float,default=.1016)
ap.add_argument('--clearance',type=float,default=.1016)
ap.add_argument('--suffix',default='')
args=ap.parse_args()
LAND=args.land
W=args.width
C=args.clearance
VIA=args.via
HOLE=args.hole
HC = 0.1524
# Arithmetic equality only: 10^-12 mm is not a fabrication-rule tolerance.
ARITHMETIC_EPS_MM = 1e-12

def at_least(actual, required=0.0):
    return actual >= required - ARITHMETIC_EPS_MM

def read_csv(p):
    return list(csv.DictReader(p.open()))

def num(v):
    return round(v, 12)

inputs = [BASE/'engineering/mechanical/micron-lp4-independent-grid-verification.json',
          BASE/'engineering/mechanical/micron-fw-independent-mechanics.json',
          BASE/'engineering/mechanical/bga-coordinate-verification.json',
          BASE/'engineering/mechanical/core-stackup-process-proposal.json',
          BASE/'engineering/mechanical/bga-K230-physical-centers.csv',
          BASE/'engineering/pin-types/k230-all390-type-audit.csv',
          BASE/'cad/high-temp-candidate/master-pin-assignments.csv',
          BASE/'engineering/decoupling-allocation.csv',
          THERMAL/'MTFC16GAPALBH-AAT_grid196_physical153.csv']
hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
ledger_path=BASE/'engineering/routing/high-temp-ddr-route-contract.csv'
ledger=read_csv(ledger_path)
hashes[str(ledger_path)]=hashlib.sha256(ledger_path.read_bytes()).hexdigest()
live_ddr_balls={r['dram_ball'] for r in ledger}
lp = json.loads(inputs[0].read_text())['grid']
lp = [dict(p, category=('unused' if p['function'] in ['NB','NC','DNU'] else
       'ground' if p['function']=='VSS' else 'power' if p['function'].startswith('VDD') else 'non_supply_functional')) for p in lp]
em = read_csv(inputs[-1])
erows = 'A B C D E F G H J K L M N P'.split()
for p in em:
    row, col = re.fullmatch(r'([A-Z]+)([0-9]+)', p['ball']).groups()
    p.update(x_mm=(int(col)-7.5)*.5, y_mm=(erows.index(row)-6.5)*.5, physical=p['physical']=='True')
km = {p['pin']:p for p in read_csv(inputs[6]) if p['reference']=='U1'}
kt = {p['ball']:p for p in read_csv(inputs[5])}
k = []
krows = 'A B C D E F G H J K L M N P R T U V W Y'.split()
for p in read_csv(inputs[4]):
    f = km[p['ball']]
    row,col = re.fullmatch(r'([A-Z]+)([0-9]+)',p['ball']).groups()
    category = 'unused' if not f['net'] else 'ground' if f['net']=='GND' else 'power' if kt[p['ball']]['proposed_compact_type']=='power_in' else 'signal'
    k.append(dict(ball=p['ball'], function=f['function'], net=f['net'], category=category,
        physical=True, x_mm=float(p['x_mm']), y_mm=float(p['y_mm']),
        ring=min(krows.index(row),19-krows.index(row),int(col)-1,20-int(col))))

def dogbone(px,py,land,via,hole=HOLE,hc=HC):
    q=math.hypot(px,py)/2
    return dict(nearest_center_mm=num(q), land_mm=land, via_pad_mm=via,
        via_land_copper_gap_mm=num(q-(land+via)/2),
        copper_gap_margin_mm=num(q-(land+via)/2-C),
        drill_to_land_gap_mm=num(q-hole/2-land/2),
        hole_gap_margin_mm=num(q-hole/2-land/2-hc),
        passes_nominal_copper_and_hole_clearance=at_least(q-(land+via)/2,C) and at_least(q-hole/2-land/2,hc))

packages = {}
for name, balls, px, py, lands in [('FW200',lp,.8,.65,[.30,.325,.35,.375,.40,.425,.45]),
       ('BH153',em,.5,.5,[.20,.25,.275,.30,.325,.35,.40]),
       ('K230',k,.65,.65,[.275,.30,.325,.35,.375,.40])]:
    phys = [p for p in balls if p['physical']]
    packages[name] = dict(counts=dict(Counter(p['category'] for p in phys)),
        physical_count=len(phys), pitch_x_mm=px,pitch_y_mm=py,
        trials=[dict(land_mm=d, max_trace_between_lands_x_mm=num(px-d-2*C),
                     max_trace_between_lands_y_mm=num(py-d-2*C),
                     one_selected_trace_x=at_least(px-d-2*C,W),one_selected_trace_y=at_least(py-d-2*C,W),
                     dogbone=dogbone(px,py,d,VIA)) for d in lands],
        cell_center_max_land_for_selected_via_mm=num(math.hypot(px,py)-VIA-2*C))

via_corridors = []
for pitch in [.5,.65,.8]:
    for hole in [.15,.2]:
        for hc in [.1524,.1778,.2,.2286]:
            copper_gap=pitch-VIA-2*C
            hole_gap=pitch-hole-2*hc
            anti=max(VIA+2*C,hole+2*hc)
            via_corridors.append(dict(pitch_mm=pitch, drill_assumption_mm=hole,
                hole_clearance_mm=hc, retained_pad_max_trace_mm=num(copper_gap),
                nonfunctional_pad_removed_max_trace_mm=num(hole_gap),
                combined_retained_pad_max_trace_mm=num(min(copper_gap,hole_gap)),
                retained_pad_passes_selected_width=at_least(min(copper_gap,hole_gap),W),
                removed_pad_passes_selected_width=at_least(hole_gap,W),
                retained_pad_min_plane_antipad_diameter_mm=num(anti),
                retained_pad_plane_web_mm=num(pitch-anti),
                removed_pad_hole_antipad_diameter_mm=num(hole+2*hc),
                removed_pad_plane_web_mm=num(hole_gap)))

# Each connected SoC signal counted from the frozen candidate net assignment.
ksignals=[p for p in k if p['category']=='signal']
ddr=[p for p in ksignals if p['net'].startswith('DDR_') and p['net'] not in ['DDR_VREF','DDR_ZN']]
kreport=dict(connected_signal_count=len(ksignals), signal_ring_histogram=dict(sorted(Counter(p['ring'] for p in ksignals).items())),
       DDR65_count=len(ddr),DDR_ring_histogram=dict(sorted(Counter(p['ring'] for p in ddr).items())),
       deepest_signal_balls=[p for p in ksignals if p['ring']==max(q['ring'] for q in ksignals)],
       counts_by_ring={r:dict(Counter(p['category'] for p in k if p['ring']==r)) for r in range(10)},
       DDR_sector_column_min=min(int(re.search(r'\d+',p['ball']).group()) for p in ddr))

# A strictly local constructive eMMC escape witness, with deliberately explicit
# unqualified 0.35-mm round lands. It is not an exact-part land recommendation.
eb={p['ball']:p for p in em}
def xy(ball): return (eb[ball]['x_mm'],eb[ball]['y_mm'])
def via(ball, at=None): return dict(ball=ball, net=eb[ball]['function'], xy=at or xy(ball))
vias=[via(p['ball']) for p in em if p['category'] in ['ground','power','internal_regulator'] and p['ball']!='A6']
vias += [via(b) for b in ['B2','B3','B4','B5','B6','K5']]
vias += [via('M5',xy('L5')),via('M6',xy('L6')),via('A6',(0.,-4.5))]
routes=[]
def route(ball,layer,points):
    routes.append(dict(ball=ball,net=eb[ball]['function'],layer=layer,points=points,width_mm=W))
for b in ['A3','A4','A5']: route(b,'L1',[xy(b),(xy(b)[0],-7.)])
for b in ['B2','B3','B4','B5','B6']: route(b,'L3',[xy(b),(xy(b)[0],-7.)])
for b,nb,dest in [('M5','L5',(-6.25,xy('L5')[1])),('M6','L6',(6.25,xy('L6')[1]))]:
    route(b,'L1',[xy(b),xy(nb)])
    route(b,'L3',[xy(nb),dest])
route('K5','L3',[xy('K5'),(-6.25,xy('K5')[1])])
route('C2','L3',[xy('C2'),(-6.25,xy('C2')[1])])
route('A6','L1',[xy('A6'),(-.75,-3.75),(0.,-4.5)])

def dist_point_seg(p,a,b):
    vx,vy=b[0]-a[0],b[1]-a[1]
    den=vx*vx+vy*vy
    t=max(0,min(1,((p[0]-a[0])*vx+(p[1]-a[1])*vy)/den)) if den else 0
    return math.hypot(p[0]-a[0]-t*vx,p[1]-a[1]-t*vy)

def orientation(a,b,c): return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def dist_seg_seg(a,b,c,d):
    # Closed segment intersections including the collinear case.
    if orientation(a,b,c)*orientation(a,b,d)<=0 and orientation(c,d,a)*orientation(c,d,b)<=0:
        if max(min(a[0],b[0]),min(c[0],d[0]))<=min(max(a[0],b[0]),max(c[0],d[0])) and max(min(a[1],b[1]),min(c[1],d[1]))<=min(max(a[1],b[1]),max(c[1],d[1])):
            return 0.
    return min(dist_point_seg(p,x,y) for p,x,y in [(a,c,d),(b,c,d),(c,a,b),(d,a,b)])

checks=[]
for r in routes:
    obstacles=[]
    if r['layer']=='L1':
        obstacles += [(p['ball'],p['function'],xy(p['ball']),LAND/2+C+W/2,'physical_land') for p in em if p['physical']]
    obstacles += [(p['ball'],p['net'],p['xy'],max(VIA/2+C,HOLE/2+HC)+W/2,'PTH') for p in vias]
    for ball,net,loc,radius,kind in obstacles:
        if ball==r['ball']: continue
        minimum=min(dist_point_seg(loc,a,b) for a,b in zip(r['points'],r['points'][1:]))-radius
        checks.append(dict(route_ball=r['ball'],layer=r['layer'],other_ball=ball,kind=kind,margin_mm=num(minimum)))
for i,r in enumerate(routes):
    for s in routes[i+1:]:
        if r['layer']!=s['layer'] or r['ball']==s['ball']:continue
        margin=min(dist_seg_seg(a,b,c,d) for a,b in zip(r['points'],r['points'][1:]) for c,d in zip(s['points'],s['points'][1:]))-W-C
        checks.append(dict(route_ball=r['ball'],other_ball=s['ball'],layer=r['layer'],kind='trace_to_trace',margin_mm=num(margin)))
for i,v in enumerate(vias):
    for u in vias[i+1:]:
        if v['net']==u['net']:continue
        spacing=math.dist(v['xy'],u['xy'])
        checks.append(dict(route_ball=v['ball'],other_ball=u['ball'],layer='all',kind='via_pad_to_via_pad',margin_mm=num(spacing-VIA-C)))
    for p in em:
        if not p['physical'] or p['ball']==v['ball']:continue
        if p['function']==v['net']:continue
        checks.append(dict(route_ball=v['ball'],other_ball=p['ball'],layer='L1',kind='via_to_physical_land',margin_mm=num(math.dist(v['xy'],xy(p['ball']))-(VIA+LAND)/2-C)))
        checks.append(dict(route_ball=v['ball'],other_ball=p['ball'],layer='L1',kind='drill_to_physical_land',margin_mm=num(math.dist(v['xy'],xy(p['ball']))-(HOLE+LAND)/2-HC)))
physical=[p for p in em if p['physical']]
for i,p in enumerate(physical):
    for q in physical[i+1:]:
        # Retain every physical NC/RFU/VSF copper feature independently.
        checks.append(dict(route_ball=p['ball'],other_ball=q['ball'],layer='L1',kind='physical_land_to_physical_land',margin_mm=num(math.dist(xy(p['ball']),xy(q['ball']))-LAND-C)))
bad=[q for q in checks if not at_least(q['margin_mm'])]
witness=dict(status='PASS_CONDITIONAL_LOCAL_GEOMETRY_ONLY' if not bad else 'FAILED',
    note='No PDN, impedance, return-via, length match, solder mask, placement or final net routing approval. All physical lands retained, all 20 power/ground balls have modeled vias; DS not used in HS200. VDDIM escape included but its top-side capacitor and return via not placed.',
    trial_round_BGA_land_mm=LAND, via_pad_mm=VIA, assumed_drill_mm=HOLE,hole_to_copper_mm=HC,
    nominal_annular_ring_mm=num((VIA-HOLE)/2),
    annular_ring_margin_vs_published_3mil_mm=num((VIA-HOLE)/2-.0762),
    mechanical_hole_margin_vs_published_0p15_mm=num(HOLE-.15),
    via_pad_fits_BGA_copper=at_least(LAND,VIA),
    process_warning='Geometry PASS does not override annular-ring or drill minima, or qualify the exact-part copper/mask construction.',
    nominal_local_signal_egress_layers=['L1','L3'],required_host_signals=11,
    signal_balls_L1=['A3','A4','A5'],signal_balls_L3=['B2','B3','B4','B5','B6','K5','M5','M6'],
    power_ground_via_count=sum(p['category'] in ['power','ground'] for p in em),
    modeled_via_count=len(vias),minimum_checked_margin_mm=min(q['margin_mm'] for q in checks),checks=len(checks),
    failures=bad,vias=vias,routes=routes)

# Bounded K230 local witness; all OTHER vias are explicitly unplaced/reserved.
# Always use the unchanged 4/4-mil, 0.35/0.15-mm rules, independent of eMMC args.
kb={p['ball']:p for p in k}
kvias=[dict(ball='J6',xy=(-3.25,-1.30)),dict(ball='L6',xy=(-3.25,.65))]
kroutes=[]
for v in kvias:
    p=kb[v['ball']]
    kroutes += [dict(ball=v['ball'],layer='L1',points=[(p['x_mm'],p['y_mm']),v['xy']]),
                dict(ball=v['ball'],layer='L3',points=[v['xy'],(-7.2,v['xy'][1])])]
kwitness=[]
for kd in [.25,.27]:
    margins=[]
    for r in kroutes:
        obstacles=[]
        if r['layer']=='L1':obstacles += [(p['ball'],(p['x_mm'],p['y_mm']),kd/2+.1016+.1016/2) for p in k]
        obstacles += [(v['ball'],v['xy'],max(.35/2+.1016,.15/2+.1524)+.1016/2) for v in kvias]
        for ball,loc,rad in obstacles:
            if ball!=r['ball']:
                margins.append(dict(ball=r['ball'],other=ball,layer=r['layer'],kind='trace_to_obstacle',margin_mm=num(min(dist_point_seg(loc,a,b) for a,b in zip(r['points'],r['points'][1:]))-rad)))
    for v in kvias:
        for p in k:
            if p['ball']==v['ball']:continue
            distance=math.dist(v['xy'],(p['x_mm'],p['y_mm']))
            margins.append(dict(ball=v['ball'],other=p['ball'],layer='L1',kind='via_pad_to_land',margin_mm=num(distance-(.35+kd)/2-.1016)))
            margins.append(dict(ball=v['ball'],other=p['ball'],layer='L1',kind='drill_to_land',margin_mm=num(distance-(.15+kd)/2-.1524)))
    for i,r in enumerate(kroutes):
        for s in kroutes[i+1:]:
            if r['layer']==s['layer'] and r['ball']!=s['ball']:
                margins.append(dict(ball=r['ball'],other=s['ball'],layer=r['layer'],kind='trace_to_trace',margin_mm=num(min(dist_seg_seg(a,b,c,d) for a,b in zip(r['points'],r['points'][1:]) for c,d in zip(s['points'],s['points'][1:]))-.2032)))
    margins.append(dict(ball='J6',other='L6',layer='all',kind='via_pad_to_via_pad',margin_mm=num(math.dist(kvias[0]['xy'],kvias[1]['xy'])-.35-.1016)))
    failures=[m for m in margins if not at_least(m['margin_mm'])]
    assert not failures,failures
    kwitness.append(dict(status='PASS_TWO_SIGNAL_LOCAL_GEOMETRY_ONLY',BGA_copper_mm=kd,
        via_copper_mm=.35,assumed_drill_mm=.15,trace_width_mm=.1016,copper_clearance_mm=.1016,hole_clearance_mm=.1524,
        all390_physical_top_lands_retained=True,checks=len(margins),minimum_margin_mm=min(m['margin_mm'] for m in margins),
        controlling_checks=sorted(margins,key=lambda m:m['margin_mm'])[:8],failures=failures,
        source_ball_centers={b:(kb[b]['x_mm'],kb[b]['y_mm']) for b in ['J6','L6']},vias=kvias,routes=kroutes,
        scope_limit='Only two staggered local dogbones and their L3 egress are modeled. Every other required signal/power/ground via is unrouted/reserved and may obstruct these exits. No full K230 escape, PDN, plane continuity, timing or assembly approval.'))

decaps=read_csv(inputs[7])
report=dict(status='CONDITIONAL_ANALYTIC_ESCAPE_STUDY_NOT_CAD_RELEASE',source_sha256=hashes,
    units='mm',rule_basis={'trace_width':W,'copper_clearance':C,'via_pad':VIA,'drill_assumption':HOLE,'hole_clearance':HC},
    arithmetic_comparison={'equality_epsilon_mm':ARITHMETIC_EPS_MM,'purpose':'Floating-point representation error only; not a fabrication-rule relaxation. Zero nominal clearance margin remains zero process tolerance.'},
    packages=packages,via_corridor_sensitivity=via_corridors,K230_functional=kreport,K230_deepest_local_witness=kwitness,
    LPDDR_non_supply_functional_quadrants={name: [p['ball'] for p in lp if p['category']=='non_supply_functional' and ((p['x_mm']<0)==left) and ((p['y_mm']<0)==upper)] for name,left,upper in [('NW',True,True),('NE',False,True),('SW',True,False),('SE',False,False)]},
    LPDDR_live_SoC_joins_by_quadrant={name: [p['ball'] for p in lp if p['ball'] in live_ddr_balls and ((p['x_mm']<0)==left) and ((p['y_mm']<0)==upper)] for name,left,upper in [('NW',True,True),('NE',False,True),('SW',True,False),('SE',False,False)]},
    DDR_route_contract_gate=dict(live_joins=len(ledger),groups=dict(Counter(r['sink_group'] for r in ledger)),
        local_functional_balls_excluded_from_SoC_egress=['A5/ZQ0','G2/ODT_CA_A','T2/ODT_CA_B'],
        timing_status='Local geometric fanout and PCB equal length do not establish flight-time matching; use official SoC package lengths, missing Micron package delay model, actual manufactured dielectric/via delays, SI and training.'),
    eMMC_local_witness=witness,
    decoupling={'count':len(decaps),'by_rail':dict(Counter(p['net'] for p in decaps)),
      'local_geometry_unassigned':True,'top_only':True,
      'eMMC_VDDIM_C2_nominal_minimum_distance_to_body_edge_mm':3.0},
    invariants={'frozen_files_modified':False,'CAD_modified':False,'CSN33_not_accessed_or_retried':True,
                'source_0p40_FW_and_0p30_BH_package_SMD_notes_not_used_as_PCB_recommendations':True})
report['top_side_decoupler_distance_bounds']={}
for name,bs,hx,hy in [('K230',k,6.55,6.55),('FW200',lp,5.05,7.3),('BH153',em,5.8,6.55)]:
    d=[dict(ball=p['ball'],function=p['function'],distance_to_nearest_max_body_edge_mm=num(min(hx-abs(p['x_mm']),hy-abs(p['y_mm'])))) for p in bs if p['category']=='power']
    report['top_side_decoupler_distance_bounds'][name]=dict(
        interpretation='Geometric lower bound from a power-ball center to outside the maximum body projection. Add capacitor land/courtyard, manufacturing clearance, and actual route/via detours; not an electrical path model or placement approval.',
        maximum_body_half_width_mm=hx,maximum_body_half_height_mm=hy,
        minimum_over_power_balls_mm=min(p['distance_to_nearest_max_body_edge_mm'] for p in d),
        maximum_over_power_balls_mm=max(p['distance_to_nearest_max_body_edge_mm'] for p in d),balls=d)
report['registration_sensitivity']=dict(
    nominal_via_pad_mm=VIA,nominal_hole_assumption_mm=HOLE,published_min_ring_mm=.0762,
    nominal_ring_mm=num((VIA-HOLE)/2),
    radial_registration_etch_budget_before_min_ring_mm=num((VIA-HOLE)/2-.0762),
    maximum_actual_drill_at_zero_registration_budget_mm=num(VIA-2*.0762),
    ring_if_actual_drill_0p20_mm=num((VIA-.2)/2),
    warning='Nominal requested hole may be finished bore. A 0.20-mm compensated drill cannot retain a 0.0762-mm annulus in a 0.35-mm pad even with zero registration error under this conservative circle model. Fabricator-specific breakout rules are not assumed.')
(OUT/f'memory-soc-functional-escape-analysis{args.suffix}.json').write_text(json.dumps(report,indent=2)+'\n')
with (OUT/f'memory-soc-functional-balls{args.suffix}.csv').open('w') as f:
    writer=csv.DictWriter(f,fieldnames=['package','ball','function','category','x_mm','y_mm','ring'])
    writer.writeheader()
    for name,bs in [('FW200',lp),('BH153',em),('K230',k)]:
        writer.writerows(dict(package=name,**{key:p.get(key,'') for key in ['ball','function','category','x_mm','y_mm','ring']}) for p in bs if p['physical'])

# A readable vector diagram of the witness. This is deliberately not a footprint.
scale=38
def X(x):return 45+(x+7)*scale
def Y(y):return 95+(y+7.5)*scale
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1260" height="740" viewBox="0 0 1260 740">',
     '<rect width="1260" height="740" fill="white"/>',
     f'<text x="35" y="30" font-family="sans-serif" font-size="21">BH153 sparse through-via witness: conditional {LAND:g} mm Cu, {W:g}/{C:g} mm trace/space</text>',
     '<text x="35" y="54" font-family="sans-serif" font-size="15">11 HS200 signals; all physical balls retained; 20 power/ground vias modeled. No CAD or assembly approval.</text>']
for panel,layer in enumerate(['L1','L3']):
    off=panel*615
    svg.append(f'<g transform="translate({off},0)">')
    svg.append(f'<text x="50" y="85" font-family="sans-serif" font-size="20">{layer}</text>')
    svg.append(f'<rect x="{X(-5.75)}" y="{Y(-6.5)}" width="{11.5*scale}" height="{13*scale}" fill="none" stroke="#555" stroke-dasharray="5 4"/>')
    if layer=='L1':
        for p in em:
            if p['physical']:
                col='#98bdf0' if p['category']=='signal' else '#c0c0c0'
                svg.append(f'<circle cx="{X(p["x_mm"])}" cy="{Y(p["y_mm"])}" r="{LAND/2*scale}" fill="{col}" stroke="#666" stroke-width=".5"/>')
    for v in vias:
        x,y=v['xy']
        svg.append(f'<circle cx="{X(x)}" cy="{Y(y)}" r="{VIA/2*scale}" fill="#d49c62" stroke="#654" stroke-width=".5"/>')
        svg.append(f'<circle cx="{X(x)}" cy="{Y(y)}" r="{HOLE/2*scale}" fill="white"/>')
    for r in routes:
        if r['layer']==layer:
            pts=' '.join(f'{X(x)},{Y(y)}' for x,y in r['points'])
            svg.append(f'<polyline points="{pts}" fill="none" stroke="#064eaa" stroke-width="{W*scale}"/>')
            x,y=r['points'][-1]
            if r['net'].startswith('DAT') or (layer=='L1' and r['net'] in ['CMD','CLK']):
                tx,ty=X(x),Y(y)-7
                svg.append(f'<text x="{tx}" y="{ty}" transform="rotate(-50 {tx} {ty})" font-family="sans-serif" font-size="10">{r["net"]}</text>')
            else:
                svg.append(f'<text x="{X(x)+4}" y="{Y(y)-3}" font-family="sans-serif" font-size="10">{r["net"]}</text>')
    svg.append('</g>')
svg += ['<text x="35" y="695" font-family="sans-serif" font-size="14">Copper/pad/trace geometry only; ground-plane webs, return stitches, test-pad keepouts, CReg network and SI/PI remain unresolved.</text>',
        f'<text x="35" y="719" font-family="sans-serif" font-size="14">Process gates: ring {(VIA-HOLE)/2:.4f} mm vs 0.0762 mm minimum; hole {HOLE:g} mm vs 0.15 mm minimum. Exact-part land remains unqualified.</text>','</svg>']
(OUT/f'emmc-sparse-through-via-conditional-witness{args.suffix}.svg').write_text('\n'.join(svg))
assert not bad, bad[:10]
assert len(ddr)==65
assert len(decaps)==77
assert len([p for p in lp if p['physical']])==200
assert len([p for p in em if p['physical']])==153
assert len(k)==390
print(json.dumps({'output':str(OUT),'eMMC_witness_status':witness['status'],'checks':len(checks),
 'minimum_margin_mm':witness['minimum_checked_margin_mm'],'K230_signal_count':len(ksignals),
 'K230_signal_rings':kreport['signal_ring_histogram'],'K230_DDR_rings':kreport['DDR_ring_histogram'],
 'LPDDR_live_join_quadrants':{n:len(v) for n,v in report['LPDDR_live_SoC_joins_by_quadrant'].items()}},indent=2))
