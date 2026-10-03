#!/usr/bin/env python3
"""Geometric lower bounds for top-only local bypass; not a PDN model."""
from pathlib import Path
import collections,csv,hashlib,json,xml.etree.ElementTree as ET
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
COORD=ROOT/'engineering/mechanical/bga-K230-physical-centers.csv'
ALLOC=ROOT/'engineering/decoupling-allocation.csv'
XML=ROOT/'cad/high-temp-candidate/master.xml'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    points=list(csv.DictReader(COORD.open()))
    by_ball={r['ball']:r for r in points}
    allocation=list(csv.DictReader(ALLOC.open()))
    assert len(points)==390 and len(allocation)==77
    groups=collections.defaultdict(list)
    for r in allocation:groups[r['net']].append(r)
    assigned=collections.defaultdict(list)
    for net in ET.parse(XML).getroot().findall('./nets/net'):
        name=net.attrib['name']
        if name not in groups:continue
        for node in net.findall('node'):
            if node.attrib['ref']!='U1':continue
            ball=node.attrib['pin'];c=by_ball[ball]
            x,y=float(c['x_mm']),float(c['y_mm'])
            body_distance=6.55-max(abs(x),abs(y))
            assigned[name].append({'ball':ball,'source_function':c['source_function_label'],
                'x_mm':x,'y_mm':y,'minimum_lateral_distance_to_max_body_edge_mm':round(body_distance,6),
                'minimum_lateral_distance_to_external_component_extent_with_0p25_clearance_mm':round(body_distance+.25,6)})
    report={'status':'GEOMETRIC_REACH_SCREEN_ONLY_NOT_DECOUPLING_OR_ROUTING_PROOF',
        'source_files_sha256':{str(p.relative_to(ROOT)):sha(p) for p in [COORD,ALLOC,XML]},
        'allocation_count':len(allocation),
        'allocation_scope':'All77 grouped bypass parts from the source allocation. Some rails also decouple external memory; the rail totals are not asserted to be77 capacitors assigned to K230 alone.',
        'geometry':{'K230_max_body_mm':[13.1,13.1],
                    'body_source':'engineering/mechanical/bga-mechanical-audit.md; Canaan HDG package drawing D/E max13.100mm',
                    'body_source_url':'https://raw.githubusercontent.com/kendryte/k230_docs/main/zh/00_hardware/images/HDG/image007.png',
                    'component_clearance_assumption_mm':.25,
                    'distance_definition':'Planar minimum from ball center to any component/land extent outside a body-aligned13.1mm square plus0.25mm separation: 6.55-max(abs(x),abs(y))+.25. Component center distance is greater.',
                    'not_a_route_length_or_loop_inductance_estimate':True},
        'groups':[],
        'findings':[
            'The top-only requirement prevents placing bypass components directly below central power balls.',
            'CORE balls K11/L11 have a6.475mm minimum lateral separation from external component extents under the stated clearance assumption.',
            'Bypass allocation counts and summed footprint area do not verify local power/ground loop impedance.',
            'Local power/ground vias, uninterrupted reference planes and actual decoupling placement require a combined escape/PDN design; HDI alone does not move top-side components beneath the package.',
            'No maximum acceptable electrical distance is inferred from these geometric values. Required impedance, transient current, package parasitics, capacitor effective impedance and rail-plane structure remain necessary inputs.']}
    for name,components in sorted(groups.items()):
        balls=assigned[name]
        distances=[b['minimum_lateral_distance_to_external_component_extent_with_0p25_clearance_mm'] for b in balls]
        report['groups'].append({'net':name,'allocated_references':[r['reference'] for r in components],
            'allocation_values':dict(collections.Counter(r['value'] for r in components)),
            'K230_ball_count':len(balls),'K230_balls':balls,
            'minimum_lateral_bounds_range_mm':[min(distances),max(distances)] if distances else None,
            'placement_still_required':True})
    (OUT/'topside-bypass-reach.json').write_text(json.dumps(report,indent=2)+'\n')
    fig,(ax,table)=plt.subplots(1,2,figsize=(11,6),gridspec_kw={'width_ratios':[1.25,1]})
    ax.scatter([float(p['x_mm']) for p in points],[float(p['y_mm']) for p in points],s=12,color='#b9c1c9')
    power=[p for v in assigned.values() for p in v]
    sc=ax.scatter([p['x_mm'] for p in power],[p['y_mm'] for p in power],
        c=[p['minimum_lateral_distance_to_external_component_extent_with_0p25_clearance_mm'] for p in power],
        cmap='magma_r',vmin=3,vmax=6.5,s=42,edgecolor='white',lw=.4)
    ax.add_patch(Rectangle((-6.55,-6.55),13.1,13.1,fill=False,lw=1.2,color='#222'))
    ax.add_patch(Rectangle((-6.8,-6.8),13.6,13.6,fill=False,lw=1,color='#777',linestyle='--'))
    ax.set_xlim(-7.4,7.4);ax.set_ylim(7.4,-7.4);ax.set_aspect('equal')
    ax.set_xlabel('Package x (mm)');ax.set_ylabel('Package y (mm)')
    ax.set_title('K230 power balls on allocated rails\nTop-side capacitor extents stay outside dashed box',fontsize=10)
    fig.colorbar(sc,ax=ax,shrink=.75,label='Geometric lateral lower bound (mm)')
    table.axis('off')
    lines=['77 allocated bypass parts; placement remains open','', 'Rail                      Count   K230 reach range']
    for g in report['groups']:
        bounds=g['minimum_lateral_bounds_range_mm']
        lines.append(f"{g['net']:<24} {len(g['allocated_references']):>3}     {bounds[0]:.3f}–{bounds[1]:.3f} mm")
    lines += ['', 'Counts include shared memory rails.', 'These are geometry bounds, not loop lengths.', '',
              'Central CORE K11/L11: ≥6.475 mm', 'CPU/KPU examples: ≥5.825 mm', '',
              'Needed next: local vias, plane continuity,', 'real capacitor placement and PDN verification.']
    table.text(0,.98,'\n'.join(lines),ha='left',va='top',family='monospace',fontsize=8.4,linespacing=1.6)
    fig.suptitle('TOP-SIDE BYPASS REACH • NO PLACEMENT OR ELECTRICAL QUALIFICATION',fontsize=11,fontweight='bold')
    fig.tight_layout(rect=[0,0,1,.95])
    fig.savefig(OUT/'topside-bypass-reach.svg');fig.savefig(OUT/'topside-bypass-reach.png',dpi=180)
    print(json.dumps({'allocations':len(allocation),'K230_power_balls_on_allocated_rails':len(power),'maximum_lateral_lower_bound_mm':max(p['minimum_lateral_distance_to_external_component_extent_with_0p25_clearance_mm'] for p in power)},indent=2))

if __name__=='__main__':main()
