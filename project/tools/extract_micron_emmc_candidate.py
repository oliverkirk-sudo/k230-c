#!/usr/bin/env python3
from pathlib import Path
import fitz,csv,json,hashlib
B=Path(__file__).resolve().parents[1];S=Path('/workspace/shared/k230-memory-review/thermal-candidates');src=S/'micron-emmc.pdf';p=fitz.open(src)[8];rows='A B C D E F G H J K L M N P'.split();found={}
for w in p.get_text('words'):
 x=(w[0]+w[2])/2;y=(w[1]+w[3])/2
 if not (127<x<480 and 170<y<505):continue
 col=round((x-137.74)/25.59)+1;row=round((y-176.45)/24.75)
 assert 1<=col<=14 and 0<=row<14,w
 k=f'{rows[row]}{col}';assert k not in found,(k,w);found[k]=w[4]
assert len(found)==153
previous={r['ball']:r for r in csv.DictReader(open(S/'MTFC16GAPALBH-AAT_grid196_physical153.csv'))}
assert set(found)=={k for k,v in previous.items() if v['physical']=='True'}
normalize=lambda v:v.upper().replace('_','').replace(' ','')
assert all(normalize(v)==normalize(previous[k]['function']) for k,v in found.items())
samsung={r['ball_or_grid']:r for r in csv.DictReader(open(B/'engineering/memory/KLMAG1JETD_grid196_physical153.csv'))}
assert set(found)=={k for k,v in samsung.items() if v['physical_ball']=='True'}
alias={'VDD':'VCCQ','VDDF':'VCC','VDDI':'VDDIM','DATASTROBE':'DS','RSTN':'RSTN'}
def canon(v):return alias.get(normalize(v),normalize(v))
changes=[]
for k,v in found.items():
 old=samsung[k]['function']
 if canon(old)!=canon(v):changes.append(dict(ball=k,samsung=old,micron=v,kind='ground_domain_name' if old=='VSS' and v=='VSSQ' else 'unused_to_vendor_function' if v.startswith('VSF') else 'unused_category' if old in ['NC','RFU'] and v in ['NC','RFU'] else 'REVIEW_FUNCTION_DIFFERENCE'))
r={'part':'MTFC16GAPALBH-AAT','status':'CANDIDATE_NOT_APPROVED_SUBSTITUTION','source_page':9,'source_url':'https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/234/EMMC_5F00_DATASHEET.pdf','source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'physical_count':153,'full_grid_count':196,'independent_text_grid_matches_first_visual_transcription':True,'grid':[dict(ball=f'{a}{c}',function=found.get(f'{a}{c}','NB'),physical=f'{a}{c}' in found) for a in rows for c in range(1,15)],'differences_from_samsung':changes,'constraints':['All VCC/VCCQ and VSS/VSSQ balls connected.','VSF balls are internally functional bidirectional pins, not NC; no external use assigned, never assume unbonded.','RFU externally floating.','CReg uses Micron exact-part network; no transfer to Samsung.','Power-up/reset and firmware behavior still need review.']}
(B/'engineering/high-temp-candidates/micron-emmc-ball-comparison.json').write_text(json.dumps(r,indent=2));print('153 balls independently matched; normalized differences:',changes)
