#!/usr/bin/python3
"""Create only a NEW local K230 coupon from the independently checked geometry.
Run with /usr/bin/python3 for the distribution pcbnew module.
No source board, other candidate, or existing native trial is rewritten.
"""
import os
for n in ['XDG_CONFIG_HOME','XDG_DATA_HOME','XDG_CACHE_HOME']:
    os.environ[n]='/tmp/k230-ddr-constrained/'+n
import csv,hashlib,json,subprocess
from pathlib import Path
import pcbnew as k

ENG=Path(__file__).resolve().parent;ROOT=ENG.parents[1]
OUT=ROOT/'cad/bga-engineering-candidates/k230-ddr-constrained'
LIB=OUT/'K230_Engineering.pretty';BASE='K230_DDR_CONSTRAINED_LOCAL_TRIAL'
FP='K230_390_NSMD027_ENGINEERING_ONLY'
for p in [OUT,LIB,OUT/'preview']:p.mkdir(parents=True,exist_ok=True)
j=json.loads((ENG/'trial-groups-outer-21.json').read_text())
audit=json.loads((ENG/'trial-groups-outer-21-audit.json').read_text())
assert audit['nominal']['status']=='PASS_NOMINAL_LOCAL_GEOMETRY_ONLY'
assert audit['trial_sha256']==hashlib.sha256((ENG/'trial-groups-outer-21.json').read_bytes()).hexdigest()
types={r['ball']:r['proposed_compact_type'] for r in csv.DictReader((ROOT/'engineering/pin-types/k230-all390-type-audit.csv').open())}
def mm(x):return k.FromMM(x)
def pt(x,y):return k.VECTOR2I(mm(x),mm(y))
def loc(p):return pt(p[0]+100,p[1]+100)
def dump(path,v):path.write_text(json.dumps(v,indent=2)+'\n')
board=k.BOARD();board.SetCopperLayerCount(8)
s=board.GetDesignSettings();s.SetBoardThickness(mm(1.2));s.m_HasStackup=False
for attr,val in [('m_MinClearance',.1016),('m_TrackMinWidth',.1016),('m_ViasMinSize',.325),('m_MinThroughDrill',.15),('m_ViasMinAnnularWidth',.0762),('m_HoleClearance',.1524),('m_HoleToHoleMin',.20),('m_SolderMaskExpansion',0),('m_SolderMaskMinWidth',.10),('m_SolderMaskToCopperClearance',0),('m_SolderPasteMargin',0),('m_CopperEdgeClearance',.20),('m_MaxError',.001)]:setattr(s,attr,mm(val))
s.m_AllowSoldermaskBridgesInFPs=False;s.m_SolderPasteMarginRatio=0;s.m_TentViasFront=True;s.m_TentViasBack=True
nets={}
for name in sorted({b['xml_net'] for b in j['balls']}):
    n=k.NETINFO_ITEM(board,name);board.Add(n);nets[name]=n
fp=k.FOOTPRINT(board);fp.SetFPID(k.LIB_ID('K230_Engineering',FP));fp.SetReference('U1');fp.SetValue('K230 ENGINEERING ONLY');fp.SetAttributes(k.FP_SMD)
fp.SetLibDescription('Unqualified K230 390-land engineering NSMD candidate: copper .27 mm, mask .37 mm, paste .27 mm. Exact physical ball identities, top view. No manufacturer PCB footprint recommendation claimed.')
fp.Reference().SetLayer(k.F_Fab);fp.Reference().SetPosition(pt(0,-7));fp.Reference().SetTextSize(pt(.5,.5));fp.Reference().SetTextThickness(mm(.08))
fp.Value().SetLayer(k.F_Fab);fp.Value().SetPosition(pt(0,7));fp.Value().SetTextSize(pt(.5,.5));fp.Value().SetTextThickness(mm(.08))
for b in j['balls']:
    p=k.PAD(fp);p.SetNumber(b['ball']);p.SetAttribute(k.PAD_ATTRIB_SMD);p.SetShape(k.PAD_SHAPE_CIRCLE);p.SetSize(pt(.27,.27));p.SetPosition(pt(b['x'],b['y']));p.SetLayerSet(k.PAD.SMDMask());p.SetLocalSolderMaskMargin(mm(.05));p.SetLocalSolderPasteMargin(mm(0));p.SetLocalSolderPasteMarginRatio(0.0);p.SetPinFunction(b['function']);p.SetPinType(types[b['ball']]);p.SetNet(nets[b['xml_net']]);fp.Add(p)
def line(owner,a,b,layer,width=.1):
    sh=k.PCB_SHAPE(owner);sh.SetShape(k.SHAPE_T_SEGMENT);sh.SetStart(pt(*a));sh.SetEnd(pt(*b));sh.SetLayer(layer);sh.SetWidth(mm(width));owner.Add(sh)
for layer,r in [(k.F_Fab,6.55),(k.F_CrtYd,6.8)]:
    corners=[(-r,-r),(r,-r),(r,r),(-r,r),(-r,-r)]
    for a,b in zip(corners,corners[1:]):line(fp,a,b,layer,.05 if layer==k.F_CrtYd else .1)
board.Add(fp);k.PCB_IO_MGR.PluginFind(k.PCB_IO_MGR.KICAD_SEXP).FootprintSave(str(LIB),fp);fp.SetPosition(pt(100,100))
layers={'L1':k.F_Cu,'L3':k.In2_Cu,'L6':k.In5_Cu,'L8':k.B_Cu}
for v in j['vias']:
    z=k.PCB_VIA(board);z.SetPosition(loc(v['xy']));z.SetWidth(k.F_Cu,mm(.325));z.SetDrill(mm(.15));z.SetViaType(k.VIATYPE_THROUGH);z.SetLayerPair(k.F_Cu,k.B_Cu);z.SetRemoveUnconnected(False);z.SetNet(nets[v['net']]);z.SetFrontTentingMode(k.TENTING_MODE_TENTED);z.SetBackTentingMode(k.TENTING_MODE_TENTED);board.Add(z)
for r in j['routes']:
    for a,b in zip(r['points'],r['points'][1:]):
        t=k.PCB_TRACK(board);t.SetStart(loc(a));t.SetEnd(loc(b));t.SetWidth(mm(.1016));t.SetLayer(layers[r['layer']]);t.SetNet(nets[r['net']]);board.Add(t)
corners=[(90,90),(110,90),(110,110),(90,110),(90,90)]
for a,b in zip(corners,corners[1:]):line(board,a,b,k.Edge_Cuts)
for txt,y in [('K230 DDR TOPOLOGY COUPON - NOT MODULE PCB',91),('209 EXITS | 6 DDR PAIRS: SAME LAYER / 1 VIA | NO PLANES',108.5),('SPACING / COUPLING / TIMING / PDN UNQUALIFIED',109.2)]:
    t=k.PCB_TEXT(board);t.SetText(txt);t.SetPosition(pt(100,y));t.SetTextSize(pt(.4,.4));t.SetTextThickness(mm(.07));t.SetLayer(k.Dwgs_User);board.Add(t)
k.SaveBoard(str(OUT/(BASE+'.kicad_pcb')),board)
(OUT/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "K230_Engineering")(type "KiCad")(uri "${KIPRJMOD}/K230_Engineering.pretty")(options "")(descr "Unqualified K230 local trial")))\n')
template=json.loads(Path('/usr/share/kicad/template/Arduino_Uno/Arduino_Uno.kicad_pro').read_text())
severities={key:('warning' if val=='ignore' else val) for key,val in template['board']['design_settings']['rule_severities'].items()}
rules=dict(min_clearance=.1016,min_track_width=.1016,min_via_diameter=.325,min_through_hole_diameter=.15,min_via_annular_width=.0762,min_hole_clearance=.1524,min_hole_to_hole=.20,min_copper_edge_clearance=.20,solder_mask_to_copper_clearance=0,max_error=.001,min_text_height=.15,min_text_thickness=.025,min_silk_clearance=.10,min_connection=0,min_resolved_spokes=2,allow_blind_buried_vias=False,allow_microvias=False)
project={'meta':{'filename':BASE+'.kicad_pro','version':1},'board':{'design_settings':{'meta':{'filename':'board_design_settings.json','version':2},'rules':rules,'rule_severities':severities,'drc_exclusions':[],'track_widths':[0,.1016],'via_dimensions':[{'diameter':.325,'drill':.15}]}},'net_settings':{'meta':{'version':4},'classes':[{'name':'Default','clearance':.1016,'track_width':.1016,'via_diameter':.325,'via_drill':.15,'microvia_diameter':.2,'microvia_drill':.1,'diff_pair_width':.1016,'diff_pair_gap':.1016,'diff_pair_via_gap':.1016}],'netclass_assignments':{},'netclass_patterns':[]}}
dump(OUT/(BASE+'.kicad_pro'),project)
(OUT/(BASE+'.kicad_dru')).write_text('''(version 1)
# Conditional PCBWay advanced nominal trial, not JLC hole-clearance rules.
(rule "Local copper clearance" (constraint clearance (min 0.1016mm)))
(rule "Local trace width" (constraint track_width (min 0.1016mm)))
(rule "Nominal via pad" (condition "A.Type == 'Via'") (constraint via_diameter (min 0.325mm) (max 0.325mm)))
(rule "Nominal via bore" (condition "A.Type == 'Via'") (constraint hole_size (min 0.15mm) (max 0.15mm)))
(rule "Selected 3mil nominal annulus" (condition "A.Type == 'Via'") (constraint annular_width (min 0.0762mm)))
(rule "Hole to other net copper" (constraint hole_clearance (min 0.1524mm)))
(rule "Added local drill spacing check" (constraint hole_to_hole (min 0.20mm)))
''')
argv=['kicad-cli','pcb','drc','--format','json','--all-track-errors','--severity-all','--exit-code-violations','-o',str(ENG/'native-drc.json'),str(OUT/(BASE+'.kicad_pcb'))]
run=subprocess.run(argv,text=True,capture_output=True);(ENG/'native-drc.log').write_text(run.stdout+run.stderr);dump(ENG/'native-drc-command.json',dict(argv=argv,exit_code=run.returncode,kicad_version=k.GetBuildVersion()))
if run.returncode not in (0,5):raise RuntimeError(run.stdout+run.stderr)
for name,ls in [('L1','F.Cu'),('L3','In2.Cu'),('L6','In5.Cu'),('L8','B.Cu')]:
    cmd=['kicad-cli','pcb','export','svg','--layers',ls+',Edge.Cuts,F.Fab,Dwgs.User','--page-size-mode','2','--exclude-drawing-sheet','--mode-single','-o',str(OUT/'preview'/('native-'+name+'.svg')),str(OUT/(BASE+'.kicad_pcb'))]
    z=subprocess.run(cmd,text=True,capture_output=True)
    if z.returncode:raise RuntimeError(z.stdout+z.stderr)
print(run.stdout+run.stderr)
