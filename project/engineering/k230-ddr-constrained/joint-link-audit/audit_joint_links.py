#!/usr/bin/env python3
"""Audit direct existing-SoC-via to existing-RAM-via DDR candidate paths.

This auditor never changes an input, router, or CAD file. It reuses the old
independent analytic copper/hole audit, not the router's occupancy masks.
Passing this audit is not native CAD, SI, timing, fabrication, or release approval.
"""
import argparse
import copy
import csv
import hashlib
import json
import math
import sys
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
OLD = HERE.parent / 'link-trial'
sys.path.insert(0, str(OLD))
import audit_links as analytic
import route_links as source

PAIRS = ['DDR_DQSA0', 'DDR_DQSA1', 'DDR_DQSB0', 'DDR_DQSB1', 'DDR_CLKA', 'DDR_CLKB']
IDENTITY_FIELDS = ['net', 'soc_ball', 'soc_actual_function', 'dram_ball',
                   'dram_actual_function', 'sink_group', 'soc_package_trace_um',
                   'guide_alias_hazard']


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':'))


def multiset(rows):
    return Counter(canonical(r) for r in rows)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_semantics(j):
    """Reconcile changed whole-netlist hashes without rewriting frozen provenance."""
    frozen = HERE / 'frozen-reference' / 'master-pin-assignments.csv'
    current_csv = source.ROOT / 'cad/high-temp-candidate/master-pin-assignments.csv'
    current_xml = source.ROOT / 'cad/high-temp-candidate/master.xml'
    expected_hash = j['source_sha256']['cad/high-temp-candidate/master-pin-assignments.csv']
    if sha(current_csv) == expected_hash:
        frozen = current_csv
    if not frozen.exists() or sha(frozen) != expected_hash:
        return dict(status='UNVERIFIED_FROZEN_PIN_MAP', verified=False)
    def csv_map(path):
        with path.open() as f:
            return {(r['reference'], r['pin']): (r['function'], r['net']) for r in csv.DictReader(f)}
    old, cur = csv_map(frozen), csv_map(current_csv)
    xml = {}
    for net in ET.parse(current_xml).getroot().findall('nets/net'):
        name = net.get('name')
        for node in net.findall('node'):
            xml[(node.get('ref'), node.get('pin'))] = (node.get('pinfunction'),
                '' if name.startswith('unconnected-') else name)
    changed = [dict(reference=k[0], pin=k[1], frozen=old.get(k), current=cur.get(k))
               for k in sorted(set(old) | set(cur)) if old.get(k) != cur.get(k)]
    relevant = {k for k in set(old) | set(cur) | set(xml) if k[0] in ('U1', 'U2', 'U3')}
    mismatches = [dict(reference=k[0], pin=k[1], frozen=old.get(k), current_csv=cur.get(k),
                       current_xml=xml.get(k)) for k in sorted(relevant)
                  if not (old.get(k) == cur.get(k) == xml.get(k))]
    return dict(status='MATCH_U1_U2_U3_FUNCTION_NET_ENDPOINTS' if not mismatches else 'FAIL_RELEVANT_ENDPOINT_MATCH',
        verified=not mismatches, frozen_csv_path=str(frozen), frozen_csv_sha256=sha(frozen),
        current_csv_sha256=sha(current_csv), current_xml_sha256=sha(current_xml),
        verified_endpoint_counts=dict(Counter(k[0] for k in relevant)),
        relevant_endpoint_mismatches=mismatches, all_changed_pin_function_net_records=changed,
        changed_references=sorted({d['reference'] for d in changed}),
        note='Frozen CSV is byte-identical to the candidate-recorded source. Current CSV and XML '
             'are compared independently for U1/U2/U3 functions and nets. Component values and '
             'footprints outside this routing scope are not qualified by the pin-map comparison.')


def inspect_structure(j, baseline):
    """Derive connectivity from source identities and emitted geometry only."""
    _, source_balls, source_vias, source_routes, contract = source.load()
    expected = {c['net']: c for c in contract}
    errors = []
    checks = []

    def check(name, ok, detail=None):
        checks.append(dict(check=name, passed=bool(ok), detail=detail))
        if not ok:
            errors.append(dict(check=name, detail=detail))
        return bool(ok)

    check('source_contract_exact_65_unique_nets', len(contract) == len(expected) == 65)
    for key, rows in [('balls', j['balls']), ('vias', j['vias'])]:
        check(key + '_unique_ids', len({x['id'] for x in rows}) == len(rows))
    check('all_590_ball_lands_preserved', len(j['balls']) == 590 and
          multiset(j['balls']) == multiset(source_balls) == multiset(baseline['balls']))
    # Functional plane ports may change only for the 130 DDR signal vias.
    def physical(v):
        return {k: x for k, x in v.items() if k != 'functional_layers'}
    check('all_502_vias_physical_geometry_preserved', len(j['vias']) == 502 and
          multiset(map(physical, j['vias'])) == multiset(map(physical, source_vias)) ==
          multiset(map(physical, baseline['vias'])))
    base_vias = {v['id']: v for v in source_vias}
    check('non_DDR_via_functional_layers_preserved', all(
        v['id'] in base_vias and v == base_vias[v['id']]
        for v in j['vias'] if v['net'] not in expected))
    retained = [r for r in source_routes if not (
        r['ref'] == 'U1' and r['purpose'] == 'via_to_outside_body' and r['net'] in expected)]
    candidate_static = [r for r in j['routes'] if r['purpose'] != 'actual_DDR_link']
    check('only_65_DDR_exit_tracks_removed_all_other_routes_preserved',
          len(source_routes) - len(retained) == 65 and multiset(retained) == multiset(candidate_static),
          dict(source_routes=len(source_routes), expected_retained=len(retained), candidate_retained=len(candidate_static)))
    for key in ('rules', 'placement'):
        check(key + '_preserved', j[key] == baseline[key])
    for key in ('bounds_xy_mm', 'grid_shape'):
        check('search_' + key + '_preserved', j['search'][key] == baseline['search'][key])
    actual_hashes = {str(p.relative_to(source.ROOT)): sha(p) for p in source.SOURCES}
    hash_changes = [dict(path=k, frozen_sha256=j['source_sha256'].get(k), current_sha256=v)
                    for k, v in actual_hashes.items() if j['source_sha256'].get(k) != v]
    reconciled = source_semantics(j)
    allowed_changed = {'cad/high-temp-candidate/master-pin-assignments.csv', 'cad/high-temp-candidate/master.xml'}
    check('nonmaster_routing_source_hashes_match_current',
          all(d['path'] in allowed_changed for d in hash_changes), hash_changes)
    check('current_U1_U2_U3_pin_function_net_semantics_match_frozen', reconciled['verified'], reconciled)
    check('source_hashes_match_original_baseline', j['source_sha256'] == baseline['source_sha256'])

    balls = {b['id']: b for b in j['balls']}
    vias = {v['id']: v for v in j['vias']}
    routed = defaultdict(list)
    links = defaultdict(list)
    declared = defaultdict(list)
    for r in j['routes']:
        routed[r['net']].append(r)
        if r['purpose'] == 'actual_DDR_link':
            links[r['net']].append(r)
    for row in j['pernet']:
        declared[row['net']].append(row)
    check('candidate_links_exact_65_source_nets_once', set(links) == set(expected) and
          all(len(v) == 1 for v in links.values()))
    check('pernet_exact_65_source_nets_once', set(declared) == set(expected) and
          all(len(v) == 1 for v in declared.values()))
    records = []
    for net, c in expected.items():
        sb, rb = 'U1:' + c['soc_ball'], 'U2:' + c['dram_ball']
        bs, br, vs, vr = balls.get(sb), balls.get(rb), vias.get(sb), vias.get(rb)
        rs = routed[net]
        ds = [r for r in rs if r['ref'] == 'U1' and r['purpose'] == 'ball_to_via']
        dr = [r for r in rs if r['ref'] == 'U2' and r['purpose'] == 'ball_to_via']
        lk = links[net][0] if len(links[net]) == 1 else None
        layer = lk.get('layer') if lk else None
        identities = bool(bs and br and vs and vr and all(v['net'] == net for v in (bs, br, vs, vr)))
        local_ok = bool(identities and len(ds) == len(dr) == 1 and
            ds[0]['layer'] == dr[0]['layer'] == 'L1' and
            ds[0]['id'] == sb and dr[0]['id'] == rb and
            ds[0]['points'] == [[bs['x'], bs['y']], vs['xy']] and
            dr[0]['points'] == [[br['x'], br['y']], vr['xy']])
        path_ok = bool(local_ok and lk and lk['ref'] == 'U1_TO_U2' and
            lk['id'] == net and lk['soc_ball'] == c['soc_ball'] and lk['dram_ball'] == c['dram_ball'] and
            lk['ball'] == c['soc_ball'] + '->' + c['dram_ball'] and layer in ('L3', 'L8') and
            len(lk['points']) >= 2 and lk['points'][0] == vs['xy'] and lk['points'][-1] == vr['xy'] and
            all(len(p) == 2 and all(math.isfinite(z) for z in p) for p in lk['points']) and
            all(math.dist(a, b) > 0 for a, b in zip(lk['points'], lk['points'][1:])))
        ports_ok = bool(path_ok and all(set(v['functional_layers']) == {'L1', layer} and
            {'L1', layer}.issubset(v['retained_annuli']) for v in (vs, vr)))
        decl = declared[net][0] if len(declared[net]) == 1 else {}
        manifest_ok = all(decl.get(k) == c[k] for k in IDENTITY_FIELDS) and decl.get('layer') == layer
        check('source_identity_and_manifest:' + net, identities and manifest_ok)
        check('both_exact_L1_dogbones:' + net, local_ok)
        check('direct_via_to_via_path_and_ports:' + net, path_ok and ports_ok)
        by_layer = defaultdict(float)
        for r in ds + dr + ([lk] if lk else []):
            by_layer[r['layer']] += sum(math.dist(a, b) for a, b in zip(r['points'], r['points'][1:]))
        total = sum(by_layer.values())
        check('declared_planar_length_matches:' + net,
              isinstance(decl.get('complete_planar_length_mm'), (int, float)) and
              abs(decl['complete_planar_length_mm'] - total) < 1e-7)
        records.append(dict(c, layer=layer, local_dogbones_verified=local_ok,
            candidate_path_exists=bool(path_ok and ports_ok),
            actual_via_sequence=[sb, rb] if ports_ok else [],
            actual_layer_sequence=['L1', layer, 'L1'] if ports_ok else [],
            actual_via_count=2 if ports_ok else None,
            actual_layer_changes=2 if ports_ok else None,
            planar_length_by_layer_mm=dict(by_layer), candidate_planar_length_mm=total,
            board_delay_ps='UNQUALIFIED', dram_package_delay_ps='UNAVAILABLE',
            accepted_DDR_connection=False))
    bynet = {r['net']: r for r in records}
    pairs = []
    for stem in PAIRS:
        pair = [bynet[stem + s] for s in ('_P', '_N')]
        same = pair[0]['layer'] == pair[1]['layer'] and pair[0]['layer'] in ('L3', 'L8')
        equal = all(p['actual_via_count'] == p['actual_layer_changes'] == 2 for p in pair)
        check('differential_pair_common_layer_and_two_transitions:' + stem, same and equal)
        pairs.append(dict(pair=stem, candidate_paths_exist=all(p['candidate_path_exists'] for p in pair),
            same_layer=same, layer=pair[0]['layer'] if same else None,
            actual_vias=[p['actual_via_count'] for p in pair],
            actual_layer_changes=[p['actual_layer_changes'] for p in pair], equal_actual_vias=equal,
            planar_lengths_mm=[p['candidate_planar_length_mm'] for p in pair],
            planar_length_skew_mm=abs(pair[0]['candidate_planar_length_mm'] - pair[1]['candidate_planar_length_mm']),
            soc_package_lengths_um=[p['soc_package_trace_um'] for p in pair],
            dram_package_delays='UNAVAILABLE', timing_match_qualified=False, accepted_DDR_pair=False))
    groups = defaultdict(list)
    for p in records:
        groups[p['sink_group']].append(p)
    group_layers = {k: sorted({p['layer'] for p in ps if p['layer']}) for k, ps in groups.items()}
    check('mixed_byte_layer_relaxation_declared', all(len(layers) == 1 for group, layers in group_layers.items()
          if 'BYTE' in group) or j['search'].get('common_byte_layer_engineering_target_relaxed') is True)
    return dict(status='PASS_SOURCE_IDENTITY_AND_PATH_STRUCTURE' if not errors else 'FAIL_STRUCTURE',
                checks=checks, errors=errors, pernet=records, pairs=pairs, group_layers=group_layers,
                source_provenance=dict(frozen_hashes_preserved=True, whole_source_hash_changes=hash_changes,
                                       semantic_reconciliation=reconciled),
                candidate_paths=sum(p['candidate_path_exists'] for p in records), accepted_DDR_links=0,
                native_audit_status='NOT_RUN', timing_match_qualified=False)


def run(candidate, baseline_path):
    raw = candidate.read_bytes()
    j = json.loads(raw)
    baseline = json.loads(baseline_path.read_text())
    structure = inspect_structure(j, baseline)
    print(json.dumps({'stage': 'structure', 'candidate_paths': structure['candidate_paths'],
                      'error_count': len(structure['errors']), 'errors': structure['errors']}), flush=True)
    geometry, tracks = analytic.audit(j)
    print(json.dumps({'stage': 'geometry', 'checks': geometry['checks'],
                      'failure_count': geometry['failure_count']}), flush=True)
    # Use contract-derived identities and actual route layers, not copied summary metadata.
    screen_input = copy.deepcopy(j)
    screen_input['pernet'] = structure['pernet']
    spacing = analytic.spacing(screen_input, tracks)
    spacing['qualification'] += (' Joint links include the former SoC escape region; the old separate '
        'K230 local DDR-fanout scope is empty. Mixed L3/L8 byte allocation is an explicitly relaxed '
        'engineering target; layer-dependent delay matching and continuous return paths remain unresolved.')
    ids = {t['id']: t['net'] for t in tracks}
    ids.update({'land:' + b['id']: b['net'] for b in j['balls']})
    ids.update({'via:' + v['id']: v['net'] for v in j['vias']})
    ids.update({'hole:' + v['id']: v['net'] for v in j['vias']})
    implicated = set()
    conflict_pairs = set()
    for f in geometry['failures']:
        nets = [ids.get(f['a']), ids.get(f['b'])]
        implicated.update(n for n in nets if n)
        conflict_pairs.add(tuple(sorted(str(n) for n in nets)))
    paths_ok = structure['candidate_paths'] == 65 and not structure['errors']
    nominal_pass = paths_ok and geometry['failure_count'] == 0
    for p in structure['pernet']:
        p['implicated_in_analytic_geometry_failure'] = p['net'] in implicated
        p['nominal_analytic_candidate_verified'] = bool(nominal_pass)
    return dict(status='NOMINAL_ANALYTIC_CANDIDATE_ONLY_AWAITING_NATIVE_AUDIT' if nominal_pass else
                'REJECTED_CANDIDATE_GEOMETRY_OR_STRUCTURE', candidate_path=str(candidate.resolve()),
        candidate_sha256=hashlib.sha256(raw).hexdigest(), baseline_path=str(baseline_path.resolve()),
        baseline_sha256=sha(baseline_path), analytic_audit_source_sha256=sha(OLD / 'audit_links.py'),
        audit_source_sha256=sha(Path(__file__)), input_unchanged_after_audit=sha(candidate) == hashlib.sha256(raw).hexdigest(),
        router_reported_edge_events=j['search'].get('conflicting_grid_edge_events'),
        summary=dict(candidate_paths=structure['candidate_paths'], structural_error_count=len(structure['errors']),
            analytic_geometry_checks=geometry['checks'], analytic_geometry_failures=geometry['failure_count'],
            analytic_conflicting_net_pairs=len(conflict_pairs), analytic_implicated_nets=sorted(implicated),
            nominal_conflict_free_candidate_links=65 if nominal_pass else 0, accepted_DDR_links=0,
            native_audit_status='NOT_RUN', production_ready=False),
        structure=structure, geometry=geometry, spacing=spacing,
        limitations=list(dict.fromkeys(j.get('limitations', []) + [
            'Candidate path existence does not mean an electrically valid or accepted DDR connection.',
            'Accepted_DDR_links remains zero: this tool does not run or certify native CAD audits.',
            'Analytic clearance uses nominal circular pads, nominal drill holes and a common trace width; no fabrication tolerances qualified.',
            'No coupling, impedance, plane/reference copper, return-current, crosstalk, SI/PI, timing or training qualification.',
            'Differential pairs retain common routing layers and two actual transitions; coupled routing and delay/length matching are not qualified.',
            'Byte-common-layer is a relaxed engineering target; mixed L3/L8 propagation delay needs stack-aware matching.',
            'SoC package lengths are retained by exact source-ball identity; DRAM package delays unavailable.',
            'Three RAM bias balls remain unrouted; power/ground dogbones are plane ports rather than completed PDN.',
            'Other components, castellations, complete board geometry, top-only assembly and enclosed 75–85 C thermal operation are not validated.'
        ])))


def write_csv(path, rows):
    with path.open('w', newline='') as f:
        fields = list(dict.fromkeys(k for row in rows for k in row))
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows({k: json.dumps(v) if isinstance(v, (dict, list)) else v for k, v in row.items()} for row in rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('candidate', type=Path)
    parser.add_argument('--baseline', type=Path, default=OLD / 'actual-links.json')
    parser.add_argument('--output-dir', type=Path)
    args = parser.parse_args()
    output = args.output_dir or HERE / 'results' / args.candidate.resolve().parent.name
    output.mkdir(parents=True, exist_ok=True)
    result = run(args.candidate, args.baseline)
    (output / 'joint-link-audit.json').write_text(json.dumps(result, indent=2) + '\n')
    for name, rows in [('connectivity-pernet', result['structure']['pernet']),
                       ('pair-audit', result['structure']['pairs']),
                       ('structure-checks', result['structure']['checks']),
                       ('geometry-failures', result['geometry']['failures']),
                       ('spacing', result['spacing']['records'])]:
        write_csv(output / (name + '.csv'), rows)
    print(json.dumps({'status': result['status'], 'output_dir': str(output),
                      'summary': result['summary'], 'pair_audit': result['structure']['pairs'],
                      'spacing': result['spacing']['summary_by_scope']}, indent=2), flush=True)
    return 0 if result['summary']['nominal_conflict_free_candidate_links'] == 65 else 2


if __name__ == '__main__':
    sys.exit(main())
