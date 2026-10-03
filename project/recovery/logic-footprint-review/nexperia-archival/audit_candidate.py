#!/usr/bin/python3
"""Independent native checks for the archival SOT1160-1 candidate, no builder import."""
from pathlib import Path
import hashlib,itertools,json,math,os,re,subprocess,xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[3];O=R/'recovery/logic-footprint-review/nexperia-archival';C=R/'cad/recovery-footprint-candidates/nexperia-archival';L=C/'CMK230_NXP_Archival_Candidates.pretty'
NAME='NXP_SOT1160-1_74AUP2G97_1.4x1.8_P0.4_ArchivalCrosschecked_CANDIDATE'
for key,leaf in [('XDG_CACHE_HOME','cache'),('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data')]:
 p=C/'runtime'/leaf;p.mkdir(parents=True,exist_ok=True);os.environ[key]=str(p)
import pcbnew as k
mm=k.ToMM;nm=k.FromMM;count=0
# Independently transcribed from the actual archived outline/reflow pixels.
EXP={'1':(-.525,-.2,.65,.22),'2':(-.575,.2,.55,.22),'3':(-.4,.775,.22,.55),'4':(0,.775,.22,.55),'5':(.4,.775,.22,.55),'6':(.575,.2,.55,.22),'7':(.575,-.2,.55,.22),'8':(.4,-.775,.22,.55),'9':(0,-.775,.22,.55),'10':(-.4,-.775,.22,.55)}
NETS={'1':'GND','2':'BOOT_VOLTAGE_QUALIFIED_1V8','3':'RESET_RELEASE_REQUEST_1V8','4':'GND','5':'FIXED_RAILS_PGOOD_3V3','6':'GND','7':'RSTN','8':'STORAGE_ENABLE_1V8','9':'VDD1P8','10':'FIXED_RAILS_PGOOD_3V3'}
def near(a,b):
 global count
 count+=1;assert abs(a-b)<2e-6,(a,b)
def eq(a,b):
 assert len(a)==len(b)
 for x,y in zip(a,b):near(x,y)
def xywh(p):return tuple(mm(v) for v in [p.GetPosition().x,p.GetPosition().y,p.GetSize().x,p.GetSize().y])
def load():
 f=k.FootprintLoad(str(L),NAME);assert f is not None;return f
def copper(f):return [p for p in f.Pads() if p.IsOnCopperLayer()]
def numbered(f,n):return next(p for p in copper(f) if p.GetNumber()==n)
def validate(f,origin=(0,0)):
 ps=list(f.Pads());cp=copper(f);assert len(ps)==30 and len(cp)==10 and {p.GetNumber() for p in cp}==set(EXP)
 for layer,delta in [(k.F_Cu,0),(k.F_Mask,.125),(k.F_Paste,-.04)]:
  pads=[p for p in ps if p.IsOnLayer(layer)];assert len(pads)==10
  for num,(x,y,w,h) in EXP.items():
   matches=[p for p in pads if abs(xywh(p)[0]-origin[0]-x)<2e-6 and abs(xywh(p)[1]-origin[1]-y)<2e-6];assert len(matches)==1
   p=matches[0];eq(xywh(p),(x+origin[0],y+origin[1],w+delta,h+delta));assert p.GetShape()==k.PAD_SHAPE_RECT
   assert set(p.GetLayerSet().Seq())=={layer} and p.GetAttribute()==k.PAD_ATTRIB_SMD
   assert p.GetNumber()==(num if layer==k.F_Cu else '')
   assert p.GetLocalSolderMaskMargin()==0 and p.GetLocalSolderPasteMargin()==0;near(p.GetLocalSolderPasteMarginRatio(),0)
 for layer,box in [(k.F_CrtYd,(-1.25,-1.45,1.25,1.45)),(k.Dwgs_User,(-.75,-.95,.75,.95)),(k.Cmts_User,(-.825,-1.025,.825,1.025))]:
  g=[a for a in f.GraphicalItems() if a.GetLayer()==layer];assert len(g)==1 and g[0].GetShape()==k.SHAPE_T_RECT
  g=g[0];eq((mm(g.GetStart().x)-origin[0],mm(g.GetStart().y)-origin[1],mm(g.GetEnd().x)-origin[0],mm(g.GetEnd().y)-origin[1]),box)
 near(float(f.GetFieldText('HEIGHT_MAX_MM')),.5);assert not list(f.Zones())
 return ps
f=load();ps=validate(f)
report={'status':'PASS_ARCHIVAL_PIXELS_CURRENT_PRIMARY_TEXT_CROSSCHECK_PROCESS_UNQUALIFIED','kicad':k.GetBuildVersion(),'electrical_copper_pads':10,'explicit_mask_only_apertures':10,'explicit_paste_only_apertures':10,'no_extra_exposed_pad':True,'negative_controls':[]}
def mirror(f):
 for p in f.Pads():p.SetPosition(k.VECTOR2I(p.GetPosition().x,-p.GetPosition().y))
def symmetrize(f):
 p=numbered(f,'1');p.SetPosition(k.VECTOR2I(nm(-.575),nm(-.2)));p.SetSize(k.VECTOR2I(nm(.55),nm(.22)))
def swap(f):
 a,b=numbered(f,'1'),numbered(f,'2');a.SetNumber('2');b.SetNumber('1')
def missingmask(f):
 p=next(p for p in f.Pads() if p.IsOnLayer(k.F_Mask));ls=k.LSET();ls.AddLayer(k.B_Mask);p.SetLayerSet(ls)
def wrongpaste(f):
 for p in f.Pads():
  if p.IsOnLayer(k.F_Paste):p.SetSize(k.VECTOR2I(p.GetSize().x+nm(.04),p.GetSize().y+nm(.04)))
def ep(f):
 p=k.PAD(f);p.SetNumber('11');p.SetSize(k.VECTOR2I(nm(.05),nm(.05)));p.SetAttribute(k.PAD_ATTRIB_SMD);ls=k.LSET();ls.AddLayer(k.F_Cu);p.SetLayerSet(ls);f.Add(p)
negative_owners=[]
for label,mutate in [('wrong_terminal_view_mirror',mirror),('lose_long_pin1_asymmetry',symmetrize),('swap_pin1_pin2',swap),('missing_mask',missingmask),('one_to_one_paste',wrongpaste),('invented_EP11',ep)]:
 print('Checking negative control:',label,flush=True)
 bad=load();negative_owners.append(bad);mutate(bad)
 try:validate(bad)
 except AssertionError:report['negative_controls'].append({'control':label,'caught':True})
 else:raise AssertionError(label+' accepted')
def gap(pads):
 return min(math.hypot(max(0,abs(xywh(a)[0]-xywh(b)[0])-(xywh(a)[2]+xywh(b)[2])/2),max(0,abs(xywh(a)[1]-xywh(b)[1])-(xywh(a)[3]+xywh(b)[3])/2)) for a,b in itertools.combinations(pads,2))
for layer,name,target in [(k.F_Cu,'copper',.18),(k.F_Mask,'mask',.055),(k.F_Paste,'paste',.22)]:
 result=gap([p for p in ps if p.IsOnLayer(layer)]);near(result,target);report['minimum_'+name+'_gap_mm']=round(result,6)
report['mask_web_controls']=[{'minimum_required_mm':v,'actual_mm':.055,'passes_geometry':.055+1e-9>=v,'factory_accepted':False} for v in [.05,.055,.056,.075]]
assert [v['passes_geometry'] for v in report['mask_web_controls']]==[True,True,False,False]
report['stencil_geometry']=[{'copper_size_mm':[w,h],'paste_size_mm':[w-.04,h-.04],'stencil_mm':.1,'area_ratio':(w-.04)*(h-.04)/(2*((w-.04)+(h-.04))*.1),'coverage_ratio':(w-.04)*(h-.04)/(w*h),'process_acceptance':False} for w,h in [(.65,.22),(.55,.22),(.22,.55)]]
xml=E.parse(R/'cad/recovery-compact-candidate/master.xml').getroot();comps={c.attrib['ref']:c for c in xml.findall('./components/comp')}
actual={node.attrib['pin']:net.attrib['name'] for net in xml.findall('./nets/net') for node in net.findall('node') if node.attrib['ref']=='U92'};assert actual==NETS
assert comps['U92'].findtext('value')=='74AUP2G97GUX DUAL SCHMITT AND CANDIDATE'
for ref in ['U14','U92']:assert not comps[ref].findtext('footprint') and not comps[ref].findtext('./fields/field[@name="Footprint"]')
report['pin_net_parity']={'frozen_U92_export_matches':True,'nets':NETS,'actual_power_pins':{'VCC':'9','GND':'4'},'grounded_logic_inputs':['1','6'],'bypass_affinity':'Use physical VCC9/GND4, not grounded logic inputs1/6. TI U14 is VCC5/GND2; pin3 is a tied-high logic input.'}
def board(real=False):
 b=k.BOARD();f=load();f.SetReference('U92' if real else 'UQA2');f.SetValue('74AUP2G97GUX');f.SetFPID(k.LIB_ID('CMK230_NXP_Archival_Candidates',NAME));f.SetPosition(k.VECTOR2I(nm(5),nm(5)));b.Add(f);nets={}
 for p in copper(f):
  name=NETS[p.GetNumber()] if real else 'UNIQUE_PIN_'+p.GetNumber()
  if name not in nets:nets[name]=k.NETINFO_ITEM(b,name);b.Add(nets[name])
  p.SetNet(nets[name])
 for a,z in [((0,0),(10,0)),((10,0),(10,10)),((10,10),(0,10)),((0,10),(0,0))]:
  s=k.PCB_SHAPE();s.SetShape(k.SHAPE_T_SEGMENT);s.SetLayer(k.Edge_Cuts);s.SetStart(k.VECTOR2I(*[nm(v) for v in a]));s.SetEnd(k.VECTOR2I(*[nm(v) for v in z]));s.SetWidth(nm(.05));b.Add(s)
 return b
def project(name,clear):return {'meta':{'filename':name+'.kicad_pro','version':1},'board':{'design_settings':{'rules':{'min_clearance':clear,'min_copper_edge_clearance':.25,'min_silk_clearance':.1,'min_text_height':.8,'min_text_thickness':.08},'rule_severities':{'clearance':'error','missing_courtyard':'error','malformed_courtyard':'error','solder_mask_bridge':'error'}}},'net_settings':{'classes':[{'name':'Default','clearance':clear,'track_width':.1,'via_diameter':.3,'via_drill':.15}],'meta':{'version':3}}}
def save(b,name,clear=.15,mask=.05):
 ds=b.GetDesignSettings();ds.m_SolderMaskMinWidth=nm(mask);ds.m_AllowSoldermaskBridgesInFPs=False
 k.SaveBoard(str(C/(name+'.kicad_pcb')),b);(C/(name+'.kicad_pro')).write_text(json.dumps(project(name,clear),indent=2)+'\n')
 reread=k.LoadBoard(str(C/(name+'.kicad_pcb')));near(mm(reread.GetDesignSettings().m_SolderMaskMinWidth),mask);assert not reread.GetDesignSettings().m_AllowSoldermaskBridgesInFPs
 validate(next(iter(reread.GetFootprints())),(5,5))
qa=board();save(qa,'NXP_Geometry_QA_ONLY');save(qa,'NXP_Negative_Clearance_0181',.181);save(qa,'NXP_Negative_Mask_0056',mask=.056);save(qa,'NXP_Process_020_0075',.2,.075)
real=board(True);save(real,'NXP_U92_Actual_Nets_ONLY')
rb=k.LoadBoard(str(C/'NXP_U92_Actual_Nets_ONLY.kicad_pcb'));assert {p.GetNumber():p.GetNetname() for f in rb.GetFootprints() for p in copper(f)}==NETS
ds=qa.GetDesignSettings();ds.m_SolderPasteMargin=nm(-.02);ds.m_SolderPasteMarginRatio=-.1;ds.m_SolderMaskExpansion=nm(.08)
for f in qa.GetFootprints():
 f.SetLocalSolderPasteMargin(nm(-.03));f.SetLocalSolderPasteMarginRatio(-.15);f.SetLocalSolderMaskMargin(nm(.1))
 for p in f.Pads():
  if p.IsOnLayer(k.F_Paste):a=p.GetSolderPasteMargin(k.F_Paste);eq((mm(a.x),mm(a.y)),(0,0))
  if p.IsOnLayer(k.F_Mask):near(mm(p.GetSolderMaskExpansion(k.F_Mask)),0)
save(qa,'NXP_Aperture_Override_Control')
def run(cmd):
 p=subprocess.run(cmd,capture_output=True,text=True);return {'command':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
drc=[]
for name in ['NXP_Geometry_QA_ONLY','NXP_Negative_Clearance_0181','NXP_Negative_Mask_0056','NXP_Process_020_0075','NXP_U92_Actual_Nets_ONLY']:
 a=run(['kicad-cli','pcb','drc','--format','json','--severity-all','--exit-code-violations','-o',str(O/(name+'-drc.json')),str(C/(name+'.kicad_pcb'))]);drc.append(a);print(name,a['returncode'],a['stdout'].strip())
(O/'native-drc-runs.json').write_text(json.dumps(drc,indent=2)+'\n')
plots=[]
for name,tag in [('NXP_Geometry_QA_ONLY','base'),('NXP_Aperture_Override_Control','overrides')]:
 for layer in ['F.Cu','F.Mask','F.Paste']:
  a=run(['kicad-cli','pcb','export','svg','--mode-single','--layers',layer,'--fit-page-to-board','--exclude-drawing-sheet','-o',str(O/'evidence'/f'native-{tag}-{layer}.svg'),str(C/(name+'.kicad_pcb'))]);assert a['returncode']==0,a;plots.append(a)
 a=run(['kicad-cli','pcb','export','gerbers','--layers','F.Cu,F.Mask,F.Paste,F.Silkscreen,F.Fab,F.Courtyard','-o',str(O/'evidence'/('gerbers-'+tag)),str(C/(name+'.kicad_pcb'))]);assert a['returncode']==0,a;plots.append(a)
a=run(['kicad-cli','pcb','export','gerbers','--layers','F.Mask','-o',str(O/'evidence/gerbers-mask-0075'),str(C/'NXP_Process_020_0075.kicad_pcb')]);assert a['returncode']==0,a;plots.append(a)
(O/'native-export-runs.json').write_text(json.dumps(plots,indent=2)+'\n')
def svggeom(p):return [(x.tag.split('}')[-1],dict(x.attrib)) for x in E.parse(p).getroot().iter() if x.tag.split('}')[-1] in ['path','polygon','rect','circle','ellipse','polyline']]
report['export_parity']={}
for layer in ['F.Cu','F.Mask','F.Paste']:
 a=svggeom(O/'evidence'/f'native-base-{layer}.svg');b=svggeom(O/'evidence'/f'native-overrides-{layer}.svg');assert a==b;report['export_parity'][layer]={'native_svg_geometry_equal':True,'geometry_elements':len(a)}
def gerber_rectangles(path):
 text=path.read_text();aps={int(n):(float(w),float(h)) for n,w,h in re.findall(r'%ADD(\d+)R,([0-9.]+)X([0-9.]+)\*%',text)};rects=[]
 if aps:
  current=None
  for line in text.splitlines():
   sel=re.fullmatch(r'D(\d+)\*',line)
   if sel:current=int(sel[1])
   flash=re.fullmatch(r'X(-?\d+)Y(-?\d+)D03\*',line)
   if flash:assert current in aps;rects.append((int(flash[1])/1e6-5,-int(flash[2])/1e6-5,*aps[current]))
 else:
  for reg in re.findall(r'G36\*(.*?)G37\*',text,re.S):
   pts=[(int(x)/1e6,-int(y)/1e6) for x,y in re.findall(r'X(-?\d+)Y(-?\d+)D0[12]\*',reg)];assert pts[0]==pts[-1];pts=pts[:-1];assert len(pts)==4
   xs=[x for x,y in pts];ys=[y for x,y in pts];assert len(set(xs))==2 and len(set(ys))==2
   rects.append(((max(xs)+min(xs))/2-5,(max(ys)+min(ys))/2-5,max(xs)-min(xs),max(ys)-min(ys)))
 return sorted(rects)
report['gerber_geometry']={}
for layer,ext,delta in [('F_Cu','gtl',0),('F_Mask','gts',.125),('F_Paste','gtp',-.04)]:
 expected=sorted((x,y,w+delta,h+delta) for x,y,w,h in EXP.values());records=[]
 for name,tag in [('NXP_Geometry_QA_ONLY','base'),('NXP_Aperture_Override_Control','overrides')]:
  actual=gerber_rectangles(O/'evidence'/('gerbers-'+tag)/(name+'-'+layer+'.'+ext));assert len(actual)==10
  for a,b in zip(actual,expected):eq(a,b)
  records.append({'mode':tag,'exact_rectangular_apertures':10,'centers_and_dimensions_match':True})
 report['gerber_geometry'][layer]=records
strictpath=O/'evidence/gerbers-mask-0075/NXP_Process_020_0075-F_Mask.gts'
stricttext=strictpath.read_text();assert stricttext.count('G36*')==1 and 'D03*' not in stricttext
try:gerber_rectangles(strictpath)
except AssertionError:strict_rejected=True
else:raise AssertionError('Merged mask unexpectedly passed source-exact rectangular-aperture parser')
report['mask_export_process_control']={'source_mask_expansion_per_side_mm':.0625,'nominal_web_mm':.055,'base_native_mask_web_setting_mm':.05,'base_individual_regions':10,'strict_native_mask_web_setting_mm':.075,'strict_complex_merged_regions':1,'strict_rejected_by_source_exact_aperture_check':strict_rejected,'meaning':'Explicit mask-only pads do not prevent native global minimum-width merging. 0.075-mm output is a diagnostic merged-mask control, not the source-exact candidate release. No gang-mask or reduced-expansion manufacturing approval.'}
def read_drc(n):return json.loads((O/(n+'-drc.json')).read_text())
base=read_drc('NXP_Geometry_QA_ONLY');assert not base['violations'] and not base['unconnected_items']
report['intrinsic_drc']={'violations':0,'unconnected':0,'provisional_clearance_mm':.15,'provisional_mask_web_mm':.05}
report['drc_sensitivity']={}
for name in ['NXP_Negative_Clearance_0181','NXP_Negative_Mask_0056','NXP_Process_020_0075']:
 d=read_drc(name);types={}
 for v in d['violations']:types[v['type']]=types.get(v['type'],0)+1
 report['drc_sensitivity'][name]=types
assert report['drc_sensitivity']['NXP_Negative_Clearance_0181'].get('clearance')==6
assert not report['drc_sensitivity']['NXP_Negative_Mask_0056']
report['mask_native_drc_limit']='0.056-mm native minimum saved and round-trip verified, but native DRC misses 0.055-mm web in explicit mask-only apertures. Independent geometry rejects it; factory/CAM review remains mandatory.'
actual=read_drc('NXP_U92_Actual_Nets_ONLY');assert not actual['violations'] and len(actual['unconnected_items'])==3
report['actual_net_fixture']={'geometry_violations':0,'unconnected_items':3,'expected':'Two GND ties and one FIXED_RAILS_PGOOD_3V3 tie intentionally unrouted in local fixture','system_schematic_DRC_parity_claimed':False}
ti=json.loads((O.parent/'freeze-manifest.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert all(sha(R/p)==m['sha256'] for p,m in ti['files'].items());assert all(sha(R/p)==s for p,s in ti['protected_electrical_files'].items())
report['frozen_TI_files_unchanged']=len(ti['files']);report['frozen_electrical_files_unchanged']=len(ti['protected_electrical_files']);report['numeric_assertions']=count
(O/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
