#!/usr/bin/env python3
"""Independent package-side evidence check; never a PCB-land generator."""
from pathlib import Path
import hashlib
import json
import fitz

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
PDF=Path('/workspace/shared/k230-memory-review/thermal-candidates/micron-emmc.pdf')
GRID=ROOT/'engineering/high-temp-candidates/micron-emmc-ball-comparison.json'
rows='A B C D E F G H J K L M N P'.split()

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    page=fitz.open(PDF)[10]
    balls=[];test_pads=[];other=[]
    for drawing in page.get_drawings():
        items=drawing['items'];r=drawing['rect']
        if len(items)!=4 or not all(i[0]=='c' for i in items) or abs(r.width-r.height)>.02:
            continue
        center=((r.x0+r.x1)/2,(r.y0+r.y1)/2)
        if 4<r.width<4.1: balls.append(center)
        elif 3.4<r.width<3.5: test_pads.append(center)
        else:other.append(dict(center=center,diameter_in_pdf_points=r.width))
    assert len(balls)==153 and len(test_pads)==56 and len(other)==1
    xs=sorted(set(round(x,2) for x,y in balls))
    ys=sorted(set(round(y,2) for x,y in balls))
    assert len(xs)==14 and len(ys)==14
    found={rows[min(range(14),key=lambda k:abs(ys[k]-y))]+str(14-min(range(14),key=lambda k:abs(xs[k]-x))) for x,y in balls}
    grid=json.loads(GRID.read_text())
    expected={r['ball'] for r in grid['grid'] if r['physical']}
    assert found==expected
    report={
        'status':'PACKAGE_GEOMETRY_AND_OCCUPANCY_VERIFIED_PCB_LANDS_UNQUALIFIED',
        'exact_part':'MTFC16GAPALBH-AAT',
        'source':{'pdf_local_external_to_project':str(PDF),'url':grid['source_url'],'sha256':sha(PDF),
                  'document':'8GB–128GB e.MMC Automotive, Rev. G 10/18 EN, CCMTD-841846911-10434',
                  'mechanical_pdf_page':11,'figure':5,'signal_map_pdf_page':9,
                  'visual_review':'Actual PDF page11 rendered and inspected, including all dimensions, view orientation and no-ball test-pad note'},
        'package':{'code':'BH','body_nominal_mm':[11.5,13.0],'body_tolerance_each_axis_mm':.1,
                   'overall_height_nominal_mm':1.0,'overall_height_tolerance_mm':.1,
                   'caption_height_1p1_mm_is_upper_limit':True,
                   'ball_protrusion_mm':.214,'ball_protrusion_tolerance_mm':.04,
                   'protrusion_is_not_board_joint_standoff':True,
                   'pitch_mm':[.5,.5],'pitch_tolerance':'No independent +/- pitch tolerance specified; TYP in figure',
                   'ball_center_span_mm':[6.5,6.5],
                   'physical_ball_count':153,'post_reflow_ball_diameter_mm':.319,
                   'ball_diameter_tolerance':'No explicit diameter tolerance printed; do not import Samsung +/-0.05 mm',
                   'surface_profile_to_seating_datum_A_mm':.08,
                   'package_ball_pad_condition':'Dimensions apply to solder balls post-reflow on diameter0.30 mm SMD ball pads',
                   'package_pad_is_not_a_PCB_land_recommendation':True,
                   'auxiliary_package_test_pads':{'count':56,'diameter_mm':.27,'finish':'Au plated','solder_balls':False,
                                                 'PCB_interpretation':'Do not generate PCB solder lands or paste for these package test contacts'}},
        'independent_occupancy_check':{'method':'Extract closed four-Bezier circles of package-ball size from the mechanical PDF. Reverse bottom-view column order14→1 into component-top convention; compare to independently transcribed top-view figure3.',
                                       'physical_ball_circle_count':len(balls),'auxiliary_test_circle_count':len(test_pads),
                                       'other_circle_count':len(other),'other_circle_role':'Top-view A1 identification mark',
                                       'full_grid_sites':196,'physical_sites':153,'absent_sites':43,
                                       'source_grid_sha256':sha(GRID),'occupancy_mismatches':[],
                                       'pixel_coordinates_define_geometry':False},
        'coordinate_convention':{'view':'Component top, balls down; +X right, +Y down',
                                 'x_formula':'(column - 7.5)*0.5 mm','y_formula':'(zero_based_row_index - 6.5)*0.5 mm',
                                 'A1_mm':[-3.25,-3.25],'P14_mm':[3.25,3.25]},
        'related_already_verified_inputs':{
            'Micron_FW':'engineering/mechanical/micron-fw-independent-mechanics.json',
            'K230':'engineering/mechanical/bga-mechanical-audit.md',
            'K230_note':'0.270 mm Ball Solder Mask Opening is package context. It is not sufficient to define board copper, mask and paste.'},
        'restricted_source_handling':'Micron CSN-33 was not accessed or retried. This check uses the previously available exact-part datasheet only.',
        'manufacturing_release_gaps':['Exact-part board-side land pattern and tolerances','NSMD/SMD and soldermask process qualification','Stencil thickness and paste aperture qualification with mixed components','Filled/capped via and local trace/clearance process','Reflow/warpage/reliability at intended high temperature']}
    (OUT/'micron-emmc-package-evidence.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'physical_balls':len(balls),'no_ball_test_pads':len(test_pads),'occupancy_mismatches':0,'output':str(OUT/'micron-emmc-package-evidence.json')},indent=2))

if __name__=='__main__':main()
