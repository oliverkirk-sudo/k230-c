#!/usr/bin/env python3
"""Independent candidate area/rectangle sensitivity; never alters baseline CAD or screens."""
from pathlib import Path
import json, copy, random, hashlib, ast
ROOT=Path(__file__).resolve().parents[2]; M=ROOT/'engineering/mechanical'
area=json.loads((M/'passive-candidate-rectangle-input-snapshot.json').read_text())
caps=json.loads((M/'passive-capacitor-candidate-review.json').read_text())
baseline={p['reference']:p for p in area['components'] if p['reservation_dense_mm2']>0}
# Reuse only the two pure rectangle functions; do not execute the baseline tool's file writes.
tree=ast.parse((ROOT/'tools/pack_component_envelopes.py').read_text())
pure=ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ['overlaps','subtract']],type_ignores=[])
env={};exec(compile(pure,'baseline_rectangle_functions','exec'),env)
overlaps,subtract=env['overlaps'],env['subtract']
def pack(parts):
 total=sum(p['dense_reservation_xy_mm'][0]*p['dense_reservation_xy_mm'][1] for p in parts.values())
 if total>1156+1e-7:return {'result':'AREA_SUM_EXCEEDS_PROVISIONAL_INTERIOR','placed_count':None,'requested_count':len(parts),'packing_attempted':False}
 best=None
 for seed in range(20):
  free=[(0,0,34,34)];placed={};fixed={'U1':(0,0,13.5,13.5),'U2':(13.75,0,10.5,15.5),'U3':(0,13.75,12,13.5)}
  for ref,r in fixed.items():placed[ref]=r;free=subtract(free,r)
  rng=random.Random(seed);remain=[p for ref,p in parts.items() if ref not in fixed]
  remain.sort(key=lambda p:p['dense_reservation_xy_mm'][0]*p['dense_reservation_xy_mm'][1]*(1+rng.random()*.25),reverse=True)
  failed=[]
  for p in remain:
   w,h=p['dense_reservation_xy_mm'];choices=[]
   for f in free:
    for ww,hh in [(w,h),(h,w)]:
     if ww<=f[2]+1e-7 and hh<=f[3]+1e-7:choices.append(((min(f[2]-ww,f[3]-hh),max(f[2]-ww,f[3]-hh),f[1],f[0]),(f[0],f[1],ww,hh)))
   if not choices:failed.append(p['reference']);continue
   r=min(choices,key=lambda x:x[0])[1];placed[p['reference']]=r;free=subtract(free,r)
  score=(len(failed),sum(parts[r]['dense_reservation_xy_mm'][0]*parts[r]['dense_reservation_xy_mm'][1] for r in failed))
  if best is None or score<best[0]:best=(score,seed,placed,failed)
  if not failed:break
 _,seed,placed,failed=best
 for ref,r in placed.items():
  assert min(r[:2])>=-1e-7 and r[0]+r[2]<=34+1e-7 and r[1]+r[3]<=34+1e-7
  for ref2,r2 in placed.items():
   if ref<ref2:assert not overlaps(r,r2)
 return {'result':'RECTANGLES_PACKED' if not failed else 'BOUNDED_HEURISTIC_INCOMPLETE_NOT_IMPOSSIBILITY_PROOF','placed_count':len(placed),'requested_count':len(parts),'unplaced':failed,'pairwise_overlap_count':0,'seed':seed,'packing_attempted':True}

def create_case(label,res1206,res0603,remove=(),ferrites=False,coil=False):
 p=copy.deepcopy(baseline)
 for group in caps['coherent_review_candidate']['group_area_deltas']:
  for ref in group['references']:p[ref]['dense_reservation_xy_mm']=list(res0603 if group['candidate_mpn']=='CL10B475KQ8NFQC' else res1206)
 for ref in remove:del p[ref]
 if ferrites:
  for n in range(202,211):p[f'FB{n}']['dense_reservation_xy_mm']=[1.8,1.2]
 if coil:p['L21']['dense_reservation_xy_mm']=[4.1,4.2]
 total=round(sum(x['dense_reservation_xy_mm'][0]*x['dense_reservation_xy_mm'][1] for x in p.values()),4)
 return {'name':label,'status':'UNQUALIFIED_REVIEW_SCENARIO','area_mm2':total,'margin_to_1156_mm2':round(1156-total,4),
         'removed_capacitor_positions':list(remove),'candidate_capacitor_count':143-len(remove),
         'ferrite_35um_candidate':ferrites,'TI_listed_XEL3520_L21_candidate':coil,'packing':pack(p)}
cases=[]
cases.append(create_case('X7R: all input pairs, conservative maximum-land reservations',[4.9,2.4],[3,1.5]))
for s in caps['manufacturer_midpoint_assembly_sensitivities']:
 remove=caps['optional_single_input_scenario']['candidate_remove_reference_positions'] if s['count_1206_22uF']==21 else []
 cases.append(create_case(s['scenario'],s['reservation_1206_xy_mm'],s['reservation_0603_xy_mm'],remove))
s=caps['manufacturer_midpoint_assembly_sensitivities'][-1]
cases.append(create_case('X7R: four single inputs, midpoint +0.10 clearance, 35um ferrite and XEL3520 candidates',s['reservation_1206_xy_mm'],s['reservation_0603_xy_mm'],caps['optional_single_input_scenario']['candidate_remove_reference_positions'],True,True))
report={'scope':'CANDIDATE_AREA_AND_RECTANGLE_SCREEN_ONLY','baseline_dense_area_mm2':area['summary']['dense_0201_small_passives_reservation_mm2'],
        'baseline_envelopes':len(baseline),'baseline_source_sha256':hashlib.sha256((M/'passive-candidate-rectangle-input-snapshot.json').read_bytes()).hexdigest(),
        'snapshot_status':'Historical243-envelope geometry baseline before lead addedC245/C246; not currentBOM',
        'cap_source_sha256':hashlib.sha256((M/'passive-capacitor-candidate-review.json').read_bytes()).hexdigest(),
        'provisional_interior_mm':[34,34],'algorithm':'Same bounded20-seed rectangle heuristic and fixed BGA envelopes as baseline',
        'not_checked':['local decoupling location and hot loops','electrical release and guaranteed Ceff','BGA escape and route corridors','PDN and thermal behavior','component height and assembly process','real castellation geometry'],
        'cases':cases}
(M/'passive-candidate-area-packing-scenarios.json').write_text(json.dumps(report,indent=2)+'\n')
for c in cases:print(c['name'],c['area_mm2'],c['packing'])
