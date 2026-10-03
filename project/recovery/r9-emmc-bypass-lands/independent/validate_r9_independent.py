#!/usr/bin/env python3
"""Bounded independent R9 audit; no mutation of either input project.
Run with Python 3 and installed KiCad CLI + pcbnew bindings.
"""
import argparse, collections, copy, datetime, hashlib, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path
import xml.etree.ElementTree as ET
_bootstrap = tempfile.TemporaryDirectory(prefix='r9-pcbnew-')
for _key, _leaf in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data')]:
    os.environ[_key] = str(Path(_bootstrap.name)/_leaf)
    Path(os.environ[_key]).mkdir()
try:
    import pcbnew as pcb
except ImportError:
    sys.path.append('/usr/lib/python3/dist-packages')
    import pcbnew as pcb

REFS = ['C64', 'C65', 'C69', 'C70', 'C71', 'C72']
PREFIX = 'CMK230_EMMC_Bypass_Candidates:'
LARGE = 'Murata_GRM188R71A225_ReflowMid_SOURCE_CANDIDATE'
SMALL = 'Murata_GRM155R71C104_ReflowMid_SOURCE_CANDIDATE'
EXPECT = {r:PREFIX+(LARGE if r in ['C64','C69','C71'] else SMALL) for r in REFS}
EXPECTED_NET = {'C64':'EMMC_VDDIM','C65':'EMMC_VDDIM','C69':'VEMMC_IO','C70':'VEMMC_IO','C71':'VDD_3V3','C72':'VDD_3V3'}
PHYS = Path('cad/recovery-physical-candidate')
REV = Path('recovery/r9-emmc-bypass-lands')
LIB = Path('cad/recovery-emmc-bypass-candidates/CMK230_EMMC_Bypass_Candidates.pretty')
GEOM = {LARGE:dict(pad=[.65,.70],centre=.675,body=[1.7,.9],court=[2.6,1.5],a=[.6,.8],b=[.6,.7],c=[.6,.8]),SMALL:dict(pad=[.4,.5],centre=.4,body=[1.05,.55],court=[1.8,1.2],a=[.3,.5],b=[.35,.45],c=[.4,.6])}

def require(ok,msg):
    if not ok: raise AssertionError(msg)

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,obj): p.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def sx(text):
    tokens=re.findall(r'"(?:\\.|[^"\\])*"|[()]|[^\s()]+',text); stack=[];root=None
    for t in tokens:
        if t=='(': stack.append([])
        elif t==')':
            v=stack.pop()
            if stack: stack[-1].append(v)
            else: require(root is None,'multiple roots');root=v
        else: stack[-1].append(json.loads(t) if t.startswith('"') else t)
    require(not stack and root is not None,'invalid s-expression');return root

def nodes(a,name): return [x for x in a if isinstance(x,list) and x and x[0]==name]
def node(a,name): return next(iter(nodes(a,name)),None)
def props(sym): return {p[1]:p[2] for p in nodes(sym,'property')}
def canonical_xml(e): return [e.tag,sorted(e.attrib.items()),(e.text or '').strip(),[canonical_xml(ch) for ch in e]]

def graph(path):
    r=ET.parse(path).getroot();comps={c.get('ref'):canonical_xml(c) for c in r.findall('./components/comp')}; bindings={}
    for n in r.findall('./nets/net'):
        attrs=tuple(sorted((k,v) for k,v in n.attrib.items() if k!='code'))
        for nd in n.findall('node'):
            key=(nd.get('ref'),nd.get('pin'));require(key not in bindings,'duplicate binding '+str(key));bindings[key]=(attrs,tuple(sorted(nd.attrib.items())))
    return r,comps,bindings

def net_name(bindings,ref,pin):return dict(bindings[(ref,pin)][0])['name']
def compare_graph(baseline,candidate):
    br,bc,bn=baseline;cr,cc,cn=candidate
    require(set(bc)==set(cc),'component references changed')
    for ref in bc:
        b=copy.deepcopy(br.find("./components/comp[@ref='%s']"%ref)); c=copy.deepcopy(cr.find("./components/comp[@ref='%s']"%ref))
        if ref in EXPECT:
            require((b.findtext('footprint') or '')=='','baseline footprint was assigned '+ref)
            require(c.findtext('footprint')==EXPECT[ref],'wrong footprint '+ref)
            require(c.findtext("fields/field[@name='Footprint']")==EXPECT[ref],'wrong footprint field '+ref)
            for e in [b,c]:
                for x in list(e):
                    if x.tag=='footprint':e.remove(x)
                fs=e.find('fields')
                if fs is not None:
                    for f in list(fs):
                        if f.get('name')=='Footprint':fs.remove(f)
        require(canonical_xml(b)==canonical_xml(c),'component attributes changed '+ref)
    require(bn==cn,'net/node attributes changed')
    require(len(cc)==254 and len(cn)==1509,'unexpected graph size')
    require(len({net_name(cn,*k) for k in cn})==457,'unexpected distinct nets')
    for ref,net in EXPECTED_NET.items():
        require(net_name(cn,ref,'1')==net,'wrong role '+ref)
        require(net_name(cn,ref,'2')=='GND','wrong return '+ref)
    require(net_name(cn,'R561','1')=='VDD1P8' and net_name(cn,'R561','2')=='VEMMC_IO','VCCQ feed changed')
    assigned=sum(bool(c.findtext('footprint')) for c in cr.findall('./components/comp'))
    require(assigned==221,'assignment count changed')
    return {'components':254,'bindings':1509,'distinct_nets':457,'assigned':assigned,'gaps':254-assigned,'footprint_changes':REFS}

def sch_compare(b,c):
    files=sorted((b/PHYS).glob('*.kicad_sch'));require({p.name for p in files}=={p.name for p in (c/PHYS).glob('*.kicad_sch')},'schematic file set changed')
    changes=[]; states={}
    for bf in files:
        cf=c/PHYS/bf.name;bt=sx(bf.read_text());ct=sx(cf.read_text())
        for sym in nodes(ct,'symbol'):
            p=props(sym);r=p.get('Reference');
            if r and not r.startswith('#'):
                states[r]={k:node(sym,k)[1] if node(sym,k) else None for k in ['in_bom','on_board','dnp']}
        # Compare the full tree after changing only the six authorized fields in a baseline copy.
        expected=copy.deepcopy(bt)
        for sym in nodes(expected,'symbol'):
            r=props(sym).get('Reference')
            if r in EXPECT:
                f=next(x for x in nodes(sym,'property') if x[1]=='Footprint');require(f[2]=='','baseline schematic already assigned');f[2]=EXPECT[r];changes.append(r)
        if bf.name=='CMK230_Core_REVIEW.kicad_sch':
            rv=node(node(expected,'title_block'),'rev');require(rv[1]=='RCV-R8','unexpected baseline rev');rv[1]='RCV-R9'
        require(expected==ct,'unauthorized schematic tree change '+bf.name)
    require(sorted(changes)==REFS,'not exactly six schematic footprint changes')
    require(len(states)==254,'schematic instance count')
    for ref in ['JP1','R45','R47','R528']:require(states[ref]['dnp']=='yes','DNP changed '+ref)
    return {'files_compared':len(files),'physical_component_references':len(states),'states':states,'allowed_noncomponent_change':'Root title revision RCV-R8 to RCV-R9'}

def footprint_check(path,name):
    a=sx(path.read_text());g=GEOM[name];require(a[:2]==['footprint',name],'footprint identity')
    pads=nodes(a,'pad');copper=[p for p in pads if 'F.Cu' in node(p,'layers')[1:]];paste=[p for p in pads if 'F.Paste' in node(p,'layers')[1:]]
    require(len(pads)==4 and len(copper)==2 and len(paste)==2,'pad counts')
    expected=sorted([(-g['centre'],0,*g['pad']),(g['centre'],0,*g['pad'])])
    def geom(ps):return sorted(tuple(round(float(x),6) for x in node(p,'at')[1:3]+node(p,'size')[1:3]) for p in ps)
    require(geom(copper)==expected and geom(paste)==expected,'copper or paste dimensions '+name)
    require({p[1] for p in copper}=={'1','2'} and all(p[1]=='' for p in paste),'pad identities')
    require(all(p[3]=='rect' and node(p,'layers')[1:]==['F.Cu','F.Mask'] and float(node(p,'solder_mask_margin')[1])==.05 for p in copper),'copper layers/mask choices')
    require(all(p[3]=='rect' and node(p,'layers')[1:]==['F.Paste'] for p in paste),'separate 1:1 paste choices')
    rectangles={node(x,'layer')[1]:x for x in nodes(a,'fp_rect')}
    for layer,key in [('F.Fab','body'),('F.CrtYd','court')]:
        rect=rectangles[layer];start=list(map(float,node(rect,'start')[1:]));end=list(map(float,node(rect,'end')[1:]));wh=[round(end[i]-start[i],6) for i in range(2)]
        require(wh==g[key],layer+' extents')
    actual={'a':2*g['centre']-g['pad'][0],'b':g['pad'][0],'c':g['pad'][1]}
    require(all(g[k][0]-1e-8<=actual[k]<=g[k][1]+1e-8 for k in actual),'outside source range')
    return {'copper_geometry_mm':actual,'pad_centres_X_mm':[-g['centre'],g['centre']],'max_body_mm':g['body'],'engineering_courtyard_mm':g['court'],'mask_expansion_mm':.05,'separate_paste_1_to_1':True,'source_row_applies':'L/W tolerance within +/-0.10 mm','qualification':'Copper source ranges only; mask, paste and courtyard remain unqualified engineering choices'}

def gerber(path):
    text=path.read_text();require('%MOMM*%' in text and '%FSLAX46Y46*%' in text,'unsupported Gerber format');aps={}
    for n,kind,param in re.findall(r'%ADD(\d+)(R|RoundRect),([^*]+)\*%',text):
        vals=list(map(float,param.split('X')))
        if kind=='R':dim=vals[:2]
        else:
            r=vals[0];xs=vals[1:9:2];ys=vals[2:9:2];dim=[max(xs)-min(xs)+2*r,max(ys)-min(ys)+2*r]
        aps[int(n)]=[round(v,6) for v in dim]
    d=None;flashes=[]
    for line in text.splitlines():
        m=re.fullmatch(r'D(\d+)\*',line)
        if m:d=int(m[1])
        m=re.fullmatch(r'X(-?\d+)Y(-?\d+)D03\*',line)
        if m:require(d in aps,'undefined aperture');flashes.append((int(m[1])/1e6,int(m[2])/1e6,*aps[d]))
    require(len(flashes)==4,'expected four isolated-fixture flashes')
    return sorted(flashes)

def reject(test):
    try:test()
    except AssertionError:return True
    return False

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--baseline',type=Path,required=True);ap.add_argument('--candidate',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--kicad-cli',default='kicad-cli');args=ap.parse_args();b=args.baseline.resolve();c=args.candidate.resolve();o=args.output.resolve();o.mkdir(parents=True,exist_ok=True)
    require(b!=c and not o.is_relative_to(b) and not o.is_relative_to(c),'output must be outside the input projects')
    before={str(p.relative_to(c)):sha(p) for d in [c/PHYS,c/LIB,c/REV] for p in d.glob('*') if p.is_file() and p.suffix in ['.kicad_sch','.kicad_mod','.kicad_pcb','.kicad_pro','.xml']}
    base=graph(b/PHYS/'master.xml');saved=graph(c/PHYS/'master.xml');result=compare_graph(base,saved);schemas=sch_compare(b,c);write(o/'population-states.json',schemas)
    require((b/'data/candidate-bom.csv').read_bytes()==(c/'data/candidate-bom.csv').read_bytes(),'candidate BOM changed');result['bom_identical']=True
    geom={name:footprint_check(c/LIB/(name+'.kicad_mod'),name) for name in GEOM};write(o/'footprint-geometry.json',geom)
    # Ensure saved fixture uses these exact source-derived geometries and synthetic nets.
    fixture=c/REV/'EMMC_BYPASS_LANDS_GEOMETRY_ONLY.kicad_pcb';board=pcb.LoadBoard(str(fixture));fps={fp.GetReference():fp for fp in board.GetFootprints()};require(set(fps)=={'C64','C65'},'isolated fixture members')
    for ref,name in [('C64',LARGE),('C65',SMALL)]:
        fp=fps[ref];require(str(fp.GetFPID().GetLibItemName())==name,'fixture footprint name')
        require(abs(fp.GetOrientationDegrees())<1e-8,'fixture rotation not expected')
        for layer in [pcb.F_Cu,pcb.F_Paste]:
            tuples=[]
            for q in fp.Pads():
                if q.IsOnLayer(layer):
                    d=q.GetPosition()-fp.GetPosition();tuples.append(tuple(round(pcb.ToMM(x),6) for x in [d.x,d.y,q.GetSize().x,q.GetSize().y]))
                    if layer==pcb.F_Cu:require(q.GetNetname()==ref+'_'+q.GetNumber(),'fixture net is not synthetic unique')
            require(sorted(tuples)==sorted([(-GEOM[name]['centre'],0,*GEOM[name]['pad']),(GEOM[name]['centre'],0,*GEOM[name]['pad'])]),'fixture pad geometry mismatch')
    cam={};expected_cam={'F_Cu':[(4.325,-5,.65,.7),(5.675,-5,.65,.7),(12.6,-5,.4,.5),(13.4,-5,.4,.5)],'F_Paste':[(4.325,-5,.65,.7),(5.675,-5,.65,.7),(12.6,-5,.4,.5),(13.4,-5,.4,.5)],'F_Mask':[(4.325,-5,.75,.8),(5.675,-5,.75,.8),(12.6,-5,.5,.6),(13.4,-5,.5,.6)]}
    exts={'F_Cu':'gtl','F_Paste':'gtp','F_Mask':'gts'}
    for layer,expected in expected_cam.items():
        f=c/REV/'native-cam'/('EMMC_BYPASS_LANDS_GEOMETRY_ONLY-'+layer+'.'+exts[layer]);got=gerber(f);require(got==sorted(expected),'saved CAM dimensions '+layer);cam[layer]={'saved_flashes':got,'sha256':sha(f)}
    controls={}
    for ref,bad in [('C64','VEMMC_IO'),('C69','VDD_3V3'),('C71','EMMC_VDDIM')]:
        badgraph=copy.deepcopy(saved);r=badgraph[0];oldnet=next(n for n in r.findall('./nets/net') if n.find("node[@ref='%s'][@pin='1']"%ref) is not None);nd=oldnet.find("node[@ref='%s'][@pin='1']"%ref);oldnet.remove(nd);dest=next(n for n in r.findall('./nets/net') if n.get('name')==bad);dest.append(nd)
        # Recreate the graph from the mutated XML, exercising the full graph comparator.
        tmp=o/('negative-'+ref+'-rail.xml');ET.ElementTree(r).write(tmp,encoding='unicode');controls[ref+'_rail_mixup_rejected']=reject(lambda:compare_graph(base,graph(tmp)));tmp.unlink()
    for ref,tag,attr,val in [('C69','value',None,'3.3uF'),('C65','property','dnp','')]:
        r=copy.deepcopy(saved[0]);comp=r.find("./components/comp[@ref='%s']"%ref)
        if tag=='value':comp.find('value').text=val
        else:ET.SubElement(comp,'property',{'name':attr,'value':val})
        tmp=o/('negative-'+ref+'-'+tag+'.xml');ET.ElementTree(r).write(tmp,encoding='unicode');controls[ref+'_'+tag+'_change_rejected']=reject(lambda:compare_graph(base,graph(tmp)));tmp.unlink()
    # Full source-geometry checker rejects a concrete wrong copper size.
    text=(c/LIB/(LARGE+'.kicad_mod')).read_text().replace('(size 0.65 0.7)','(size 0.4 0.5)',1);tmp=o/'negative-land.kicad_mod';tmp.write_text(text);controls['wrong_copper_size_rejected']=reject(lambda:footprint_check(tmp,LARGE));tmp.unlink()
    require(all(controls.values()),'a graph or geometry negative control escaped')
    logs=[]
    with tempfile.TemporaryDirectory(prefix='r9-independent-') as td:
        t=Path(td);env=os.environ.copy();env.update({'XDG_CONFIG_HOME':str(t/'config'),'XDG_CACHE_HOME':str(t/'cache'),'XDG_DATA_HOME':str(t/'data'),'TZ':'UTC'})
        for key in ['XDG_CONFIG_HOME','XDG_CACHE_HOME','XDG_DATA_HOME']:Path(env[key]).mkdir()
        def clean(s):
            for prefix,label in [(str(b),'${BASELINE}'),(str(c),'${CANDIDATE}'),(str(o),'${OUTPUT}'),(str(t),'${RUNTIME}')]:s=s.replace(prefix,label)
            return s
        def run(cmd):
            z=subprocess.run([args.kicad_cli]+list(map(str,cmd)),capture_output=True,text=True,env=env,timeout=90);logs.append({'args':clean(' '.join(map(str,cmd))),'returncode':z.returncode,'stdout':clean(z.stdout),'stderr':clean(z.stderr)});require(z.returncode in [0,5],'native command failed '+z.stdout+z.stderr);return z
        fresh=t/'fresh-master.xml';run(['sch','export','netlist','--format','kicadxml','-o',fresh,c/PHYS/'CMK230_Core_REVIEW.kicad_sch']);compare_graph(base,graph(fresh));require(graph(fresh)[1:]==saved[1:],'fresh/saved graph mismatch')
        (o/'fresh-master.xml').write_text(clean(fresh.read_text()))
        erc=t/'erc.json';run(['sch','erc','--format','json','--severity-all','-o',erc,c/PHYS/'CMK230_Core_REVIEW.kicad_sch']);er=json.loads(erc.read_text());errs=[v for s in er['sheets'] for v in s['violations']];require(not errs,'fresh ERC violations');(o/'fresh-erc.json').write_text(clean(erc.read_text()))
        # Copy the fixture and project rules; all save/export mutations occur in the copy.
        fb=t/fixture.name;shutil.copy2(fixture,fb);shutil.copy2(fixture.with_suffix('.kicad_pro'),fb.with_suffix('.kicad_pro'));shutil.copy2(c/REV/'fp-lib-table',t/'fp-lib-table')
        # Native DRC library comparisons must resolve copied candidate libraries.
        table=(t/'fp-lib-table').read_text().replace('${KIPRJMOD}/../../cad/recovery-emmc-bypass-candidates',str(c/'cad/recovery-emmc-bypass-candidates'));(t/'fp-lib-table').write_text(table)
        drc=t/'fixture-drc.json';run(['pcb','drc','--format','json','--severity-all','--exit-code-violations','-o',drc,fb]);dr=json.loads(drc.read_text());require(not dr['violations'] and not dr['unconnected_items'],'fresh fixture DRC');(o/'fresh-fixture-drc.json').write_text(clean(drc.read_text()))
        freshcam=t/'cam';freshcam.mkdir();run(['pcb','export','gerbers','--layers','F.Cu,F.Paste,F.Mask','-o',str(freshcam)+'/',fb])
        for layer,expected in expected_cam.items():
            f=freshcam/('EMMC_BYPASS_LANDS_GEOMETRY_ONLY-'+layer+'.'+exts[layer]);require(gerber(f)==sorted(expected),'fresh CAM dimensions '+layer);cam[layer]['fresh_matches_saved']=True
            dst=o/'native-cam';dst.mkdir(exist_ok=True);(dst/f.name).write_text(clean(f.read_text()))
        neg=pcb.LoadBoard(str(fb));fp=next(x for x in neg.GetFootprints() if x.GetReference()=='C64');q=next(q for q in fp.Pads() if q.GetNumber()=='2');q.SetPosition(pcb.VECTOR2I(fp.GetPosition().x+pcb.FromMM(.075),fp.GetPosition().y));nf=t/'NEGATIVE_ACTUAL_CLEARANCE_010.kicad_pcb';pcb.SaveBoard(str(nf),neg);shutil.copy2(fb.with_suffix('.kicad_pro'),nf.with_suffix('.kicad_pro'));nd=t/'negative-clearance-drc.json';ret=run(['pcb','drc','--format','json','--severity-all','--exit-code-violations','-o',nd,nf]);nr=json.loads(nd.read_text());clearances=[v for v in nr['violations'] if v.get('type')=='clearance'];require(clearances and ret.returncode==5,'actual copper clearance defect escaped DRC');controls['actual_0p10mm_clearance_rejected_by_0p20mm_rule']=True
        (o/'negative-clearance-drc.json').write_text(clean(nd.read_text()));(o/nf.name).write_text(clean(nf.read_text()));shutil.copy2(nf.with_suffix('.kicad_pro'),o/nf.with_suffix('.kicad_pro').name)
        result['native']={'kicad_version':pcb.Version(),'ERC_violations':len(errs),'fixture_DRC_violations':len(dr['violations']),'fixture_unconnected':len(dr['unconnected_items']),'negative_clearance_DRC_returncode':ret.returncode,'negative_clearance_violations':len(clearances)}
    after={rel:sha(c/rel) for rel in before};require(before==after,'input project CAD mutated')
    result.update({'status':'PASS bounded independent audit','checked_at_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'input_paths':{'baseline':'${BASELINE}','candidate':'${CANDIDATE}'},'input_cad_unchanged':True,'source_range_and_body_applicability':'Verified against the prior manufacturer-authored exact-part review: GRM188 L/W tolerance +/-0.1mm; GRM155 +/-0.05mm, both within the +/-0.10mm reflow rows. Max body outlines cover package tolerances.','negative_controls':controls,'scope_limits':['isolated geometry fixture, not module placement','no effective-capacitance or combined hot/bias/aging qualification','no thermal or mechanical fit proof','mask, paste and courtyard are unqualified choices','JLC MOQ1 remains unverified']})
    write(o/'cam-verification.json',cam);write(o/'native-command-log.json',logs);write(o/'input-cad-sha256.json',before);write(o/'independent-review.json',result)
    write(o/'artifact-sha256.json',{str(p.relative_to(o)):sha(p) for p in sorted(o.rglob('*')) if p.is_file() and p.name!='artifact-sha256.json' and '__pycache__' not in p.parts})
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
