#!/usr/bin/env python3
"""Build drawing-checked TI footprints. Mechanical/land verification, not a PCB release.
Only writes the dedicated verified-footprints library and mechanical audit data.
All dimensions mm; component-side view, +x right and +y down.
"""
from pathlib import Path
import json, csv, hashlib
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'cad/verified-footprints'
LIB=OUT/'CMK230_Verified.pretty'; LIB.mkdir(parents=True,exist_ok=True)
MECH=ROOT/'engineering/mechanical'
def f(v): return f'{v:.9f}'.rstrip('0').rstrip('.') or '0'
def vec(*v):return ' '.join(f(x) for x in v)
def rect(a,b,layer,width=.05):return f'  (fp_rect (start {vec(*a)}) (end {vec(*b)}) (stroke (width {f(width)}) (type default)) (fill none) (layer "{layer}"))'
def line(a,b,layer,width=.1):return f'  (fp_line (start {vec(*a)}) (end {vec(*b)}) (stroke (width {f(width)}) (type default)) (layer "{layer}"))'
def pad(num,x,y,w,h,shape='roundrect',radius=.05,layers=('F.Cu','F.Paste','F.Mask'),mask=None):
 s=f'  (pad "{num}" smd {shape} (at {vec(x,y)}) (size {vec(w,h)}) (layers '+ ' '.join(f'"{l}"' for l in layers)+')'
 if shape=='roundrect':s+=f' (roundrect_rratio {f(radius/min(w,h))})'
 if mask is not None:s+=f' (solder_mask_margin {f(mask)})'
 # Never inherit a board-wide paste reduction for the TI example aperture.
 if 'F.Paste' in layers:s+=' (solder_paste_margin 0) (solder_paste_margin_ratio 0)'
 return s+')'
models=[]
def emit(name,mpn,body,maxbody,court,pads,source,pages,height,details,marker=None,flash=0):
 bw,bh=body;cx,cy=court
 a=[f'(footprint "{name}" (version 20241229) (generator "cmk230_drawing_audit") (layer "F.Cu")',f'  (descr "Drawing-verified TI land example; {mpn}; {source}; pages {pages}. Process assumptions documented; not fabrication release.")',f'  (tags "CMK230 drawing_verified {mpn}")','  (attr smd)',f'  (property "Reference" "REF**" (at 0 {f(-cy-.7)}) (layer "F.SilkS") (effects (font (size 0.8 0.8) (thickness 0.12))))',f'  (property "Value" "{mpn}" (at 0 {f(cy+.65)}) (layer "F.Fab") (effects (font (size 0.55 0.55) (thickness 0.08))))']
 # Nominal package outline with chamfer marking A1 / pin 1 corner; maximum envelope on Dwgs.User.
 cut=min(.2,bw/5)
 points=[(-bw/2+cut,-bh/2),(bw/2,-bh/2),(bw/2,bh/2),(-bw/2,bh/2),(-bw/2,-bh/2+cut)]
 a += [line(points[i],points[(i+1)%len(points)],'F.Fab') for i in range(len(points))]
 a += [rect((-maxbody[0]/2,-maxbody[1]/2),(maxbody[0]/2,maxbody[1]/2),'Dwgs.User'),rect((-cx,-cy),(cx,cy),'F.CrtYd')]
 # Standalone silk orientation marker above-left, kept outside all soldermask apertures.
 if marker is None:marker=(-cx+.1,-cy+.1)
 a += [f'  (fp_circle (center {vec(*marker)}) (end {vec(marker[0]+.045,marker[1])}) (stroke (width 0.09) (type default)) (fill none) (layer "F.SilkS"))']
 for p in pads:
  pp={k:v for k,v in p.items() if k not in ('function','exposed_w','exposed_h')}
  # Explicit mask-only apertures preserve the exact R0.05 mask-defined opening.
  # KiCad's normal solder_mask_margin scales roundrect radius; it is not a true offset.
  if p['num'] and 'mask' in p:
   m=pp.pop('mask'); pp['layers']=tuple(z for z in pp.get('layers',('F.Cu','F.Paste','F.Mask')) if z!='F.Mask')
   a.append(pad(**pp))
   shape=p.get('shape','roundrect')
   a.append(pad('',p['x'],p['y'],p['w']+2*m,p['h']+2*m,shape=shape,radius=p.get('radius',.05)+m,layers=('F.Mask',),mask=0))
  else:a.append(pad(**pp))
 a.append(')');(LIB/(name+'.kicad_mod')).write_text('\n'.join(a)+'\n')
 m={'name':name,'mpn':mpn,'body_nominal_mm':body,'body_max_mm':maxbody,'additional_mold_flash_per_side_mm':flash,'courtyard_half_width_height_mm':court,'courtyard_policy':'At least 0.25 mm from maximum body/copper/mask envelope; rounded outward to 0.05 mm, orientation marker included','height_max_mm':height,'source_url':source,'source_pages':pages,'details':details,'electrical_pad_count':sum(bool(p['num']) for p in pads),'paste_only_aperture_count':sum(p.get('layers')==('F.Paste',) for p in pads),'pads':pads}
 models.append(m)

# RSV0016A 4220314/C, 02/2020, official example board/stencil.
ps=[];fn=['S1B','D1','S2A','S2B','D2','GND','D3','S3B','S3A','D4','S4B','S4A','EN_N','VDD','SEL','S1A']
for i,y in enumerate([-.6,-.2,.2,.6],1):ps.append(dict(num=str(i),x=-.75 if i==1 else -.8,y=y,w=.7 if i==1 else .6,h=.2,mask=.05,function=fn[i-1]))
for i,x in enumerate([-.6,-.2,.2,.6],5):ps.append(dict(num=str(i),x=x,y=1.2,w=.2,h=.6,mask=.05,function=fn[i-1]))
for i,y in enumerate([.6,.2,-.2,-.6],9):ps.append(dict(num=str(i),x=.8,y=y,w=.6,h=.2,mask=.05,function=fn[i-1]))
for i,x in enumerate([.6,.2,-.2,-.6],13):ps.append(dict(num=str(i),x=x,y=-1.2,w=.2,h=.6,mask=.05,function=fn[i-1]))
emit('TI_RSV0016A_TMUX1574_1.8x2.6_P0.4_DrawingVerified','TMUX1574RSVR',(1.8,2.6),(1.85,2.65),(1.4,1.8),ps,'https://www.ti.com/lit/ds/symlink/tmux1574.pdf','3,36-38',.55,'NSMD example. Explicit +0.05 mm mask expansion equals TI maximum; board fabricator must control tolerance. One-to-one copper/paste with R0.05 corners, TI example 0.125 mm stencil. Pin1 is 0.7 x 0.2 at (-0.75,-0.6), its left edge aligned to the other left pads; NO exposed center pad.',marker=(-1.30,-1.65))

# DBV0005A 4214839/K, 08/2024.
ps=[];fn={1:'A',2:'B',3:'GND',4:'Y',5:'VCC'}
for n,x,y in [(1,-1.3,-.95),(2,-1.3,0),(3,-1.3,.95),(4,1.3,.95),(5,1.3,-.95)]:ps.append(dict(num=str(n),x=x,y=y,w=1.1,h=.6,mask=.05,function=fn[n]))
emit('TI_DBV0005A_SN74LVC1G32_SOT23_5_DrawingVerified','SN74LVC1G32DBVR',(1.6,2.9),(1.75,3.05),(2.15,2.05),ps,'https://www.ti.com/lit/ds/symlink/sn74lvc1g32.pdf','41-43',1.45,'NSMD example, selected mask expansion +0.05 mm within TI 0.07 mm maximum. One-to-one copper/paste, R0.05 corners, TI example 0.125 mm stencil. Courtyard additionally accounts for up to 0.25 mm mold flash per body side.',marker=(-2.0,-1.8),flash=.25)

# DMQ0006A 4222645/E, 09/2023. SMD is TI-preferred; example dimensions are EXPOSED metal.
ps=[];fn={1:'EN',2:'PG',3:'FB',4:'GND',5:'SW',6:'VIN'}
for n,x,y,w,h in [(1,-.65,-.5,.6,.25),(2,-.65,0,.6,.25),(3,-.65,.5,.6,.25),(4,.45,.5,1,.2),(5,.45,0,1,.2),(6,.45,-.5,1,.2)]:
 ps.append(dict(num=str(n),x=x,y=y,w=w+.1,h=h+.1,radius=.1,layers=('F.Cu','F.Mask'),mask=-.05,function=fn[n],exposed_w=w,exposed_h=h))
 ps.append(dict(num='',x=x,y=y,w=w,h=h,radius=.05,layers=('F.Paste',)))
emit('TI_DMQ0006A_TPS6282xA_1.5x1.5_SMD_DrawingVerified','TPS6282xADMQ',(1.5,1.5),(1.55,1.55),(1.25,1.05),ps,'https://www.ti.com/lit/ds/symlink/tps62827.pdf','3,32-34',1.0,'SMD preferred example. Selected copper overlap 0.05 mm each side equals TI minimum: left copper 0.70x0.35, right 1.10x0.30; explicit mask aperture offset -0.05 exposes 0.60x0.25 / 1.00x0.20. Independent paste-only R0.05 apertures equal exposed area. TI example 0.125 mm stencil. Body center is origin; asymmetric centers -0.65 / +0.45. NO center exposed pad.',marker=(-1.12,-.94))

# YCG0015 4224261/B 08/2019. SMD preferred, 0.2 mm opening, minimum 0.0325 overlap.
ps=[];fn={'A1':'AGND','A2':'VSET_PG','A3':'VOS',**{r+str(c):v for r,v in [('B','PGND'),('C','SW'),('D','VIN')] for c in [1,2,3]},'E1':'EN','E2':'SDA','E3':'SCL'}
for ri,row in enumerate('ABCDE'):
 for c in [1,2,3]:
  x=(c-2)*.35;y=(ri-2)*.35;n=row+str(c)
  ps.append(dict(num=n,x=x,y=y,w=.265,h=.265,shape='circle',layers=('F.Cu','F.Mask'),mask=-.0325,function=fn[n],exposed_w=.2,exposed_h=.2))
  ps.append(dict(num='',x=x,y=y,w=.21,h=.21,radius=.05,layers=('F.Paste',)))
emit('TI_YCG0015_TPS628640_1.05x1.78_P0.35_SMD_DrawingVerified','TPS628640BYCGR',(1.05,1.78),(1.07,1.80),(.80,1.15),ps,'https://www.ti.com/lit/ds/symlink/tps62864.pdf','4,30-32',.5,'SMD preferred. Selected copper diameter 0.265, explicit -0.0325 mm mask aperture offset gives diameter 0.200 opening, exactly TI minimum overlap. The paste aperture is a 0.21 mm R0.05 rounded SQUARE, not a circle. TI example 0.075 mm stencil. Adjacent copper clearance is only 0.085 mm; needs manufacturer acceptance/HDI escape assessment. A1 upper-left.',marker=(-.70,-1.04))

(MECH/'small-parts-footprint-spec.json').write_text(json.dumps(models,indent=2)+'\n')
with (MECH/'small-parts-pad-coordinate-audit.csv').open('w') as fd:
 cols=['footprint','mpn','pad','function','x_mm','y_mm','copper_w_mm','copper_h_mm','exposed_w_mm','exposed_h_mm','mask_margin_mm','source_url','source_pages'];w=csv.DictWriter(fd,cols);w.writeheader()
 for m in models:
  for p in m['pads']:
   if not p['num']:continue
   mask=p['mask'];w.writerow(dict(zip(cols,[m['name'],m['mpn'],p['num'],p.get('function',''),f(p['x']),f(p['y']),f(p['w']),f(p['h']),f(p.get('exposed_w',p['w'])),f(p.get('exposed_h',p['h'])),f(mask),m['source_url'],m['source_pages']])))
(OUT/'fp-lib-table').write_text('(fp_lib_table\n  (version 7)\n  (lib (name "CMK230_Verified")(type "KiCad")(uri "${KIPRJMOD}/CMK230_Verified.pretty")(options "")(descr "Drawing-verified TI footprints; read mechanical audit before manufacture"))\n)\n')
print(f'Wrote {len(models)} footprints; {sum(m["electrical_pad_count"] for m in models)} numbered copper pads')
