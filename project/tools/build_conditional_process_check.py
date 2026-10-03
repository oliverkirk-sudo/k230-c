#!/usr/bin/env python3
from pathlib import Path
import json,re,shutil,hashlib
B=Path(__file__).resolve().parents[1];H=B/'cad/high-temp-candidate';O=B/'cad/conditional-process-check';O.mkdir(exist_ok=True)
for p in list(H.glob('*.kicad_sch'))+[H/'CMK230_Core_REVIEW.kicad_pro',H/'CMK230_Core_REVIEW.kicad_pcb',H/'Integrated.kicad_sym',H/'sym-lib-table',H/'fp-lib-table']:
 shutil.copyfile(p,O/p.name)
rules=['(version 1)','# CONDITIONAL proposed process model. No DRC exclusions or severity overrides.','(rule "Proposed general 4mil clearance" (constraint clearance (min 0.1016mm)))','(rule "Proposed general 4mil track" (constraint track_width (min 0.1016mm)))']
pairs=[('A1','A2'),('A2','A3'),('A2','B2'),('A3','B3'),('B1','C1'),('B2','C2'),('B3','C3'),('C1','D1'),('C2','D2'),('C3','D3'),('D1','E1'),('D2','E2'),('D3','E3'),('E1','E2'),('E2','E3')]
for ref in ['U22','U23']:
 for a,b in pairs:
  condition=f"A.Type == 'Pad' && B.Type == 'Pad' && A.memberOfFootprint('{ref}') && B.memberOfFootprint('{ref}') && ((A.Pad_Number == '{a}' && B.Pad_Number == '{b}') || (A.Pad_Number == '{b}' && B.Pad_Number == '{a}'))"
  rules.append(f'(rule "Source YCG {ref} {a}-{b} local3mil" (condition "{condition}") (constraint clearance (min 0.0762mm)))')
(O/'CMK230_Core_REVIEW.kicad_dru').write_text('\n'.join(rules)+'\n')
meta={'status':'SEPARATE_CONDITIONAL_PROCESS_MODEL_NOT_FACTORY_ACCEPTANCE','source_board_sha256':hashlib.sha256((H/'CMK230_Core_REVIEW.kicad_pcb').read_bytes()).hexdigest(),'source_netlist_sha256':hashlib.sha256((H/'master.xml').read_bytes()).hexdigest(),'default_diagnostic_preserved':str((H/'partial-pcb-drc-parity.json').relative_to(B)),'general_clearance_mm':.1016,'general_track_mm':.1016,'exact_pad_pairs_per_ref':pairs,'applicable_references':['U22','U23'],'pair_clearance_mm':.0762,'source_footprint':'CMK230_Verified:TI_YCG0015_TPS628640_1.05x1.78_P0.35_SMD_DrawingVerified','nominal_source_gap_mm':.085,'nominal_margin_mm':.0088,'sources':['https://www.pcbway.com/advanced-pcb-capabilities.html','https://www.ti.com/lit/ds/symlink/tps62864.pdf'],'limitations':['Published minima are nominal capability, not tolerance guarantee.','Etch bias/variation, mask alignment, stencil and assembly acceptance remain open.','Advanced fine-line conditions cannot automatically be combined with selected 1oz stack and castellations.','Rule applies to enumerated pad-to-pad pairs only; no arbitrary pad-to-track or nearby copper relaxation.','No incomplete connectivity or missing footprint errors are suppressed.']}
(O/'process-model-manifest.json').write_text(json.dumps(meta,indent=2));print('Generated separate conditional model,30 exact pad-pair rules')
