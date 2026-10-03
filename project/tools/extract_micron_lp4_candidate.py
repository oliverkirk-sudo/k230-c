#!/usr/bin/env python3
from pathlib import Path
import fitz,csv,json,hashlib
B=Path(__file__).resolve().parents[1];src=Path('/workspace/shared/k230-memory-review/thermal-candidates/micron-lp4.pdf');p=fitz.open(src)[20]
rows='A B C D E F G H J K L M N P R T U V W Y AA AB'.split();xs={i:123.58+(i-1)*34.017 for i in range(1,13)};found={}
for w in p.get_text('words'):
 x=(w[0]+w[2])/2;y=(w[1]+w[3])/2
 if not (110<x<515 and 138<y<577):continue
 col=min(xs,key=lambda c:abs(xs[c]-x));ri=round((y-147.3)/20.0093)
 if not 0<=ri<22 or col in [6,7] or rows[ri] in ['L','M']:raise ValueError(w)
 key=f'{rows[ri]}{col}';assert key not in found,(key,w);found[key]=w[4]
assert len(found)==200
old={r['ball_or_grid']:r for r in csv.DictReader(open(B/'engineering/memory/K4F8E304HB_grid264_physical200.csv'))}
assert set(found)=={k for k,r in old.items() if r['physical_ball']=='True'}
def norm(s):return s.upper().replace('ZQ_A','ZQ0')
changes=[{'ball':k,'samsung':old[k]['function'],'micron':v,'category':'unused_category_change' if old[k]['function'] in ['DNU','NC'] and v in ['DNU','NC'] else 'single_rank_name_alias' if (old[k]['function'].upper().startswith(('CS_','CKE_')) and v.startswith(('CS0_','CKE0_'))) else 'functional_change'} for k,v in found.items() if norm(old[k]['function'])!=norm(v)]
result={'part':'MT53E256M32D2FW-046 AAT:B','status':'DERIVED_CANDIDATE_NOT_APPROVED_SUBSTITUTION','source_pdf_page':21,'source_figure':5,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'source_url':'https://www.mouser.com/datasheet/2/671/200b_z00m_sdp_ddp_auto_lpddr4_lpddr4x-3193603.pdf','orientation':'top view ball down','physical_count':len(found),'full_grid_count':264,'grid':[{'ball':f'{r}{c}','function':found.get(f'{r}{c}','NB'),'physical':f'{r}{c}' in found} for r in rows for c in range(1,13)],'normalized_ball_function_changes_from_current_samsung':changes,'normalization_notes':['Case-insensitive channel suffixes.','Samsung ZQ_a corresponds to Micron ZQ0; Micron pin description requires240Ohm +/-1% toVDDQ.', 'CS/CKE versus CS0/CKE0 are single-rank naming aliases; no net remapping inferred.'],'remaining_gates':['Second independent grid review.','Exact order/package height/land geometry; not drop-in.','DDR timing/training/ODT/drive/ZQ protocol and temperature refresh behavior.','Temperature definition and real thermal path.']}
(B/'engineering/high-temp-candidates/micron-lp4-ball-comparison.json').write_text(json.dumps(result,indent=2));print('200 physical balls; changes:',changes)
