#!/usr/bin/env python3
"""Verify actual plotted Gerber coordinates and sizes against source values."""
import json,re
from pathlib import Path
M=Path(__file__).resolve().parent
expected=[(4.025,4.35),(4.025,5),(4.025,5.65),(5.975,5.65),(5.975,4.35),
          (10.025,4.35),(10.025,5),(10.025,5.65),(11.975,5.65),(11.975,5),(11.975,4.35)]
report={}
for layer,ext,size in [('F_Cu','gtl',(.75,.4)),('F_Mask','gts',(.85,.5)),('F_Paste','gtp',(.65,.3))]:
 t=(M/'nexperia-standard-qa-gerbers'/f'Nexperia_Standard_Geometry_QA_ONLY-{layer}.{ext}').read_text()
 apertures={int(n):(float(w),float(h))for n,w,h in re.findall(r'%ADD(\d+)R,([\d.]+)X([\d.]+)\*%',t)}
 seen=[];ap=None
 for line in t.splitlines():
  if m:=re.fullmatch(r'D(\d+)\*',line):ap=int(m[1])
  if m:=re.fullmatch(r'X(-?\d+)Y(-?\d+)D03\*',line):
   x,y=int(m[1])/1e6,-int(m[2])/1e6
   ix=next(i for i,e in enumerate(expected)if abs(e[0]-x)<1e-7 and abs(e[1]-y)<1e-7)
   assert all(abs(a-b)<1e-7 for a,b in zip(apertures[ap],size))
   seen.append(ix)
 assert len(seen)==len(set(seen))==11
 report[layer]={'status':'PASS','rectangular_flashes':11,'size_mm':size,'exact_positions_checked':True}
(M/'nexperia-standard-gerber-verification.json').write_text(json.dumps({'scope':'Isolated native Gerbers only, two package samples','layers':report},indent=2)+'\n')
print(json.dumps(report,indent=2))
