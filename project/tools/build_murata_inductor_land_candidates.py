#!/usr/bin/python3
"""Source land candidates only; electrical and assembly qualification remain open."""
from pathlib import Path
import pcbnew as k,json,hashlib
B=Path(__file__).resolve().parents[1];D=B/'cad/verified-footprints/inductor-candidates';L=D/'CMK230_Inductor_Candidates.pretty';L.mkdir(parents=True,exist_ok=True)
parts=[dict(mpn='DFE201612E-R24M=P2',refs=['L22','L23'],height=1.2,pdf='/workspace/shared/k230-reference/mechanical/passive-review/murata-DFE201612E-JETE243A-0006.pdf',source='https://search.murata.co.jp/Ceramy/image/img/P02/J(E)TE243A-0006.pdf'),dict(mpn='DFE201610E-R47M=P2',refs=['L24','L25','L26'],height=1.,pdf='/workspace/shared/k230-reference/mechanical/compact-inductor-Murata-JETE243A-0001-official.pdf',source='https://pim.murata.com/asset/pim4/inductor/J(E)TE243A-0001_PDF_INDUCTOR')]
plugin=k.PCB_IO_MGR.PluginFind(k.PCB_IO_MGR.KICAD_SEXP);board=k.BOARD()
for ii,q in enumerate(parts):
 name='Murata_'+q['mpn'].replace('=','_')+'_SOURCE_LAND_PROCESS_CANDIDATE';q['footprint']=name
 f=k.FOOTPRINT(None);f.SetFPID(k.LIB_ID('CMK230_Inductor_Candidates',name));f.SetReference('L**');f.Reference().SetLayer(k.F_Fab);f.Reference().SetPosition(k.VECTOR2I(0,k.FromMM(-1.7)));f.SetValue(q['mpn']);f.Value().SetVisible(False);f.SetAttributes(k.FP_SMD)
 f.SetLibDescription('Source p5 copper. No unrelated copper or through-holes under coil per p7; not automatically enforced. Mask/paste/assembly and hot loss unqualified.')
 for num,sign in [(1,-1),(2,1)]:
  pad=k.PAD(f);pad.SetNumber(str(num));pad.SetAttribute(k.PAD_ATTRIB_SMD);pad.SetShape(k.PAD_SHAPE_RECT);pad.SetSize(k.VECTOR2I(k.FromMM(.8),k.FromMM(1.8)));pad.SetPosition(k.VECTOR2I(k.FromMM(sign*.8),0));ls=k.LSET();[ls.AddLayer(z) for z in [k.F_Cu,k.F_Mask]];pad.SetLayerSet(ls);pad.SetLocalSolderMaskMargin(k.FromMM(.05));f.Add(pad)
  paste=k.PAD(f);paste.SetNumber('');paste.SetAttribute(k.PAD_ATTRIB_SMD);paste.SetShape(k.PAD_SHAPE_RECT);paste.SetSize(k.VECTOR2I(k.FromMM(.8),k.FromMM(1.8)));paste.SetPosition(pad.GetPosition());ps=k.LSET();ps.AddLayer(k.F_Paste);paste.SetLayerSet(ps);f.Add(paste)
 def rect(w,h,layer):
  xy=[(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)]
  for a,b in zip(xy,xy[1:]+xy[:1]):
   z=k.PCB_SHAPE();z.SetShape(k.SHAPE_T_SEGMENT);z.SetStart(k.VECTOR2I(k.FromMM(a[0]),k.FromMM(a[1])));z.SetEnd(k.VECTOR2I(k.FromMM(b[0]),k.FromMM(b[1])));z.SetLayer(layer);z.SetWidth(k.FromMM(.05));f.Add(z)
 rect(2.2,1.8,k.F_Fab);rect(3.,2.4,k.F_CrtYd);rect(2.2,1.8,k.Dwgs_User)
 plugin.FootprintSave(str(L),f);f=plugin.FootprintLoad(str(L),name);assert len([p for p in f.Pads() if p.GetNumber()])==2
 for p in f.Pads():
  if not p.GetNumber():assert not p.IsOnLayer(k.F_Cu) and p.IsOnLayer(k.F_Paste)
 f.SetReference('L'+str(ii+1));f.SetPosition(k.VECTOR2I(k.FromMM(10+ii*10),k.FromMM(10)));board.Add(f)
 q.update(copper_land_mm=[.8,1.8],pad_centers_mm=[[-.8,0],[.8,0]],land_gap_mm=.8,max_body_mm=[2.2,1.8],courtyard_mm=[3.,2.4],mask_expansion_mm=.05,paste='two explicit unnumbered 1:1 F.Paste-only apertures; process candidate',under_coil_restriction='No through-holes or unrelated copper under full maximum body; source gives no layer exemption. Dwgs.User marker only; NOT automatically enforced.',source_sha256=hashlib.sha256(Path(q['pdf']).read_bytes()).hexdigest(),footprint_sha256=hashlib.sha256((L/(name+'.kicad_mod')).read_bytes()).hexdigest())
for a,b in [((0,0),(30,0)),((30,0),(30,20)),((30,20),(0,20)),((0,20),(0,0))]:
 z=k.PCB_SHAPE();z.SetShape(k.SHAPE_T_SEGMENT);z.SetStart(k.VECTOR2I(k.FromMM(a[0]),k.FromMM(a[1])));z.SetEnd(k.VECTOR2I(k.FromMM(b[0]),k.FromMM(b[1])));z.SetLayer(k.Edge_Cuts);z.SetWidth(k.FromMM(.05));board.Add(z)
k.SaveBoard(str(D/'Murata_Inductor_Geometry_QA_ONLY.kicad_pcb'),board)
(D/'source-land-validation.json').write_text(json.dumps({'status':'SOURCE_COPPER_CANDIDATES_NOT_ELECTRICALLY_OR_MANUFACTURING_QUALIFIED','date_utc':'2026-09-30','source_pages_visually_inspected':[5,7],'parts':parts,'limits':['No assignment to main schematic yet.','No inferred polarity or winding start from symmetric unmarked source drawing.','No unrelated-copper/through-hole enforcement claimed; exact-net-aware rule needed at placement.','Source lands exact; mask+50um,paste1:1,courtyard250um beyond mask are declared process assumptions.','L21 unchanged; no hot-current qualification or full-board fit implied.']},indent=2))
print('Created2 source land candidates and isolated native board')
