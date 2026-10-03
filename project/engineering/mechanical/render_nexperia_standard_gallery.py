#!/usr/bin/python3
"""Render the actual native footprint layer geometry for visual review."""
from pathlib import Path
import pcbnew as k
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
R=Path(__file__).resolve().parents[2];M=R/'engineering/mechanical';L=R/'cad/verified-footprints/nexperia-standard-candidate/CMK230_Nexperia_Standard_Candidates.pretty'
fig,axes=plt.subplots(2,3,figsize=(12,8.6),layout='constrained')
for row,(name,label)in enumerate([('Nexperia_SOT353-1_AUP1G17_06_DrawingVerified_CANDIDATE','SOT353-1 / U91, U93'),('Nexperia_SOT363-2_AUP1G97_DrawingVerified_CANDIDATE','SOT363-2 / U92, U94')]):
 fp=k.FootprintLoad(str(L),name)
 for col,(layer,title,color)in enumerate([(k.F_Cu,'Copper 0.75 × 0.40','#b66b12'),(k.F_Mask,'Mask opening 0.85 × 0.50','#138b68'),(k.F_Paste,'Paste 0.65 × 0.30','#416cab')]):
  ax=axes[row,col]
  ax.add_patch(Rectangle((-.875,-1.3),1.75,2.6,fill=False,edgecolor='#999',linestyle=':',linewidth=1,label='Max body + protrusions'))
  ax.add_patch(Rectangle((-.625,-1),1.25,2,fill=False,edgecolor='#222',linewidth=1))
  ax.add_patch(Rectangle((-1.7,-1.55),3.4,3.1,fill=False,edgecolor='#953b9c',linestyle='--',linewidth=1.1))
  for p in fp.Pads():
   if not p.IsOnLayer(layer):continue
   x,y=k.ToMM(p.GetPosition().x),k.ToMM(p.GetPosition().y);w,h=k.ToMM(p.GetSize().x),k.ToMM(p.GetSize().y)
   ax.add_patch(Rectangle((x-w/2,y-h/2),w,h,facecolor=color,edgecolor='#333',linewidth=.8,alpha=.8))
   if layer==k.F_Cu:ax.text(x,y,p.GetNumber(),ha='center',va='center',fontsize=11,color='white',weight='bold')
  ax.set(xlim=(-1.9,1.9),ylim=(1.8,-1.8),aspect='equal',title=label+'\n'+title,xlabel='X / mm',ylabel='Y / mm')
  ax.set_xticks([-1.5,0,1.5]);ax.set_yticks([-1.5,0,1.5]);ax.grid(alpha=.16)
fig.suptitle('Nexperia standard logic candidates · component top view\nPurple: project courtyard 3.4 × 3.1 mm · dotted grey: body including protrusions',fontsize=14)
fig.savefig(M/'nexperia-standard-footprint-layer-gallery.png',dpi=160)
print('Saved gallery from actual native footprint layers')
