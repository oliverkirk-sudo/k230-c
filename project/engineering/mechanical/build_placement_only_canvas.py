#!/usr/bin/python3
"""Create an isolated 38x38 top-side body-fit canvas; no manufacturing BGA pads.
Does not edit integrated or module master CAD. No routes, vias, drills or edge pads.
"""
from pathlib import Path
import pcbnew as k
import csv,json,math,itertools,hashlib
R=Path(__file__).resolve().parents[2];M=R/'engineering/mechanical';BASE=R/'cad/verified-footprints';O=BASE/'placement-only';O.mkdir(exist_ok=True)
L=BASE/'CMK230_Verified.pretty';P=O/'Mechanical_Placeholders.pretty';P.mkdir(exist_ok=True)

def fmt(x):return f'{x:.6f}'.rstrip('0').rstrip('.') or '0'
def ln(a,b,layer='Dwgs.User',width=.015):return f'(fp_line (start {fmt(a[0])} {fmt(a[1])}) (end {fmt(b[0])} {fmt(b[1])}) (stroke (width {fmt(width)}) (type default)) (layer "{layer}"))'
def rc(w,h,layer):return f'(fp_rect (start {fmt(-w/2)} {fmt(-h/2)}) (end {fmt(w/2)} {fmt(h/2)}) (stroke (width 0.05) (type default)) (fill none) (layer "{layer}"))'
specs=[('U1','K230',13,13,13.1,13.1,12,12,'bga-K230-physical-centers.csv'),('U2','K4F8E304HB',10,15,10.1,15.1,27,12,'bga-K4F8E304HB-physical-centers.csv'),('U3','KLMAG1JETD',11.5,13,11.6,13.1,12,28,'bga-KLMAG1JETD-physical-centers.csv')]
records=[];board=k.BOARD()
for ref,part,w,h,mw,mh,x,y,src in specs:
 name=part+'_MECHANICAL_ONLY_NO_PADS';rows=list(csv.DictReader((M/src).open()))
 a=[f'(footprint "{name}" (version 20241229) (generator "cmk230_placement_canvas") (layer "F.Cu") (attr board_only exclude_from_bom exclude_from_pos_files)',f'(descr "MECHANICAL PLACEHOLDER ONLY. Crosses are verified ball centers, NOT ball outlines or copper/mask/paste pads. {src}")',f'(property "Reference" "{ref}" (at 0 {fmt(-h/2-.6)}) (layer "F.Fab") (effects (font (size 0.8 0.8) (thickness 0.12))))',f'(property "Value" "{part} MECHANICAL ONLY" (at 0 {fmt(h/2+.7)}) (layer "F.Fab") (effects (font (size 0.65 0.65) (thickness 0.1))))',rc(w,h,'F.Fab'),rc(mw,mh,'Dwgs.User'),rc(mw+.5,mh+.5,'F.CrtYd')]
 for row in rows:
  px,py=float(row['x_mm']),float(row['y_mm']);a.extend([ln((px-.04,py),(px+.04,py)),ln((px,py-.04),(px,py+.04))])
 a.append(ln((-w/2,-h/2+.6),(-w/2+.6,-h/2),'F.Fab',.15))
 a.append(')');(P/(name+'.kicad_mod')).write_text('\n'.join(a)+'\n')
 fp=k.FootprintLoad(str(P),name);assert len(fp.Pads())==0
 fp.SetFPID(k.LIB_ID('Mechanical_Placeholders',name));fp.SetReference(ref);fp.SetPosition(k.VECTOR2I(k.FromMM(x),k.FromMM(y)))
 fp.SetValue({'U1':'K230\n390 centers','U2':'LPDDR4\n200 centers','U3':'eMMC\n153 centers'}[ref]);fp.Value().SetPosition(k.VECTOR2I(k.FromMM(x),k.FromMM(y)));board.Add(fp)
 records.append(dict(reference=ref,part=part,kind='MECHANICAL_ONLY_NO_PADS',center_x_mm=x,center_y_mm=y,rotation_deg=0,nominal_body_w_mm=w,nominal_body_h_mm=h,max_body_w_mm=mw,max_body_h_mm=mh,courtyard_w_mm=mw+.5,courtyard_h_mm=mh+.5,physical_center_crosses=len(rows),copper_pads=0))

# Same package types as the candidate register; this is placement-only, not a netlist import.
small=[('U11','TMUX1574RSVR','RSV',24,25),('U12','TMUX1574RSVR','RSV',28,25),('U13','TMUX1574RSVR','RSV',32,25),('U14','SN74LVC1G32DBVR','DBV',28,30),('U21','TPS62827ADMQ','DMQ',20.5,22),('U22','TPS628640BYCGR','YCG',34,9),('U23','TPS628640BYCGR','YCG',34,14),('U24','TPS62826ADMQ','DMQ',20.5,26),('U25','TPS62825ADMQ','DMQ',21.5,31),('U26','TPS62826ADMQ','DMQ',25,34.5)]
parts=json.loads((M/'small-parts-footprint-spec.json').read_text())
for ref,part,tag,x,y in small:
 name=next(p.stem for p in L.glob('*.kicad_mod') if tag in p.stem);fp=k.FootprintLoad(str(L),name)
 fp.SetFPID(k.LIB_ID('CMK230_Verified',name));fp.SetReference(ref);fp.SetValue(part);fp.Value().SetVisible(False);fp.SetPosition(k.VECTOR2I(k.FromMM(x),k.FromMM(y)));board.Add(fp)
 spec=next(z for z in parts if z['name']==name);w,h=spec['body_nominal_mm'];mw,mh=spec['body_max_mm'];cx,cy=spec['courtyard_half_width_height_mm']
 # Individual dummy nets let geometry DRC see same-footprint electrical clearances without pretending connectivity.
 for p in fp.Pads():
  if p.IsOnLayer(k.F_Cu):
   net=k.NETINFO_ITEM(board,ref+'_'+p.GetNumber()+'_UNROUTED');board.Add(net);p.SetNet(net)
 records.append(dict(reference=ref,part=part,kind='DRAWING_VERIFIED_SMALL_FOOTPRINT_UNROUTED',center_x_mm=x,center_y_mm=y,rotation_deg=0,nominal_body_w_mm=w,nominal_body_h_mm=h,max_body_w_mm=mw,max_body_h_mm=mh,courtyard_w_mm=2*cx,courtyard_h_mm=2*cy,physical_center_crosses=0,copper_pads=sum(p.IsOnLayer(k.F_Cu) for p in fp.Pads())))

def boardline(a,b,layer,width=.05):
 s=k.PCB_SHAPE();s.SetShape(k.SHAPE_T_SEGMENT);s.SetLayer(layer);s.SetStart(k.VECTOR2I(*(k.FromMM(v) for v in a)));s.SetEnd(k.VECTOR2I(*(k.FromMM(v) for v in b)));s.SetWidth(k.FromMM(width));board.Add(s)
for a,b in [((0,0),(38,0)),((38,0),(38,38)),((38,38),(0,38)),((0,38),(0,0))]:boardline(a,b,k.Edge_Cuts)
# Illustration only. This is NOT a castellation keepout rule, cutout, or verified edge geometry.
for a,b in [((2,2),(36,2)),((36,2),(36,36)),((36,36),(2,36)),((2,36),(2,2))]:boardline(a,b,k.Dwgs_User,.05)
for text,x,y,size in [('PLACEMENT ONLY - NOT A MANUFACTURING PCB',19,-3,1.0),('38 x 38 mm | all 13 IC bodies on top | no routes / vias / edge pads',19,-1.5,.7),('BGA crosses = nominal centers, NOT copper pads or solder balls',19,40,.7),('2 mm edge band is illustrative only; castellation geometry unresolved',19,41.4,.65),('Passives, inductors, crystals, decoupling and test access are NOT placed',19,42.8,.65)]:
 t=k.PCB_TEXT(board);t.SetText(text);t.SetTextSize(k.VECTOR2I(k.FromMM(size),k.FromMM(size)));t.SetTextThickness(k.FromMM(.1));t.SetLayer(k.Dwgs_User);t.SetPosition(k.VECTOR2I(k.FromMM(x),k.FromMM(y)));board.Add(t)
boardname='CMK230_Placement_ONLY_NOT_FOR_FAB';k.SaveBoard(str(O/(boardname+'.kicad_pcb')),board)
(O/(boardname+'.kicad_pro')).write_text((BASE/'Footprint_Geometry_QA_ONLY.kicad_pro').read_text().replace('Footprint_Geometry_QA_ONLY',boardname))
(O/'fp-lib-table').write_text('(fp_lib_table (version 7)\n(lib (name "CMK230_Verified")(type "KiCad")(uri "${KIPRJMOD}/../CMK230_Verified.pretty")(options "")(descr "Drawing checked TI patterns"))\n(lib (name "Mechanical_Placeholders")(type "KiCad")(uri "${KIPRJMOD}/Mechanical_Placeholders.pretty")(options "")(descr "BODY AND CENTER MARKS ONLY - NO BGA PADS"))\n)\n')
with (M/'placement-only-positions.csv').open('w') as f:
 writer=csv.DictWriter(f,records[0].keys());writer.writeheader();writer.writerows(records)
# Independent bounding-box comparisons of actual chosen maximum assembly envelopes.
def box(r):
 x,y=r['center_x_mm'],r['center_y_mm'];a,b=r['courtyard_w_mm']/2,r['courtyard_h_mm']/2
 return x-a,y-b,x+a,y+b
min_edge=100;min_pair=100;closest=None
for r in records:
 x0,y0,x1,y1=box(r);min_edge=min(min_edge,x0,y0,38-x1,38-y1)
 assert min(x0,y0)>=2 and max(x1,y1)<=36
for a,b in itertools.combinations(records,2):
 a0,a1,a2,a3=box(a);b0,b1,b2,b3=box(b)
 dx=max(0,b0-a2,a0-b2);dy=max(0,b1-a3,a1-b3)
 assert dx>0 or dy>0,(a['reference'],b['reference'],'courtyard overlap')
 gap=math.hypot(dx,dy)
 if gap<min_pair:min_pair=gap;closest=[a['reference'],b['reference']]
# Reopen saved CAD, count actual native entities and top-side placement.
r=k.LoadBoard(str(O/(boardname+'.kicad_pcb')));fps=list(r.GetFootprints());assert len(fps)==13
assert all(f.GetLayer()==k.F_Cu for f in fps);assert len(r.GetTracks())==0;assert r.GetAreaCount()==0
for f in fps:
 if f.GetReference() in ['U1','U2','U3']:assert len(f.Pads())==0
count=sum(p.IsOnLayer(k.F_Cu) for f in fps for p in f.Pads());assert count==107
result={'status':'PASS_FOR_ILLUSTRATIVE_BODY_FIT_ONLY','outline_mm':[38,38],'top_side_footprints':13,'bga_placeholders_no_copper':3,'bga_center_crosses':743,'small_ic_instances':10,'small_numbered_copper_pads':count,'tracks_and_vias':len(r.GetTracks()),'zones':r.GetAreaCount(),'castellation_pads':0,'drills':0,'minimum_chosen_courtyard_to_outline_mm':round(min_edge,6),'minimum_courtyard_pair_gap_mm':round(min_pair,6),'closest_courtyard_pair':closest,'illustrative_edge_band_mm':2,'illustrative_edge_band_not_manufacturing_geometry':True,'excluded':['passives and decoupling placement','inductor placement and switch-current loops','clock/crystal placement','escape fanout and routing','stackup and via design','thermal and PDN analysis','complete final BOM fit','castellation/drill/plating/edge manufacturing geometry','schematic parity / electrical connectivity'],'files':{'pcb':str(O/(boardname+'.kicad_pcb')),'positions':str(M/'placement-only-positions.csv')}}
(M/'placement-only-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
