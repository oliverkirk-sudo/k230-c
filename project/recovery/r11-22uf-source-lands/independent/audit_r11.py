#!/usr/bin/env python3
"""Independent, read-only R11 audit. Requires KiCad CLI and pcbnew (/usr/bin/python3).
Writes only --out and --runtime; native checks use a private copy of --candidate.
"""
import argparse,ast,copy,csv,hashlib,json,math,os,pathlib,re,shutil,subprocess,xml.etree.ElementTree as ET
ap=argparse.ArgumentParser();ap.add_argument('--baseline',type=pathlib.Path,required=True);ap.add_argument('--candidate',type=pathlib.Path,required=True);ap.add_argument('--out',type=pathlib.Path,required=True);ap.add_argument('--runtime',type=pathlib.Path,required=True);a=ap.parse_args()
B=a.baseline.resolve();C=a.candidate.resolve();O=a.out.resolve();R=a.runtime.resolve()
assert B.is_dir() and C.is_dir(), 'Input project directories must exist'
assert all(target!=source and source not in target.parents for target in [O,R] for source in [B,C]), 'Output/runtime must be outside both input projects'
assert O!=R, 'Use separate output and runtime directories'
O.mkdir(parents=True,exist_ok=True);R.mkdir(parents=True,exist_ok=True)
for variable,subdir in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data')]:
 task_directory=R/subdir;task_directory.mkdir(exist_ok=True);os.environ[variable]=str(task_directory)
import pcbnew as pcb
A=pathlib.Path('cad/recovery-physical-candidate');E=pathlib.Path('recovery/r11-22uf-source-lands');LIB='CMK230_Bulk22_Candidates';NAME='Samsung_CL31B226_1206_ReflowMid_SOURCE_CANDIDATE';ID=LIB+':'+NAME;LP=pathlib.Path('cad/recovery-bulk22-candidates')/(LIB+'.pretty');REFS={'C206','C207','C208','C212','C213','C214','C540','C552','C562'}
fail=[];checks=[];negative=[];logs={}
def check(name,condition,detail=None):
 checks.append({'check':name,'pass':bool(condition),'detail':detail})
 if not condition:fail.append(name)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,data): (O/name).write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
def normalize(v):
 if isinstance(v,dict):return {k:normalize(x) for k,x in v.items()}
 if isinstance(v,list):return [normalize(x) for x in v]
 if isinstance(v,str):
  for base,label in [(str(R),'<runtime>'),(str(C),'<candidate>'),(str(B),'<baseline>'),(str(O),'<output>')]:v=v.replace(base,label)
 return v
def xmlcanon(e,drop_fp=False):
 if drop_fp and (e.tag=='footprint' or (e.tag=='field' and e.attrib.get('name')=='Footprint')):return None
 children=[z for c in e if (z:=xmlcanon(c,drop_fp)) is not None]
 return [e.tag,sorted(e.attrib.items()),(e.text or '').strip(),children]
def graph(path):
 root=ET.parse(path).getroot(); comps={e.attrib['ref']:e for e in root.findall('./components/comp')};bindings={}
 for net in root.findall('./nets/net'):
  for node in net.findall('node'):
   key=(node.attrib['ref'],node.attrib['pin']);assert key not in bindings
   bindings[key]={'net':net.attrib['name'],'net_class':net.attrib.get('class'),'node':dict(node.attrib)}
 return root,comps,bindings
br,bc,bn=graph(B/A/'master.xml');cr,cc,cn=graph(C/A/'master.xml')
initial_main={str(p.relative_to(C)):sha(p) for p in (C/A).iterdir() if p.is_file() and (p.suffix in ['.kicad_sch','.kicad_pro','.py','.xml'] or p.name.endswith('lib-table'))};initial_main[str(LP/(NAME+'.kicad_mod'))]=sha(C/LP/(NAME+'.kicad_mod'))
check('254_exact_component_identities',len(bc)==len(cc)==254 and set(bc)==set(cc))
check('all_non_footprint_component_XML_preserved',all(xmlcanon(bc[k],True)==xmlcanon(cc[k],True) for k in bc))
changed={k for k in bc if bc[k].findtext('footprint')!=cc[k].findtext('footprint')};check('exactly_nine_blank_to_named_assignments',changed==REFS and all(not bc[k].findtext('footprint') and cc[k].findtext('footprint')==ID for k in REFS),sorted(changed))
check('1509_full_pin_bindings_preserved',len(bn)==len(cn)==1509 and bn==cn)
check('457_net_names_preserved',len({v['net'] for v in cn.values()})==457 and {v['net'] for v in bn.values()}=={v['net'] for v in cn.values()})
assigned=sum(bool(x.findtext('footprint')) for x in cc.values());check('230_assigned_24_gaps',assigned==230 and len(cc)-assigned==24,{'assigned':assigned,'gaps':len(cc)-assigned})
check('nine_values_preserved',all(cc[k].findtext('value')==bc[k].findtext('value') and cc[k].findtext('value').startswith('22uF') for k in REFS))
for k,net in {**{r:'VDD0P8_CPU' for r in ['C206','C207','C208']},**{r:'VDD0P8_KPU' for r in ['C212','C213','C214']},'C540':'VDD1P1_DDR_IO','C552':'VDD1P1_DDR_IO','C562':'VDD1P8'}.items():check('pin_pair_'+k,cn[(k,'1')]['net']==net and cn[(k,'2')]['net']=='GND')
check('47uF_and_inputs_unmodified',all(xmlcanon(bc[k])==xmlcanon(cc[k]) for k in ['C201','C218','C223','C228','C203','C204','C210','C211','C216','C217','C220','C221','C225','C226','C230','C231']))
# A complete source-schematic token comparison covers dnp/in_bom/on_board, symbol UUIDs,
# library symbols, wiring and properties that a simple electrical net comparison misses.
def sx(text):
 tokens=re.findall(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+',text);stack=[];root=None
 for tok in tokens:
  if tok=='(':
   z=[]
   if stack:stack[-1].append(z)
   stack.append(z)
  elif tok==')':root=stack.pop()
  else:stack[-1].append(json.loads(tok) if tok.startswith('"') else tok)
 assert not stack;return root

def children(node,key):return [x for x in node if isinstance(x,list) and x and x[0]==key]
def child(node,key):return next(x for x in children(node,key))
def prop(node,key):return next(x for x in children(node,'property') if x[1]==key)
def symref(node):
 try:return prop(node,'Reference')[2]
 except StopIteration:return None
schematic_changes=[];source_refs={}
for bf in sorted((B/A).glob('*.kicad_sch')):
 rel=A/bf.name;b=sx(bf.read_text());c=sx((C/rel).read_text());expected=copy.deepcopy(b)
 for n in children(expected,'symbol'):
  ref=symref(n)
  if ref in REFS:
   assert prop(n,'Footprint')[2]=='';prop(n,'Footprint')[2]=ID;source_refs[ref]=bf.name
 if bf.name=='CMK230_Core_REVIEW.kicad_sch':
  rev=child(child(expected,'title_block'),'rev');check('baseline_root_revision_RCV_R9',rev[1]=='RCV-R9');rev[1]='RCV-R11'
 check('schematic_exact_allowed_changes_'+bf.name,expected==c)
 if bf.read_bytes()!=(C/rel).read_bytes():schematic_changes.append(str(rel))
check('all_nine_source_symbols_once',set(source_refs)==REFS and len(source_refs)==9,source_refs)
check('only_three_schematic_files_changed',set(schematic_changes)=={str(A/'CMK230_Core_REVIEW.kicad_sch'),str(A/'10_Six_Rail_Power.kicad_sch'),str(A/'12_Local_Decoupling.kicad_sch')},schematic_changes)
# Ownership: exactly one library declaration, correct project-relative directory and one part.
tab=sx((C/A/'fp-lib-table').read_text());base_tab=sx((B/A/'fp-lib-table').read_text());new_entries=[x for x in children(tab,'lib') if child(x,'name')[1]==LIB]
check('one_library_owner',len(new_entries)==1)
entry=new_entries[0];uri=child(entry,'uri')[1];resolved=(C/A/uri.replace('${KIPRJMOD}/','')).resolve();check('library_uri_resolves_expected',resolved==(C/LP).resolve(),uri)
filtered=copy.deepcopy(tab);filtered.remove(next(x for x in filtered if isinstance(x,list) and x and x[0]=='lib' and child(x,'name')[1]==LIB));check('older_library_owners_unchanged',filtered==base_tab)
check('only_one_new_library_part',[x.name for x in (C/LP).glob('*.kicad_mod')]==[NAME+'.kicad_mod'])
# Generator changed only by root revision, explicit nine-ref FP update and table append.
btxt=(B/A/'build_review.py').read_text();ctxt=(C/A/'build_review.py').read_text();ba=ast.parse(btxt.replace('RCV-R9','RCV-R11'));ca=ast.parse(ctxt);updates=[]
for node in list(ca.body):
 if isinstance(node,ast.Expr) and isinstance(node.value,ast.Call) and isinstance(node.value.func,ast.Attribute) and isinstance(node.value.func.value,ast.Name) and node.value.func.value.id=='FP' and node.value.func.attr=='update':
  d=ast.literal_eval(node.value.args[0])
  if set(d)==REFS:updates.append(d);ca.body.remove(node)
check('generator_nine_ref_update_exact',updates==[{ref:ID for ref in updates[0]}] if updates else False)
check('generator_expected_three_append_statements',len(ca.body)==len(ba.body)+3)
check('generator_existing_AST_preserved',ast.dump(ast.Module(body=ca.body[:-3],type_ignores=[]),include_attributes=False)==ast.dump(ba,include_attributes=False))
check('generator_appended_table_entry',LIB in ast.unparse(ast.Module(body=ca.body[-3:],type_ignores=[])) and uri in ast.unparse(ast.Module(body=ca.body[-3:],type_ignores=[])))
# Exact source file and drawing authority, separate from engineering process settings.
source=C/E/'source-review';manifest=json.loads((source/'artifact-sha256.json').read_text());missing=[n for n in manifest if not(source/n).is_file()];bad=[n for n,h in manifest.items() if (source/n).is_file() and sha(source/n)!=h];check('copied_source_manifest_resolves',not missing and not bad,{'missing':missing,'hash_mismatch':bad})
geom=json.loads((source/'geometry-review.json').read_text());part=next(x for x in geom['parts'] if x['mpn']=='CL31B226KPHNNNE');check('source_22uF_land_authority',part['manufacturer_reflow_status']=='APPLICABLE_3216_PLUS_MINUS_0P20_ROW' and part['manufacturer_reflow_source_page']==33 and part['body_max_LWT_mm']==[3.4,1.8,1.8]);check('47uF_proposal_unselected',geom['engineering_derived_47uF_proposal']['selected'] is False)
fp=sx((C/LP/(NAME+'.kicad_mod')).read_text())
def pad_data(tree):
 z=[]
 for n in children(tree,'pad'):
  z.append({'number':n[1],'type':n[2],'shape':n[3],'at':[float(v) for v in child(n,'at')[1:3]],'size':[float(v) for v in child(n,'size')[1:3]],'layers':child(n,'layers')[1:],'mask_margin':float(child(n,'solder_mask_margin')[1]) if children(n,'solder_mask_margin') else 0})
 return z
pads=pad_data(fp);cu=[p for p in pads if 'F.Cu' in p['layers']];paste=[p for p in pads if 'F.Paste' in p['layers']];check('exact_two_copper_pads',sorted(cu,key=lambda p:p['number'])==[{'number':str(i),'type':'smd','shape':'rect','at':[x,0.0],'size':[1.25,1.8],'layers':['F.Cu','F.Mask'],'mask_margin':.05} for i,x in [(1,-1.475),(2,1.475)]]);check('separate_unnumbered_1to1_paste',sorted(paste,key=lambda p:p['at'])==[{'number':'','type':'smd','shape':'rect','at':[x,0.0],'size':[1.25,1.8],'layers':['F.Paste'],'mask_margin':0} for x in [-1.475,1.475]] and len(pads)==4)
def rect_data(tree,layer):
 n=next(n for n in children(tree,'fp_rect') if child(n,'layer')[1]==layer);return {'start':[float(v) for v in child(n,'start')[1:3]],'end':[float(v) for v in child(n,'end')[1:3]],'stroke':float(child(child(n,'stroke'),'width')[1])}
body=rect_data(fp,'F.Fab');court=rect_data(fp,'F.CrtYd');check('max_body_centerline_dimensions',body=={'start':[-1.7,-.9],'end':[1.7,.9],'stroke':.05});check('courtyard_centerline_dimensions',court=={'start':[-2.425,-1.225],'end':[2.425,1.225],'stroke':.05})
def clearance(tree):
 q=pad_data(tree);c=rect_data(tree,'F.CrtYd');inn=[c['start'][0]+c['stroke']/2,c['start'][1]+c['stroke']/2,c['end'][0]-c['stroke']/2,c['end'][1]-c['stroke']/2];m=[p for p in q if 'F.Mask' in p['layers']];box=[min(p['at'][0]-p['size'][0]/2-p['mask_margin'] for p in m),min(p['at'][1]-p['size'][1]/2-p['mask_margin'] for p in m),max(p['at'][0]+p['size'][0]/2+p['mask_margin'] for p in m),max(p['at'][1]+p['size'][1]/2+p['mask_margin'] for p in m)];return [round(box[0]-inn[0],8),round(box[1]-inn[1],8),round(inn[2]-box[2],8),round(inn[3]-box[3],8)]
clear=clearance(fp);check('actual_mask_to_courtyard_inner_edge_0p25',clear==[.25]*4,clear)
check('conditional_process_description',all(s in child(fp,'descr')[1].lower() for s in ['mask','paste','courtyard','unqualified']))
# Mutations in memory exercise the exact graph and actual edge-clearance checks.
for name,ref,newnet in [('CPU_to_KPU','C206','VDD0P8_KPU'),('KPU_to_CPU','C212','VDD0P8_CPU'),('DDR_to_1V8','C540','VDD1P8'),('1V8_to_DDR','C562','VDD1P1_DDR_IO')]:
 g=copy.deepcopy(cn);g[(ref,'1')]['net']=newnet;changedpins=[list(k) for k in g if g[k]!=bn[k]];negative.append({'name':name,'detected':changedpins==[[ref,'1']],'witness':changedpins})
mut=copy.deepcopy(fp);n=next(n for n in children(mut,'fp_rect') if child(n,'layer')[1]=='F.CrtYd');child(n,'start')[1:]=['-2.375','-1.175'];child(n,'end')[1:]=['2.375','1.175'];mc=clearance(mut);negative.append({'name':'courtyard_inner_edge_clearance_reduced','detected':min(mc)<.25,'actual_clearances_mm':mc,'required_mm':.25})
# Isolated native checking. The original project is never exported or regenerated.
work=R/'candidate-copy';shutil.copytree(C,work,dirs_exist_ok=True);env=os.environ.copy()
for k,n in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data')]:d=R/n;d.mkdir(exist_ok=True);env[k]=str(d)
def run(label,args):
 rr=subprocess.run(['kicad-cli',*map(str,args)],env=env,cwd=work,capture_output=True,text=True,timeout=90);logs[label]=normalize({'returncode':rr.returncode,'stdout':rr.stdout,'stderr':rr.stderr});return rr.returncode
sch=work/A/'CMK230_Core_REVIEW.kicad_sch';fresh=R/'fresh-master.xml';rc=run('fresh_netlist',['sch','export','netlist','--format','kicadxml','-o',fresh,sch]);check('native_netlist_exit0',rc==0)
fr,fc,fn=graph(fresh);check('fresh_export_254_identities_saved_master_match',set(fc)==set(cc) and all(xmlcanon(fc[k])==xmlcanon(cc[k]) for k in cc));check('fresh_export_1509_bindings_saved_master_match',fn==cn)
erc=R/'fresh-erc.json';rc=run('fresh_erc',['sch','erc','--format','json','--severity-all','--exit-code-violations','-o',erc,sch]);er=json.loads(erc.read_text());ev=[v for s in er['sheets'] for v in s['violations']];check('fresh_ERC_zero',rc==0 and not ev,{'exit_code':rc,'violations':len(ev)});save('fresh-erc.json',normalize(er))
fixture=work/E/'BULK22_LANDS_GEOMETRY_ONLY.kicad_pcb';board=pcb.LoadBoard(str(fixture));fps=list(board.GetFootprints());check('saved_fixture_one_footprint',len(fps)==1);bf=fps[0];check('saved_fixture_identity_owner',bf.GetFPID().GetLibNickname()==LIB and bf.GetFPID().GetLibItemName()==NAME)
# Check the embedded saved-footprint geometry, not only the library file.
fixture_sx=sx(fixture.read_text());embedded=child(fixture_sx,'footprint');check('saved_fixture_pad_geometry_matches_library',pad_data(embedded)==pads or sorted(pad_data(embedded),key=lambda p:(p['number'],p['at']))==sorted(pads,key=lambda p:(p['number'],p['at'])));check('saved_fixture_actual_courtyard_clearance',clearance(embedded)==[.25]*4)
drc=R/'fresh-drc.json';rc=run('fresh_geometry_drc',['pcb','drc','--format','json','--severity-all','--exit-code-violations','-o',drc,fixture]);dr=json.loads(drc.read_text());check('fresh_geometry_DRC_zero',rc==0 and not dr['violations'] and not dr['unconnected_items'],{'exit_code':rc,'violations':len(dr['violations']),'unconnected':len(dr['unconnected_items'])});save('fresh-geometry-drc.json',normalize(dr))
cam=R/'fresh-cam';cam.mkdir(exist_ok=True);rc=run('fresh_cam',['pcb','export','gerbers','--layers','F.Cu,F.Mask,F.Paste','--output',cam,fixture]);check('fresh_CAM_exit0',rc==0)
def normcam(text):return '\n'.join(line for line in text.splitlines() if not line.startswith('%TF.CreationDate,') and not line.startswith('G04 Created by KiCad'))
def camdata(text):
 apos={};flashes=[];active=None
 for line in text.splitlines():
  m=re.match(r'%ADD(\d+)(R|RoundRect),([^*]+)\*%',line)
  if m:
   vals=[float(v) for v in m[3].split('X')]
   if m[2]=='R':size=vals[:2]
   else:radius=vals[0];xs=vals[1:9:2];ys=vals[2:9:2];size=[max(xs)-min(xs)+2*radius,max(ys)-min(ys)+2*radius]
   apos[m[1]]={'shape':m[2],'bounds_xy_mm':[round(x,7) for x in size]}
  m=re.fullmatch(r'D(\d+)\*',line)
  if m:active=m[1]
  m=re.fullmatch(r'X(-?\d+)Y(-?\d+)D03\*',line)
  if m:flashes.append({'position_mm':[int(m[1])/1e6,int(m[2])/1e6],'aperture':apos[active]})
 return {'apertures':apos,'flashes':flashes}
camresults={}
for suffix,layer,expected in [('gtl','Cu',[1.25,1.8]),('gts','Mask',[1.35,1.9]),('gtp','Paste',[1.25,1.8])]:
 name='BULK22_LANDS_GEOMETRY_ONLY-F_'+layer+'.'+suffix;old=(C/E/'native-cam'/name).read_text();new=(cam/name).read_text();data=camdata(old);camresults[layer]=data
 check('saved_vs_fresh_CAM_'+layer,normcam(old)==normcam(new))
 check('CAM_two_expected_flashes_'+layer,len(data['flashes'])==2 and all(z['aperture']['bounds_xy_mm']==expected for z in data['flashes']) and sorted(z['position_mm'] for z in data['flashes'])==[[6.525,-6.0],[9.475,-6.0]],data)
# A real native copper clearance violation, on an isolated copied board.
badboard=pcb.LoadBoard(str(fixture));badfp=list(badboard.GetFootprints())[0];p1=next(x for x in badfp.Pads() if x.GetNumber()=='1');p2=next(x for x in badfp.Pads() if x.GetNumber()=='2');pos=p1.GetPosition();p2.SetPosition(pcb.VECTOR2I(pos.x+pcb.FromMM(1.30),pos.y));badfile=R/'bad-clearance.kicad_pcb';pcb.SaveBoard(str(badfile),badboard);shutil.copyfile(fixture.with_suffix('.kicad_pro'),badfile.with_suffix('.kicad_pro'));badreport=R/'bad-clearance-drc.json';rc=run('negative_native_copper_clearance',['pcb','drc','--format','json','--severity-all','--exit-code-violations','-o',badreport,badfile]);bad=json.loads(badreport.read_text());types=[x['type'] for x in bad['violations']];negative.append({'name':'native_copper_gap_0p05_vs_rule_0p20','detected':rc!=0 and any('clearance' in x for x in types),'actual_copper_gap_mm':.05,'rule_minimum_mm':.2,'native_exit_code':rc,'violation_types':types});save('negative-native-clearance.json',normalize(bad))
check('all_negative_controls_detected',all(x['detected'] for x in negative),negative)
final_main={rel:sha(C/rel) for rel in initial_main};check('source_CAD_unchanged_during_audit',final_main==initial_main)
# Tree diff records the scope without redistributing any vendor originals.
def files(root):return {str(f.relative_to(root)):sha(f) for f in root.rglob('*') if f.is_file()}
old=files(B);new=files(C);diff={'changed':sorted(k for k in old.keys()&new.keys() if old[k]!=new[k]),'added':sorted(new.keys()-old.keys()),'removed':sorted(old.keys()-new.keys())};check('no_files_removed',not diff['removed'])
allowed_changed={str(A/n) for n in ['12_Local_Decoupling.kicad_sch','master.xml','build_review.py','erc.json','10_Six_Rail_Power.kicad_sch','fp-lib-table','CMK230_Core_REVIEW.kicad_sch','README.md']};check('only_expected_existing_files_changed',set(diff['changed'])<=allowed_changed,diff['changed']);check('new_files_scoped',all(k.startswith(str(E)+'/') or k==str(LP/(NAME+'.kicad_mod')) for k in diff['added']))
bd=(B/A/'README.md').read_text();cd=(C/A/'README.md').read_text();check('active_README_append_only_bounded_R11_status',cd.startswith(bd) and 'R11 assigns nine Samsung22µF' in cd[len(bd):] and '230 assigned/24 gaps' in cd[len(bd):] and 'input-bank options remain unselected' in cd[len(bd):])
save('checks.json',checks);save('negative-controls.json',negative);save('cam-audit.json',camresults);save('source-tree-diff.json',diff);save('native-command-results.json',logs);save('input-hashes.json',{'baseline_master':sha(B/A/'master.xml'),'candidate_master':sha(C/A/'master.xml'),'candidate_relevant_CAD':initial_main,'source_specsheet_sha256':'742b9759b46abf22af1f61562aac31870345cf654ca240911f98fda44cf58167'})
summary={'status':'PASS_BOUNDED_GEOMETRY_REVIEW' if not fail else 'FAIL','failed_checks':fail,'checks':len(checks),'component_identities':len(cc),'pin_bindings':len(cn),'footprint_assignment_changes':sorted(changed),'assigned':assigned,'unassigned':len(cc)-assigned,'fresh_ERC_violations':len(ev),'fresh_fixture_DRC_violations':len(dr['violations']),'actual_mask_to_courtyard_inner_edge_mm':clear,'negative_controls':len(negative),'limits':['Footprint-only evidence checkpoint; no full-core placement or routed board validation.','Mask, paste and courtyard choices remain conditional process assumptions.','Body/land provenance is not Ceff, PDN, assembly or production qualification.','Source rail-budget intervals remain historical screening inputs, not aggregate limits for all filtered branches.','47uF proposal remains unselected and regulator-input option unapplied.','Isolated fixture nets are diagnostic; fixture copper-layer count does not approve a production stack.'],'source_CAD_unchanged':final_main==initial_main};save('summary.json',summary);print(json.dumps(summary,indent=2));raise SystemExit(1 if fail else 0)
