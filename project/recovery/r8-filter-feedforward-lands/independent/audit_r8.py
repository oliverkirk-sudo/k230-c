#!/usr/bin/env python3
"""Independent read-only R7/R8 identity, saved geometry and CAM audit.

Run with KiCad's pcbnew-capable Python; all exports and mutations go to --output.
"""
from pathlib import Path
import argparse, collections, copy, hashlib, json, os, re, shutil, subprocess
import xml.etree.ElementTree as ET

ap=argparse.ArgumentParser()
ap.add_argument('--project',type=Path,required=True)
ap.add_argument('--baseline',type=Path,required=True)
ap.add_argument('--output',type=Path,required=True)
ap.add_argument('--runtime',type=Path,required=True)
a=ap.parse_args();P=a.project.resolve();B=a.baseline.resolve();O=a.output.resolve();O.mkdir(parents=True,exist_ok=True)
R=P/'recovery/r8-filter-feedforward-lands';A=P/'cad/recovery-physical-candidate'
L=P/'cad/recovery-filter-candidates/CMK230_Filter_Feedforward_Candidates.pretty'
LIB='CMK230_Filter_Feedforward_Candidates'
FB=[f'FB{i}' for i in range(202,211)];CAP=['C202','C219','C224','C229']
expected={r:LIB+':Murata_BLM15PX121_18um_SourcePattern_CONDITIONAL' for r in FB}
expected.update({r:LIB+':KEMET_C0402_C0G_DensityB_SOURCE_CANDIDATE' for r in CAP})
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
dump=lambda n,d:(O/n).write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
env=os.environ.copy()
for k,d in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data')]:
    q=a.runtime.resolve()/d;q.mkdir(parents=True,exist_ok=True);env[k]=str(q);os.environ[k]=str(q)
import pcbnew as pcb
log=[]
def run(args):
    x=subprocess.run(['kicad-cli',*map(str,args)],env=env,capture_output=True,text=True,timeout=60)
    log.append(dict(command=['kicad-cli',*map(str,args)],returncode=x.returncode,stdout=x.stdout,stderr=x.stderr))
    assert x.returncode in (0,5),(x.returncode,x.stderr)
    return x
def canon(e):
    return (e.tag,tuple(sorted(e.attrib.items())),(e.text or '').strip(),tuple(sorted((canon(c) for c in e),key=repr)))
def parse(path):
    r=ET.parse(path).getroot()
    c={e.get('ref'):e for e in r.findall('components/comp')}
    n={(z.get('ref'),z.get('pin')):(n.get('name'),z.get('pinfunction'),z.get('pintype')) for n in r.findall('nets/net') for z in n.findall('node')}
    return r,c,n
def nofp(c):
    c=copy.deepcopy(c)
    f=c.find('footprint')
    if f is not None:c.remove(f)
    for f in c.findall("fields/field[@name='Footprint']"):f.text=''
    return canon(c)
def mm(v):return round(pcb.ToMM(0 if v is None else v),6)
def geometry(board):
    out={}
    for f in board.GetFootprints():
        out[f.GetReference()]={'id':str(f.GetFPID().GetLibItemName()),'origin':[mm(f.GetPosition().x),mm(f.GetPosition().y)],'pads':sorted([dict(number=q.GetNumber(),x=mm(q.GetPosition().x-f.GetPosition().x),y=mm(q.GetPosition().y-f.GetPosition().y),w=mm(q.GetSize().x),h=mm(q.GetSize().y),shape=int(q.GetShape()),layers=[pcb.LayerName(i) for i in (pcb.F_Cu,pcb.B_Cu,pcb.F_Mask,pcb.B_Mask,pcb.F_Paste,pcb.B_Paste) if q.IsOnLayer(i)],mask_margin_mm=mm(q.GetLocalSolderMaskMargin()),net=q.GetNetname()) for q in f.Pads()],key=repr)}
    return out
def check_geom(g):
    for ref,d in [('FB202',1.2),('FB203',.7),('FB204',.5)]:
        pads=g[ref]['pads']
        for layer,h in [('F.Cu',d),('F.Mask',.5),('F.Paste',.5)]:
            p=[q for q in pads if layer in q['layers']]
            assert sorted((q['x'],q['y'],q['w'],q['h']) for q in p)==[(-.4,0,.4,h),(.4,0,.4,h)],(ref,layer,p)
            assert all(q['layers']==[layer] for q in p)
        assert [(q['number'],q['x']) for q in sorted(pads,key=lambda q:q['x']) if q['number']]==[('1',-.4),('2',.4)]
        assert all(q['mask_margin_mm']==0 for q in pads)
    pads=g['C202']['pads']
    for layer in ['F.Cu','F.Mask','F.Paste']:
        p=[q for q in pads if layer in q['layers']]
        assert sorted((q['x'],q['y'],q['w'],q['h']) for q in p)==[(-.45,0,.62,.62),(.45,0,.62,.62)]
        if layer=='F.Mask':assert all(q['mask_margin_mm']==.05 for q in p)
    assert all('B.Cu' not in q['layers'] and 'B.Mask' not in q['layers'] and 'B.Paste' not in q['layers'] for f in g.values() for q in f['pads'])

watched=[*A.glob('*.kicad_sch'),A/'master.xml',A/'fp-lib-table',*L.glob('*.kicad_mod'),R/'FILTER_LANDS_GEOMETRY_ONLY.kicad_pcb',R/'FILTER_LANDS_GEOMETRY_ONLY.kicad_pro']
before={str(p.relative_to(P)):sha(p) for p in watched}
br,bc,bn=parse(B/'cad/recovery-physical-candidate/master.xml');r,c,n=parse(A/'master.xml')
assert set(c)==set(bc) and len(c)==254
assert n==bn and len(n)==1509 and len(r.findall('nets/net'))==457
changed={ref:c[ref].findtext('footprint') for ref in c if c[ref].findtext('footprint')!=bc[ref].findtext('footprint')}
assert changed==expected
assert all(nofp(c[ref])==nofp(bc[ref]) for ref in c),'Non-footprint component identity changed'
assert canon(br.find('nets'))==canon(r.find('nets'))
assert sum(bool(q.findtext('footprint')) for q in c.values())==215
assert sum(not q.findtext('footprint') for q in c.values())==39
schematics=[]
for p in A.glob('*.kicad_sch'):
    b=B/'cad/recovery-physical-candidate'/p.name
    s=p.read_text().replace('(rev "RCV-R8")','(rev "RCV-R7")')
    for value in set(expected.values()):s=s.replace('(property "Footprint" "'+value+'"','(property "Footprint" ""')
    assert s==b.read_text(),p.name
    schematics.append(p.name)
dnp=sorted(ref for ref,v in c.items() if any(p.get('name')=='dnp' for p in v.findall('property')))
assert dnp==['JP1','R45','R47','R528']
run(['sch','export','netlist','--format','kicadxml','-o',O/'fresh-master.xml',A/'CMK230_Core_REVIEW.kicad_sch'])
fr,fc,fn=parse(O/'fresh-master.xml');assert fn==n and set(fc)==set(c)
assert all(canon(fc[ref])==canon(c[ref]) for ref in c)
run(['sch','erc','--format','json','--severity-all','-o',O/'fresh-erc.json',A/'CMK230_Core_REVIEW.kicad_sch'])
erc=json.loads((O/'fresh-erc.json').read_text());assert not [v for sh in erc['sheets'] for v in sh['violations']]
dump('identity-check.json',dict(baseline_master_sha256=sha(B/'cad/recovery-physical-candidate/master.xml'),r8_master_sha256=sha(A/'master.xml'),components=254,bindings=1509,nets=457,assigned=215,gaps=39,changed_footprints=changed,component_nonfootprint_identity_unchanged=True,nets_full_identity_unchanged=True,schematics_exact_after_13_footprints_and_revision_normalization=schematics,unchanged_DNP_refs=dnp,BOM_population_flags_unchanged=True,fresh_native_export_matches=True,fresh_ERC_violations=0))

board=pcb.LoadBoard(str(R/'FILTER_LANDS_GEOMETRY_ONLY.kicad_pcb'));g=geometry(board);check_geom(g)
assert len(g)==4 and board.GetCopperLayerCount()==6
# Match the embedded fixture lands to freshly loaded library geometry, including layer allocation.
for f in board.GetFootprints():
    lp=pcb.FootprintLoad(str(L),f.GetFPID().GetLibItemName());assert lp
    libpads=sorted((q.GetNumber(),mm(q.GetPosition().x),mm(q.GetPosition().y),mm(q.GetSize().x),mm(q.GetSize().y),tuple(q.GetLayerSet().Seq()),mm(q.GetLocalSolderMaskMargin())) for q in lp.Pads())
    actual=sorted((q.GetNumber(),mm(q.GetPosition().x-f.GetPosition().x),mm(q.GetPosition().y-f.GetPosition().y),mm(q.GetSize().x),mm(q.GetSize().y),tuple(q.GetLayerSet().Seq()),mm(q.GetLocalSolderMaskMargin())) for q in f.Pads())
    assert libpads==actual,f.GetReference()
copyboard=O/'native-roundtrip.kicad_pcb';pcb.SaveBoard(str(copyboard),board)
assert geometry(pcb.LoadBoard(str(copyboard)))==g
shutil.copyfile(R/'FILTER_LANDS_GEOMETRY_ONLY.kicad_pro',copyboard.with_suffix('.kicad_pro'))
local_lib=O/'source-footprints'/L.name;shutil.copytree(L,local_lib,dirs_exist_ok=True)
(O/'fp-lib-table').write_text('(fp_lib_table (lib (name "'+LIB+'") (type "KiCad") (uri "${KIPRJMOD}/source-footprints/'+L.name+'") (options "") (descr "Read-only independent source library")))\n')
run(['pcb','drc','--format','json','--severity-all','-o',O/'roundtrip-drc.json',copyboard])
drc=json.loads((O/'roundtrip-drc.json').read_text());assert not drc['violations'] and not drc['unconnected_items']
cam=O/'native-cam';cam.mkdir(exist_ok=True)
run(['pcb','export','gerbers','--layers','F.Cu,F.Mask,F.Paste','--output',cam,copyboard])

def gerber(path):
    text=path.read_text();apertures={};active=None;ref=None;flashes=[]
    assert '%FSLAX46Y46*%' in text and '%MOMM*%' in text
    for ln in text.splitlines():
        m=re.fullmatch(r'%ADD(\d+)(\w+),([^*]+)\*%',ln)
        if m:
            code,kind,args=m.groups();nums=list(map(float,args.split('X')))
            if kind=='R':w,h=nums;shape=dict(kind='R',w=w,h=h)
            elif kind=='RoundRect':
                radius=nums[0];coords=nums[1:9];xs=coords[::2];ys=coords[1::2]
                shape=dict(kind='RoundRect',w=round(max(xs)-min(xs)+2*radius,6),h=round(max(ys)-min(ys)+2*radius,6),radius=radius)
            else:raise AssertionError(kind)
            apertures[int(code)]=shape
        m=re.fullmatch(r'D(\d+)\*',ln)
        if m:active=int(m.group(1))
        m=re.match(r'%TO\.(?:C|P),([^,*]+)',ln)
        if m:ref=m.group(1)
        m=re.fullmatch(r'X(-?\d+)Y(-?\d+)D03\*',ln)
        if m:flashes.append(dict(ref=ref,x=int(m.group(1))/1e6,y=-int(m.group(2))/1e6,**apertures[active]))
    assert not re.search(r'D0[12]\*',text),'Unexpected stroke beyond independent flash parser'
    return sorted(flashes,key=repr)
def checkcam(directory):
    answer={}
    for suffix,layer in [('gtl','F.Cu'),('gts','F.Mask'),('gtp','F.Paste')]:
        f=next(directory.glob('*.'+suffix));flashes=gerber(f);assert len(flashes)==8
        for z in flashes:
            ref=z['ref'];origin=g[ref]['origin'];x=round(z['x']-origin[0],6);y=round(z['y']-origin[1],6)
            if ref.startswith('FB'):
                d={'FB202':1.2,'FB203':.7,'FB204':.5}[ref] if layer=='F.Cu' else .5
                assert (x,y,z['w'],z['h'],z['kind']) in [(-.4,0,.4,d,'R'),(.4,0,.4,d,'R')],(layer,z)
            else:
                assert x in (-.45,.45) and y==0
                if layer=='F.Mask':assert (z['w'],z['h'],z['kind'],z.get('radius'))==(.72,.72,'RoundRect',.05)
                else:assert (z['w'],z['h'],z['kind'])==(.62,.62,'R')
        answer[layer]=flashes
    return answer
cams=checkcam(cam);sourcecams=checkcam(R/'native-cam');assert cams==sourcecams
dump('saved-geometry-and-cam.json',dict(kicad_version=pcb.Version(),six_layer_geometry_fixture=True,fixture_is_core_layout=False,geometry=g,native_roundtrip_identical=True,loaded_library_matches_embedded=True,fresh_fixture_DRC_violations=0,fresh_fixture_unconnected=0,flash_geometry=cams,source_CAM_matches_fresh_native_export=True,Murata_nominal_mask_registration_allowance_mm=0,KEMET_mask_expansion_mm=.05,KEMET_mask_export_radius_mm=.05,paste='1:1 relative to exposed Murata lands and KEMET copper; candidate assumption, not manufacturer-qualified stencil'))

controls=[]
def expect_reject(name,fun):
    try:fun()
    except AssertionError:controls.append(dict(name=name,result='REJECTED_AS_EXPECTED'));return
    raise AssertionError('Control was not caught: '+name)
# Mutate real saved native pads, reload, export CAM, and independently reject both.
for name,layer,newheight in [('18um_copper_shrunk_to_35um_width',pcb.F_Cu,.7),('18um_mask_exposes_copper_shoulders',pcb.F_Mask,1.2),('18um_paste_covers_copper_shoulders',pcb.F_Paste,1.2)]:
    nb=pcb.LoadBoard(str(copyboard));nf=next(f for f in nb.GetFootprints() if f.GetReference()=='FB202')
    q=next(q for q in nf.Pads() if q.IsOnLayer(layer));q.SetSize(pcb.VECTOR2I(pcb.FromMM(.4),pcb.FromMM(newheight)))
    path=O/(name+'.kicad_pcb');pcb.SaveBoard(str(path),nb)
    expect_reject(name+'_native_reload',lambda:check_geom(geometry(pcb.LoadBoard(str(path)))))
    negcam=O/(name+'-cam');negcam.mkdir(exist_ok=True)
    run(['pcb','export','gerbers','--layers','F.Cu,F.Mask,F.Paste','--output',negcam,path])
    expect_reject(name+'_native_CAM',lambda:checkcam(negcam))
bad=copy.deepcopy(g)
for q in bad['C202']['pads']:q['x']/=2
expect_reject('KEMET_C_dimension_misread_as_full_pitch',lambda:check_geom(bad))

# Physical negative: two different-net pad pairs have 0.05 mm vertical edge spacing against 0.20 mm rule.
nb=pcb.LoadBoard(str(copyboard));nf=next(f for f in nb.GetFootprints() if f.GetReference()=='FB203');nf.SetPosition(pcb.VECTOR2I(pcb.FromMM(4),pcb.FromMM(5)))
neg=O/'clearance-negative.kicad_pcb';pcb.SaveBoard(str(neg),nb);shutil.copyfile(copyboard.with_suffix('.kicad_pro'),neg.with_suffix('.kicad_pro'))
run(['pcb','drc','--format','json','--severity-all','-o',O/'clearance-negative-drc.json',neg])
nd=json.loads((O/'clearance-negative-drc.json').read_text());clear=[v for v in nd['violations'] if v['type']=='clearance']
assert clear,nd
controls.append(dict(name='native_0p05mm_different_net_clearance_against_0p20mm_rule',result='REJECTED_AS_EXPECTED',clearance_violations=len(clear),all_violation_types=dict(collections.Counter(v['type'] for v in nd['violations']))))
dump('negative-controls.json',dict(controls=controls,physical_native_DRC_proved=True))

after={str(p.relative_to(P)):sha(p) for p in watched};assert before==after
dump('input-integrity.json',dict(input_project_unchanged=True,files=before))
dump('native-command-log.json',log)
dump('result.json',dict(result='PASS_BOUNDED_INDEPENDENT_AUDIT',changed_refs=sorted(expected),assigned=215,gaps=39,ERC_violations=0,geometry_DRC_violations=0,negative_controls=len(controls),main_CAD_edited=False,production_approval=False,conditions=['Exact nominal Murata mask has no registration allowance','18um is conservative conditional local reservation, not approved six-layer copper stack','Local rectangles do not qualify continuing copper cross-section or heat removal','Paste and KEMET mask assumptions require assembly process acceptance','Actual peak/hot DCR/filter/sequence/loop/thermal and full-core-routing gates remain']))
print(json.dumps(json.loads((O/'result.json').read_text()),indent=2))

# Public reports retain explicit logical roots, never executor-specific absolute paths.
replacements=sorted([(str(P),'PROJECT_ROOT'),(str(B),'BASELINE_ROOT'),(str(O),'OUTPUT_ROOT'),(str(a.runtime.resolve()),'RUNTIME_ROOT')],key=lambda x:len(x[0]),reverse=True)
for path in O.rglob('*'):
    if path.is_file() and path.suffix in ('.json','.xml'):
        data=path.read_text()
        for src,dst in replacements:data=data.replace(src,dst)
        path.write_text(data)
