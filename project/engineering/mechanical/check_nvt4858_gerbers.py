#!/usr/bin/env python3
"""Check actual KiCad Gerber rectangular flashes against independent source values."""
from pathlib import Path
import re,json
M=Path(__file__).resolve().parent
expected=[(-.6,-.6,.9,.22),(-.625,-.2,.85,.22),(-.625,.2,.85,.22),(-.625,.6,.85,.22),
          (-.6,1.175,.22,.55),(-.2,1.175,.22,.55),(.2,1.175,.22,.55),(.6,1.175,.22,.55),
          (.625,.6,.85,.22),(.625,.2,.85,.22),(.625,-.2,.85,.22),(.625,-.6,.85,.22),
          (.6,-1.175,.22,.55),(.2,-1.175,.22,.55),(-.2,-1.175,.22,.55),(-.6,-1.175,.22,.55)]
report={}
for layer,ext,offset in [('F_Cu','gtl',0),('F_Mask','gts',.1),('F_Paste','gtp',-.05)]:
 t=(M/'nvt4858-qa-gerbers'/f'NVT4858_Geometry_QA_ONLY-{layer}.{ext}').read_text()
 apertures={int(n):(float(w),float(h)) for n,w,h in re.findall(r'%ADD(\d+)R,([\d.]+)X([\d.]+)\*%',t)}
 seen=[];ap=None
 for line in t.splitlines():
  if m:=re.fullmatch(r'D(\d+)\*',line):ap=int(m[1])
  if m:=re.fullmatch(r'X(-?\d+)Y(-?\d+)D03\*',line):
   x=int(m[1])/1e6-5;y=-int(m[2])/1e6-5
   ix=next(i for i,e in enumerate(expected) if abs(e[0]-x)<1e-7 and abs(e[1]-y)<1e-7)
   w,h=apertures[ap];e=expected[ix];assert abs(w-e[2]-offset)<1e-7 and abs(h-e[3]-offset)<1e-7
   seen.append(ix)
 assert len(seen)==len(set(seen))==16
 report[layer]={'status':'PASS','checked_rectangular_flashes':16,'coordinates_sizes_and_layer_checked':True}
(M/'nvt4858-gerber-verification.json').write_text(json.dumps({'scope':'Isolated native Gerber geometry only','layers':report},indent=2)+'\n');print(json.dumps(report,indent=2))
