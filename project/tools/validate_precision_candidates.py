#!/usr/bin/env python3
from pathlib import Path
import xml.etree.ElementTree as E,json
B=Path(__file__).resolve().parents[1];H=B/'cad/high-temp-candidate';x=E.parse(H/'master.xml');cs={c.get('ref'):c for c in x.findall('.//components/comp')}
expected={'R201':'3.32k','R202':'10k','R207':'8.66k','R208':'10k','R210':'20k','R211':'10k','R213':'45.3k','R214':'10k','R525':'88.7k','R526':'10k','R63':'240R','R64':'240R','R65':'240R','R66':'240R','R67':'30k','R68':'30k','R69':'200R','R70':'200R','R71':'200R'}
fp='CMK230_Passive_Candidates:Vishay_TNPW0402_IPC7351_SourceLand_PROCESS_CANDIDATE'
for ref,val in expected.items():
 c=cs[ref];v=c.findtext('value');assert v.startswith(val+' ') and 'TOTAL<=0.70pct CANDIDATE' in v,(ref,v);assert c.findtext('footprint')==fp
j=cs['J1'];assert j.find("property[@name='exclude_from_board']") is None and j.find("property[@name='exclude_from_bom']") is not None
r={'status':'SOURCE_FAMILY_AND_GEOMETRY_CANDIDATE_NOT_LIFETIME_OR_POWER_QUALIFIED','verified_references':expected,'assigned_footprint':fp,'count':len(expected),'initial_tolerance_pct':.1,'TCR_ppm_per_K':10,'conditional_total_resistance_error_pct':.70,'sources':['https://www.vishay.com/docs/28758/tnpw_e3.pdf','https://www.vishay.com/doc?28950'],'remaining_gates':['exact mission/film-temperature/lifetime error','calibration-pin dissipation and thermal derating','mask/stencil/assembly acceptance','exact ordering and availability']}
(H/'precision-resistor-validation.json').write_text(json.dumps(r,indent=2));print('PASS 19 values and source-land assignments; edge retained on-board')
