#!/usr/bin/env python3
"""Candidate isolation subcircuit only. Boot/power readiness remains an integration gate."""
import pathlib,uuid,json,csv
root=pathlib.Path(__file__).resolve().parents[1];out=root/'cad/storage';out.mkdir(exist_ok=True)
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
  text=[f'(symbol "Storage:{name}" (pin_names hide) (pin_numbers hide) (in_bom yes) (on_board yes) (property "Reference" "{name}" (at 0 {h+3} 0) (effects (font (size 1.27 1.27)))) (property "Value" "{name}" (at 0 {h+1} 0) (effects (font (size 1.27 1.27)))) (symbol "{name}_1_1" '+''.join(shape)]
  for num,yy,ang in [('1',py,270),('2',-py,90)]:text.append(f'(pin passive line (at 0 {yy} {ang}) (length {length}) (name "~" (effects (font (size 1 1)))) (number "{num}" (effects (font (size 1 1)))))')
  text.append('))');symbols[name]={'str':'\n'.join(text),'positions':pos,'h':h};return
 # tuple(number,name,type), top-to-bottom actual pin numbers, not package geometry
 h=max(5.08,(len(pins)-1)*1.27+2.54);s=[f'(symbol "Storage:{name}" (pin_names (offset 1.016)) (in_bom yes) (on_board yes) (property "Reference" "U" (at 0 {h+3} 0) (effects (font (size 1.27 1.27)))) (property "Value" "{name}" (at 0 {h+1} 0) (effects (font (size 1.27 1.27)))) (symbol "{name}_1_1" (rectangle (start -12.7 {h}) (end 12.7 {-h}) (stroke (width .254) (type default)) (fill (type background)))']
 pos={}
 for i,(num,n,typ) in enumerate(pins):
  y=(len(pins)-1)*1.27-i*2.54;pos[str(num)]=(-17.78,y)
  s.append(f'(pin {typ} line (at -17.78 {y:.4f} 0) (length 5.08) (name "{n}" (effects (font (size .9 .9)))) (number "{num}" (effects (font (size .9 .9)))))')
 s.append('))');symbols[name]={'str':'\n'.join(s),'positions':pos,'h':h}
def comp(name,ref,value,x,y,nets,dnp=False):
 comps.append((name,ref,value,x,y,nets,dnp))
rs={1:'S1B',2:'D1',3:'S2A',4:'S2B',5:'D2',6:'GND',7:'D3',8:'S3B',9:'S3A',10:'D4',11:'S4B',12:'S4A',13:'EN',14:'VDD',15:'SEL',16:'S1A'}
symbol('TMUX1574RSV',[(i,n,'power_in' if n in ['VDD','GND'] else 'input' if n in ['SEL','EN'] else 'passive') for i,n in rs.items()])
symbol('SN74LVC1G32DBV',[(1,'A','input'),(2,'B','input'),(3,'GND','power_in'),(4,'Y','output'),(5,'VCC','power_in')])
symbol('R',[(1,'1','passive'),(2,'2','passive')]);symbol('C',[(1,'1','passive'),(2,'2','passive')]);symbol('SJ2',[(1,'1','passive'),(2,'2','passive')])
channels={1:(2,16,1),2:(5,3,4),3:(7,9,8),4:(10,12,11)}
alloc=[('U11',1,'MMC0_CLK','EMMC_CLK','TF_HOST_CLK'),('U11',2,'MMC0_CMD','EMMC_CMD','TF_HOST_CMD'),('U11',3,'MMC0_D0','EMMC_DAT0','TF_HOST_D0'),('U11',4,'MMC0_D1','EMMC_DAT1','TF_HOST_D1'),('U12',1,'MMC0_D2','EMMC_DAT2','TF_HOST_D2'),('U12',2,'MMC0_D3','EMMC_DAT3','TF_HOST_D3'),('U12',3,'EMMC_RSTN','MMC0_RST_N','GND'),('U12',4,'GND','GND','GND')]+[('U13',i+1,f'MMC0_D{i+4}',f'EMMC_DAT{i+4}','GND') for i in range(4)]
for ref,x in [('U11',91.44),('U12',228.6),('U13',365.76)]:
 nets={'6':'GND','14':'VSW_3V3','15':'GND' if ref=='U13' else 'MODE_TF','13':'DISABLE_OR_TF' if ref=='U13' else 'GLOBAL_DISABLE'}
 for rr,ch,d,a,b in alloc:
  if rr==ref:
   for pin,net in zip(channels[ch],[d,a,b]):nets[str(pin)]=net
 comp('TMUX1574RSV',ref,'TMUX1574RSVR / CANDIDATE',x,71.12,nets)
comp('SN74LVC1G32DBV','U14','SN74LVC1G32DBVR',91.44,147.32,{'1':'GLOBAL_DISABLE','2':'MODE_TF','3':'GND','4':'DISABLE_OR_TF','5':'VSW_3V3'})
comp('R','R31','10k',228.6,134.62,{'1':'MODE_TF','2':'GND'})
comp('SJ2','JP1','OPEN=EMMC / CLOSED=TF; COLD ONLY',365.76,134.62,{'1':'MODE_TF','2':'VSW_3V3'},True)
comp('R','R32','10k',228.6,165.1,{'1':'GLOBAL_DISABLE','2':'VSW_3V3'})
comp('R','R33','10k',365.76,165.1,{'1':'DISABLE_OR_TF','2':'VSW_3V3'})
comp('R','R34','10k RESET BIAS',91.44,180.34,{'1':'EMMC_RSTN','2':'VEMMC_IO'})
for i,x in enumerate([91.44,182.88,274.32,365.76],1):comp('C',f'C{30+i}','100nF',x,210.82,{'1':'VSW_3V3','2':'GND'})
sch=[f'(kicad_sch (version 20250114) (generator "cmk230_storage_candidate") (uuid "{rid}") (paper "A3") (title_block (title "Cold storage selector - proposed subcircuit ONLY") (rev "D1-subcircuit")) (lib_symbols '+''.join(s['str'] for s in symbols.values())+')']
for name,ref,value,x,y,nets,dnp in comps:
 h=symbols[name]['h'];sch.append(f'(symbol (lib_id "Storage:{name}") (at {x} {y} 0) (unit 1) (in_bom yes) (on_board yes) (dnp {"yes" if dnp else "no"}) (uuid "{u()}") (property "Reference" "{ref}" (at {x} {y-h-5} 0) (effects (font (size 1.27 1.27)))) (property "Value" "{value}" (at {x} {y-h-2.5} 0) (effects (font (size 1 1)))) (instances (project "CMK230_Storage_Selector_CANDIDATE" (path "/{rid}" (reference "{ref}") (unit 1)))))')
 for p,n in nets.items():
  dx,dy=symbols[name]['positions'][p];px=x+dx;py=y-dy;lx=px-7.62
  sch.append(f'(wire (pts (xy {px:.4f} {py:.4f}) (xy {lx:.4f} {py:.4f})) (stroke (width 0) (type default)) (uuid "{u()}"))')
  sch.append(f'(label "{n}" (at {lx:.4f} {py:.4f} 0) (effects (font (size 1 1)) (justify right bottom)) (uuid "{u()}"))')
  connectivity.append({'reference':ref,'part':value,'pin':p,'net':n})
for yy,txt in [(15,'PROPOSED SWITCH SUBCIRCUIT. No internal core schematic/PCB completion or HS200 qualification implied.'),(240,'VSW_3V3 and GLOBAL_DISABLE are OFF-SHEET integration inputs. GLOBAL_DISABLE must stay HIGH until rails + ROM/PHY voltage are proven safe.'),(247,'Cold only: remove all power before changing JP1. Default OPEN = eMMC. Keep eMMC VCC=3.3V and VCCQ=1.8V powered in both modes.'),(254,'No level translation. Do not connect VDD3P3_SD to 1.8V. Boot straps, early-ROM signaling and sequencer implementation remain release gates.')]:
 sch.append(f'(text "{txt}" (at 15 {yy} 0) (effects (font (size 1.27 1.27)) (justify left)) (uuid "{u()}"))')
sch.append('(embedded_fonts no))');(out/'CMK230_Storage_Selector_CANDIDATE.kicad_sch').write_text('\n'.join(sch))
(out/'CMK230_Storage_Selector_CANDIDATE.kicad_pro').write_text(json.dumps({'meta':{'filename':'CMK230_Storage_Selector_CANDIDATE.kicad_pro','version':1}},indent=2))
(out/'Storage.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "cmk230_storage")'+''.join(s['str'].replace('Storage:','',1) for s in symbols.values())+')')
(out/'sym-lib-table').write_text('(sym_lib_table (lib (name "Storage") (type "KiCad") (uri "${KIPRJMOD}/Storage.kicad_sym") (options "") (descr "Candidate storage switching only")))')
with (root/'engineering/storage/switch-pin-net-matrix.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=connectivity[0]);w.writeheader();w.writerows(connectivity)
print(len(comps),'components,',len(connectivity),'pin-net assignments')
