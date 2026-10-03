#!/usr/bin/python3
from pathlib import Path
import pcbnew as k
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
ROOT=Path(__file__).resolve().parents[2]
lib=ROOT/'cad/verified-footprints/translator-candidate/CMK230_Translator_Candidate.pretty'
fp=k.FootprintLoad(str(lib),next(lib.glob('*.kicad_mod')).stem)
fig,axes=plt.subplots(1,3,figsize=(12,5));colors=['#b64e33','#466cac','#66707b']
cu=[p for p in fp.Pads() if p.IsOnLayer(k.F_Cu)]
for i,layer in enumerate([k.F_Cu,k.F_Mask,k.F_Paste]):
 ax=axes[i];ax.set_aspect('equal');ax.set_xlim(-1.45,1.45);ax.set_ylim(1.85,-1.85)
 for p in fp.Pads():
  if not p.IsOnLayer(layer):continue
  x,y=k.ToMM(p.GetPosition().x),k.ToMM(p.GetPosition().y);w,h=k.ToMM(p.GetSize().x),k.ToMM(p.GetSize().y)
  ax.add_patch(Rectangle((x-w/2,y-h/2),w,h,facecolor=colors[i],edgecolor='white',lw=.6))
 for p in cu:ax.text(k.ToMM(p.GetPosition().x),k.ToMM(p.GetPosition().y),p.GetNumber(),ha='center',va='center',color='white',fontsize=8)
 ax.add_patch(Rectangle((-.9,-1.3),1.8,2.6,fill=False,linestyle='--',edgecolor='#293347',lw=.8))
 ax.add_patch(Rectangle((-1.4,-1.8),2.8,3.6,fill=False,linestyle=':',edgecolor='#777777',lw=.8))
 ax.plot([-.9,-.65],[-1.05,-1.3],color='#293347',lw=1)
 ax.axhline(0,color='#ddd',lw=.5,zorder=-1);ax.axvline(0,color='#ddd',lw=.5,zorder=-1)
 ax.set_title(['Copper: 16 pads','Mask: 16 openings','Paste: 16 apertures'][i],fontsize=11,color=colors[i]);ax.set_xlabel('mm');ax.tick_params(labelsize=8)
axes[0].set_ylabel('mm; +Y down')
fig.suptitle('NVT4858HK | SOT1161-2 | component-side view',fontsize=16,y=.98)
fig.text(.5,.915,'Native KiCad pad objects. Pin 1 has the longer land; no exposed center pad.',ha='center',fontsize=10)
fig.text(.5,.035,'Dashed = nominal body; dotted = project courtyard. Drawing candidate only; assembly/stencil approval pending.',ha='center',fontsize=9)
plt.subplots_adjust(top=.86,bottom=.14,wspace=.28,left=.06,right=.98)
fig.savefig(ROOT/'engineering/mechanical/nvt4858-footprint-layer-gallery.png',dpi=170,facecolor='white')
