#!/usr/bin/env python3
"""Bounded DDR-first fanout with real equal-count transitions and explicit failures.

Preserves the generic control. All live high-speed DDR balls, including outer
balls, receive one physically routed L1-to-escape transition; unresolved signal
vias and their dogbones are removed from the emitted geometry, never counted.
DDR only uses L3/L8, whose proposed neighbors are GND. Reference copper is not
modeled, and this is neither an impedance nor a timing proof.
"""
import copy, csv, hashlib, heapq, json, math, sys, time
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
import geometry_core as g
OUT=Path(__file__).resolve().parent
GROUPS=['B_BYTE0','B_BYTE1','B_ADDRESS_COMMAND','A_ADDRESS_COMMAND','A_BYTE1','A_BYTE0']
PAIRS=['DDR_DQSA0','DDR_DQSA1','DDR_DQSB0','DDR_DQSB1','DDR_CLKA','DDR_CLKB']

def allocate(balls):
    vias=[];routes=[]
    for b in balls:
        p=[b['x'],b['y']]
        if b['category']=='unused':continue
        high=bool(b['ddr65'] and b['ddr65']['sink_group']!='RESET_ASYNCHRONOUS')
        if b['category']=='signal' and b['ring']==0 and not high:
            q=[math.copysign(g.LIMIT,b['x']),b['y']] if abs(b['x'])>abs(b['y']) else [b['x'],math.copysign(g.LIMIT,b['y'])]
            routes.append(dict(ball=b['ball'],net=b['net'],layer='L1',purpose='direct_signal_escape',points=[p,q]))
        else:
            q=[round(b['x']+.325,8),round(b['y']-.325,8)]
            vias.append(dict(ball=b['ball'],net=b['net'],category=b['category'],xy=q,pad=g.VIA,hole=g.HOLE,
                added_outer_ddr_transition=high and b['ring']==0,
                retained_annuli=['L1','L2','L3','L4','L5','L6','L7','L8'],
                functional_layers=['L1']+(['L2','L4','L7'] if b['category']=='ground' else ['L5'] if b['category']=='power' else [])))
            routes.append(dict(ball=b['ball'],net=b['net'],layer='L1',purpose='ball_to_via',points=[p,q]))
    assert len(vias)==327 and sum(v['category'] in ('power','ground') for v in vias)==158
    assert sum(v['added_outer_ddr_transition'] for v in vias)==16
    return vias,routes

class Router:
    def __init__(self,balls,vias):
        self.grid=g.Lattice();n=self.grid.n
        self.base=np.zeros((4,n,n),dtype=np.int16);self.masks={}
        rad=max(g.VIA/2+g.CLEAR+g.W/2,g.HOLE/2+g.HC+g.W/2)
        for v in vias:
            m=self.grid.circle(v['xy'],rad);self.base+=m;self.masks[v['ball']]=m
        self.vias={v['ball']:v for v in vias};self.balls={b['ball']:b for b in balls}
        self.dynamic=np.zeros((3,4,n,n),dtype=bool);self.loads=[0,0,0]
        self.routes=[];self.stats=[]
    def search(self,b,allowed):
        grid=self.grid;n=grid.n;source=self.vias[b['ball']]['xy'];x,y=grid.index(source)
        blocked=np.broadcast_to((self.base-self.masks[b['ball']])>0,self.dynamic.shape)|self.dynamic
        queue=[];prev={};dist={};expanded=0
        for layer in allowed:
            k=(layer,x,y);dist[k]=self.loads[layer]*.02
            heapq.heappush(queue,(dist[k]+min(x,y,n-1-x,n-1-y),dist[k],k))
        while queue:
            _,cost,k=heapq.heappop(queue)
            if cost!=dist[k]:continue
            layer,x,y=k;expanded+=1
            if x==0 or y==0 or x==n-1 or y==n-1:
                pts=[grid.xy(x,y)]
                while k in prev:
                    k=prev[k];pts.append(grid.xy(k[1],k[2]))
                return layer,g.simplify(pts[::-1]),expanded
            for direction,(dx,dy) in enumerate(grid.dirs):
                nx,ny=x+dx,y+dy
                if nx<0 or ny<0 or nx>=n or ny>=n or blocked[layer,direction,y,x]:continue
                nk=(layer,nx,ny);ng=cost+1
                if ng<dist.get(nk,float('inf')):
                    dist[nk]=ng;prev[nk]=k;h=min(nx,ny,n-1-nx,n-1-ny)
                    heapq.heappush(queue,(ng+h,ng,nk))
        return None,None,expanded
    def route_one(self,b,allowed,stage):
        layer,pts,expanded=self.search(b,allowed)
        self.stats.append(dict(ball=b['ball'],net=b['net'],stage=stage,allowed_layers=[g.LAYERS[l] for l in allowed],expanded_nodes=expanded,solved=pts is not None))
        if pts is None:return False
        r=dict(ball=b['ball'],net=b['net'],layer=g.LAYERS[layer],purpose='via_to_outside_body',points=pts)
        self.routes.append(r);self.loads[layer]+=1
        for a,z in zip(pts,pts[1:]):self.dynamic[layer]|=self.grid.segment(a,z,g.W+g.CLEAR)
        return True

def run(mode='groups',order='outer',assignment=0):
    balls=g.load();vias,routes=allocate(balls);router=Router(balls,vias)
    byname={b['net']:b for b in balls};byball={b['ball']:b for b in balls}
    layers={name:(0 if ((assignment>>i)&1)==0 else 2) for i,name in enumerate(GROUPS)}
    paired=set();unsolved={};pairchoices=[]
    # Every pair is routed before any unpaired DDR or general signal.
    for stem in PAIRS:
        bs=[byname[stem+'_P'],byname[stem+'_N']];group=bs[0]['ddr65']['sink_group']
        preferred=layers[group];allowed_options=[preferred] if mode=='groups' else [preferred,2 if preferred==0 else 0]
        old_dynamic=router.dynamic.copy();old_load=router.loads.copy();old_n=len(router.routes)
        success=False
        for l in allowed_options:
            for pair_order in [bs,bs[::-1]]:
                router.dynamic=old_dynamic.copy();router.loads=old_load.copy();router.routes=router.routes[:old_n]
                if all(router.route_one(b,[l],'differential_pair') for b in pair_order):
                    success=True;break
            if success:break
        pairchoices.append(dict(pair=stem,group=group,layer=g.LAYERS[l] if success else None,solved=success))
        if not success:
            router.dynamic=old_dynamic;router.loads=old_load;router.routes=router.routes[:old_n]
            for b in bs:unsolved[b['ball']]='Differential pair could not be routed atomically on its common allowed ground-reference layer(s).'
        paired.update(b['ball'] for b in bs)
    signal=[b for b in balls if b['category']=='signal' and b['ball'] in router.vias and b['ball'] not in paired]
    def key(b):
        d=b['ddr65'];rank=(0 if d and d['sink_group']!='RESET_ASYNCHRONOUS' else 1 if d else 2)
        return rank,(-b['ring'] if order=='deep' else b['ring']),b['ball']
    signal.sort(key=key)
    for i,b in enumerate(signal):
        d=b['ddr65'];high=d and d['sink_group']!='RESET_ASYNCHRONOUS'
        allowed=[layers[d['sink_group']]] if high and mode=='groups' else [0,2] if d else [0,1,2]
        if not router.route_one(b,allowed,'DDR_group' if high else 'DDR_reset' if d else 'general_signal'):
            unsolved[b['ball']]='No path on constrained layer(s) in fixed-via bounded search with previously committed DDR-priority routes; not an impossibility proof.'
        if i%30==0:print(mode,order,assignment,i+1,len(signal),'solved',len(router.routes),'unsolved',len(unsolved),flush=True)
    # Signal vias without a complete physical internal route are not retained.
    # Initial reserved positions remain conservative obstacles during this bounded trial.
    vias=[v for v in vias if v['ball'] not in unsolved]
    routes=[r for r in routes if r['ball'] not in unsolved]+router.routes
    vmap={v['ball']:v for v in vias}
    for r in router.routes:vmap[r['ball']]['functional_layers'].append(r['layer'])
    unresolved=[dict(ball=b,net=byball[b]['net'],category='signal',ring=byball[b]['ring'],via_xy=router.vias[b]['xy'],
        ddr_group=byball[b]['ddr65']['sink_group'] if byball[b]['ddr65'] else None,reason=reason,
        emitted_signal_vias=0,emitted_routes=0) for b,reason in unsolved.items()]
    summary=dict(physical_lands=390,signal_demand=209,signal_escapes=209-len(unsolved),unsolved_signals=len(unsolved),
        high_speed_ddr_demand=64,high_speed_ddr_solved=64-sum(bool(byball[b]['ddr65'] and byball[b]['ddr65']['sink_group']!='RESET_ASYNCHRONOUS') for b in unsolved),
        DDR65_solved=65-sum(bool(byball[b]['ddr65']) for b in unsolved),
        complete_differential_pairs=sum(p['solved'] for p in pairchoices),
        power_balls=53,ground_balls=105,open_balls=23,power_ground_vias=158,
        direct_signal_escapes=sum(r['purpose']=='direct_signal_escape' for r in routes),
        signal_vias=sum(v['category']=='signal' for v in vias),total_vias=len(vias),
        actual_added_outer_ddr_vias=sum(v['added_outer_ddr_transition'] for v in vias),
        escaped_by_layer=dict(Counter(r['layer'] for r in routes if r['purpose']!='ball_to_via')))
    data=dict(status='UNRELEASED_CONSTRAINED_LOCAL_FANOUT_NOT_DDR_TIMING_PASS',mode=mode,order=order,assignment=assignment,
        source_sha256={p:hashlib.sha256((g.ROOT/p).read_bytes()).hexdigest() for p in g.INPUTS},
        rules=dict(trace_width=g.W,copper_clearance=g.CLEAR,top_land=g.LAND,via_pad=g.VIA,assumed_hole=g.HOLE,hole_to_other_copper=g.HC,
            ball_pitch=.65,nominal_annular_ring=(g.VIA-g.HOLE)/2,selected_min_annular_ring=.0762),
        search=dict(step_mm=g.STEP,mode='DDR-first four-neighbor A*; one real L1-to-signal transition per solved high-speed DDR net; atomically commit same-layer pairs',
            bound_mm=g.LIMIT,body_half_width_mm=g.BODY,initial_signal_via_obstacles=169,removed_unrouted_via_obstacles=len(unsolved),
            high_speed_allowed_layers=['L3','L8'],group_common_layer_is_additional_engineering_target=mode=='groups',
            group_layer_assignment={k:g.LAYERS[v] for k,v in layers.items()},pair_choices=pairchoices,
            equal_vias_policy='Every solved high-speed DDR net has exactly one real via with both L1 and internal routing; no NC markers or dummy vias. Unsolved nets are not counted as matched.'),
        balls=balls,vias=vias,routes=routes,unsolved_signal_balls=unresolved,searchstats=router.stats,summary=summary)
    path=OUT/f'trial-{mode}-{order}-{assignment}.json';path.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(summary),flush=True)
    return data
if __name__=='__main__':run(*sys.argv[1:3],int(sys.argv[3]) if len(sys.argv)>3 else 0)
