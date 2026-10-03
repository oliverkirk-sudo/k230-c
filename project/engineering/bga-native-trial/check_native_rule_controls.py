#!/usr/bin/env python3
"""Positive controls: stricter limits must be detected by native KiCad DRC.

The delivered candidate board/rules are read-only to this script. All copies and
reports remain under engineering/bga-native-trial/rule-controls.
"""
import os
for name, suffix in [('XDG_DATA_HOME','.local/share'),('XDG_CONFIG_HOME','.config'),('XDG_CACHE_HOME','.cache')]:
    os.environ[name] = '/tmp/kicad-footprint-home/' + suffix
import hashlib,json,subprocess,shutil
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
CAD=ROOT/'cad/bga-engineering-candidates/bh153-sparse-trial'
ENG=ROOT/'engineering/bga-native-trial'
BASE='BH153_SPARSE_LOCAL_TRIAL'
specs=[
    ('annulus', 'annular_width', .080, 'annular_width', "(condition \"A.Type == 'Via'\")"),
    ('hole_to_copper', 'hole_clearance', .280, 'hole_clearance', ''),
    ('hole_to_hole', 'hole_to_hole', .360, 'hole_to_hole', ''),
    ('mask_web', None, .110, 'solder_mask_bridge', ''),
]
result=[]
before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in CAD.glob(BASE+'.*')}
for name,constraint,minimum,expected,condition in specs:
    out=ENG/'rule-controls'/name
    out.mkdir(parents=True,exist_ok=True)
    for suffix in ['.kicad_pcb','.kicad_pro','.kicad_dru']:
        shutil.copyfile(CAD/(BASE+suffix),out/(BASE+suffix))
    shutil.copyfile(CAD/'fp-lib-table',out/'fp-lib-table')
    (out/'fp-lib-table').write_text((out/'fp-lib-table').read_text().replace('${KIPRJMOD}/BH153_Engineering.pretty',str(CAD/'BH153_Engineering.pretty')))
    if constraint:
        p=out/(BASE+'.kicad_dru')
        p.write_text(p.read_text()+f'\n(rule "POSITIVE CONTROL {name}: deliberately too strict" {condition} (constraint {constraint} (min {minimum}mm)))\n')
    else:
        p=out/(BASE+'.kicad_pcb')
        assert '(solder_mask_min_width 0.1)' in p.read_text()
        p.write_text(p.read_text().replace('(solder_mask_min_width 0.1)',f'(solder_mask_min_width {minimum})'))
    argv=['kicad-cli','pcb','drc','--format','json','--all-track-errors','--severity-all','--exit-code-violations','-o',str(out/'drc.json'),str(out/(BASE+'.kicad_pcb'))]
    r=subprocess.run(argv,capture_output=True,text=True)
    (out/'drc.log').write_text(r.stdout+r.stderr)
    assert r.returncode==5, r.stdout+r.stderr
    d=json.loads((out/'drc.json').read_text())
    counts=Counter(v['type'] for key in ['violations','unconnected_items'] for v in d[key])
    detected=counts[expected]>0
    result.append({'control':name,'candidate_limit_mm':{'annulus':.075,'hole_to_copper':.20,'hole_to_hole':.20,'mask_web':.10}[name],
        'control_limit_mm':minimum,'expected_violation':expected,'detected':detected,'violation_counts':counts,
        'exit_code':r.returncode,'report':str((out/'drc.json').relative_to(ROOT))})
after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in CAD.glob(BASE+'.*')}
assert before==after, 'Control mutated delivered candidate!'
summary={'status':'PASS' if all(x['detected'] for x in result) else 'FAIL','candidate_files_unchanged':True,'candidate_sha256':after,'controls':result}
(ENG/'rule-control-results.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
assert summary['status']=='PASS'
