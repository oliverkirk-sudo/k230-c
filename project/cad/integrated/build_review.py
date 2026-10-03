#!/usr/bin/env python3
import pathlib,csv,json,uuid,collections,re,subprocess
OUT=pathlib.Path(__file__).resolve().parent; BASE=OUT.parents[1]; SRC=BASE/'data/k230-source-extraction'
def read(p):return list(csv.DictReader(open(p)))
def uid():return str(uuid.uuid4())
def q(s):return json.dumps(str(s))
NC_PINS={('U1','A20'),('U1','Y1'),('U1','Y20'),('U1','U6'),('U1','D8')}
LP4_UNUSED={'C20','D19','D20','F18','G17','H18','H19','K20','L17','L18','L20','M17','M20','N18'}
RANK1_UNUSED={'J17','J19','P18','T19'}
NC_PINS.update(('U1',p) for p in LP4_UNUSED|RANK1_UNUSED)
NC_PINS.add(('U3','H5'))
NC_PINS.update({('U89','3'),('U90','3'),('U91','1'),('U93','1'),('U95','6')})
ROOT=uid(); PROJ='CMK230_Core_REVIEW'; symbols={}; sheets=[]; matrix=[]; conflicts=[]
FP={'U95':'CMK230_Translator_Candidate:NXP_SOT1161-2_NVT4858HK_1.8x2.6_P0.4_DrawingVerified_CANDIDATE','Y2':'CMK230_Crystals:YXC_X322524MOB4SI_3225_4P_DrawingCandidate'}
for refs,name in [(['U11','U12','U13'],'TI_RSV0016A_TMUX1574_1.8x2.6_P0.4_DrawingVerified'),(['U14'],'TI_DBV0005A_SN74LVC1G32_SOT23_5_DrawingVerified'),(['U21','U24','U25','U26'],'TI_DMQ0006A_TPS6282xA_1.5x1.5_SMD_DrawingVerified'),(['U22','U23'],'TI_YCG0015_TPS628640_1.05x1.78_P0.35_SMD_DrawingVerified')]:
 for r in refs:FP[r]='CMK230_Verified:'+name
for r in ['U91','U93']:FP[r]='CMK230_Compact_Candidates:TI_DRL0005A_AUP_5P_DrawingVerified_CANDIDATE'
for r in ['U92','U94']:FP[r]='CMK230_Compact_Candidates:TI_DRL0006A_AUP1G97_DrawingVerified_CANDIDATE'
for r in ['U89','U90']:FP[r]='CMK230_Compact_Candidates:TI_DRV0006A_D_TPS3808_6P_EP7_DrawingVerified_CANDIDATE'


def text(s,x=15,y=15):return f'(text {q(s)} (at {x} {y} 0) (effects (font (size 1.15 1.15)) (justify left)) (uuid "{uid()}"))'
def define(name,groups):
 ss=[f'(symbol "Integrated:{name}" (pin_names (offset 1.016)) (in_bom yes) (on_board yes) (property "Reference" "U" (at 0 0 0) (effects (font (size 1.27 1.27)))) (property "Value" "{name}" (at 0 0 0) (effects (font (size 1.27 1.27))))'];pos={}
 for n,g in enumerate(groups,1):
  h=(len(g)+1)*1.27;ss.append(f'(symbol "{name}_{n}_1" (rectangle (start -25.4 {h}) (end 35.56 {-h}) (stroke (width .254) (type default)) (fill (type background)))')
  for i,(p,fn,typ) in enumerate(g):
   yy=(len(g)-1)*1.27-i*2.54;pos[(n,str(p))]=(-30.48,yy)
   ss.append(f'(pin {typ} line (at -30.48 {yy:.4f} 0) (length 5.08) (name {q(fn)} (effects (font (size .65 .65)))) (number {q(p)} (effects (font (size .8 .8)))))')
  ss.append(')')
 ss.append(')');symbols[name]={'s':'\n'.join(ss),'pos':pos,'groups':groups}
def start(title):
 sh={'id':uid(),'sid':uid(),'name':f'{len(sheets)+1:02d}_{title}','title':title,'body':[],'libs':set()};sheets.append(sh);return sh
def place(sh,name,ref,val,unit,x,y,nets,status='',dnp=False,onboard=True):
 x=round(x/1.27)*1.27;y=round(y/1.27)*1.27
 fp_prop=f'(property \"Footprint\" {q(FP.get(ref,""))} (at {x} {y} 0) (effects (font (size 1 1)) hide))'
 sh['libs'].add(name);h=symbols[name].get('h',(len(symbols[name]['groups'][unit-1])+1)*1.27)
 sh['body'].append(f'(symbol (lib_id "Integrated:{name}") (at {x} {y} 0) (unit {unit}) (in_bom {"yes" if onboard else "no"}) (on_board {"yes" if onboard else "no"}) (dnp {"yes" if dnp else "no"}) (uuid "{uid()}") (property "Reference" "{ref}" (at {x} {y-h-5} 0) (effects (font (size 1.27 1.27)))) (property "Value" {q(val)} (at {x} {y-h-2} 0) (effects (font (size .9 .9)))) {fp_prop} (instances (project "{PROJ}" (path "/{ROOT}/{sh["sid"]}" (reference "{ref}") (unit {unit})))))')
 for p,fn,typ in symbols[name]['groups'][unit-1]:
  p=str(p);net=nets.get(p,'');dx,dy=symbols[name]['pos'][(unit,p)];px=x+dx;py=y-dy;lx=px-5.08
  matrix.append(dict(reference=ref,unit=unit,pin=p,function=fn,net=net,status=(why.get(p,status) if ref=='U1' else status) if net else ('MANUAL_EMMC_GRID_NC_RFU_REVIEW_OPEN' if ref=='U3' and fn in ['NC','RFU'] else 'OPEN_TBD_NO_NC_FLAG'),sheet=sh['name']))
  if (ref,p) in NC_PINS:
   assert not net
   matrix[-1]['status']='TPS386000_CT_OPEN_FIXED_20MS' if ref=='U81' and p in ['2','3','4','5'] else 'TPS386000_UNUSED_REFERENCE_OR_WATCHDOG_OUTPUT' if ref=='U81' and p in ['13','19'] else 'TPS3850_WATCHDOG_DISABLED_CWD_OPEN' if ref in ['U84','U85','U86','U88'] and p=='2' else 'UNUSED_WATCHDOG_OUTPUT' if ref in ['U84','U85','U86','U88'] and p=='8' else 'TPS3808_CT_OPEN_SELECTS_20MS' if ref in ['U89','U90'] and p=='3' else 'OPTIONAL_TF_CLOCK_FEEDBACK_UNUSED_TIMING_GATE' if ref=='U95' and p=='6' else 'OFFICIAL_PINOUT_LP4_MODE_UNUSED' if ref=='U1' and p in LP4_UNUSED else 'REFERENCE_SINGLE_RANK_UNUSED_OUTPUT' if ref=='U1' and p in RANK1_UNUSED else 'EMMC_HS200_UNUSED_HS400_STROBE_OUTPUT' if ref=='U3' and p=='H5' else 'REFERENCE_UNUSED_ANALOG_TEST_OUTPUT' if ref=='U1' and p=='D8' else 'GUIDE_EXPLICIT_MIPI_ATB_FLOAT' if ref=='U1' and p=='U6' else 'MANUFACTURER_RFU_NO_USE_MUST_REMAIN_OPEN' if fn=='RFU' else 'MANUFACTURER_NC_DNU_MUST_REMAIN_OPEN'
   sh['body'].append(f'(no_connect (at {px:.4f} {py:.4f}) (uuid "{uid()}"))')
  if net:
   sh['body'] += [f'(wire (pts (xy {px:.4f} {py:.4f}) (xy {lx:.4f} {py:.4f})) (stroke (width 0) (type default)) (uuid "{uid()}"))',f'(global_label {q(net)} (shape bidirectional) (at {lx:.4f} {py:.4f} 0) (effects (font (size .85 .85)) (justify right)) (uuid "{uid()}"))']
def chunks(a,n=40):return [a[i:i+n] for i in range(0,len(a),n)]
def multipages(name,ref,val,groups,nets,title,status,onboard=True):
 define(name,groups)
 for i,g in enumerate(groups):
  if i%4==0:
   sh=start(title+f'_{i//4+1}');sh['body'].append(text('REVIEW ONLY - unresolved pins intentionally open; no fabrication footprint. '+status))
  place(sh,name,ref,val,i+1,110+(i%2)*195,80+((i%4)//2)*125,nets,status,onboard=onboard)
 return
soc=read(SRC/'k230-390-balls.csv'); canon={r['soc_ball']:r['soc_signal'] for r in soc}; sn={};why={}
def assign(ball,net,source):
 if ball in sn and sn[ball]!=net:conflicts.append([ball,sn[ball],net,why[ball],source]);return
 sn[ball]=net;why[ball]=source
module=read(BASE/'engineering/module-to-soc-candidates.csv'); edges=read(BASE/'data/cm-k230-pinmap.csv')
for r in module:
 if r['soc_ball']:
  assert canon[r['soc_ball']]==r['soc_signal']
  if not r['module_name'].startswith('TFCARD_') and r['module_name']!='RSTN':assign(r['soc_ball'],r['module_name'],'module-name correspondence CANDIDATE')
for b,n in {'B10':'PWR_CPU_SCL','A10':'PWR_CPU_SDA','A11':'PWR_KPU_SCL','D12':'PWR_KPU_SDA','A9':'GND','C12':'PMU_INT4_AUTO_START','C10':'PMU_INT0','B11':'PMU_OUT0_STATUS','C11':'PMU_OUT1_STATUS'}.items():assign(b,n,'parent verified private GPIO assignment / TEST_EN ground')
for b,n in {'K17':'DDR_VREF','K19':'DDR_ZN','U7':'MIPI_REXT','A3':'USB1_VBUS','C3':'USB0_VBUS','C4':'USB1_TXRTUNE','D4':'USB0_TXRTUNE','F3':'CODEC_VCM'}.items():assign(b,n,'parent verified 01studio bias source')
for r in soc:
 b,f=r['soc_ball'],r['soc_signal']
 if f.startswith('MMC0_'):assign(b,f,'dedicated storage path; strobe unresolved')
 if f in ['VSS','AVSS']:assign(b,'GND','named ground ball')
 if f.startswith(('VDD','AVDD','VAA')) and b not in sn:assign(b,'AVDD1P8_PMU' if f in ['AVDD1P8_RTC','AVDD1P8_LDO'] else f,'canonical rail endpoint; PMU shared RTC/LDO filtered domain')
for b,n in {'B12':'RTC_XIN','A12':'RTC_XOUT','B8':'CLK24_XIN','A8':'CLK24_XOUT','B9':'SOC_RSTN','C8':'BOOT0','C9':'BOOT1'}.items():assign(b,n,'existing aux')
ddr=read(SRC/'01studio-soc-to-lpddr4-65nets.csv');rn={'G2':'LPDDR4_ODT_A','T2':'LPDDR4_ODT_B','A5':'LPDDR4_ZQ'}
for r in ddr:assign(r['soc_ball'],r['reference_net'],'01studio exact DDR join');rn[r['dram_ball']]=r['reference_net']
TYPE_MAP=json.loads((BASE/'engineering/pin-types/k230-type-audit-manifest.json').read_text())['proposed_compact_pin_types']
assert set(TYPE_MAP)==set(canon)
groups=[]
for unit in sorted(set(r['source_unit'] for r in soc)):
 groups+=chunks([(r['soc_ball'],r['soc_signal'],TYPE_MAP[r['soc_ball']]) for r in soc if r['source_unit']==unit])
multipages('K230_390','U1','K230 full 390 physical balls',groups,sn,'SoC','Module correspondence is candidate; no GPIO repurposing')
MEMORY_TYPES=json.loads((BASE/'engineering/pin-types/memory-type-audit-manifest.json').read_text())['proposed_pin_types']
ram=[r for r in read(BASE/'engineering/memory/K4F8E304HB_grid264_physical200.csv') if r['physical_ball']=='True'];assert len(ram)==200
for r in ram:
 if r['function'] in ['NC','DNU']:NC_PINS.add(('U2',r['ball_or_grid']))
 if r['function'].startswith('VSS'):rn[r['ball_or_grid']]='GND'
 # Keep memory supplies distinct and undriven for power integration.
 if r['function'] in ['VDD1','VDD2','VDDQ']:rn[r['ball_or_grid']]={'VDD1':'VDD1P8','VDD2':'VDD1P1_DDR_IO','VDDQ':'VDD1P1_DDR_IO'}[r['function']]
multipages('K4F8E304HB_200','U2','K4F8E304HB 1GB LPDDR4 REVIEW',chunks([(r['ball_or_grid'],r['function'],MEMORY_TYPES['U2'][r['ball_or_grid']]) for r in ram]),rn,'LPDDR4','65 exact SoC joins; source NC/DNU flagged; bias on dedicated sheet')
em=[r for r in read(BASE/'engineering/memory/KLMAG1JETD_grid196_physical153.csv') if r['physical_ball']=='True'];assert len(em)==153
for r in em:
 if r['function'] in ['NC','RFU']:
  assert r['status']=='SOURCE_P5_VECTOR_CIRCLE_AND_LABEL_VERIFIED'
  NC_PINS.add(('U3',r['ball_or_grid']))
en={};explicit=read(BASE/'engineering/memory/KLMAG1JETD_explicit_function_balls.csv')
for r in explicit:
 f=r['function'];n= 'EMMC_'+f if f.startswith('DAT') or f in ['CMD','CLK','RSTN'] else {'VSS':'GND','VDD':'VEMMC_IO','VDDF':'VDD_3V3','VDDI':'EMMC_VDDI'}.get(f)
 if n:en[r['ball']]=n
multipages('KLMAG1JETD_153','U3','KLMAG1JETD 16GB eMMC REVIEW',chunks([(r['ball_or_grid'],r['function'],MEMORY_TYPES['U3'][r['ball_or_grid']]) for r in em]),en,'eMMC','153-ball grid verified; NC/RFU no-use flagged; VDDI analog stabilization only; reference caps unqualified; HS400 strobe unused')
multipages('CMK230_140_CONTRACT','J1','CM-K230 edge contract ONLY',chunks([(r['pin'],r['name'],'passive') for r in edges],35),{r['pin']:{'VOUT_3V3':'VDD_3V3','VOUT_1V8':'VDD1P8'}.get(r['name'],r['name']) for r in edges},'Edge_Contract','140 same-module pads; NOT carrier footprint',False)
# Reuse source circuit declarations, never execute their writes.
for src,title in [('generate_core_aux.py','Clock_Reset_Boot'),('generate_storage_switch.py','Cold_Storage_Selector'),('generate_power.py','Six_Rail_Power'),('generate_bias.py','DDR_USB_MIPI_Bias'),('generate_decoupling.py','Local_Decoupling'),('generate_pmu_startup.py','PMU_Automatic_Startup'),('generate_emmc_support.py','EMMC_Local_Bias'),('generate_supervisor.py','Hardware_Reset_Interlock'),('generate_tf_translator.py','TF_Voltage_Translation')]:
 ns={'__file__':str(BASE/'tools'/src)};code=(BASE/'tools'/src).read_text().split('sch=[',1)[0].split('# Assigned references intentionally',1)[0].split('\nwith (root/',1)[0];exec(code,ns)
 sh=start(title);sh['paper']='A2' if title=='Hardware_Reset_Interlock' else 'A0' if title in ['Six_Rail_Power','Local_Decoupling'] else 'A3';sh['body'].append(text('REVIEW: reset/storage release, complete rail validation and firmware remain gates; no fabrication release'))
 if title=='DDR_USB_MIPI_Bias':sh['body'] += [text('C61 is across TOP VREF resistor. EMMC_VDDI is an internal regulator node; C64+C65 are OLIMEX3V3 reference values; Samsung1V8/ESR qualification remains open.',15,240)]
 if title=='Six_Rail_Power':sh['body'] += [text('CPU/KPU: separate private software I2C buses; both 0.8 V startup/address 0x49. CORE PG gates downstream EN.',15,24),text('Shared AVDD1P8_PMU feeds RTC and LDO. Full reset and storage-safe release policy remains incomplete.',15,805)]
 if title=='Local_Decoupling':sh['body'] += [text('77 caps: source RAM groups plus declared new digital baseline. Top-side only; no placement or PI qualification.',15,24)]
 for name,s in ns['symbols'].items():
  if name=='K230_AUX_SUBSET':continue
  new=title+'_'+name
  # Reconstruct exact pin numbers/types from source symbol definition.
  pins=re.findall(r'\(pin (\w+) line .*?\(name "([^"]+)" .*?\(number "([^"]+)"',s['str'],re.S)
  symbols[new]={'s':re.sub(r'\(symbol "[^"]+:','(symbol "Integrated:',s['str'],count=1).replace('Integrated:'+name+'"','Integrated:'+new+'"',1).replace('(symbol "'+name+'_','(symbol "'+new+'_'),'pos':{(1,p):xy for p,xy in s['positions'].items()},'groups':[[(p,n,t) for t,n,p in pins]],'h':s['h']}
 for name,ref,val,x,y,nets,dnp in ns['comps']:
  if ref=='U1':continue
  nets={p:{'VDD_1V8':'VDD1P8','VSW_3V3':'VDD_3V3'}.get(n,n) for p,n in nets.items()}
  place(sh,title+'_'+name,ref,val,1,x,y,nets,'existing reference subcircuit; integration unqualified',dnp)
# Explicit CAD source semantics, generated only from audited passive source paths.
paths=json.loads((OUT/'power-source-paths.json').read_text())
assert len(paths) in [17,18] and all(r['passive_path'] for r in paths)
assert not any(r['net'].startswith('BANK') for r in paths)
sh=start('Audited_Source_Declarations')
sh['body'] += [text('CAD power-source declarations ONLY. Each internal source has a traced U21-U26 SW / L / FB / 0R path.',15,15),text('These are not extra components or a claim of voltage, sequencing, loop, thermal or PCB qualification.',15,23),text('VIN_5V and GND are external input-contract sources. Bank declarations express required external inputs; VCCQ has an actual conditional1V8 feed.',15,31)]
define('AUDITED_SOURCE',[[('1','SOURCE_DECLARATION','power_out')]])
entries=paths+[{'net':'VIN_5V','source':'EXTERNAL_INPUT_5V'},{'net':'GND','source':'EXTERNAL_GROUND_RETURN'}]+[{'net':f'BANK{x}_VDDIO','source':f'REQUIRED_EXTERNAL_BANK{x}_SUPPLY'} for x in range(6)]
for j,r in enumerate(entries):
 place(sh,'AUDITED_SOURCE',f'#PS{j+1:03d}',r['source'],1,75+(j%3)*128,55+(j//3)*25,{'1':r['net']},'CAD_DECLARATION_TRACEABLE_NOT_HARDWARE_PART',onboard=False)

# Metadata and self-contained libraries.
for sh in sheets:
 paper=sh.get('paper','A3')
 body=[f'(kicad_sch (version 20250114) (generator "cmk230_review") (uuid "{sh["id"]}") (paper "{paper}") (title_block (title {q(sh["title"]+" - REVIEW ONLY")}) (rev "REVIEW-D3-v8")) (lib_symbols '+''.join(symbols[n]['s'] for n in sorted(sh['libs']))+')']+sh['body']+['(embedded_fonts no))']
 (OUT/(sh['name']+'.kicad_sch')).write_text('\n'.join(body))
body=[f'(kicad_sch (version 20250114) (generator "cmk230_review") (uuid "{ROOT}") (paper "A3") (title_block (title "CM-K230 38x38 mm replacement - integrated REVIEW") (rev "REVIEW-D3-v8")) (lib_symbols)',text('REVIEW ONLY: 1GB LPDDR4 + 16GB eMMC / cold exclusive TF. NOT a PCB or fabrication release.'),text('Global nets join sheets. U1 is the only SoC. Unresolved pins remain open; documented unused pins have explicit no-use markers.',15,23),text('140-pad perimeter contract is logical only. 17 small-IC and 1 crystal footprints assigned; BGA and module-edge fabrication geometry remain unqualified.',15,31)]
for i,sh in enumerate(sheets):
 x=20+(i%3)*130;y=48+(i//3)*39
 body.append(f'(sheet (at {x} {y}) (size 115 23) (stroke (width .254) (type default)) (fill (color 0 0 0 0)) (uuid "{sh["sid"]}") (property "Sheetname" "{sh["title"]}" (at {x} {y-1} 0) (effects (font (size 1.27 1.27)) (justify left bottom))) (property "Sheetfile" "{sh["name"]}.kicad_sch" (at {x} {y+24} 0) (effects (font (size 1 1)) (justify left top))) (instances (project "{PROJ}" (path "/{ROOT}" (page "{i+2}")))))')
body+=['(embedded_fonts no))'];(OUT/(PROJ+'.kicad_sch')).write_text('\n'.join(body));(OUT/(PROJ+'.kicad_pro')).write_text(json.dumps({'meta':{'filename':PROJ+'.kicad_pro','version':1}},indent=2))
(OUT/'Integrated.kicad_sym').write_text('(kicad_symbol_lib (version 20241209) (generator "cmk230_review")'+''.join(s['s'].replace('Integrated:','',1) for s in symbols.values())+')')
(OUT/'sym-lib-table').write_text('(sym_lib_table (lib (name "Integrated") (type "KiCad") (uri "${KIPRJMOD}/Integrated.kicad_sym") (options "") (descr "Review only physical-pin symbols")))')
with open(OUT/'master-pin-assignments.csv','w') as f:w=csv.DictWriter(f,fieldnames=matrix[0]);w.writeheader();w.writerows(matrix)
validation={'soc_physical_pins':len(soc),'ram_physical_pins':len(ram),'emmc_physical_pins':len(em),'contract_pins':len(edges),'ddr_joins':len(ddr),'module_candidate_matches':sum(bool(r['soc_ball']) for r in module),'assignment_conflicts':conflicts,'duplicate_reference_pin':[k for k,c in collections.Counter((r['reference'],r['pin']) for r in matrix).items() if c>1],'unassigned_pins':sum(not r['net'] for r in matrix),'manufacturer_nc_flags':len(NC_PINS),'open_review_pins':sum(not r['net'] and (r['reference'],r['pin']) not in NC_PINS for r in matrix),'sheets':len(sheets),'component_references':sorted(set(r['reference'] for r in matrix))}
(OUT/'source-validation.json').write_text(json.dumps(validation,indent=2));assert not conflicts;assert not validation['duplicate_reference_pin'];print(json.dumps(validation,indent=2))

(OUT/"fp-lib-table").write_text('(fp_lib_table (lib (name "CMK230_Verified") (type "KiCad") (uri "${KIPRJMOD}/../verified-footprints/CMK230_Verified.pretty") (options "") (descr "Drawing-verified small IC footprints; process qualification required")) (lib (name "CMK230_Compact_Candidates") (type "KiCad") (uri "${KIPRJMOD}/../verified-footprints/compact-options/CMK230_Compact_Candidates.pretty") (options "") (descr "Compact package candidates; pin-remap verified")) (lib (name "CMK230_Crystals") (type "KiCad") (uri "${KIPRJMOD}/../verified-footprints/crystals/CMK230_Crystals.pretty") (options "") (descr "Manufacturer crystal land candidate; process and oscillator unqualified")) (lib (name "CMK230_Translator_Candidate") (type "KiCad") (uri "${KIPRJMOD}/../verified-footprints/translator-candidate/CMK230_Translator_Candidate.pretty") (options "") (descr "NVT4858 drawing candidate; process and SI unqualified")))')
