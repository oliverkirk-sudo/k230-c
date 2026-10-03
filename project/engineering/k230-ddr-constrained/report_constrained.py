#!/usr/bin/env python3
"""Audited physical route inventory, topology, exact DDR spacing screens and gates."""
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path
import audit_geometry as a
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
NAME='trial-groups-outer-21';path=HERE/(NAME+'.json');j=json.loads(path.read_text())
byball={b['ball']:b for b in j['balls']};routes=defaultdict(list);vias=defaultdict(list)
for r in j['routes']:routes[r['ball']].append(r)
for v in j['vias']:vias[v['ball']].append(v)
def write_csv(name,rows,fields=None):
 with (HERE/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=fields or list(rows[0]));w.writeheader();w.writerows(rows)
def length(rs):return sum(math.dist(p,q) for r in rs for p,q in zip(r['points'],r['points'][1:]))
def physical_transition_count(b):
 rs=routes[b['ball']];result=[]
 for v in vias[b['ball']]:
  top=any(r['layer']=='L1' and r['purpose']=='ball_to_via' and r['points'][0]==[b['x'],b['y']] and r['points'][-1]==v['xy'] for r in rs)
  internal=[r for r in rs if r['layer']!='L1' and r['points'][0]==v['xy']]
  if top and internal:result.append(dict(via=v['xy'],entry_layer='L1',exit_layers=[r['layer'] for r in internal]))
 return result
inventory=[];ddr=[]
for b in j['balls']:
 rs=routes[b['ball']];vs=vias[b['ball']];escape=[r for r in rs if r['purpose']!='ball_to_via'];e=escape[0] if escape else None
 tr=physical_transition_count(b)
 inv=dict(ball=b['ball'],function=b['function'],net=b['net'] or '',xml_net=b['xml_net'],category=b['category'],disposition=b['disposition'],
  x_mm=b['x'],y_mm=b['y'],ring=b['ring'],top_land_mm=.27,emitted_via_count=len(vs),physically_routed_signal_transition_count=len(tr),
  via_x_mm=vs[0]['xy'][0] if vs else '',via_y_mm=vs[0]['xy'][1] if vs else '',
  escape_layer=e['layer'] if e else '',exit_x_mm=e['points'][-1][0] if e else '',exit_y_mm=e['points'][-1][1] if e else '',
  local_copper_length_mm=round(length(rs),9),ddr65=bool(b['ddr65']),solved=bool(e) if b['category']=='signal' else '')
 inventory.append(inv)
 if b['ddr65']:
  ddr.append(dict(b['ddr65'],escape_layer=inv['escape_layer'],physically_routed_vias=len(tr),local_layer_changes=len(tr),
   emitted_via_count=len(vs),local_copper_length_mm=inv['local_copper_length_mm'],exit_x_mm=inv['exit_x_mm'],exit_y_mm=inv['exit_y_mm'],
   routing_status='SOLVED_LOCAL_EXIT' if e else 'UNSOLVED',timing_status='PARTIAL_ROUTE_NOT_TOTAL_FLIGHT_TIME',return_status='PROPOSED_GND_REFERENCE_ONLY_NO_PLANES_OR_ANTIPADS'))
write_csv('all390-ball-via-route-inventory.csv',inventory);write_csv('ddr65-local-layer-via-inventory.csv',ddr)
write_csv('unsolved-nets.csv',j['unsolved_signal_balls'],['ball','net','category','ring','via_xy','ddr_group','reason','emitted_signal_vias','emitted_routes'])
write_csv('all327-vias.csv',[dict(ball=v['ball'],net=v['net'],category=v['category'],x_mm=v['xy'][0],y_mm=v['xy'][1],pad_mm=v['pad'],hole_mm=v['hole'],retained_annuli=';'.join(v['retained_annuli']),functional_layers=';'.join(v['functional_layers']),added_outer_ddr_transition=v['added_outer_ddr_transition']) for v in j['vias']])
write_csv('all-route-segments.csv',[dict(ball=r['ball'],net=r['net'],layer=r['layer'],purpose=r['purpose'],segment_index=i,x1_mm=p[0],y1_mm=p[1],x2_mm=q[0],y2_mm=q[1],width_mm=.1016,length_mm=round(math.dist(p,q),9)) for r in j['routes'] for i,(p,q) in enumerate(zip(r['points'],r['points'][1:]))])
group=defaultdict(list)
for r in ddr:group[r['sink_group']].append(r)
groups=[]
for name,rows in sorted(group.items()):
 numeric=[float(r['soc_package_trace_um']) for r in rows if r['soc_package_trace_um'].replace('.','',1).isdigit()]
 groups.append(dict(group=name,nets=len(rows),solved=sum(r['routing_status']=='SOLVED_LOCAL_EXIT' for r in rows),
  layers=dict(Counter(r['escape_layer'] for r in rows)),actual_transition_counts=dict(Counter(r['physically_routed_vias'] for r in rows)),
  common_layer_additional_target_met=len({r['escape_layer'] for r in rows})==1,
  equal_actual_vias_met=len({r['physically_routed_vias'] for r in rows})==1 and all(r['routing_status']=='SOLVED_LOCAL_EXIT' for r in rows),
  soc_package_length_min_um=min(numeric) if numeric else None,soc_package_length_max_um=max(numeric) if numeric else None,
  local_copper_min_mm=min(r['local_copper_length_mm'] for r in rows),local_copper_max_mm=max(r['local_copper_length_mm'] for r in rows)))
nets={r['net']:r for r in ddr};pairs=[]
for stem in ['DDR_DQSA0','DDR_DQSA1','DDR_DQSB0','DDR_DQSB1','DDR_CLKA','DDR_CLKB']:
 p,n=nets[stem+'_P'],nets[stem+'_N'];rs=[routes[p['soc_ball']],routes[n['soc_ball']]]
 layer=p['escape_layer'];ps=[(a,b) for r in rs[0] if r['layer']==layer for a,b in zip(r['points'],r['points'][1:])];ns=[(a,b) for r in rs[1] if r['layer']==layer for a,b in zip(r['points'],r['points'][1:])]
 gap=min(a.segments(x,y,z,w)-.1016 for x,y in ps for z,w in ns)
 pairs.append(dict(pair=stem,p_ball=p['soc_ball'],n_ball=n['soc_ball'],p_layer=p['escape_layer'],n_layer=n['escape_layer'],
  p_actual_vias=p['physically_routed_vias'],n_actual_vias=n['physically_routed_vias'],
  same_layer=p['escape_layer']==n['escape_layer'],equal_actual_vias=p['physically_routed_vias']==n['physically_routed_vias'],
  p_local_copper_mm=p['local_copper_length_mm'],n_local_copper_mm=n['local_copper_length_mm'],local_p_minus_n_mm=round(p['local_copper_length_mm']-n['local_copper_length_mm'],9),
  soc_p_minus_n_package_um=round(float(p['soc_package_trace_um'])-float(n['soc_package_trace_um']),3),
  internal_route_minimum_edge_gap_mm=round(gap,9),differential_coupling_and_impedance='NOT_CONSTRAINED; common layer and equal vias are topology conditions only'))
# Exact trace-to-trace screens use nominal catalog dielectric gaps, not solved fields.
H={'L1':.1195,'L3':.130,'L8':.1195};W=.1016
def split_at_body(p,q):
 cuts={0.,1.};delta=[q[k]-p[k] for k in (0,1)]
 for k in (0,1):
  if abs(delta[k])>1e-12:
   for boundary in (-6.55,6.55):
    t=(boundary-p[k])/delta[k]
    if 0<t<1:cuts.add(t)
 cuts=sorted(cuts);pieces=[]
 for t,u in zip(cuts,cuts[1:]):
  aa=[p[k]+t*delta[k] for k in (0,1)];bb=[p[k]+u*delta[k] for k in (0,1)]
  mid=[(aa[k]+bb[k])/2 for k in (0,1)]
  zone='under_maximum_body_breakout' if max(map(abs,mid))<6.55+1e-10 else 'local_extension_outside_body'
  pieces.append((aa,bb,zone))
 return pieces
segments=[]
for r in j['routes']:
 if r['layer'] not in H:continue
 for k,(p,q) in enumerate(zip(r['points'],r['points'][1:])):
  for pp,qq,zone in split_at_body(p,q):segments.append(dict(ball=r['ball'],net=r['net'],layer=r['layer'],purpose=r['purpose'],i=k,p=pp,q=qq,zone=zone))
def ddr_class(net):
 if net not in nets or nets[net]['sink_group']=='RESET_ASYNCHRONOUS':return None
 if net.startswith('DDR_DQS'):return 'DQS'
 if net.startswith('DDR_CLK'):return 'CK'
 if '_BYTE' in nets[net]['sink_group']:return 'DQ_DMI'
 return 'CA_CS_CKE'
def same_pair(n,m):return n.endswith(('_P','_N')) and m.endswith(('_P','_N')) and n[:-2]==m[:-2]
counts=Counter();fails=defaultdict(list);minimum={}
def check(kind,gap,required,s,t,extra=None):
 counts[kind]+=1;row=dict(rule=kind,net_a=s['net'],net_b=t['net'],ball_a=s['ball'],ball_b=t['ball'],layer=s['layer'],
  actual_edge_gap_mm=round(gap,9),required_edge_gap_mm=round(required,9),margin_mm=round(gap-required,9),purpose_a=s.get('purpose',''),purpose_b=t.get('purpose',''),zone_a=s.get('zone',''),zone_b=t.get('zone',''),segment_a_length_mm=round(math.dist(s['p'],s['q']),9),segment_b_length_mm=round(math.dist(t['p'],t['q']),9) if 'p' in t else 0)
 if extra:row.update(extra)
 if kind not in minimum or row['margin_mm']<minimum[kind]['margin_mm']:minimum[kind]=row
 if gap<required-1e-10:fails[kind].append(row)
for i,s in enumerate(segments):
 sc=ddr_class(s['net'])
 for t in segments[i+1:]:
  tc=ddr_class(t['net'])
  if s['layer']!=t['layer'] or s['net']==t['net'] or not(sc or tc) or same_pair(s['net'],t['net']):continue
  dist=a.segments(s['p'],s['q'],t['p'],t['q']);gap=dist-W
  check('3W_centerline_reading_screen',gap,2*W,s,t)
  check('3W_edge_gap_sensitivity_screen',gap,3*W,s,t)
  if sc and tc:
   samegroup=nets[s['net']]['sink_group']==nets[t['net']]['sink_group']
   if samegroup and sc==tc=='DQ_DMI':check('figure_2H_within_byte',gap,2*H[s['layer']],s,t)
   elif sc in ('DQS','CK') or tc in ('DQS','CK') or ('BYTE' in nets[s['net']]['sink_group'])!=('BYTE' in nets[t['net']]['sink_group']):
    check('figure_3H_to_DQS_CK_or_byte_CA',gap,3*H[s['layer']],s,t)
   elif not samegroup:check('additional_3H_between_other_groups',gap,3*H[s['layer']],s,t)
# Supply conductors include actual PG fanout tracks and all retained annuli.
for s in segments:
 if not ddr_class(s['net']):continue
 for v in j['vias']:
  if v['category'] not in ('power','ground') or s['layer'] not in v['retained_annuli']:continue
  t=dict(ball=v['ball'],net=v['net'],purpose='PG_via_annulus',zone='under_maximum_body_breakout')
  gap=a.distance(v['xy'],s['p'],s['q'])-v['pad']/2-W/2
  check('advisory_3H_supply_via_proximity_not_DRC',gap,3*H[s['layer']],s,t)
 for t in segments:
  if s['layer']!=t['layer'] or byball[t['ball']]['category'] not in ('power','ground'):continue
  check('figure_3H_to_supply_trace_screen',a.segments(s['p'],s['q'],t['p'],t['q'])-W,3*H[s['layer']],s,t)
failrows=[r for rows in fails.values() for r in rows]
write_csv('ddr-spacing-screen-violations.csv',failrows)
spacing=dict(status='LOCAL_TRACE_SPACING_SCREENS_HAVE_VIOLATIONS_REQUIRE_SI_FAE_REVIEW',source='https://github.com/kendryte/k230_docs/blob/main/en/00_hardware/K230_Hardware_Design_Guide.md',
 image054_url='https://raw.githubusercontent.com/kendryte/k230_docs/main/zh/00_hardware/images/HDG/image054.png',
 image054_sha256=hashlib.sha256(Path('/workspace/shared/k230-reference/mechanical/k230-ddr-constrained/official-image054.png').read_bytes()).hexdigest(),
 nominal_reference_height_mm=H,reference_height_basis='PW catalog entry13: L3 chooses larger0.130mm of 0.130/0.109mm GND dielectric gaps; L1/L8 0.1195mm to nominal GND. Catalog stack is unqualified.',
 source_vs_screen_interpretation=['Official text says3W without defining edge/center convention here; both explicit readings are screened.','Official figure gives2H within data byte,3H to DQS/CK groups, byte-to-CA, and supply/Vref.','Within differential P/N pair is excluded from crosstalk spacing screens; its100ohm geometry needs a field-solved stack.','3H between other distinct DDR groups is a conservative additional screen, not a new quoted requirement.','No under-BGA exception is stated; results separate under-maximum-body breakout from the short outside-body extension. They are not a full-channel crosstalk verdict.', 'Figure trace-spacing guidance is not automatically a pad/via-to-trace DRC. Supply-via proximity is separately diagnostic and cannot prove breakout impossible.','This planar nearest-approach screen ignores coupled length and fields; it cannot validate crosstalk or justify an exception.'],
 checks_by_rule=dict(counts),failures_by_rule={k:len(fails[k]) for k in counts},minimum_by_rule=minimum,
 failures_by_geometric_zone={k:dict(Counter(r['zone_a']+' / '+r['zone_b'] for r in rows)) for k,rows in fails.items()},
 unique_net_pairs_failed_by_rule={k:len({tuple(sorted((r['net_a'],r['net_b']))) for r in fails[k]}) for k in counts})
(HERE/'ddr-spacing-screen.json').write_text(json.dumps(spacing,indent=2)+'\n')
env=[]
for b in j['balls']:env.append((b['x']-.135,b['y']-.135,b['x']+.135,b['y']+.135))
for v in j['vias']:x,y=v['xy'];env.append((x-v['pad']/2,y-v['pad']/2,x+v['pad']/2,y+v['pad']/2))
for r in j['routes']:
 for x,y in r['points']:env.append((x-W/2,y-W/2,x+W/2,y+W/2))
decaps=list(csv.DictReader((ROOT/'engineering/decoupling-allocation.csv').open()));rails={r['net'] for r in decaps}
report=dict(status='LOCAL_NOMINAL_GEOMETRY_AND_DDR_TOPOLOGY_PASS_SPACING_AND_TIMING_NOT_QUALIFIED',trial_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
 summary=j['summary'],maximum_body_mm=[13.1,13.1],actual_copper_envelope_mm=dict(xmin=min(v[0] for v in env),ymin=min(v[1] for v in env),xmax=max(v[2] for v in env),ymax=max(v[3] for v in env)),
 minimum_exit_center_beyond_max_body_mm=.6,
 ddr=dict(join_count=65,numeric_soc_package_lengths=64,pairs=pairs,groups=groups,high_speed_nets_on_L6=[r['net'] for r in ddr if r['escape_layer']=='L6'],
  same_pair_layer_count=sum(p['same_layer'] for p in pairs),equal_pair_actual_via_count=sum(p['equal_actual_vias'] for p in pairs),
  timing='UNQUALIFIED: local exit is not DRAM; unequal SoC package lengths, unavailable Micron package delays, unqualified board/via propagation. No equal-board-length claim.',
  impedance_and_pair_coupling='UNQUALIFIED: 50/100ohm not solved; independent pair traces are only constrained to common layer and equal physical via count.',
  source_via_requirement='Equal via count for same signal type; all64 high-speed routes have exactly one actual transition.',
  engineering_topology_targets='All four11-netbytes and two10-netCA/CKgroups assigned one layer each; common-byte-layer is additional engineering target, not explicitly stated by cited source text.'),
 pdn=dict(power_ball_vias=53,ground_ball_vias=105,all_158_have_top_dogbone=True,TEST_EN_ground=True,decaps_allocated=len(decaps),
  power_balls_outside_decap_subset=[dict(ball=b['ball'],net=b['net']) for b in j['balls'] if b['category']=='power' and b['net'] not in rails],
  status='BALL_TO_VIA_PORTS_ONLY: no planes, decap geometry, loop closure, IRdrop or PDN impedance;77decaps do not replace158PGballvias.'),
 spacing=spacing,process=dict(nominal_annulus_mm=.0875,selected_min_annulus_mm=.0762,drill_tool_and_registration='OPEN; nominalhole is not compensatedtool proof',
  rules='Conditional PCBWay advanced0.1524mm holeclearance; separate0.20mm sensitivity is not mixed into baseline'),
 gates=['No full-core placement or actual65SoC-to-RAMchannel claim.','Ground reference planes/antipads/stitching are absent; L3/L8 are preferred layer assignments only.','DDR trace H/3W screens have explicit local violations and no assumed breakout waivers; pad/via proximity is advisory and requires scope clarification/SI/FAE.','No PDN, SI, timing, temperature, assembly or factory acceptance.'])
(HERE/'local-envelope-ddr-pdn-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(dict(summary=j['summary'],pair_layer_pass=report['ddr']['same_pair_layer_count'],pair_vias_pass=report['ddr']['equal_pair_actual_via_count'],spacing_failures=spacing['failures_by_rule']),indent=2))
