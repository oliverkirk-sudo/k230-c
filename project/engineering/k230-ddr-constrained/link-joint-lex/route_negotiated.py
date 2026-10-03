#!/usr/bin/env python3
"""Negotiated-congestion candidate; static geometry unchanged; never a timing pass."""
import sys,json,copy,time,heapq,math,random,hashlib
from pathlib import Path
from collections import defaultdict,Counter
import numpy as np
HERE=Path(__file__).resolve().parent;OLD=HERE.parent/'link-trial';sys.dont_write_bytecode=True;sys.path.insert(0,str(OLD));import route_links as m
start=time.monotonic();src,balls,vias,routes,contract=m.load()
ddr_names={c['net'] for c in contract}
oldends={p['net']:(p['points'][-1],p['layer']) for p in routes if p['ref']=='U1' and p['purpose']=='via_to_outside_body'}
sv={v['net']:v['xy'] for v in vias if v['ref']=='U1' and v['net'] in ddr_names}
ends={n:(sv[n],oldends[n][1]) for n in ddr_names}
routes=[p for p in routes if not(p['ref']=='U1' and p['purpose']=='via_to_outside_body' and p['net'] in ddr_names)]
r=m.Router(vias,routes);grid=r.grid
rv={v['net']:v for v in vias if v['ref']=='U2' and v['category']=='signal'};contracts={c['net']:c for c in contract};names=list(contracts)
static={}
for n in names:
 l=m.LAYERS.index(ends[n][1]);b=r.base[l].copy()
 for ol,shape in r.own[n]:
  if ol in (None,l):grid.apply(b,shape,-1)
 static[n]=b>0
occupancy=np.zeros(r.base.shape,dtype=np.int16);history=np.zeros(r.base.shape,dtype=np.float32);masks={};paths={};edgepaths={};stats=[]
def pathmask(points):
 result=np.zeros(r.base.shape[1:],dtype=bool)
 for a,b in zip(points,points[1:]):
  ix,mask=grid.mask(a,b,m.W+m.CLEAR);result[ix]|=mask
 return result

def solve(n,present):
 l=m.LAYERS.index(ends[n][1]);block=static[n];sx,sy=grid.index(ends[n][0]);tx,ty=grid.index(rv[n]['xy']);S=(sx,sy);T=(tx,ty)
 def heuristic(x,y):return abs(grid.x[x]-grid.x[tx])+abs(grid.y[y]-grid.y[ty])
 queue=[(0.,heuristic(sx,sy),0.,S)];dist={S:(0.,0.)};prev={};count=0
 while queue:
  bad,f,cost,k=heapq.heappop(queue)
  if (bad,cost)!=dist[k]:continue
  x,y=k;count+=1
  if k==T:
   nodes=[k];edges=[]
   while k in prev:
    before,d=prev[k];edges.append((d,before[1],before[0]));k=before;nodes.append(k)
   pts=[m.rnd([grid.x[x],grid.y[y]]) for x,y in nodes[::-1]]
   return m.g.simplify(pts),edges[::-1],count
  for d,(dx,dy) in enumerate(grid.dirs):
   if not grid.valid[d,y,x] or block[d,y,x]:continue
   xx,yy=x+dx,y+dy;nk=(xx,yy);length=abs(grid.x[xx]-grid.x[x])+abs(grid.y[yy]-grid.y[y])
   # Lexicographic priority: any zero-conflict path beats every colliding path.
   hist=float(history[l,d,y,x]);nb=bad+length*float(occupancy[l,d,y,x])*(1+hist);nc=cost+length*(1+.05*hist)
   nd=(nb,nc)
   if nd<dist.get(nk,(float('inf'),float('inf'))):
    dist[nk]=nd;prev[nk]=(k,d);heapq.heappush(queue,(nb,nc+heuristic(xx,yy),nc,nk))
 return None,[],count

def conflicts():
 out={};total=0
 for n,edges in edgepaths.items():
  l=m.LAYERS.index(ends[n][1]);hits=[]
  for d,y,x in edges:
   # The route's own clearance mask contributes exactly one.
   other=int(occupancy[l,d,y,x])-1
   if other>0:hits.append((d,y,x,other));total+=other
  if hits:out[n]=hits
 return out,total

def snapshot(iteration,score,conf):
 old=json.loads((OLD/'actual-links.json').read_text());old['routes']=copy.deepcopy(routes)
 for n,p in paths.items():
  c=contracts[n];old['routes'].append(dict(ref='U1_TO_U2',id=n,ball=c['soc_ball']+'->'+c['dram_ball'],net=n,layer=ends[n][1],purpose='actual_DDR_link',soc_ball=c['soc_ball'],dram_ball=c['dram_ball'],points=p))
 for v in old['vias']:
  if v['ref']=='U2' and v['category']=='signal':v['functional_layers']=list(dict.fromkeys(['L1',ends[v['net']][1]]))
 for c in old['pernet']:
  n=c['net'];rr=[q for q in old['routes'] if q['net']==n];lengths=defaultdict(float)
  for q in rr:lengths[q['layer']]+=sum(math.dist(a,b) for a,b in zip(q['points'],q['points'][1:]))
  c.update(source_via=ends[n][0],soc_exit=None,candidate_path_exists=True,complete_ball_to_ball=(score==0),routed_transition_count=2,planar_length_by_layer_mm=dict(lengths),complete_planar_length_mm=sum(lengths.values()),route_segments=sum(len(q['points'])-1 for q in rr),unsolved_reason=None)
 old['unsolved']=[] if score==0 else copy.deepcopy(old['pernet']);old['summary'].update(candidate_DDR_paths=65,completed_DDR_links=65 if score==0 else 0,unsolved_DDR_links=0 if score==0 else 65,complete_differential_pairs=6 if score==0 else 0,completed_by_layer=dict(Counter(ends[n][1] for n in paths)))
 old['source_sha256']={str(p.relative_to(m.ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in m.SOURCES}
 old['status']='JOINT_NEGOTIATED_SEARCH_CANDIDATE_NOT_ACCEPTED_OR_TIMING_QUALIFIED'
 old['summary']['k230_non_ddr_signal_exits']=144
 old['summary']['k230_signal_exits']=144
 old['summary']['DDR_existing_via_sources']=65
 old['search']['mode']='Joint DDR lexicographic conflict-before-length routing; static geometry unchanged; layer assignments unchanged'
 old['search']['iteration']=iteration;old['search']['conflicting_grid_edge_events']=score;old['search']['conflicting_nets']=sorted(conf)
 old['search']['guideline_spacing_enforced_during_search']=False;old['searchstats']=stats
 old['limitations'].append('Candidate paths are not accepted connections until independent analytic/native collision and connectivity audits pass. No coupled pair routing or delay tuning performed.')
 (HERE/'best-search-candidate.json').write_text(json.dumps(old,indent=2))
 if score==0:(HERE/'actual-links.json').write_text(json.dumps(old,indent=2))

resume=json.loads((HERE.parent/'link-joint-strong/best-search-candidate.json').read_text())
for q in resume['routes']:
 if q['purpose']!='actual_DDR_link':continue
 n=q['net'];paths[n]=q['points'];masks[n]=pathmask(paths[n]);l=m.LAYERS.index(ends[n][1]);occupancy[l]+=masks[n]
 # Reconstruct directed grid edges from simplified rectilinear segments.
 edges=[]
 for a,b in zip(paths[n],paths[n][1:]):
  x,y=grid.index(a);tx,ty=grid.index(b)
  d=0 if tx>x else 1 if tx<x else 2 if ty>y else 3
  dx,dy=grid.dirs[d]
  while (x,y)!=(tx,ty):edges.append((d,y,x));x+=dx;y+=dy
 edgepaths[n]=edges
assert set(paths)==set(names)
initial_conf,initial_score=conflicts()
print('RESUMED',len(paths),'candidate paths; edge events',initial_score,flush=True)
best=10**12;lastconf=initial_conf;max_iter=int(sys.argv[1]) if len(sys.argv)>1 else 24
for iteration in range(max_iter):
 # Difficult/conflicting routes first, with deterministic tie perturbation.
 rng=random.Random(100+iteration)
 order=sorted(names,key=lambda n:(-len(lastconf.get(n,[])),-math.dist(ends[n][0],rv[n]['xy'])+rng.random()*4))
 present=min(10000.,160*(1.7**iteration));nodes=0
 for n in order:
  l=m.LAYERS.index(ends[n][1])
  if n in masks:occupancy[l]-=masks[n]
  p,edges,num=solve(n,present);nodes+=num
  if p is None:raise RuntimeError('Static path unexpectedly unavailable: '+n)
  paths[n]=p;edgepaths[n]=edges;masks[n]=pathmask(p);occupancy[l]+=masks[n]
 conf,score=conflicts();elapsed=time.monotonic()-start
 stats.append(dict(iteration=iteration,conflicting_nets=len(conf),edge_events=score,nodes=nodes,elapsed_s=elapsed,present_cost=present))
 print(json.dumps(stats[-1]),flush=True)
 if score<best:best=score;snapshot(iteration,score,conf)
 (HERE/'search-progress.json').write_text(json.dumps({'status':'RUNNING' if score else 'NOMINAL_GRID_CANDIDATE_FOUND_AWAIT_INDEPENDENT_AUDIT','best_edge_events':best,'iterations':stats},indent=2))
 if score==0:break
 for n,hits in conf.items():
  l=m.LAYERS.index(ends[n][1])
  for d,y,x,count in hits:
   increment=min(32.,2*count);history[l,d,y,x]+=increment
   dx,dy=grid.dirs[d];reverse={0:1,1:0,2:3,3:2}[d];history[l,reverse,y+dy,x+dx]+=increment
 lastconf=conf
else:
 d=json.loads((HERE/'search-progress.json').read_text());d['status']='BOUNDED_SEARCH_INCOMPLETE_WITH_CONFLICTS';(HERE/'search-progress.json').write_text(json.dumps(d,indent=2))
print('DONE best_edge_events',best,'elapsed_s',round(time.monotonic()-start,3),flush=True)
