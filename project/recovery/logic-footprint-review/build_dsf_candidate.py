#!/usr/bin/python3
"""Build only the isolated TI DSF candidate. Does not assign a system footprint."""
import csv, hashlib, json, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'recovery/logic-footprint-review'
CAD = ROOT / 'cad/recovery-footprint-candidates'
LIB = CAD / 'CMK230_Recovery_Logic_Candidates.pretty'
NAME = 'TI_DSF0006A_SN74LVC1G97_1x1_P0.35_SourceExample_CANDIDATE'
PDF = Path('/workspace/shared/k230-reference/sn74lvc1g97.pdf')
SHA = '53e8bc4d0f966f6e1d8d28987240f17a07e94bec6658ebc92ab322dccae7f416'
assert hashlib.sha256(PDF.read_bytes()).hexdigest() == SHA
for p in [OUT / 'evidence', LIB]: p.mkdir(parents=True, exist_ok=True)

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
protected = {str(p.relative_to(ROOT)): digest(p) for p in sorted((ROOT/'cad/recovery-compact-candidate').rglob('*')) if p.is_file()}
invariant = OUT/'frozen-electrical-inputs.json'
if invariant.exists():
    assert json.loads(invariant.read_text()) == protected, 'Frozen electrical branch changed since first snapshot'
else: invariant.write_text(json.dumps(protected, indent=2)+'\n')

def fmt(v): return f'{v:.9f}'.rstrip('0').rstrip('.') or '0'
def vec(*v): return ' '.join(map(fmt, v))
def line(a,b,layer,width=.05):
    return f'  (fp_line (start {vec(*a)}) (end {vec(*b)}) (stroke (width {fmt(width)}) (type default)) (layer "{layer}"))'
def pad(num,x,y,w,h,r,layer):
    return f'  (pad "{num}" smd roundrect (at {vec(x,y)}) (size {vec(w,h)}) (layers "{layer}") (roundrect_rratio {fmt(r/min(w,h))}) (solder_mask_margin 0) (solder_paste_margin 0) (solder_paste_margin_ratio 0))'

# Independent visual transcription: TI 4220597/B 06/2022, PDF physical pp29-31.
# Top/component view is p30/p31; package underside in p29 must not be copied unmirrored.
pins = [(1,-.4,-.35,'In1','GLOBAL_DISABLE'),(2,-.4,0,'GND','GND'),
        (3,-.4,.35,'In0','VDD_3V3'),(4,.4,.35,'Y','DISABLE_OR_TF'),
        (5,.4,0,'VCC','VDD_3V3'),(6,.4,-.35,'In2','MODE_TF')]
lines=[f'(footprint "{NAME}" (version 20241229) (generator "cmk230_recovery") (layer "F.Cu")',
       '  (descr "TI DSF0006A 4220597/B 06/2022 source board/stencil example; SN74LVC1G97DSFR; max height 0.40 mm. Copper R0.05 0.60x0.17; paste R0.05 0.60x0.15, example stencil 0.09. Project NSMD +0.05, explicit R0.10 apertures. ASSEMBLY PROCESS UNQUALIFIED; NOT FOR FABRICATION.")',
       '  (tags "DSF0006A SN74LVC1G97DSFR SOURCE_EXAMPLE_CANDIDATE")',
       '  (attr smd)',
       '  (property "Reference" "REF**" (at 0 -1.25) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.1))))',
       '  (property "Value" "SN74LVC1G97DSFR" (at 0 1.25) (layer "F.Fab") (effects (font (size 0.5 0.5) (thickness 0.08))))',
       '  (property "HEIGHT_MAX_MM" "0.40" (at 0 0) (layer "F.Fab") hide (effects (font (size 0.5 0.5) (thickness 0.08))))',
       '  (property "SOURCE_DRAWING" "4220597/B 06/2022; PDF pp29-31" (at 0 0) (layer "F.Fab") hide (effects (font (size 0.5 0.5) (thickness 0.08))))']
pts=[(-.3,-.5),(.5,-.5),(.5,.5),(-.5,.5),(-.5,-.3)]
lines += [line(pts[i],pts[(i+1)%len(pts)],'F.Fab') for i in range(len(pts))]
lines += ['  (fp_rect (start -0.525 -0.525) (end 0.525 0.525) (stroke (width 0.05) (type default)) (fill none) (layer "Dwgs.User"))',
          '  (fp_rect (start -1 -0.8) (end 1 0.8) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))',
          '  (fp_circle (center -0.88 -0.69) (end -0.85 -0.69) (stroke (width 0.08) (type default)) (fill none) (layer "F.SilkS"))']
for n,x,y,func,net in pins:
    lines += [pad(n,x,y,.6,.17,.05,'F.Cu'),pad('',x,y,.7,.27,.1,'F.Mask'),pad('',x,y,.6,.15,.05,'F.Paste')]
lines += [')']
fp=LIB/(NAME+'.kicad_mod'); fp.write_text('\n'.join(lines)+'\n')
(CAD/'fp-lib-table').write_text('(fp_lib_table\n  (version 7)\n  (lib (name "CMK230_Recovery_Logic_Candidates")(type "KiCad")(uri "${KIPRJMOD}/CMK230_Recovery_Logic_Candidates.pretty")(options "")(descr "Isolated recovery candidates; source examples, process unqualified"))\n)\n')

spec={
 'status':'TI_DRAWING_GEOMETRY_CANDIDATE_ONLY_NEXPERIA_BLOCKED',
 'footprint': 'CMK230_Recovery_Logic_Candidates:'+NAME,
 'file':str(fp.relative_to(ROOT)), 'footprint_sha256':digest(fp),
 'mpn':'SN74LVC1G97DSFR','reference':'U14','package':'DSF0006A',
 'source':{'url':'https://www.ti.com/lit/ds/symlink/sn74lvc1g97.pdf','path':str(PDF),'sha256':SHA,'datasheet_revision':'SCES416N January 2017','drawing_revision':'4220597/B 06/2022','physical_pages':[3,29,30,31],'pixels_independently_inspected':True},
 'coordinate_frame':'Component side, origin at body center, +X right, +Y down; pin1 upper-left. Bottom-view package drawing not copied unmirrored.',
 'body_midrange_mm':[1,1],'body_min_mm':[.95,.95],'body_max_mm':[1.05,1.05],'height_max_mm':.4,
 'pitch_mm':.35,'copper_land_mm':[.6,.17],'copper_corner_radius_mm':.05,
 'paste_aperture_mm':[.6,.15],'paste_corner_radius_mm':.05,'source_example_stencil_mm':.09,
 'mask_strategy':'Project-selected NSMD +0.05 mm true constant offset; source allows at most 0.07 mm. Explicit non-copper mask apertures, independent of board/footprint margin settings.',
 'mask_opening_mm':[.7,.27],'mask_corner_radius_mm':.1,'mask_expansion_mm':.05,
 'source_max_mask_expansion_mm':.07,
 'courtyard_mm':[2,1.6],'courtyard_area_mm2':3.2,
 'courtyard_basis':'Project choice: >=0.25 mm to outline centerline beyond mask/body maximum, outward 0.05-mm rounding. 0.025-mm half stroke reduces physical inner-edge distance. Not a TI area claim.',
 'pins':[{'number':n,'x_mm':x,'y_mm':y,'function':fun,'net':net} for n,x,y,fun,net in pins],
 'assembly_approval':False,'active_schematic_assignment_changed':False,
 'gates':['Actual soldermask web/registration and finished copper clearances must be approved by the selected factory.', '0.09-mm stencil is TI example only: check aperture release, corner fidelity, deposited volume, reflow, placement and rework.', 'Pin1 marking/orientation and local bypass/routing need final board review.', 'No assembled-height, thermal, electrical, placement/routing or complete-board-fit qualification is implied.']}
(OUT/'ti-dsf-spec.json').write_text(json.dumps(spec,indent=2)+'\n')
with (OUT/'ti-dsf-pad-map.csv').open('w') as f:
    w=csv.writer(f); w.writerow(['pin','function','candidate_net','x_mm','y_mm','copper_w_mm','copper_h_mm','copper_radius_mm','mask_w_mm','mask_h_mm','mask_radius_mm','paste_w_mm','paste_h_mm','paste_radius_mm'])
    for n,x,y,fun,net in pins:w.writerow([n,fun,net,x,y,.6,.17,.05,.7,.27,.1,.6,.15,.05])
for n in [29,30,31]: shutil.copyfile(PDF.parent/f'TI_DSF_page_{n}.png',OUT/'evidence'/f'TI_DSF_page_{n}.png')
if Path('/tmp/TI97-pin-map.png').exists(): shutil.copyfile('/tmp/TI97-pin-map.png',OUT/'evidence/TI_DSF_pin_map_page_3.png')
print(fp)
