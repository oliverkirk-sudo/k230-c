#!/usr/bin/env python3
from pathlib import Path
import xml.etree.ElementTree as E,json,re
B=Path(__file__).resolve().parents[1];P=B/'cad/high-temp-candidate';x=E.parse(P/'master.xml');pn={}
for n in x.findall('.//nets/net'):
 for z in n.findall('node'):pn[(z.get('ref'),z.get('pin'))]=n.get('name')
v={c.get('ref'):c.findtext('value') for c in x.findall('.//components/comp')};tol=.007;bias=50e-9;out=[];rescount=capcount=0
for name,net,top,lo_limit,hi_limit in [('CORE','VDD0P8_CORE',3320,.72,.88),('DDR','VDD1P1_DDR_IO',8660,1.06,1.17),('1V8','VDD1P8',20000,1.7,1.95),('3V3','VDD_3V3',45300,3.07,3.6)]:
 fb='FB_'+name
 toprefs=[r for r in v if r.startswith('R') and pn.get((r,'1'))==net and pn.get((r,'2'))==fb]
 botrefs=[r for r in v if r.startswith('R') and pn.get((r,'1'))==fb and pn.get((r,'2'))=='GND']
 caps=[r for r in v if r.startswith('C') and pn.get((r,'1'))==net and pn.get((r,'2'))==fb]
 assert len(toprefs)==len(botrefs)==len(caps)==1
 tr,br,cr=toprefs[0],botrefs[0],caps[0]
 assert float(v[tr].split('k')[0])*1000==top
 assert float(v[br].split('k')[0])*1000==10000
 assert 'TNPW0402' in v[tr] and '10ppm' in v[tr] and 'TOTAL<=0.70pct' in v[tr]
 assert v[cr].startswith('1.2nF')
 assert abs(top*1.2e-9-(top*10)*120e-12)<1e-15
 lo=.6*.99*(1+top*(1-tol)/(10000*(1+tol)))-bias*top*(1+tol)
 hi=.6*1.01*(1+top*(1+tol)/(10000*(1-tol)))+bias*top*(1+tol)
 assert lo>lo_limit and hi<hi_limit
 out.append(dict(rail=name,net=net,top_reference=tr,bottom_reference=br,feedforward_reference=cr,top_ohm=top,bottom_ohm=10000,feedforward_F=1.2e-9,nominal_V=.6*(1+top/10000),static_min_with_bias_V=lo,static_max_with_bias_V=hi,min_limit_V=lo_limit,max_limit_V=hi,low_budget_V=lo-lo_limit,high_budget_V=hi_limit-hi))
 rescount+=2;capcount+=1
r={'status':'CONDITIONAL_STATIC_SCREEN_NOT_QUALIFICATION','total_resistor_error':tol,'FB_reference_error':.01,'FB_bias_envelope_A':bias,'verified_resistors':rescount,'verified_feedforward_caps':capcount,'source':'https://www.ti.com/lit/ds/symlink/tps62827.pdf section8.2.2.2 equation5','rails':out,'assumptions':['Total0.70% is a declared screening allowance, not merely initial tolerance.','CandidateTNPW0402 0.1%/10ppm reduces temperature contribution; actual mission/life/assembly environment must be reviewed.','All ripple/distribution/loop/transient margin remains to be qualified.','Divider dissipation increases by about0.380mW total; no rail nominal changed.']}
(P/'scaled-feedback-validation.json').write_text(json.dumps(r,indent=2));print('PASS',rescount,'feedback resistors and',capcount,'scaled feedforward capacitors')
