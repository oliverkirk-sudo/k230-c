#!/usr/bin/env python3
from pathlib import Path
import json,xml.etree.ElementTree as E,collections
B=Path(__file__).resolve().parents[1];H=B/'cad/high-temp-candidate';d=json.load(open(H/'bypass-candidate-assignments.json'));x=E.parse(H/'master.xml');cs={c.get('ref'):c for c in x.findall('.//components/comp')};review=[]
for r in d['components']:
 c=cs[r['reference']];fp='CMK230_Bypass_Candidates:Samsung_'+r['candidate_mpn']+'_MIDPOINT_LAND_DENSE_CANDIDATE'
 assert c.findtext('footprint')==fp
 assert c.findtext('value').startswith(r['nominal']+' '+r['candidate_mpn'])
 review.append({'reference':r['reference'],'mpn_candidate':r['candidate_mpn'],'nominal':r['nominal'],'footprint':fp})
for ref in d['explicitly_unselected_Micron_bypass_refs']:assert not cs[ref].findtext('footprint'),ref
assert len(review)==112
out={'status':'LAYOUT_SOURCE_ASSIGNMENTS_VERIFIED_EFFECTIVE_CAPACITANCE_AND_ASSEMBLY_OPEN','assignments':review,'count':len(review),'counts_by_mpn':dict(collections.Counter(r['mpn_candidate'] for r in review)),'strict_memory_local_bypass_not_selected':d['explicitly_unselected_Micron_bypass_refs']}
(H/'bypass-candidate-validation.json').write_text(json.dumps(out,indent=2));print('PASS112 candidate assignments; minimum-sensitive memory sites remain unselected')
