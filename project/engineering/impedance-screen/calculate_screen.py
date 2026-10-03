#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
# Copyright The KiCad Developers, see the source URL in NOTICE.md.
# Copyright (C) 2026 CM-K230 redesign contributors (adaptation and screening).
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 2, or (at your option) any later version.
# This program is distributed WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See COPYING-GPL-2.0.txt for the license.
"""Reproducible quasi-static screening, never fabrication dimensions.

Equations are identified in assumptions.json. No solver, network, CAD mutation,
IBIS or proprietary model. All geometric arguments use mm; results use ohms.
The finite-strip impedance equations follow the publicly documented KiCad
implementation (Copyright The KiCad Developers, GPL-2.0-or-later).
"""
import hashlib
import json
import math
from pathlib import Path
from scipy.optimize import brentq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
ZF0 = 376.730313668


def strip_centered(w, plane_gap, t, er):
    """Finite rectangular strip, same dielectric on both sides; KiCad formula."""
    d = plane_gap - t
    assert min(w, plane_gap, t, er) > 0 and d > 0
    if w / d >= 0.35:
        fringe = (2 * plane_gap * math.log((2 * plane_gap - t) / d)
                  - t * math.log(plane_gap**2 / d**2 - 1)) / math.pi
        return ZF0 * d / (4 * math.sqrt(er) * (w + fringe))
    ratio = min(t / w, w / t)
    equivalent_diameter = max(t, w) / 2 * (
        1 + ratio / math.pi * (1 + math.log(4 * math.pi / ratio))
        + 0.236 * ratio**1.65)
    return ZF0 / (2 * math.pi * math.sqrt(er)) * math.log(
        4 * plane_gap / (math.pi * equivalent_diameter))


def strip_offset(w, near=0.109, far=0.130, t=0.035, er=4.525):
    """KiCad image/harmonic construction with correctly defined surface gaps.

    Homogeneous surrogate only; mixed core/prepreg permittivity is bracketed
    separately, never replaced with a claimed measured effective permittivity.
    """
    z_near = strip_centered(w, 2 * near + t, t, er)
    z_far = strip_centered(w, 2 * far + t, t, er)
    return 2 / (1 / z_near + 1 / z_far)


def ni_strip_offset(w, near=0.109, far=0.130, t=0.035, er=4.525):
    """NI Ultiboard 374488E, printed p.6-13, H=near and H1=far."""
    return ((1 - near / (4 * far)) * 80 / math.sqrt(er)
            * math.log(4 * (2 * near + t) / (0.67 * math.pi * (0.8 * w + t))))


def air_impedance(u):
    f = 6 + (2 * math.pi - 6) * math.exp(-(30.666 / u)**0.7528)
    return ZF0 / (2 * math.pi) * math.log(f / u + math.sqrt(1 + (2 / u)**2))


def hj_effective_er(u, er):
    a = (1 + math.log((u**4 + (u / 52)**2) / (u**4 + 0.432)) / 49
         + math.log(1 + (u / 18.1)**3) / 18.7)
    b = 0.564 * ((er - 0.9) / (er + 3))**0.053
    return (er + 1) / 2 + (er - 1) / 2 * (1 + 10 / u)**(-a * b)


def hj_microstrip(w, h=0.1195, t=0.035, er=4.45):
    """Qucs H-J quasi-static single microstrip, finite-thickness correction."""
    u, tn = w / h, t / h
    du_air = 0 if t == 0 else tn / math.pi * math.log(
        1 + 4 * math.e / tn * math.tanh(math.sqrt(6.517 * u))**2)
    du_mixed = du_air / 2 * (1 + 1 / math.cosh(math.sqrt(er - 1)))
    ur = u + du_mixed
    return air_impedance(ur) / math.sqrt(hj_effective_er(ur, er))


def ni_microstrip(w, h=0.1195, t=0.035, er=4.45):
    """NI Ultiboard printed p.6-9; independent coarse formula check."""
    return 87 / math.sqrt(er + 1.41) * math.log(5.98 * h / (0.8 * w + t))


def strip_diff(w, gap, se_model=strip_offset, **kwargs):
    """NI user-defined-Z0 coupling heuristic, not a multilayer field solution."""
    b = kwargs.get('near', 0.109) + kwargs.get('far', 0.130) + kwargs.get('t', 0.035)
    return 2 * se_model(w, **kwargs) * (1 - 0.347 * math.exp(-2.9 * gap / b))


def micro_diff(w, gap, se_model=hj_microstrip, **kwargs):
    """NI user-defined-Z0 heuristic; H-J substitution is a screening hybrid."""
    h = kwargs.get('h', 0.1195)
    return 2 * se_model(w, **kwargs) * (1 - 0.48 * math.exp(-0.96 * gap / h))


def solve_width(fn, target):
    return brentq(lambda w: fn(w) - target, 0.005, 0.8, xtol=1e-12)


def r(x):
    return round(float(x), 8)


def span(values):
    values = list(values)
    return [r(min(values)), r(max(values))]


def main():
    w = gap = 0.1016
    out = {
        'status': 'ANALYTICAL_SCREEN_ONLY_NOT_MANUFACTURING_OR_SI_APPROVAL',
        'units': {'length': 'mm', 'impedance': 'ohm'},
        'baseline': {
            'L3': {'width': w, 'pair_gap': gap,
                   'single_KiCad_offset_homogeneous_surrogate': r(strip_offset(w)),
                   'single_NI_offset_homogeneous_surrogate': r(ni_strip_offset(w)),
                   'diff_NI_factor_KiCad_Z0': r(strip_diff(w, gap)),
                   'diff_NI_offset': r(strip_diff(w, gap, ni_strip_offset)),
                   'isolated_twice_Z0': r(2 * strip_offset(w))},
            'L8_uncoated': {'width': w, 'pair_gap': gap,
                            'single_Hammerstad_Jensen': r(hj_microstrip(w)),
                            'single_NI': r(ni_microstrip(w)),
                            'diff_NI_factor_HJ_Z0': r(micro_diff(w, gap)),
                            'diff_NI': r(micro_diff(w, gap, ni_microstrip))}},
        'single_50ohm_widths': {
            'L3_KiCad_offset': r(solve_width(strip_offset, 50)),
            'L3_NI_offset': r(solve_width(ni_strip_offset, 50)),
            'L8_uncoated_HJ': r(solve_width(hj_microstrip, 50)),
            'L8_uncoated_NI': r(solve_width(ni_microstrip, 50))},
        'L3_catalog_bracket': {},
        'differential_100ohm_width_by_gap': [],
        'four_mil_width_gap_to_100ohm': {},
        'illustrative_sensitivity': [],
        'spacing': [],
    }
    # Both ground planes placed at near or far distance; homogeneous catalog
    # Dk extrema. This geometric envelope includes the physical asymmetric
    # cross section, but approximation error is NOT bounded by this interval.
    extrema = [(h, er) for h in [0.109, 0.130] for er in [4.45, 4.6]]
    out['L3_catalog_bracket'] = {
        'single_4mil_ohm': span(strip_centered(w, 2*h+.035, .035, er) for h, er in extrema),
        'single_50ohm_width_mm': span(solve_width(lambda x: strip_centered(x, 2*h+.035, .035, er), 50) for h, er in extrema),
        'method': 'Moved-plane homogeneous catalog extrema; excludes formula error and fabrication variation',
        'actual_geometry_Dk_only_4mil_ohm': span(strip_offset(w, er=e) for e in [4.45, 4.6]),
        'actual_geometry_Dk_only_50ohm_width_mm': span(solve_width(lambda x:strip_offset(x, er=e),50) for e in [4.45, 4.6])}
    for g in [0.1016, 0.15, 0.2, 0.25, 0.3, 0.4]:
        out['differential_100ohm_width_by_gap'].append({
            'gap_mm': g,
            'L3_width_KiCad_NI_factor': r(solve_width(lambda x:strip_diff(x,g),100)),
            'L3_width_NI_offset': r(solve_width(lambda x:strip_diff(x,g,ni_strip_offset),100)),
            'L8_uncoated_width_HJ_NI_factor': r(solve_width(lambda x:micro_diff(x,g),100)),
            'L8_uncoated_width_NI': r(solve_width(lambda x:micro_diff(x,g,ni_microstrip),100))})
    out['four_mil_width_gap_to_100ohm'] = {
        'L3': None,
        'L3_reason': 'Both nominal formulas have 2*isolated_Z0 below 100 ohm',
        'L8_uncoated_HJ_NI_factor': r(brentq(lambda s:micro_diff(w,s)-100,.001,2)),
        'L8_uncoated_NI': r(brentq(lambda s:micro_diff(w,s,ni_microstrip)-100,.001,2))}
    alternative={'near':.175,'far':.230,'t':.035,'er':4.67}
    out['PW_8L_1P6_70_ALTERNATIVE']={
        'planes_L3':['L2_GND','L4_GND'],
        'planes_L6_conditionally':['L5_GND_REPLACES_POWER','L7_GND'],
        'L3_and_L6_same_mirrored_geometry':True,
        'parameters':alternative,
        'catalog_Dk_values':[4.6,4.74],
        'single_4mil_KiCad':r(strip_offset(w,**alternative)),
        'single_4mil_NI':r(ni_strip_offset(w,**alternative)),
        'single_50ohm_width_KiCad':r(solve_width(lambda x:strip_offset(x,**alternative),50)),
        'single_50ohm_width_NI':r(solve_width(lambda x:ni_strip_offset(x,**alternative),50)),
        'actual_geometry_Dk_only_width50_range':span(solve_width(lambda x:strip_offset(x,near=.175,far=.230,er=e),50) for e in [4.6,4.74]),
        'moved_planes_catalog_bracket_4mil_Z0':span(strip_centered(w,2*h+.035,.035,e) for h in [.175,.230] for e in [4.6,4.74]),
        'moved_planes_catalog_bracket_width50':span(solve_width(lambda x:strip_centered(x,2*h+.035,.035,e),50) for h in [.175,.230] for e in [4.6,4.74]),
        'four_mil_pair_gap_to_100_KiCad_NI_factor':r(brentq(lambda s:strip_diff(w,s,**alternative)-100,.001,2)),
        'four_mil_pair_gap_to_100_NI':r(brentq(lambda s:strip_diff(w,s,ni_strip_offset,**alternative)-100,.001,2)),
        'pair_widths_for_100':[
           {'gap_mm':g,
            'width_KiCad_NI_factor':r(solve_width(lambda x:strip_diff(x,g,**alternative),100)),
            'width_NI':r(solve_width(lambda x:strip_diff(x,g,ni_strip_offset,**alternative),100))}
           for g in [.1016,.15,.2,.25,.3,.4]],
        'L8_outer_stack_unchanged':True,
        'allocation_status':'CONDITIONAL_SCREEN_ONLY; converting L5 power into continuous ground and moving power chiefly to L8 requires a new PDN/current/return-path review',
        'does_not_solve':['full routing','BGA escape and lands','through-via stubs and antipads','top-only assembly','mechanical height','thermal and PDN closure']}
    for er in [4.0, 4.45, 4.525, 4.6, 4.8]:
        out['illustrative_sensitivity'].append({'parameter':'uniform_Dk','value':er,
          'L3_Z0_4mil':r(strip_offset(w,er=er)), 'L8_uncoated_Z0_4mil':r(hj_microstrip(w,er=er)),
          'L3_width_for_50':r(solve_width(lambda x:strip_offset(x,er=er),50)),
          'L8_uncoated_width_for_50':r(solve_width(lambda x:hj_microstrip(x,er=er),50))})
    for t in [.025,.035,.045]:
        out['illustrative_sensitivity'].append({'parameter':'copper_thickness_mm','value':t,
          'L3_Z0_4mil':r(strip_offset(w,t=t)), 'L8_uncoated_Z0_4mil':r(hj_microstrip(w,t=t))})
    for multiplier in [.9,1.0,1.1]:
        out['illustrative_sensitivity'].append({'parameter':'dielectric_gap_multiplier','value':multiplier,
          'L3_Z0_4mil':r(strip_offset(w,near=.109*multiplier,far=.130*multiplier)),
          'L8_uncoated_Z0_4mil':r(hj_microstrip(w,h=.1195*multiplier))})
    for actual_w in [.0916,.1016,.1116]:
        out['illustrative_sensitivity'].append({'parameter':'finished_width_mm','value':actual_w,
          'L3_Z0':r(strip_offset(actual_w)), 'L8_uncoated_Z0':r(hj_microstrip(actual_w))})
    # Screen lower limit for an infinitely thick overcoat with the SAME Dk as
    # substrate. It is deliberately not a real solder-mask-thickness prediction.
    filled=lambda x:hj_microstrip(x,er=1)/math.sqrt(4.45)
    out['L8_conditional_mask_extremes']={
        'condition':'If overcoat Dk is between 1 and 4.45, no adjacent conductor, rectangular geometry',
        'bare_4mil_ohm':r(hj_microstrip(w)),
        'all_space_filled_4mil_ohm':r(filled(w)),
        'bare_width_for_50_mm':r(solve_width(hj_microstrip,50)),
        'all_space_filled_width_for_50_mm':r(solve_width(filled,50)),
        'not_a_tolerance':'Extremely loose conditional limiting-media screen; real mask Dk and thickness unknown'}
    for layer,h,ww in [('L3_4mil',.130,w),('L8_4mil',.1195,w),
                       ('L3_nominal_50ohm',.130,solve_width(strip_offset,50)),
                       ('L8_uncoated_HJ_50ohm',.1195,solve_width(hj_microstrip,50)),
                       ('L3_L6_1p6mm_conditional_50ohm',.230,solve_width(lambda x:strip_offset(x,**alternative),50))]:
        out['spacing'].append({'case':layer,'width_mm':r(ww),'chosen_reference_surface_gap_mm':h,
          'two_H_mm':r(2*h),'three_H_mm':r(3*h),'three_W_mm':r(3*ww),
          'provisional_within_byte_edge_gap_mm':r(max(2*h,3*ww)),
          'provisional_other_group_strobe_clock_supply_vref_edge_gap_mm':r(max(3*h,3*ww)),
          'if_3W_is_center_to_center_then_edge_gap_mm':r(2*ww)})
    # Meaningful algebra/behavior checks, not claims of external calibration.
    assert abs(strip_offset(.1016,near=.13,far=.109)-strip_offset(.1016))<1e-10
    assert abs(strip_offset(.1016,near=.12,far=.12)-strip_centered(.1016,.275,.035,4.525))<1e-10
    assert strip_offset(.12)<strip_offset(.10)
    assert hj_microstrip(.12)<hj_microstrip(.10)
    assert strip_diff(w,.2)>strip_diff(w,.1)
    assert micro_diff(w,.2)>micro_diff(w,.1)
    assert abs(strip_diff(w,10)-2*strip_offset(w))<1e-10
    assert abs(micro_diff(w,10)-2*hj_microstrip(w))<1e-10
    for fn in [strip_offset,ni_strip_offset,hj_microstrip,ni_microstrip]:
        assert abs(fn(solve_width(fn,50))-50)<1e-7
    out['verification']={'assertions_passed':12,'scope':'symmetry, centered limit, monotonicity, weak-coupling limits and inverse solutions; no external field-solver validation'}
    inputs=['engineering/mechanical/core-stackup-process-proposal.json',
            'engineering/routing/DDR_ROUTE_CONTRACT.md']
    out['input_sha256']={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in inputs}
    (HERE/'calculations.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['baseline','single_50ohm_widths','L3_catalog_bracket',
                     'differential_100ohm_width_by_gap','L8_conditional_mask_extremes','PW_8L_1P6_70_ALTERNATIVE','verification']},indent=2))


if __name__ == '__main__':
    main()
