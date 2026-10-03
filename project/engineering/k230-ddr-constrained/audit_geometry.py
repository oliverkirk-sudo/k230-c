#!/usr/bin/env python3
"""Exact continuous geometric checks of emitted route primitives.

Independent from the search edge masks. No raster clearance approximation.
Circles represent copper lands/annuli; round-ended segments represent traces.
Unconnected top solder lands are treated as unique isolated copper nets.
"""
import csv, hashlib, html, json, math, sys
from collections import Counter,defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
EPS=1e-10
def distance(p,a,b):
    u=[b[0]-a[0],b[1]-a[1]]; den=sum(x*x for x in u)
    t=min(1.,max(0.,sum((p[i]-a[i])*u[i] for i in (0,1))/den)) if den else 0.
    return math.hypot(*(p[i]-a[i]-t*u[i] for i in (0,1)))
def segments(a,b,c,d):
    def cross(p,q,r):return (q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0])
    if cross(a,b,c)*cross(a,b,d)<=0 and cross(c,d,a)*cross(c,d,b)<=0:
        if all(max(min(a[k],b[k]),min(c[k],d[k]))<=min(max(a[k],b[k]),max(c[k],d[k])) for k in (0,1)):return 0.
    return min(distance(a,c,d),distance(b,c,d),distance(c,a,b),distance(d,a,b))

def audit(j,hc):
    rules=j['rules'];w=rules['trace_width'];clear=rules['copper_clearance']
    checks=Counter();minimum={};fail=[];bylayer=defaultdict(list);holes=[];tracks=[]
    def check(kind,gap,required,a,b,layer):
        margin=gap-required;checks[kind]+=1
        r=dict(kind=kind,a=a,b=b,layer=layer,actual_gap_mm=round(gap,12),required_gap_mm=required,margin_mm=round(margin,12))
        if kind not in minimum or margin<minimum[kind]['margin_mm']:minimum[kind]=r
        if margin<-EPS:fail.append(r)
    for b in j['balls']:
        bylayer['L1'].append(dict(id='land:'+b['ball'],ball=b['ball'],net=b['net'] or '__open_'+b['ball'],xy=[b['x'],b['y']],r=b['physical_top_land_diameter']/2,kind='land'))
    for v in j['vias']:
        for l in v['retained_annuli']:
            bylayer[l].append(dict(id='via:'+v['ball'],ball=v['ball'],net=v['net'],xy=v['xy'],r=v['pad']/2,kind='via'))
        holes.append(dict(id='hole:'+v['ball'],ball=v['ball'],net=v['net'],xy=v['xy'],r=v['hole']/2))
    for i,r in enumerate(j['routes']):
        for k,(a,b) in enumerate(zip(r['points'],r['points'][1:])):
            tracks.append(dict(id=f"track:{r['ball']}:{r['layer']}:{k}",ball=r['ball'],net=r['net'],layer=r['layer'],a=a,b=b,r=w/2))
    for layer,pads in bylayer.items():
        for i,a in enumerate(pads):
            for b in pads[i+1:]:
                if a['net']==b['net']:continue
                check('copper_'+a['kind']+'_'+b['kind'],math.dist(a['xy'],b['xy'])-a['r']-b['r'],clear,a['id'],b['id'],layer)
        for h in holes:
            for p in pads:
                if h['net']==p['net']:continue
                check('hole_to_'+p['kind'],math.dist(h['xy'],p['xy'])-h['r']-p['r'],hc,h['id'],p['id'],layer)
    for i,a in enumerate(tracks):
        for p in bylayer[a['layer']]:
            if a['net']==p['net']:continue
            check('trace_to_'+p['kind'],distance(p['xy'],a['a'],a['b'])-p['r']-a['r'],clear,a['id'],p['id'],a['layer'])
        for h in holes:
            if a['net']==h['net']:continue
            check('hole_to_trace',distance(h['xy'],a['a'],a['b'])-h['r']-a['r'],hc,h['id'],a['id'],a['layer'])
        for b in tracks[i+1:]:
            if a['layer']!=b['layer'] or a['net']==b['net']:continue
            check('trace_to_trace',segments(a['a'],a['b'],b['a'],b['b'])-a['r']-b['r'],clear,a['id'],b['id'],a['layer'])
    min_drill=min((math.dist(a['xy'],b['xy'])-a['r']-b['r'],a['ball'],b['ball']) for i,a in enumerate(holes) for b in holes[i+1:])
    connectivity=[]
    vias={v['ball']:v for v in j['vias']};routes=defaultdict(list)
    for r in j['routes']:routes[r['ball']].append(r)
    for b in j['balls']:
        rs=routes[b['ball']];p=[b['x'],b['y']];v=vias.get(b['ball'])
        if b['category']=='unused':
            ok=not rs and not v
            status='physical_land_retained_intentionally_open' if ok else 'ERROR_OPEN_BALL_CONNECTED'
        elif b['category'] in ('power','ground'):
            ok=v is not None and len([r for r in rs if r['layer']=='L1' and r['points'][0]==p and r['points'][-1]==v['xy']])==1
            status='one_dedicated_via_ball_connection_present_plane_port_only' if ok else 'ERROR_MISSING_PDN_BALL_VIA'
        else:
            escape=[r for r in rs if r['purpose'] in ('direct_signal_escape','via_to_outside_body')]
            ok=len(escape)==1
            if ok:
                r=escape[0];ok=max(map(abs,r['points'][-1]))>j['search']['body_half_width_mm']+EPS
                if r['layer']=='L1':ok &= r['points'][0]==p
                else:
                    ok &= bool(v and r['points'][0]==v['xy'] and r['layer'] in v['functional_layers'] and any(t['layer']=='L1' and t['points'][0]==p and t['points'][-1]==v['xy'] for t in rs))
            status='signal_continuous_to_outside_body' if ok else 'UNSOLVED_SIGNAL'
        connectivity.append(dict(ball=b['ball'],net=b['net'],category=b['category'],status=status))
    return dict(status='PASS_NOMINAL_LOCAL_GEOMETRY_ONLY' if not fail and not any(r['status'].startswith(('ERROR','UNSOLVED')) for r in connectivity) else 'INCOMPLETE_OR_FAIL',
        hole_to_other_copper_mm=hc,checks=sum(checks.values()),checks_by_kind=dict(checks),failure_count=len(fail),
        minimum_by_kind=minimum,failures=fail,minimum_drill_edge_separation=dict(gap_mm=min_drill[0],balls=list(min_drill[1:]),qualification='measured only; tool-to-tool fabrication rule not selected'),
        connectivity=connectivity,connectivity_counts=dict(Counter(r['status'] for r in connectivity)),
        method='analytic circle/circle, point/segment and segment/segment distances on actual emitted coordinates; all different-net copper and drill-to-other-net copper checked')

def svg(j,out):
    colors={'L1':'#ba3030','L3':'#2e7d32','L6':'#6a3dad','L8':'#2051a7'}
    s=['<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1740" viewBox="0 0 1600 1740">','<rect width="1600" height="1740" fill="#fff"/>',
        '<text x="35" y="40" font-family="sans-serif" font-size="27">K230 DDR topology-constrained local fanout</text>',
        '<text x="35" y="70" font-family="sans-serif" font-size="17">390 physical lands · 209 signals · 327 real vias (158 PG) · all via annuli retained</text>']
    for idx,layer in enumerate(['L1','L3','L6','L8']):
        ox=30+(idx%2)*785;oy=110+(idx//2)*785;scale=49
        def tr(p):return [ox+365+p[0]*scale,oy+380+p[1]*scale]
        s.append(f'<text x="{ox}" y="{oy}" font-family="sans-serif" font-size="23">{layer}: {sum(r["layer"]==layer and r["purpose"]!="ball_to_via" for r in j["routes"])} signal exits</text>')
        body=j['search']['body_half_width_mm'];x,y=tr([-body,-body]);s.append(f'<rect x="{x}" y="{y}" width="{2*body*scale}" height="{2*body*scale}" fill="#fafafa" stroke="#777" stroke-dasharray="5 4"/>')
        for b in j['balls']:
            x,y=tr([b['x'],b['y']]);fc={'signal':'#a7b9cd','ground':'#999','power':'#eeaf55','unused':'#fff'}[b['category']]
            s.append(f'<circle cx="{x}" cy="{y}" r="{.135*scale}" fill="{fc if layer=="L1" else "#f1f1f1"}" stroke="#aaa" stroke-width=".45"><title>{html.escape(b["ball"]+" "+str(b["net"]))}</title></circle>')
        for r in j['routes']:
            if r['layer']!=layer:continue
            pts=' '.join(f'{x},{y}' for x,y in map(tr,r['points']))
            s.append(f'<polyline points="{pts}" fill="none" stroke="{colors[layer]}" stroke-width="{j["rules"]["trace_width"]*scale}" stroke-linecap="round" stroke-linejoin="round"><title>{html.escape(r["ball"]+" "+r["net"])}</title></polyline>')
        for v in j['vias']:
            x,y=tr(v['xy']);c='#a55f00' if v['category']=='power' else '#444' if v['category']=='ground' else colors[layer]
            s.append(f'<circle cx="{x}" cy="{y}" r="{v["pad"]/2*scale}" fill="{c}"><title>{v["ball"]} {v["net"]}</title></circle><circle cx="{x}" cy="{y}" r="{v["hole"]/2*scale}" fill="white"/>')
        for b in j['unsolved_signal_balls']:
            x,y=tr(b['via_xy']);s.append(f'<circle cx="{x}" cy="{y}" r="12" fill="none" stroke="#f00" stroke-width="2"/><text x="{x+13}" y="{y}" fill="#f00" font-size="14">{b["ball"]}</text>')
    s.extend(['<text x="35" y="1700" font-family="sans-serif" font-size="17">Conditional PCBWay advanced process: 0.1016 mm trace/clearance, 0.325/0.15 mm vias, hole clearance 0.1524 mm</text>',
      '<text x="35" y="1727" font-family="sans-serif" font-size="17">DDR pairs: common layer / real via count. Spacing, coupling, timing, PDN and factory acceptance remain unqualified.</text>','</svg>'])
    out.write_text('\n'.join(s)+'\n')

def main():
    path=Path(sys.argv[1]);j=json.loads(path.read_text());name=path.stem
    result=dict(trial_file=path.name,trial_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        nominal=audit(j,j['rules']['hole_to_other_copper']),separate_hole_clearance_0p20=audit(j,.20))
    (HERE/(name+'-audit.json')).write_text(json.dumps(result,indent=2)+'\n')
    svg(j,HERE/(name+'.svg'))
    for k in ['nominal','separate_hole_clearance_0p20']:
        a=result[k];print(k,a['status'],'checks',a['checks'],'failures',a['failure_count'],a['connectivity_counts'])

if __name__=='__main__':main()
