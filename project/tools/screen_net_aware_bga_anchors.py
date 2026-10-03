#!/usr/bin/env python3
"""Bounded three-package anchor search using actual nets; no routing/fit qualification."""
from pathlib import Path
import csv,json,math,xml.etree.ElementTree as E,hashlib
B=Path(__file__).resolve().parents[1];H=B/'cad/high-temp-candidate';O=B/'engineering/core-floorplan-study'
def rows(p):return list(csv.DictReader(open(p)))
points={}
for r in rows(B/'engineering/bga-engineering-candidates/memory-soc-functional-balls.csv'):points.setdefault(r['package'],{})[r['ball']]=(float(r['x_mm']),float(r['y_mm']))
ps=points['K230'];pr=points['FW200'];pe=points['BH153'];mr=rows(H/'master-pin-assignments.csv');pins={(r['reference'],r['pin']):r for r in mr}
edges={r['pin']:(float(r['module_x_mm'])+19,float(r['module_y_mm'])+19) for r in rows(B/'engineering/mechanical/castellation-proposal-contacts.csv')}
x=E.parse(H/'master.xml');direct=[]
for n in x.findall('.//nets/net'):
 u=[p.get('pin') for p in n.findall('node') if p.get('ref')=='U1'];j=[p.get('pin') for p in n.findall('node') if p.get('ref')=='J1']
 if len(u)==len(j)==1 and not pins['U1',u[0]]['function'].startswith(('VDD','AVDD','GND','VSS')):
  name=n.get('name');weight=2 if name.startswith(('CSI','DSI','USB')) else 1;direct.append((u[0],j[0],name,weight))
ddr=rows(B/'data/k230-source-extraction/01studio-soc-to-lpddr4-65nets.csv')
sfun={r['function']:r['pin'] for r in mr if r['reference']=='U1'};em=[]
for r in mr:
 if r['reference']!='U3':continue
 f=r['function'];sf='MMC0_D'+f[3:] if f.startswith('DAT') else {'CLK':'MMC0_CLK','CMD':'MMC0_CMD','RST_n':'MMC0_RST_N'}.get(f)
 if sf:em.append((sfun[sf],r['pin']))
assert len(ddr)==65 and len(em)==11
# Verified maximum body plus0.25mm per side; no escape or decap apron implied.
sizes={'U1':(13.6,13.6),'U2':(10.6,15.1),'U3':(12.1,13.6)}
def rot(p,r):
 a,b=p
 return [(a,b),(-b,a),(-a,-b),(b,-a)][r]
def abspt(p,c,r):a,b=rot(p,r);return a+c[0],b+c[1]
def box(ref,c,r):w,h=sizes[ref];w,h=(h,w) if r%2 else (w,h);return c[0]-w/2,c[1]-h/2,w,h
def inside(b):return b[0]>=1.3 and b[1]>=1.3 and b[0]+b[2]<=36.7 and b[1]+b[3]<=36.7
def overlap(a,b):return a[0]<b[0]+b[2] and a[0]+a[2]>b[0] and a[1]<b[1]+b[3] and a[1]+a[3]>b[1]
def length(a,b):return abs(a[0]-b[0])+abs(a[1]-b[1])
def adjacent(ref,sc,sr,side):
 out=[];vx,vy=rot(side,sr);sw,sh=sizes['U1']
 for r in range(4):
  w,h=sizes[ref];w,h=(h,w) if r%2 else (w,h)
  for gap in [.5,1.5,2.5]:
   distance=(sw/2+w/2+gap) if vx else (sh/2+h/2+gap)
   for off in [-4,-2,0,2,4]:
    c=(sc[0]+vx*distance-vy*off,sc[1]+vy*distance+vx*off);bb=box(ref,c,r)
    if inside(bb):out.append((c,r,bb,gap))
 return out
best=[];tested=0
for sx in range(9,30,2):
 for sy in range(9,30,2):
  sc=(sx,sy)
  for sr in range(4):
   sb=box('U1',sc,sr)
   if not inside(sb):continue
   sd={p:abspt(v,sc,sr) for p,v in ps.items()}
   ec=sum(weight*length(sd[p],edges[j]) for p,j,name,weight in direct)
   rr=[]
   for c,r,bb,gap in adjacent('U2',sc,sr,(1,0)):
    ds=[length(sd[v['soc_ball']],abspt(pr[v['dram_ball']],c,r)) for v in ddr];rr.append((sum(ds),max(ds),c,r,bb,gap))
   ee=[]
   for c,r,bb,gap in adjacent('U3',sc,sr,(0,-1)):
    ds=[length(sd[p],abspt(pe[q],c,r)) for p,q in em];ee.append((sum(ds),max(ds),c,r,bb,gap))
   for a in sorted(rr)[:12]:
    for e in sorted(ee)[:12]:
     if overlap(a[4],e[4]):continue
     tested+=1;score=2*a[0]+e[0]+ec
     best.append({'score':score,'DDR_sum_manhattan_mm':a[0],'DDR_max_manhattan_mm':a[1],'MMC_lower_bound_sum_mm':e[0],'edge_weighted_sum_mm':ec,'anchors':{'U1':{'center':sc,'rotation_clockwise_deg':sr*90},'U2':{'center':a[2],'rotation_clockwise_deg':a[3]*90},'U3':{'center':e[2],'rotation_clockwise_deg':e[3]*90}},'body_plus_clearance_rectangles':{'U1':sb,'U2':a[4],'U3':e[4]}})
   best=sorted(best,key=lambda a:a['score'])[:30]
assert best
out={'status':'THREE_PACKAGE_NET_AWARE_ANCHOR_SEARCH_NOT_COMPLETE_PLACEMENT','coordinate_convention':'module top view,origin top-left,+x right,+y down;rotations clockwise','candidate_combinations_tested':tested,'direct_edge_signals_used':len(direct),'DDR_joins':65,'eMMC_host_paths':11,'objective':'2x DDR Manhattan length + MMC endpoint lower bound + direct-edge Manhattan length (CSI/DSI/USB weight2); heuristic, not electrical delay','scope_limits':['Storage paths contain mux/translation not placed; direct endpoint score is only a lower bound.','No PDN/local decouplers/regulator loops or rest-of-BOM fit enforced.','No congestion, vias, obstacles, impedance, skew, timing or thermal verification.','Geometry uses conditional1.30mm edge reservation and maximum-package body plus0.25mm per side.','Search is bounded to plausible DDR-side/MMC-side adjacency; not a global optimum proof.'],'best_candidates':best,'input_hashes':{str(p.relative_to(B)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [H/'master.xml',B/'engineering/bga-engineering-candidates/memory-soc-functional-balls.csv']}}
(O/'net-aware-bga-anchors.json').write_text(json.dumps(out,indent=2));print(json.dumps({'tested':tested,'edge_nets':len(direct),'best':best[0]},indent=2))
