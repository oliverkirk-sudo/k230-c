#!/usr/bin/env python3
"""Candidate isolation subcircuit only. Boot/power readiness remains an integration gate."""
import pathlib,uuid,json,csv
root=pathlib.Path(__file__).resolve().parents[1];out=root/'cad/decoupling';out.mkdir(exist_ok=True)
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
  text=[f'(symbol "Decoupling:{name}" (pin_names hide) (pin_numbers hide) (in_bom yes) (on_board yes) (property "Reference" "{name}" (at 0 {h+3} 0) (effects (font (size 1.27 1.27)))) (property "Value" "{name}" (at 0 {h+1} 0) (effects (font (size 1.27 1.27)))) (symbol "{name}_1_1" '+''.join(shape)]
  for num,yy,ang in [('1',py,270),('2',-py,90)]:text.append(f'(pin passive line (at 0 {yy} {ang}) (length {length}) (name "~" (effects (font (size 1 1)))) (number "{num}" (effects (font (size 1 1)))))')
  text.append('))');symbols[name]={'str':'\n'.join(text),'positions':pos,'h':h};return
 # tuple(number,name,type), top-to-bottom actual pin numbers, not package geometry
 h=max(5.08,(len(pins)-1)*1.27+2.54);s=[f'(symbol "Decoupling:{name}" (pin_names (offset 1.016)) (in_bom yes) (on_board yes) (property "Reference" "U" (at 0 {h+3} 0) (effects (font (size 1.27 1.27)))) (property "Value" "{name}" (at 0 {h+1} 0) (effects (font (size 1.27 1.27)))) (symbol "{name}_1_1" (rectangle (start -12.7 {h}) (end 12.7 {-h}) (stroke (width .254) (type default)) (fill (type background)))']
 pos={}
 for i,(num,n,typ) in enumerate(pins):
  y=(len(pins)-1)*1.27-i*2.54;pos[str(num)]=(-17.78,y)
  s.append(f'(pin {typ} line (at -17.78 {y:.4f} 0) (length 5.08) (name "{n}" (effects (font (size .9 .9)))) (number "{num}" (effects (font (size .9 .9)))))')
 s.append('))');symbols[name]={'str':'\n'.join(s),'positions':pos,'h':h}
def comp(name,ref,value,x,y,nets,dnp=False):
 comps.append((name,ref,value,x,y,nets,dnp))

symbol('C',[(1,'1','passive'),(2,'2','passive')])
groups=[('VDD0P8_CORE',['4.7uF']*2+['100nF']*14,'NEW per-power-ball baseline'),('VDD0P8_CPU',['4.7uF']+['100nF']*3,'NEW per-power-ball baseline'),('VDD0P8_KPU',['4.7uF']*2+['100nF']*6,'NEW per-power-ball baseline'),('VDD0P8_DDR_CORE',['4.7uF']+['100nF']*4,'NEW per-power-ball baseline'),('VDD1P1_DDR_IO',['4.7uF']+['100nF']*5,'SoC DDR IO reference-style'),('VDD1P1_DDR_IO',['22uF','4.7uF']+['100nF']*10,'DRAM VDD2 source C20-C31'),('VDD1P1_DDR_IO',['22uF','4.7uF']+['100nF']*8,'DRAM VDDQ source C40-C49'),('VDD1P8',['22uF','4.7uF']+['100nF']*6,'DRAM VDD1 source C32-C39')]+[(f'BANK{i}_VDDIO',['100nF'],'IO-bank reference-style') for i in range(6)]+[('VDD1P8',['100nF','100nF'],'SoC generic1.8 baseline')]
alloc=[];n=500
for gi,(net,vals,why) in enumerate(groups):
 for j,val in enumerate(vals):
  x=76.2+j*66.04;y=55.88+gi*48.26;n+=1;comp('C',f'C{n}',val,x,y,{'1':net,'2':'GND'});alloc.append({'reference':f'C{n}','net':net,'value':val,'basis':why,'placement':'TOP only; no geometry assigned; group location must follow power balls'})
with (root/'engineering/decoupling-allocation.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=alloc[0]);w.writeheader();w.writerows(alloc)
sch=[f'(kicad_sch (version 20250114) (generator "cmk230_decoupling") (uuid "{rid}") (paper "A0") (title_block (title "Local decoupling allocation - layout and PI unverified") (rev "D1-subcircuit")) (lib_symbols '+''.join(s['str'] for s in symbols.values())+')']
for name,ref,value,x,y,nets,dnp in comps:
 h=symbols[name]['h'];sch.append(f'(symbol (lib_id "Decoupling:{name}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp {"yes" if dnp else "no"}) (uuid "{u()}") (property "Reference" "{ref}" (at {x} {y-h-5} 0) (effects (font (size 1.27 1.27)))) (property "Value" "{value}" (at {x} {y-h-2.5} 0) (effects (font (size 1 1)))) (instances (project "CMK230_Decoupling_CANDIDATE" (path "/{rid}" (reference "{ref}") (unit 1)))))')
 for p,n in nets.items():
  dx,dy=symbols[name]['positions'][p];px=x+dx;py=y-dy;lx=px-7.62
  sch.append(f'(wire (pts (xy {px:.4f} {py:.4f}) (xy {lx:.4f} {py:.4f})) (stroke (width 0) (type default)) (uuid "{u()}"))')
  sch.append(f'(label "{n}" (at {lx:.4f} {py:.4f} 0) (effects (font (size 1 1)) (justify right bottom)) (uuid "{u()}"))')
  connectivity.append({'reference':ref,'part':value,'pin':p,'net':n})
for yy,txt in [(15,'DECOUPLING ALLOCATION: reference DRAM groups + new split-digital-domain baseline; all top-side placement remains to be solved.'),(24,'Group rows are not PCB positions. Generic cap values are not procurement-qualified MPNs; verify effective capacitance/ESL/ESR and SI/PI.'),(800,'No bottom-side components allowed. Higher capacitor count does not prove low inductance or feasible BGA escape. Complete rail budget and placement audit required.')]:
 sch.append(f'(text "{txt}" (at 15 {yy} 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "{u()}"))')
sch.append('(embedded_fonts no))');(out/'CMK230_Decoupling_CANDIDATE.kicad_sch').write_text('\n'.join(sch))
(out/'CMK230_Decoupling_CANDIDATE.kicad_pro').write_text(json.dumps({'meta':{'filename':'CMK230_Decoupling_CANDIDATE.kicad_pro','version':1}},indent=2))
(out/'Decoupling.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "cmk230_decoupling")'+''.join(s['str'].replace('Decoupling:','',1) for s in symbols.values())+')')
(out/'sym-lib-table').write_text('(sym_lib_table (lib (name "Decoupling") (type "KiCad") (uri "${KIPRJMOD}/Decoupling.kicad_sym") (options "") (descr "Verified bias topology, values subject to final review")))')
with (root/'engineering/decoupling-pin-net-matrix.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=connectivity[0]);w.writeheader();w.writerows(connectivity)
print(len(comps),'components,',len(connectivity),'pin-net assignments')
