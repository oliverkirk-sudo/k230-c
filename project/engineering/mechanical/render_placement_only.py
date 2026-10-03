#!/usr/bin/python3
from pathlib import Path
import csv,json
import pcbnew as k
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle,FancyBboxPatch
R=Path(__file__).resolve().parents[2];M=R/'engineering/mechanical';B=R/'cad/verified-footprints/placement-only/CMK230_Placement_ONLY_NOT_FOR_FAB.kicad_pcb';board=k.LoadBoard(str(B))
rows=list(csv.DictReader((M/'placement-only-positions.csv').open()))
fig=plt.figure(figsize=(13,10));ax=fig.add_axes([.07,.15,.64,.76]);side=fig.add_axes([.75,.15,.23,.7]);side.axis('off')
ax.set_aspect('equal');ax.set_xlim(-1,39);ax.set_ylim(39,-1);ax.set_xticks(range(0,39,2));ax.set_yticks(range(0,39,2));ax.grid(color='#e8ebef',lw=.5,zorder=-5);ax.set_xlabel('mm');ax.set_ylabel('mm')
ax.add_patch(Rectangle((0,0),38,38,facecolor='#fbfaf6',edgecolor='#172333',lw=2,zorder=-3));ax.add_patch(Rectangle((2,2),34,34,facecolor='white',edgecolor='#a4956b',linestyle='--',lw=1,zorder=-2))
fpbyref={x.GetReference():x for x in board.GetFootprints()}
colors={'U1':'#688db2','U2':'#75a394','U3':'#b9946c'}
for r in rows:
 ref=r['reference'];x,y=float(r['center_x_mm']),float(r['center_y_mm']);w,h=float(r['nominal_body_w_mm']),float(r['nominal_body_h_mm']);cw,ch=float(r['courtyard_w_mm']),float(r['courtyard_h_mm']);fp=fpbyref[ref]
 ax.add_patch(Rectangle((x-cw/2,y-ch/2),cw,ch,fill=False,edgecolor='#994d91',ls=':',lw=.9))
 if ref in colors:
  ax.add_patch(Rectangle((x-w/2,y-h/2),w,h,facecolor=colors[ref],alpha=.18,edgecolor=colors[ref],lw=1.5))
  for g in fp.GraphicalItems():
   if g.GetLayer()==k.Dwgs_User and g.GetShape()==k.SHAPE_T_SEGMENT:
    ax.plot([k.ToMM(g.GetStart().x),k.ToMM(g.GetEnd().x)],[k.ToMM(g.GetStart().y),k.ToMM(g.GetEnd().y)],color=colors[ref],lw=.35)
  label={'U1':'U1  K230\n13 x 13 mm body\n390 center marks','U2':'U2  LPDDR4\n10 x 15 mm body\n200 center marks','U3':'U3  eMMC\n11.5 x 13 mm body\n153 center marks'}[ref]
  ax.text(x,y,label,ha='center',va='center',fontsize=10,color='#263a4a',bbox=dict(boxstyle='round,pad=.35',fc='white',ec='none',alpha=.9))
  ax.plot([x-w/2,x-w/2+.55],[y-h/2+.55,y-h/2],color='#283946',lw=2)
 else:
  ax.add_patch(Rectangle((x-w/2,y-h/2),w,h,facecolor='#eedcc1',edgecolor='#8a5b34',lw=.7))
  for p in fp.Pads():
   if not p.IsOnLayer(k.F_Cu):continue
   xx,yy=k.ToMM(p.GetPosition().x),k.ToMM(p.GetPosition().y);ww,hh=k.ToMM(p.GetSize().x),k.ToMM(p.GetSize().y)
   if p.GetShape()==k.PAD_SHAPE_CIRCLE:patch=Circle((xx,yy),ww/2,fc='#a74032',ec='none')
   else:patch=FancyBboxPatch((xx-ww/2,yy-hh/2),ww,hh,boxstyle=f'round,pad=0,rounding_size={k.ToMM(p.GetRoundRectCornerRadius())}',fc='#a74032',ec='none')
   ax.add_patch(patch)
  ax.text(x,y-ch/2-.45,ref,fontsize=8,ha='center',va='bottom',color='#70342b',bbox=dict(fc='white',ec='none',pad=.3))
fig.suptitle('CM-K230 | 38 x 38 mm top-side body-fit canvas',fontsize=19,fontweight='bold',y=.97)
fig.text(.07,.935,'PLACEMENT ONLY  •  No production BGA lands, castellations, routes or vias',fontsize=11,color='#8d3d31')
side.text(0,1,'13 IC instances',fontsize=16,fontweight='bold',va='top')
side.text(0,.93,'3 BGA mechanical placeholders\n3 TMUX1574 switches\n1 SN74LVC1G32 OR gate\n4 TPS6282xA regulators\n2 TPS628640 regulators',fontsize=11,linespacing=1.6,va='top')
side.text(0,.65,'Geometry check',fontsize=13,fontweight='bold',va='top')
side.text(0,.59,'All chosen envelopes fit on top\nNo courtyard overlaps\nNearest courtyard gap: 0.85 mm\nNearest outline gap: 2.45 mm',fontsize=10.5,linespacing=1.6,va='top')
side.text(0,.38,'Still unplaced / unproven',fontsize=13,fontweight='bold',va='top',color='#8d3d31')
side.text(0,.32,'Inductors and passives\nDecoupling and power loops\nClocks and test access\nBGA escape, stackup and routing\nThermal and PDN performance\nCastellation manufacturing geometry',fontsize=10.5,linespacing=1.6,va='top')
fig.text(.07,.08,'Dotted purple: chosen assembly envelopes   |   Dashed inset: illustrative 2 mm edge reserve, not a manufacturing rule',fontsize=9.5,color='#505c69')
fig.text(.07,.04,'This demonstrates the drawn IC bodies fit. It does not establish a routable, thermally adequate, or manufacturable module.',fontsize=10,color='#8d3d31')
fig.savefig(M/'placement-only-canvas.png',dpi=170,facecolor='white')
