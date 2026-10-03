#!/usr/bin/env python3
"""Candidate isolation subcircuit only. Boot/power readiness remains an integration gate."""
import pathlib,uuid,json,csv
root=pathlib.Path(__file__).resolve().parents[1];out=root/'cad/supervisor';out.mkdir(exist_ok=True)
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
  text=[f'(symbol "Supervisor:{name}" (pin_names hide) (pin_numbers hide) (in_bom yes) (on_board yes) (property "Reference" "{name}" (at 0 {h+3} 0) (effects (font (size 1.27 1.27)))) (property "Value" "{name}" (at 0 {h+1} 0) (effects (font (size 1.27 1.27)))) (symbol "{name}_1_1" '+''.join(shape)]
  for num,yy,ang in [('1',py,270),('2',-py,90)]:text.append(f'(pin passive line (at 0 {yy} {ang}) (length {length}) (name "~" (effects (font (size 1 1)))) (number "{num}" (effects (font (size 1 1)))))')
  text.append('))');symbols[name]={'str':'\n'.join(text),'positions':pos,'h':h};return
 # tuple(number,name,type), top-to-bottom actual pin numbers, not package geometry
 h=max(5.08,(len(pins)-1)*1.27+2.54);s=[f'(symbol "Supervisor:{name}" (pin_names (offset 1.016)) (in_bom yes) (on_board yes) (property "Reference" "U" (at 0 {h+3} 0) (effects (font (size 1.27 1.27)))) (property "Value" "{name}" (at 0 {h+1} 0) (effects (font (size 1.27 1.27)))) (symbol "{name}_1_1" (rectangle (start -12.7 {h}) (end 12.7 {-h}) (stroke (width .254) (type default)) (fill (type background)))']
 pos={}
 for i,(num,n,typ) in enumerate(pins):
  y=(len(pins)-1)*1.27-i*2.54;pos[str(num)]=(-17.78,y)
  s.append(f'(pin {typ} line (at -17.78 {y:.4f} 0) (length 5.08) (name "{n}" (effects (font (size .9 .9)))) (number "{num}" (effects (font (size .9 .9)))))')
 s.append('))');symbols[name]={'str':'\n'.join(s),'positions':pos,'h':h}
def comp(name,ref,value,x,y,nets,dnp=False):
 comps.append((name,ref,value,x,y,nets,dnp))


symbol('R',[(1,'1','passive'),(2,'2','passive')]);symbol('C',[(1,'1','passive'),(2,'2','passive')])
symbol('TPS386000_RGP',[(1,'MR','input'),(2,'CT4_OPEN','passive'),(3,'CT3_OPEN','passive'),(4,'CT2_OPEN','passive'),(5,'CT1_OPEN','passive'),(6,'SENSE4H_UNUSED','input'),(7,'SENSE4L','input'),(8,'SENSE3','input'),(9,'SENSE2','input'),(10,'SENSE1','input'),(11,'NC_GND_RECOMMENDED','passive'),(12,'GND','power_in'),(13,'VREF_UNUSED','output'),(14,'VDD','power_in'),(15,'RESET1_OD','open_collector'),(16,'RESET2_OD','open_collector'),(17,'RESET3_OD','open_collector'),(18,'RESET4_OD','open_collector'),(19,'WDO_UNUSED','open_collector'),(20,'WDI','input'),(21,'EP_GND','power_in')])
symbol('TPS3850H01_DRC',[(1,'VDD','power_in'),(2,'CWD_NC_DISABLE','passive'),(3,'SET0','input'),(4,'CRST','passive'),(5,'GND','power_in'),(6,'SET1','input'),(7,'WDI','input'),(8,'WDO_UNUSED','open_collector'),(9,'RESET_OD','open_collector'),(10,'SENSE','input'),(11,'EP_GND','power_in')])
symbol('TPS3808G01_DBV',[(1,'RESET_OD','open_collector'),(2,'GND','power_in'),(3,'MR','input'),(4,'CT_NC_20MS','passive'),(5,'SENSE','input'),(6,'VDD','power_in')])
symbol('AUP1G17_DBV',[(1,'NC','no_connect'),(2,'A','input'),(3,'GND','power_in'),(4,'Y','output'),(5,'VCC','power_in')])
symbol('AUP1G07_DBV',[(1,'NC','no_connect'),(2,'A','input'),(3,'GND','power_in'),(4,'Y_OD','open_collector'),(5,'VCC','power_in')])
symbol('AUP1G06_DBV',[(1,'NC','no_connect'),(2,'A','input'),(3,'GND','power_in'),(4,'Y_OD','open_collector'),(5,'VCC','power_in')])
symbol('AUP1G08_DBV',[(1,'A','input'),(2,'B','input'),(3,'GND','power_in'),(4,'Y','output'),(5,'VCC','power_in')])
rn=500;cn=800
monitors=[('CORE','VDD0P8_CORE','8.45k'),('CPU','VDD0P8_CPU','8.45k'),('KPU','VDD0P8_KPU','8.45k'),('DDR_IO','VDD1P1_DDR_IO','16.8k'),('DDR_CORE','VDD0P8_DDR_CORE','8.9k'),('1V8','VDD1P8','33.2k'),('3V3','VDD_3V3','66.5k'),('MIPI0P8','AVDD0P8_MIPI','8.9k')]
for j,(role,rail,rt) in enumerate(monitors):
 x=100.33+(j%4)*276.86;y=88.9+(j//4)*238.76;sense='SENSE_'+role;ct='RESET_T_'+role
 if j==0:
  comp('TPS386000_RGP','U81','TPS386000RGPR WIDE-MARGIN RAILS',x,y,{'1':'VIN_5V','6':'GND','7':'SENSE_3V3','8':'SENSE_KPU','9':'SENSE_CPU','10':'SENSE_CORE','11':'GND','12':'GND','14':'VIN_5V','15':'ALL_RAILS_GOOD_3V3','16':'ALL_RAILS_GOOD_3V3','17':'ALL_RAILS_GOOD_3V3','18':'ALL_RAILS_GOOD_3V3','20':'GND','21':'GND'})
 elif j not in [1,2,6]:
  comp('TPS3850H01_DRC',f'U{81+j}','TPS3850H01DRCR PRECISION DOMAIN',x,y,{'1':'VIN_5V','3':'VIN_5V','4':ct,'5':'GND','6':'GND','7':'GND','9':'ALL_RAILS_GOOD_3V3','10':sense,'11':'GND'})
 for val,a,z,dx,dy in [(rt+' total<=0.15%',rail,sense,-25.4,83.82),('10k total<=0.15%',sense,'GND',93.98,83.82),('10k 8.5-11.5ms','VIN_5V',ct,-25.4,147.32)]:
  rn+=1
  if not ('8.5-11.5ms' in val and j in [0,1,2,6]):comp('R',f'R{rn}',val,x+dx,y+dy,{'1':a,'2':z})
 cn+=1
 if j not in [1,2,6]:comp('C',f'C{cn}','100nF',x+93.98,y+147.32,{'1':'VIN_5V','2':'GND'})
# Independent supply-loss guard is powered from held-up 1V8, not from VIN.
comp('TPS3808G01_DBV','U89','TPS3808G01DBVR VIN GUARD',100.33,566.42,{'1':'ALL_RAILS_GOOD_3V3','2':'GND','3':'VDD1P8','5':'VIN_GUARD_SENSE','6':'VDD1P8'})
comp('R','R525','88.7k total<=0.15%',75.0,647.7,{'1':'VIN_5V','2':'VIN_GUARD_SENSE'})
comp('R','R526','10k total<=0.15%',190.5,647.7,{'1':'VIN_GUARD_SENSE','2':'GND'})
comp('R','R527','10k RAW PG PULLUP',75.0,713.74,{'1':'VDD_3V3','2':'ALL_RAILS_GOOD_3V3'})
comp('C','C809','100nF',190.5,713.74,{'1':'VDD1P8','2':'GND'})
# Preserve external RSTN as an input, do not drive the carrier's reset net.
comp('AUP1G08_DBV','U94','SN74AUP1G08DBVR RESET REQUEST',377.19,566.42,{'1':'RAILS_GOOD_LOGIC_1V8','2':'RSTN','3':'GND','4':'RESET_RELEASE_REQUEST_1V8','5':'VDD1P8'})
comp('TPS3808G01_DBV','U90','TPS3808G01DBVR RESET DELAY',654.05,566.42,{'1':'SOC_RSTN','2':'GND','3':'RESET_RELEASE_REQUEST_1V8','5':'VDD1P8','6':'VDD1P8'})
comp('AUP1G07_DBV','U91','SN74AUP1G07DBVR FAULT CLAMP',930.91,566.42,{'2':'RESET_RELEASE_REQUEST_1V8','3':'GND','4':'SOC_RSTN','5':'VDD1P8'})
comp('R','R530','100k SOC RESET PULLUP',654.05,647.7,{'1':'VDD1P8','2':'SOC_RSTN'})
# Hardware qualification link is DNP by default; it is not an OTP programmer.
comp('AUP1G08_DBV','U92','SN74AUP1G08DBVR QUALIFY',377.19,721.36,{'1':'RAILS_GOOD_LOGIC_1V8','2':'BOOT_VOLTAGE_QUALIFIED_1V8','3':'GND','4':'STORAGE_ENABLE_1V8','5':'VDD1P8'})
comp('AUP1G06_DBV','U93','SN74AUP1G06DBVR DISABLE',930.91,721.36,{'2':'STORAGE_ENABLE_1V8','3':'GND','4':'GLOBAL_DISABLE','5':'VDD1P8'})
comp('R','R528','0R QUALIFICATION STRAP DNP',515.62,721.36,{'1':'VDD1P8','2':'BOOT_VOLTAGE_QUALIFIED_1V8'},True)
comp('R','R529','100k DEFAULT INHIBIT',654.05,721.36,{'1':'BOOT_VOLTAGE_QUALIFIED_1V8','2':'GND'})
for j,ref in enumerate(['U94','U90','U91','U92','U93']):
 comp('C',f'C{810+j}','100nF '+ref,350.52+j*160.02,802.64,{'1':'VDD1P8','2':'GND'})
comp('AUP1G17_DBV','U96','SN74AUP1G17DBVR PG SCHMITT',377.19,647.7,{'2':'ALL_RAILS_GOOD_3V3','3':'GND','4':'RAILS_GOOD_LOGIC_1V8','5':'VDD1P8'})
comp('C','C817','100nF U96',510.54,647.7,{'1':'VDD1P8','2':'GND'})
sch=[]
if __name__=='__main__':
 (root/'engineering/reset').mkdir(exist_ok=True)
 for name,ref,val,x,y,nets,dnp in comps:
  for p,n in nets.items():connectivity.append({'reference':ref,'part':val,'pin':p,'net':n,'dnp':dnp})
 with (root/'engineering/reset/supervisor-pin-net-matrix.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=connectivity[0]);w.writeheader();w.writerows(connectivity)
 print(len(comps),'components',len(connectivity),'pins')
