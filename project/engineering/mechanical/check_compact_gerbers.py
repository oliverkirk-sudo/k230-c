#!/usr/bin/env python3
"""Check native Gerber output against an independent drawing transcription."""
from pathlib import Path
import re,json
M=Path(__file__).resolve().parent
centers={'U301':(5,5),'U302':(14,5),'U303':(23,5),'U304':(5,15)}
# Entries are relative x,y,width,height,corner radius. All three are roundrects.
drl=[(-.74,-.5,.67,.3,.05),(-.74,0,.67,.3,.05),(-.74,.5,.67,.3,.05),(.74,.5,.67,.3,.05),(.74,-.5,.67,.3,.05)]
dck=[(-1.1,-.65,.95,.4,.05),(-1.1,0,.95,.4,.05),(-1.1,.65,.95,.4,.05),(1.1,.65,.95,.4,.05),(1.1,-.65,.95,.4,.05)]
drv=[(-.975,-.65,.45,.3,.05),(-.975,0,.45,.3,.05),(-.975,.65,.45,.3,.05),(.975,.65,.45,.3,.05),(.975,0,.45,.3,.05),(.975,-.65,.45,.3,.05)]
base={'U301':drl,'U302':dck,'U303':drv+[(0,0,1,1.6,.05)]};base['U304']=[(-.74,-.5,.67,.3,.05),(-.74,0,.67,.3,.05),(-.74,.5,.67,.3,.05),(.74,.5,.67,.3,.05),(.74,0,.67,.3,.05),(.74,-.5,.67,.3,.05)];report={}
for layer,ext in [('F_Cu','gtl'),('F_Mask','gts'),('F_Paste','gtp')]:
 expected={k:list(v) for k,v in base.items()}
 if layer=='F_Mask':expected={k:[(x,y,w+.1,h+.1,r+.05) for x,y,w,h,r in v] for k,v in base.items()}
 if layer=='F_Paste':expected['U303']=drv+[(0,-.45,1,.7,.05),(0,.45,1,.7,.05)]
 t=(M/'compact-qa-gerbers'/f'Compact_Package_Geometry_QA_ONLY-{layer}.{ext}').read_text();aps={}
 for n,params in re.findall(r'%ADD(\d+)RoundRect,([^*]+)\*%',t):
  a=[float(z) for z in params.split('X')];r=a[0];aps[int(n)]=(max(a[1:9:2])-min(a[1:9:2])+2*r,max(a[2:9:2])-min(a[2:9:2])+2*r,r)
 seen=[];ref=None;ap=None
 for line in t.splitlines():
  if m:=re.match(r'%TO.[CP],(U\d+)(?:,[^*]+)?\*%',line):ref=m[1]
  elif m:=re.match(r'D(\d+)\*',line):ap=int(m[1])
  elif m:=re.match(r'X(-?\d+)Y(-?\d+)D03\*',line):
   x=int(m[1])/1e6-centers[ref][0];y=-int(m[2])/1e6-centers[ref][1];w,h,r=aps[ap]
   ix=next(i for i,e in enumerate(expected[ref]) if abs(e[0]-x)<1e-6 and abs(e[1]-y)<1e-6)
   for a,b in zip((x,y,w,h,r),expected[ref][ix]):assert abs(a-b)<2e-6,(layer,ref,ix,a,b)
   seen.append((ref,ix))
 assert len(seen)==len(set(seen))==sum(len(v) for v in expected.values())
 report[layer]={'status':'PASS','checked_flashes':len(seen),'checked_properties':['component-side coordinate','copper/mask/paste layer','rounded-rectangle width and height','corner radius','EP split-paste positions']}
(M/'compact-gerber-verification.json').write_text(json.dumps({'scope':'Native compact-candidate QA export only; not manufacturing release','layers':report},indent=2)+'\n');print(json.dumps(report,indent=2))
