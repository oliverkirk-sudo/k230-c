#!/usr/bin/env python3
"""Validate the actual recovered R7 fixture against the current master; no source edits."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,xml.etree.ElementTree as ET
import derive_assembly_paste as policy
from test_policy import plot,normalized_gerber,layer_file
p=argparse.ArgumentParser();p.add_argument('--project',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();P=a.project.resolve();O=a.out.resolve();O.mkdir(parents=True,exist_ok=False)
h=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
A=P/'cad/recovery-physical-candidate';master=A/'master.xml';contract=P/'tools/population_contract.py';D=P/'recovery/r7-links-and-features/independent';source=D/'INDEPENDENT_R7_FEATURES_REVIEW_ONLY.kicad_pcb';oldhash=h(source)
cs={c.attrib['ref']:c for c in ET.parse(master).getroot().findall('./components/comp')}
table=(A/'fp-lib-table').read_text();libs={name:Path(uri.replace('${KIPRJMOD}',str(A))).resolve()for name,uri in re.findall(r'\(lib \(name "([^"]+)"\).*?\(uri "([^"]+)"\)',table,re.S)}
s=source.read_text();tree=policy.parse(s);edits=[];aliases=[]
for fp in tree.nodes('footprint'):
 ref=policy.ref_of(fp);old=fp.children[1];target=cs[ref].findtext('footprint');lib,name=target.split(':')
 assert old.value=='Audit_Footprints:'+name,(ref,old.value,target)
 local=D/'Audit_Footprints.pretty'/(name+'.kicad_mod');original=libs[lib]/(name+'.kicad_mod');assert h(local)==h(original),(ref,local,original)
 edits.append((old.start,old.end,json.dumps(target)));aliases.append({'ref':ref,'old_alias':old.value,'authoritative_FPID':target,'source_library_sha256':h(original)})
for start,end,text in sorted(edits,reverse=True):s=s[:start]+text+s[end:]
normalized=O/'R7_AUTHORITATIVE_ALIASES_REVIEW_ONLY.kicad_pcb';normalized.write_text(s);shutil.copy2(source.with_suffix('.kicad_pro'),normalized.with_suffix('.kicad_pro'))
derived=O/'R7_DNP_PASTE_DERIVED_REVIEW_ONLY.kicad_pcb';r=policy.derive(normalized,derived,master,contract,True);shutil.copy2(source.with_suffix('.kicad_pro'),derived.with_suffix('.kicad_pro'))
assert len(r['changes'])==2 and {c['ref']for c in r['changes']}=={'R528'}
assert all(c['action']=='remove_paste_only_aperture'for c in r['changes'])
plot(normalized,O/'source-cam');plot(derived,O/'derived-cam')
for layer in ['F.Cu','B.Cu','F.Mask','B.Mask','F.Fab','Edge.Cuts']:
 assert normalized_gerber(layer_file(O/'source-cam',layer))==normalized_gerber(layer_file(O/'derived-cam',layer)),layer
flash=lambda f:len(re.findall(r'D03\*',f.read_text()))
counts={layer:{'source':flash(layer_file(O/'source-cam',layer)),'derived':flash(layer_file(O/'derived-cam',layer))}for layer in ['F.Cu','F.Mask','F.Paste','B.Paste']}
assert counts['F.Cu']=={'source':18,'derived':18}and counts['F.Mask']=={'source':18,'derived':18}and counts['F.Paste']=={'source':14,'derived':12}and counts['B.Paste']=={'source':0,'derived':0}
assert h(source)==oldhash
report={'status':'PASS_REVIEW_ONLY','fixture_scope':'Actual recovered ten-reference R7 geometry; library aliases alone normalized after exact source-file hash equality. No core board claim.','source_project_path':str(source.relative_to(P)),'source_sha256':oldhash,'aliases':aliases,'derivation':r,'CAM_flashes':counts,'preserved_CAM_layers':['F.Cu','B.Cu','F.Mask','B.Mask','F.Fab','Edge.Cuts'],'source_unchanged':True,'master_sha256':h(master),'qualification':'No stencil process or full-core manufacturing qualification'}
(O/'recovered-fixture-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'CAM_flashes':counts}))
