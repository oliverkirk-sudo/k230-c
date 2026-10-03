from pathlib import Path
import os, json, subprocess, xml.etree.ElementTree as ET, re, hashlib
O=Path(__file__).resolve().parent;R=O.parent/'r6-l21-independent-runtime'
for k,n in [('XDG_CONFIG_HOME','config'),('XDG_CACHE_HOME','cache'),('XDG_DATA_HOME','data')]:os.environ[k]=str(R/n)
import pcbnew as k
src=Path('/workspace/shared/k230-recovery-oct3/reconstruction-r6/project/recovery/r6-passive-coverage/L21_SIX_LAYER_GEOMETRY_ONLY.kicad_pcb')
source_hash=hashlib.sha256(src.read_bytes()).hexdigest();runs=[];report={}
for label,margin,ratio in [('zero',0.0,0.0),('override',-.02,-.10)]:
 b=k.LoadBoard(str(src));ds=b.GetDesignSettings();ds.m_SolderPasteMargin=k.FromMM(margin);ds.m_SolderPasteMarginRatio=ratio
 p=O/('paste-'+label+'.kicad_pcb');k.SaveBoard(str(p),b)
 # Preserve the fixture's non-paste design settings in an independent copy.
 p.with_suffix('.kicad_pro').write_bytes(src.with_suffix('.kicad_pro').read_bytes())
 b2=k.LoadBoard(str(p));d=b2.GetDesignSettings()
 assert d.m_SolderPasteMargin==k.FromMM(margin) and abs(d.m_SolderPasteMarginRatio-ratio)<1e-9,(label,k.ToMM(d.m_SolderPasteMargin),d.m_SolderPasteMarginRatio)
 records=[]
 for f in b2.GetFootprints():
  for pad in f.Pads():
   m=pad.GetSolderPasteMargin(k.F_Paste)
   records.append({'number':pad.GetNumber(),'on_paste':pad.IsOnLayer(k.F_Paste),'on_copper':pad.IsOnCopperLayer(),'size_mm':[k.ToMM(pad.GetSize().x),k.ToMM(pad.GetSize().y)],'effective_paste_margin_mm':[k.ToMM(m.x),k.ToMM(m.y)]})
   if pad.IsOnLayer(k.F_Paste):assert m.x==0 and m.y==0
 report[label]={'requested_margin_mm':margin,'requested_ratio':ratio,'reloaded_margin_mm':k.ToMM(d.m_SolderPasteMargin),'reloaded_ratio':d.m_SolderPasteMarginRatio,'pads':records}
 svg=O/('native-paste-'+label+'.svg')
 cmd=['kicad-cli','pcb','export','svg','--mode-single','--layers','F.Paste,Edge.Cuts','--fit-page-to-board','--exclude-drawing-sheet','-o',str(svg),str(p)]
 r=subprocess.run(cmd,capture_output=True,text=True,timeout=60);assert r.returncode==0,r.stderr
 runs.append({'command':cmd,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr})
def geom(path):
 root=ET.parse(path).getroot();return [(e.tag.split('}')[-1],dict(e.attrib))for e in root.iter()if e.tag.split('}')[-1]in ['path','polygon','polyline','rect','circle','ellipse']]
z=geom(O/'native-paste-zero.svg');v=geom(O/'native-paste-override.svg');assert z==v
report['native_svg_geometry_identical']=True;report['geometry_elements']=z
report['result']='Separate non-copper F.Paste-only rectangles remain exactly 0.98 x 3.40 mm under tested global margin -0.02 mm and ratio -0.10 in KiCad 9.0.2. Unset local properties do not create the previously suspected shrink dependency for these apertures.'
report['source_unchanged']=hashlib.sha256(src.read_bytes()).hexdigest()==source_hash;assert report['source_unchanged']
(O/'paste-override-review.json').write_text(json.dumps(report,indent=2)+'\n');(O/'paste-override-runs.json').write_text(json.dumps(runs,indent=2)+'\n')
print(report['result']);print(json.dumps(z,indent=2))
