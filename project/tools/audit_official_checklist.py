#!/usr/bin/env python3
"""Traceable checklist ledger. Model passes are never layout or hardware qualification."""
from pathlib import Path
import xml.etree.ElementTree as E,json,hashlib,re,collections,sys
B=Path(__file__).resolve().parents[1];P=Path(sys.argv[1]) if len(sys.argv)>1 else B/'cad/integrated';x=E.parse(P/'master.xml');pn={};nets={}
for n in x.findall('.//nets/net'):
 nodes={(p.get('ref'),p.get('pin')) for p in n.findall('node')};nets[n.get('name')]=nodes
 for z in nodes:pn[z]=n.get('name')
vals={c.get('ref'):c.findtext('value') for c in x.findall('.//components/comp')}
def edge(r,p,n):return pn.get((r,p))==n
def shunt(r,n,value):return {pn.get((r,'1')),pn.get((r,'2'))}=={n,'GND'} and vals.get(r,'').startswith(value)
checks={
 'all_soc_power_pins_net_named':all(pn.get(('U1',p.get('num'))) for p in x.findall(".//libpart[@part='K230_390']/pins/pin") if p.get('type')=='power_in'),
 'unused_analog_power_connected':all(n in nets for n in ['AVDD1P8_ADC','AVDD1P8_CODEC']),
 'rtc_ldo_common_domain':edge('U1','F14','AVDD1P8_PMU') and edge('U1','F15','AVDD1P8_PMU'),
 'pmu_start_strap':edge('R401','1','AVDD1P8_PMU') and edge('R401','2','PMU_INT4_AUTO_START') and edge('U1','C12','PMU_INT4_AUTO_START'),
 '24m_feedback':{pn.get(('R42','1')),pn.get(('R42','2'))}=={'CLK24_XIN','CLK24_XOUT'} and vals['R42'].startswith('1M'),
 'rtc_feedback':{pn.get(('R41','1')),pn.get(('R41','2'))}=={'RTC_XIN','RTC_XOUT'} and vals['R41'].startswith('1M'),
 'emmc_pulls':edge('R562','1','EMMC_CMD') and edge('R562','2','VEMMC_IO') and vals['R562'].startswith('22k') and all(edge(f'R{563+i}','1',f'EMMC_DAT{i}') and edge(f'R{563+i}','2','VEMMC_IO') and vals[f'R{563+i}'].startswith('47k') for i in range(8)),
 'host_strobe_bias':shunt('R572','MMC0_STROBE','100k'),
 'vcm_pair':shunt('C63','CODEC_VCM','100nF') and shunt('C66','CODEC_VCM','4.7uF'),
 'micbias_pair':shunt('C67','MIC_BIAS','4.7uF') and shunt('C68','MIC_BIAS','100nF'),
 'tf_voltage_separation':edge('U95','14','VDD_3V3') and edge('U95','15','VDD1P8') and all(not any(r=='U1' for r,p in v) for n,v in nets.items() if n.startswith('TFCARD_')),
}
# Source clause IDs cover every numbered section and split independently actionable obligations.
rows=[]
def add(i,page,label,status,target,evidence,check=None):
 if check:assert checks[check],(i,check)
 rows.append(dict(id=i,source_pdf_page=page,requirement_label=label,status=status,target=target,evidence_or_next_action=evidence,automated_check=check))
add('1.1a',1,'I/O voltage','unresolved','BANK0..5_VDDIO; U95; carrier peripherals','Six external bank supplies require matched carrier voltages and startup order. OTP/readback and translation SI remain open.','tf_voltage_separation')
add('1.1b',1,'Power ordering','unresolved','U21 CORE_PGOOD_5V; U24..26; MIPI rails','CORE enables dependent converters. External banks and filtered-rail ramps require measured sequencing; PG structure alone is insufficient.')
add('1.1c',1,'RTC/LDO order','passed_model','U1 F14/F15; AVDD1P8_PMU','Both pins intentionally share the filtered PMU node. This closes relative net ordering, not ramp/PI qualification.','rtc_ldo_common_domain')
add('1.1d',1,'All supplies/grounds','passed_model','All U1 power_in balls; ADC/CODEC','Every modeled power ball has a named network; external bank sources remain explicit board-boundary requirements.','all_soc_power_pins_net_named')
add('1.1e',1,'Analog filters','unresolved','FB202/203/204/207; C231 onward','PLL/VAA/MIPI L-filter topology present. Reference uses120Ω while checklist gives100Ω; impedance/DC-bias/PI and exact approved part require reconciliation.')
add('1.2a',1,'Boot selection','unresolved','BOOT0/BOOT1; R44..R47; J1','PhysicalMMC0 baseline retained. Same-OTP SD/eMMC protocol selection and earliest voltage remain unverified.')
add('1.2b',2,'Boot button','unresolved','Carrier BOOT pins','No button added on core. Carrier must produce a different sampled boot state for recovery; verify actual carrier wiring and reset timing.')
add('1.3a',2,'24MHz accuracy','unresolved','Y2; C43/C44; R42','Exact candidate initial/temp/aging budget does not establish whole-condition20ppm.85°C grade also under review.')
add('1.3b',2,'Passive feedback','passed_model','R42 between24M pins','1M feedback present; load/negative-resistance/drive testing remains open.','24m_feedback')
add('1.3c',2,'Active clock option','not_applicable_current_variant','Y1/Y2 passive','No active oscillator is fitted. A later active substitution must revisit supply, XOUT disposition and waveform requirements.')
add('1.3d',2,'RTC accuracy','unresolved','Y1; C41/C42; R41','MPN/full-temperature drift and startup not qualified; feedback source is Canaan2023 reference, not01Studio RTC drawing.','rtc_feedback')
add('1.4',2,'DDR mapping','unresolved','U1/U2;65-join matrix','65 source-exact joins pass against01Studio reference. Recommended Lushan mapping equivalence and proposedMicron training require review; no vendor submission made.')
add('1.5a',2,'Persistent PMU power','unresolved','AVDD1P8_PMU','Common supply exists while main1V8 runs. Required off/sleep/wake semantics and isolation are not implemented in BSP.')
add('1.5b',2,'PMU inputs','passed_model','PAD68/R401; PAD64/R402','INT4 shares PMU supply through0Ω; INT0 is inactive bias rather than local button. Firmware ownership/startup measurement remains open.','pmu_start_strap')
add('1.6a',3,'Sensor routing/control','unresolved','CSI edge nets; GPIO controls','Physical aliases retained. Sensor pinmux, voltage and carrier connector assignment must be validated for selected peripherals.')
add('1.6b',3,'Sensor ground contacts','deferred_to_layout','CSI pairs;140-pin edge contract','Do not reorder compatible contacts. Audit ground adjacency against original edge order and complete carrier route; add return paths without repurposing pins.')
add('1.7a',3,'Display routing/control','unresolved','DSI edge nets; GPIO controls','Pin contract retained; software/panel voltage and MIPI lane configuration remain untested.')
add('1.7b',3,'Display ground contacts','deferred_to_layout','DSI pairs; edge contract','Connector/return-path audit still required; original compatible numbering must remain fixed.')
add('1.8a',3,'MMC assignment/voltage','unresolved','MMC0 selector; U95; externalTF','Intentional departure from default MMC1SDIO: both storage choices useMMC0 to preserve edge contract. ROM-stage support needs evidence.')
add('1.8b',3,'eMMC pulls','passed_model','R562;R563..570;R572','CMD22k/DAT47k local pulls and host strobe100k bias present. Unused eMMC H5 output stays open.','emmc_pulls')
add('1.8c',3,'SD pulls','unresolved','U95; externalTF socket','Translator internal pulls are documented, but carrier external-pull population and combined strength/RC require confirmation; do not blindly double pullups.')
add('1.9',4,'USB ESD','unresolved','USB0/1 edge pairs; carrier sockets','Protection belongs near actual external connector; no socket/ESD device is presumed present from the core netlist. Require low-capacitance selected part and carrier evidence.')
add('1.10a',4,'MICBIAS setting','unresolved','MIC_BIAS; BSP codec settings','Output setting must match external microphone supply; no active microphone design was selected.')
add('1.10b',4,'MICBIAS decoupling','corrected_model','C67/C68; U1 E3','Added4.7uF+100nF locally. Actual effective capacitance and near-pin placement still required.','micbias_pair')
add('1.10c',4,'Microphone AC coupling','unresolved','MICPL/MICNL/MICPR/MICNR edge pins','Raw compatible core signals retained. Determine series100nF placement on carrier; adding it silently inside core could change DC interface behavior.')
add('1.10d',4,'Headphone AC coupling','unresolved','HPOUTL/HPOUTR edge pins','Carrier coupling/load/amplifier input must be verified. Never connect two driven outputs based on ambiguous prose.')
add('1.10e',4,'VCM decoupling','corrected_model','C63/C66; U1 F3','Added missing4.7uF alongside100nF. Near-pin placement and effective value remain open.','vcm_pair')
add('1.11a',4,'PDM wiring/voltage','unresolved','GenericGPIO edge contract; futureMIC carrier','No PDM microphone fitted on core. Selected pinmux, left/right sharing and voltage belong to BSP/carrier acceptance.')
add('1.11b',4,'I2S wiring/voltage','unresolved','GenericGPIO edge contract; futureaudio carrier','No I2S microphone fitted on core. Selected clock/WS/data and shared-channel policy require integration testing.')
add('1.12',5,'SPI flash wiring/pulls','not_applicable_current_variant','No SPIflash fitted','ExposedGPIO remain unaltered. Any carrier flash needs its own pinmux, voltage and pulls; not implicitly provided by core.')
add('2.1a',5,'Digital PDN placement','deferred_to_layout','CORE/CPU/KPU/DDR_CORE groups','Split rails intentionally differ from merged reference. Local ball-to-cap loops, return paths and total effective capacitance unqualified.')
add('2.1b',5,'DDR PDN placement','deferred_to_layout','U1 DDR IO; U2 VDD2/VDDQ','Keep SoC-side and memory-side local groups; rectangular packing does not satisfy proximity.')
add('2.1c',5,'1.8V PDN placement','deferred_to_layout','VDD1P8; USB; PMU; bank supplies','Common/filtered domain layout and external-bank source boundary must be reviewed.')
add('2.1d',5,'3.3V PDN placement','deferred_to_layout','USB3V3; SD; VOUT; externalbanks','Route/load compatibility and carrier power-return paths remain open.')
add('2.2',6,'Clock shielding','deferred_to_layout','Y1/Y2 XIN/XOUT','Ground shielding and uninterrupted reference plane required; no routed PCB exists.')
add('2.3',6,'DDR layout review','deferred_to_layout','65 DDR joins; package lengths','Source topology alone is not length/impedance/escape validation. Full SI/PI and qualified review needed; no vendor upload authorized.')
add('2.4',6,'eMMC routing','deferred_to_layout','EMMC DAT/CMD/CLK; selector','Apply source length/matching goals, then evaluate added switch discontinuities. No length or HS200 pass claimed.')
add('2.5a',6,'USB matching/impedance','deferred_to_layout','USB0/1 D+/D-','90Ω differential and pair-length objectives must include core plus carrier.')
add('2.5b',6,'USB return/length','deferred_to_layout','USB paths/connector','Continuous ground, via companions, connector distance and neighbor spacing need routing audit.')
add('2.6',7,'MIPI RX routing','deferred_to_layout','CSI lanes','100Ω differential, within-pair/intergroup matching and total-length goals require core+carrier budget.')
add('2.7',7,'MIPI TX routing','deferred_to_layout','DSI lanes','Checklist repeats RX-style group names; resolve the intendedTX grouping rather than invent constraints. Preserve continuous return paths.')
add('2.8',8,'Audio shielding','deferred_to_layout','MIC/HPOUT/MICBIAS','Ground reference, shielding and stitching require layout and carrier audit.')
add('2.9',8,'TF routing','deferred_to_layout','TF_HOST;U95;TFCARD;external socket','Include translation delay and external carrier route; raw trace matching alone cannot prove timing.')
add('2.10',8,'SPI routing','not_applicable_current_variant','No coreSPIflash','Carrier SPI use remains application-specific and outside current core routing validation.')
# External implementation is out of scope; retain only required core interface boundaries.
external={'1.2b','1.6a','1.7a','1.8c','1.9','1.10a','1.10c','1.10d','1.11a','1.11b'}
for r in rows:
 r['scope']='core'
 if r['id'] in external:
  r['status']='external_boundary_only';r['scope']='external implementation excluded by user'
  r['evidence_or_next_action']='Core handoff requirement only; no peripheral circuit designed. '+r['evidence_or_next_action']
 if r['id'] in ['1.6b','1.7b']:
  r['status']='unresolved_compatibility_exception'
  r['evidence_or_next_action']='Original fixed edge pinout has adjacent pairs without intervening ground (CSI58–63;DSI79–88). Preserve numbering; explicitly review return path/crosstalk, not a claimed checklist pass.'
sections={re.match(r'(\d+\.\d+)',r['id']).group(1) for r in rows}
assert sections=={f'1.{i}' for i in range(1,13)}|{f'2.{i}' for i in range(1,11)}
result={'source':'https://kendryte-download.canaan-creative.com/developer/k230/HDK/%E5%8E%9F%E7%90%86%E5%9B%BEPCB%E8%AE%BE%E8%AE%A1CHECKLIST.pdf','scope':'Every numbered section covered; model-level passes only. No submission/contact/simulation/fabrication.','master_sha256':hashlib.sha256((P/'master.xml').read_bytes()).hexdigest(),'checks':checks,'items':rows,'counts':dict(collections.Counter(r['status'] for r in rows))}
D=P/'checklist' if len(sys.argv)>1 else B/'engineering/checklist';D.mkdir(parents=True,exist_ok=True);(D/'official-checklist-ledger.json').write_text(json.dumps(result,indent=2))
text=['# Official checklist audit ledger','',result['scope'],'','Source: '+result['source'],'','| Clause | Page | Requirement | Status | Target | Evidence / next action |','|---|---:|---|---|---|---|']
for r in rows:text.append('| '+ ' | '.join(str(r[k]).replace('|','/') for k in ['id','source_pdf_page','requirement_label','status','target','evidence_or_next_action'])+' |')
(D/'OFFICIAL_CHECKLIST_AUDIT.md').write_text('\n'.join(text)+'\n')
print(len(rows),'items;',len(checks),'automated assertions;',result['counts']);assert all(checks.values())
