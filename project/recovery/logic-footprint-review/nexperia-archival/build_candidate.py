#!/usr/bin/python3
"""Isolated NXP archival/current-text cross-checked candidate; no active CAD edits."""
from pathlib import Path
import csv, hashlib, json
R=Path(__file__).resolve().parents[3];O=R/'recovery/logic-footprint-review/nexperia-archival';C=R/'cad/recovery-footprint-candidates/nexperia-archival';L=C/'CMK230_NXP_Archival_Candidates.pretty'
NAME='NXP_SOT1160-1_74AUP2G97_1.4x1.8_P0.4_ArchivalCrosschecked_CANDIDATE'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source=json.loads((O/'source-acceptance.json').read_text())
assert source['outline_pixels_reviewed'] and source['reflow_pixels_reviewed'] and source['component_side_numbering_verified']
for item in source['local_sources']:assert sha(Path(item['path']))==item['sha256']
ti=json.loads((O.parent/'freeze-manifest.json').read_text());assert all(sha(R/k)==v['sha256'] for k,v in ti['files'].items())
assert all(sha(R/k)==v for k,v in ti['protected_electrical_files'].items())
L.mkdir(parents=True,exist_ok=True)
# Drawing sot1160-1_fr: component side, +X right and +Y down.
# Long land on upper-left is physical pin1, verified separately against sot1160-1_po.
pins=[(1,-.525,-.2,.65,.22,'1B','GND'),(2,-.575,.2,.55,.22,'1C','BOOT_VOLTAGE_QUALIFIED_1V8'),
 (3,-.4,.775,.22,.55,'2Y','RESET_RELEASE_REQUEST_1V8'),(4,0,.775,.22,.55,'GND','GND'),
 (5,.4,.775,.22,.55,'2A','FIXED_RAILS_PGOOD_3V3'),(6,.575,.2,.55,.22,'2B','GND'),
 (7,.575,-.2,.55,.22,'2C','RSTN'),(8,.4,-.775,.22,.55,'1Y','STORAGE_ENABLE_1V8'),
 (9,0,-.775,.22,.55,'VCC','VDD1P8'),(10,-.4,-.775,.22,.55,'1A','FIXED_RAILS_PGOOD_3V3')]
def f(x):return f'{x:.8f}'.rstrip('0').rstrip('.') or '0'
def vec(*x):return ' '.join(map(f,x))
def line(a,b,layer,width=.05):return f'  (fp_line (start {vec(*a)}) (end {vec(*b)}) (stroke (width {f(width)}) (type default)) (layer "{layer}"))'
def pad(num,x,y,w,h,layer):return f'  (pad "{num}" smd rect (at {vec(x,y)}) (size {vec(w,h)}) (layers "{layer}") (solder_mask_margin 0) (solder_paste_margin 0) (solder_paste_margin_ratio 0))'
body=source['body_nominal_mm'];bodymax=source['body_max_mm'];height=source['height_max_mm']
lines=[f'(footprint "{NAME}" (version 20241229) (generator "cmk230_recovery") (layer "F.Cu")',
 '  (descr "NXP SOT1160-1 archival source sot1160-1_fr visually checked; current Nexperia 2022 text dimension cross-check. Exact asymmetric pin1; ten copper pads and explicit mask/paste openings. PROCESS UNQUALIFIED; NOT FOR FABRICATION.")',
 '  (tags "SOT1160-1 74AUP2G97GUX ARCHIVAL_CURRENT_TEXT_CROSSCHECKED_CANDIDATE")','  (attr smd)',
 '  (property "Reference" "REF**" (at 0 -1.95) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.1))))',
 '  (property "Value" "74AUP2G97GUX" (at 0 1.95) (layer "F.Fab") (effects (font (size 0.55 0.55) (thickness 0.08))))',
 f'  (property "HEIGHT_MAX_MM" "{f(height)}" (at 0 0) (layer "F.Fab") hide (effects (font (size 0.5 0.5) (thickness 0.08))))',
 '  (property "SOURCE_STATUS" "Archival NXP pixels plus current 2022 Nexperia text; PDF revision identity not claimed" (at 0 0) (layer "F.Fab") hide (effects (font (size 0.5 0.5) (thickness 0.08))))']
bx,by=body[0]/2,body[1]/2;pts=[(-bx+.2,-by),(bx,-by),(bx,by),(-bx,by),(-bx,-by+.2)]
lines += [line(pts[i],pts[(i+1)%5],'F.Fab') for i in range(5)]
lines += [f'  (fp_rect (start {vec(-bodymax[0]/2,-bodymax[1]/2)}) (end {vec(bodymax[0]/2,bodymax[1]/2)}) (stroke (width 0.05) (type default)) (fill none) (layer "Dwgs.User"))',
 '  (fp_rect (start -0.825 -1.025) (end 0.825 1.025) (stroke (width 0.05) (type default)) (fill none) (layer "Cmts.User"))',
 '  (fp_rect (start -1.25 -1.45) (end 1.25 1.45) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))',
 '  (fp_circle (center -1.11 -0.55) (end -1.07 -0.55) (stroke (width 0.08) (type default)) (fill none) (layer "F.SilkS"))']
for n,x,y,w,h,fn,net in pins:lines.extend([pad(n,x,y,w,h,'F.Cu'),pad('',x,y,w+.125,h+.125,'F.Mask'),pad('',x,y,w-.04,h-.04,'F.Paste')])
lines.append(')');fp=L/(NAME+'.kicad_mod');fp.write_text('\n'.join(lines)+'\n')
(C/'fp-lib-table').write_text('(fp_lib_table\n  (version 7)\n  (lib (name "CMK230_NXP_Archival_Candidates")(type "KiCad")(uri "${KIPRJMOD}/CMK230_NXP_Archival_Candidates.pretty")(options "")(descr "Archival pixels/current primary text cross-check; process unqualified"))\n)\n')
spec={'status':'ARCHIVAL_PIXEL_GEOMETRY_CURRENT_TEXT_CROSSCHECKED_PROCESS_UNQUALIFIED','footprint':str(fp.relative_to(R)),'footprint_sha256':sha(fp),'mpn':'74AUP2G97GUX','package':'SOT1160-1','source_acceptance':'source-acceptance.json','coordinate_frame':'Component side, origin package center, +X right, +Y down; upper-left long land is pin1','body_nominal_mm':body,'body_max_mm':bodymax,'height_max_mm':height,'pitch_mm':.4,'mask_expansion_each_side_mm':.0625,'paste_reduction_each_side_mm':.02,'source_stencil_mm':.1,'copper_bbox_mm':[1.7,2.1],'source_clearance_placement_bbox_mm':[1.95,2.35],'project_courtyard_mm':[2.5,2.9],'courtyard_basis':'Project choice, >=0.25 mm to courtyard centerline beyond source clearance/placement bounding dimensions, outward 0.05-mm grid rounding; not a manufacturer land dimension','pads':[{'pin':n,'function':fn,'net':net,'x_mm':x,'y_mm':y,'copper_mm':[w,h],'mask_mm':[w+.125,h+.125],'paste_mm':[w-.04,h-.04]} for n,x,y,w,h,fn,net in pins],'native_layer_strategy':'10 numbered F.Cu-only rects, 10 unnumbered F.Mask-only rects, 10 unnumbered F.Paste-only rects; no exposed pad, no invented corner radii','process_qualified':False,'active_CAD_assignment_changed':False}
spec.update({'excluded_protrusions_max_per_side_mm':.075,'body_max_including_protrusions_mm':[1.65,2.05],'maximum_envelope_layer':'Cmts.User'})
(O/'footprint-spec.json').write_text(json.dumps(spec,indent=2)+'\n')
with (O/'pad-map.csv').open('w') as fd:
 w=csv.writer(fd);w.writerow(['pin','function','net','x_mm','y_mm','copper_w_mm','copper_h_mm','mask_w_mm','mask_h_mm','paste_w_mm','paste_h_mm'])
 for n,x,y,a,b,fn,net in pins:w.writerow([n,fn,net,x,y,a,b,a+.125,b+.125,a-.04,b-.04])
print(fp)
