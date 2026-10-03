"""Explicit transcription of Canaan Figure3-12 net endpoints; NOT a released netlist."""
import csv,pathlib
root=pathlib.Path(__file__).resolve().parents[1]
mem={r['function']:r['ball_or_grid'] for r in csv.DictReader((root/'engineering/memory/K4F8E304HB_grid264_physical200.csv').open()) if r['category']=='SIGNAL'}
connections=[]
def add(logical,soc,mfn):
 connections.append({'reference_net':logical,'K230_ball':soc,'Samsung_function':mfn,'Samsung_ball':mem[mfn],'source':'Canaan hardware guide Figure3-12 image023 + Samsung p10','status':'PROPOSED_DUAL_CHANNEL_ADAPTATION_NOT_TRAINING_VALIDATED'})
for ch,balls in [('A','U16 T16 V16 Y16 W18 V18 Y18 U17 R17 T18 R18 U20 W19 U18 P16 T17'),('B','D17 D16 E18 E17 C17 C18 C19 B19 D14 A14 B14 C14 B17 C16 A17 B16')]:
 for i,b in enumerate(balls.split()):add(f'DQ_{ch}{i}',b,f'DQ{i}_{ch.lower()}')
for ch,balls in [('A','M19 L16 N19 N20 M18 P19'),('B','E20 G19 G18 H17 F17 F19')]:
 for i,b in enumerate(balls.split()):add(f'CA_{ch}{i}',b,f'CA{i}_{ch.lower()}')
for ch,ck,dqs,dmi,cs,cke in [('A','R19 R20','W17 Y17 V20 V19','V17 P17','T20','N17'),('B','G20 F20','B18 A18 B15 A15','D18 C15','J20','J18')]:
 for edge,b in zip(['t','c'],ck.split()):add(f'CK_{edge.upper()}_{ch}',b,f'CK_{edge}_{ch.lower()}')
 for (i,e),b in zip([(0,'t'),(0,'c'),(1,'t'),(1,'c')],dqs.split()):add(f'DQS{i}_{e.upper()}_{ch}',b,f'DQS{i}_{e}_{ch.lower()}')
 for i,b in enumerate(dmi.split()):add(f'DMI{i}_{ch}',b,f'DMI{i}_{ch.lower()}')
 add('CS_'+ch,cs,'CS_'+ch.lower());add('CKE_'+ch,cke,'CKE_'+ch.lower())
add('RESET_N_A_B','J16','RESET_n')
assert len(connections)==65
assert len({r['K230_ball'] for r in connections})==65
assert len({r['Samsung_ball'] for r in connections})==65
with (root/'engineering/memory/ddr-reference-adaptation-candidates.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=connections[0]);w.writeheader();w.writerows(connections)
print('65 unique SoC/DRAM function endpoint candidates; no power/termination/decoupling netlist')
