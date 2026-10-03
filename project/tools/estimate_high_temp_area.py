#!/usr/bin/env python3
"""Screening estimate of rectangular placement reservations, never a layout/fit proof."""
from pathlib import Path
import xml.etree.ElementTree as E,json,collections,re
B=Path(__file__).resolve().parents[1];x=E.parse(B/'cad/high-temp-candidate/master.xml');comps=x.findall('.//components/comp')
specs={r['name']:r for r in json.load(open(B/'engineering/mechanical/small-parts-footprint-spec.json'))}
for r in json.load(open(B/'engineering/mechanical/compact-footprint-spec.json')):
 r['courtyard_half_width_height_mm']=[v/2 for v in r['courtyard_mm']];specs[r['name']]=r
nvt_path=B/'engineering/mechanical/nvt4858-footprint-spec.json'
if nvt_path.exists():
 nvt=json.load(open(nvt_path));specs[nvt['footprint'].split(':')[-1]]={'courtyard_half_width_height_mm':[v/2 for v in nvt['project_courtyard_mm']]}
rows=[]
for c in comps:
 ref=c.get('ref');val=c.findtext('value');dnp=c.find("property[@name='dnp']") is not None;kind=''.join(filter(str.isalpha,ref));fp=c.findtext('footprint') or ''
 a=None;basis='unselected reservation, NOT manufacturing geometry'
 if ref=='J1':a=(0,0);basis='logical edge contract; perimeter band accounted separately'
 elif ref=='U1':a=(13.5,13.5);basis='13x13 body +0.25mm provisional clearance, no BGA escape allowance'
 elif ref=='U2':a=(10.5,15.0);basis='10x14.5 body +0.25mm provisional clearance, no BGA escape allowance'
 elif ref=='U3':a=(12,13.5);basis='11.5x13 body +0.25mm provisional clearance, no BGA escape allowance'
 elif fp.split(':')[-1] in specs:
  h=specs[fp.split(':')[-1]]['courtyard_half_width_height_mm'];a=(h[0]*2,h[1]*2);basis='drawing-verified existing footprint courtyard'
 elif ref in ['U91','U92','U93','U94']:
  a=(3.4,3.1);basis='Nexperia GW source-verified candidate courtyard; no tiny GX footprint assumed'
 elif kind=='R' and 'TNPW0402' in val:
  a=(2.1,1.2);basis='Vishay current document28950 IPC-based 1.5x0.6mm copper envelope plus mask/assembly budget; process candidate'
 elif ref=='U81':a=(4.5,4.5)
 elif ref in ['U84','U85','U86','U88']:a=(3.5,3.5)
 elif kind=='U' and ref!='U95':a=(3.6,3.2)
 elif ref=='U95':a=(2.8,3.6)
 elif kind=='L':
  a=(3.0,2.4) if ref in ['L22','L23','L24','L25','L26'] else (4.6,4.6)
  if ref in ['L22','L23']:basis='Murata DFE201612E drawing p5: 2.4x1.8mm land envelope + hypothetical 0.05mm mask and 0.25mm clearance per side; reservation only, see passive-inductor-candidate-review.md'
 elif kind=='Y':
  a=(3.8,2.1) if ref=='Y1' else (4.2,3.5)
  if ref=='Y2':basis='YXC X322524MOB4SI RevB0 p3 source-derived candidate: 1.4x1.2mm lands at X+/-1.1,Y+/-0.85; mask+0.05mm and courtyard+0.25mm; see cad/verified-footprints/crystals/geometry-source.json'
 elif kind=='FB':a=(2.2,1.3)
 elif kind=='TP':a=(1.5,1.5)
 elif kind=='JP':a=(3,2)
 elif kind=='C':
  m=re.match(r'([\d.]+)uF',val)
  uf=float(m.group(1)) if m else 0
  if uf>=47:a=(2.8,1.8)
  elif uf>=2:a=(2.2,1.3)
  elif uf>=1:a=(1.6,1)
 elif kind=='R' and ('total' in val):
  k=float(re.match(r'([\d.]+)k',val).group(1));a=(3.8,2) if k>260 else (2.8,1.8) if k>130 else (2.2,1.3)
 elif ref=='R220':
  a=(3.2,1.7);basis='Vishay WSL060300000ZEA9 official land span2.52x1.01mm plus hypothetical mask and clearance; see passive-small-parts-review.md'
 elif ref=='R561':
  a=(2.0,1.2);basis='Candidate WFZ040200000ZE66 power-feed jumper: official1.4x0.6mm copper envelope plus hypothetical0.05mm mask/0.25mm clearance; assembly and application qualification pending'
 area_dense=a[0]*a[1] if a else 1.1*.7
 area_0402=a[0]*a[1] if a else 1.6*1
 rows.append(dict(reference=ref,value=val,dnp=dnp,bom_included=ref!='J1' and kind not in ['TP','JP'] and not dnp,package_basis=basis,dense_reservation_xy_mm=list(a) if a else [1.1,.7],standard_reservation_xy_mm=list(a) if a else [1.6,1],reservation_dense_mm2=area_dense,reservation_0402_mm2=area_0402))
summary={'conditional_castellation_proposal_available_mm2':1253.16,'conditional_edge_reservation_mm':1.30,'physical_component_count_excluding_DNP_logical_edge_and_testpoints':sum(r['bom_included'] for r in rows),'all_xml_reference_count':len(rows),'DNP_references':[r['reference'] for r in rows if r['dnp']],'type_counts':dict(collections.Counter(''.join(filter(str.isalpha,r['reference'])) for r in rows)),'board_area_mm2':38*38,'assumed_edge_reserve_each_side_mm':2,'available_after_assumed_perimeter_band_mm2':34*34,'dense_0201_small_passives_reservation_mm2':sum(r['reservation_dense_mm2'] for r in rows),'0402_small_passives_reservation_mm2':sum(r['reservation_0402_mm2'] for r in rows),'interpretation':'Area sum is only an optimistic lower-bound screen; does NOT prove packing, escape, routing, local decoupling, thermal feasibility or assembly compatibility. DNP/test point land reservations still consume area. Unknown component choices can grow. Edge band is an explicit provisional assumption, not recovered original geometry.'}
(B/'cad/high-temp-candidate/full-bom-area-screen.json').write_text(json.dumps({'summary':summary,'components':rows},indent=2));print(json.dumps(summary,indent=2))
