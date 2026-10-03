#!/usr/bin/env python3
"""Generate interface-only KiCad assets, never fabrication outputs."""
import re, pathlib, json, uuid, csv
ROOT=pathlib.Path(__file__).resolve().parents[1]
SRC=ROOT/'source-interface'
def parse(p):return [dict(re.findall(r'\|([^=|]+)=([^|\r\n]*)',l)) for l in p.read_text().splitlines()]
pins=sorted([r for r in parse(SRC/'CM-K230.schdoc') if r.get('RECORD')=='2'],key=lambda r:int(r['DESIGNATOR']))
pads=sorted([r for r in parse(SRC/'CM-K230.pcbdoc') if r.get('RECORD')=='Pad'],key=lambda r:int(r['NAME']))
assert len(pins)==len(pads)==140
assert [int(r['DESIGNATOR']) for r in pins]==list(range(1,141))
mm=lambda v:float(v.removesuffix('mil'))*.0254
cx=mm('3769.5276mil'); cy=mm('3784.3480mil')
fp=['(footprint "CMK230_Carrier_Mating_ONLY" (version 20241229) (generator "cmk230_contract") (layer "F.Cu") (descr "Carrier mating lands from 01Studio; NOT castellated module fabrication") (attr smd)', '(fp_text reference "REF**" (at 0 -21) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))', '(fp_text value "CMK230_Carrier_Mating_ONLY" (at 0 21) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))','(fp_rect (start -19 -19) (end 19 19) (stroke (width .15) (type default)) (fill none) (layer "F.Fab"))']
coords=[]
for p in pads:
 n=int(p['NAME']); x=mm(p['X'])-cx;y=cy-mm(p['Y']);angle=-float(p['ROTATION']);sx=mm(p['XSIZE']);sy=mm(p['YSIZE'])
 fp.append(f'(pad "{n}" smd oval (at {x:.6f} {y:.6f} {angle}) (size {sx:.6f} {sy:.6f}) (layers "F.Cu" "F.Paste" "F.Mask") (solder_mask_margin 0.0508))')
 coords.append(dict(pin=n,x_mm=round(x,6),y_mm=round(y,6),rotation_deg=angle,pad_x_mm=round(sx,6),pad_y_mm=round(sy,6),kind='carrier_smd_land_not_castellation'))
fp.append('(fp_rect (start -19.80 -19.80) (end 19.80 19.80) (stroke (width 0.05) (type default)) (fill none) (layer "F.CrtYd"))');fp.append(')');(ROOT/'cad/CMK230.pretty/CMK230_Carrier_Mating_ONLY.kicad_mod').write_text('\n'.join(fp))
with (ROOT/'data/mating_land_coordinates.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=coords[0].keys());w.writeheader();w.writerows(coords)
u=lambda:str(uuid.uuid4())
parts=['(symbol "CMK230_Interface_Contract" (pin_names (offset 1.016)) (in_bom yes) (on_board yes) (property "Reference" "M" (at 0 47.5 0) (effects (font (size 1.27 1.27)))) (property "Value" "INTERFACE_ONLY" (at 0 45 0) (effects (font (size 1.27 1.27)))) (property "Footprint" "CMK230:CMK230_Carrier_Mating_ONLY" (at 0 0 0) (effects (font (size 1 1)) hide))']
for unit in range(1,5):
 parts.append(f'(symbol "CMK230_Interface_Contract_{unit}_1" (rectangle (start -25.4 44.45) (end 25.4 -44.45) (stroke (width .254) (type default)) (fill (type background)))')
 for i,p in enumerate(pins[(unit-1)*35:unit*35]):
  yy=43.18-i*2.54
  parts.append(f'(pin passive line (at -30.48 {yy:.2f} 0) (length 5.08) (name "{p["NAME"]}" (effects (font (size 1 1)))) (number "{p["DESIGNATOR"]}" (effects (font (size 1 1)))))')
 parts.append(')')
parts.append(')'); sym='\n'.join(parts)
(ROOT/'cad/CMK230.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "cmk230_contract")\n'+sym+'\n)')
rid=u(); sch=[f'(kicad_sch (version 20250114) (generator "cmk230_contract") (uuid "{rid}") (paper "A3") (title_block (title "CM-K230 interface contract ONLY - no internal circuit") (rev "D0")) (lib_symbols '+sym.replace('(symbol "CMK230_Interface_Contract"','(symbol "CMK230:CMK230_Interface_Contract"',1)+')']
for unit,(x,y) in enumerate([(86.36,76.2),(254,76.2),(86.36,200.66),(254,200.66)],1):
 sch.append(f'(symbol (lib_id "CMK230:CMK230_Interface_Contract") (at {x} {y} 0) (unit {unit}) (in_bom yes) (on_board yes) (dnp no) (uuid "{u()}") (property "Reference" "M1" (at {x} {y-48} 0) (effects (font (size 1.27 1.27)))) (property "Value" "INTERFACE_ONLY" (at {x} {y-45} 0) (effects (font (size 1.27 1.27)))) (instances (project "CMK230_Interface_ONLY" (path "/{rid}" (reference "M1") (unit {unit})))))')
sch.append('(text "D0 REVIEW ONLY: Pin names verified from module symbol. All passive types deliberate. No SoC, DDR, PMIC or internal nets. NOT FOR FABRICATION." (at 15 270 0) (effects (font (size 1.27 1.27)) (justify left))) (embedded_fonts no))')
(ROOT/'cad/CMK230_Interface_ONLY.kicad_sch').write_text('\n'.join(sch))
(ROOT/'cad/sym-lib-table').write_text('(sym_lib_table (lib (name "CMK230") (type "KiCad") (uri "${KIPRJMOD}/CMK230.kicad_sym") (options "") (descr "Interface only")))')
(ROOT/'cad/fp-lib-table').write_text('(fp_lib_table (lib (name "CMK230") (type "KiCad") (uri "${KIPRJMOD}/CMK230.pretty") (options "") (descr "CARRIER footprint only")))')
print('Generated140 carrier lands and140 symbol pins; source geometry preserved')
