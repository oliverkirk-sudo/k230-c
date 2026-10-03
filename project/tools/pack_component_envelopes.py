#!/usr/bin/env python3
"""No electrical/layout claims: pack explicit 2D reservation rectangles for feasibility screening."""
from pathlib import Path
import json,math,random
B=Path(__file__).resolve().parents[1];D=B/'engineering/mechanical';rows=json.load(open(D/'full-bom-area-screen.json'))['components'];parts={r['reference']:r for r in rows if r['reservation_dense_mm2']>0}
def overlaps(a,b):return a[0]<b[0]+b[2]-1e-7 and a[0]+a[2]>b[0]+1e-7 and a[1]<b[1]+b[3]-1e-7 and a[1]+a[3]>b[1]+1e-7
def subtract(free,r):
 out=[]
 for f in free:
  if not overlaps(f,r):out.append(f);continue
  x,y,w,h=f;xx,yy,ww,hh=r
  if xx>x+1e-7:out.append((x,y,xx-x,h))
  if xx+ww<x+w-1e-7:out.append((xx+ww,y,x+w-xx-ww,h))
  if yy>y+1e-7:out.append((x,y,w,yy-y))
  if yy+hh<y+h-1e-7:out.append((x,yy+hh,w,y+h-yy-hh))
 keep=[]
 for i,a in enumerate(out):
  if any(i!=j and a[0]>=b[0]-1e-7 and a[1]>=b[1]-1e-7 and a[0]+a[2]<=b[0]+b[2]+1e-7 and a[1]+a[3]<=b[1]+b[3]+1e-7 and (a!=b or j<i) for j,b in enumerate(out)):continue
  keep.append(a)
 return keep
best=None
for seed in range(20):
 free=[(0,0,34,34)];placed={};fixed={'U1':(0,0,13.5,13.5),'U2':(13.75,0,10.5,15.5),'U3':(0,13.75,12,13.5)}
 for ref,r in fixed.items():placed[ref]=r;free=subtract(free,r)
 rng=random.Random(seed)
 remain=[r for ref,r in parts.items() if ref not in fixed]
 # Large areas first; controlled perturbations only among comparably sized parts.
 remain.sort(key=lambda r:r['reservation_dense_mm2']*(1+rng.random()*.25),reverse=True)
 failed=[]
 for p in remain:
  w,h=p['dense_reservation_xy_mm'];choices=[]
  for f in free:
   for ww,hh in [(w,h),(h,w)]:
    if ww<=f[2]+1e-7 and hh<=f[3]+1e-7:
     choices.append(((min(f[2]-ww,f[3]-hh),max(f[2]-ww,f[3]-hh),f[1],f[0]),(f[0],f[1],ww,hh)))
  if not choices:failed.append(p['reference']);continue
  rect=min(choices,key=lambda a:a[0])[1];placed[p['reference']]=rect;free=subtract(free,rect)
 score=(len(failed),sum(parts[r]['reservation_dense_mm2'] for r in failed))
 if best is None or score<best[0]:best=(score,seed,placed,failed)
 if not failed:break
score,seed,placed,failed=best
for a,r in placed.items():
 assert min(r[:2])>=-1e-7 and r[0]+r[2]<=34+1e-7 and r[1]+r[3]<=34+1e-7
 for b,q in placed.items():
  if a<b:assert not overlaps(r,q),(a,b)
result={'scope':'2D_ENVELOPE_PACKING_ONLY_NOT_PCB_PLACEMENT_OR_ROUTING','algorithm':'bounded20-seed MaxRects-style rectangle screen;3 BGA envelopes fixed','seed':seed,'placed_count':len(placed),'requested_count':len(parts),'unplaced':failed,'pairwise_overlap_count':0,'interior_mm':[34,34],'provisional_edge_band_mm':2,'rotation_allowed':True,'not_checked':['selected passive MPNs and land patterns','local decoupling affinity','switching loop geometry','BGA escape and vias','routing corridors','return paths','thermal coupling','edge castellation fabrication geometry','manufacturing process'],'placements':[{'reference':ref,'x_mm':r[0]+2,'y_mm':r[1]+2,'w_mm':r[2],'h_mm':r[3],'dnp':parts[ref]['dnp']} for ref,r in placed.items()]}
(D/'full-envelope-packing-study.json').write_text(json.dumps(result,indent=2))
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="1560" viewBox="0 0 1400 1560"><rect width="1400" height="1560" fill="white"/>','<text x="50" y="50" font-family="sans-serif" font-size="27">FULL BOM ENVELOPE STUDY - NOT A PCB LAYOUT</text>','<text x="50" y="92" font-family="sans-serif" font-size="19">Provisional rectangles only. No electrical pads, routing, thermal or local-PDN qualification.</text>','<rect x="70" y="150" width="1254" height="1254" fill="#eee" stroke="#111" stroke-width="3"/>','<rect x="136" y="216" width="1122" height="1122" fill="white" stroke="#777" stroke-dasharray="9 5"/>']
for r in result['placements']:
 ref=r['reference'];kind=''.join(filter(str.isalpha,ref));color={'U':'#bdd4ef','C':'#d9e8cd','R':'#f1e3ba','L':'#f7c4a7','FB':'#efcddb','Y':'#d6c8ed','TP':'#eee','JP':'#eee'}.get(kind,'#ddd')
 x=70+r['x_mm']*33;y=150+r['y_mm']*33;w=r['w_mm']*33;h=r['h_mm']*33
 svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}" stroke="#555" stroke-width="1"/>')
 svg.append(f'<text x="{x+w/2}" y="{y+h/2+3}" text-anchor="middle" font-family="sans-serif" font-size="{min(13,max(8,h*.35))}">{ref}</text>')
svg.append(f'<text x="70" y="1440" font-family="sans-serif" font-size="22">{len(placed)}/{len(parts)} envelopes placed; {len(failed)} unplaced; zero rectangle overlaps</text>')
svg.append('<text x="70" y="1480" font-family="sans-serif" font-size="18">38 x 38 mm outline;2 mm edge band assumed. A packed rectangle is not a routed or validated component.</text></svg>')
(D/'full-envelope-packing-study.svg').write_text('\n'.join(svg))
try:
 import cairosvg
 cairosvg.svg2png(bytestring='\n'.join(svg).encode(),write_to=str(D/'full-envelope-packing-study.png'))
except ImportError:pass
print(len(placed),'/',len(parts),'placed; unplaced:',failed)
