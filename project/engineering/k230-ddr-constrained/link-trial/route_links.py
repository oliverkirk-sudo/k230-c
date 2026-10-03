#!/usr/bin/env python3
"""Fixed-placement, fixed-K230-fanout bounded DDR link trial; no SI/timing claim.
All emitted coordinates use module top-left, +X right and +Y down, mm.
"""
import csv,json,math,hashlib,heapq,sys,time,copy
from pathlib import Path
from collections import Counter,defaultdict
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PARENT=HERE.parent
sys.dont_write_bytecode=True
sys.path.insert(0,str(PARENT))
import geometry_core as g
W,CLEAR,VIA,HOLE,HC=.1016,.1016,.325,.15,.1524
LAYERS=['L3','L8']; ALL=['L1','L2','L3','L4','L5','L6','L7','L8']
RAM_LAND=.300
SOURCES=[PARENT/'trial-groups-outer-21.json', ROOT/'engineering/mechanical/micron-lp4-independent-grid-verification.json', ROOT/'engineering/bga-engineering-candidates/memory-soc-functional-escape-analysis.json',ROOT/'cad/high-temp-candidate/master-pin-assignments.csv',ROOT/'cad/high-temp-candidate/master.xml',ROOT/'engineering/routing/high-temp-ddr-route-contract.csv',ROOT/'engineering/mechanical/core-stackup-process-proposal.json']
def rnd(p):return [round(float(z),8) for z in p]
def u1(p):return rnd([25-p[0],11-p[1]])
def u2(p):return rnd([11.4+p[0],11+p[1]])
def load():
    import xml.etree.ElementTree as ET
    src=json.loads(SOURCES[0].read_text());grid=json.loads(SOURCES[1].read_text())['grid']
    sensitivity=json.loads(SOURCES[2].read_text())['packages']['FW200']['trials']
    assert any(x['land_mm']==RAM_LAND for x in sensitivity)
    masters={r['pin']:r for r in csv.DictReader(SOURCES[3].open()) if r['reference']=='U2'}
    xml={n.get('pin'):(net.get('name'),len(net.findall('node'))) for net in ET.parse(SOURCES[4]).getroot().findall('nets/net') for n in net.findall('node') if n.get('ref')=='U2'}
    contract=list(csv.DictReader(SOURCES[5].open()));ddr={r['dram_ball']:r for r in contract}
    balls=[];vias=[];routes=[]
    for b in src['balls']:
        n=copy.deepcopy(b);n.update(ref='U1',id='U1:'+b['ball'],local_xy=[b['x'],b['y']]);n['x'],n['y']=u1([b['x'],b['y']]);balls.append(n)
    for v in src['vias']:
        n=copy.deepcopy(v);n.update(ref='U1',id='U1:'+v['ball'],xy=u1(v['xy']));vias.append(n)
    for r in src['routes']:
        n=copy.deepcopy(r);n.update(ref='U1',id='U1:'+r['ball'],points=[u1(p) for p in r['points']]);routes.append(n)
    for p in grid:
        if not p['physical']:continue
        b=p['ball'];m=masters[b];net=m['net'] or None;f=p['function'];xy=u2([p['x_mm'],p['y_mm']])
        assert f==m['function'],(b,f,m)
        assert net is None or net==xml[b][0]
        cat='unused' if f in ('NC','DNU') else 'ground' if f=='VSS' else 'power' if f.startswith('VDD') else 'signal' if b in ddr else 'local_bias'
        assert cat!='unused' or xml[b][1]==1
        balls.append(dict(ref='U2',id='U2:'+b,ball=b,function=f,net=net,xml_net=xml[b][0],xml_endpoint_count=xml[b][1],category=cat,local_xy=[p['x_mm'],p['y_mm']],x=xy[0],y=xy[1],physical_top_land_diameter=RAM_LAND,ddr65=ddr.get(b)))
        # Local bias balls are retained but no invented remote bias/resistor geometry.
        if cat in ('unused','local_bias'):continue
        q=u2([p['x_mm']+.4,p['y_mm']-.325])
        v=dict(ref='U2',id='U2:'+b,ball=b,net=net,category=cat,xy=q,pad=VIA,hole=HOLE,retained_annuli=ALL,functional_layers=['L1']+(['L2','L4','L7'] if cat=='ground' else ['L5'] if cat=='power' else []))
        vias.append(v);routes.append(dict(ref='U2',id='U2:'+b,ball=b,net=net,layer='L1',purpose='ball_to_via',points=[xy,q]))
    assert Counter(b['category'] for b in balls if b['ref']=='U2')==dict(unused=22,ground=58,power=52,signal=65,local_bias=3)
    assert len(balls)==590 and len(vias)==502
    assert all(next(b for b in balls if b['id']=='U1:'+r['soc_ball'])['net']==r['net']==masters[r['dram_ball']]['net'] for r in contract)
    return src,balls,vias,routes,contract
class Grid:
    def __init__(self,vias):
        # Fixed search window on the 38x38 module; no other component keepouts modeled.
        self.bounds=[5.5,33.0,1.5,21.5]
        x0,x1,y0,y1=self.bounds
        self.x=np.array(sorted(set([x0,x1]+[round(17.85+n*.08125,8) for n in range(-200,201) if x0<17.85+n*.08125<x1]+[round(7.4+n*.4,8) for n in range(24) if x0<7.4+n*.4<x1])))
        self.y=np.array(sorted(set([y0,y1]+[round(3.85+n*.08125,8) for n in range(-60,230) if y0<3.85+n*.08125<y1])))
        self.nx=len(self.x);self.ny=len(self.y)
        xx,yy=np.meshgrid(self.x,self.y)
        self.sx=np.broadcast_to(xx,(4,self.ny,self.nx));self.sy=np.broadcast_to(yy,(4,self.ny,self.nx))
        self.ex=np.stack([np.pad(xx[:,1:],((0,0),(0,1)),mode='edge'),np.pad(xx[:,:-1],((0,0),(1,0)),mode='edge'),xx,xx])
        self.ey=np.stack([yy,yy,np.pad(yy[1:,:],((0,1),(0,0)),mode='edge'),np.pad(yy[:-1,:],((1,0),(0,0)),mode='edge')])
        self.valid=np.ones(self.sx.shape,dtype=bool);self.valid[0,:,-1]=False;self.valid[1,:,0]=False;self.valid[2,-1,:]=False;self.valid[3,0,:]=False
        self.dirs=[(1,0),(-1,0),(0,1),(0,-1)]
    def area(self,a,b,rad):
        xmin,xmax=min(a[0],b[0])-rad,max(a[0],b[0])+rad;ymin,ymax=min(a[1],b[1])-rad,max(a[1],b[1])+rad
        # Include candidate edges adjacent to bbox, then analytically test each.
        ix0=max(0,np.searchsorted(self.x,xmin)-1);ix1=min(self.nx,np.searchsorted(self.x,xmax)+1)
        iy0=max(0,np.searchsorted(self.y,ymin)-1);iy1=min(self.ny,np.searchsorted(self.y,ymax)+1)
        return (slice(None),slice(iy0,iy1),slice(ix0,ix1))
    def mask(self,a,b,rad):
        ix=self.area(a,b,rad);sx,sy,ex,ey=(v[ix] for v in (self.sx,self.sy,self.ex,self.ey));dx=ex-sx;dy=ey-sy;den=dx*dx+dy*dy;den=np.maximum(den,1e-30)
        ds=[]
        for px,py in [a,b]:
            t=np.clip(((px-sx)*dx+(py-sy)*dy)/den,0,1);ds.append(np.hypot(sx+t*dx-px,sy+t*dy-py))
        ax,ay=a;bx,by=b;ux=bx-ax;uy=by-ay;d=ux*ux+uy*uy
        if d>1e-20:
            for px,py in [(sx,sy),(ex,ey)]:
                t=np.clip(((px-ax)*ux+(py-ay)*uy)/d,0,1);ds.append(np.hypot(px-ax-t*ux,py-ay-t*uy))
            o1=dx*(ay-sy)-dy*(ax-sx);o2=dx*(by-sy)-dy*(bx-sx);o3=ux*(sy-ay)-uy*(sx-ax);o4=ux*(ey-ay)-uy*(ex-ax)
            cross=(o1*o2<=1e-18)&(o3*o4<=1e-18)&(np.maximum(np.minimum(sx,ex),min(ax,bx))<=np.minimum(np.maximum(sx,ex),max(ax,bx))+1e-12)&(np.maximum(np.minimum(sy,ey),min(ay,by))<=np.minimum(np.maximum(sy,ey),max(ay,by))+1e-12)
        else:cross=False
        dist=np.minimum.reduce(ds);mask=(dist<rad-1e-10)|cross
        return ix,mask
    def apply(self,target,shape,value=1):
        ix,m=shape;target[ix]+=m.astype(target.dtype)*value
    def index(self,p):
        ix=np.argmin(abs(self.x-p[0]));iy=np.argmin(abs(self.y-p[1]));assert abs(self.x[ix]-p[0])<1e-7 and abs(self.y[iy]-p[1])<1e-7,p
        return int(ix),int(iy)
    def search(self,start,goal,block,maxnodes=240000):
        sx,sy=self.index(start);tx,ty=self.index(goal);S=(sx,sy);T=(tx,ty)
        def h(x,y):return abs(self.x[x]-self.x[tx])+abs(self.y[y]-self.y[ty])
        q=[(h(sx,sy),0.,S)];dist={S:0};prev={};count=0
        while q:
            f,cost,k=heapq.heappop(q)
            if abs(cost-dist[k])>1e-12:continue
            x,y=k;count+=1
            if k==T:
                out=[rnd([self.x[x],self.y[y]])]
                while k in prev:
                    k=prev[k];out.append(rnd([self.x[k[0]],self.y[k[1]]]))
                return g.simplify(out[::-1]),count,'solved'
            if count>=maxnodes:return None,count,'bounded_node_limit'
            for d,(dx,dy) in enumerate(self.dirs):
                if not self.valid[d,y,x] or block[d,y,x]:continue
                xx,yy=x+dx,y+dy;nk=(xx,yy);nc=cost+abs(self.x[xx]-self.x[x])+abs(self.y[yy]-self.y[y])
                if nc<dist.get(nk,float('inf'))-1e-12:
                    dist[nk]=nc;prev[nk]=k;heapq.heappush(q,(nc+h(xx,yy),nc,nk))
        return None,count,'no_path_in_fixed_geometry'
class Router:
    def __init__(self,vias,routes):
        self.grid=Grid(vias);g=self.grid;self.base=np.zeros((2,4,g.ny,g.nx),dtype=np.int16);self.own=defaultdict(list);self.dynamic=np.zeros(self.base.shape,dtype=np.int16);self.links=[];self.stats=[]
        rad=max(VIA/2+CLEAR+W/2,HOLE/2+HC+W/2)
        for v in vias:
            shape=g.mask(v['xy'],v['xy'],rad)
            for l in range(2):g.apply(self.base[l],shape)
            self.own[v['net']].append((None,shape))
        for r in routes:
            if r['layer'] not in LAYERS:continue
            l=LAYERS.index(r['layer'])
            for a,b in zip(r['points'],r['points'][1:]):
                shape=g.mask(a,b,W+CLEAR);g.apply(self.base[l],shape);self.own[r['net']].append((l,shape))
    def one(self,c,source,target,layer):
        l=LAYERS.index(layer);block=self.base[l].copy()
        for ol,shape in self.own[c['net']]:
            if ol in (None,l):self.grid.apply(block,shape,-1)
        block=(block>0)|(self.dynamic[l]>0)
        points,nodes,status=self.grid.search(source,target,block)
        self.stats.append(dict(net=c['net'],layer=layer,source=source,target=target,expanded_nodes=nodes,result=status))
        if points is None:return False
        r=dict(ref='U1_TO_U2',id=c['net'],ball=c['soc_ball']+'->'+c['dram_ball'],net=c['net'],layer=layer,purpose='actual_DDR_link',soc_ball=c['soc_ball'],dram_ball=c['dram_ball'],points=points)
        self.links.append(r)
        for a,b in zip(points,points[1:]):self.grid.apply(self.dynamic[l],self.grid.mask(a,b,W+CLEAR))
        return True

def main():
    source_hash={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in SOURCES}
    src,balls,vias,routes,contract=load();router=Router(vias,routes)
    ends={r['net']:(r['points'][-1],r['layer']) for r in routes if r['ref']=='U1' and r['purpose']=='via_to_outside_body'}
    rv={v['net']:v for v in vias if v['ref']=='U2' and v['category']=='signal'}
    contracts={r['net']:r for r in contract};paired=set();pairs=[];fail={}
    stems=['DDR_DQSA0','DDR_DQSA1','DDR_DQSB0','DDR_DQSB1','DDR_CLKA','DDR_CLKB']
    for stem in stems:
        nets=[stem+'_P',stem+'_N'];layer=ends[nets[0]][1];assert ends[nets[1]][1]==layer
        oldn=len(router.links);dyn=router.dynamic.copy();success=False
        for ordering in [nets,nets[::-1]]:
            router.links=router.links[:oldn];router.dynamic=dyn.copy()
            if all(router.one(contracts[n],ends[n][0],rv[n]['xy'],layer) for n in ordering):success=True;break
        if not success:
            router.links=router.links[:oldn];router.dynamic=dyn
            for n in nets:fail[n]='Atomic differential pair failed in both leg orders on its fixed common layer; no partial leg committed.'
        pairs.append(dict(pair=stem,layer=layer,complete=success));paired.update(nets)
        print(stem,success,'links',len(router.links),flush=True)
    # Fixed proximity priority: nearer RAM target first within a group, keep identities.
    remaining=[c for c in contract if c['net'] not in paired]
    remaining.sort(key=lambda c:(c['sink_group']=='RESET_ASYNCHRONOUS',math.dist(ends[c['net']][0],rv[c['net']]['xy']),c['net']))
    for i,c in enumerate(remaining):
        n=c['net'];ok=router.one(c,ends[n][0],rv[n]['xy'],ends[n][1])
        if not ok:fail[n]='No route in fixed fanout, real through-via obstacles, chosen route order and bounded L3/L8 window; not a global impossibility proof.'
        if i%8==0:print('single',i+1,len(remaining),'links',len(router.links),'unsolved',len(fail),flush=True)
    routes+=router.links
    completed={r['net'] for r in router.links}
    for v in vias:
        if v['ref']=='U2' and v['net'] in completed:v['functional_layers'].append(ends[v['net']][1])
    pernet=[]
    for c in contract:
        n=c['net'];rr=[r for r in routes if r['net']==n];complete=n in completed
        lengths=defaultdict(float)
        for r in rr:
            lengths[r['layer']]+=sum(math.dist(a,b) for a,b in zip(r['points'],r['points'][1:]))
        pernet.append(dict(c,complete_ball_to_ball=complete,layer=ends[n][1],routed_transition_count=2 if complete else None,local_ball_connected_vias=2,soc_exit=ends[n][0],ram_via=rv[n]['xy'],planar_length_by_layer_mm=dict(lengths),complete_planar_length_mm=sum(lengths.values()) if complete else None,route_segments=sum(len(r['points'])-1 for r in rr),unsolved_reason=fail.get(n),board_delay_ps='UNQUALIFIED',dram_package_delay_ps='UNAVAILABLE'))
    data=dict(status='BOUNDED_ACTUAL_DDR_LINK_TRIAL_NOT_RELEASED',source_sha256=source_hash,
        rules=dict(trace_width=W,copper_clearance=CLEAR,via_pad=VIA,assumed_hole=HOLE,hole_to_other_copper=HC,k230_top_land=.27,ram_top_land=RAM_LAND,ram_land_basis='Existing FW200 0.300 mm engineering sensitivity; not a Micron PCB recommendation',retained_annuli=ALL),
        placement=dict(coordinate_system='38x38 mm module top-left origin, +X right, +Y down; trial only',U1=dict(center=[25,11],rotation_deg=180,max_body=[13.1,13.1]),U2=dict(center=[11.4,11],rotation_deg=0,max_body=[10.1,14.6]),body_edge_gap_mm=2.0),
        search=dict(bounds_xy_mm=router.grid.bounds,grid_shape=[router.grid.nx,router.grid.ny],max_expanded_nodes_per_search=240000,mode='Rectilinear A* with analytic segment exclusions, fixed existing K230 fanout and fixed RAM dogbones; L3/L8 only; no interconnect vias added',group_layer_assignment=src['search']['group_layer_assignment'],differential_pairs=pairs,guideline_spacing_enforced_during_search=False,extra_components_keepouts_and_return_copper_modeled=False),
        balls=balls,vias=vias,routes=routes,pernet=pernet,unsolved=[p for p in pernet if not p['complete_ball_to_ball']],searchstats=router.stats,
        summary=dict(physical_lands=len(balls),k230_lands=390,ram_lands=200,ram_absent_grid_sites=64,k230_signal_exits=209,ram_power_vias=52,ram_ground_vias=58,ram_signal_dogbone_vias=65,ram_local_bias_balls_unrouted=3,total_vias=len(vias),required_DDR_links=65,completed_DDR_links=len(completed),unsolved_DDR_links=len(fail),complete_differential_pairs=sum(p['complete'] for p in pairs),all_completed_DDR_links_actual_vias=2,all_completed_DDR_links_actual_layer_changes=2,completed_by_layer=dict(Counter(ends[n][1] for n in completed))),
        limitations=['No impedance, coupling, reference-plane copper, return-path, timing, training, SI/PI, assembly, thermal or factory qualification.','No length tuning performed. SoC package lengths retained by exact ball join; Micron package delays unavailable.','All 110 RAM power/GND vias have actual L1 dogbones and plane ports, not a PDN completion claim.','Three local bias balls and their intended nets retained; resistor connections not routed or placed.','Unsolved RAM signal dogbones are retained as explicitly incomplete real ball-connected stubs; they are not counted as complete paths or as matched differential pairs.','Local 0.1016 mm copper rule enforced by search; Figure 054 2H/3H and separate 3W text evaluated by audit, not inferred as passing.','Other components and castellations not modeled; fixed 2.0 mm body gap is trial placement only.'])
    (HERE/'actual-links.json').write_text(json.dumps(data,indent=2)+'\n')
    for name,rows in [('pernet',pernet),('unsolved',data['unsolved']),('perball',balls),('vias',vias)]:
        fields=list(dict.fromkeys(k for r in rows for k in r))
        with (HERE/(name+'.csv')).open('w') as f:
            w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows([{k:json.dumps(v) if isinstance(v,(list,dict)) else v for k,v in r.items()} for r in rows])
    print(json.dumps(data['summary']),flush=True)
if __name__=='__main__':main()
