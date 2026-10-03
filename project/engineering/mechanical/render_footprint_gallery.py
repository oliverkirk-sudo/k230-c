#!/usr/bin/python3
"""Engineering gallery rendered from actual KiCad footprint objects, not source spec."""
import pcbnew as k
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle,FancyBboxPatch,Rectangle
from pathlib import Path
R=Path(__file__).resolve().parents[2];L=R/'cad/verified-footprints/CMK230_Verified.pretty';O=R/'engineering/mechanical'
rows=[('RSV','TMUX1574RSVR / RSV0016A',1.45,1.85),('DBV','SN74LVC1G32DBVR / DBV0005A',2.2,2.1),('DMQ','TPS6282xADMQ / DMQ0006A',1.3,1.1),('YCG','TPS628640BYCGR / YCG0015',.85,1.2)]
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
   ax.plot([k.ToMM(shape.GetStart().x),k.ToMM(shape.GetEnd().x)],[k.ToMM(shape.GetStart().y),k.ToMM(shape.GetEnd().y)],color='#252c38',lw=.8,ls='--',alpha=.8)
  ax.axhline(0,color='#d8dde5',lw=.4,zorder=-1);ax.axvline(0,color='#d8dde5',lw=.4,zorder=-1)
  ax.set_title(['Copper','Mask openings','Paste apertures'][col],fontsize=10,fontweight='bold',color=colors[col])
  ax.set_xlabel('mm');ax.tick_params(labelsize=7)
  for sp in ax.spines.values():sp.set_color('#e0e3e8')
  if col==0:ax.set_ylabel(title+'\nmm',fontsize=9)
fig.suptitle('TI drawing-verified footprints | component-side view',fontsize=17,fontweight='bold',y=.99)
fig.text(.5,.968,'Actual KiCad 9 pad objects; origin at body center; dashed line = nominal body',ha='center',fontsize=10,color='#505866')
fig.text(.5,.014,'Engineering review only. Explicit mask/paste apertures must be preserved. Production stackup and stencil process are not approved.',ha='center',fontsize=9,color='#843628')
plt.subplots_adjust(top=.94,bottom=.055,hspace=.45,wspace=.28,left=.08,right=.98)
fig.savefig(O/'TI-footprint-layer-gallery.png',dpi=170,facecolor='white')
