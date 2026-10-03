#!/usr/bin/python3
"""Final bounded drawing-only recheck; no R4 writes."""
from pathlib import Path
import hashlib,json,re
import pcbnew

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
LIB=BASE/'reconstruction-r4/project/cad/recovery-bga-candidates/CMK230_Recovery_BGA_Candidates.pretty'
OLD=BASE/'restored-v12-r2_1'
checks=[];hashes={}
def sha(p):
    h=hashlib.sha256(p.read_bytes()).hexdigest();hashes[str(p.relative_to(BASE))]=h;return h
def ck(name,ok): checks.append({'check':name,'pass':bool(ok)})
def sx(text):
    stack=[];roots=[]
    for t in re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()]+',text):
        if t=='(':
            x=[];(stack[-1] if stack else roots).append(x);stack.append(x)
        elif t==')':stack.pop()
        else:stack[-1].append(json.loads(t) if t.startswith('"') else t)
    assert not stack and len(roots)==1
    return roots[0]
def kids(a,k):return [x for x in a if isinstance(x,list) and x and x[0]==k]
def rawpads(text):
    out=[]
    for m in re.finditer(r'\(pad\s',text):
        start=m.start();depth=0;quoted=False;escape=False
        for end in range(start,len(text)):
            c=text[end]
            if escape:escape=False;continue
            if c=='\\' and quoted:escape=True;continue
            if c=='"':quoted=not quoted
            if quoted:continue
            if c=='(':depth+=1
            if c==')':depth-=1
            if depth==0:out.append(text[start:end+1]);break
    return out
def xy(v):return (round(pcbnew.ToMM(v.x),6),round(pcbnew.ToMM(v.y),6))
def edges(fp,layer):
    return {(xy(g.GetStart()),xy(g.GetEnd())) for g in fp.GraphicalItems() if g.GetLayer()==layer}
def rectangle(x,y):return {((-x,-y),(x,-y)),((x,-y),(x,y)),((x,y),(-x,y)),((-x,y),(-x,-y))}

configs=[('U1','K230_390_NSMD027_ENGINEERING_ONLY',
    'cad/bga-engineering-candidates/k230-ddr-constrained/K230_Engineering.pretty',390,
    'e966f4f52f50f9939f1d93ae072eac6c764d35586e854e20e5297eed4404c2cb',
    'b9fff5d510772b7c98865cae0d2f7d5119b8e9f1be229223d106bbbace78a9e3'),
    ('U3','MTFC16GAPALBH_AAT_BH153_NSMD030_ENGINEERING_ONLY',
    'cad/bga-engineering-candidates/bh153-sparse-trial/BH153_Engineering.pretty',153,
    '2d80cba28c836720179e842b70d5b71bf92c8c4fc0759a16b8862244411507cf',
    'aff22c7309212fc23b34a65be1fdb34148a23cb2c8a1ddf95a0f0d32e4af2f6f')]
for ref,name,oldpath,count,oldhash,newhash in configs:
    old=OLD/oldpath/(name+'.kicad_mod');new=LIB/(name+'.kicad_mod')
    ck(ref+' original legacy source hash unchanged',sha(old)==oldhash)
    ck(ref+' revised drawing hash matches reviewed revision',sha(new)==newhash)
    a=old.read_text();b=new.read_text()
    ck(ref+' all pad subtrees byte-identical',len(rawpads(a))==count and rawpads(a)==rawpads(b))
    oldtree=sx(a);newtree=sx(b)
    ck(ref+' all non-line footprint subtrees unchanged',[x for x in oldtree if not isinstance(x,list) or x[0]!='fp_line']==[x for x in newtree if not isinstance(x,list) or x[0]!='fp_line'])
    fp=pcbnew.FootprintLoad(str(LIB),name);pads=list(fp.Pads())
    ck(ref+' native physical-pad count and front layers unchanged',len(pads)==count and all(p.IsOnLayer(pcbnew.F_Cu) and p.IsOnLayer(pcbnew.F_Mask) and p.IsOnLayer(pcbnew.F_Paste) and not p.IsOnLayer(pcbnew.B_Cu) for p in pads))
    if ref=='U1':
        ck('K230 native A1 remains physically absent','A1' not in {p.GetNumber() for p in pads})
        cue=((-6.55,-5.85),(-5.85,-6.55))
        oldfp=pcbnew.FootprintLoad(str(old.parent),name)
        ck('K230 only one native F.Fab diagonal added',edges(fp,pcbnew.F_Fab)==edges(oldfp,pcbnew.F_Fab)|{cue})
        ck('K230 native courtyard unchanged',edges(fp,pcbnew.F_CrtYd)==edges(oldfp,pcbnew.F_CrtYd))
    else:
        ck('BH153 native full maximum-body rectangle plus inner A1 cue',edges(fp,pcbnew.F_Fab)==rectangle(5.8,6.55)|{((-5.8,-5.85),(-5.1,-6.55))})
        ck('BH153 native courtyard is complete 12.1 by 13.6 mm rectangle',edges(fp,pcbnew.F_CrtYd)==rectangle(6.05,6.8))
initial=json.loads((HERE/'independent-review.json').read_text())
fw=LIB/'Micron_FW200_NSMD030_ENGINEERING_ONLY.kicad_mod'
ck('FW200 complete file unchanged from initial source/native/CAM review',sha(fw)==initial['input_sha256'][str(fw.relative_to(BASE))])
pdf=BASE/'private-sources/micron-emmc.pdf'
ck('Fresh eMMC PDF hash matches exact recovered source',sha(pdf)=='52ad8018f63554d3e34f970b1516e488543c6a25bd144bcbf33d666fa2a82d71')
result={'date_utc':'2026-10-03','status':'PASS_FINAL_DRAWING_ONLY_ADDENDUM' if all(c['pass'] for c in checks) else 'FAIL',
    'check_count':len(checks),'checks':checks,'failures':[c for c in checks if not c['pass']],
    'fresh_source_visual_review':{'document':'Micron automotive e.MMC Rev. G 10/18 EN','page':11,'figure':5,
        'visually_inspected':True,'body_nominal_mm':[11.5,13.0],'body_tolerance_each_axis_mm':.1,'body_maximum_mm':[11.6,13.1],
        'orientation':'Top-view A1 corner upper-left; ball-side mechanical columns reversed. The added diagonal is an engineering orientation cue, not an exact depiction of the package marking.'},
    'result':'All 743 electrical lands and their mask/paste definitions remain unchanged. Revised BGA geometry imports natively. Initial FW200 source and CAM findings remain valid. Original legacy source footprints unchanged.',
    'drawing_changes':{'BH153':'Full F.Fab maximum-body rectangle 11.6 x 13.1 mm; courtyard 12.1 x 13.6 mm; inside upper-left orientation cue.',
                       'K230':'One upper-left F.Fab corner cue added; absent A1 is not converted to a land.'},
    'boundary':'Conditional footprint geometry only. No new stack, via/HDI, land-pattern, stencil, assembly, thermal, full-board fit, or routing qualification. No native DRC rerun in this addendum.',
    'input_sha256':hashes,'initial_review_preserved':'independent-review.json'}
(HERE/'final-drawing-addendum.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'status':result['status'],'checks':len(checks),'failures':result['failures']},indent=2))
