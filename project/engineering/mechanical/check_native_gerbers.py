#!/usr/bin/env python3
"""Verify KiCad native QA Gerber flashes, aperture shapes, corner radii, coordinates.
Expected geometry is separately transcribed; does not use builder/spec.
This isolated QA board is NOT the CM-K230 module production Gerber.
"""
from pathlib import Path
import re,json,math
ROOT=Path(__file__).resolve().parent
centers={'U101':(7,7),'U102':(19,7),'U103':(7,17),'U104':(19,17)}
xy={
'U101':[(-.75,-.6),(-.8,-.2),(-.8,.2),(-.8,.6),(-.6,1.2),(-.2,1.2),(.2,1.2),(.6,1.2),(.8,.6),(.8,.2),(.8,-.2),(.8,-.6),(.6,-1.2),(.2,-1.2),(-.2,-1.2),(-.6,-1.2)],
'U102':[(-1.3,-.95),(-1.3,0),(-1.3,.95),(1.3,.95),(1.3,-.95)],
'U103':[(-.65,-.5),(-.65,0),(-.65,.5),(.45,.5),(.45,0),(.45,-.5)],
'U104':[((c-2)*.35,(r-2)*.35) for r in range(5) for c in range(1,4)]}
summary={'scope':'Native Gerber QA only; not production module output','layers':{}}
for lname,ext in [('F_Cu','gtl'),('F_Mask','gts'),('F_Paste','gtp')]:
 p=ROOT/'qa-gerbers'/f'Footprint_Geometry_QA_ONLY-{lname}.{ext}'
 text=p.read_text();aps={}
 for n,shape,params in re.findall(r'%ADD(\d+)(RoundRect|C),([^*]+)\*%',text):
  a=[float(z) for z in params.split('X')]
  if shape=='C':w=h=a[0];r=None
  else:
   r=a[0];xs=a[1:9:2];ys=a[2:9:2];w=max(xs)-min(xs)+2*r;h=max(ys)-min(ys)+2*r
  aps[int(n)]=(shape,w,h,r)
 flashes=[];active=None;ref=None
 for line in text.splitlines():
  if m:=re.match(r'%TO.[CP],(U\d+)(?:,[^*]+)?\*%',line):ref=m[1]
  elif m:=re.match(r'D(\d+)\*',line):active=int(m[1])
  elif m:=re.match(r'X(-?\d+)Y(-?\d+)D03\*',line):
   x=int(m[1])/1e6-centers[ref][0];y=-int(m[2])/1e6-centers[ref][1]
   ix=next(i for i,(xx,yy) in enumerate(xy[ref]) if abs(xx-x)<1e-6 and abs(yy-y)<1e-6)
   shape,w,h,r=aps[active]
   if ref=='U101':
    ew,eh=(.7,.2) if ix==0 else ((.6,.2) if ix in [1,2,3,8,9,10,11] else (.2,.6))
    er=.05;es='RoundRect'
    if lname=='F_Mask':ew+=.1;eh+=.1;er=.1
   elif ref=='U102':
    ew,eh,er,es=1.1,.6,.05,'RoundRect'
    if lname=='F_Mask':ew+=.1;eh+=.1;er=.1
   elif ref=='U103':
    ew,eh,er,es=(.6,.25,.05,'RoundRect') if ix<3 else (1.,.2,.05,'RoundRect')
    if lname=='F_Cu':ew+=.1;eh+=.1;er=.1
   else:
    ew=eh=.265 if lname=='F_Cu' else (.2 if lname=='F_Mask' else .21)
    er=.05 if lname=='F_Paste' else None;es='RoundRect' if lname=='F_Paste' else 'C'
   assert shape==es,(lname,ref,shape,es)
   for a,b in [(w,ew),(h,eh)]+([] if r is None else [(r,er)]):assert abs(a-b)<2e-6,(lname,ref,ix,a,b)
   flashes.append((ref,ix))
 assert len(flashes)==42 and len(set(flashes))==42
 assert set(flashes)=={(ref,i) for ref,lst in xy.items() for i in range(len(lst))}
 summary['layers'][lname]={'flash_count':len(flashes),'unique_positions':len(set(flashes)),'shape_dimension_corner_radius_checks':'PASS'}
summary['status']='PASS'
(ROOT/'native-gerber-verification.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
