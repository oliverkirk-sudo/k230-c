#!/usr/bin/env python3
"""Generate isolated compact-package candidates; never edits integrated schematic/PCB.
Geometry transcribed from actual TI drawings. Process-selected mask/courtyard declared.
"""
from pathlib import Path
import json,csv,hashlib
R=Path(__file__).resolve().parents[2];M=R/'engineering/mechanical';O=R/'cad/verified-footprints/compact-options';L=O/'CMK230_Compact_Candidates.pretty';L.mkdir(parents=True,exist_ok=True)
def f(x):return f'{x:.8f}'.rstrip('0').rstrip('.') or '0'
def p(n,x,y,w,h,layers,r=.05):
 s=f'(pad "{n}" smd roundrect (at {f(x)} {f(y)}) (size {f(w)} {f(h)}) (layers '+ ' '.join('"'+z+'"' for z in layers)+f') (roundrect_rratio {f(r/min(w,h))})'
 if 'F.Mask' in layers:s+=' (solder_mask_margin 0)'
 if 'F.Paste' in layers:s+=' (solder_paste_margin 0) (solder_paste_margin_ratio 0)'
 return s+')'
def rect(w,h,layer):return f'(fp_rect (start {f(-w/2)} {f(-h/2)}) (end {f(w/2)} {f(h/2)}) (stroke (width 0.05) (type default)) (fill none) (layer "{layer}"))'
items=[
 {'id':'DRL','name':'TI_DRL0005A_AUP_5P_DrawingVerified_CANDIDATE','body_midrange_mm':[1.2,1.6],'body_min_mm':[1.1,1.5],'body_max_mm':[1.3,1.7],'additional_flash_per_side_mm':.15,'max_lead_span_mm':1.7,'max_height_mm':.6,'courtyard_mm':[2.8,2.5],'pitch_mm':.5,'x_mm':.74,'land_mm':[.67,.3],'stencil_mm':.1,'drawing':'DRL0005A 4220753/E 11/2024','pages':{'sn74aup1g08':[3,34,35,36],'sn74aup1g06':[3,49,50,51],'sn74aup1g07':[3,45,46,47],'sn74aup1g17':[3,35,36,37]}},
 {'id':'DCK','name':'TI_DCK0005A_AUP_5P_DrawingVerified_CANDIDATE','body_midrange_mm':[1.25,2.0],'body_min_mm':[1.1,1.85],'body_max_mm':[1.4,2.15],'additional_flash_per_side_mm':.25,'max_lead_span_mm':2.4,'max_height_mm':1.1,'courtyard_mm':[3.8,3.2],'pitch_mm':.65,'x_mm':1.1,'land_mm':[.95,.4],'stencil_mm':.125,'drawing':'DCK0005A 4214834/G 11/2024','pages':{'sn74aup1g08':[3,50,51,52],'sn74aup1g06':[3,33,34,35],'sn74aup1g07':[3,32,33,34]}},
 {'id':'DRV','name':'TI_DRV0006A_D_TPS3808_6P_EP7_DrawingVerified_CANDIDATE','body_midrange_mm':[2,2],'body_min_mm':[1.9,1.9],'body_max_mm':[2.1,2.1],'additional_flash_per_side_mm':0,'max_height_mm':.8,'courtyard_mm':[3,2.6],'pitch_mm':.65,'x_mm':.975,'land_mm':[.45,.3],'stencil_mm':.125,'drawing':'DRV0006A 4222173/C 11/2025 and DRV0006D 4225563/A 12/2019, identical example board/stencil geometry','pages':{'tps3808':[4,30,31,32,33,34,35]}}
]
items.append({'id':'DRL6','name':'TI_DRL0006A_AUP1G97_DrawingVerified_CANDIDATE','body_midrange_mm':[1.2,1.6],'body_min_mm':[1.1,1.5],'body_max_mm':[1.3,1.7],'additional_flash_per_side_mm':.15,'max_lead_span_mm':1.7,'max_height_mm':.6,'courtyard_mm':[2.8,2.5],'pitch_mm':.5,'x_mm':.74,'land_mm':[.67,.3],'stencil_mm':.1,'drawing':'DRL0006A 4223266/F 11/2024','pages':{'sn74aup1g97':[1,2,3,18,19,20]}})

coords=[]
for v in items:
 w,h=v['body_midrange_mm'];cw,ch=v['courtyard_mm'];x=v['x_mm'];y=v['pitch_mm'];pw,ph=v['land_mm'];n=v['name']
 a=[f'(footprint "{n}" (version 20241229) (generator "cmk230_compact_audit") (layer "F.Cu") (attr smd)',f'(descr "PACKAGE CANDIDATE ONLY; {v["drawing"]}; read compact-package-audit before substitution")',f'(property "Reference" "REF**" (at 0 {f(-ch/2-.7)}) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))',f'(property "Value" "{v["id"]}_CANDIDATE" (at 0 {f(ch/2+.7)}) (layer "F.Fab") (effects (font (size 0.6 0.6) (thickness 0.1))))',rect(w,h,'F.Fab'),rect(*v['body_max_mm'],'Dwgs.User'),rect(cw,ch,'F.CrtYd')]
 a.append(f'(fp_line (start {f(-w/2)} {f(-h/2+.2)}) (end {f(-w/2+.2)} {f(-h/2)}) (stroke (width 0.1) (type default)) (layer "F.Fab"))')
 a.append(f'(fp_circle (center {f(-cw/2+.1)} {f(-ch/2+.1)}) (end {f(-cw/2+.145)} {f(-ch/2+.1)}) (stroke (width 0.09) (type default)) (fill none) (layer "F.SilkS"))')
 sites=[(1,-x,-y),(2,-x,0),(3,-x,y),(4,x,y)]
 sites+=([(5,x,-y)] if v['id'] not in ['DRV','DRL6'] else [(5,x,0),(6,x,-y)])
 for num,xx,yy in sites:
  a += [p(str(num),xx,yy,pw,ph,['F.Cu','F.Paste']),p('',xx,yy,pw+.1,ph+.1,['F.Mask'],.1)]
  coords.append(dict(package=v['id'],pad=str(num),x_mm=xx,y_mm=yy,copper_width_mm=pw,copper_height_mm=ph,copper_radius_mm=.05,mask_width_mm=pw+.1,mask_height_mm=ph+.1,mask_radius_mm=.1,paste='1:1 with copper',pin_type='SIGNAL_OR_POWER',source_drawing=v['drawing']))
 if v['id']=='DRV':
  a += [p('7',0,0,1,1.6,['F.Cu']),p('',0,0,1.1,1.7,['F.Mask'],.1),p('',0,-.45,1,.7,['F.Paste']),p('',0,.45,1,.7,['F.Paste'])]
  coords.append(dict(package='DRV',pad='7',x_mm=0,y_mm=0,copper_width_mm=1,copper_height_mm=1.6,copper_radius_mm=.05,mask_width_mm=1.1,mask_height_mm=1.7,mask_radius_mm=.1,paste='two 1.0x0.7 R0.05 apertures at y=+/-0.45',pin_type='EXPOSED_PAD_CONNECT_GND',source_drawing=v['drawing']))
  v['thermal_pad_mm']=[1,1.6];v['thermal_pad_paste_apertures']=[{'x_mm':0,'y_mm':s*.45,'width_mm':1,'height_mm':.7,'radius_mm':.05} for s in [-1,1]];v['thermal_vias']='Optional in TI drawing; not instantiated. Board stackup/process choice remains.'
 a.append(')');(L/(n+'.kicad_mod')).write_text('\n'.join(a)+'\n')
 v['mask_strategy']='Explicit unnumbered F.Mask apertures, NSMD, chosen +0.05 mm constant-offset opening; TI max0.05 DRL / max0.07 DCK and DRV; local margin0 locks geometry'
 v['paste_strategy']='Copper plus paste on signal pads with local paste margin/ratio0. DRV EP7 uses two explicit unnumbered paste-only apertures.'
 v['courtyard_policy']='Project-selected0.25 mm beyond copper/mask or maximum body plus stated flash, rounded outward to0.05mm. Not a TI dimension.'
(M/'compact-footprint-spec.json').write_text(json.dumps(items,indent=2)+'\n')
with (M/'compact-pad-coordinate-audit.csv').open('w') as fd:
 z=csv.DictWriter(fd,coords[0].keys());z.writeheader();z.writerows(coords)
(O/'fp-lib-table').write_text('(fp_lib_table (version 7)\n(lib (name "CMK230_Compact_Candidates")(type "KiCad")(uri "${KIPRJMOD}/CMK230_Compact_Candidates.pretty")(options "")(descr "Compact mechanical candidates; exact pin audit required; no integrated CAD change"))\n)\n')
# Exact pin-number compatibility, not cross-function part substitution.
rows=[]
for root,funcs in [('SN74AUP1G06',['NC','A','GND','Y_OPEN_DRAIN_INVERTING','VCC']),('SN74AUP1G07',['NC','A','GND','Y_OPEN_DRAIN_NONINVERTING','VCC']),('SN74AUP1G08',['A','B','GND','Y_AND','VCC']),('SN74AUP1G17',['NC','A','GND','Y_SCHMITT_NONINVERTING_PUSH_PULL','VCC'])]:
 for i,fn in enumerate(funcs,1):rows.append({'base_part':root,'from_package':'DBV','from_pin':i,'to_package':'DCK or DRL','to_pin':i,'function':fn,'source_url':f'https://www.ti.com/lit/ds/symlink/{root.lower()}.pdf','source_page':3,'action':'Package-only candidate; same base logic part; preserve numbered net and NC handling'})
for dbv,drv,fn in [(1,6,'RESET_N'),(2,5,'GND'),(3,4,'MR_N'),(4,3,'CT'),(5,2,'SENSE'),(6,1,'VDD'),('',7,'EXPOSED_PAD_GND')]:rows.append({'base_part':'TPS3808G01','from_package':'DBV','from_pin':dbv,'to_package':'DRV','to_pin':drv,'function':fn,'source_url':'https://www.ti.com/lit/ds/symlink/tps3808.pdf','source_page':4,'action':'Requires new/remapped symbol plus EP7 grounded; not footprint-swap-only'})
with (M/'compact-package-pin-remap.csv').open('w') as fd:
 z=csv.DictWriter(fd,rows[0].keys());z.writeheader();z.writerows(rows)
# Report a no-write adaptation of current selected U89/U90 nets, preserving CT open20ms intent.
input_path=R/'engineering/reset/supervisor-pin-net-matrix.csv';matrix=list(csv.DictReader(input_path.open()));adapt=[]
for ref in ['U89','U90']:
 d={int(r['pin']):r['net'] for r in matrix if r['reference']==ref}
 for old,new,fn in [(1,6,'RESET_N'),(2,5,'GND'),(3,4,'MR_N'),(4,3,'CT'),(5,2,'SENSE'),(6,1,'VDD')]:
  adapt.append({'reference':ref,'function':fn,'dbv_pin':old,'drv_pin':new,'existing_net_or_intent':d.get(old,'INTENTIONAL_OPEN_CT_SELECTS20MS' if old==4 else 'UNRESOLVED'),'integration_action':'Preserve intentional open CT on new pin3' if old==4 else 'Move existing named net to DRV pin'})
 adapt.append({'reference':ref,'function':'EP_GND','dbv_pin':'NONE','drv_pin':7,'existing_net_or_intent':'GND','integration_action':'Add explicit symbol pin7 and connect to GND; solder mandatory'})
with (M/'compact-TPS3808-proposed-net-remap.csv').open('w') as fd:
 z=csv.DictWriter(fd,adapt[0].keys());z.writeheader();z.writerows(adapt)
# Hash all local TI sources; originals remain outside package tree.
man=[]
for src in ['sn74aup1g06','sn74aup1g07','sn74aup1g08','sn74aup1g17','sn74aup1g97','tps3808']:
 path=Path('/workspace/shared/k230-reference')/(src+'.pdf')
 man.append({'part':src,'source_url':f'https://www.ti.com/lit/ds/symlink/{src}.pdf','local_file':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pages_by_package':{i['id']:i['pages'][src] for i in items if src in i['pages']},'visual_review':'Actual function and mechanical/board/stencil pages viewed. Source page images kept outside distributable tree.'})
(M/'compact-TI-source-manifest.json').write_text(json.dumps(man,indent=2)+'\n')
print('Wrote 4 compact package candidates; no integrated CAD modified.')

# Schmitt AND correction is a circuit change, not a pin-compatible 1G08 package substitution.
func=[(1,'B','GND_CONFIG'),(2,'GND','GND'),(3,'A','SIGNAL_A'),(4,'Y','AND_OUTPUT'),(5,'VCC','SUPPLY'),(6,'C','SIGNAL_C')]
with (M/'compact-AUP1G97-function-pin-audit.csv').open('w') as fd:
 z=csv.writer(fd);z.writerow(['pad','function','and_configuration','source_url','source_pages'])
 for n,f,net in func:z.writerow([n,f,net,'https://www.ti.com/lit/ds/symlink/sn74aup1g97.pdf','1-3'])
truth=[(0,0,0,0),(0,0,1,0),(0,1,0,1),(0,1,1,1),(1,0,0,0),(1,0,1,1),(1,1,0,0),(1,1,1,1)]
assert all(Y==(A if C else B) for C,B,A,Y in truth)
assert all(Y==(A & C) for C,B,A,Y in truth if B==0)
with (M/'compact-AUP1G97-truth-table.csv').open('w') as fd:
 z=csv.writer(fd);z.writerow(['C','B','A','Y','matches_C_select_A_else_B','B_zero_matches_A_AND_C'])
 for C,B,A,Y in truth:z.writerow([C,B,A,Y,True,True if B==0 else 'not_applicable'])
(M/'compact-AUP1G97-status.json').write_text(json.dumps({'source_sha256':hashlib.sha256(Path('/workspace/shared/k230-reference/sn74aup1g97.pdf').read_bytes()).hexdigest(),'source_url':'https://www.ti.com/lit/ds/symlink/sn74aup1g97.pdf','logic_pages':[1,2,3],'mechanical_pages':[18,19,20],'logic':'Y=(C AND A) OR ((NOT C) AND B)','AND_configuration':'B pin1=GND; pin2=GND; A pin3/C pin6=signals; Y pin4; VCC pin5','truth_table_rows_checked':8,'AND_rows_checked':4,'all_inputs_Schmitt_trigger':True,'new_footprint':'CMK230_Compact_Candidates:TI_DRL0006A_AUP1G97_DrawingVerified_CANDIDATE','current_requested_refs':{'U91':'SN74AUP1G07 DRL5','U93':'SN74AUP1G06 DRL5','U92':'SN74AUP1G97 DRL6 Schmitt AND','U94':'SN74AUP1G97 DRL6 Schmitt AND','U89':'TPS3808G01 DRV+EP7','U90':'TPS3808G01 DRV+EP7'},'U96_status':'Removed by design lead; earlier 1G17 candidate remains alternative only','master_CAD_modified':False,'previous_compact_area_scenarios':'Historical; not current BOM after topology correction'},indent=2)+'\n')
