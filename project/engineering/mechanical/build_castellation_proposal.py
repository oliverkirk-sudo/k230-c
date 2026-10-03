#!/usr/bin/env python3
"""Reproduce a nominal module-edge proposal; this is not a fabrication release.

Use /usr/bin/python3 (KiCad 9 pcbnew). Only files in cad/castellation-proposal
and castellation-* mechanical reports are written. No integrated CAD is read or
changed. Full source documents are external to the distributable project.
"""
import csv
import hashlib
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon, Rectangle
import pcbnew

ROOT = Path(__file__).resolve().parents[2]
MECH = ROOT / 'engineering/mechanical'
OUT = ROOT / 'cad/castellation-proposal'
LIB = OUT / 'CMK230_Castellation_Proposal.pretty'
NAME = 'CMK230_38x38_140P1_D0.50_Oval0.80x1.80_PROCESS_UNQUALIFIED'
SOURCE = ROOT / 'data/mating_land_coordinates.csv'
P = dict(board_mm=38.0, hole_mm=0.5, pad_transverse_mm=0.8,
         pad_normal_mm=1.8, mask_expansion_mm=0.05,
         mask_registration_budget_mm=0.0762,
         component_to_mask_clearance_mm=0.25)
# The last two fields are engineering budgets, not vendor accepted tolerances.


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def capsule(w, length, steps=512):
    """CCW polygon, local x tangential and y outward normal."""
    r = w / 2
    a = (length - w) / 2
    return [(r * math.cos(t), a + r * math.sin(t))
            for t in [i * math.pi / steps for i in range(steps + 1)]] + [
        (r * math.cos(t), -a + r * math.sin(t))
        for t in [math.pi + i * math.pi / steps for i in range(steps + 1)]]


def circle(d, x=0, y=0, steps=1024):
    return [(x + d/2 * math.cos(i*2*math.pi/steps),
             y + d/2 * math.sin(i*2*math.pi/steps)) for i in range(steps)]


def clip(poly, axis, bound, keep_less):
    if not poly:
        return []
    out = []
    def inside(p):
        return p[axis] <= bound + 1e-12 if keep_less else p[axis] >= bound - 1e-12
    for a, b in zip(poly, poly[1:] + poly[:1]):
        ina, inb = inside(a), inside(b)
        if ina:
            out.append(a)
        if ina != inb:
            t = (bound-a[axis])/(b[axis]-a[axis])
            out.append((a[0]+t*(b[0]-a[0]), a[1]+t*(b[1]-a[1])))
    return out


def area(poly):
    return abs(sum(a[0]*b[1]-b[0]*a[1]
                   for a, b in zip(poly, poly[1:]+poly[:1]))) / 2 if poly else 0


def overlap(dx=0, dy=0, profile=0, hole=0.5, drill_x=0, drill_y=0):
    # Actual carrier SHAPE=ROUND with unequal dimensions is an obround, as in
    # cad/CMK230.pretty/CMK230_Carrier_Mating_ONLY.kicad_mod. Integrate exact
    # cross-section functions; no rectangular carrier-envelope substitution.
    y = np.linspace(-.9, min(profile,.9), 200001)
    def half_width(y, w, length, center_y=0):
        q = np.maximum(np.abs(y-center_y)-(length-w)/2,0)
        return np.sqrt(np.maximum((w/2)**2-q*q,0))
    mc=half_width(y,.8,1.8)
    cc=half_width(y,.559994,1.599999,dy-.254)
    left=np.maximum(-mc,dx-cc);right=np.minimum(mc,dx+cc)
    base=np.maximum(right-left,0)
    q=y-drill_y
    hr=np.sqrt(np.maximum((hole/2)**2-q*q,0))
    removed=np.maximum(np.minimum(right,drill_x+hr)-np.maximum(left,drill_x-hr),0)
    removed[np.abs(q)>hole/2]=0
    return float(np.trapezoid(base-removed,y))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    LIB.mkdir(exist_ok=True)
    rows = list(csv.DictReader(SOURCE.open()))
    assert len(rows) == 140 and sorted(int(r['pin']) for r in rows) == list(range(1,141))
    contacts = []
    for r in rows:
        x, y = float(r['x_mm']), float(r['y_mm'])
        if abs(y) > abs(x):
            side = 'north' if y < 0 else 'south'
            mx, my = round(x), math.copysign(19, y)
            w, h = .8, 1.8
            along = x
        else:
            side = 'west' if x < 0 else 'east'
            mx, my = math.copysign(19, x), round(y)
            w, h = 1.8, .8
            along = y
        contacts.append(dict(pin=int(r['pin']), side=side, module_center_mm=[mx,my],
                             carrier_center_mm=[x,y], carrier_rotation_deg=float(r['rotation_deg']),
                             carrier_local_size_mm=[float(r['pad_x_mm']),float(r['pad_y_mm'])],
                             module_copper_size_xy_mm=[w,h],
                             source_along_rounding_error_mm=round(along-round(along),9)))
    for side in ['north','south','east','west']:
        sr = [r for r in contacts if r['side']==side]
        assert len(sr)==35
        axis = 0 if side in ['north','south'] else 1
        assert sorted(r['module_center_mm'][axis] for r in sr)==list(range(-17,18))

    # One footprint with intentional Edge.Cuts and plated through-hole geometry.
    # The component is an editable manufacturing proposal, not the carrier land.
    footprint = pcbnew.FOOTPRINT(None)
    footprint.SetFPID(pcbnew.LIB_ID('CMK230_Castellation_Proposal', NAME))
    footprint.SetReference('EDGE_PROPOSAL')
    footprint.SetValue('UNQUALIFIED_FACTORY_PROCESS')
    footprint.SetLibDescription('New module fabrication proposal; 140 PTH castellations. No factory acceptance. Carrier row is +/-18.746 mm; drill row +/-19 mm.')
    for txt, y in [(footprint.Reference(),-21),(footprint.Value(),21)]:
        txt.SetPosition(pcbnew.VECTOR2I(0,pcbnew.FromMM(y)))
        txt.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(.8),pcbnew.FromMM(.8)))
        txt.SetTextThickness(pcbnew.FromMM(.12))
        txt.SetLayer(pcbnew.Dwgs_User)
    for c in contacts:
        pad = pcbnew.PAD(footprint)
        pad.SetNumber(str(c['pin']))
        pad.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
        pad.SetProperty(pcbnew.PAD_PROP_CASTELLATED)
        pad.SetShape(pcbnew.PAD_SHAPE_OVAL)
        pad.SetSize(pcbnew.VECTOR2I(*[pcbnew.FromMM(v) for v in c['module_copper_size_xy_mm']]))
        pad.SetDrillSize(pcbnew.VECTOR2I(pcbnew.FromMM(.5),pcbnew.FromMM(.5)))
        pad.SetPosition(pcbnew.VECTOR2I(*[pcbnew.FromMM(v) for v in c['module_center_mm']]))
        layers = pcbnew.LSET.AllCuMask()
        layers.AddLayer(pcbnew.F_Mask)
        layers.AddLayer(pcbnew.B_Mask)
        pad.SetLayerSet(layers)
        pad.SetLocalSolderMaskMargin(pcbnew.FromMM(.05))
        footprint.Add(pad)
    def rect(x, y, layer, width=.05):
        pts = [(-x,-y),(x,-y),(x,y),(-x,y)]
        for a,b in zip(pts,pts[1:]+pts[:1]):
            seg=pcbnew.PCB_SHAPE(footprint)
            seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
            seg.SetStart(pcbnew.VECTOR2I(*[pcbnew.FromMM(v) for v in a]))
            seg.SetEnd(pcbnew.VECTOR2I(*[pcbnew.FromMM(v) for v in b]))
            seg.SetLayer(layer);seg.SetWidth(pcbnew.FromMM(width));footprint.Add(seg)
    rect(19,19,pcbnew.Edge_Cuts)
    unrounded_band = .9+.05+P['mask_registration_budget_mm']+P['component_to_mask_clearance_mm']
    band = math.ceil(unrounded_band*10-1e-9)/10
    rect(19-band,19-band,pcbnew.Dwgs_User)
    pcbnew.PCB_IO_MGR.PluginFind(pcbnew.PCB_IO_MGR.KICAD_SEXP).FootprintSave(str(LIB),footprint)
    board=pcbnew.BOARD()
    board.SetCopperLayerCount(8)
    # Thickness is an explicit proposal, without invented dielectric definitions.
    board.GetDesignSettings().SetBoardThickness(pcbnew.FromMM(1.2))
    fp = pcbnew.FootprintLoad(str(LIB),NAME)
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(50),pcbnew.FromMM(50)))
    board.Add(fp)
    pcbnew.SaveBoard(str(OUT/'CMK230_Castellation_NOMINAL_PROPOSAL.kicad_pcb'),board)
    (OUT/'fp-lib-table').write_text('(fp_lib_table\n (lib (name "CMK230_Castellation_Proposal")(type "KiCad")(uri "${KIPRJMOD}/CMK230_Castellation_Proposal.pretty")(options "")(descr "PROCESS UNQUALIFIED module edge proposal"))\n)\n')

    # A conservative rectangle exists inside every oval; unlike sampled overlap
    # corners, its interval-intersection area is a proof for continuous offsets.
    # At local normal [-.50,-.25], pad width is .8 and nominal hole is absent.
    # Use only the carrier oval's inscribed straight rectangle, not its box.
    def interval_min(a,b,c,d,budget):
        return max(0,min(min(b,d-budget)-max(a,c-budget),min(b,d+budget)-max(a,c+budget)))
    sensitivities=[]
    for b in [0,.05,.10,.15,.20,.25]:
        lower_width=interval_min(-.4,.4,-.559994/2,.559994/2,b)
        lower_depth=interval_min(-.5,-.25,-.254-(1.599999-.559994)/2,-.254+(1.599999-.559994)/2,b)
        corner_values=[overlap(x,y) for x in [-b,0,b] for y in [-b,0,b]]
        sensitivities.append(dict(effective_relative_offset_each_axis_mm=b,
                                  nominal_shape_sample_min_overlap_mm2=round(min(corner_values),8),
                                  sampling_is_not_a_global_worst_case_proof=True,
                                  analytic_guaranteed_inscribed_rectangle_mm2=round(lower_width*lower_depth,8),
                                  assumptions='Pure relative translation only, nominal pad/hole/profile and full wettable copper. Carrier/module positional error and placement translation must be included in the budget. Angular error, pad-size, mask, coplanarity and solder coverage are not qualified.'))
    # Broader direct tolerance sensitivity: protect [-.50,-.40] from a .58 hole
    # whose center can move .075 inward; trim at -.20 still leaves this rectangle.
    broad_b=.15
    broad_lower=interval_min(-.4,.4,-.559994/2,.559994/2,broad_b)*.10
    # Conditional joint pose proof. Rotate the whole module about its center;
    # bound displacement of every contact center by 2 R sin(theta/2). Erode an
    # inscribed carrier rectangle by the analogous local rotational bound.
    # This is a deliberately requested sensitivity case, not an assembly spec.
    rotation_deg=.1
    translation_mm=.1
    theta=math.radians(rotation_deg)
    center_radius=math.hypot(19,17)
    translation_projected=translation_mm*(math.cos(theta)+math.sin(theta))
    center_budget=translation_projected+2*center_radius*math.sin(theta/2)+.000004
    cw=.559994/2
    ch=(1.599999-.559994)/2
    local_erosion=2*math.hypot(cw,ch)*math.sin(theta/2)
    pose_width=interval_min(-.4,.4,-cw+local_erosion,cw-local_erosion,center_budget)
    pose_depth=interval_min(-.5,-.25,-.254-ch+local_erosion,-.254+ch-local_erosion,center_budget)
    data=dict(status='REVIEWABLE_NOMINAL_PROPOSAL_FACTORY_AND_ASSEMBLY_UNQUALIFIED',
        source_coordinates=str(SOURCE.relative_to(ROOT)),source_coordinates_sha256=sha(SOURCE),
        parameters=P, parameters_not_claimed_as_factory_tolerances=['mask_registration_budget_mm','component_to_mask_clearance_mm'],
        hole_size_definition='0.50 mm is the requested nominal FINISHED plated opening before edge routing. KiCad drill attribute is the requested nominal, not a specification of the physical production drill tool. Factory compensation and final acceptance remain open.',
        source_evidence_files=['castellation-fab-source-review.json','core-stackup-process-proposal.json','original-step-edge-evidence.json'],
        module_outline_mm=[38,38],normal_module_drill_centers_abs_mm=19,
        authoritative_carrier_normal_centers_abs_mm=18.746,
        carrier_land_shape='Obround: source-interface/CM-K230.pcbdoc SHAPE=ROUND, unequal XSIZE/YSIZE; existing converted carrier footprint uses smd oval',
        carrier_source_sha256=sha(ROOT/'source-interface/CM-K230.pcbdoc'),
        intended_normal_center_offset_mm=.254,
        along_edge_centers_mm=list(range(-17,18)),contact_count=140,
        maximum_source_rounding_error_mm=max(abs(c['source_along_rounding_error_mm']) for c in contacts),
        source_rounding_note='Microscopic source conversion noise is normalized to the explicitly specified 1 mm pitch; carrier source coordinates are retained for proof.',
        nominal_checks=dict(annular_ring_transverse_mm=.15,annular_ring_inward_centerline_mm=.65,
             copper_gap_mm=.2,hole_edge_gap_mm=.5,mask_opening_transverse_mm=.9,mask_opening_normal_mm=1.9,
             mask_web_mm=.1,corner_to_nearest_hole_center_mm=2,corner_to_nearest_copper_edge_mm=1.6,
             carrier_land_world_transverse_mm=.559994,carrier_land_world_normal_mm=1.599999,
             carrier_inward_edge_coordinate_mm=17.9460005,carrier_outward_edge_coordinate_mm=19.5459995,
             module_inward_copper_coordinate_mm=18.1,carrier_to_module_inboard_tip_margin_mm=.1539995,
             nominal_copper_overlap_area_per_contact_mm2=round(overlap(),8)),
        corner_panelization_gate='1.6 mm nominal bare edge near each corner is not an approved tab or clamp provision; four populated edges need panel retention/routing review.',
        soldermask_assessment='0.05 mm expansion leaves exactly 0.10 mm nominal web, the PCBWay dedicated-page minimum. Any process requirement for a larger web, larger expansion or opening-size allowance changes this proposal. Green LPI and preserved individual bridges are requested, not accepted.',
        copper_layers='Same PTH pad and plated barrel on all eight copper layers. Every internal plane needs a net-specific clearance; retain unused annuli for barrel support.',
        paste_layers='No module-side paste on castellations. Carrier stencil and solder volume must be qualified separately for module mounting.',
        tolerance_status='No accepted fabricator-specific tolerance stack is available. Published generic capabilities from different services are not combined into a fictitious qualified process.',
        published_generic_tolerance_stress_case=dict(source='https://www.pcbway.com/capabilities.html',
             outline_size_tolerance_mm=.2,hole_position_tolerance_mm=.075,finished_hole_diameter_tolerance_mm=.08,
             interpretation='The size tolerance does not establish local drill-to-route registration. Treating +/-0.2 as an independent edge-location bound is an intentionally conservative stress calculation, not the vendor definition.',
             assumed_independent_edge_plus_drill_error_mm=.275,minimum_radius_mm=.21,
             minimum_retained_radial_depth_mm=-.065,
             conclusion='Generic tolerance figures cannot guarantee the profile intersects every hole; a joint drill/route registration requirement is mandatory.',
             transverse_ring_at_max_hole_and_position_before_etch_mm=.035),
        required_tolerance_relationships=dict(retained_depth='h_min = D_min/2 - E_drill_to_route for edge-centered holes',
             open_hole='E_drill_to_route < D_min/2',
             minimum_ring='a_min = (W_min - D_max)/2 - E_drill_to_copper',
             mask_bridge='web_min = pitch_min - opening_width_max - differential_opening_position_error',
             requested_values='To be accepted together by one selected factory. No accepted numeric limits are invented here.'),
        component_reservation=dict(depth_from_nominal_edge_mm=band,
             formula='0.90 inward copper + 0.05 mask expansion + 0.0762 published PCBWay standard mask-offset budget + 0.25 engineering component-to-mask clearance = 1.2762 mm, rounded outward to 1.30 mm; this mixed-source engineering budget is not acceptance of a factory process',
             central_square_mm=38-2*band,central_square_area_mm2=(38-2*band)**2,
             delta_against_historical_2mm_band_mm2=(38-2*band)**2-34**2,
             status='Conditional geometric reservation. Do not silently replace the committed 2 mm baseline or count the gain as routed space.',
             component_rule='All top-side component body and exposed solder-land extents stay inside this central square, or require an explicit local clearance analysis. The 0.25 mm is an engineering assembly separation, not a published fab minimum.',
             sensitivities=[dict(mask_registration_budget_mm=r,band_mm=.9+.05+r+.25,area_mm2=(38-2*(.9+.05+r+.25))**2) for r in [0,.05,.075,.10,.20]],
             ordinary_copper_rule='Non-castellation edge copper/planes retain the selected factory profile clearance plus its agreed edge tolerance. Do not extend arbitrary planes to the edge.',
             bottom_rule='No bottom-side components. Bottom castellated lands remain exposed; other bottom conductors must avoid accidental carrier contact. Carrier under-module geometry and standoff are not yet qualified.'),
        overlap_sensitivity=sensitivities,
        angular_error_status='Not included in the translation-only rows; a separate explicitly assumed joint-pose lower bound is provided. Actual assembly acceptance and pad/mask tolerances remain open.',
        joint_pose_sensitivity=dict(assembly_translation_each_global_axis_mm=translation_mm,
             assembly_rotation_about_module_center_deg=rotation_deg,
             assumption_status='Illustrative engineering budget only, not a vendor placement guarantee',
             largest_contact_center_radius_bound_mm=center_radius,
             global_translation_projected_into_rotated_axes_bound_mm=translation_projected,
             center_translation_plus_rotation_bound_each_axis_mm=center_budget,
             carrier_inscribed_rectangle_rotation_erosion_each_edge_mm=local_erosion,
             guaranteed_nominal_geometric_overlap_lower_bound_mm2=pose_width*pose_depth,
             method='Use exact carrier straight rectangle, erode every side by 2*local_radius*sin(theta/2), then intersect its translated bounding intervals with the retained module rectangle [-.4,.4] x [-.5,-.25]. Contact-center rotation is conservatively bounded by 2*hypot(19,17)*sin(theta/2), plus translation_per_global_axis*(cos(theta)+sin(theta)) and source-rounding noise.',
             limitations='Nominal dimensions/profile/drill and full exposed copper only. Hole/copper manufacturing errors, mask, solder, board warpage and real placement capability remain unqualified.'),
        broader_tolerance_inscribed_rectangle=dict(effective_relative_axis_budget_mm=.15,
             finished_hole_max_mm=.58,drill_inward_error_max_mm=.075,inward_profile_error_mm=.20,
             guaranteed_geometric_overlap_rectangle_mm2=round(broad_lower,8),
             restrictions='Proof uses unshrunk .8 copper and nominal carrier land dimensions, ignoring mask/etch. Positive remaining land overlap does not rescue a missed or damaged half-hole.'),
        missing_mating_tolerances=['Carrier pad size/position and soldermask opening tolerances','Module-to-carrier placement and angular error','Carrier stencil, paste volume, wetting and post-reflow stand-off','Board flatness/warpage at reflow and operating temperature','Local drill-to-route and drill-to-copper registration for the chosen castellation process'],
        contacts=contacts)
    (MECH/'castellation-proposal-dimensional-proof.json').write_text(json.dumps(data,indent=2)+'\n')
    with (MECH/'castellation-proposal-contacts.csv').open('w') as f:
        w=csv.writer(f);w.writerow(['pin','side','module_x_mm','module_y_mm','carrier_x_mm','carrier_y_mm','hole_mm','copper_x_mm','copper_y_mm'])
        for c in contacts:w.writerow([c['pin'],c['side'],*c['module_center_mm'],*c['carrier_center_mm'],.5,*c['module_copper_size_xy_mm']])

    fig, axes=plt.subplots(1,3,figsize=(15,5.3),gridspec_kw={'width_ratios':[1.15,1,1]})
    ax=axes[0]
    ax.add_patch(Rectangle((-19,-19),38,38,fill=False,lw=1.4,color='#222'))
    ax.add_patch(Rectangle((-19+band,-19+band),38-2*band,38-2*band,facecolor='#eaf2e4',edgecolor='#508147',lw=.9))
    for c in contacts:
        x,y=c['module_center_mm'];w,h=c['module_copper_size_xy_mm']
        # Rectangles show reserved extent, circles locate drills; detailed true
        # curved copper shape is in the canonical second panel.
        ax.add_patch(Rectangle((x-w/2,y-h/2),w,h,facecolor='#b77721',edgecolor='none',alpha=.65,clip_on=True))
    ax.set_xlim(-19,19);ax.set_ylim(19,-19);ax.set_aspect('equal')
    ax.set_title('140 contacts, fixed 1 mm pitch\n38 × 38 mm module proposal',fontsize=10)
    ax.text(0,0,'35.4 × 35.4 mm\nconditional component region\n\n1.30 mm derived reservation\nprocess acceptance pending',ha='center',va='center',fontsize=10)
    ax.set_xlabel('x (mm)');ax.set_ylabel('y (mm)')
    ax=axes[1]
    ax.add_patch(Polygon([(x,y-.254) for x,y in capsule(.559994,1.599999)],facecolor='#608eae',alpha=.45,label='Carrier oval land'))
    ax.add_patch(Polygon(clip(capsule(.9,1.9),1,0,True),facecolor='#73a861',alpha=.25,label='Module mask opening'))
    ax.add_patch(Polygon(clip(capsule(.8,1.8),1,0,True),facecolor='#bd802f',alpha=.8,label='Module copper'))
    ax.add_patch(Polygon(clip(circle(.5),1,0,True),facecolor='white',edgecolor='#222',lw=.6,label='Plated half-hole void'))
    ax.axhline(0,color='#222',lw=1);ax.axhline(-band,color='#508147',linestyle='--',lw=1)
    ax.annotate('Nominal profile',(0,0),(.48,.10),fontsize=8,arrowprops={'arrowstyle':'-'})
    ax.text(.45,-1.24,'Component boundary',fontsize=8,va='bottom')
    ax.set_xlim(-.8,1.15);ax.set_ylim(-1.5,.7);ax.set_aspect('equal')
    ax.set_xlabel('Along edge (mm)');ax.set_ylabel('Outward normal (mm)')
    ax.set_title('Carrier and module geometry differ\n0.254 mm normal center offset',fontsize=10)
    ax.legend(fontsize=7,loc='upper right',framealpha=.9)
    ax=axes[2]
    xs=[x['effective_relative_offset_each_axis_mm'] for x in sensitivities]
    ax.plot(xs,[x['nominal_shape_sample_min_overlap_mm2'] for x in sensitivities],'o-',label='Nominal-shape sample minimum')
    ax.plot(xs,[x['analytic_guaranteed_inscribed_rectangle_mm2'] for x in sensitivities],'s-',label='Continuous-offset proven lower bound')
    ax.set_xlabel('Effective relative error per axis (mm)');ax.set_ylabel('Copper overlap area (mm²)')
    ax.set_title('Pure-translation mating sensitivity\nassembly tolerance remains unqualified',fontsize=10)
    ax.grid(alpha=.2);ax.legend(fontsize=7,loc='lower left')
    fig.suptitle('CASTELLATION PROPOSAL • NOMINAL GEOMETRY ONLY • NO FABRICATION RELEASE',fontsize=12,fontweight='bold')
    fig.tight_layout(rect=[0,0,1,.94])
    fig.savefig(MECH/'castellation-proposal-profile.svg')
    fig.savefig(MECH/'castellation-proposal-profile.png',dpi=180)
    print(json.dumps({'contacts':len(contacts),'nominal_overlap_mm2':overlap(),'conditional_band_mm':band,'conditional_interior_mm2':(38-2*band)**2,'footprint':str(LIB/(NAME+'.kicad_mod'))},indent=2))


if __name__ == '__main__':
    main()
