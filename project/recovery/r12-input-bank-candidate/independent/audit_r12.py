#!/usr/bin/env python3
"""Independent R12 audit. Read-only source trees; all native writes use --runtime.
Requires Python 3, kicad-cli, and a Python installation with pcbnew.
No implementation validator is imported or executed.
"""
from pathlib import Path
import argparse,ast,copy,csv,hashlib,json,math,os,re,shutil,subprocess,sys,xml.etree.ElementTree as ET
KEEP={'C203','C210','C211','C216','C217','C220','C225','C230'}
DROP={'C204','C221','C226','C231'}
BYPASS={'C205','C209','C215','C222','C227','C232'}
VALUE='22uF CL31B226KPHNNNE INPUT BANK CANDIDATE'
FP='CMK230_Bulk22_Candidates:Samsung_CL31B226_1206_ReflowMid_SOURCE_CANDIDATE'
REL='cad/recovery-inputbank-candidate'; BASEREL='cad/recovery-physical-candidate'
class AuditFailure(Exception):pass
def need(test,message):
 if not test:raise AuditFailure(message)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(obj):return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def inventory(p):return {f.relative_to(p).as_posix():sha(f) for f in sorted(p.rglob('*')) if f.is_file()}
def xtree(e):return [e.tag,dict(sorted(e.attrib.items())),(e.text or '').strip(),[xtree(x) for x in e]]
def xmlstate(path):
 r=ET.parse(path).getroot();parts={};nodes={};nets={}
 for c in r.findall('./components/comp'):
  ref=c.get('ref');need(ref not in parts,'duplicate component '+ref)
  parts[ref]={'attributes':dict(c.attrib),'value':c.findtext('value'),'footprint':c.findtext('footprint') or '', 'fields':sorted((x.get('name'),x.text or '',dict(x.attrib)) for x in c.findall('./fields/field')),'libsource':dict(c.find('libsource').attrib),'properties':sorted([dict(x.attrib) for x in c.findall('property')],key=lambda x:json.dumps(x,sort_keys=True)),'sheetpath':{k:v for k,v in c.find('sheetpath').attrib.items() if k!='tstamps'},'other_children':[xtree(x) for x in c if x.tag not in {'value','footprint','fields','libsource','property','sheetpath','tstamps'}]}
 for n in r.findall('./nets/net'):
  name=n.get('name');need(name not in nets,'duplicate named net '+name);nets[name]={k:v for k,v in n.attrib.items() if k!='code'}
  for x in n.findall('node'):
   key=x.get('ref')+'.'+x.get('pin');need(key not in nodes,'duplicate numbered pin binding '+key);nodes[key]={'net':name,'node_attributes':dict(sorted(x.attrib.items()))}
 return {'parts':parts,'nodes':nodes,'nets':nets,'libparts':xtree(r.find('libparts'))}
def expected_state(b):
 e=copy.deepcopy(b)
 for ref in KEEP:
  need(e['parts'][ref]['value']=='10uF 10V X7R' and not e['parts'][ref]['footprint'],'predecessor cap mismatch '+ref)
  e['parts'][ref]['value']=VALUE;e['parts'][ref]['footprint']=FP
  e['parts'][ref]['fields']=[(k,FP if k=='Footprint' else v,a) for k,v,a in e['parts'][ref]['fields']]
 for ref in DROP:del e['parts'][ref]
 e['nodes']={k:v for k,v in e['nodes'].items() if k.rsplit('.',1)[0] not in DROP}
 return e
def check_state(got,want):
 for key in ['parts','nodes','nets','libparts']:
  if got[key]!=want[key]:
   if isinstance(got[key],dict):changed=sorted(k for k in set(got[key])|set(want[key]) if got[key].get(k)!=want[key].get(k));raise AuditFailure(key+' mismatch: '+','.join(changed[:16]))
   raise AuditFailure(key+' mismatch')
def sexpr(text):
 tokens=re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()]+',text);stack=[];roots=[]
 for t in tokens:
  if t=='(':
   a=[]
   if stack:stack[-1].append(a)
   else:roots.append(a)
   stack.append(a)
  elif t==')':need(bool(stack),'unbalanced S-expression');stack.pop()
  else:
   need(bool(stack),'atom outside S-expression');stack[-1].append(json.loads(t) if t.startswith('"') else t)
 need(not stack and len(roots)==1,'invalid S-expression root');return roots[0]
def children(a,name):return [x for x in a if isinstance(x,list) and x and x[0]==name]
def child(a,name):
 x=children(a,name);return x[0] if x else None
def atom(a,name,default=None):
 x=child(a,name);return x[1] if x and len(x)>1 else default
def prop(a,name):return next((x[2] for x in children(a,'property') if x[1]==name),None)
def clean_native(a):
 if not isinstance(a,list):return a
 return [clean_native(x) for x in a if not(isinstance(x,list) and x and x[0] in {'uuid','instances'})]
def native_states(folder):
 result={};no_connect={};declaration=None
 for f in sorted(folder.glob('*.kicad_sch')):
  a=sexpr(f.read_text());no_connect[f.name]=sorted(json.dumps(clean_native(x),sort_keys=True) for x in children(a,'no_connect'))
  for x in children(a,'symbol'):
   if not child(x,'lib_id'):continue
   ref=prop(x,'Reference');key=ref+'|'+str(atom(x,'unit'))
   need(key not in result,'duplicate native instance '+key);result[key]={'file':f.name,'data':clean_native(x)}
  if f.name=='17_Audited_Source_Declarations.kicad_sch':
   z=clean_native(a)
   for block in children(z,'title_block'):
    block[:]=[x for x in block if not(isinstance(x,list) and x and x[0]=='rev')]
   declaration=z
 return {'instances':result,'no_connect':no_connect,'declaration_sheet':declaration}
def expected_native(b):
 e=copy.deepcopy(b)
 for key in list(e['instances']):
  ref=key.rsplit('|',1)[0]
  if ref in DROP:del e['instances'][key]
  elif ref in KEEP:
   for p in children(e['instances'][key]['data'],'property'):
    if p[1]=='Value':p[2]=VALUE
    if p[1]=='Footprint':p[2]=FP
 return e
def check_native(got,want):
 for key in ['instances','no_connect','declaration_sheet']:need(got[key]==want[key],'native '+key+' mismatch')
def footprint_state(path):
 a=sexpr(path.read_text());pads=[]
 for p in children(a,'pad'):
  pads.append({'number':p[1],'type':p[2],'shape':p[3],'at':list(map(float,child(p,'at')[1:])),'size':list(map(float,child(p,'size')[1:])),'layers':child(p,'layers')[1:],'mask_margin':float(atom(p,'solder_mask_margin')) if child(p,'solder_mask_margin') else None})
 rects=[{'start':list(map(float,child(x,'start')[1:])),'end':list(map(float,child(x,'end')[1:])),'stroke':float(atom(child(x,'stroke'),'width'))} for x in children(a,'fp_rect') if atom(x,'layer')=='F.CrtYd']
 return {'pads':pads,'courtyards':rects}
def check_footprint(g):
 expected=[]
 for number,x in [('1',-1.475),('2',1.475)]:
  expected.append({'number':number,'type':'smd','shape':'rect','at':[x,0.0],'size':[1.25,1.8],'layers':['F.Cu','F.Mask'],'mask_margin':.05})
  expected.append({'number':'','type':'smd','shape':'rect','at':[x,0.0],'size':[1.25,1.8],'layers':['F.Paste'],'mask_margin':None})
 need(g['pads']==expected,'footprint copper, pin identity, mask or paste mismatch')
 need(g['courtyards']==[{'start':[-2.425,-1.225],'end':[2.425,1.225],'stroke':.05}],'footprint courtyard mismatch')
def library_files(folder):
 a=sexpr((folder/'fp-lib-table').read_text());out={}
 for l in children(a,'lib'):
  name=atom(l,'name');uri=atom(l,'uri');need(name not in out,'duplicate footprint library '+name);need('${KIPRJMOD}' in uri,'nonportable footprint-library URI');out[name]=(folder/uri.replace('${KIPRJMOD}/','')).resolve()
 return out
def csvstate(path):return sorted(list(csv.DictReader(path.open())),key=lambda x:(x['reference'],x['unit'],x['pin']))
def save(path,o):path.write_text(json.dumps(o,indent=2,ensure_ascii=False)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--project',type=Path,required=True);ap.add_argument('--predecessor',type=Path,required=True);ap.add_argument('--review-baseline',type=Path,required=True,help='Published R10 project used by the source review');ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--kicad-cli',default='kicad-cli');ap.add_argument('--pcbnew-python',default='/usr/bin/python3');a=ap.parse_args()
 P=a.project.resolve();B=a.predecessor.resolve();RB=a.review_baseline.resolve();T=a.runtime.resolve();O=a.out.resolve();need(P.is_dir() and B.is_dir() and RB.is_dir(),'source project missing');need(not T.exists(),'runtime must be a new directory');need(T!=P and T!=B and P not in T.parents and B not in T.parents,'runtime must be outside source projects');T.mkdir(parents=True);O.mkdir(parents=True,exist_ok=True)
 source_before=inventory(P);old_before=inventory(B);missing=[k for k,h in old_before.items() if source_before.get(k)!=h];need(not missing,'Published predecessor files changed or missing: '+','.join(missing[:12]))
 logs={};env=os.environ.copy()
 for key,name in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data')]:x=T/name;x.mkdir();env[key]=str(x)
 env['PYTHONDONTWRITEBYTECODE']='1'
 def normal(s):
  for path,label in [(T,'<runtime>'),(P,'<project>'),(B,'<predecessor>')]:s=s.replace(str(path),label)
  return s
 def run(label,argv,timeout=120):
  r=subprocess.run(argv,env=env,capture_output=True,text=True,timeout=timeout);logs[label]={'command':[normal(str(x)) for x in argv],'returncode':r.returncode,'stdout':normal(r.stdout),'stderr':normal(r.stderr)};need(r.returncode==0,'Native command failed '+label+': '+normal(r.stderr)[-500:]);return r.stdout
 W=T/'project';shutil.copytree(P,W);C=W/REL;BC=W/BASEREL;orig=P/REL
 def export(label,folder,name):
  out=T/name;run(label,[a.kicad_cli,'sch','export','netlist','--format','kicadxml','-o',str(out),str(folder/'CMK230_Core_REVIEW.kicad_sch')]);return out
 baseline=xmlstate(B/BASEREL/'master.xml');review_baseline=xmlstate(RB/BASEREL/'master.xml');bridge=json.loads((P/'recovery/r12-input-bank-candidate/r10-r11-source-scope-bridge.json').read_text());bridge_refs=set(bridge['scoped_refs']);need(bridge_refs==KEEP|DROP|BYPASS|{f'U{i}' for i in range(21,27)}|{'R201','R202','R205','R206','R207','R208','R210','R211','R213','R214'},'source scope bridge membership');need(sha(RB/BASEREL/'master.xml')==bridge['old_master_sha256'] and sha(B/BASEREL/'master.xml')==bridge['new_master_sha256'],'source bridge full-file hashes');need(all(review_baseline['parts'][r]==baseline['parts'][r] for r in bridge_refs),'R10-R11 source scope component mismatch');need({k:v for k,v in review_baseline['nodes'].items() if k.rsplit('.',1)[0] in bridge_refs}=={k:v for k,v in baseline['nodes'].items() if k.rsplit('.',1)[0] in bridge_refs},'R10-R11 source scope pin metadata mismatch');want=expected_state(baseline);check_state(xmlstate(orig/'master.xml'),want)
 fresh_base=export('baseline_fresh_export',BC,'baseline-fresh.xml');check_state(xmlstate(fresh_base),baseline)
 fresh=export('candidate_fresh_export',C,'candidate-fresh.xml');got=xmlstate(fresh);check_state(got,want)
 bn=native_states(B/BASEREL);wn=expected_native(bn);gn=native_states(C);check_native(gn,wn)
 need(len(got['parts'])==250 and len(got['nodes'])==1501 and len(got['nets'])==457,'candidate counts inconsistent')
 need(sum(bool(v['footprint']) for v in got['parts'].values())==238,'assigned footprint count inconsistent')
 gaps=sorted(k for k,v in got['parts'].items() if not v['footprint']);need(len(gaps)==12,'unassigned footprint count inconsistent')
 for ref in KEEP|BYPASS:need(got['nodes'][ref+'.1']['net']=='VIN_5V' and got['nodes'][ref+'.2']['net']=='GND','input bank net mismatch '+ref)
 for ref in BYPASS:need(got['parts'][ref]==baseline['parts'][ref] and got['parts'][ref]['value'].startswith('100nF'),'bypass changed '+ref)
 dnp=sorted(r for r,v in got['parts'].items() if any(p.get('name')=='dnp' for p in v['properties']));need(dnp==['JP1','R45','R47','R528'],'DNP protection changed')
 declarations={k:v for k,v in gn['instances'].items() if k.startswith('#PS')};need(len(declarations)==26,'source declaration count')
 for key,v in declarations.items():
  z=v['data'];need(atom(z,'in_bom')=='no' and atom(z,'on_board')=='no' and prop(z,'Footprint')=='','source declaration became hardware '+key)
 need(not any(r.startswith('#') for r in got['parts']),'source declarations exported as physical components')
 for ref in ['J1','JP1','TP81','TP82']:
  z=gn['instances'][ref+'|1']['data'];need(atom(z,'in_bom')=='no' and atom(z,'on_board')=='yes','fabricated feature population mismatch '+ref)
 csvwant=[v for v in csvstate(B/BASEREL/'master-pin-assignments.csv') if v['reference'] not in DROP];need(csvstate(C/'master-pin-assignments.csv')==csvwant,'pin assignment CSV mismatch')
 for sidecar in ['power-source-paths.json','memory-types.json']:
  need((orig/sidecar).read_bytes()==(B/BASEREL/sidecar).read_bytes(),'protected sidecar mismatch '+sidecar)
 bp=json.loads((orig/'bypass-candidate-assignments.json').read_text());oldbp=json.loads((B/BASEREL/'bypass-candidate-assignments.json').read_text());need(bp['components']==oldbp['components'],'generic bypass assignment changes')
 libs=library_files(C);unique_fps=sorted(set(v['footprint'] for v in got['parts'].values() if v['footprint']))
 for identity in unique_fps:
  lib,name=identity.split(':',1);need(lib in libs and (libs[lib]/(name+'.kicad_mod')).is_file(),'footprint unresolved '+identity)
 lib,name=FP.split(':',1);fpfile=libs[lib]/(name+'.kicad_mod');fpg=footprint_state(fpfile);check_footprint(fpg)
 need(sha(fpfile)==sha(B/'cad/recovery-bulk22-candidates/CMK230_Bulk22_Candidates.pretty'/fpfile.name),'source footprint changed from R11')
 need((C/'Integrated.kicad_sym').read_bytes()==(B/BASEREL/'Integrated.kicad_sym').read_bytes(),'standalone symbol library changed')
 native_code='''import pcbnew,json,sys
fp=pcbnew.FootprintLoad(sys.argv[1],sys.argv[2])
assert fp
pads=[]
for p in fp.Pads():
 pads.append({'number':p.GetNumber(),'xy_mm':[pcbnew.ToMM(p.GetPosition().x),pcbnew.ToMM(p.GetPosition().y)],'size_mm':[pcbnew.ToMM(p.GetSize().x),pcbnew.ToMM(p.GetSize().y)],'layers':list(p.GetLayerSet().Seq()),'mask_margin_mm':None if p.GetLocalSolderMaskMargin() is None else pcbnew.ToMM(p.GetLocalSolderMaskMargin())})
assert len(pads)==4
assert len([p for p in pads if pcbnew.F_Cu in p['layers']])==2
assert all(p['number'] in ['1','2'] for p in pads if pcbnew.F_Cu in p['layers'])
assert all(p['layers']==[pcbnew.F_Paste] for p in pads if not p['number'])
print(json.dumps({'kicad_version':pcbnew.GetBuildVersion(),'pads':pads}))'''
 native_fp=json.loads(run('native_footprint_load',[a.pcbnew_python,'-c',native_code,str(libs[lib]),name]))
 erc=T/'candidate-erc.json';run('candidate_erc',[a.kicad_cli,'sch','erc','--format','json','--severity-all','-o',str(erc),str(C/'CMK230_Core_REVIEW.kicad_sch')]);ercj=json.loads(erc.read_text());violations=[v for s in ercj['sheets'] for v in s['violations']];need(not violations,'ERC violations present')
 # Prove the candidate generator reconstructs the exact expected scope independently.
 run('generator',[sys.executable,str(C/'build_review.py')]);regen=export('regenerated_export',C,'regenerated.xml');check_state(xmlstate(regen),want);check_native(native_states(C),wn);need(csvstate(C/'master-pin-assignments.csv')==csvwant,'generator CSV mismatch')
 need((C/'Integrated.kicad_sym').read_bytes()==(B/BASEREL/'Integrated.kicad_sym').read_bytes(),'generator symbol library mismatch')
 regen_erc=T/'regenerated-erc.json';run('regenerated_erc',[a.kicad_cli,'sch','erc','--format','json','--severity-all','-o',str(regen_erc),str(C/'CMK230_Core_REVIEW.kicad_sch')]);need(not [v for s in json.loads(regen_erc.read_text())['sheets'] for v in s['violations']],'regenerated ERC violations')
 controls=[]
 def reject(label,fn):
  try:fn()
  except AuditFailure as e:controls.append({'control':label,'rejected':True,'reason':str(e)})
  else:raise AuditFailure('Negative control escaped: '+label)
 x=copy.deepcopy(got);x['parts']['C204']=copy.deepcopy(baseline['parts']['C204']);reject('removed_reference_reintroduced',lambda:check_state(x,want))
 x=copy.deepcopy(got);del x['parts']['C205'];reject('mandatory100nF_bypass_missing',lambda:check_state(x,want))
 x=copy.deepcopy(got);x['parts']['C210']['value']='10uF 10V X7R';reject('wrong_input_nominal_value',lambda:check_state(x,want))
 x=copy.deepcopy(got);x['parts']['C203']['footprint']='wrong:part';reject('wrong_input_footprint_identity',lambda:check_state(x,want))
 x=copy.deepcopy(got);x['nodes']['C220.1']['net']='VDD1P1_DDR_IO';reject('input_capacitor_on_output_net',lambda:check_state(x,want))
 x=copy.deepcopy(got);x['nodes']['U22.D1']['node_attributes']['pintype']='input';reject('regulator_pin_electrical_type_changed',lambda:check_state(x,want))
 x=copy.deepcopy(got)
 def mutate_pin_name(tree):
  if tree[0]=='pin' and tree[1].get('name')=='VIN':tree[1]['name']='VIN_WRONG';return True
  return any(mutate_pin_name(c) for c in tree[3])
 need(mutate_pin_name(x['libparts']),'symbol pin mutation precondition');reject('symbol_pin_function_name_changed',lambda:check_state(x,want))
 x=copy.deepcopy(gn);child(x['instances']['R528|1']['data'],'dnp')[1]='no';reject('storage_qualification_DNP_removed',lambda:check_native(x,wn))
 x=copy.deepcopy(gn);child(x['instances']['J1|1']['data'],'in_bom')[1]='yes';reject('fabricated_edge_added_to_BOM',lambda:check_native(x,wn))
 x=copy.deepcopy(gn);child(x['instances']['#PS001|1']['data'],'on_board')[1]='yes';reject('declaration_became_hardware',lambda:check_native(x,wn))
 x=copy.deepcopy(fpg);x['pads'][0]['at'][0]+=.1;reject('incorrect_source_pad_pitch',lambda:check_footprint(x))
 x=copy.deepcopy(fpg);x['pads'][1]['layers']=['F.Cu'];reject('anonymous_paste_became_copper',lambda:check_footprint(x))
 x=copy.deepcopy(fpg);x['pads'][0]['mask_margin']=.1;reject('unreviewed_mask_expansion',lambda:check_footprint(x))
 # Native-file negative: keep all counts plausible but move only C203 input to output.
 power=C/'10_Six_Rail_Power.kicad_sch';clean=power.read_text();lines=clean.splitlines(keepends=True);i=next(i for i,s in enumerate(lines) if s.startswith('(symbol (lib_id') and '(property "Reference" "C203"' in s);j=next(j for j in range(i+1,len(lines)) if lines[j].startswith('(global_label "VIN_5V"'));lines[j]=lines[j].replace('(global_label "VIN_5V"','(global_label "VDD0P8_CORE"',1);power.write_text(''.join(lines));bad=export('negative_native_input_net_export',C,'negative-input-net.xml');reject('native_schematic_wrong_input_net',lambda:check_state(xmlstate(bad),want));power.write_text(clean)
 # Native-file negative: defeat storage qualification while leaving graph topology intact.
 interlock=C/'15_Hardware_Reset_Interlock.kicad_sch';clean=interlock.read_text();lines=clean.splitlines(keepends=True);i=next(i for i,s in enumerate(lines) if s.startswith('(symbol (lib_id') and '(property "Reference" "R528"' in s);need('(dnp yes)' in lines[i],'R528 mutation precondition');lines[i]=lines[i].replace('(dnp yes)','(dnp no)',1);interlock.write_text(''.join(lines));bad=export('negative_native_population_export',C,'negative-population.xml');reject('native_schematic_R528_populated',lambda:check_state(xmlstate(bad),want));interlock.write_text(clean)
 # Regeneration negative: accidentally omit one survivor from the implementation selector.
 script=C/'build_review.py';clean=script.read_text();m=re.search(r'^INPUT_CAP_SURVIVORS=(\[.*\])$',clean,re.M);need(bool(m),'generator selector missing');selector=ast.literal_eval(m.group(1));need('C230' in selector,'generator selector precondition');selector.remove('C230');script.write_text(clean[:m.start(1)]+repr(selector)+clean[m.end(1):]);run('negative_generator_missing_survivor',[sys.executable,str(script)]);bad=export('negative_generator_export',C,'negative-generator.xml');reject('generator_omitted_survivor',lambda:check_state(xmlstate(bad),want));script.write_text(clean)
 need(inventory(B)==old_before,'predecessor changed during audit');need(inventory(P)==source_before,'source project changed during audit')
 docs=['cad/recovery-inputbank-candidate/README.md','recovery/r12-input-bank-candidate/README.md'];doc_hashes={x:sha(P/x) for x in docs}
 actual=json.loads((P/'recovery/r12-input-bank-candidate/actual-footprint-area.json').read_text());court=fpg['courtyards'][0];L=court['end'][0]-court['start'][0];Wc=court['end'][1]-court['start'][1];need(abs(L*Wc*8-actual['total_courtyard_rectangle_area_mm2'])<1e-8,'actual courtyard report inconsistent')
 need(actual['matched_source_scenario_added_area_mm2']==[34.4,36.08],'matched-area report inconsistent')
 result={'status':'PASS_BOUNDED_INDEPENDENT_AUDIT','predecessor_revision':'R11','candidate_revision':'RCV-INBANK-R12','published_predecessor_files_preserved':len(old_before),'source_project_files_unchanged_during_audit':True,'predecessor_master_sha256':sha(B/BASEREL/'master.xml'),'preserved_baseline_master_sha256':sha(P/BASEREL/'master.xml'),'candidate_cached_master_sha256':sha(orig/'master.xml'),'candidate_semantic_sha256':digest(got),'source_review_R10_R11_bridge_independently_verified':True,'source_review_bridge_reference_count':len(bridge_refs),'source_review_R10_master_sha256':sha(RB/BASEREL/'master.xml'),'fresh_baseline_matches_published_master':True,'fresh_candidate_matches_exact_expected_delta':True,'generator_reproduces_expected_electrical_native_population_and_CSV_contract':True,'candidate_components':len(got['parts']),'candidate_bindings':len(got['nodes']),'candidate_nets':len(got['nets']),'footprint_assigned_count':238,'footprint_gap_count':len(gaps),'remaining_footprint_gaps':gaps,'all_assigned_footprint_identities_resolve':True,'unique_assigned_footprint_files':len(unique_fps),'changed_value_footprint_refs':sorted(KEEP),'removed_refs':sorted(DROP),'preserved100nF_bypasses':sorted(BYPASS),'DNP_refs':dnp,'protected_source_declarations':len(declarations),'declarations_remain_non_BOM_non_board_and_absent_from_physical_netlist':True,'all_other_native_instances_no_connects_component_fields_pin_functions_types_nets_and_symbol_libraries_preserved':True,'nominal_input_uF_before_after':[120,176],'fresh_ERC_violations':0,'regenerated_ERC_violations':0,'source_footprint_sha256':sha(fpfile),'negative_controls_rejected':len(controls),'documentation_sha256':doc_hashes,'qualifications_not_established':['Combined guaranteed Ceff and capacitor life','UVLO/falling VIN slew and startup/transients','Input ripple current or thermal qualification','PCB placement, 38mm fit, routing, stackup, assembly or fabrication release'],'baseline_promoted':False,'real_defects_found':[],'documentation_observation':'Candidate and recovery READMEs identify RCV-INBANK-R12 and preserved R11 baseline. Copied PHYSICAL_STAGE.md remains historical RCV-PHYS1 context; it does not govern this audit.'}
 save(O/'audit-results.json',result);save(O/'negative-controls.json',{'negative_controls':controls,'native_mutation_exports_performed':3,'data_only_controls':len(controls)-3,'implementation_validator_used':False})
 save(O/'source-footprint-check.json',{'exact_MPN':'CL31B226KPHNNNE','land_source':'Exact Samsung spec p33, metric3216 +/-0.20mm row; pre-audited primary source hashes remain in source-review','source_copper_ranges_mm':{'a':[1.64,1.76],'b':[1.19,1.31],'c':[1.74,1.86]},'audited_footprint':fpg,'native_import':native_fp,'copper_envelope_mm':[4.2,1.8],'solder_mask_expansion_mm':.05,'paste':'Two unnumbered F.Paste-only 1:1 rectangles, no anonymous copper','courtyard_centerline_LW_mm':[L,Wc],'eight_centerline_rectangles_area_mm2':L*Wc*8,'eight_outer_stroke_envelope_area_mm2':(L+.05)*(Wc+.05)*8,'matched_area_comparison_delta_mm2':[34.4,36.08],'metric_distinction':'95.06mm2 is the chosen eight footprint courtyard centerline-rectangle total. 34.4–36.08mm2 are matched-assumption deltas against unassigned baseline source reservations. Outer rendered stroke envelope is a third distinct metric. None establishes board fit.','process_qualified':False})
 save(O/'native-checks.json',logs);save(O/'preservation-manifest.json',{'predecessor_inventory_sha256':digest(old_before),'current_project_inventory_sha256':digest(source_before),'published_files_checked':len(old_before),'published_predecessor_files_unchanged':True,'unchanged_preserved_baseline':True,'native_outputs_confined_to_runtime_copy':True,'documentation_sha256':doc_hashes})
 print(json.dumps(result,indent=2))
if __name__=='__main__':
 try:main()
 except (AuditFailure,AssertionError) as e:print('AUDIT FAILED: '+str(e),file=sys.stderr);sys.exit(1)
