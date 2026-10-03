#!/usr/bin/env python3
"""Candidate isolation subcircuit only. Boot/power readiness remains an integration gate."""
import pathlib,uuid,json,csv
root=pathlib.Path(__file__).resolve().parents[1];out=root/'cad/power';out.mkdir(exist_ok=True)
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
  text=[f'(symbol "Power:{name}" (pin_names hide) (pin_numbers hide) (in_bom yes) (on_board yes) (property "Reference" "{name}" (at 0 {h+3} 0) (effects (font (size 1.27 1.27)))) (property "Value" "{name}" (at 0 {h+1} 0) (effects (font (size 1.27 1.27)))) (symbol "{name}_1_1" '+''.join(shape)]
  for num,yy,ang in [('1',py,270),('2',-py,90)]:text.append(f'(pin passive line (at 0 {yy} {ang}) (length {length}) (name "~" (effects (font (size 1 1)))) (number "{num}" (effects (font (size 1 1)))))')
  text.append('))');symbols[name]={'str':'\n'.join(text),'positions':pos,'h':h};return
 # tuple(number,name,type), top-to-bottom actual pin numbers, not package geometry
 h=max(5.08,(len(pins)-1)*1.27+2.54);s=[f'(symbol "Power:{name}" (pin_names (offset 1.016)) (in_bom yes) (on_board yes) (property "Reference" "U" (at 0 {h+3} 0) (effects (font (size 1.27 1.27)))) (property "Value" "{name}" (at 0 {h+1} 0) (effects (font (size 1.27 1.27)))) (symbol "{name}_1_1" (rectangle (start -12.7 {h}) (end 12.7 {-h}) (stroke (width .254) (type default)) (fill (type background)))']
 pos={}
 for i,(num,n,typ) in enumerate(pins):
  y=(len(pins)-1)*1.27-i*2.54;pos[str(num)]=(-17.78,y)
  s.append(f'(pin {typ} line (at -17.78 {y:.4f} 0) (length 5.08) (name "{n}" (effects (font (size .9 .9)))) (number "{num}" (effects (font (size .9 .9)))))')
 s.append('))');symbols[name]={'str':'\n'.join(s),'positions':pos,'h':h}
def comp(name,ref,value,x,y,nets,dnp=False):
 comps.append((name,ref,value,x,y,nets,dnp))

symbol('TPS6282xA_DMQ',[(1,'EN','input'),(2,'PG_OD','open_collector'),(3,'FB','input'),(4,'GND','power_in'),(5,'SW','power_out'),(6,'VIN','power_in')])
symbol('TPS628640B_YCG',[("A1","AGND","power_in"),("A2","VSET_FAULT_HIGH","passive"),("A3","VOS","input"),("B1","PGND","power_in"),("B2","PGND","power_in"),("B3","PGND","power_in"),("C1","SW","power_out"),("C2","SW","passive"),("C3","SW","passive"),("D1","VIN","power_in"),("D2","VIN","power_in"),("D3","VIN","power_in"),("E1","EN","input"),("E2","SDA","bidirectional"),("E3","SCL","input")])
for name in ['R','C','L','FB']:symbol(name,[(1,'1','passive'),(2,'2','passive')])
cnum=200;rnum=200
rail_specs=[]
def cap(val,x,y,net):
 global cnum;cnum+=1;comp('C',f'C{cnum}',val,x,y,{'1':net,'2':'GND'})
def res(val,x,y,a,b):
 global rnum;rnum+=1;comp('R',f'R{rnum}',val,x,y,{'1':a,'2':b})
# Six separate rails; no startup-address trick and no merging CPU/KPU into CORE.
rails=[(21,'CORE','VDD0P8_CORE','TPS62827ADMQ','33.2k total_error<=0.15%',190.5,88.9),(22,'CPU','VDD0P8_CPU','TPS628640BYCGR',None,546.1,88.9),(23,'KPU','VDD0P8_KPU','TPS628640BYCGR',None,901.7,88.9),(24,'DDR','VDD1P1_DDR_IO','TPS62826ADMQ','86.6k total_error<=0.15%',190.5,378.46),(25,'1V8','VDD1P8','TPS62825ADMQ','200k total_error<=0.15%',546.1,378.46),(26,'3V3','VDD_3V3','TPS62826ADMQ','453k total_error<=0.15%',901.7,378.46)]
for n,role,outnet,mpn,rt,x,y in rails:
 en='CORE_ENABLE' if n==21 else 'CORE_PGOOD_5V';sw=f'SW_{role}'
 if rt:
  fb=f'FB_{role}';pg='CORE_PGOOD_5V' if n==21 else 'FIXED_RAILS_PGOOD_3V3'
  comp('TPS6282xA_DMQ',f'U{n}',mpn,x,y,{'1':en,'2':pg,'3':fb,'4':'GND','5':sw,'6':'VIN_5V'})
  comp('L',f'L{n}',('0.47uH XFL4015-471MEB REF' if n==21 else '0.47uH DFE201610E-R47M=P2 CANDIDATE'),x+127,y,{'1':sw,'2':outnet})
  cap('47uF X7R / Ceff>=10uF',x+127,y+66.04,outnet)
  res(rt,x-71.12,y+116.84,outnet,fb);res('100k total_error<=0.15%',x+30.48,y+116.84,fb,'GND')
  cnum+=1;comp('C',f'C{cnum}','120pF C0G',x+127,y+116.84,{'1':outnet,'2':fb})
  if n==21:res('100k',x+30.48,y+167.64,pg,'VIN_5V')
  else:rnum+=1 # retain reference-number stability; remove redundant 1V8 pull-up
  if n==21:res('10k',x-71.12,y+167.64,'CORE_ENABLE','VIN_5V')
 else:
  nets={'A1':'GND','A2':f'VSET_{role}','A3':outnet,'B1':'GND','B2':'GND','B3':'GND','C1':sw,'C2':sw,'C3':sw,'D1':'VIN_5V','D2':'VIN_5V','D3':'VIN_5V','E1':en,'E2':f'PWR_{role}_SDA','E3':f'PWR_{role}_SCL'}
  comp('TPS628640B_YCG',f'U{n}',mpn,x,y,nets)
  comp('L',f'L{n}','0.24uH DFE201612E-R24M REF',x+127,y,{'1':sw,'2':outnet})
  for dx in [-71.12,30.48,127]:cap('22uF X7R / total Ceff>=30uF',x+dx,y+116.84,outnet)
  res('56.2k 1% / 0.8V / addr0x49',x-71.12,y+167.64,f'VSET_{role}','GND')
  cap('100nF',x+127,y+167.64,'VIN_5V')
 cap('10uF 10V X7R',x-71.12,y+66.04,'VIN_5V');cap('10uF 10V X7R',x+30.48,y+66.04,'VIN_5V')
 if rt:cap('100nF',x+127,y+167.64,'VIN_5V')
 rail_specs.append({'reference':f'U{n}','role':role,'part':mpn,'output_net':outnet,'nominal_V':{'CORE':.7992,'CPU':.8,'KPU':.8,'DDR':1.1196,'1V8':1.8,'3V3':3.318}[role],'enable_net':en,'status':'candidate_not_thermal_or_loop_qualified'})
# Four private pullups: separate software I2C buses, both devices at 0x49.
for x,net in zip([190.5,426.72,662.94,899.16],['PWR_CPU_SCL','PWR_CPU_SDA','PWR_KPU_SCL','PWR_KPU_SDA']):res('4.7k',x,594.36,net,'VDD1P8')
# Reference-style domain isolation. DDR core link must have low resistance, not an arbitrary high-DCR ferrite.
filters=[('VDD0P8_CORE','VDD0P8_DDR_CORE','0R WSL060300000ZEA9 Rmax=0.25mOhm'),('VDD0P8_CORE','AVDD0P8_PLL','120Ohm@100MHz Rdc<=0.1Ohm'),('VDD0P8_CORE','AVDD0P8_MIPI','120Ohm@100MHz Rdc<=0.1Ohm'),('VDD1P8','VAA_DDR','120Ohm@100MHz Rdc<=0.1Ohm'),('VDD1P8','AVDD1P8_USB','120Ohm@100MHz Rdc<=0.1Ohm'),('VDD1P8','AVDD1P8_PMU','120Ohm@100MHz Rdc<=0.1Ohm'),('VDD1P8','AVDD1P8_MIPI','120Ohm@100MHz Rdc<=0.1Ohm'),('VDD1P8','AVDD1P8_ADC','120Ohm@100MHz Rdc<=0.1Ohm'),('VDD1P8','AVDD1P8_CODEC','120Ohm@100MHz Rdc<=0.1Ohm'),('VDD_3V3','AVDD3P3_USB','120Ohm@100MHz Rdc<=0.1Ohm'),('VDD_3V3','VDD3P3_SD','0R Rmax<=50mOhm')]
for i,(src,dst,val) in enumerate(filters):
 x=129.54+(i%6)*198.12;y=652.78+(i//6)*91.44
 if val.startswith('0R'):res(val,x,y,src,dst)
 else:comp('FB',f'FB{201+i}',val,x,y,{'1':src,'2':dst})
 cap('100nF REF / local PI UNQUALIFIED',x,y+27.94,dst)
 if dst=='AVDD1P8_PMU':cap('100nF local second PMU ball',x,y+55.88,dst)
# 01Studio CanMV-K230 V1.0 sheet4 C120/C121 and C122/C123: two local caps per MIPI rail.
cap('100nF MIPI source second ball',100,860,'AVDD1P8_MIPI')
cap('100nF MIPI source second ball',300,860,'AVDD0P8_MIPI')
# Assigned references intentionally avoid U1/U2/U3, selector and clock pages.
(root/'engineering/power').mkdir(exist_ok=True)
with (root/'engineering/power/rail-components.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=rail_specs[0]);w.writeheader();w.writerows(rail_specs)
sch=[f'(kicad_sch (version 20250114) (generator "cmk230_power_candidate") (uuid "{rid}") (paper "A0") (title_block (title "Six-rail power draft - sequencing and load validation incomplete") (rev "D1-subcircuit")) (lib_symbols '+''.join(s['str'] for s in symbols.values())+')']
for name,ref,value,x,y,nets,dnp in comps:
 h=symbols[name]['h'];sch.append(f'(symbol (lib_id "Power:{name}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp {"yes" if dnp else "no"}) (uuid "{u()}") (property "Reference" "{ref}" (at {x} {y-h-5} 0) (effects (font (size 1.27 1.27)))) (property "Value" "{value}" (at {x} {y-h-2.5} 0) (effects (font (size 1 1)))) (instances (project "CMK230_Power_CANDIDATE" (path "/{rid}" (reference "{ref}") (unit 1)))))')
 for p,n in nets.items():
  dx,dy=symbols[name]['positions'][p];px=x+dx;py=y-dy;lx=px-7.62
  sch.append(f'(wire (pts (xy {px:.4f} {py:.4f}) (xy {lx:.4f} {py:.4f})) (stroke (width 0) (type default)) (uuid "{u()}"))')
  sch.append(f'(label "{n}" (at {lx:.4f} {py:.4f} 0) (effects (font (size 1 1)) (justify right bottom)) (uuid "{u()}"))')
  connectivity.append({'reference':ref,'part':value,'pin':p,'net':n})
for yy,txt in [(15,'POWER CANDIDATE: no PCB/thermal/loop validation. CORE PG gates downstream EN; complete reset/storage readiness sequencer still required.'),(24,'CPU/KPU both cold-start 0.8V / I2C0x49 on separate PRIVATE software buses. GPIO ownership and true open-drain driver must be implemented.'),(805,'Input: nominal5V within each regulator limits. Capacitor EFFECTIVE values and inductor saturation/thermal corners must be checked before layout release.'),(813,'Analog filters follow reference strategy; this is not the complete SoC/DRAM decoupling network. Do not equate linked nets with qualified ripple/sequence.')]:
 sch.append(f'(text "{txt}" (at 15 {yy} 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "{u()}"))')
sch.append('(embedded_fonts no))');(out/'CMK230_Power_CANDIDATE.kicad_sch').write_text('\n'.join(sch))
(out/'CMK230_Power_CANDIDATE.kicad_pro').write_text(json.dumps({'meta':{'filename':'CMK230_Power_CANDIDATE.kicad_pro','version':1}},indent=2))
(out/'Power.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "cmk230_power")'+''.join(s['str'].replace('Power:','',1) for s in symbols.values())+')')
(out/'sym-lib-table').write_text('(sym_lib_table (lib (name "Power") (type "KiCad") (uri "${KIPRJMOD}/Power.kicad_sym") (options "") (descr "Candidate power rails only")))')
with (root/'engineering/power/power-pin-net-matrix.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=connectivity[0]);w.writeheader();w.writerows(connectivity)
print(len(comps),'components,',len(connectivity),'pin-net assignments')
