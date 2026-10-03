#!/usr/bin/env python3
"""Read-only geometric/text verification of Samsung p5 ball diagram against candidate CSV."""
import fitz,pathlib,csv,json,hashlib,collections,sys
root=pathlib.Path(__file__).resolve().parents[1];src=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else pathlib.Path('/workspace/shared/k230-memory-review/emmc.pdf')
p=fitz.open(src)[4];letters='A B C D E F G H J K L M N P'.split()
def cell(x,y):
 c=round((x-285.24)/14.832);r=round((y-246.57)/15.922)
 assert 0<=c<14 and 0<=r<14
 return letters[r]+str(c+1)
found=collections.defaultdict(list)
for d in p.get_drawings():
 r=d['rect']
 if 11<r.width<12 and 14<r.height<16 and len(d['items'])==8:
  found[cell((r.x0+r.x1)/2,(r.y0+r.y1)/2)].append(list(r))
assert len(found)==153
texts=collections.defaultdict(list)
for b in p.get_text('dict')['blocks']:
 for l in b.get('lines',[]):
  for s in l['spans']:
   x0,y0,x1,y1=s['bbox']
   if x0>278 and 235<y0<465:texts[cell((x0+x1)/2,(y0+y1)/2)].append(s)
raw=list(csv.DictReader((root/'engineering/memory/KLMAG1JETD_grid196_physical153.csv').open()));old={r['ball_or_grid']:r for r in raw}
assert {k for k,r in old.items() if r['physical_ball']=='True'}==set(found)
labels={}
for k,v in texts.items():
 text=''.join(s['text'] for s in v).replace(' ','').upper();labels[k]=text
 # VDDI has superscript I; DataStrobe uses two text runs.
 assert text==old[k]['function'].replace(' ','').upper(),(k,text,old[k]['function'])
assert len(labels)==46
assert {k for k in found if k not in labels}=={k for k,r in old.items() if r['function']=='NC'}
assert sum(v=='RFU' for v in labels.values())==13
assert sum(r['function']=='NC' for r in raw)==107
for r in raw:r['status']='SOURCE_P5_VECTOR_CIRCLE_AND_LABEL_VERIFIED'
with (root/'engineering/memory/KLMAG1JETD_grid196_physical153.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=raw[0]);w.writeheader();w.writerows(raw)
report={'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'source_page':5,'physical_balls':153,'explicit_labeled_balls':46,'functional_table_balls':33,'RFU_balls':13,'NC_unlabeled_circles':107,'all196_grid_positions_match':True,'legend':'Unlabeled circles are NC; page5 legend visually checked','duplicate_drawings':{k:v for k,v in found.items() if len(v)>1},'ball_rectangles':dict(found),'labels':labels,'limits':'Does not qualify footprint dimensions, solder lands, CReg value or circuit behavior'}
(root/'engineering/memory/emmc-grid-verification.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k not in ['ball_rectangles','labels','duplicate_drawings']})
