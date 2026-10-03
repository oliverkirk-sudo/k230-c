#!/usr/bin/env python3
"""Draw NXP SOT1161-2 from its official reflow drawing; never edits master CAD."""
from pathlib import Path
import json, csv, hashlib

ROOT = Path(__file__).resolve().parents[2]
MECH = ROOT / 'engineering/mechanical'
OUT = ROOT / 'cad/verified-footprints/translator-candidate'
LIB = OUT / 'CMK230_Translator_Candidate.pretty'
LIB.mkdir(parents=True, exist_ok=True)
NAME = 'NXP_SOT1161-2_NVT4858HK_1.8x2.6_P0.4_DrawingVerified_CANDIDATE'
functions = ['DAT2A','DAT3A','DAT0A','DAT1A','CLKA','CLK_FB','GND','CLKB',
             'DAT1B','DAT0B','DAT3B','DAT2B','CMDB','VCCB','VCCA','CMDA']
rows = []
for n in range(1, 17):
    if n <= 4:
        x, y, w, h = (-.6 if n == 1 else -.625), -.6 + (n-1)*.4, (.9 if n == 1 else .85), .22
    elif n <= 8:
        x, y, w, h = -.6 + (n-5)*.4, 1.175, .22, .55
    elif n <= 12:
        x, y, w, h = .625, .6 - (n-9)*.4, .85, .22
    else:
        x, y, w, h = .6 - (n-13)*.4, -1.175, .22, .55
    rows.append(dict(pad=n, function=functions[n-1], x_mm=round(x,6), y_mm=round(y,6),
                     copper_width_mm=w, copper_height_mm=h,
                     mask_width_mm=round(w+.1,6), mask_height_mm=round(h+.1,6),
                     paste_width_mm=round(w-.05,6), paste_height_mm=round(h-.05,6)))

def f(v): return f'{v:.6f}'.rstrip('0').rstrip('.') or '0'
def rect(w,h,layer):
    return f'(fp_rect (start {-w/2} {-h/2}) (end {w/2} {h/2}) (stroke (width 0.05) (type default)) (fill none) (layer "{layer}"))'
def pad(n,x,y,w,h,layer):
    extra = ' (solder_mask_margin 0)' if layer == 'F.Mask' else ' (solder_paste_margin 0) (solder_paste_margin_ratio 0)' if layer == 'F.Paste' else ''
    return f'(pad "{n}" smd rect (at {f(x)} {f(y)}) (size {f(w)} {f(h)}) (layers "{layer}"){extra})'

s = [f'(footprint "{NAME}" (version 20241229) (generator "cmk230_nxp_drawing_audit") (layer "F.Cu") (attr smd)',
     '(descr "NXP SOT1161-2 official reflow drawing 26 January 2021 p3; NVT4858HK pinout Rev2.4 p7-9; candidate only")',
     '(property "Reference" "REF**" (at 0 -2.4) (layer "F.SilkS") (effects (font (size .8 .8) (thickness .12))))',
     '(property "Value" "NVT4858HK_CANDIDATE" (at 0 2.4) (layer "F.Fab") (effects (font (size .6 .6) (thickness .1))))',
     rect(1.8,2.6,'F.Fab'), rect(2.05,2.85,'Dwgs.User'), rect(2.8,3.6,'F.CrtYd'),
     '(fp_line (start -.9 -1.05) (end -.65 -1.3) (stroke (width .1) (type default)) (layer "F.Fab"))',
     '(fp_circle (center -1.25 -1.6) (end -1.20 -1.6) (stroke (width .1) (type default)) (fill none) (layer "F.SilkS"))']
for r in rows:
    for layer, prefix, num in [('F.Cu','copper',r['pad']),('F.Mask','mask',''),('F.Paste','paste','')]:
        s.append(pad(num,r['x_mm'],r['y_mm'],r[prefix+'_width_mm'],r[prefix+'_height_mm'],layer))
s.append(')')
(LIB/(NAME+'.kicad_mod')).write_text('\n'.join(s)+'\n')
(OUT/'fp-lib-table').write_text('(fp_lib_table (version 7)\n(lib (name "CMK230_Translator_Candidate")(type "KiCad")(uri "${KIPRJMOD}/CMK230_Translator_Candidate.pretty")(options "")(descr "NXP drawing candidate; no manufacturing release"))\n)\n')
with (MECH/'nvt4858-pad-coordinate-audit.csv').open('w') as fd:
    writer=csv.DictWriter(fd,rows[0]); writer.writeheader(); writer.writerows(rows)
spec = {'footprint': 'CMK230_Translator_Candidate:'+NAME, 'package': 'SOT1161-2 XQFN16',
        'coordinate_frame': 'Component/top view, +X right, +Y down, body-centered origin',
        'nominal_body_mm':[1.8,2.6], 'body_max_mm':[1.9,2.7], 'additional_protrusion_each_side_mm':.075,
        'max_height_mm':.5, 'pitch_mm':.4, 'project_courtyard_mm':[2.8,3.6],
        'vendor_clearance_outline_mm':[2.35,3.15],
        'mask_expansion_each_side_mm':.05, 'paste_reduction_each_side_mm':.025, 'recommended_stencil_mm':.1,
        'apertures':'16 rectangular copper, 16 explicit mask, 16 explicit paste; no exposed center pad',
        'pad1_exception':'Side pad1 copper length .90 mm versus .85 mm for other seven side pads; shifted +.025 mm in X to keep common outer edge',
        'manufacturing_status':'Drawing geometry checked only; assembly/process approval pending', 'pads':rows}
(MECH/'nvt4858-footprint-spec.json').write_text(json.dumps(spec,indent=2)+'\n')
evidence=Path('/workspace/shared/k230-reference/mechanical/passive-review')
sources=[]
for file,url,pages in [('NXP-SOT1161-2.pdf','https://www.nxp.com/docs/en/package-information/SOT1161-2.pdf',[1,2,3]),
                       ('NXP-NVT4858.pdf','https://www.nxp.com/docs/en/data-sheet/NVT4858.pdf',[4,7,8,9])]:
    path=evidence/file
    sources.append({'file':str(path),'url':url,'pages':pages,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
(MECH/'nvt4858-source-manifest.json').write_text(json.dumps(sources,indent=2)+'\n')
print('Created isolated NVT4858HK footprint candidate:', NAME)
