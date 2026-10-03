#!/usr/bin/python3
"""Render original review graphics from native KiCad exports; no vendor-page copies."""
from pathlib import Path
import copy,os,re,subprocess,xml.etree.ElementTree as E
R=Path(__file__).resolve().parents[3];O=R/'recovery/logic-footprint-review/nexperia-archival/evidence';C=R/'cad/recovery-footprint-candidates/nexperia-archival'
NS='http://www.w3.org/2000/svg';E.register_namespace('',NS)
def el(tag,attrs=None,text=None):
 x=E.Element('{'+NS+'}'+tag,attrs or {})
 if text is not None:x.text=text
 return x
def canvas(w,h):
 root=el('svg',{'viewBox':f'0 0 {w} {h}','width':str(w),'height':str(h)});root.append(el('rect',{'width':str(w),'height':str(h),'fill':'#f5f7fa'}));return root
def label(root,x,y,text,size=20,color='#172b45'):
 root.append(el('text',{'x':str(x),'y':str(y),'font-family':'DejaVu Sans, sans-serif','font-size':str(size),'fill':color},text))
def render(root,name,width=1800):
 path=O/(name+'.svg');E.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)
 env=os.environ.copy()
 for key,leaf in [('XDG_CACHE_HOME','cache'),('XDG_CONFIG_HOME','config'),('XDG_DATA_HOME','data')]:env[key]=str(C/'runtime'/leaf)
 p=subprocess.run(['inkscape',str(path),'--export-type=png','--export-filename='+str(O/(name+'.png')),'--export-width='+str(width)],env=env,text=True,capture_output=True);assert p.returncode==0,p.stderr
 print(O/(name+'.png'))
pins=[('1',-.525,-.2),('2',-.575,.2),('3',-.4,.775),('4',0,.775),('5',.4,.775),('6',.575,.2),('7',.575,-.2),('8',.4,-.775),('9',0,-.775),('10',-.4,-.775)]
root=canvas(1500,860);label(root,35,48,'NXP SOT1160-1 / 74AUP2G97GUX',30);label(root,35,83,'Archival manufacturer drawing pixels + current primary text cross-check | component-side native KiCad plots',18)
panels=[('F.Cu','Copper','10 numbered pads; long pin 1 retained','#a42f37'),('F.Mask','Mask openings','Source +0.0625 mm; 0.055 mm web','#126954'),('F.Paste','Paste openings','Source -0.02 mm per side; 0.10 mm stencil','#28549b')]
for i,(layer,title,desc,color) in enumerate(panels):
 left=30+495*i;cx=left+225;cy=405;scale=190
 root.append(el('rect',{'x':str(left),'y':'115','width':'465','height':'540','rx':'15','fill':'white','stroke':'#d6deea'}));label(root,left+20,153,title,25,color);label(root,left+18,184,desc,17,color)
 group=el('g',{'transform':f'translate({cx} {cy}) scale({scale}) translate(-5.025 -5.025)'})
 source=E.parse(O/f'native-base-{layer}.svg').getroot()
 for p in source.iter():
  if p.tag.split('}')[-1] in ['path','polygon','rect','circle','ellipse','polyline']:
   q=copy.deepcopy(p);q.set('style',f'fill:{color};stroke:none');group.append(q)
 root.append(group);root.append(el('rect',{'x':str(cx-.7*scale),'y':str(cy-.9*scale),'width':str(1.4*scale),'height':str(1.8*scale),'fill':'none','stroke':'#8795aa','stroke-dasharray':'5,5','stroke-width':'1.4'}))
 for n,x,y in pins:root.append(el('text',{'x':str(cx+x*scale),'y':str(cy+y*scale+5),'text-anchor':'middle','font-family':'DejaVu Sans, sans-serif','font-size':'16','font-weight':'bold','fill':'white'},n))
 label(root,left+18,630,'VCC = pin 9; actual package GND = pin 4',17,color)
label(root,35,698,'Pin 1: 0.65 x 0.22 mm. Other side lands: 0.55 x 0.22 mm. Top/bottom: 0.22 x 0.55 mm',20)
label(root,35,735,'Dashed body: 1.40 x 1.80 mm. Maximum with excluded protrusions: 1.65 x 2.05 mm; height max 0.50 mm',19)
label(root,35,773,'Outline: 2009-12-29. Reflow: copyright 2010, no printed issue date. Current PDF identity is not claimed',18)
label(root,35,816,'Process unqualified: native 0.075 mm mask-web setting merges these openings. Inspect the actual mask Gerber',19,'#95382d')
render(root,'NXP_native_layer_review')

root=canvas(1250,760);label(root,35,48,'NXP mask export changes with the global minimum web',29);label(root,35,83,'Same source-exact footprint and +0.0625 mm mask expansion in both native fixtures',20)
for i,(tag,file,title,subtitle,color) in enumerate([('base','NXP_Geometry_QA_ONLY-F_Mask.gts','0.05 mm setting','10 separate source-exact openings','#126954'),('mask-0075','NXP_Process_020_0075-F_Mask.gts','0.075 mm setting','1 merged region; source geometry rejected','#a42f37')]):
 left=30+i*620;cx=left+285;cy=392;root.append(el('rect',{'x':str(left),'y':'115','width':'590','height':'530','rx':'15','fill':'white','stroke':'#d6deea'}));label(root,left+20,154,title,25,color);label(root,left+20,184,subtitle,21,color)
 text=(O/('gerbers-'+tag)/file).read_text();group=el('g',{'transform':f'translate({cx} {cy}) scale(175) translate(-5 -5)'})
 regions=re.findall(r'G36\*(.*?)G37\*',text,re.S)
 for region in regions:
  pts=[(int(x)/1e6,-int(y)/1e6) for x,y in re.findall(r'X(-?\d+)Y(-?\d+)D0[12]\*',region)]
  d='M '+' L '.join(f'{x},{y}' for x,y in pts)+' Z';group.append(el('path',{'d':d,'fill':color,'fill-rule':'evenodd','stroke':'none'}))
 root.append(group);label(root,left+20,622,'Native DRC reports no mask bridge in either case',18,color)
label(root,35,679,'Independent geometry rejects a 0.075 mm requirement against the 0.055 mm nominal source web',22)
label(root,35,722,'The merged output is a diagnostic control. No gang-mask, registration or assembly process approval is implied',18,'#95382d')
render(root,'NXP_mask_export_control',1600)
