#!/usr/bin/python3
"""Engineering gallery rendered from actual KiCad footprint objects, not source spec."""
import pcbnew as k
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,FancyBboxPatch,Rectangle
from pathlib import Path
R=Path(__file__).resolve().parents[2];L=R/'cad/verified-footprints/compact-options/CMK230_Compact_Candidates.pretty';O=R/'engineering/mechanical'
rows=[('DRL0005','AUP DRL0005A',1.45,1.3),('DRL0006','AUP1G97 DRL0006A',1.45,1.3),('DCK','AUP DCK0005A',1.95,1.65),('DRV','TPS3808 DRV0006A/D',1.55,1.35)]
fig,axes=plt.subplots(4,3,figsize=(12,14));colors=['#ba4a36','#486bae','#666b75']
for row,(find,title,xx,yy) in enumerate(rows):
 fp=k.FootprintLoad(str(L),next(p.stem for p in L.glob('*.kicad_mod') if find in p.stem))
 cp=[p for p in fp.Pads() if p.IsOnLayer(k.F_Cu)]
 for col,layer in enumerate([k.F_Cu,k.F_Mask,k.F_Paste]):
  ax=axes[row,col];ax.set_aspect('equal');ax.set_xlim(-xx,xx);ax.set_ylim(yy,-yy)
  for p in fp.Pads():
   if not p.IsOnLayer(layer):continue
   x,y=k.ToMM(p.GetPosition().x),k.ToMM(p.GetPosition().y);w,h=k.ToMM(p.GetSize().x),k.ToMM(p.GetSize().y)
   if p.GetShape()==k.PAD_SHAPE_CIRCLE:patch=Circle((x,y),w/2,fc=colors[col],ec='white',lw=.5)
   else:patch=FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle=f'round,pad=0,rounding_size={k.ToMM(p.GetRoundRectCornerRadius())}',fc=colors[col],ec='white',lw=.5)
   ax.add_patch(patch)
  for p in cp:
   ax.text(k.ToMM(p.GetPosition().x),k.ToMM(p.GetPosition().y),p.GetNumber(),fontsize=7 if find!='RSV' else 6,ha='center',va='center',color='white')
  for shape in fp.GraphicalItems():
   if shape.GetLayer()!=k.F_Fab:continue
   x0,y0=k.ToMM(shape.GetStart().x),k.ToMM(shape.GetStart().y);x1,y1=k.ToMM(shape.GetEnd().x),k.ToMM(shape.GetEnd().y)
   if shape.GetShape()==k.SHAPE_T_RECT:ax.add_patch(Rectangle((min(x0,x1),min(y0,y1)),abs(x1-x0),abs(y1-y0),fill=False,edgecolor='#252c38',lw=.8,ls='--',alpha=.8))
   else:ax.plot([x0,x1],[y0,y1],color='#252c38',lw=.8,ls='--',alpha=.8)
  ax.axhline(0,color='#d8dde5',lw=.4,zorder=-1);ax.axvline(0,color='#d8dde5',lw=.4,zorder=-1)
  ax.set_title(['Copper','Mask openings','Paste apertures'][col],fontsize=10,fontweight='bold',color=colors[col])
  ax.set_xlabel('mm');ax.tick_params(labelsize=7)
  for sp in ax.spines.values():sp.set_color('#e0e3e8')
  if col==0:ax.set_ylabel(title+'\nmm',fontsize=9)
fig.suptitle('Compact package candidates | component-side view',fontsize=17,fontweight='bold',y=.99)
fig.text(.5,.953,'Actual KiCad 9 pad objects; origin at body center; dashed line = midrange body',ha='center',fontsize=10,color='#505866')
fig.text(.5,.014,'Engineering review only. Explicit mask/paste apertures must be preserved. Production stackup and stencil process are not approved.',ha='center',fontsize=9,color='#843628')
plt.subplots_adjust(top=.91,bottom=.075,hspace=.5,wspace=.28,left=.08,right=.98)
fig.savefig(O/'compact-footprint-layer-gallery.png',dpi=170,facecolor='white')
