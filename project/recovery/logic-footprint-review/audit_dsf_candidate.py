#!/usr/bin/python3
"""Independent hard-coded source expectations applied to native persisted KiCad objects.

No builder/spec import. Writes isolated QA boards, plots, and reports only.
"""
from pathlib import Path
import copy, hashlib, itertools, json, math, os, re, subprocess, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'recovery/logic-footprint-review'; CAD=ROOT/'cad/recovery-footprint-candidates'
LIB=CAD/'CMK230_Recovery_Logic_Candidates.pretty'; NAME='TI_DSF0006A_SN74LVC1G97_1x1_P0.35_SourceExample_CANDIDATE'
for key,leaf in [('XDG_CACHE_HOME','cache'),('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data')]:
    p=CAD/'runtime'/leaf; p.mkdir(parents=True,exist_ok=True); os.environ[key]=str(p)
import pcbnew as k
mm=k.ToMM; nm=k.FromMM
EXPECT={'1':(-.4,-.35),'2':(-.4,0),'3':(-.4,.35),'4':(.4,.35),'5':(.4,0),'6':(.4,-.35)}
NETS={'1':'GLOBAL_DISABLE','2':'GND','3':'VDD_3V3','4':'DISABLE_OR_TF','5':'VDD_3V3','6':'MODE_TF'}
count=0
def near(a,b):
    global count
    count+=1
    assert abs(a-b)<2e-6, (a,b)
def eqseq(a,b):
    assert len(a)==len(b)
    for x,y in zip(a,b):near(x,y)
def xy(p):return (mm(p.GetPosition().x),mm(p.GetPosition().y))
def wh(p):return (mm(p.GetSize().x),mm(p.GetSize().y))
def layers(p):return set(p.GetLayerSet().Seq())
def load():
    f=k.FootprintLoad(str(LIB),NAME); assert f is not None; return f
def validate(f,origin=(0,0)):
    pads=list(f.Pads()); cp=[p for p in pads if p.IsOnCopperLayer()];mp=[p for p in pads if p.IsOnLayer(k.F_Mask)];pp=[p for p in pads if p.IsOnLayer(k.F_Paste)]
    assert len(pads)==18 and len(cp)==6 and len(mp)==6 and len(pp)==6
    numbered={p.GetNumber():p for p in cp}; assert set(numbered)==set(EXPECT)
    for num,(x,y) in EXPECT.items():
        p=numbered[num];eqseq(xy(p),(x+origin[0],y+origin[1]));eqseq(wh(p),(.60,.17));near(mm(p.GetRoundRectCornerRadius()),.05)
        assert layers(p)=={k.F_Cu} and p.GetAttribute()==k.PAD_ATTRIB_SMD and p.GetShape()==k.PAD_SHAPE_ROUNDRECT
        for coll,layer,size,radius in [(mp,k.F_Mask,(.70,.27),.10),(pp,k.F_Paste,(.60,.15),.05)]:
            matches=[q for q in coll if abs(xy(q)[0]-x-origin[0])<2e-6 and abs(xy(q)[1]-y-origin[1])<2e-6]
            assert len(matches)==1
            q=matches[0];assert q.GetNumber()=='' and layers(q)=={layer} and not q.IsOnCopperLayer()
            assert q.GetShape()==k.PAD_SHAPE_ROUNDRECT and q.GetAttribute()==k.PAD_ATTRIB_SMD
            eqseq(wh(q),size);near(mm(q.GetRoundRectCornerRadius()),radius)
            assert q.GetLocalSolderMaskMargin()==0 and q.GetLocalSolderPasteMargin()==0
            near(q.GetLocalSolderPasteMarginRatio(),0)
    assert len(list(f.Zones()))==0
    near(float(f.GetFieldText('HEIGHT_MAX_MM')),.4)
    assert f.GetAttributes() & k.FP_SMD
    for layer,expect in [(k.F_CrtYd,(-1,-.8,1,.8)),(k.Dwgs_User,(-.525,-.525,.525,.525))]:
        shapes=[s for s in f.GraphicalItems() if s.GetLayer()==layer];assert len(shapes)==1
        s=shapes[0];assert s.GetShape()==k.SHAPE_T_RECT
        eqseq([mm(s.GetStart().x)-origin[0],mm(s.GetStart().y)-origin[1],mm(s.GetEnd().x)-origin[0],mm(s.GetEnd().y)-origin[1]],expect)
    return cp,mp,pp

f=load(); cp,mp,pp=validate(f)
report={'status':'PASS_ISOLATED_GEOMETRY_NOT_MANUFACTURING_RELEASE','kicad':k.GetBuildVersion(),'units':'mm','source_transcription':'TI PDF pp3,29-31 4220597/B 06/2022; independent validator constants, no builder/spec import','electrical_copper_pads':6,'mask_only_apertures':6,'paste_only_apertures':6,'total_native_pads':18,'negative_geometry_controls':[]}

def cpnum(f,n):return next(p for p in f.Pads() if p.GetNumber()==n)
def mirror(f):
    for p in f.Pads():p.SetPosition(k.VECTOR2I(p.GetPosition().x,-p.GetPosition().y))
def wrong_paste_shrink(f):
    for p in f.Pads():
        if p.IsOnLayer(k.F_Paste):p.SetSize(k.VECTOR2I(nm(.58),nm(.15)))
def wrong_radius(f): cpnum(f,'1').SetRoundRectCornerRadius(nm(.04))
def swap_number(f):
    a,b=cpnum(f,'1'),cpnum(f,'6');a.SetNumber('6');b.SetNumber('1')
def extra_ep(f):
    p=k.PAD(f);p.SetNumber('7');p.SetAttribute(k.PAD_ATTRIB_SMD);p.SetSize(k.VECTOR2I(nm(.05),nm(.05)));ls=k.LSET();ls.AddLayer(k.F_Cu);p.SetLayerSet(ls);f.Add(p)
def missing_mask(f):f.Remove(next(p for p in f.Pads() if p.IsOnLayer(k.F_Mask)))
for label,mutate in [('bottom_view_mirror',mirror),('swap_pins_1_6',swap_number),('global_style_paste_shrink',wrong_paste_shrink),('wrong_copper_corner_radius',wrong_radius),('invented_exposed_pad',extra_ep),('missing_mask_aperture',missing_mask)]:
    wrong=load();mutate(wrong)
    try:validate(wrong)
    except AssertionError:report['negative_geometry_controls'].append({'control':label,'caught':True})
    else:raise AssertionError('Validator accepted '+label)

def min_gap(pads):
    # Rectangular bounding gap is exact for the closest aligned equal-width roundrects here.
    return min(math.hypot(max(0,abs(xy(a)[0]-xy(b)[0])-(wh(a)[0]+wh(b)[0])/2),max(0,abs(xy(a)[1]-xy(b)[1])-(wh(a)[1]+wh(b)[1])/2)) for a,b in itertools.combinations(pads,2))
report['min_copper_gap_mm']=round(min_gap(cp),6);near(report['min_copper_gap_mm'],.18)
report['min_mask_web_mm']=round(min_gap(mp),6);near(report['min_mask_web_mm'],.08)
report['min_paste_aperture_gap_mm']=round(min_gap(pp),6);near(report['min_paste_aperture_gap_mm'],.20)
report['native_geometry_mask_web_controls']=[]
for required in [.075,.08,.081,.1]:
    passes=min_gap(mp)+1e-9>=required
    assert passes==(required<=.08)
    report['native_geometry_mask_web_controls'].append({'required_web_mm':required,'actual_minimum_mm':.08,'meets_geometric_rule':passes,'factory_approved':False})
report['mask_expansion_sensitivity']=[{'expansion_per_side_mm':e,'same_column_mask_web_mm':round(.35-.17-2*e,6),'opposing_mask_gap_mm':round(.8-.6-2*e,6),'status':'candidate selected' if e==.05 else 'unbuilt within-source option; process unqualified'} for e in [.03,.04,.05,.06,.07]]
area=lambda w,h,r:w*h-(4-math.pi)*r*r
perim=lambda w,h,r:2*(w+h)-8*r+2*math.pi*r
report['stencil_geometry_screen']={'paste_area_per_aperture_mm2':area(.6,.15,.05),'copper_area_per_pad_mm2':area(.6,.17,.05),'paste_to_copper_area_ratio':area(.6,.15,.05)/area(.6,.17,.05),'paste_wall_area_at_source_009_stencil_mm2':perim(.6,.15,.05)*.09,'paste_area_to_wall_area_ratio':area(.6,.15,.05)/(perim(.6,.15,.05)*.09),'minimum_width_to_stencil_thickness':.15/.09,'status':'geometric quantities only; no stencil-release or assembly acceptance'}

# Verify candidate U14 electrical mapping but keep both U14 and U92 footprint fields blank.
xml=ET.parse(ROOT/'cad/recovery-compact-candidate/master.xml').getroot()
comps={c.attrib['ref']:c for c in xml.findall('./components/comp')}
assert comps['U14'].findtext('value')=='SN74LVC1G97DSFR SCHMITT OR CANDIDATE'
assert comps['U92'].findtext('value')=='74AUP2G97GUX DUAL SCHMITT AND CANDIDATE'
for ref in ['U14','U92']:
    assert not comps[ref].findtext('footprint')
    assert not comps[ref].findtext('./fields/field[@name="Footprint"]')
actual={node.attrib['pin']:net.attrib['name'] for net in xml.findall('./nets/net') for node in net.findall('node') if node.attrib['ref']=='U14'}
assert actual==NETS,(actual,NETS)
report['pin_net_parity']={'reference':'U14','matches_frozen_export':True,'pad_net_map':actual,'U14_footprint_field_remains_blank':True,'U92_footprint_field_remains_blank':True,'new_system_pcb_created':False}

def make_board(realnets=False):
    b=k.BOARD();fp=load();fp.SetReference('U14' if realnets else 'UQA1');fp.SetValue('SN74LVC1G97DSFR');fp.SetFPID(k.LIB_ID('CMK230_Recovery_Logic_Candidates',NAME));fp.SetPosition(k.VECTOR2I(nm(5),nm(5)));b.Add(fp)
    nets={}
    for p in fp.Pads():
        if not p.IsOnCopperLayer():continue
        name=NETS[p.GetNumber()] if realnets else 'INDEPENDENT_PAD_'+p.GetNumber()
        if name not in nets:nets[name]=k.NETINFO_ITEM(b,name);b.Add(nets[name])
        p.SetNet(nets[name])
    for a,z in [((0,0),(10,0)),((10,0),(10,10)),((10,10),(0,10)),((0,10),(0,0))]:
        s=k.PCB_SHAPE();s.SetShape(k.SHAPE_T_SEGMENT);s.SetLayer(k.Edge_Cuts);s.SetStart(k.VECTOR2I(*[nm(v) for v in a]));s.SetEnd(k.VECTOR2I(*[nm(v) for v in z]));s.SetWidth(nm(.05));b.Add(s)
    return b

def project(name,clearance=.15,maskweb=.075):
    return {'meta':{'filename':name+'.kicad_pro','version':1},'board':{'design_settings':{'rules':{'min_clearance':clearance,'min_copper_edge_clearance':.25,'min_silk_clearance':.1,'min_silk_text_height':.5,'min_silk_text_thickness':.08,'min_track_width':.075,'min_through_hole_diameter':.15,'min_via_diameter':.3,'solder_mask_clearance':0,'solder_mask_min_width':maskweb,'allow_soldermask_bridges_in_footprints':False},'rule_severities':{'missing_courtyard':'error','malformed_courtyard':'error','courtyards_overlap':'error','clearance':'error','solder_mask_bridge':'error'}}},'net_settings':{'classes':[{'name':'Default','clearance':clearance,'track_width':.1,'via_diameter':.3,'via_drill':.15}],'meta':{'version':3}}}
def save(b,name,clearance=.15,maskweb=.075):
    # These are native board setup fields, not merely project-rule JSON keys.
    b.GetDesignSettings().m_SolderMaskMinWidth=nm(maskweb)
    b.GetDesignSettings().m_AllowSoldermaskBridgesInFPs=False
    k.SaveBoard(str(CAD/(name+'.kicad_pcb')),b);(CAD/(name+'.kicad_pro')).write_text(json.dumps(project(name,clearance,maskweb),indent=2)+'\n')
    reread=k.LoadBoard(str(CAD/(name+'.kicad_pcb')))
    near(mm(reread.GetDesignSettings().m_SolderMaskMinWidth),maskweb)
    assert not reread.GetDesignSettings().m_AllowSoldermaskBridgesInFPs
qa=make_board();save(qa,'TI_DSF_Geometry_QA_ONLY')
save(qa,'TI_DSF_Negative_Clearance_0181',.181)
save(qa,'TI_DSF_Negative_Mask_Web_0081',maskweb=.081)
save(qa,'TI_DSF_Process_020_Clearance_010_Web',.2,.1)
real=make_board(True);save(real,'TI_DSF_U14_Pin_Parity_ONLY')
roundtrip=k.LoadBoard(str(CAD/'TI_DSF_Geometry_QA_ONLY.kicad_pcb')); validate(next(iter(roundtrip.GetFootprints())),(5,5))
report['persisted_board_library_geometry_parity']=True
realround=k.LoadBoard(str(CAD/'TI_DSF_U14_Pin_Parity_ONLY.kicad_pcb'))
assert {p.GetNumber():p.GetNetname() for fp in realround.GetFootprints() for p in fp.Pads() if p.IsOnCopperLayer()}==NETS

# Explicit apertures must defeat both board and footprint-wide process overrides.
ds=qa.GetDesignSettings();ds.m_SolderPasteMargin=nm(-.02);ds.m_SolderPasteMarginRatio=-.10;ds.m_SolderMaskExpansion=nm(.08)
for fp in qa.GetFootprints():
    fp.SetLocalSolderPasteMargin(nm(-.03));fp.SetLocalSolderPasteMarginRatio(-.15);fp.SetLocalSolderMaskMargin(nm(.1))
    for p in fp.Pads():
        if p.IsOnLayer(k.F_Paste):
            m=p.GetSolderPasteMargin(k.F_Paste);eqseq((mm(m.x),mm(m.y)),(0,0))
        if p.IsOnLayer(k.F_Mask):near(mm(p.GetSolderMaskExpansion(k.F_Mask)),0)
save(qa,'TI_DSF_Aperture_Override_Control')
overpro=project('TI_DSF_Aperture_Override_Control');rules=overpro['board']['design_settings']['rules'];rules.update({'solder_mask_clearance':.08,'solder_paste_margin':-.02,'solder_paste_margin_ratio':-.1})
(CAD/'TI_DSF_Aperture_Override_Control.kicad_pro').write_text(json.dumps(overpro,indent=2)+'\n')

def run(cmd):
    p=subprocess.run(cmd,text=True,capture_output=True)
    return {'command':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
drc=[]
for name in ['TI_DSF_Geometry_QA_ONLY','TI_DSF_Negative_Clearance_0181','TI_DSF_Negative_Mask_Web_0081','TI_DSF_Process_020_Clearance_010_Web','TI_DSF_U14_Pin_Parity_ONLY']:
    r=run(['kicad-cli','pcb','drc','--format','json','--severity-all','--exit-code-violations','-o',str(OUT/(name+'-drc.json')),str(CAD/(name+'.kicad_pcb'))]);drc.append(r)
    print(name,r['returncode'],r['stdout'].strip())
(OUT/'native-drc-runs.json').write_text(json.dumps(drc,indent=2)+'\n')
plots=[]
for name,tag in [('TI_DSF_Geometry_QA_ONLY','base'),('TI_DSF_Aperture_Override_Control','overrides')]:
    for layer in ['F.Cu','F.Mask','F.Paste']:
        target=OUT/'evidence'/f'native-{tag}-{layer}.svg'
        r=run(['kicad-cli','pcb','export','svg','--mode-single','--layers',layer,'--fit-page-to-board','--exclude-drawing-sheet','-o',str(target),str(CAD/(name+'.kicad_pcb'))]);assert r['returncode']==0,r;plots.append(r)
    r=run(['kicad-cli','pcb','export','gerbers','--layers','F.Cu,F.Mask,F.Paste,F.Silkscreen,F.Fab,F.Courtyard','-o',str(OUT/'evidence'/('gerbers-'+tag)),str(CAD/(name+'.kicad_pcb'))]);assert r['returncode']==0,r;plots.append(r)
def svg_geometry(file):
    return [(x.tag.split('}')[-1],dict(x.attrib)) for x in ET.parse(file).getroot().iter() if x.tag.split('}')[-1] in ['path','polygon','polyline','rect','circle','ellipse']]
report['export_override_parity']={}
for layer in ['F.Cu','F.Mask','F.Paste']:
    a=svg_geometry(OUT/'evidence'/f'native-base-{layer}.svg');b=svg_geometry(OUT/'evidence'/f'native-overrides-{layer}.svg');assert a==b
    report['export_override_parity'][layer]={'equal_geometry':True,'geometry_element_count':len(a)}
(OUT/'native-export-runs.json').write_text(json.dumps(plots,indent=2)+'\n')
# Inspect the actual native Gerber aperture definitions and flashes, not only visual plots.
report['gerber_source_geometry_parity']={}
def expected_polygon(w,h,r):
    points=[]
    for cx,cy,start in [(w/2-r,-h/2+r,-90),(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180)]:
        for j in range(5):
            t=math.radians(start+j*22.5);points.append((cx+r*math.cos(t),cy+r*math.sin(t)))
    return points
for layer,ext,size,radius in [('F_Cu','gtl',(.6,.17),.05),('F_Mask','gts',(.7,.27),.1),('F_Paste','gtp',(.6,.15),.05)]:
    layer_records=[]
    for tag,base in [('base','TI_DSF_Geometry_QA_ONLY'),('overrides','TI_DSF_Aperture_Override_Control')]:
        text=(OUT/'evidence'/('gerbers-'+tag)/(base+'-'+layer+'.'+ext)).read_text()
        apertures=re.findall(r'%ADD\d+RoundRect,([^*]+)\*%',text)
        if layer=='F_Mask':
            assert not apertures
            regions=re.findall(r'G36\*(.*?)G37\*',text,re.S);assert len(regions)==6
            centers=[];polygons=[]
            for region in regions:
                pts=[(int(x)/1e6,-int(y)/1e6) for x,y in re.findall(r'X(-?\d+)Y(-?\d+)D0[12]\*',region)]
                assert pts[0]==pts[-1];pts=pts[:-1];assert len(pts)==20
                xs=[p[0] for p in pts];ys=[p[1] for p in pts];cx=(max(xs)+min(xs))/2;cy=(max(ys)+min(ys))/2
                eqseq((max(xs)-min(xs),max(ys)-min(ys)),size);centers.append((cx-5,cy-5))
                local=[(x-cx,y-cy) for x,y in pts];expected=expected_polygon(*size,radius)
                # Each output vertex must match one exact-radius arc vertex within output quantization.
                assert all(any(math.hypot(x-a,y-b)<2e-6 for a,b in expected) for x,y in local)
                assert all(any(math.hypot(x-a,y-b)<2e-6 for x,y in local) for a,b in expected)
                polygons.append(sorted(pts))
            for actual,expected in zip(sorted(centers),sorted(EXPECT.values())):eqseq(actual,expected)
            if tag=='base':mask_base=sorted(polygons)
            else:assert sorted(polygons)==mask_base
            layer_records.append({'mode':tag,'aperture_size_mm':list(size),'source_roundrect_radius_mm':radius,'separate_region_count':6,'arc_vertex_quantization_tolerance_mm':.000002,'maximum_arc_chord_inset_mm':radius*(1-math.cos(math.radians(11.25)))})
        else:
            assert len(apertures)==1
            vals=list(map(float,apertures[0].split('X')));assert len(vals)==10 and vals[-1]==0
            rr=vals[0];xs=vals[1:9:2];ys=vals[2:9:2]
            near(rr,radius);eqseq((max(xs)-min(xs)+2*rr,max(ys)-min(ys)+2*rr),size)
            flashes=[(int(x)/1e6-5,-int(y)/1e6-5) for x,y in re.findall(r'X(-?\d+)Y(-?\d+)D03\*',text)]
            assert len(flashes)==6
            for actual,expected in zip(sorted(flashes),sorted(EXPECT.values())):eqseq(actual,expected)
            layer_records.append({'mode':tag,'aperture_size_mm':list(size),'roundrect_radius_mm':rr,'flash_count':len(flashes)})
    report['gerber_source_geometry_parity'][layer]=layer_records
base=json.loads((OUT/'TI_DSF_Geometry_QA_ONLY-drc.json').read_text());assert not base['violations'] and not base['unconnected_items'] and not base['schematic_parity']
neg=json.loads((OUT/'TI_DSF_Negative_Clearance_0181-drc.json').read_text());assert any(v['type']=='clearance' for v in neg['violations'])
real_drc=json.loads((OUT/'TI_DSF_U14_Pin_Parity_ONLY-drc.json').read_text());assert not real_drc['violations']
assert len(real_drc['unconnected_items'])==1
report['actual_net_fixture_drc']={'violations':0,'unconnected_items':1,'expected_unconnected_net':'VDD_3V3 pins3/5','reason':'Unrouted source-bound local footprint fixture; no invented tie route or system placement'}
report['intrinsic_drc']={'clearance_mm':.15,'mask_web_rule_mm':.075,'violations':len(base['violations']),'unconnected':len(base['unconnected_items']),'all_pads_have_independent_nets':True,'meaning':'Intrinsic footprint fixture only, no routed-system DRC or schematic DRC parity claim'}
report['drc_sensitivity']={}
for name in ['TI_DSF_Negative_Clearance_0181','TI_DSF_Negative_Mask_Web_0081','TI_DSF_Process_020_Clearance_010_Web']:
    r=json.loads((OUT/(name+'-drc.json')).read_text());types={}
    for v in r['violations']:types[v['type']]=types.get(v['type'],0)+1
    report['drc_sensitivity'][name]=types
mask_negative=report['drc_sensitivity']['TI_DSF_Negative_Mask_Web_0081'];assert not mask_negative
report['native_mask_drc_blind_spot']='KiCad9.0.2 does not report the 0.08-mm web of these explicit mask-only pads under a 0.081-mm minimum. The independent native pad-geometry controls reject 0.081 and 0.10 mm. Clean DRC is NOT proof of a mask-web process rule.'
protected=json.loads((OUT/'frozen-electrical-inputs.json').read_text())
current={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'cad/recovery-compact-candidate').rglob('*')) if p.is_file()}
assert current==protected
report['frozen_electrical_files_unchanged']=len(protected)
report['numeric_assertions_passed']=count
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
