#!/usr/bin/env python3
"""Generate isolated candidates from Nexperia's current recommended PCB lands."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[2]
MECH = ROOT / 'engineering/mechanical'
OUT = ROOT / 'cad/verified-footprints/nexperia-standard-candidate'
LIBNAME = 'CMK230_Nexperia_Standard_Candidates'
LIB = OUT / (LIBNAME + '.pretty')
LIB.mkdir(parents=True, exist_ok=True)
SOURCES = Path('/workspace/shared/k230-reference/mechanical/nexperia-high-temp')

def f(v): return f'{v:.6f}'.rstrip('0').rstrip('.') or '0'
def rect(w,h,layer):
    return f'(fp_rect (start {f(-w/2)} {f(-h/2)}) (end {f(w/2)} {f(h/2)}) (stroke (width .05) (type default)) (fill none) (layer "{layer}"))'
def pad(n,x,y,w,h,layer):
    local = ' (solder_mask_margin 0)' if layer == 'F.Mask' else ' (solder_paste_margin 0) (solder_paste_margin_ratio 0)' if layer == 'F.Paste' else ''
    return f'(pad "{n}" smd rect (at {f(x)} {f(y)}) (size {f(w)} {f(h)}) (layers "{layer}"){local})'

packages = []
for count, package, suffix, parts, refs, date, drawing_date in [
    (5,'SOT353-1','AUP1G17_06',['74AUP1G17GW,125','74AUP1G06GW,125'],['U91','U93'],'2022-11-15','2022-11-03'),
    (6,'SOT363-2','AUP1G97',['74AUP1G97GW,125'],['U92','U94'],'2022-11-21','2022-11-07')]:
    name=f'Nexperia_{package}_{suffix}_DrawingVerified_CANDIDATE'
    positions={1:(-.975,-.65),2:(-.975,0),3:(-.975,.65),4:(.975,.65)}
    positions.update({5:(.975,-.65)} if count==5 else {5:(.975,0),6:(.975,-.65)})
    rows=[]
    s=[f'(footprint "{name}" (version 20241229) (generator "cmk230_nexperia_drawing_audit") (layer "F.Cu") (attr smd)',
       f'(descr "Nexperia {package} package information {date}, p2 outline and p3 recommended reflow lands, stencil .125mm. CANDIDATE: no assembly release.")',
       f'(property "Reference" "REF**" (at 0 -2.0) (layer "F.SilkS") (effects (font (size .8 .8) (thickness .12))))',
       f'(property "Value" "{package}_CANDIDATE" (at 0 2.0) (layer "F.Fab") (effects (font (size .6 .6) (thickness .1))))',
       rect(1.25,2.0,'F.Fab'),rect(1.75,2.6,'Dwgs.User'),rect(3.4,3.1,'F.CrtYd'),
       '(fp_line (start -.625 -.75) (end -.375 -1) (stroke (width .1) (type default)) (layer "F.Fab"))',
       '(fp_circle (center -1.5 -1.15) (end -1.45 -1.15) (stroke (width .1) (type default)) (fill none) (layer "F.SilkS"))']
    # Source occupied area is a stepped outline, not a full 2.9x2.35 rectangle.
    occupied=[(-1.45,-1),(-.775,-1),(-.775,-1.175),(.775,-1.175),(.775,-1),
              (1.45,-1),(1.45,1),(.775,1),(.775,1.175),(-.775,1.175),(-.775,1),(-1.45,1)]
    for a,b in zip(occupied,occupied[1:]+occupied[:1]):
        s.append(f'(fp_line (start {f(a[0])} {f(a[1])}) (end {f(b[0])} {f(b[1])}) (stroke (width .03) (type dash)) (layer "Dwgs.User"))')
    for n,(x,y) in positions.items():
        row=dict(pad=n,x_mm=x,y_mm=y,copper_mm=[.75,.4],mask_mm=[.85,.5],paste_mm=[.65,.3])
        rows.append(row)
        for layer,prefix,num in [('F.Cu','copper',n),('F.Mask','mask',''),('F.Paste','paste','')]:
            s.append(pad(num,x,y,*row[prefix+'_mm'],layer))
    s.append(')')
    (LIB/(name+'.kicad_mod')).write_text('\n'.join(s)+'\n')
    pdf=SOURCES/(package+'.pdf')
    packages.append(dict(package=package,footprint=LIBNAME+':'+name,parts=parts,reference_instances=refs,
        source=dict(pdf=str(pdf),url=f'https://assets.nexperia.com/documents/package-information/{package}.pdf',
                    sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),document_date=date,
                    outline_page=2,outline_issue_date='2021-12-16',reflow_page=3,reflow_issue_date=drawing_date,
                    access='Normal public cloud-browser PDF view and download control; no login, access-warning override, or restricted-download retry'),
        coordinate_frame='Component top view, origin at body center, +X right, +Y down; package p2 top view rotated 90 degrees clockwise to put pin1 upper-left',
        nominal_body_mm=[1.25,2.0],maximum_body_mm=[1.35,2.2],excluded_protrusion_max_each_side_mm=.2,
        body_with_protrusions_max_mm=[1.75,2.6],maximum_lead_span_mm=2.4,maximum_seated_height_mm=1.1,
        pitch_mm=.65,pad_row_center_separation_mm=1.95,
        copper_total_extent_mm=[2.7,1.7],mask_total_extent_mm=[2.8,1.8],paste_total_extent_mm=[2.6,1.6],
        vendor_occupied_bbox_mm=[2.9,2.35],vendor_occupied_polygon_mm=occupied,
        project_courtyard_mm=[3.4,3.1],project_courtyard_area_mm2=10.54,
        courtyard_basis='At least .25mm beyond vendor occupied bounding box, explicit mask openings, maximum leads and maximum body including drawing-excluded .2mm protrusions per side; Y enlarged to3.1mm for protrusions',
        recommended_stencil_mm=.125,mask_expansion_each_side_mm=.05,paste_reduction_each_side_mm=.05,
        apertures=f'{count} rectangular electrical copper pads + {count} explicit mask openings + {count} explicit paste openings; no exposed pad',
        status='DRAWING_GEOMETRY_CANDIDATE_ASSEMBLY_PROCESS_UNQUALIFIED',pads=rows))

(OUT/'fp-lib-table').write_text(f'(fp_lib_table (version 7)\n(lib (name "{LIBNAME}")(type "KiCad")(uri "${{KIPRJMOD}}/{LIBNAME}.pretty")(options "")(descr "Current Nexperia PCB drawing candidates; assembly unqualified"))\n)\n')
spec=dict(status='SOURCE_DERIVED_CANDIDATES_NO_MAIN_CAD_EDITS',packages=packages,
    area_comparison=dict(standard_four_vendor_occupied_bbox_total_mm2=27.26,
        X2SON_four_published_occupied_bbox_total_mm2=5.04,
        vendor_occupied_bbox_delta_mm2=22.22,
        standard_four_verified_project_courtyards_total_mm2=42.16,
        X2SON_courtyard_status='Not verified; no real courtyard-to-courtyard delta is claimed',
        standard_project_courtyard_vs_vendor_bbox_extra_mm2=14.9,
        notes=['Manufacturer occupied dimensions are bounding boxes for stepped outlines, not literal copper areas.',
               'Four-part courtyard total does not imply board placement, routing, thermal or PDN fit.']),
    validation_files=['nexperia-standard-footprint-verification.json','nexperia-standard-geometry-drc.json','nexperia-standard-footprint-independent-review.json'],
    pin_review='nexperia-standard-logic-variant-review.json')
(MECH/'nexperia-standard-footprint-spec.json').write_text(json.dumps(spec,indent=2)+'\n')
print('Generated two separate Nexperia standard-package candidates')
