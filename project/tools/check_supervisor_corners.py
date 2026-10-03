#!/usr/bin/env python3
from pathlib import Path
import json,csv
B=Path(__file__).resolve().parents[1]; rows=[]
# Total resistor error includes initial tolerance and temperature drift, not merely room-temperature tolerance.
for name,rt,rb,minop,maxop,supply_min,supply_max in [
 ('CORE',8450,10000,.72,.88,.790814,.807595),('CPU',8450,10000,.72,.88,.792,.808),('KPU',8450,10000,.72,.88,.792,.808),
 ('DDR_IO',16800,10000,1.06,1.17,None,None),('DDR_CORE',8900,10000,.744,.88,.790814-.4*.00025,.807595),
 ('VDD1P8',33200,10000,1.7,1.95,1.779626,1.820426),('VDD3V3',66500,10000,2.97,3.63,3.279444,3.356676),
 ('MIPI0P8',8900,10000,.744,.88,.790814-.1*.1,.807595)]:
 tol=.0015; quad=name in ['CORE','CPU','KPU','VDD3V3']; bias=25e-9 if quad else 50e-9; vmin=.396 if quad else .3968; vmax=.404 if quad else .4032; hyst=.010 if quad else .0032
 lo=vmin*(1+rt*(1-tol)/(rb*(1+tol)))-bias*rt*(1+tol)
 hi=vmax*(1+rt*(1+tol)/(rb*(1-tol)))+bias*rt*(1+tol)
 rise=(vmax+hyst)*(1+rt*(1+tol)/(rb*(1-tol)))+bias*rt*(1+tol)
 if name in ['CORE','DDR_IO','VDD1P8','VDD3V3','DDR_CORE','MIPI0P8']:
  # TPS6282xA FB0.6V ±1%; feedback resistors total0.1% in existing circuit budget.
  feedback_top={'CORE':33200,'DDR_IO':86600,'VDD1P8':200000,'VDD3V3':453000,'DDR_CORE':33200,'MIPI0P8':33200}[name]
  supply_min=.6*.99*(1+feedback_top*(1-tol)/(100000*(1+tol)));supply_max=.6*1.01*(1+feedback_top*(1+tol)/(100000*(1-tol)))
  if name=='DDR_CORE':supply_min-=.4*.00025
  if name=='MIPI0P8':supply_min-=.1*.1
 rows.append(dict(rail=name,supervisor='TPS386000' if quad else 'TPS3850H01',top_ohm=rt,bottom_ohm=rb,total_resistor_tolerance_fraction=tol,trip_low_V=lo,trip_high_V=hi,release_high_V=rise,operating_min_V=minop,operating_max_V=maxop,source_static_min_V=supply_min,source_static_max_V=supply_max,static_restart_margin_V=supply_min-rise,static_min_voltage_margin_V=supply_min-minop,static_max_voltage_margin_V=maxop-supply_max,classification='STATIC_ONLY_RIPPLE_DISTRIBUTION_RESPONSE_AND_TEMPERATURE_QUALIFICATION_REQUIRED'))
for r in rows:
 assert r['trip_low_V']>r['operating_min_V'],r
 assert r['release_high_V']<r['source_static_min_V'],r
 assert r['source_static_max_V']<r['operating_max_V'],r
p=B/'engineering/reset/tps3850-candidate-corners.json';p.write_text(json.dumps(rows,indent=2))
with p.with_suffix('.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
for r in rows:print(r['rail'], 'trip low',round(r['trip_low_V'],6),'release high',round(r['release_high_V'],6),'restart margin mV',round(r['static_restart_margin_V']*1000,3))
