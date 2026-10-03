#!/usr/bin/env python3
"""Candidate isolation subcircuit only. Boot/power readiness remains an integration gate."""
import pathlib,uuid,json,csv
root=pathlib.Path(__file__).resolve().parents[1];out=root/'cad/core-aux';out.mkdir(exist_ok=True)
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
  text=[f'(symbol "CoreAux:{name}" (pin_names hide) (pin_numbers hide) (in_bom yes) (on_board yes) (property "Reference" "{name}" (at 0 {h+3} 0) (effects (font (size 1.27 1.27)))) (property "Value" "{name}" (at 0 {h+1} 0) (effects (font (size 1.27 1.27)))) (symbol "{name}_1_1" '+''.join(shape)]
  for num,yy,ang in [('1',py,270),('2',-py,90)]:text.append(f'(pin passive line (at 0 {yy} {ang}) (length {length}) (name "~" (effects (font (size 1 1)))) (number "{num}" (effects (font (size 1 1)))))')
  text.append('))');symbols[name]={'str':'\n'.join(text),'positions':pos,'h':h};return
 # tuple(number,name,type), top-to-bottom actual pin numbers, not package geometry
 h=max(5.08,(len(pins)-1)*1.27+2.54);s=[f'(symbol "CoreAux:{name}" (pin_names (offset 1.016)) (in_bom yes) (on_board yes) (property "Reference" "U" (at 0 {h+3} 0) (effects (font (size 1.27 1.27)))) (property "Value" "{name}" (at 0 {h+1} 0) (effects (font (size 1.27 1.27)))) (symbol "{name}_1_1" (rectangle (start -12.7 {h}) (end 12.7 {-h}) (stroke (width .254) (type default)) (fill (type background)))']
 pos={}
 for i,(num,n,typ) in enumerate(pins):
  y=(len(pins)-1)*1.27-i*2.54;pos[str(num)]=(-17.78,y)
  s.append(f'(pin {typ} line (at -17.78 {y:.4f} 0) (length 5.08) (name "{n}" (effects (font (size .9 .9)))) (number "{num}" (effects (font (size .9 .9)))))')
 s.append('))');symbols[name]={'str':'\n'.join(s),'positions':pos,'h':h}
def comp(name,ref,value,x,y,nets,dnp=False):
 comps.append((name,ref,value,x,y,nets,dnp))

symbol('K230_AUX_SUBSET',[("B12","CLK32K768_XIN","input"),("A12","CLK32K768_XOUT","output"),("B8","CLK24M_XIN","input"),("A8","CLK24M_XOUT","output"),("B9","RSTN","input"),("C8","GPIO0_BOOT0","input"),("C9","GPIO1_BOOT1","input")])
symbol('R',[(1,'1','passive'),(2,'2','passive')]);symbol('C',[(1,'1','passive'),(2,'2','passive')])
symbol('XTAL2',[(1,'1','passive'),(2,'2','passive')]);symbol('XTAL4_REF',[(1,'XTAL','passive'),(2,'GND','passive'),(3,'XTAL','passive'),(4,'GND','passive')])
comp('K230_AUX_SUBSET','U1','K230 SYSTEM BALLS ONLY',91.44,63.5,{'B12':'RTC_XIN','A12':'RTC_XOUT','B8':'CLK24_XIN','A8':'CLK24_XOUT','B9':'RSTN','C8':'BOOT0','C9':'BOOT1'})
comp('XTAL2','Y1','32.768kHz / MPN TBD',228.6,50.8,{'1':'RTC_XOUT','2':'RTC_XIN'})
comp('R','R41','1M REF',365.76,50.8,{'1':'RTC_XOUT','2':'RTC_XIN'})
comp('C','C41','12pF REF / TUNE',228.6,81.28,{'1':'RTC_XOUT','2':'GND'})
comp('C','C42','12pF REF / TUNE',365.76,81.28,{'1':'RTC_XIN','2':'GND'})
comp('XTAL4_REF','Y2','X322524MOB4SI 24MHz CL12pF CANDIDATE',91.44,119.38,{'1':'CLK24_XOUT','2':'GND','3':'CLK24_XIN','4':'GND'})
comp('R','R42','1M REF',228.6,119.38,{'1':'CLK24_XOUT','2':'CLK24_XIN'})
comp('C','C43','12pF REF / TUNE',365.76,111.76,{'1':'CLK24_XOUT','2':'GND'})
comp('C','C44','12pF REF / TUNE',365.76,142.24,{'1':'CLK24_XIN','2':'GND'})
comp('R','R43','100k REF',91.44,170.18,{'1':'VDD_1V8','2':'RSTN'})
comp('C','C45','100nF REF',228.6,170.18,{'1':'RSTN','2':'GND'})
comp('R','R44','10k BOOT0 LOW',91.44,210.82,{'1':'BOOT0','2':'GND'})
comp('R','R45','10k BOOT0 HIGH / DNP',182.88,210.82,{'1':'BOOT0','2':'VDD_1V8'},True)
comp('R','R46','10k BOOT1 HIGH',274.32,210.82,{'1':'BOOT1','2':'VDD_1V8'})
comp('R','R47','10k BOOT1 LOW / DNP',365.76,210.82,{'1':'BOOT1','2':'GND'},True)
sch=[f'(kicad_sch (version 20250114) (generator "cmk230_core_aux") (uuid "{rid}") (paper "A3") (title_block (title "K230 clocks reset and boot - reference adaptation ONLY") (rev "D1-subcircuit")) (lib_symbols '+''.join(s['str'] for s in symbols.values())+')']
for name,ref,value,x,y,nets,dnp in comps:
 h=symbols[name]['h'];sch.append(f'(symbol (lib_id "CoreAux:{name}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp {"yes" if dnp else "no"}) (uuid "{u()}") (property "Reference" "{ref}" (at {x} {y-h-5} 0) (effects (font (size 1.27 1.27)))) (property "Value" "{value}" (at {x} {y-h-2.5} 0) (effects (font (size 1 1)))) (instances (project "CMK230_Clock_Reset_REFERENCE" (path "/{rid}" (reference "{ref}") (unit 1)))))')
 for p,n in nets.items():
  dx,dy=symbols[name]['positions'][p];px=x+dx;py=y-dy;lx=px-7.62
  sch.append(f'(wire (pts (xy {px:.4f} {py:.4f}) (xy {lx:.4f} {py:.4f})) (stroke (width 0) (type default)) (uuid "{u()}"))')
  sch.append(f'(label "{n}" (at {lx:.4f} {py:.4f} 0) (effects (font (size 1 1)) (justify right bottom)) (uuid "{u()}"))')
  connectivity.append({'reference':ref,'part':value,'pin':p,'net':n})
for yy,txt in [(15,'REFERENCE ADAPTATION ONLY: K230 symbol is 7 balls, not full SoC. Source CanMV-K230 V1.0 sheet 1.'),(240,'12pF and 1M are source-reference values. Select exact crystals; tune CL/ESR/drive/startup with actual PCB parasitics.'),(247,'RSTN RC is not a rail-good supervisor. Power/reset sequencer remains separate; keep external module reset behavior.'),(254,'BOOT0 low / BOOT1 high targets documented MMC0 baseline. Do not tie storage MODE_TF to BOOT straps without ROM verification.')]:
 sch.append(f'(text "{txt}" (at 15 {yy} 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "{u()}"))')
sch.append('(embedded_fonts no))');(out/'CMK230_Clock_Reset_REFERENCE.kicad_sch').write_text('\n'.join(sch))
(out/'CMK230_Clock_Reset_REFERENCE.kicad_pro').write_text(json.dumps({'meta':{'filename':'CMK230_Clock_Reset_REFERENCE.kicad_pro','version':1}},indent=2))
(out/'CoreAux.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "cmk230_aux")'+''.join(s['str'].replace('CoreAux:','',1) for s in symbols.values())+')')
(out/'sym-lib-table').write_text('(sym_lib_table (lib (name "CoreAux") (type "KiCad") (uri "${KIPRJMOD}/CoreAux.kicad_sym") (options "") (descr "K230 auxiliary reference subset")))')
with (root/'engineering/core-aux-pin-net-matrix.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=connectivity[0]);w.writeheader();w.writerows(connectivity)
print(len(comps),'components,',len(connectivity),'pin-net assignments')
