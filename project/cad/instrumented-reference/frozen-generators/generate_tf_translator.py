#!/usr/bin/env python3
"""Candidate isolation subcircuit only. Boot/power readiness remains an integration gate."""
import pathlib,uuid,json,csv
root=pathlib.Path(__file__).resolve().parents[1];out=root/'cad/tf-translator';out.mkdir(exist_ok=True)
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
  text=[f'(symbol "TFTranslator:{name}" (pin_names hide) (pin_numbers hide) (in_bom yes) (on_board yes) (property "Reference" "{name}" (at 0 {h+3} 0) (effects (font (size 1.27 1.27)))) (property "Value" "{name}" (at 0 {h+1} 0) (effects (font (size 1.27 1.27)))) (symbol "{name}_1_1" '+''.join(shape)]
  for num,yy,ang in [('1',py,270),('2',-py,90)]:text.append(f'(pin passive line (at 0 {yy} {ang}) (length {length}) (name "~" (effects (font (size 1 1)))) (number "{num}" (effects (font (size 1 1)))))')
  text.append('))');symbols[name]={'str':'\n'.join(text),'positions':pos,'h':h};return
 # tuple(number,name,type), top-to-bottom actual pin numbers, not package geometry
 h=max(5.08,(len(pins)-1)*1.27+2.54);s=[f'(symbol "TFTranslator:{name}" (pin_names (offset 1.016)) (in_bom yes) (on_board yes) (property "Reference" "U" (at 0 {h+3} 0) (effects (font (size 1.27 1.27)))) (property "Value" "{name}" (at 0 {h+1} 0) (effects (font (size 1.27 1.27)))) (symbol "{name}_1_1" (rectangle (start -12.7 {h}) (end 12.7 {-h}) (stroke (width .254) (type default)) (fill (type background)))']
 pos={}
 for i,(num,n,typ) in enumerate(pins):
  y=(len(pins)-1)*1.27-i*2.54;pos[str(num)]=(-17.78,y)
  s.append(f'(pin {typ} line (at -17.78 {y:.4f} 0) (length 5.08) (name "{n}" (effects (font (size .9 .9)))) (number "{num}" (effects (font (size .9 .9)))))')
 s.append('))');symbols[name]={'str':'\n'.join(s),'positions':pos,'h':h}
def comp(name,ref,value,x,y,nets,dnp=False):
 comps.append((name,ref,value,x,y,nets,dnp))


symbol('NVT4858_HK',[(1,'DAT2A','bidirectional'),(2,'DAT3A','bidirectional'),(3,'DAT0A','bidirectional'),(4,'DAT1A','bidirectional'),(5,'CLKA','input'),(6,'CLK_FB','output'),(7,'GND','power_in'),(8,'CLKB','output'),(9,'DAT1B','bidirectional'),(10,'DAT0B','bidirectional'),(11,'DAT3B','bidirectional'),(12,'DAT2B','bidirectional'),(13,'CMDB','bidirectional'),(14,'VCCB','power_in'),(15,'VCCA','power_in'),(16,'CMDA','bidirectional')])
symbol('C',[(1,'1','passive'),(2,'2','passive')])
comp('NVT4858_HK','U95','NVT4858HKZ TF HS50 CANDIDATE',100.33,116.84,{'1':'TF_HOST_D2','2':'TF_HOST_D3','3':'TF_HOST_D0','4':'TF_HOST_D1','5':'TF_HOST_CLK','7':'GND','8':'TFCARD_CLK','9':'TFCARD_D1','10':'TFCARD_D0','11':'TFCARD_D3','12':'TFCARD_D2','13':'TFCARD_CMD','14':'VDD_3V3','15':'VDD1P8','16':'TF_HOST_CMD'})
comp('C','C815','1uF X5R/X7R ESR<0.5Ohm',275.59,81.28,{'1':'VDD1P8','2':'GND'})
comp('C','C816','100nF X5R/X7R',275.59,144.78,{'1':'VDD_3V3','2':'GND'})
sch=[]
if __name__=='__main__':
 for name,ref,val,x,y,nets,dnp in comps:
  for p,n in nets.items():connectivity.append({'reference':ref,'part':val,'pin':p,'net':n})
 with (root/'engineering/storage/tf-translator-pin-net-matrix.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=connectivity[0]);w.writeheader();w.writerows(connectivity)
 print(len(comps),'components',len(connectivity),'pins')
