from pathlib import Path
import json,re,shutil,ast
R=Path(__file__).resolve().parent;P=R/'project';A=P/'cad/recovery-physical-candidate';O=P/'recovery/r7-links-and-features';O.mkdir(parents=True,exist_ok=True)
LIB='CMK230_Recovery_Link_Candidates';LD=P/'cad/recovery-link-candidates'/(LIB+'.pretty');LD.mkdir(parents=True,exist_ok=True)
FP=dict.fromkeys(['R205','R206'],'CMK230_Passive_Candidates:Vishay_TNPW0402_IPC7351_SourceLand_PROCESS_CANDIDATE')
FP.update(dict.fromkeys(['R221','R401','R528'],'CMK230_Recovery_Passive_Candidates:Vishay_CRCW0201_SourceLand_PROCESS_CANDIDATE'))
FP.update({'R220':LIB+':Vishay_WSL0603_9_SourceLand_PROCESS_CANDIDATE','R561':LIB+':Vishay_WFZ0402_SourceLand_PROCESS_CANDIDATE','JP1':LIB+':Core_Cold_Selector_Open_SolderBridge_CANDIDATE','TP81':LIB+':Core_PMUSTATUS_Top_TestPad_0p8_CANDIDATE','TP82':LIB+':Core_PMUSTATUS_Top_TestPad_0p8_CANDIDATE'})
features={'JP1','TP81','TP82'}
def roots(s):
 depth=0;q=False;esc=False;start=None
 for i,c in enumerate(s):
  if q:
   if esc:esc=False
   elif c=='\\':esc=True
   elif c=='"':q=False
  elif c=='"':q=True
  elif c=='(':
   if depth==1:start=i
   depth+=1
  elif c==')':
   depth-=1
   if depth==1 and start is not None:yield start,i+1,s[start:i+1];start=None
changed=[]
for f in A.glob('*.kicad_sch'):
 s=f.read_text();edits=[]
 for a,b,t in roots(s):
  if not t.startswith('(symbol '):continue
  m=re.search(r'\(property "Reference" "([^"]+)"',t)
  if m and m[1]in FP:
   ref=m[1];old=re.search(r'\(property "Footprint" "([^"]*)"',t);assert old and not old[1]
   nt=t[:old.start(1)]+FP[ref]+t[old.end(1):]
   if ref in features:
    assert '(in_bom yes)'in nt and '(on_board yes)'in nt
    nt=nt.replace('(in_bom yes)','(in_bom no)',1)
   edits.append((a,b,nt));changed.append(ref)
 for a,b,t in reversed(edits):s=s[:a]+t+s[b:]
 if f.name=='CMK230_Core_REVIEW.kicad_sch':s=s.replace('RCV-R6','RCV-R7')
 if edits or f.name=='CMK230_Core_REVIEW.kicad_sch':f.write_text(s)
assert sorted(changed)==sorted(FP)
def header(name,descr,feature=False):
 return [f'(footprint "{name}" (version 20241229) (generator "cmk230_candidate") (layer "F.Cu") (descr "{descr}")', '(attr smd'+(' exclude_from_pos_files exclude_from_bom'if feature else'')+')', '(fp_text reference "REF**" (at 0 -1.5) (layer "F.SilkS") (effects (font (size 1 1) (thickness .15))))',f'(fp_text value "{name}" (at 0 1.5) (layer "F.Fab") (effects (font (size .8 .8) (thickness .12))))']
def rect(x,y,layer):return f'(fp_rect (start {-x/2} {-y/2}) (end {x/2} {y/2}) (stroke (width .05) (type default)) (fill none) (layer "{layer}"))'
for ref,pad,gap,body,court in [('R220',(1.01,1.01),.50,(1.80,1.02),(3.12,1.62)),('R561',(.50,.60),.40,(1.10,.60),(2.00,1.20))]:
 name=FP[ref].split(':')[1];xs=[-(pad[0]+gap)/2,(pad[0]+gap)/2];lines=header(name,'Manufacturer source copper; nonpolar. Body envelope conservative. Mask paste courtyard and hot electrical behavior unqualified.')+[rect(*body,'F.Fab'),rect(*court,'F.CrtYd')]
 for num,x in enumerate(xs,1):
  lines.append(f'(pad "{num}" smd rect (at {x} 0) (size {pad[0]} {pad[1]}) (layers "F.Cu" "F.Mask") (solder_mask_margin .05))')
  lines.append(f'(pad "" smd rect (at {x} 0) (size {pad[0]} {pad[1]}) (layers "F.Paste"))')
 lines.append(')');(LD/(name+'.kicad_mod')).write_text('\n'.join(lines)+'\n')
name=FP['JP1'].split(':')[1];lines=header(name,'Fabricated copper feature. Normally open: no connecting copper and no paste. Bridge only with power off. DNP means bridge absent, not copper omitted.',True)+[rect(2.4,1.8,'F.CrtYd')]
for number,x in [(1,-.5),(2,.5)]:lines.append(f'(pad "{number}" smd rect (at {x} 0) (size .7 1.0) (layers "F.Cu" "F.Mask") (solder_mask_margin .05))')
lines.append(')');(LD/(name+'.kicad_mod')).write_text('\n'.join(lines)+'\n')
name=FP['TP81'].split(':')[1];lines=header(name,'Bare top copper observation pad; no drive injection, no paste, no hole, no purchased part. Probe access and process unqualified.',True)+[rect(1.4,1.4,'F.CrtYd'),'(pad "1" smd circle (at 0 0) (size .8 .8) (layers "F.Cu" "F.Mask") (solder_mask_margin .05))',')'];(LD/(name+'.kicad_mod')).write_text('\n'.join(lines)+'\n')
entry=' (lib (name "'+LIB+'") (type "KiCad") (uri "${KIPRJMOD}/../recovery-link-candidates/'+LIB+'.pretty") (options "") (descr "Source-derived zero links and explicitly proposed fabricated copper features"))'
f=A/'fp-lib-table';s=f.read_text().rstrip();f.write_text(s[:-1]+entry+')\n')
f=A/'build_review.py';s=f.read_text().replace('RCV-R6','RCV-R7');s=s.replace('\n\ndef text(','\nFP.update('+repr(FP)+')\nPCB_FEATURE_REFS={\'J1\',\'JP1\',\'TP81\',\'TP82\'}\n\ndef text(',1)
old='{"yes" if onboard else "no"}';assert s.count(old)==1;s=s.replace(old,'{"yes" if onboard and ref not in PCB_FEATURE_REFS else "no"}',1)
old='onboard or ref=="J1"';assert s.count(old)==1;s=s.replace(old,'onboard or ref in PCB_FEATURE_REFS',1)
s+='\np=OUT/\'fp-lib-table\'; t=p.read_text().rstrip(); p.write_text(t[:-1]+'+repr(entry)+"+')')\n";ast.parse(s);f.write_text(s)
(O/'assignments.json').write_text(json.dumps(FP,indent=2)+'\n')
(O/'feature-contract.json').write_text(json.dumps({'features':{'JP1':{'pins':{'1':'MODE_TF','2':'VDD_3V3'},'DNP':True,'default':'OPEN; eMMC mode; no copper short or paste','service':'power off and discharge before manual solder bridge change; boot/OTP compatibility remains unqualified'},'TP81':{'pins':{'1':'PMU_OUT0_STATUS'},'DNP':False,'use':'observation only'},'TP82':{'pins':{'1':'PMU_OUT1_STATUS'},'DNP':False,'use':'observation only'}},'on_board_required':True,'board_only_flag_required':False,'exclude_from_bom':True,'exclude_from_position':True,'copper_retained_even_when_DNP':True,'geometry_status':'engineering proposal; no manufacturer/factory approval'},indent=2)+'\n')
d=O/'source-review';d.mkdir(exist_ok=True)
for p in (R.parent/'precision-zero-source-review').iterdir():
 if p.is_file()and p.suffix in ['.md','.json']:shutil.copyfile(p,d/p.name)
print('Assigned7 passive identities and3 retained-on-board copper features')
