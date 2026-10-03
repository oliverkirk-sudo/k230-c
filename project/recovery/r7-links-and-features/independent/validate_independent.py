#!/usr/bin/python3
"""Read-only R7 audit. Output is an isolated review fixture, never production CAD."""
import argparse,copy,csv,hashlib,importlib.util,json,os,re,shutil,subprocess
from pathlib import Path
import sys
sys.dont_write_bytecode=True
import xml.etree.ElementTree as ET
import pcbnew as k
ap=argparse.ArgumentParser();ap.add_argument('--baseline',type=Path,required=True);ap.add_argument('--project',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--runtime',type=Path,required=True);a=ap.parse_args();B=a.baseline.resolve();P=a.project.resolve();O=a.output.resolve();T=a.runtime.resolve();O.mkdir(parents=True,exist_ok=True);T.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
env=os.environ.copy()
for key,leaf in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data')]:
 (T/leaf).mkdir(exist_ok=True);env[key]=str(T/leaf);os.environ[key]=str(T/leaf)
logs={}
def run(key,args):
 r=subprocess.run(['kicad-cli',*args],capture_output=True,text=True,env=env,timeout=90);logs[key]={'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr};assert r.returncode in [0,5],logs[key];return r
tracked=[p for p in (P/'cad').rglob('*') if p.is_file() and p.suffix in ['.kicad_sch','.kicad_pcb','.kicad_mod','.kicad_sym','.kicad_pro']]
before={str(p.relative_to(P)):sha(p) for p in tracked}
for label,root in [('r6',B),('r7',P)]:
 dest=T/label/'cad/recovery-physical-candidate';shutil.copytree(root/'cad',T/label/'cad',dirs_exist_ok=True)
 run(label+'_netlist',['sch','export','netlist','--format','kicadxml','-o',str(O/(label+'-fresh.xml')),str(dest/'CMK230_Core_REVIEW.kicad_sch')])
def graph(f):
 t=ET.parse(f);c={x.get('ref'):dict(value=x.findtext('value'),footprint=x.findtext('footprint') or '',properties=sorted((q.get('name'),q.get('value','')) for q in x.findall('property'))) for x in t.findall('./components/comp')};n={ (q.get('ref'),q.get('pin')):(x.get('name'),q.get('pinfunction',''),q.get('pintype','')) for x in t.findall('./nets/net') for q in x.findall('node')};return t,c,n
bt,bc,bn=graph(O/'r6-fresh.xml');pt,pc,pn=graph(O/'r7-fresh.xml');refs={'R205','R206','R220','R221','R401','R528','R561','JP1','TP81','TP82'};features={'JP1','TP81','TP82'}
assert len(bc)==len(pc)==254 and bn==pn and len(pn)==1509
assert {r for r in pc if pc[r]['value']!=bc[r]['value']}==set()
assert {r for r in pc if pc[r]['footprint']!=bc[r]['footprint']}==refs
assert {r for r in pc if pc[r]['properties']!=bc[r]['properties']}==features
for r in pc:
 exp=copy.deepcopy(bc[r]);exp['footprint']=pc[r]['footprint']
 if r in features: exp['properties']=sorted(exp['properties']+[('exclude_from_bom','')])
 assert exp==pc[r],r
assert [r for r in pc if ('dnp','') in pc[r]['properties']]==[r for r in bc if ('dnp','') in bc[r]['properties']]
assert {r for r in pc if ('dnp','') in pc[r]['properties']}=={'JP1','R45','R47','R528'}
# Parse and normalize only the explicitly allowed schematic changes.
def sexp(text):
 toks=re.findall(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+',text);stack=[];out=[]
 for t in toks:
  if t=='(':x=[]; (stack[-1] if stack else out).append(x);stack.append(x)
  elif t==')':stack.pop()
  else:stack[-1].append(json.loads(t) if t.startswith('"') else t)
 assert not stack and len(out)==1;return out[0]
def children(x,key):return [y for y in x if isinstance(y,list) and y and y[0]==key]
def one(x,key):return children(x,key)[0]
field_changes=[];rev_changes=[];bom_changes=[]
bs=B/'cad/recovery-physical-candidate';ps=P/'cad/recovery-physical-candidate'
assert {p.name for p in bs.glob('*.kicad_sch')}=={p.name for p in ps.glob('*.kicad_sch')}
for old in bs.glob('*.kicad_sch'):
 x=sexp(old.read_text());y=sexp((ps/old.name).read_text());xn=copy.deepcopy(x);yn=copy.deepcopy(y)
 xr=one(one(xn,'title_block'),'rev');yr=one(one(yn,'title_block'),'rev')
 if xr!=yr:rev_changes.append({'file':old.name,'before':xr[1],'after':yr[1]});yr[1]=xr[1]
 xs={one(z,'uuid')[1]:z for z in children(xn,'symbol')};ys={one(z,'uuid')[1]:z for z in children(yn,'symbol')};assert set(xs)==set(ys)
 for u,sym in xs.items():
  other=ys[u];props={v[1]:v for v in children(sym,'property')};q={v[1]:v for v in children(other,'property')};r=props['Reference'][2]
  if props.get('Footprint')!=q.get('Footprint'):
   assert r in refs and props['Footprint'][2]=='';field_changes.append(r);q['Footprint'][2]=props['Footprint'][2]
  if one(sym,'in_bom')!=one(other,'in_bom'):
   assert r in features and one(sym,'in_bom')[1]=='yes' and one(other,'in_bom')[1]=='no';bom_changes.append(r);one(other,'in_bom')[1]='yes'
  assert one(sym,'on_board')==one(other,'on_board') and one(sym,'dnp')==one(other,'dnp')
 assert xn==yn,old.name
assert set(field_changes)==refs and len(field_changes)==10 and set(bom_changes)==features and len(bom_changes)==3
assert rev_changes==[{'file':'CMK230_Core_REVIEW.kicad_sch','before':'RCV-R6','after':'RCV-R7'}]
# Resolve actual library files and load through KiCad, independent of assignment JSON.
libtree=sexp((ps/'fp-lib-table').read_text());libpaths={one(l,'name')[1]:Path(one(l,'uri')[1].replace('${KIPRJMOD}',str(ps))).resolve() for l in children(libtree,'lib')}
fps={};source_files={}
for r in refs:
 lib,name=pc[r]['footprint'].split(':');source_files[r]=libpaths[lib]/(name+'.kicad_mod');fps[r]=k.FootprintLoad(str(libpaths[lib]),name);assert fps[r]
mm=k.ToMM
numbered=lambda f:{p.GetNumber():p for p in f.Pads() if p.GetNumber()}
def geom(f,w,h,ctr):
 d=numbered(f);assert set(d)=={'1','2'}
 for n,x in [('1',-ctr),('2',ctr)]:
  p=d[n];assert p.GetShape()==k.PAD_SHAPE_RECT and [round(mm(p.GetSize().x),6),round(mm(p.GetSize().y),6)]==[w,h];assert [round(mm(p.GetPosition().x),6),round(mm(p.GetPosition().y),6)]==[x,0];assert p.IsOnLayer(k.F_Cu) and not p.IsOnLayer(k.B_Cu)
for r,w,h,c in [('R205',.55,.6,.475),('R206',.55,.6,.475),('R220',1.01,1.01,.755),('R561',.5,.6,.45),('R221',.28,.43,.255),('R401',.28,.43,.255),('R528',.28,.43,.255),('JP1',.7,1.,.5)]:geom(fps[r],w,h,c)
for r in features:
 f=fps[r];assert not f.IsBoardOnly() and f.IsExcludedFromBOM() and f.IsExcludedFromPosFiles();assert not any(p.IsOnLayer(k.F_Paste) or p.IsOnLayer(k.B_Paste) for p in f.Pads());assert not any(g.GetLayer() in [k.F_Cu,k.B_Cu] for g in f.GraphicalItems())
for r in ['TP81','TP82']:
 d=numbered(fps[r]);assert list(d)==['1'];p=d['1'];assert p.GetShape()==k.PAD_SHAPE_CIRCLE and p.GetSize().x==p.GetSize().y==k.FromMM(.8) and p.GetDrillSize().x==p.GetDrillSize().y==0
for r,body,court in [('R220',[1.8,1.02],[3.12,1.62]),('R561',[1.1,.6],[2,1.2])]:
 f=fps[r]
 for layer,expect in [(k.F_Fab,body),(k.F_CrtYd,court)]:
  shapes=[g for g in f.GraphicalItems() if g.GetLayer()==layer and isinstance(g,k.PCB_SHAPE)];assert len(shapes)==1
  z=shapes[0];assert [round(abs(mm(z.GetEnd().x-z.GetStart().x)),6),round(abs(mm(z.GetEnd().y-z.GetStart().y)),6)]==expect
 assert len(list(f.Pads()))==4 and len([p for p in f.Pads() if not p.GetNumber() and p.IsOnLayer(k.F_Paste)])==2
# Import the common helper and test real attributes and negative controls.
spec=importlib.util.spec_from_file_location('review_population_contract',P/'tools/population_contract.py');pop=importlib.util.module_from_spec(spec);spec.loader.exec_module(pop)
elements={x.get('ref'):x for x in pt.findall('./components/comp')};neg=[]
for r,f in fps.items():
 beforepads=[(p.GetNumber(),p.GetPosition().x,p.GetPosition().y,p.GetSize().x,p.GetSize().y) for p in f.Pads()];pop.apply_population(elements[r],f);pop.validate_population(elements[r],f);assert beforepads==[(p.GetNumber(),p.GetPosition().x,p.GetPosition().y,p.GetSize().x,p.GetSize().y) for p in f.Pads()]
 assert f.IsDNP()==(r in ['JP1','R528']);assert f.IsExcludedFromBOM()==(r in features);assert f.IsExcludedFromPosFiles()==(r in features or r=='R528');assert not f.IsBoardOnly()
for ref,mutation,label in [('R220',lambda f:f.SetBoardOnly(True),'BoardOnly on resistor'),('JP1',lambda f:f.SetBoardOnly(True),'BoardOnly on schematic bridge'),('R528',lambda f:f.SetExcludedFromPosFiles(False),'DNP resistor added to positions'),('TP81',lambda f:f.SetExcludedFromPosFiles(False),'test pad added to positions'),('JP1',lambda f:f.SetDNP(False),'bridge populated by default'),('TP82',lambda f:f.SetExcludedFromBOM(False),'test pad added to BOM')]:
 f=fps[ref].Duplicate();mutation(f)
 try:pop.validate_population(elements[ref],f)
 except AssertionError:neg.append(label)
 else:raise AssertionError('Missed control: '+label)
# Isolated ten-reference fixture; retain distinct source nets on the real electrical pads.
b=k.BOARD();b.SetCopperLayerCount(6);nets={};positions={r:(5+7*(i%5),5+7*(i//5)) for i,r in enumerate(sorted(refs))};fixture_lib=O/'Audit_Footprints.pretty';fixture_lib.mkdir(exist_ok=True)
for r in sorted(refs):
 f=fps[r];f.SetReference(r);f.SetValue(pc[r]['value']);f.SetPosition(k.VECTOR2I(*[k.FromMM(v) for v in positions[r]]));name=pc[r]['footprint'].split(':')[1];shutil.copy2(source_files[r],fixture_lib/(name+'.kicad_mod'));f.SetFPID(k.LIB_ID('Audit_Footprints',name));b.Add(f)
 for num,pad in numbered(f).items():
  n=pn[(r,num)][0]
  if n not in nets:nets[n]=k.NETINFO_ITEM(b,n);b.Add(nets[n])
  pad.SetNet(nets[n])
for start,end in [((0,0),(38,0)),((38,0),(38,20)),((38,20),(0,20)),((0,20),(0,0))]:
 g=k.PCB_SHAPE();g.SetShape(k.SHAPE_T_SEGMENT);g.SetStart(k.VECTOR2I(*[k.FromMM(v) for v in start]));g.SetEnd(k.VECTOR2I(*[k.FromMM(v) for v in end]));g.SetWidth(k.FromMM(.05));g.SetLayer(k.Edge_Cuts);b.Add(g)
fpath=O/'INDEPENDENT_R7_FEATURES_REVIEW_ONLY.kicad_pcb';k.SaveBoard(str(fpath),b);fpath.with_suffix('.kicad_pro').write_text(json.dumps({'board':{'design_settings':{'rules':{'min_clearance':.2,'min_solder_mask_width':.1,'min_copper_edge_clearance':.25,'min_silk_clearance':.1}}}},indent=2)+'\n');(O/'fp-lib-table').write_text('(fp_lib_table (lib (name "Audit_Footprints") (type "KiCad") (uri "${KIPRJMOD}/Audit_Footprints.pretty") (options "") (descr "Read-only source copies for independent review fixture")))\n')
loaded=k.LoadBoard(str(fpath));assert loaded.GetCopperLayerCount()==6 and len(list(loaded.GetTracks()))==0 and len(list(loaded.Zones()))==0
for f in loaded.GetFootprints():
 r=f.GetReference();pop.validate_population(elements[r],f)
 for n,pad in numbered(f).items():assert pad.GetNetname()==pn[(r,n)][0]
assert sum(len(numbered(f)) for f in loaded.GetFootprints())==18
(O/'cam').mkdir(exist_ok=True)
run('gerbers',['pcb','export','gerbers','--layers','F.Cu,F.Mask,F.Paste','--output',str(O/'cam'),str(fpath)])
for suffix,label in [('.gtl','copper'),('.gts','mask'),('.gtp','paste')]:
 path=next((O/'cam').glob('*'+suffix));text=path.read_text();logs[label]={'flash_count':len(re.findall(r'D03\*',text)),'line_draw_count':len(re.findall(r'D01\*',text))}
assert logs['copper']['flash_count']==18 and logs['copper']['line_draw_count']==0;assert logs['mask']['flash_count']==18;assert logs['paste']['flash_count']==14
pastetext=next((O/'cam').glob('*.gtp')).read_text();paste_by_ref={}
for ref,chunk in re.findall(r'%TO.C,([^*]+)\*%(.*?)(?=%TD\*%)',pastetext,re.S):paste_by_ref[ref]=paste_by_ref.get(ref,0)+len(re.findall(r'D03\*',chunk))
assert paste_by_ref.get('R528')==2 and all(r not in paste_by_ref for r in features)
for extra,label in [([], 'positions_default'),(['--exclude-dnp'],'positions_exclude_dnp')]:
 dest=O/(label+'.csv');run(label,['pcb','export','pos','--format','csv','--units','mm',*extra,'--output',str(dest),str(fpath)]);rows=list(csv.DictReader(dest.open()));got={x['Ref'] for x in rows};assert got=={'R205','R206','R220','R221','R401','R561'},got;logs[label]['references']=sorted(got)
run('fixture_drc',['pcb','drc','--format','json','--severity-all','-o',str(O/'fixture-drc.json'),str(fpath)])
run('fresh_erc',['sch','erc','--format','json','--severity-all','-o',str(O/'erc.json'),str(T/'r7/cad/recovery-physical-candidate/CMK230_Core_REVIEW.kicad_sch')])
erc=json.loads((O/'erc.json').read_text());assert not [v for s in erc['sheets'] for v in s['violations']]
drc=json.loads((O/'fixture-drc.json').read_text());assert not drc['violations']
after={str(p.relative_to(P)):sha(p) for p in tracked};assert before==after
report={'status':'PASS_WITH_EXPLICIT_QUALIFICATION_LIMITS','kicad':k.GetBuildVersion(),'components':254,'bindings':1509,'nets':len({x[0] for x in pn.values()}),'changed_footprint_references':sorted(field_changes),'changed_BOM_flag_references':sorted(bom_changes),'metadata_changes':rev_changes,'values_preserved':True,'pin_net_function_type_bindings_preserved':True,'on_board_and_DNP_preserved':True,'DNP_references':['JP1','R45','R47','R528'],'assigned_before':sum(bool(x['footprint']) for x in bc.values()),'assigned_after':sum(bool(x['footprint']) for x in pc.values()),'source_copper_geometry_matches':True,'WSL_body_xy_mm':[1.8,1.02],'WSL_courtyard_xy_mm':[3.12,1.62],'WFZ_body_xy_mm':[1.1,.6],'WFZ_courtyard_xy_mm':[2,1.2],'new_features_no_paste_or_copper_short':True,'native_fixture_numbered_pads':18,'native_CAM':{x:logs[x] for x in ['copper','mask','paste']},'paste_apertures_by_reference':paste_by_ref,'R528_DNP_paste_retained':True,'assembly_stencil_variant_gate_open':True,'placement_refs':logs['positions_default']['references'],'negative_controls_rejected':neg,'erc_violations':0,'fixture_drc_violations':0,'fixture_unconnected_items':len(drc['unconnected_items']),'main_CAD_hashes_unchanged':True,'no_full_board_fit_or_routing_qualification':True,'no_hardware_thermal_or_factory_qualification':True}
(O/'independent-review.json').write_text(json.dumps(report,indent=2)+'\n');(O/'native-checks.json').write_text(json.dumps(logs,indent=2)+'\n');(O/'input-sha256.json').write_text(json.dumps({'r6_schematics':{p.name:sha(p) for p in bs.glob('*.kicad_sch')},'r7_schematics':{p.name:sha(p) for p in ps.glob('*.kicad_sch')},'footprint_sources':{r:{'relative_path':str(f.relative_to(P)),'sha256':sha(f)} for r,f in source_files.items()},'population_contract_sha256':sha(P/'tools/population_contract.py')},indent=2)+'\n');print(json.dumps(report,indent=2))
