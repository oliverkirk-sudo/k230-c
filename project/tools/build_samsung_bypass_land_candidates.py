#!/usr/bin/python3
from pathlib import Path
import pcbnew as k,json,hashlib
B=Path(__file__).resolve().parents[1];D=B/'cad/verified-footprints/bypass-candidates';L=D/'CMK230_Bypass_Candidates.pretty';L.mkdir(parents=True,exist_ok=True)
parts=[dict(mpn='CL03B104KP3NNWC',gap=.25,padlength=.34,padwidth=.33,body=[.63,.33],value='100nF',pdf='samsung-CL03B104KP3NNW-specsheet.pdf',ranges=[[.22,.28],[.31,.37],[.30,.36]],source='https://product.samsungsem.com/mlcc/CL03B104KP3NNW.do'),dict(mpn='CL10B475KQ8NFQC',gap=.70,padlength=.78,padwidth=.95,body=[1.75,.95],value='4.7uF',pdf='samsung-CL10B475KQ8NFQ-specsheet.pdf',ranges=[[.65,.75],[.73,.83],[.90,1.00]],source='https://product.samsungsem.com/mlcc/CL10B475KQ8NFQ.do')]
for q in parts:
 name='Samsung_'+q['mpn']+'_MIDPOINT_LAND_DENSE_CANDIDATE';q['footprint']=name
 g,a,w=q['gap'],q['padlength'],q['padwidth'];span=g+2*a
 f=k.FOOTPRINT(None);f.SetFPID(k.LIB_ID('CMK230_Bypass_Candidates',name));f.SetReference('C**');f.Reference().SetLayer(k.F_Fab);f.Reference().SetPosition(k.VECTOR2I(0,k.FromMM(-1)));f.SetValue(q['mpn']);f.Value().SetVisible(False);f.SetAttributes(k.FP_SMD)
 for num,sgn in [(1,-1),(2,1)]:
  p=k.PAD(f);p.SetNumber(str(num));p.SetAttribute(k.PAD_ATTRIB_SMD);p.SetShape(k.PAD_SHAPE_RECT);p.SetSize(k.VECTOR2I(k.FromMM(a),k.FromMM(w)));p.SetPosition(k.VECTOR2I(k.FromMM(sgn*(g+a)/2),0));ls=k.LSET();[ls.AddLayer(z) for z in [k.F_Cu,k.F_Mask,k.F_Paste]];p.SetLayerSet(ls);p.SetLocalSolderMaskMargin(k.FromMM(.05));f.Add(p)
 def rect(width,height,layer,line):
  for aa,bb in [((-width/2,-height/2),(width/2,-height/2)),((width/2,-height/2),(width/2,height/2)),((width/2,height/2),(-width/2,height/2)),((-width/2,height/2),(-width/2,-height/2))]:
   sh=k.PCB_SHAPE();sh.SetShape(k.SHAPE_T_SEGMENT);sh.SetStart(k.VECTOR2I(k.FromMM(aa[0]),k.FromMM(aa[1])));sh.SetEnd(k.VECTOR2I(k.FromMM(bb[0]),k.FromMM(bb[1])));sh.SetLayer(layer);sh.SetWidth(k.FromMM(line));f.Add(sh)
 cw=max(span+.3,q['body'][0]+.2);ch=max(w+.3,q['body'][1]+.2);rect(cw,ch,k.F_CrtYd,.05);rect(*q['body'],k.F_Fab,.05)
 plugin=k.PCB_IO_MGR.PluginFind(k.PCB_IO_MGR.KICAD_SEXP);plugin.FootprintSave(str(L),f);back=plugin.FootprintLoad(str(L),name);pads=list(back.Pads());assert len(pads)==2
 assert {p.GetNumber() for p in pads}=={'1','2'}
 for p in pads:assert abs(k.ToMM(p.GetSize().x)-a)<1e-7 and abs(k.ToMM(p.GetSize().y)-w)<1e-7
 q['courtyard_mm']=[cw,ch];q['copper_span_mm']=span;q['intra_mask_web_mm']=g-.1;q['mask_expansion_mm']=.05;q['courtyard_margin_beyond_mask_mm']=.1;q['paste_area_ratio_at100um']=a*w/(2*(a+w)*.1);q['sha256']=hashlib.sha256((L/(name+'.kicad_mod')).read_bytes()).hexdigest()
 assert all(lo<=v<=hi for v,(lo,hi) in zip([g,a,w],q['ranges']))
(D/'source-land-validation.json').write_text(json.dumps({'status':'SOURCE_LAND_CANDIDATES_NOT_CEFF_OR_ASSEMBLY_QUALIFICATION','source_pdf_page':33,'source_location':'Samsung exact-part MLCC manual, physical page33, case/tolerance rows verified','parts':parts,'limitations':['Source land midpoint selected within recommended range; not a factory etch tolerance guarantee.','Mask+0.05mm,1:1paste and0.10mm margin beyond mask are declared assembly candidates.','Pair-specific body/lead spacing and rework clearances still govern placement.','Nominal capacitance, voltage and125C dielectric rating do not guarantee effective capacitance or local temperature.']},indent=2));print('PASS2 exact-part source-land candidates')
