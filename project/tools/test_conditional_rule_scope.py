#!/usr/bin/python3
from pathlib import Path
import pcbnew as k,json,shutil,subprocess,os
B=Path(__file__).resolve().parents[1];S=B/'cad/conditional-process-check';O=B/'engineering/process-rule-controls';O.mkdir(exist_ok=True)
env=dict(os.environ,XDG_CONFIG_HOME='/tmp/k230home/config',XDG_CACHE_HOME='/tmp/k230home/cache',XDG_DATA_HOME='/tmp/k230home/data',KICAD_CONFIG_HOME='/tmp/k230home/config');res=[]
for case in ['listed_pair_intrusion','foreign_track']:
 b=k.LoadBoard(str(S/'CMK230_Core_REVIEW.kicad_pcb'));f=next(f for f in b.GetFootprints() if f.GetReference()=='U22');p={p.GetNumber():p for p in f.Pads() if p.GetNumber()}
 if case=='listed_pair_intrusion':
  q=p['A2'];v=q.GetPosition();q.SetPosition(k.VECTOR2I(v.x-k.FromMM(.04),v.y))
 else:
  q=p['A1'];v=q.GetPosition();xx=k.ToMM(v.x)-k.ToMM(q.GetSize().x)/2-.085-.1016/2
  t=k.PCB_TRACK(b);t.SetStart(k.VECTOR2I(k.FromMM(xx),v.y-k.FromMM(.05)));t.SetEnd(k.VECTOR2I(k.FromMM(xx),v.y+k.FromMM(.05)));t.SetWidth(k.FromMM(.1016));t.SetLayer(k.F_Cu);t.SetNet(p['A2'].GetNet());b.Add(t)
 out=O/(case+'.kicad_pcb');k.SaveBoard(str(out),b)
 for ext in ['.kicad_pro','.kicad_dru']:shutil.copyfile(S/('CMK230_Core_REVIEW'+ext),out.with_suffix(ext))
 report=out.with_suffix('.json');run=subprocess.run(['kicad-cli','pcb','drc','--format','json','-o',str(report),str(out)],env=env,capture_output=True,text=True);assert run.returncode==0,run.stderr
 d=json.load(open(report));cs=[r for r in d['violations'] if r['type']=='clearance']
 expected='Source YCG U22 A1-A2 local3mil' if case=='listed_pair_intrusion' else 'Proposed general 4mil clearance'
 hits=[r for r in cs if expected in r['description']];assert hits,(case,cs)
 res.append({'case':case,'expected_rule_triggered':expected,'clearance_failures':len(cs),'matching_failures':len(hits),'status':'PASS_CONTROL_DETECTS_INTENTIONAL_DEFECT'})
(O/'scope-control-validation.json').write_text(json.dumps({'status':'NO_ARBITRARY_COPPER_WAIVER','controls':res,'note':'These intentionally defective test boards are not design variants or manufacturing files.'},indent=2));print(json.dumps(res,indent=2))
