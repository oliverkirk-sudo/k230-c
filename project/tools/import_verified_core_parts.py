#!/usr/bin/python3
"""Import source-reviewed assigned footprints and exact nets, parked outside outline."""
from pathlib import Path
import pcbnew as k,xml.etree.ElementTree as E,re,json,hashlib,shutil
from population_contract import apply_population, validate_population
B=Path(__file__).resolve().parents[1];H=B/'cad/high-temp-candidate';O=B/'cad/verified-import-unplaced';O.mkdir(exist_ok=True)
x=E.parse(H/'master.xml');cs=x.findall('.//components/comp')
libs={n:str(Path(u.replace('${KIPRJMOD}',str(H))).resolve()) for n,u in re.findall(r'\(name "([^"]+)"\)\s*\(type "KiCad"\)\s*\(uri "([^"]+)"\)',(H/'fp-lib-table').read_text())}
b=k.LoadBoard(str(B/'cad/castellation-proposal/CMK230_Castellation_NOMINAL_PROPOSAL.kicad_pcb'));edge=list(b.GetFootprints())[0]
netmap={};pinmap={}
for n in x.findall('.//nets/net'):
 net=k.NETINFO_ITEM(b,n.get('name'));b.Add(net);netmap[n.get('name')]=net
 for p in n.findall('node'):pinmap[p.get('ref'),p.get('pin')]=n.get('name')
root=re.search(r'\(uuid "([^"]+)"\)',(H/'CMK230_Core_REVIEW.kicad_sch').read_text())[1]
plugin=k.PCB_IO_MGR.PluginFind(k.PCB_IO_MGR.KICAD_SEXP);imported=[];missing=[];i=0
for c in cs:
 ref=c.get('ref');fp=c.findtext('footprint') or ''
 if c.find("property[@name='exclude_from_board']") is not None:continue
 if not fp:missing.append(ref);continue
 lib,name=fp.split(':',1);assert lib in libs,(ref,fp)
 if ref=='J1':f=edge;f.SetFPID(k.LIB_ID(lib,name));f.SetAttributes(f.GetAttributes()|k.FP_EXCLUDE_FROM_BOM)
 else:
  f=plugin.FootprintLoad(libs[lib],name);assert f,(ref,fp)
  f.SetPosition(k.VECTOR2I(k.FromMM(78+(i%8)*8),k.FromMM(30+(i//8)*8)));b.Add(f);i+=1
 f.SetFPID(k.LIB_ID(lib,name));f.SetReference(ref);f.SetValue(c.findtext('value'))
 apply_population(c,f)
 sheet=c.find('sheetpath').get('tstamps').strip('/');symbol=c.findtext('tstamps').split()[0]
 f.SetPath(k.KIID_PATH('/'+root+'/'+sheet+'/'+symbol))
 for p in f.Pads():
  if not p.GetNumber():
   assert not p.IsOnLayer(k.F_Cu) and not p.IsOnLayer(k.B_Cu),ref
   continue
  pn=(ref,p.GetNumber());assert pn in pinmap,(ref,p.GetNumber());p.SetNet(netmap[pinmap[pn]])
 imported.append({'reference':ref,'footprint':fp,'pad_count':len(list(f.Pads())),'schematic_path':f.GetPath().AsString(),'placement':'edge fixed' if ref=='J1' else 'PARKED OUTSIDE OUTLINE; UNPLACED'})
out=O/'CMK230_Verified_Import_UNPLACED.kicad_pcb';k.SaveBoard(str(out),b)
shutil.copyfile(B/'cad/castellation-proposal/CMK230_Castellation_NOMINAL_PROPOSAL.kicad_pro',out.with_suffix('.kicad_pro'))
b=k.LoadBoard(str(out));checks=0
components_by_ref={c.get('ref'):c for c in cs}
for f in b.GetFootprints():
 validate_population(components_by_ref[f.GetReference()],f)
 for p in f.Pads():
  if not p.GetNumber():continue
  assert p.GetNetname()==pinmap[f.GetReference(),p.GetNumber()];checks+=1
assert len(list(b.GetFootprints()))==len(imported)
r={'status':'NETLIST_BOUND_PARTIAL_IMPORT_ALL_INTERNAL_PARTS_UNPLACED','source_netlist_sha256':hashlib.sha256((H/'master.xml').read_bytes()).hexdigest(),'board_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'imported_footprints':imported,'imported_count':len(imported),'checked_pad_net_bindings':checks,'still_missing_footprints':missing,'missing_count':len(missing),'tracks':len(list(b.GetTracks())),'full_parity_claimed':False}
shutil.copyfile(out,H/'CMK230_Core_REVIEW.kicad_pcb')
(O/'import-validation.json').write_text(json.dumps(r,indent=2));print(len(imported),'footprints imported;',checks,'pad nets verified;',len(missing),'missing; no internal placement')
