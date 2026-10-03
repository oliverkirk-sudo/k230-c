#!/usr/bin/python3
"""Build a labeled gallery from actual KiCad SVG polygons, not redrawn pad geometry."""
from pathlib import Path
import copy, os, subprocess, xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[2];O=R/'recovery/logic-footprint-review/evidence';C=R/'cad/recovery-footprint-candidates'
ns='http://www.w3.org/2000/svg';E.register_namespace('',ns)
def el(name,attrs=None,text=None):
    z=E.Element('{'+ns+'}'+name,attrs or {})
    if text is not None:z.text=text
    return z
root=el('svg',{'viewBox':'0 0 1500 710','width':'1500','height':'710'})
root.append(el('rect',{'x':'0','y':'0','width':'1500','height':'710','fill':'#f5f7fa'}))
def label(x,y,text,size=20,fill='#172b45'):
    root.append(el('text',{'x':str(x),'y':str(y),'font-family':'DejaVu Sans, sans-serif','font-size':str(size),'fill':fill},text))
label(35,48,'TI DSF0006A / SN74LVC1G97DSFR',30)
label(35,83,'Actual KiCad native plots | component side | pin 1 upper-left | isolated candidate',19)
pins=[('1',-.4,-.35),('2',-.4,0),('3',-.4,.35),('4',.4,.35),('5',.4,0),('6',.4,-.35)]
panels=[('F.Cu','Copper','0.60 x 0.17 mm, R0.05','6 numbered electrical pads','#a42f37'),('F.Mask','Mask openings','0.70 x 0.27 mm, R0.10','Chosen NSMD +0.05 mm; nominal web 0.08 mm','#126954'),('F.Paste','Paste openings','0.60 x 0.15 mm, R0.05','Source example: 0.09 mm stencil','#28549b')]
for i,(layer,title,dim,desc,color) in enumerate(panels):
    left=30+i*495;cx=left+225;cy=355
    root.append(el('rect',{'x':str(left),'y':'115','width':'465','height':'440','rx':'15','fill':'white','stroke':'#d6deea'}))
    label(left+20,153,title,25,color);label(left+20,183,dim,19)
    grp=el('g',{'transform':f'translate({cx} {cy}) scale(245) translate(-5.025 -5.025)'})
    source=E.parse(O/f'native-base-{layer}.svg').getroot()
    for path in source.iter('{'+ns+'}path'):
        p=copy.deepcopy(path);p.set('style',f'fill:{color};stroke:none;');grp.append(p)
    root.append(grp)
    root.append(el('rect',{'x':str(cx-.5*245),'y':str(cy-.5*245),'width':'245','height':'245','fill':'none','stroke':'#8795aa','stroke-dasharray':'5,5','stroke-width':'1.5'}))
    for num,x,y in pins:
        root.append(el('text',{'x':str(cx+x*245),'y':str(cy+y*245+6),'text-anchor':'middle','font-family':'DejaVu Sans, sans-serif','font-size':'18','font-weight':'bold','fill':'white'},num))
    label(left+17,516,desc,16,color)
label(35,594,'Dashed outline: 1.00 mm midrange body. Maximum body: 1.05 x 1.05 mm; maximum height: 0.40 mm',19)
label(35,628,'Copper/paste dimensions: TI drawing 4220597/B (06/2022), physical PDF pp29-31. Mask offset is a project choice',18)
label(35,665,'Process unqualified. Native mask DRC misses the 0.08 mm web; independent geometry checks remain required',19,'#95382d')
svg=O/'TI_DSF_native_layer_review.svg';E.ElementTree(root).write(svg,encoding='utf-8',xml_declaration=True)
env=os.environ.copy()
for key,leaf in [('XDG_CACHE_HOME','cache'),('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data')]:env[key]=str(C/'runtime'/leaf)
p=subprocess.run(['inkscape',str(svg),'--export-type=png','--export-filename='+str(O/'TI_DSF_native_layer_review.png'),'--export-width=1800'],env=env,text=True,capture_output=True)
assert p.returncode==0,(p.stdout,p.stderr)
print(O/'TI_DSF_native_layer_review.png')
