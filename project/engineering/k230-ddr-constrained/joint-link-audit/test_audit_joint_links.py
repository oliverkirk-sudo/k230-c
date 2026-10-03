"""Mutation regressions; no source inputs or CAD are written."""
import copy
import json
import unittest
from pathlib import Path
import audit_joint_links as audit


class JointAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.candidate = json.loads((audit.HERE.parent / 'link-pair-preserved-flex/best-search-candidate.json').read_text())
        cls.baseline = json.loads((audit.OLD / 'actual-links.json').read_text())

    def inspect(self, candidate=None):
        return audit.inspect_structure(candidate or self.candidate, self.baseline)

    def test_current_candidate_structure(self):
        result = self.inspect()
        self.assertEqual(result['candidate_paths'], 65)
        self.assertEqual(result['errors'], [])
        self.assertEqual(result['accepted_DDR_links'], 0)
        self.assertTrue(all(p['same_layer'] and p['equal_actual_vias'] for p in result['pairs']))

    def test_corrupt_endpoint_detected(self):
        j = copy.deepcopy(self.candidate)
        r = next(r for r in j['routes'] if r['purpose'] == 'actual_DDR_link')
        r['points'][0][0] += 0.01
        result = self.inspect(j)
        self.assertEqual(result['candidate_paths'], 64)
        self.assertTrue(result['errors'])

    def test_moved_existing_via_detected(self):
        j = copy.deepcopy(self.candidate)
        j['vias'][0]['xy'][0] += 0.01
        self.assertIn('all_502_vias_physical_geometry_preserved',
                      [e['check'] for e in self.inspect(j)['errors']])

    def test_missing_non_DDR_route_detected(self):
        j = copy.deepcopy(self.candidate)
        target = next(r for r in j['routes'] if r['purpose'] == 'via_to_outside_body')
        j['routes'].remove(target)
        self.assertIn('only_65_DDR_exit_tracks_removed_all_other_routes_preserved',
                      [e['check'] for e in self.inspect(j)['errors']])

    def test_missing_functional_port_detected(self):
        j = copy.deepcopy(self.candidate)
        target = next(v for v in j['vias'] if v['id'] == 'U1:Y16')
        target['functional_layers'] = ['L1']
        self.assertEqual(self.inspect(j)['candidate_paths'], 64)

    def test_duplicated_link_detected(self):
        j = copy.deepcopy(self.candidate)
        j['routes'].append(copy.deepcopy(next(r for r in j['routes'] if r['purpose'] == 'actual_DDR_link')))
        self.assertIn('candidate_links_exact_65_source_nets_once',
                      [e['check'] for e in self.inspect(j)['errors']])

    def test_completion_claims_never_grant_acceptance(self):
        j = copy.deepcopy(self.candidate)
        j['summary']['completed_DDR_links'] = 65
        for r in j['pernet']:
            r['complete_ball_to_ball'] = True
        result = self.inspect(j)
        self.assertEqual(result['accepted_DDR_links'], 0)
        self.assertFalse(any(r['accepted_DDR_connection'] for r in result['pernet']))

    def test_split_differential_pair_detected(self):
        j = copy.deepcopy(self.candidate)
        net = 'DDR_DQSA0_P'
        r = next(r for r in j['routes'] if r['purpose'] == 'actual_DDR_link' and r['net'] == net)
        r['layer'] = 'L8'
        next(p for p in j['pernet'] if p['net'] == net)['layer'] = 'L8'
        for via in j['vias']:
            if via['net'] == net:
                via['functional_layers'] = ['L1', 'L8']
        self.assertIn('differential_pair_common_layer_and_two_transitions:DDR_DQSA0',
                      [e['check'] for e in self.inspect(j)['errors']])

    def test_analytic_crossing_is_rejected(self):
        j = dict(rules=dict(trace_width=.1016, copper_clearance=.1016,
                           hole_to_other_copper=.1524), balls=[],
                 vias=[dict(id='far', net='far', xy=[10., 10.], pad=.325,
                            hole=.15, retained_annuli=['L3'])],
                 routes=[dict(id='a', net='a', layer='L3', ref='test', purpose='test',
                              points=[[0., 0.], [1., 0.]]),
                         dict(id='b', net='b', layer='L3', ref='test', purpose='test',
                              points=[[.5, -1.], [.5, 1.]])])
        geometry, _ = audit.analytic.audit(j)
        self.assertEqual(geometry['failure_count'], 1)
        self.assertEqual(geometry['failures'][0]['kind'], 'trace_to_trace')
        self.assertEqual(geometry['failures'][0]['actual_gap_mm'], -.1016)


if __name__ == '__main__':
    unittest.main()
