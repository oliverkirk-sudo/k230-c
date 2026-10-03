#!/usr/bin/env python3
"""Independent analytic emitted-geometry audit; no search masks reused.
Qualified U1/U2 object IDs; exemptions depend only on exact net identity.
"""
import csv,json,math,hashlib,html
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
EPS=1e-9

def pseg(p,a,b):
    d=np.asarray(b)-np.asarray(a);l2=float(d@d)
    t=max(0.,min(1.,float((np.asarray(p)-a)@d)/l2)) if l2 else 0.
    return math.dist(p,np.asarray(a)+t*d)
def sdist(a,b,c,d):
    def cross(p,q,r):return (q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0])
    if cross(a,b,c)*cross(a,b,d)<=0 and cross(c,d,a)*cross(c,d,b)<=0 and all(max(min(a[k],b[k]),min(c[k],d[k]))<=min(max(a[k],b[k]),max(c[k],d[k])) for k in (0,1)):return 0.
    return min(pseg(a,c,d),pseg(b,c,d),pseg(c,a,b),pseg(d,a,b))
def point_segments(points,a,b):
    d=np.asarray(b)-a;l2=d@d
    t=np.clip((points-np.asarray(a))@d/l2,0,1) if l2 else np.zeros(len(points))
    return np.linalg.norm(points-np.asarray(a)-t[:,None]*d,axis=1)
def segment_many(a,b,cs,ds):
    a=np.asarray(a);b=np.asarray(b);cs=np.asarray(cs);ds=np.asarray(ds)
    uv=ds-cs;l2=np.sum(uv*uv,axis=1)
    def q(p):
        t=np.clip(np.sum((p-cs)*uv,axis=1)/np.maximum(l2,1e-30),0,1)
        return np.linalg.norm(p-cs-t[:,None]*uv,axis=1)
    dist=np.minimum.reduce([q(a),q(b),point_segments(cs,a,b),point_segments(ds,a,b)])
    d=b-a
    o1=d[0]*(cs[:,1]-a[1])-d[1]*(cs[:,0]-a[0]);o2=d[0]*(ds[:,1]-a[1])-d[1]*(ds[:,0]-a[0]);o3=uv[:,0]*(a[1]-cs[:,1])-uv[:,1]*(a[0]-cs[:,0]);o4=uv[:,0]*(b[1]-cs[:,1])-uv[:,1]*(b[0]-cs[:,0])
    overlap=np.all(np.maximum(np.minimum(a,b),np.minimum(cs,ds))<=np.minimum(np.maximum(a,b),np.maximum(cs,ds))+1e-12,axis=1)
    dist[(o1*o2<=0)&(o3*o4<=0)&overlap]=0
    return dist

def audit(j):
    w=j['rules']['trace_width'];clear=j['rules']['copper_clearance'];hc=j['rules']['hole_to_other_copper'];pads=defaultdict(list);holes=[];tracks=[]
    for b in j['balls']:pads['L1'].append(dict(id='land:'+b['id'],net=b['net'] or '__isolated_'+b['id'],xy=[b['x'],b['y']],r=b['physical_top_land_diameter']/2,kind='land'))
    for v in j['vias']:
        for l in v['retained_annuli']:pads[l].append(dict(id='via:'+v['id'],net=v['net'],xy=v['xy'],r=v['pad']/2,kind='via'))
        holes.append(dict(id='hole:'+v['id'],net=v['net'],xy=v['xy'],r=v['hole']/2,kind='hole'))
    for ri,r in enumerate(j['routes']):
        for si,(a,b) in enumerate(zip(r['points'],r['points'][1:])):
            assert math.dist(a,b)>0
            tracks.append(dict(id=f"track:{r['id']}:{r['layer']}:{ri}:{si}",net=r['net'],layer=r['layer'],purpose=r['purpose'],ref=r['ref'],a=a,b=b,r=w/2,kind='trace'))
    checks=Counter();minima={};failures=[]
    def checkvec(kind,gaps,required,first,others,layer):
        if not len(gaps):return
        checks[kind]+=len(gaps);i=int(np.argmin(gaps));indices=np.flatnonzero(gaps<required-EPS)
        def row(k):return dict(kind=kind,a=first['id'],b=others[k]['id'],layer=layer,actual_gap_mm=round(float(gaps[k]),12),required_gap_mm=required,margin_mm=round(float(gaps[k]-required),12))
        if kind not in minima or float(gaps[i]-required)<minima[kind]['margin_mm']:minima[kind]=row(i)
        failures.extend(row(int(k)) for k in indices)
    for l,ps in pads.items():
        for i,p in enumerate(ps):
            for typ in ('land','via'):
                qs=[q for q in ps[i+1:] if q['net']!=p['net'] and q['kind']==typ]
                if qs:
                    gaps=np.linalg.norm(np.array([q['xy'] for q in qs])-p['xy'],axis=1)-p['r']-np.array([q['r'] for q in qs])
                    checkvec('copper_'+p['kind']+'_'+typ,gaps,clear,p,qs,l)
        for h in holes:
            for typ in ('land','via'):
                qs=[q for q in ps if q['net']!=h['net'] and q['kind']==typ]
                if qs:
                    gaps=np.linalg.norm(np.array([q['xy'] for q in qs])-h['xy'],axis=1)-h['r']-np.array([q['r'] for q in qs])
                    checkvec('hole_to_'+typ,gaps,hc,h,qs,l)
    for i,t in enumerate(tracks):
        for typ in ('land','via'):
            qs=[q for q in pads[t['layer']] if q['net']!=t['net'] and q['kind']==typ]
            if qs:
                gaps=point_segments(np.array([q['xy'] for q in qs]),t['a'],t['b'])-t['r']-np.array([q['r'] for q in qs])
                checkvec('trace_to_'+typ,gaps,clear,t,qs,t['layer'])
        qs=[q for q in holes if q['net']!=t['net']]
        gaps=point_segments(np.array([q['xy'] for q in qs]),t['a'],t['b'])-t['r']-np.array([q['r'] for q in qs])
        checkvec('trace_to_hole',gaps,hc,t,qs,t['layer'])
        qs=[q for q in tracks[i+1:] if q['net']!=t['net'] and q['layer']==t['layer']]
        if qs:
            gaps=segment_many(t['a'],t['b'],[q['a'] for q in qs],[q['b'] for q in qs])-w
            checkvec('trace_to_trace',gaps,clear,t,qs,t['layer'])
    return dict(status='PASS_NOMINAL_PHYSICAL_GEOMETRY' if not failures else 'FAIL_PHYSICAL_GEOMETRY',checks=sum(checks.values()),checks_by_kind=dict(checks),failure_count=len(failures),minimum_by_kind=minima,failures=failures,trace_segment_count=len(tracks),exemptions='Only exact same net; NC/DNU assigned unique package-qualified isolated net IDs'),tracks

def connectivity(j):
    balls={b['id']:b for b in j['balls']};vias={v['id']:v for v in j['vias']};routed=defaultdict(list)
    for r in j['routes']:routed[r['net']].append(r)
    records=[]
    for n in j['pernet']:
        sb='U1:'+n['soc_ball'];rb='U2:'+n['dram_ball'];sv=vias[sb];rv=vias[rb];rs=routed[n['net']]
        def find(ref,purpose):return [r for r in rs if r['ref']==ref and r['purpose']==purpose]
        local_s=find('U1','ball_to_via');local_r=find('U2','ball_to_via');exit_s=find('U1','via_to_outside_body');links=find('U1_TO_U2','actual_DDR_link')
        local_ok=len(local_s)==len(local_r)==len(exit_s)==1 and local_s[0]['points']==[[balls[sb]['x'],balls[sb]['y']],sv['xy']] and local_r[0]['points']==[[balls[rb]['x'],balls[rb]['y']],rv['xy']] and exit_s[0]['points'][0]==sv['xy']
        assert local_ok,n['net']
        complete=len(links)==1 and links[0]['points'][0]==exit_s[0]['points'][-1] and links[0]['points'][-1]==rv['xy'] and links[0]['layer']==exit_s[0]['layer'] and links[0]['layer'] in ('L3','L8') and links[0]['layer'] in rv['functional_layers']
        assert complete==n['complete_ball_to_ball']
        records.append(dict(net=n['net'],soc_ball=n['soc_ball'],dram_ball=n['dram_ball'],local_dogbones_verified=True,complete_ball_to_ball=complete,actual_via_sequence=[sb,rb] if complete else None,actual_layer_sequence=['L1',exit_s[0]['layer'],'L1'] if complete else None,actual_layer_changes=2 if complete else None))
    groups=defaultdict(list)
    for n in j['pernet']:groups[n['sink_group']].append(n)
    pair=[]
    for p in j['search']['differential_pairs']:
        ns=[next(n for n in j['pernet'] if n['net']==p['pair']+suffix) for suffix in ('_P','_N')]
        pair.append(dict(pair=p['pair'],complete=all(n['complete_ball_to_ball'] for n in ns),same_layer=ns[0]['layer']==ns[1]['layer'],layer=ns[0]['layer'],actual_vias=[n['routed_transition_count'] for n in ns],equal_actual_vias=ns[0]['routed_transition_count']==ns[1]['routed_transition_count']==2,planar_lengths_mm=[n['complete_planar_length_mm'] for n in ns],planar_length_skew_mm=abs(ns[0]['complete_planar_length_mm']-ns[1]['complete_planar_length_mm']) if all(n['complete_ball_to_ball'] for n in ns) else None,soc_package_lengths_um=[n['soc_package_trace_um'] for n in ns],dram_package_delays='UNAVAILABLE',timing_match_qualified=False))
    perball=[]
    completed={r['net'] for r in records if r['complete_ball_to_ball']}
    for b in j['balls']:
        v=vias.get(b['id']);local=[r for r in j['routes'] if r['ref']==b['ref'] and r['ball']==b['ball']]
        if b['category']=='unused':assert not v and not local;status='isolated_physical_land'
        elif b['category'] in ('power','ground'):
            assert v and any(r['layer']=='L1' and r['points'][0]==[b['x'],b['y']] and r['points'][-1]==v['xy'] for r in local);status='actual_ball_to_plane_port_via_no_PDN_claim'
        elif b['category']=='local_bias':assert not v and not local;status='local_bias_resistor_route_unsolved'
        elif b['net'] in completed:status='complete_DDR_ball_to_ball'
        elif b['ddr65']:status='local_fanout_present_DDR_link_unsolved'
        else:status='retained_K230_signal_exit'
        perball.append(dict(id=b['id'],net=b['net'],category=b['category'],status=status))
    return dict(complete_links=sum(r['complete_ball_to_ball'] for r in records),pernet=records,pairs=pair,perball=perball,perball_counts=dict(Counter(b['status'] for b in perball)),group_layers={k:sorted(set(n['layer'] for n in ns)) for k,ns in groups.items()})

def spacing(j,tracks):
    contract={n['net']:n for n in j['pernet']};nets=sorted(contract);by=defaultdict(list)
    for t in tracks:
        if t['net'] in contract and t['layer'] in ('L3','L8'):by[t['net']].append(t)
    def pair(n):return n[:-2] if n.endswith(('_P','_N')) else None
    results=[]
    for i,a in enumerate(nets):
        for b in nets[i+1:]:
            layer=contract[a]['layer']
            if layer!=contract[b]['layer'] or 'RESET_ASYNCHRONOUS' in (contract[a]['sink_group'],contract[b]['sink_group']):continue
            internal=pair(a) and pair(a)==pair(b)
            samebyte=contract[a]['sink_group']==contract[b]['sink_group'] and 'BYTE' in contract[a]['sink_group']
            normaldq=not ('DQS' in a or 'DQS' in b)
            factor=2 if samebyte and normaldq else 3;H=.130 if layer=='L3' else .1195
            for scope in ('K230_local_fanout_only','actual_interconnect_only','all_inner_layer_traces'):
                aa=[t for t in by[a] if scope=='all_inner_layer_traces' or (t['purpose']=='actual_DDR_link')==(scope=='actual_interconnect_only')]
                bb=[t for t in by[b] if scope=='all_inner_layer_traces' or (t['purpose']=='actual_DDR_link')==(scope=='actual_interconnect_only')]
                if not aa or not bb:continue
                best=(float('inf'),None,None)
                for t in aa:
                    ds=segment_many(t['a'],t['b'],[q['a'] for q in bb],[q['b'] for q in bb]);k=int(np.argmin(ds));val=float(ds[k])
                    if val<best[0]:best=(val,t,bb[k])
                center,t,q=best;gap=center-j['rules']['trace_width']
                results.append(dict(net_a=a,net_b=b,group_a=contract[a]['sink_group'],group_b=contract[b]['sink_group'],layer=layer,scope=scope,closest_segment_a=t['id'],closest_segment_b=q['id'],minimum_centerline_mm=round(center,10),minimum_copper_edge_mm=round(gap,10),pair_internal=bool(internal),figure054_factor=None if internal else factor,nominal_H_mm=H,figure054_edge_gap_target_mm=None if internal else factor*H,below_figure054_edge_gap=None if internal else gap<factor*H-EPS,text3W_edge_interpretation_below=None if internal else gap<3*j['rules']['trace_width']-EPS,text3W_center_interpretation_below=None if internal else center<3*j['rules']['trace_width']-EPS,within_pair_gap_qualified=False if internal else None))
    scopes={}
    for scope in ('K230_local_fanout_only','actual_interconnect_only','all_inner_layer_traces'):
        rows=[r for r in results if r['scope']==scope and not r['pair_internal']]
        scopes[scope]=dict(compared_net_pairs=len(rows),below_figure054_2H_or_3H=sum(r['below_figure054_edge_gap'] for r in rows),below_text3W_edge_interpretation=sum(r['text3W_edge_interpretation_below'] for r in rows),below_text3W_center_interpretation=sum(r['text3W_center_interpretation_below'] for r in rows))
    return dict(status='GUIDELINE_TARGETS_NOT_MET_NO_SI_QUALIFICATION',method='Copper trace edge distances are checked against Figure 054 2H/3H. Same DQ byte excluding DQS:2H; DQS-to-byte, CA/CK and other group separations:3H engineering screen. Actual differential P/N internal gap reported only, because no within-pair gap specified. The separate 3W text does not define edge versus center; both interpretations reported. No pad/via-to-trace extrapolation of these trace guidelines.',qualification='Short local breakout and actual inter-package link traced separately, without claiming an official breakout exception. These minima alone do not quantify coupled length or crosstalk. H values are nominal unqualified stack assumptions; no manufacturer acceptance.',summary_by_scope=scopes,records=results)

def svg(j):
    s=['<svg xmlns="http://www.w3.org/2000/svg" width="1700" height="1520" viewBox="0 0 1700 1520"><rect width="1700" height="1520" fill="white"/>','<text x="35" y="40" font-family="sans-serif" font-size="25">Bounded actual K230–FW200 links: fixed trial placement</text>','<text x="35" y="69" font-family="sans-serif" font-size="17">590 retained lands · 502 real vias · all RAM power/GND dogbones · exact 65 source joins · no timing/SI qualification</text>']
    for z,layer in enumerate(['L3','L8']):
        ox=35;oy=100+z*690;sc=53
        def tr(p):return (ox+(p[0]-4.5)*sc,oy+(p[1]-1)*sc*.58)
        # Y scale intentionally same as X for correct aspect; panels use smaller scale.
        sc=30
        def tr(p):return (ox+(p[0]-4.5)*sc,oy+(p[1]-1)*sc)
        s.append(f'<text x="{ox}" y="{oy-7}" font-family="sans-serif" font-size="22">{layer}</text>')
        for ref,p in j['placement'].items():
            if ref not in ('U1','U2'):continue
            x,y=tr([p['center'][0]-p['max_body'][0]/2,p['center'][1]-p['max_body'][1]/2]);s.append(f'<rect x="{x}" y="{y}" width="{p["max_body"][0]*sc}" height="{p["max_body"][1]*sc}" fill="#fafafa" stroke="#888" stroke-dasharray="4 3"/>')
        for b in j['balls']:
            x,y=tr([b['x'],b['y']]);s.append(f'<circle cx="{x}" cy="{y}" r="{b["physical_top_land_diameter"]/2*sc}" fill="#eee" stroke="#ccc" stroke-width=".3"><title>{html.escape(b["id"]+" "+str(b["net"]))}</title></circle>')
        for r in j['routes']:
            if r['layer']!=layer:continue
            c='#19763b' if r['purpose']=='actual_DDR_link' and layer=='L3' else '#2c56b0' if r['purpose']=='actual_DDR_link' else '#999'
            pts=' '.join(f'{x},{y}' for x,y in map(tr,r['points']));s.append(f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="{j["rules"]["trace_width"]*sc}" stroke-linejoin="round" stroke-linecap="round"><title>{html.escape(r["net"]+" "+r["purpose"])}</title></polyline>')
        for v in j['vias']:
            x,y=tr(v['xy']);c='#b3752b' if v['category']=='power' else '#444' if v['category']=='ground' else '#8b97a0';s.append(f'<circle cx="{x}" cy="{y}" r="{v["pad"]/2*sc}" fill="{c}"><title>{html.escape(v["id"]+" "+v["net"])}</title></circle><circle cx="{x}" cy="{y}" r="{v["hole"]/2*sc}" fill="white"/>')
        uns=[n for n in j['unsolved'] if n['layer']==layer]
        s.append(f'<text x="950" y="{oy+20}" font-family="sans-serif" font-size="18">Unsolved on {layer}: {len(uns)}</text>')
        for k,n in enumerate(uns):s.append(f'<text x="950" y="{oy+48+k*23}" font-family="monospace" font-size="15">{n["net"]}: U1 {n["soc_ball"]} → U2 {n["dram_ball"]}</text>')
    s.append('<text x="35" y="1480" font-family="sans-serif" font-size="16">Green/blue: actual links. Gray: fixed K230 fanout. Actual geometry is in JSON/CSV; graphic shows L3/L8 only.</text></svg>')
    (HERE/'actual-links.svg').write_text('\n'.join(s)+'\n')

def main():
    path=HERE/'actual-links.json';j=json.loads(path.read_text());geometry,tracks=audit(j);conn=connectivity(j);space=spacing(j,tracks)
    result=dict(status='PHYSICAL_PARTIAL_ROUTE_ONLY_NOT_DDR_QUALIFICATION',trial_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),geometry=geometry,connectivity=conn,spacing=space)
    (HERE/'actual-links-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    for name,rows in [('spacing',space['records']),('connectivity-perball',conn['perball']),('connectivity-pernet',conn['pernet']),('pair-audit',conn['pairs'])]:
        with (HERE/(name+'.csv')).open('w') as f:
            w=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)));w.writeheader();w.writerows([{k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in r.items()} for r in rows])
    svg(j)
    print(json.dumps(dict(geometry_status=geometry['status'],checks=geometry['checks'],failures=geometry['failure_count'],complete_links=conn['complete_links'],pairs=conn['pairs'],spacing=space['summary_by_scope']),indent=2))
if __name__=='__main__':main()
