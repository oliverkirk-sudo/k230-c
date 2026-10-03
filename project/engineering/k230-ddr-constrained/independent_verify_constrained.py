#!/usr/bin/env python3
"""Independent review of the LOCAL constrained K230 fanout; no router imports.

Uses continuous disk/capsule distances, exhaustive same-layer pair checks and
source-derived physical/net demand. The separately attempted U1/U2 anchor
extension is deliberately outside this review.
"""
from collections import Counter, defaultdict
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
import csv
import hashlib
import json
import math
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TOL = 1e-9
LAYERS = tuple(f'L{i}' for i in range(1, 9))
W, CLEAR, LAND, VIA, HOLE, HC = .1016, .1016, .27, .325, .15, .1524

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def csvrows(rel):
    return list(csv.DictReader((ROOT / rel).open()))

def pt(x):
    return complex(*x)

def dot(a, b):
    return (a.conjugate() * b).real

def cross(a, b):
    return (a.conjugate() * b).imag

def pdist(p, a, b):
    v = b - a
    if v == 0:
        return abs(p - a)
    projection = dot(p - a, v) / dot(v, v)
    if projection <= 0:
        return abs(p - a)
    if projection >= 1:
        return abs(p - b)
    return abs(cross(v, p - a)) / abs(v)

def sdist(a, b, c, d):
    u, v, w = b - a, d - c, c - a
    determinant = cross(u, v)
    # Proper intersections; parallel/collinear and degenerate segments use
    # endpoint projections. Avoid spurious near-parallel floating crossings.
    box_overlap = (max(min(a.real, b.real), min(c.real, d.real)) <= min(max(a.real, b.real), max(c.real, d.real)) and
                   max(min(a.imag, b.imag), min(c.imag, d.imag)) <= min(max(a.imag, b.imag), max(c.imag, d.imag)))
    if box_overlap and abs(determinant) > 1e-14 * abs(u) * abs(v):
        s, t = cross(w, v) / determinant, cross(w, u) / determinant
        if 0 <= s <= 1 and 0 <= t <= 1:
            return 0.
    return min(pdist(a, c, d), pdist(b, c, d), pdist(c, a, b), pdist(d, a, b))

def close(a, b):
    return abs(pt(a) - pt(b)) < TOL

def xmlmap(path):
    nets, byref = {}, defaultdict(dict)
    for net in ET.parse(path).findall('./nets/net'):
        nodes = net.findall('node')
        nets[net.attrib['name']] = {(n.attrib['ref'], n.attrib['pin'], n.attrib.get('pinfunction')) for n in nodes}
        for n in nodes:
            ref, pin = n.attrib['ref'], n.attrib['pin']
            assert pin not in byref[ref], (ref, pin, 'duplicate XML pin')
            byref[ref][pin] = (net.attrib['name'], len(nodes), n.attrib.get('pinfunction'))
    return nets, byref

def main():
    source = HERE / 'trial-groups-outer-21.json'
    source_bytes = source.read_bytes()
    trial = json.loads(source_bytes)
    fixtures = [((0j, 1+1j, 1j, 1+0j), 0), ((0j, 2+0j, 1+0j, 3+0j), 0),
                ((0j, 1+0j, 2+0j, 3+0j), 1), ((0j, 1+0j, 1j, 1+1j), 1),
                ((0j, 0j, 1+0j, 1+1j), 1), ((0j, 1+0j, 1+1j, 2+1j), 1),
                ((0j, 1+1j, .5+.5j, 2+2j), 0), ((0j, 0j, 3+4j, 3+4j), 5),
                ((.325-.975j,.65-1.3j,-6.175+5.525j,-5.85+5.2j),math.hypot(6.175,6.175))]
    assert all(abs(sdist(*args)-expected) < TOL for args, expected in fixtures)
    required_rules = dict(trace_width=W, copper_clearance=CLEAR, top_land=LAND,
        via_pad=VIA, assumed_hole=HOLE, hole_to_other_copper=HC, ball_pitch=.65,
        nominal_annular_ring=(VIA-HOLE)/2, selected_min_annular_ring=.0762)
    assert trial['rules'] == required_rules
    phys = {r['ball']: r for r in csvrows('engineering/mechanical/bga-K230-physical-centers.csv')}
    types = {r['ball']: r for r in csvrows('engineering/pin-types/k230-all390-type-audit.csv')}
    extracted = {r['soc_ball']: r for r in csvrows('data/k230-source-extraction/k230-390-balls.csv')}
    assigns = {r['pin']: r for r in csvrows('cad/high-temp-candidate/master-pin-assignments.csv') if r['reference']=='U1'}
    frozen = {r['ball']: r for r in csvrows('engineering/bga-engineering-candidates/memory-soc-functional-balls.csv') if r['package']=='K230'}
    ddrrows = csvrows('engineering/routing/high-temp-ddr-route-contract.csv')
    ddr = {r['soc_ball']: r for r in ddrrows}
    xml_nets, xml_byref = xmlmap(ROOT/'cad/high-temp-candidate/master.xml')
    balls = {b['ball']: b for b in trial['balls']}
    vias = {v['ball']: v for v in trial['vias']}
    routes = defaultdict(list)
    for index, r in enumerate(trial['routes']):
        routes[r['ball']].append((index, r))
    assert len(balls)==len(trial['balls'])==len(phys)==len(assigns)==390
    assert set(balls)==set(phys)==set(types)==set(extracted)==set(assigns)==set(frozen)==set(xml_byref['U1'])
    assert len(ddrrows)==len(ddr)==65 and len({r['net'] for r in ddrrows})==65
    assert len(vias)==len(trial['vias'])==327 and len({tuple(v['xy']) for v in vias.values()})==327
    assert set(routes) <= set(balls) and set(vias) <= set(balls)
    source_hashes = {p:dict(trial_sha256=h, current_sha256=sha(ROOT/p), exact_match=h==sha(ROOT/p)) for p,h in trial['source_sha256'].items()}
    # The producer snapshot is expected to differ only in passive XML metadata.
    # Any unmapped source change other than XML is a hard stop for this review.
    assert all(v['exact_match'] for p,v in source_hashes.items() if p!='cad/high-temp-candidate/master.xml')
    rownames = 'ABCDEFGHJKLMNPRTUVWY'
    connections, endpoints, outer = [], [], []
    for name, b in balls.items():
        p, m, t, f = phys[name], assigns[name], types[name], frozen[name]
        net, x, y = m['net'] or None, float(p['x_mm']), float(p['y_mm'])
        actual_net, node_count, actual_fn = xml_byref['U1'][name]
        assert abs(x-(int(name[1:])-10.5)*.65)<TOL
        assert abs(y-(rownames.index(name[0])-9.5)*.65)<TOL
        assert close([x,y],[b['x'],b['y']]) and close([x,y],[float(f['x_mm']),float(f['y_mm'])])
        ring=min(int(name[1:])-1,20-int(name[1:]),rownames.index(name[0]),19-rownames.index(name[0]))
        assert ring==b['ring']==int(f['ring'])
        assert b['function']==p['source_function_label']==m['function']==extracted[name]['soc_signal']==t['canonical_signal']==actual_fn
        assert b['net']==net and b['xml_net']==actual_net==t['current_net']
        assert b['xml_endpoint_count']==node_count and (net is None or net==actual_net)
        category='unused' if net is None else 'ground' if net=='GND' else 'power' if t['official_dir']=='P' else 'signal'
        assert category==b['category']==f['category']
        assert b['physical_top_land_diameter']==LAND and b['ddr65']==ddr.get(name)
        rs, v = routes[name], vias.get(name)
        for _, r in rs:
            assert r['net']==net and r['layer'] in LAYERS and len(r['points'])>=2
            assert all(all(math.isfinite(z) for z in q) for q in r['points'])
            assert all(not close(a,z) for a,z in zip(r['points'],r['points'][1:]))
        high = name in ddr and ddr[name]['sink_group']!='RESET_ASYNCHRONOUS'
        if v:
            assert v['net']==net and v['category']==category and v['pad']==VIA and v['hole']==HOLE
            assert tuple(v['retained_annuli'])==LAYERS and close(v['xy'],[x+.325,y-.325])
            assert (v['pad']-v['hole'])/2>=.0762
            assert v['added_outer_ddr_transition']==bool(high and ring==0)
        if category=='unused':
            assert node_count==1 and len(rs)==0 and v is None
            state='ISOLATED_PHYSICAL_LAND_RETAINED'
            extra={}
        elif category in ('power','ground'):
            assert v and len(rs)==1
            _, r=rs[0]
            assert r['purpose']=='ball_to_via' and r['layer']=='L1'
            assert close(r['points'][0],[x,y]) and close(r['points'][-1],v['xy'])
            assert set(v['functional_layers'])==({'L1','L2','L4','L7'} if category=='ground' else {'L1','L5'})
            state='CONNECTED_LAND_DOGBONE_VIA_PLANES_UNPROVEN'
            extra=dict(via_xy=v['xy'])
        else:
            escapes=[r for _,r in rs if r['purpose'] in ('direct_signal_escape','via_to_outside_body')]
            assert len(escapes)==1
            escape=escapes[0]
            if v:
                assert len(rs)==2 and escape['purpose']=='via_to_outside_body' and escape['layer'] in ('L3','L6','L8')
                dogbones=[r for _,r in rs if r['purpose']=='ball_to_via']
                assert len(dogbones)==1 and dogbones[0]['layer']=='L1'
                assert close(dogbones[0]['points'][0],[x,y]) and close(dogbones[0]['points'][-1],v['xy'])
                assert close(escape['points'][0],v['xy']) and set(v['functional_layers'])=={'L1',escape['layer']}
            else:
                assert not high and ring==0 and len(rs)==1 and escape['layer']=='L1'
                assert escape['purpose']=='direct_signal_escape' and close(escape['points'][0],[x,y])
            outside=max(abs(c) for c in escape['points'][-1])-6.55
            assert outside>W/2 and abs(outside-.6)<TOL
            length=sum(abs(pt(z)-pt(a)) for _,r in rs for a,z in zip(r['points'],r['points'][1:]))
            extra=dict(layer=escape['layer'], via_count=int(v is not None), endpoint_xy=escape['points'][-1],
                local_centerline_length_mm=length, center_clearance_to_max_body_mm=outside,
                copper_endcap_clearance_to_max_body_mm=outside-W/2)
            endpoints.append(dict(ball=name,net=net,**extra))
            if high:
                assert v and escape['layer'] in ('L3','L8')
                if ring==0:
                    outer.append(dict(ball=name,net=net,via_xy=v['xy'],dogbone_points=dogbones[0]['points'],**extra))
            state='CONTINUOUS_TO_OUTSIDE_MAX_13P1MM_BODY'
        connections.append(dict(ball=name,net=net,category=category,state=state,**extra))
    assert Counter(b['category'] for b in balls.values())==dict(signal=209,power=53,ground=105,unused=23)
    assert len(endpoints)==len({e['net'] for e in endpoints})==209 and len(outer)==16
    assert not trial['unsolved_signal_balls']
    end_by_ball={e['ball']:e for e in endpoints}
    ddr_paths=[]
    for row in ddrrows:
        e=end_by_ball[row['soc_ball']]
        assert e['net']==row['net']
        assert ('U1',row['soc_ball'],row['soc_actual_function']) in xml_nets[row['net']]
        assert ('U2',row['dram_ball'],row['dram_actual_function']) in xml_nets[row['net']]
        ddr_paths.append(dict(e,sink_group=row['sink_group'],dram_ball=row['dram_ball'],
            soc_package_length_mm=float(row['soc_package_trace_um'])/1000 if row['soc_package_trace_um'] else None))
    bynet={p['net']:p for p in ddr_paths}
    groups=[]
    for name in sorted({p['sink_group'] for p in ddr_paths if p['sink_group']!='RESET_ASYNCHRONOUS'}):
        ps=[p for p in ddr_paths if p['sink_group']==name]
        counts=Counter(p['layer'] for p in ps)
        assert len(ps)==(11 if 'BYTE' in name else 10) and len(counts)==1 and set(counts)<={'L3','L8'}
        assert {p['via_count'] for p in ps}=={1}
        groups.append(dict(group=name,net_count=len(ps),layer=ps[0]['layer'],via_count_per_net=1,nets=[p['net'] for p in ps]))
    pairs=[]
    for net,pos in bynet.items():
        if not net.endswith('_P'):
            continue
        neg=bynet[net[:-2]+'_N']
        assert pos['layer']==neg['layer'] and pos['via_count']==neg['via_count']==1
        pairs.append(dict(pair=net[:-2],positive_ball=pos['ball'],negative_ball=neg['ball'],layer=pos['layer'],
            via_counts=[pos['via_count'],neg['via_count']],
            local_length_difference_mm=abs(pos['local_centerline_length_mm']-neg['local_centerline_length_mm']),
            endpoint_center_separation_mm=abs(pt(pos['endpoint_xy'])-pt(neg['endpoint_xy']))))
    assert len(groups)==6 and len(pairs)==6
    assert len([p for p in ddr_paths if p['sink_group']!='RESET_ASYNCHRONOUS'])==64
    assert not [p for p in ddr_paths if p['layer']=='L6']
    print('Independent source/connectivity checks passed:390 lands,209 escapes,327 vias,64 high-speed transitions,6 common-layer groups,6 equal-via/common-layer pairs.',flush=True)

    pads, tracks=defaultdict(list),defaultdict(list)
    holes=[]
    for b in balls.values():
        pads['L1'].append(dict(id='land:'+b['ball'],net=b['net'] or '__isolated__'+b['ball'],ball=b['ball'],
            p=complex(b['x'],b['y']),radius=LAND/2,kind='land'))
    for v in vias.values():
        for layer in LAYERS:
            pads[layer].append(dict(id='via:'+v['ball'],net=v['net'],ball=v['ball'],p=pt(v['xy']),radius=VIA/2,kind='via'))
        holes.append(dict(id='hole:'+v['ball'],net=v['net'],ball=v['ball'],p=pt(v['xy']),radius=HOLE/2))
    for i,r in enumerate(trial['routes']):
        for k,(a,b) in enumerate(zip(r['points'],r['points'][1:])):
            tracks[r['layer']].append(dict(id=f'route:{i}:{r["ball"]}:{r["layer"]}:{k}',net=r['net'],ball=r['ball'],
                a=pt(a),b=pt(b),radius=W/2,purpose=r['purpose']))
    counts,same_counts=Counter(),Counter()
    minima,same_minima={},{}
    fails,fails020=[],[]
    short_count=0
    open_checks=0
    # One record per unordered net pair on each physical layer, not per vertex.
    trace_pair_min={}
    def register(kind,gap,a,b,layer,hole=False):
        nonlocal short_count,open_checks
        record=dict(kind=kind,a=a['id'],b=b['id'],layer=layer,gap_mm=gap)
        if a['net']==b['net']:
            if a['ball']!=b['ball']:
                same_counts[kind]+=1
                if kind not in same_minima or gap<same_minima[kind]['gap_mm']:
                    same_minima[kind]=record
            return
        counts[kind]+=1
        need=HC if hole else CLEAR
        record.update(required_mm=need,margin_mm=gap-need)
        if kind not in minima or gap<minima[kind]['gap_mm']:
            minima[kind]=record
        if gap<need-TOL:
            fails.append(record)
        if gap<(.2 if hole else CLEAR)-TOL:
            fails020.append(dict(record,separate_margin_mm=gap-(.2 if hole else CLEAR)))
        if not hole and gap<-TOL:
            short_count+=1
        if a['net'].startswith('__isolated__') or b['net'].startswith('__isolated__'):
            open_checks+=1
        if kind=='trace_to_trace':
            key=(layer,*sorted((a['net'],b['net'])))
            if key not in trace_pair_min or gap<trace_pair_min[key]['gap_mm']:
                trace_pair_min[key]=dict(record,nets=list(key[1:]),centerline_distance_mm=gap+W)
    for layer in LAYERS:
        for a,b in combinations(pads[layer],2):
            register('copper_'+a['kind']+'_'+b['kind'],abs(a['p']-b['p'])-a['radius']-b['radius'],a,b,layer)
        for h in holes:
            for p in pads[layer]:
                register('hole_to_'+p['kind'],abs(h['p']-p['p'])-h['radius']-p['radius'],h,p,layer,True)
        for t in tracks[layer]:
            for p in pads[layer]:
                register('trace_to_'+p['kind'],pdist(p['p'],t['a'],t['b'])-p['radius']-t['radius'],t,p,layer)
            for h in holes:
                register('hole_to_trace',pdist(h['p'],t['a'],t['b'])-h['radius']-t['radius'],h,t,layer,True)
        for t,u in combinations(tracks[layer],2):
            register('trace_to_trace',sdist(t['a'],t['b'],u['a'],u['b'])-t['radius']-u['radius'],t,u,layer)
    drill_gap,da,db=min((abs(a['p']-b['p'])-a['radius']-b['radius'],a['ball'],b['ball']) for a,b in combinations(holes,2))
    print(f'Independent continuous geometry:{sum(counts.values())} different-net checks,{len(fails)} nominal failures,{short_count} copper overlaps.',flush=True)

    # Routing guidance screen is intentionally TRACE-TO-TRACE ONLY.
    # It neither inflates via/pad fabrication rules nor treats P/N coupling as
    # an unwanted-crosstalk separation rule.
    stack=json.loads((ROOT/'engineering/mechanical/core-stackup-process-proposal.json').read_text())
    selected=next(s for s in stack['published_stackup_candidates'] if s['id']=='PW_8L_1P2_70_CANDIDATE')
    dielectrics=selected['dielectric_after_lamination_L1_to_L8_mm']
    heights={'L1':[dielectrics[0]],'L3':[dielectrics[1],dielectrics[2]],'L8':[dielectrics[6]]}
    guidance=[],[]
    h_records,ambiguous_records=guidance
    pn_records=[]
    pg_nets={b['net'] for b in balls.values() if b['category']=='power'}
    hs={n:p for n,p in bynet.items() if p['sink_group']!='RESET_ASYNCHRONOUS'}
    for (layer,na,nb),r in sorted(trace_pair_min.items()):
        if na not in hs and nb not in hs:
            continue
        pairmates=na.endswith(('_P','_N')) and nb.endswith(('_P','_N')) and na[:-2]==nb[:-2]
        if pairmates:
            pn_records.append(dict(r,classification='P_N_COUPLING_NOT_ASSESSED'))
            continue
        if layer not in heights:
            continue
        ra,rb=hs.get(na),hs.get(nb)
        mult=None
        reason=None
        if ra and rb:
            if ra['sink_group']!=rb['sink_group']:
                mult,reason=3,'different_DDR_groups'
            elif ('DQS' in na or 'DQS' in nb or 'CLK' in na or 'CLK' in nb):
                mult,reason=3,'DQ_DMI_to_DQS_or_CA_to_CK'
            elif 'BYTE' in ra['sink_group']:
                mult,reason=2,'DQ_DMI_within_same_byte'
        elif na in pg_nets or nb in pg_nets or 'VREF' in na.upper() or 'VREF' in nb.upper():
            mult,reason=3,'DDR_to_supply_or_Vref_trace'
        if mult:
            thresholds=[mult*h for h in sorted(set(heights[layer]))]
            h_records.append(dict(r,reason=reason,H_multiplier=mult,candidate_H_mm=sorted(set(heights[layer])),
                conditional_required_edge_gap_mm=thresholds,
                violates_even_smallest_H=r['gap_mm']<min(thresholds)-TOL,
                violates_largest_H=r['gap_mm']<max(thresholds)-TOL))
        # The source text says3W without establishing centerline versus edge.
        # Report both hypotheses, never label either an approved constraint.
        if ra and rb:
            ambiguous_records.append(dict(r,source_text='3W',
                fails_3W_centerline_hypothesis=r['centerline_distance_mm']<3*W-TOL,
                fails_3W_edge_gap_hypothesis=r['gap_mm']<3*W-TOL))
    h_exceptions=[r for r in h_records if r['violates_even_smallest_H']]
    h_larger_only=[r for r in h_records if not r['violates_even_smallest_H'] and r['violates_largest_H']]
    h_by_layer={layer:dict(trace_pair_checks=sum(r['layer']==layer for r in h_records),
        exceptions_even_smallest_H=sum(r['layer']==layer for r in h_exceptions),
        additional_exceptions_larger_H=sum(r['layer']==layer for r in h_larger_only)) for layer in heights}
    audit=json.loads((HERE/'trial-groups-outer-21-audit.json').read_text())
    producer_comparison=dict(trial_hash_match=audit['trial_sha256']==hashlib.sha256(source_bytes).hexdigest(),
        check_count_match=audit['nominal']['checks']==sum(counts.values()),
        checks_by_kind_match=audit['nominal']['checks_by_kind']==dict(counts),
        failure_count_match=audit['nominal']['failure_count']==len(fails),
        hole020_failure_count_match=audit['separate_hole_clearance_0p20']['failure_count']==len(fails020))
    assert all(producer_comparison.values())
    assert source_bytes==source.read_bytes(), 'Raw trial changed during review'
    report=dict(status='PASS_INDEPENDENT_NOMINAL_LOCAL_FANOUT_AND_DDR_LAYER_VIA_INVARIANTS_ONLY' if not fails else 'FAIL_LOCAL_NOMINAL_GEOMETRY',
        generated_utc=datetime.now(timezone.utc).isoformat(),trial_file=source.name,
        trial_sha256=sha(source),verification_script=Path(__file__).name,verification_script_sha256=sha(Path(__file__)),
        method=dict(imports_producer_router_or_auditor=False,geometry='Exhaustive continuous closed-disk/capsule and drill-circle comparisons with analytic point-segment distances and segment intersections; no sampling.',
            algorithm_fixtures=len(fixtures),tolerance_mm=TOL,
            same_net_policy='Own and same-net electrical copper contacts exempt; different-owner same-net minima retained separately. Open lands each get a unique isolated net. Signal nets are all distinct.'),
        source_checks=dict(current_source_hashes=source_hashes,
            all390_current_U1_ball_function_net_node_count_matches=True,
            all65_current_U1_U2_DDR_pairs_match_contract=True,
            grid_rederived_from_ball_labels_and_0p65_pitch=True,
            frozen_grid_and_source_function_extract_match=True,
            absent_grid_sites=sorted({r+str(c) for r in rownames for c in range(1,21)}-set(balls)),
            xml_hash_difference='Current XML metadata may differ from producer snapshot; connectivity and pin functions independently checked. Snapshot comparison, if available, is recorded separately.'),
        demand=dict(physical_lands=len(balls),categories=dict(Counter(b['category'] for b in balls.values())),
            signal_escapes=len(endpoints),distinct_signal_nets=len({e['net'] for e in endpoints}),
            open_balls=[b['ball'] for b in balls.values() if b['category']=='unused'],
            all_open_balls_keep_land_without_via_or_route=True),
        connectivity=dict(all390_per_ball=connections,all158_power_ground_lands_reach_dedicated_vias=True,
            phantom_via_count=0,via_with_missing_dogbone_count=0,signal_via_with_missing_escape_count=0,
            PG_limit='Land-to-dedicated-via only; intended plane labels are not physical plane continuity/PDN evidence.'),
        geometry=dict(rules_mm=required_rules,total_vias=len(vias),via_categories=dict(Counter(v['category'] for v in vias.values())),
            annuli_per_layer={l:sum(p['kind']=='via' for p in pads[l]) for l in LAYERS},
            nominal_annulus_mm=(VIA-HOLE)/2,annulus_margin_mm=(VIA-HOLE)/2-.0762,
            route_records=len(trial['routes']),route_purposes=dict(Counter(r['purpose'] for r in trial['routes'])),
            segments_by_layer={l:len(tracks[l]) for l in LAYERS},signal_exit_layers=dict(Counter(e['layer'] for e in endpoints)),
            max_package_body_mm=13.1,outside_endpoint_count=len(endpoints),
            minimum_endpoint_center_clearance_mm=min(e['center_clearance_to_max_body_mm'] for e in endpoints),
            minimum_endpoint_copper_endcap_clearance_mm=min(e['copper_endcap_clearance_to_max_body_mm'] for e in endpoints),
            minimum_drill_edge_gap_mm=drill_gap,minimum_drill_pair=[da,db]),
        nominal_clearance=dict(checks=sum(counts.values()),checks_by_kind=dict(counts),failure_count=len(fails),
            failures=fails,minimum_by_kind=minima,copper_overlap_count=short_count,isolated_open_land_checks=open_checks),
        separate_hole_0p20_screen=dict(status='FAIL' if fails020 else 'PASS',failure_count=len(fails020),
            failure_kinds=dict(Counter(r['kind'] for r in fails020)),examples=fails020[:12],
            limit='Separate alternative process rule only; failure of this exact geometry is not a global impossibility proof.'),
        same_net_distinct_ball_checks=dict(counts=dict(same_counts),minima=same_minima),
        DDR=dict(status='LOCAL_LAYER_AND_REAL_VIA_INVARIANTS_PASS_NOT_COUPLED_OR_TIMING_QUALIFIED',
            all65_paths=ddr_paths,high_speed_count=64,high_speed_vias_per_net=1,
            high_speed_layers=dict(Counter(p['layer'] for p in ddr_paths if p['sink_group']!='RESET_ASYNCHRONOUS')),
            all65_exit_layers=dict(Counter(p['layer'] for p in ddr_paths)),L6_nets=[],
            complete_differential_pairs=pairs,high_speed_groups=groups,added_outer_via_count=len(outer),added_outer_vias=outer),
        routing_spacing_screen=dict(status='CONDITIONAL_TRACE_SPACING_EXCEPTIONS_FOUND' if h_exceptions else 'NO_CONDITIONAL_EXCEPTIONS_FOUND_NOT_SI_QUALIFICATION',
            source_image='/workspace/shared/k230-reference/mechanical/k230-ddr-constrained/official-image054.png',
            source_image_sha256=sha(Path('/workspace/shared/k230-reference/mechanical/k230-ddr-constrained/official-image054.png')),
            visual_interpretation='Figure dimensions are edge-to-edge:2H between DQ/DMI within byte;3H to DQS,CK,other groups,supply/Vref. No pad-to-track fabrication rule inferred. CA-to-CA within same group is not assigned2H from this figure.',
            candidate_stack_id=selected['id'],reference_H_candidates_mm=heights,
            H_qualification='L3 has two proposed ground references at0.130 and0.109mm: both hypotheses are reported; L1/L8 proposed reference dielectric0.1195mm. These are candidate stack numbers,not finalized field-solver geometry or verified continuous reference copper.',
            per_layer=h_by_layer,checks=len(h_records),exceptions_even_smallest_H_count=len(h_exceptions),
            exceptions_even_smallest_H=h_exceptions,additional_exceptions_larger_H=h_larger_only,
            trace_pair_measurements=h_records,
            ambiguous_3W=dict(width_mm=W,hypothesis_3W_mm=3*W,
                caveat='Source text does not define edge-to-edge versus center-to-center; neither reading is adopted as an approved design rule. Differential P/N mates excluded.',
                fails_centerline_count=sum(r['fails_3W_centerline_hypothesis'] for r in ambiguous_records),
                fails_edge_gap_count=sum(r['fails_3W_edge_gap_hypothesis'] for r in ambiguous_records),measurements=ambiguous_records),
            PN_minimum_gaps_measurement_only=pn_records,
            limits='Whole local trace centerlines including breakout are screened. L1 dogbones reported separately by layer. Via pads,lands,plane copper and via antipads are excluded from this routing-guidance screen. Minimum-gap exceptions quantify local shortfalls but do not model parallel coupled length,crosstalk,breakout exceptions,impedance or timing.'),
        producer_audit_comparison=producer_comparison,
        unqualified=['P/N coupling and100ohm differential/50ohm single-ended impedance',
            'Final dielectric stack and continuous ground planes,return vias,antipads and reference continuity',
            'U2-side complete routing and65-link anchor extension (separate artifact,not inspected here)',
            'DRAM package delay and full package-plus-board-plus-via timing; local copper length is not electrical delay',
            'Manufacturing drill compensation,registration and retained annulus; exact production land/mask/paste qualification',
            'Complete board routing,decoupling,PDN,current and thermal closure'],
        scope='Independent LOCAL constrained fanout review only. Frozenv10/v11,eMMC,generic K230 controls and all external state unchanged.')
    output=HERE/'independent-constrained-review.json'
    output.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(status=report['status'],report=str(output),nominal_checks=sum(counts.values()),
        nominal_failures=len(fails),H_screen=h_by_layer,ambiguous3W_centerline_fails=report['routing_spacing_screen']['ambiguous_3W']['fails_centerline_count'],
        ambiguous3W_edge_fails=report['routing_spacing_screen']['ambiguous_3W']['fails_edge_gap_count'])),flush=True)

if __name__=='__main__':
    main()
