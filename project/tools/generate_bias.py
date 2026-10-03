#!/usr/bin/env python3
"""Candidate isolation subcircuit only. Boot/power readiness remains an integration gate."""
import pathlib,uuid,json,csv
root=pathlib.Path(__file__).resolve().parents[1];out=root/'cad/bias';out.mkdir(exist_ok=True)
u=lambda:str(uuid.uuid4());rid=u();symbols={}; comps=[]; connectivity=[]
def symbol(name,pins):

 if name in ['R','C','L','FB']:
  length=2.54 if name!='C' else 3.175
  py=7.62 if name=='L' else 3.81 if name=='C' else 5.08
  shape=[]
  if name=='C':
   for yy in [.635,-.635]:shape.append(f'(polyline (pts (xy -2.54 {yy}) (xy 2.54 {yy})) (stroke (width .254) (type default)) (fill (type none)))')
  elif name=='L':
   for top in [5.08,2.54,0,-2.54]:shape.append(f'(arc (start 0 {top}) (mid 1.27 {top-1.27}) (end 0 {top-2.54}) (stroke (width .254) (type default)) (fill (type none)))')
  else:
   shape.append('(rectangle (start -1.016 2.54) (end 1.016 -2.54) (stroke (width .254) (type default)) (fill (type none)))')
   if name=='FB':shape.append('(polyline (pts (xy -1.27 -2.54) (xy 1.27 2.54)) (stroke (width .254) (type default)) (fill (type none)))')
  pos={'1':(0,py),'2':(0,-py)};h=py
  text=[f'(symbol "Bias:{name}" (pin_names hide) (pin_numbers hide) (in_bom yes) (on_board yes) (property "Reference" "{name}" (at 0 {h+3} 0) (effects (font (size 1.27 1.27)))) (property "Value" "{name}" (at 0 {h+1} 0) (effects (font (size 1.27 1.27)))) (symbol "{name}_1_1" '+''.join(shape)]
  for num,yy,ang in [('1',py,270),('2',-py,90)]:text.append(f'(pin passive line (at 0 {yy} {ang}) (length {length}) (name "~" (effects (font (size 1 1)))) (number "{num}" (effects (font (size 1 1)))))')
  text.append('))');symbols[name]={'str':'\n'.join(text),'positions':pos,'h':h};return
 # tuple(number,name,type), top-to-bottom actual pin numbers, not package geometry
 h=max(5.08,(len(pins)-1)*1.27+2.54);s=[f'(symbol "Bias:{name}" (pin_names (offset 1.016)) (in_bom yes) (on_board yes) (property "Reference" "U" (at 0 {h+3} 0) (effects (font (size 1.27 1.27)))) (property "Value" "{name}" (at 0 {h+1} 0) (effects (font (size 1.27 1.27)))) (symbol "{name}_1_1" (rectangle (start -12.7 {h}) (end 12.7 {-h}) (stroke (width .254) (type default)) (fill (type background)))']
 pos={}
 for i,(num,n,typ) in enumerate(pins):
  y=(len(pins)-1)*1.27-i*2.54;pos[str(num)]=(-17.78,y)
  s.append(f'(pin {typ} line (at -17.78 {y:.4f} 0) (length 5.08) (name "{n}" (effects (font (size .9 .9)))) (number "{num}" (effects (font (size .9 .9)))))')
 s.append('))');symbols[name]={'str':'\n'.join(s),'positions':pos,'h':h}
def comp(name,ref,value,x,y,nets,dnp=False):
 comps.append((name,ref,value,x,y,nets,dnp))

for name in ['R','C']:symbol(name,[(1,'1','passive'),(2,'2','passive')])
items=[('R','R61','10k REF','LPDDR4_ODT_A','VDD1P1_DDR_IO'),('R','R62','10k REF','LPDDR4_ODT_B','VDD1P1_DDR_IO'),('R','R63','240R 1% REF','LPDDR4_ZQ','VDD1P1_DDR_IO'),('R','R64','240R 1% REF','DDR_ZN','GND'),('R','R65','240R 1% REF','VDD1P1_DDR_IO','DDR_VREF'),('R','R66','240R 1% REF','DDR_VREF','GND'),('C','C61','100nF REF','VDD1P1_DDR_IO','DDR_VREF'),('C','C62','100nF REF','DDR_VREF','GND'),('R','R67','30k 1% REF','VIN_5V','USB0_VBUS'),('R','R68','30k 1% REF','VIN_5V','USB1_VBUS'),('R','R69','200R 1% REF','USB0_TXRTUNE','GND'),('R','R70','200R 1% REF','USB1_TXRTUNE','GND'),('R','R71','200R 1% REF','MIPI_REXT','GND'),('C','C63','100nF REF','CODEC_VCM','GND'),('C','C64','2.2uF/6.3V OLIMEX REF','EMMC_VDDI','GND'),('C','C65','220nF OLIMEX REF','EMMC_VDDI','GND'),('C','C66','4.7uF CHECKLIST REF','CODEC_VCM','GND'),('C','C67','4.7uF CHECKLIST REF','MIC_BIAS','GND'),('C','C68','100nF CHECKLIST REF','MIC_BIAS','GND'),('C','C69','2.2uF EMMC LOCAL CANDIDATE','VEMMC_IO','GND'),('C','C70','100nF EMMC LOCAL CANDIDATE','VEMMC_IO','GND'),('C','C71','2.2uF EMMC LOCAL CANDIDATE','VDD_3V3','GND'),('C','C72','100nF EMMC LOCAL CANDIDATE','VDD_3V3','GND')]
for i,(kind,ref,value,a,b) in enumerate(items):comp(kind,ref,value,76.2+(i%4)*91.44,50.8+(i//4)*53.34,{'1':a,'2':b})
sch=[f'(kicad_sch (version 20250114) (generator "cmk230_bias") (uuid "{rid}") (paper "A3") (title_block (title "DDR USB MIPI bias - reference adaptation") (rev "D1-subcircuit")) (lib_symbols '+''.join(s['str'] for s in symbols.values())+')']
for name,ref,value,x,y,nets,dnp in comps:
 h=symbols[name]['h'];sch.append(f'(symbol (lib_id "Bias:{name}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp {"yes" if dnp else "no"}) (uuid "{u()}") (property "Reference" "{ref}" (at {x} {y-h-5} 0) (effects (font (size 1.27 1.27)))) (property "Value" "{value}" (at {x} {y-h-2.5} 0) (effects (font (size 1 1)))) (instances (project "CMK230_Bias_REFERENCE" (path "/{rid}" (reference "{ref}") (unit 1)))))')
 for p,n in nets.items():
  dx,dy=symbols[name]['positions'][p];px=x+dx;py=y-dy;lx=px-7.62
  sch.append(f'(wire (pts (xy {px:.4f} {py:.4f}) (xy {lx:.4f} {py:.4f})) (stroke (width 0) (type default)) (uuid "{u()}"))')
  sch.append(f'(label "{n}" (at {lx:.4f} {py:.4f} 0) (effects (font (size 1 1)) (justify right bottom)) (uuid "{u()}"))')
  connectivity.append({'reference':ref,'part':value,'pin':p,'net':n})
for yy,txt in [(15,'REFERENCE BIAS: sources 01Studio board sheets1/2/4 and Canaan guide. Not a fabrication release.'),(240,'C61 is across the TOP VREF resistor, not another VREF-to-ground capacitor. Divider tracks the 1.1V DDR rail.'),(247,'TEST_EN A9 is grounded in master. EMMC_VDDI is an internal regulator node, NEVER an external 1.8V supply input.'),(254,'C64+C65 follow OLIMEX same-base-part3V3 reference. Samsung1V8/ESR qualification remains open.')]:
 sch.append(f'(text "{txt}" (at 15 {yy} 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "{u()}"))')
sch.append('(embedded_fonts no))');(out/'CMK230_Bias_REFERENCE.kicad_sch').write_text('\n'.join(sch))
(out/'CMK230_Bias_REFERENCE.kicad_pro').write_text(json.dumps({'meta':{'filename':'CMK230_Bias_REFERENCE.kicad_pro','version':1}},indent=2))
(out/'Bias.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "cmk230_bias")'+''.join(s['str'].replace('Bias:','',1) for s in symbols.values())+')')
(out/'sym-lib-table').write_text('(sym_lib_table (lib (name "Bias") (type "KiCad") (uri "${KIPRJMOD}/Bias.kicad_sym") (options "") (descr "Verified bias topology, values subject to final review")))')
with (root/'engineering/bias-pin-net-matrix.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=connectivity[0]);w.writeheader();w.writerows(connectivity)
print(len(comps),'components,',len(connectivity),'pin-net assignments')
