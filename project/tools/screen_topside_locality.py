#!/usr/bin/env python3
"""Conditional X7R/full-core placement locality screen. Not electrical PCB layout."""
from pathlib import Path
import json,csv,random,math
B=Path(__file__).resolve().parents[1];D=B/'engineering/mechanical';H=B/'cad/high-temp-candidate'
base=json.load(open(H/'full-bom-area-screen.json'));parts={r['reference']:dict(r) for r in base['components'] if r['reservation_dense_mm2']>0}
for r in parts.values():r['size']=r['dense_reservation_xy_mm'];r['affinity']=None
for r in parts.values():
 if 'TNPW0402' in r['value']:r['size']=[2.1,1.2]
alloc=list(csv.DictReader(open(B/'engineering/decoupling-allocation.csv')))
for r in alloc:parts[r['reference']]['affinity']='U2' if r['basis'].startswith('DRAM') else 'U1'
for ref in ['C64','C65','C69','C70','C71','C72','R573']:
 if ref in parts:parts[ref]['affinity']='U3'
# Full stronger X7R sensitivity, never silently applied to schematic.
inputs={'U21':['C203'],'U22':['C210','C211'],'U23':['C216','C217'],'U24':['C220'],'U25':['C225'],'U26':['C230']}
for ref in ['C204','C221','C226','C231']:parts.pop(ref)
outputs={'U21':(['C201'],3,False),'U22':(['C206','C207','C208'],4,True),'U23':(['C212','C213','C214'],4,True),'U24':(['C218'],3,False),'U25':(['C223'],4,False),'U26':(['C228'],5,False)}
for u,refs in inputs.items():
 for ref in refs:parts[ref]['size']=[4.9,2.4];parts[ref]['affinity']=u
for u,(refs,count,big) in outputs.items():
 for i in range(count):
  ref=refs[i] if i<len(refs) else f'PROPOSED_{u}_COUT{i+1}'
  if ref not in parts:parts[ref]={'reference':ref,'dnp':False,'value':'additional X7R SCREEN ONLY'}
  parts[ref]['size']=[4.9,2.4] if big else [3,1.55];parts[ref]['affinity']=u
# Reuse only generic rectangle intersection/subtraction helpers, not old run.
s=(B/'tools/pack_component_envelopes.py').read_text();ns={};exec(s[s.index('def overlaps'):s.index('best=None')],ns);overlaps=ns['overlaps'];subtract=ns['subtract']
fixed={'U1':(2.7,2.7,13.5,13.5),'U2':(19,2.2,10.5,15),'U3':(2.7,19,12,13.5)}
fixed.update({'U21':(16.6,19,2.5,2.1),'U22':(0,0,1.6,2.3),'U23':(0,17,1.6,2.3),'U24':(31,0,2.5,2.1),'U25':(31,17.5,2.5,2.1),'U26':(17,30,2.5,2.1)})
for i in range(21,27):parts['L'+str(i)]['affinity']='U'+str(i)
def dist(a,b):
 return math.hypot(max(a[0]-b[0]-b[2],b[0]-a[0]-a[2],0),max(a[1]-b[1]-b[3],b[1]-a[1]-a[3],0))
best=None
for seed in range(30):
 free=[(0,0,35.4,35.4)];placed=dict(fixed)
 for r in fixed.values():free=subtract(free,r)
 rng=random.Random(seed);remain=[r for ref,r in parts.items() if ref not in fixed]
 # Keep supply ICs before their bank capacitors, local bypass before unrelated tiny parts.
 remain.sort(key=lambda r:(0 if r['reference'] in inputs else 1 if r['affinity'] else 2,-r['size'][0]*r['size'][1]*(1+rng.random()*.15)))
 failed=[]
 for p in remain:
  w,h=p['size'];choices=[];target=placed.get(p['affinity'])
  for f in free:
   for ww,hh in [(w,h),(h,w)]:
    if ww<=f[2]+1e-7 and hh<=f[3]+1e-7:
     # Test each corner, rather than forcing locality-sensitive parts to top-left.
     for x,y in [(f[0],f[1]),(f[0]+f[2]-ww,f[1]),(f[0],f[1]+f[3]-hh),(f[0]+f[2]-ww,f[1]+f[3]-hh)]:
      rect=(x,y,ww,hh);local=dist(rect,target) if target else 0
      choices.append(((local,min(f[2]-ww,f[3]-hh),max(f[2]-ww,f[3]-hh)),rect))
  if not choices:failed.append(p['reference']);continue
  rect=min(choices,key=lambda x:x[0])[1];placed[p['reference']]=rect;free=subtract(free,rect)
 affinity=[(ref,dist(r,placed[parts[ref]['affinity']])) for ref,r in placed.items() if parts[ref]['affinity'] in placed]
 violations=[(ref,d) for ref,d in affinity if d>3]
 score=(len(failed),len(violations),sum(d for ref,d in affinity))
 if best is None or score<best[0]:best=(score,seed,placed,failed,affinity)
score,seed,placed,failed,affinity=best
for a,r in placed.items():
 assert min(r[:2])>=-1e-7 and r[0]+r[2]<=35.4+1e-7 and r[1]+r[3]<=35.4+1e-7
 for bb,q in placed.items():
  if a<bb:assert not overlaps(r,q)
out={'status':'CONDITIONAL_RECTANGLE_LOCALITY_SCREEN_NOT_PLACEMENT_RELEASE','scenario':'fixed distributed buck trial; stronger X7R capacitor sensitivity; all original other parts retained; no bottom components','boundary_mm':38,'conditional_edge_band_mm':1.3,'interior_mm':35.4,'component_envelopes_requested':len(parts),'placed':len(placed),'unplaced':failed,'seed':seed,'area_mm2':sum(r['size'][0]*r['size'][1] for r in parts.values()),'affinity_threshold_mm':3,'threshold_basis':'engineering screening target measured between reservation rectangles, NOT manufacturer maximum and NOT electrical path length','affinity_over_target':[{'reference':r,'distance_mm':d} for r,d in affinity if d>3],'affinity_measurements':[{'reference':r,'target':parts[r]['affinity'],'distance_mm':d} for r,d in affinity],'no_claims':['required capacitance guaranteed','BGA escape','switching loop inductance','DDR routing or skew','local via/return-path availability','thermal feasibility','factory acceptance'],'placements':[dict(reference=ref,x_mm=r[0]+1.3,y_mm=r[1]+1.3,w_mm=r[2],h_mm=r[3],affinity=parts[ref]['affinity']) for ref,r in placed.items()]}
(D/'topside-locality-screen.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:v for k,v in out.items() if k not in ['placements','affinity_measurements']},indent=2))
