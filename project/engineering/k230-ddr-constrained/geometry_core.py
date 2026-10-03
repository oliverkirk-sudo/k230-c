#!/usr/bin/env python3
"""Demand-complete local K230 escape experiment, not fabrication CAD.

All distances mm. The search lattice contains exact via-corridor midlines.
Search uses continuous segment/circle and segment/segment exclusion tests;
the separate audit rechecks the simplified output geometry independently.
"""
import csv, hashlib, heapq, json, math, os, sys, time
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
W, CLEAR, LAND, VIA, HOLE, HC = .1016, .1016, .27, .325, .15, .1524
STEP, LIMIT, BODY = .08125, 7.15, 6.55
LAYERS = ['L3','L6','L8']
EPS = 1e-10
INPUTS = ['engineering/mechanical/bga-K230-physical-centers.csv',
 'engineering/pin-types/k230-all390-type-audit.csv',
 'cad/high-temp-candidate/master-pin-assignments.csv',
 'cad/high-temp-candidate/master.xml',
 'engineering/bga-engineering-candidates/memory-soc-functional-escape-analysis.json',
 'engineering/bga-engineering-candidates/memory-soc-functional-balls.csv',
 'engineering/decoupling-allocation.csv',
 'engineering/routing/high-temp-ddr-route-contract.csv']

def read_csv(path):
    return list(csv.DictReader(open(ROOT/path)))

def load():
    import xml.etree.ElementTree as ET
    phys = read_csv(INPUTS[0]); types = {r['ball']:r for r in read_csv(INPUTS[1])}
    masters = {r['pin']:r for r in read_csv(INPUTS[2]) if r['reference']=='U1'}
    frozen = {r['ball']:r for r in read_csv(INPUTS[5]) if r['package']=='K230'}
    nets = {n.attrib['pin']:(net.attrib['name'],len(net.findall('node')))
            for net in ET.parse(ROOT/INPUTS[3]).getroot().findall('nets/net')
            for n in net.findall('node') if n.attrib['ref']=='U1'}
    ddr = {r['soc_ball']:r for r in read_csv(INPUTS[7])}
    balls=[]
    for r in phys:
        b=r['ball']; m=masters[b]; f=frozen[b]; actual=nets[b]
        assert not m['net'] or m['net']==actual[0], (b,m,actual)
        assert actual[0] == types[b]['current_net']
        assert f['x_mm']==str(float(r['x_mm'])) and f['y_mm']==str(float(r['y_mm']))
        balls.append(dict(ball=b, function=r['source_function_label'],
            net=m['net'] or None, xml_net=actual[0], xml_endpoint_count=actual[1],
            category=f['category'], disposition=m['status'],
            x=float(r['x_mm']),y=float(r['y_mm']),ring=int(f['ring']),
            ddr65=ddr.get(b), physical_top_land_diameter=LAND))
    assert len(balls)==390 and len(masters)==390 and len(nets)==390
    assert Counter(b['category'] for b in balls)==dict(signal=209,power=53,ground=105,unused=23)
    assert len(ddr)==65 and sum(b['ddr65'] is not None for b in balls)==65
    assert Counter(b['ring'] for b in balls if b['category']=='signal')=={0:56,1:59,2:42,3:34,4:16,5:2}
    for b in balls:
        if b['category']=='unused':
            assert b['net'] is None and b['xml_endpoint_count']==1, b
    return balls

def pointseg(p,a,b):
    px,py=p; ax,ay=a; bx,by=b; dx=bx-ax;dy=by-ay
    t=max(0,min(1,((px-ax)*dx+(py-ay)*dy)/(dx*dx+dy*dy))) if dx or dy else 0
    return math.hypot(px-ax-t*dx,py-ay-t*dy)

def segdist(a,b,c,d):
    def orient(p,q,r):return (q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0])
    o1,o2,o3,o4=orient(a,b,c),orient(a,b,d),orient(c,d,a),orient(c,d,b)
    if o1*o2<=EPS and o3*o4<=EPS:
        if max(min(a[0],b[0]),min(c[0],d[0]))<=min(max(a[0],b[0]),max(c[0],d[0]))+EPS and max(min(a[1],b[1]),min(c[1],d[1]))<=min(max(a[1],b[1]),max(c[1],d[1]))+EPS:return 0.
    return min(pointseg(a,c,d),pointseg(b,c,d),pointseg(c,a,b),pointseg(d,a,b))

def simplify(points):
    out=[]
    for p in points:
        if len(out)>=2:
            a,b=out[-2:]
            if abs((b[0]-a[0])*(p[1]-b[1])-(b[1]-a[1])*(p[0]-b[0]))<EPS:
                out[-1]=p;continue
        out.append(p)
    return out

class Lattice:
    def __init__(self):
        self.n=round(2*LIMIT/STEP)+1
        self.coords=np.arange(self.n)*STEP-LIMIT
        self.xx,self.yy=np.meshgrid(self.coords,self.coords)
        self.dirs=[(1,0),(-1,0),(0,1),(0,-1)]
        self.ex=np.stack([self.xx+dx*STEP for dx,dy in self.dirs])
        self.ey=np.stack([self.yy+dy*STEP for dx,dy in self.dirs])
        self.sx=np.broadcast_to(self.xx,self.ex.shape)
        self.sy=np.broadcast_to(self.yy,self.ey.shape)

    def circle(self,p,r):
        px,py=p
        t=np.clip(((px-self.sx)*(self.ex-self.sx)+(py-self.sy)*(self.ey-self.sy))/STEP**2,0,1)
        dist=np.hypot(self.sx+t*(self.ex-self.sx)-px,self.sy+t*(self.ey-self.sy)-py)
        return dist < r-EPS

    def segment(self,a,b,r):
        # Distance between each candidate edge and the closed output segment.
        ax,ay=a;bx,by=b;dx=bx-ax;dy=by-ay;l2=dx*dx+dy*dy
        d=[]
        for px,py in [(self.sx,self.sy),(self.ex,self.ey)]:
            t=np.clip(((px-ax)*dx+(py-ay)*dy)/l2,0,1)
            d.append(np.hypot(px-ax-t*dx,py-ay-t*dy))
        for px,py in [a,b]:
            t=np.clip(((px-self.sx)*(self.ex-self.sx)+(py-self.sy)*(self.ey-self.sy))/STEP**2,0,1)
            d.append(np.hypot(self.sx+t*(self.ex-self.sx)-px,self.sy+t*(self.ey-self.sy)-py))
        dist=np.minimum.reduce(d)
        o1=(self.ex-self.sx)*(ay-self.sy)-(self.ey-self.sy)*(ax-self.sx)
        o2=(self.ex-self.sx)*(by-self.sy)-(self.ey-self.sy)*(bx-self.sx)
        o3=dx*(self.sy-ay)-dy*(self.sx-ax)
        o4=dx*(self.ey-ay)-dy*(self.ex-ax)
        cross=(o1*o2<=EPS)&(o3*o4<=EPS)&(np.maximum(np.minimum(self.sx,self.ex),min(ax,bx))<=np.minimum(np.maximum(self.sx,self.ex),max(ax,bx))+EPS)&(np.maximum(np.minimum(self.sy,self.ey),min(ay,by))<=np.minimum(np.maximum(self.sy,self.ey),max(ay,by))+EPS)
        dist[cross]=0
        return dist < r-EPS

    def index(self,p):return tuple(round((c+LIMIT)/STEP) for c in p)
    def xy(self,x,y):return [round(self.coords[x],8),round(self.coords[y],8)]

    def search(self,source,blocked,loads):
        x,y=self.index(source);n=self.n
        queue=[]; prev={}; dist={}; expanded=0
        for layer in range(3):
            k=(layer,x,y);dist[k]=loads[layer]*.02
            heapq.heappush(queue,(dist[k]+min(x,y,n-1-x,n-1-y),dist[k],k))
        while queue:
            _,g,k=heapq.heappop(queue)
            if g!=dist[k]:continue
            layer,x,y=k;expanded+=1
            if x==0 or y==0 or x==n-1 or y==n-1:
                path=[self.xy(x,y)]
                while k in prev:
                    k=prev[k];path.append(self.xy(k[1],k[2]))
                return layer,simplify(path[::-1]),expanded
            for direction,(dx,dy) in enumerate(self.dirs):
                nx,ny=x+dx,y+dy
                if nx<0 or ny<0 or nx>=n or ny>=n or blocked[layer,direction,y,x]:continue
                nk=(layer,nx,ny);ng=g+1
                if ng<dist.get(nk,float('inf')):
                    dist[nk]=ng;prev[nk]=k
                    h=min(nx,ny,n-1-nx,n-1-ny)
                    heapq.heappush(queue,(ng+h,ng,nk))
        return None,None,expanded

def allocate(balls):
    vias=[];routes=[]
    for b in balls:
        p=[b['x'],b['y']]
        if b['category']=='unused':continue
        if b['category']=='signal' and b['ring']==0:
            if abs(b['x'])>abs(b['y']):q=[math.copysign(LIMIT,b['x']),b['y']]
            else:q=[b['x'],math.copysign(LIMIT,b['y'])]
            routes.append(dict(ball=b['ball'],net=b['net'],layer='L1',purpose='direct_signal_escape',points=[p,q]))
        else:
            # One unique adjacent interstice per demanding ball; no dummy vias.
            q=[round(b['x']+.325,8),round(b['y']-.325,8)]
            vias.append(dict(ball=b['ball'],net=b['net'],category=b['category'],xy=q,pad=VIA,hole=HOLE,
                retained_annuli=['L1','L2','L3','L4','L5','L6','L7','L8'],
                functional_layers=['L1']+(['L2','L4','L7'] if b['category']=='ground' else ['L5'] if b['category']=='power' else [])))
            routes.append(dict(ball=b['ball'],net=b['net'],layer='L1',purpose='ball_to_via',points=[p,q]))
    assert len(vias)==311 and sum(v['category'] in ('power','ground') for v in vias)==158
    assert len(set(tuple(v['xy']) for v in vias))==311
    return vias,routes

def route(balls,vias,routes,order):
    grid=Lattice();base=np.zeros((4,grid.n,grid.n),dtype=np.int16)
    rad=max(VIA/2+CLEAR+W/2,HOLE/2+HC+W/2)
    masks={}
    for v in vias:
        m=grid.circle(v['xy'],rad);base+=m;masks[v['ball']]=m
    dynamic=np.zeros((3,4,grid.n,grid.n),dtype=bool)
    byball={v['ball']:v for v in vias};loads=[0,0,0];unsolved=[];stats=[]
    signal=[b for b in balls if b['category']=='signal' and b['ring']>0]
    if order=='deep_first':signal.sort(key=lambda b:(-b['ring'],b['ball']))
    elif order=='outer_first':signal.sort(key=lambda b:(b['ring'],b['ball']))
    elif order.startswith('shuffle'):
        import random;random.Random(int(order.split('_')[1])).shuffle(signal)
    for i,b in enumerate(signal):
        v=byball[b['ball']]
        blocked=np.broadcast_to((base-masks[b['ball']])>0,dynamic.shape)|dynamic
        layer,points,expanded=grid.search(v['xy'],blocked,loads)
        stats.append(dict(ball=b['ball'],expanded_nodes=expanded,solved=points is not None))
        if points is None:
            unsolved.append(dict(ball=b['ball'],net=b['net'],ring=b['ring'],via_xy=v['xy'],reason='No path on any of L3/L6/L8 in this fixed via placement and prior route order; not a global impossibility proof.'))
        else:
            r=dict(ball=b['ball'],net=b['net'],layer=LAYERS[layer],purpose='via_to_outside_body',points=points)
            routes.append(r);v['functional_layers'].append(LAYERS[layer]);loads[layer]+=1
            for a,z in zip(points,points[1:]):dynamic[layer]|=grid.segment(a,z,W+CLEAR)
        if i%20==0 or points is None:print(f'{order} {i+1}/153 solved={sum(loads)} unsolved={len(unsolved)} load={loads}',flush=True)
    return unsolved,stats

def main():
    order=sys.argv[1] if len(sys.argv)>1 else 'deep_first'
    balls=load();vias,routes=allocate(balls)
    unsolved,searchstats=route(balls,vias,routes,order)
    source_hash={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in INPUTS}
    data=dict(status='UNRELEASED_LOCAL_GEOMETRY_TRIAL',order=order,source_sha256=source_hash,
        rules=dict(trace_width=W,copper_clearance=CLEAR,top_land=LAND,via_pad=VIA,assumed_hole=HOLE,hole_to_other_copper=HC,
            ball_pitch=.65,nominal_annular_ring=(VIA-HOLE)/2,selected_min_annular_ring=.0762),
        search=dict(step_mm=STEP,mode='four-neighbor A* with continuous exclusion edges; one signal layer after through via',bound_mm=LIMIT,body_half_width_mm=BODY),
        balls=balls,vias=vias,routes=routes,unsolved_signal_balls=unsolved,searchstats=searchstats,
        summary=dict(physical_lands=390,connected_signal_endpoints=209,power_balls=53,ground_balls=105,open_balls=23,
            direct_signal_escapes=56,signal_vias=153,power_ground_vias=158,total_vias=311,
            signal_escapes=209-len(unsolved),unsolved_signals=len(unsolved),
            escaped_by_layer=dict(Counter(r['layer'] for r in routes if r['purpose']!='ball_to_via'))))
    (OUT/f'trial-{order}.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(data['summary']),flush=True)

if __name__=='__main__':main()
