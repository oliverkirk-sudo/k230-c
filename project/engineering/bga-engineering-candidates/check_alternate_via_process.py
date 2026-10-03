#!/usr/bin/env python3
"""Recheck a frozen local witness against a separately published via rule set."""
from pathlib import Path
import csv,hashlib,json,math
OUT=Path(__file__).resolve().parent
SOURCE=OUT/'memory-soc-functional-escape-analysis-cu030-via030-hole015.json'
BALLS=OUT/'memory-soc-functional-balls-cu030-via030-hole015.csv'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def point_segment(p,a,b):
    v=(b[0]-a[0],b[1]-a[1]);den=v[0]**2+v[1]**2
    t=max(0,min(1,((p[0]-a[0])*v[0]+(p[1]-a[1])*v[1])/den)) if den else 0
    return math.hypot(p[0]-a[0]-t*v[0],p[1]-a[1]-t*v[1])

def main():
    w=json.loads(SOURCE.read_text())['eMMC_local_witness']
    balls=[b for b in csv.DictReader(BALLS.open()) if b['package']=='BH153']
    assert len(balls)==153 and w['assumed_drill_mm']==.15 and w['via_pad_mm']==.3
    margins=[]
    for v in w['vias']:
        for b in balls:
            if b['function']==v['net']:continue
            d=math.dist(v['xy'],[float(b['x_mm']),float(b['y_mm'])])-.15/2-.3/2-.2
            margins.append(dict(kind='via_hole_to_top_land',via=v['ball'],other=b['ball'],margin_mm=d))
        for r in w['routes']:
            if r['net']==v['net']:continue
            d=min(point_segment(v['xy'],a,b) for a,b in zip(r['points'],r['points'][1:]))-.15/2-r['width_mm']/2-.2
            margins.append(dict(kind='via_hole_to_route',via=v['ball'],other=r['ball'],layer=r['layer'],margin_mm=d))
        for u in w['vias']:
            if u['net']==v['net']:continue
            d=math.dist(v['xy'],u['xy'])-.15/2-.3/2-.2
            margins.append(dict(kind='via_hole_to_other_via_copper',via=v['ball'],other=u['ball'],margin_mm=d))
    bad=[m for m in margins if m['margin_mm'] < -1e-9]
    assert not bad,bad[:5]
    result={'status':'ALTERNATIVE_FACTORY_NOMINAL_RULE_SCREEN_ONLY_NOT_COMBINED_PROCESS_ACCEPTANCE',
        'source':{'author':'JLCPCB','url':'https://jlcpcb.com/capabilities/pcb-capabilities/',
            'access':'Public primary capability table read 2026-09-30 via web; no vendor contact or upload',
            'section':'Drilling: Min. Via hole size/diameter; Traces: Inner layer via hole to copper clearance; Via hole to Track; Via-in-Pad Process',
            'multilayer_minimum_nominal_via_hole_pad_mm':[.15,.25],
            'preferred_pad_diameter_increase_over_hole_mm':.15,
            'inner_via_hole_to_copper_mm':.2,'via_hole_to_track_mm':.2,
            'via_in_pad':'Filled and plated-over option described; default on 6+ layers',
            'scope_caveat':'Via-specific rules are distinct from component PTH annular-ring rules. This is not permission to change the frozen PCBWay stack or to apply via rules to castellations.'},
        'input_sha256':{SOURCE.name:sha(SOURCE),BALLS.name:sha(BALLS)},
        'geometry':{'BGA_copper_mm':.3,'via_copper_mm':.3,'nominal_via_hole_request_mm':.15,
                    'nominal_annulus_mm':.075,'selected_trace_width_clearance_mm':[.1016,.1016],
                    'physical_lands':153,'modeled_vias':len(w['vias'])},
        'checks':{'additional_drill_to_copper_checks':len(margins),'failures':bad,
                   'minimum_margin_mm':min(m['margin_mm'] for m in margins),
                   'tightest':sorted(margins,key=lambda m:m['margin_mm'])[:8],
                   'original_copper_checks':'Unchanged geometry inherits the separately reviewed 22031 copper/route checks; this script independently checks the stricter 0.20 mm hole-to-copper rules only.'},
        'conclusion':'The 0.075 mm annulus fails the chosen PCBWay 3 mil criterion but is not a universal topology rejection: nominal 0.30/0.15 mm matches JLCPCB preferred diameter-increase guidance and this sparse witness passes its 0.20 mm hole-clearance screen.',
        'open_gates':['JLCPCB castellation capability/help/article contradictions and four-edge panel support','A complete JLCPCB eight-layer stack with this via process, instead of silently borrowing the PCBWay dielectric schedule','Finished bore versus actual tool and registration/etch/breakout acceptance','Exact Micron NSMD land/mask/stencil/reliability qualification','Soldermask tolerances, copper thickness, reference-plane continuity, PDN and complete routing']}
    (OUT/'alternate-via-process-check.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result['checks'],indent=2))

if __name__=='__main__':main()
