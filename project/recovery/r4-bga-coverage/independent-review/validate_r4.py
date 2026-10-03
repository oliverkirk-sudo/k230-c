#!/usr/bin/env python3
"""Independent source/footprint geometry review; does not edit R4."""
from pathlib import Path
import collections,csv,hashlib,json,re
import fitz

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
R4=BASE/'reconstruction-r4/project'
OLD=BASE/'restored-v12-r2_1'
LIB=R4/'cad/recovery-bga-candidates/CMK230_Recovery_BGA_Candidates.pretty'
PDF=BASE/'private-sources/micron-lp4.pdf'
hashes={}
def read(p):
    raw=p.read_bytes();hashes[str(p.relative_to(BASE))]=hashlib.sha256(raw).hexdigest();return raw.decode()
def js(p): return json.loads(read(p))
def sx(p):
    stack=[];roots=[]
    for t in re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()]+',read(p)):
        if t=='(':
            child=[];(stack[-1] if stack else roots).append(child);stack.append(child)
        elif t==')': stack.pop()
        else: stack[-1].append(json.loads(t) if t.startswith('"') else t)
    assert not stack and len(roots)==1
    return roots[0]
def kids(a,k): return [x for x in a if isinstance(x,list) and x and x[0]==k]
def one(a,k):
    v=kids(a,k);return v[0][1:] if v else None
def pair(a,k): return [float(v) for v in one(a,k)[:2]]
checks=[]
def ck(n,p,d=None): checks.append({'check':n,'pass':bool(p),**({'details':d} if d is not None else {})})

# Independently transcribed from the actually inspected Figure 5 image, page 21.
# Each row lists physical columns 1,2,3,4,5,8,9,10,11,12. L/M are absent.
visual='''A DNU DNU VSS VDD2 ZQ0 NC VDD2 VSS DNU DNU
B DNU DQ0_A VDDQ DQ7_A VDDQ VDDQ DQ15_A VDDQ DQ8_A DNU
C VSS DQ1_A DMI0_A DQ6_A VSS VSS DQ14_A DMI1_A DQ9_A VSS
D VDDQ VSS DQS0_t_A VSS VDDQ VDDQ VSS DQS1_t_A VSS VDDQ
E VSS DQ2_A DQS0_c_A DQ5_A VSS VSS DQ13_A DQS1_c_A DQ10_A VSS
F VDD1 DQ3_A VDDQ DQ4_A VDD2 VDD2 DQ12_A VDDQ DQ11_A VDD1
G VSS ODT_CA_A VSS VDD1 VSS VSS VDD1 VSS NC VSS
H VDD2 CA0_A NC CS0_A VDD2 VDD2 CA2_A CA3_A CA4_A VDD2
J VSS CA1_A VSS CKE0_A NC CK_t_A CK_c_A VSS CA5_A VSS
K VDD2 VSS VDD2 VSS NC NC VSS VDD2 VSS VDD2
N VDD2 VSS VDD2 VSS NC NC VSS VDD2 VSS VDD2
P VSS CA1_B VSS CKE0_B NC CK_t_B CK_c_B VSS CA5_B VSS
R VDD2 CA0_B NC CS0_B VDD2 VDD2 CA2_B CA3_B CA4_B VDD2
T VSS ODT_CA_B VSS VDD1 VSS VSS VDD1 VSS RESET_n VSS
U VDD1 DQ3_B VDDQ DQ4_B VDD2 VDD2 DQ12_B VDDQ DQ11_B VDD1
V VSS DQ2_B DQS0_c_B DQ5_B VSS VSS DQ13_B DQS1_c_B DQ10_B VSS
W VDDQ VSS DQS0_t_B VSS VDDQ VDDQ VSS DQS1_t_B VSS VDDQ
Y VSS DQ1_B DMI0_B DQ6_B VSS VSS DQ14_B DMI1_B DQ9_B VSS
AA DNU DQ0_B VDDQ DQ7_B VDDQ VDDQ DQ15_B VDDQ DQ8_B DNU
AB DNU DNU VSS VDD2 VSS VSS VDD2 VSS DNU DNU'''
source={}
for line in visual.splitlines():
    r,*functions=line.split();assert len(functions)==10
    source.update({r+str(c):f for c,f in zip([1,2,3,4,5,8,9,10,11,12],functions)})
rows='A B C D E F G H J K L M N P R T U V W Y AA AB'.split()
coords={}
for b in source:
    row,col=re.fullmatch(r'([A-Z]+)(\d+)',b).groups()
    coords[b]=[round((int(col)-6.5)*.8,6),round((rows.index(row)-10.5)*.65,6)]
pdfhash=hashlib.sha256(PDF.read_bytes()).hexdigest()
ck('Fresh Micron PDF matches established exact source hash',pdfhash=='b29c808baa7e42fca9b7ccc54b673142d26b49a1fee6b3053cc8691c21832552')
pdf=fitz.open(PDF)
circles=[d['rect'] for d in pdf[23].get_drawings() if len(d['items'])==4 and all(i[0]=='c' for i in d['items']) and 3.7<d['rect'].width<4.1 and 3.7<d['rect'].height<4.1]
centers=[((r.x0+r.x1)/2,(r.y0+r.y1)/2) for r in circles]
minx,maxx=min(x for x,y in centers),max(x for x,y in centers)
miny,maxy=min(y for x,y in centers),max(y for x,y in centers)
mech=set()
for x,y in centers:
    col=round((maxx-x)/(maxx-minx)*11)+1
    row=round((y-miny)/(maxy-miny)*21)
    mech.add(rows[row]+str(col))
ck('Fresh mechanical Figure 7 has exactly 200 ball circles and matching mirrored occupancy',len(circles)==200 and len(mech)==200 and mech==set(source))
mapdata=js(R4/'engineering/high-temp-candidates/micron-lp4-ball-comparison.json')
archived={r['ball']:r['function'] for r in mapdata['grid'] if r['physical']}
ck('All 200 freshly transcribed Figure 5 functions match restored Micron map',source==archived)
contract=js(R4/'recovery/r4-bga-coverage/fw200-coordinate-contract.json')
ck('All 200 R4 contract functions and top-view coordinates match fresh source',len(contract)==200 and {r['ball']:r['function'] for r in contract}==source and all([r['x_mm'],r['y_mm']]==coords[r['ball']] for r in contract))

name='Micron_FW200_NSMD030_ENGINEERING_ONLY'
fp=sx(LIB/(name+'.kicad_mod'));pads=kids(fp,'pad')
cu=[p for p in pads if p[1]];paste=[p for p in pads if not p[1]]
ck('FW footprint has 200 unique numbered lands and 200 paste-only objects',len(cu)==200 and len(paste)==200 and len({p[1] for p in cu})==200)
ck('FW exact source occupancy, no absent-site land',set(p[1] for p in cu)==set(source))
ck('FW exact source nominal coordinates and top-view orientation',all(pair(p,'at')==coords[p[1]] for p in cu))
ck('FW copper lands are front Cu/Mask SMD circles, no automatic paste',all(p[2:4]==['smd','circle'] and set(one(p,'layers'))=={'F.Cu','F.Mask'} for p in cu))
ck('FW copper .30 mm, mask radial expansion .05 mm',all(pair(p,'size')==[.3,.3] and float(one(p,'solder_mask_margin')[0])==.05 for p in cu))
ck('FW exactly one .30 mm paste-only SMD circle at every ball center',all(p[2:4]==['smd','circle'] and one(p,'layers')==['F.Paste'] and pair(p,'size')==[.3,.3] for p in paste) and collections.Counter(tuple(pair(p,'at')) for p in paste)==collections.Counter(tuple(v) for v in coords.values()))
rects=kids(fp,'fp_rect')
fab=[r for r in rects if one(r,'layer')==['F.Fab']]
court=[r for r in rects if one(r,'layer')==['F.CrtYd']]
ck('FW F.Fab rectangle centerline is 10.1 by 14.6 mm maximum-body projection',len(fab)==1 and pair(fab[0],'start')==[-5.05,-7.3] and pair(fab[0],'end')==[5.05,7.3])
ck('FW unqualified courtyard is 10.6 by 15.1 mm',len(court)==1 and pair(court[0],'start')==[-5.3,-7.55] and pair(court[0],'end')==[5.3,7.55])
marker=kids(fp,'fp_line')
ck('FW A1 marker is upper-left on F.Fab',len(marker)==1 and one(marker[0],'layer')==['F.Fab'] and pair(marker[0],'start')==[-5.05,-6.6] and pair(marker[0],'end')==[-4.35,-7.3])
ck('FW has no routed/via/copper-zone geometry',not any(kids(fp,k) for k in ['segment','via','zone']))
height_properties={r[1]:r[2] for r in kids(fp,'property') if 'height' in r[1].lower()}

copied=[]
for ref,path in [('U1','cad/bga-engineering-candidates/k230-ddr-constrained/K230_Engineering.pretty/K230_390_NSMD027_ENGINEERING_ONLY.kicad_mod'),('U3','cad/bga-engineering-candidates/bh153-sparse-trial/BH153_Engineering.pretty/MTFC16GAPALBH_AAT_BH153_NSMD030_ENGINEERING_ONLY.kicad_mod')]:
    old=OLD/path;new=LIB/old.name
    a=read(old);b=read(new);ck(ref+' engineering footprint byte-identical to restored source',a==b)
    copied.append({'reference':ref,'footprint':old.stem,'sha256':hashlib.sha256(new.read_bytes()).hexdigest(),'identical':a==b})
native=js(HERE/'native-results.json')
for name,record in native['native_footprints'].items():
    if name.startswith('Micron'):
        digest=hashlib.sha256(json.dumps(coords,sort_keys=True).encode()).hexdigest()
        ck('Native KiCad FW centers and numbers independently match source',record['copper_pad_count']==200 and record['copper_coordinate_sha256']==digest)
checks+=native['checks']
metadata=js(R4/'recovery/r4-bga-coverage/package-metadata.json')
ck('R4 FW package metadata agrees with fresh maximum-body and height callouts',metadata['U2']['part']=='MT53E256M32D2FW-046 AAT:B' and metadata['U2']['body_max_mm']==[10.1,14.6] and metadata['U2']['package_height_max_mm']==1.1 and metadata['U2']['three_dimensional_model'] is None)

report={
    'date_utc':'2026-10-03','status':'PASS_CONDITIONAL_IDENTITY_AND_NOMINAL_GEOMETRY' if all(c['pass'] for c in checks) else 'FAIL',
    'scope':'Independent R4 BGA source identity, orientation, nominal geometry and native CAM check; no main CAD edits or production qualification.',
    'required_board':{'outline_mm':[38,38],'contacts':140,'copper_layers':6,'assembly':'top only'},
    'source':{'title':'Micron 200b x16/x32 Automotive LPDDR4/LPDDR4X, Rev. F 10/2020 EN','sha256':pdfhash,'pages_inspected':[21,24],
        'source_url':'https://www.mouser.com/datasheet/2/671/200b_z00m_sdp_ddp_auto_lpddr4_lpddr4x-3193603.pdf',
        'method':'Actual rendered pages inspected. Figure 5 manually transcribed row by row; Figure 7 ball circles extracted independently and bottom-view columns reversed. Dimensions use printed callouts, not pixel spacing.'},
    'FW200':{'exact_part':'MT53E256M32D2FW-046 AAT:B','physical_ball_count':200,'full_grid_count':264,'absent_count':64,
        'absent_rule':'All L/M row sites and all column 6/7 sites','frame':'Package-centered top view, balls down, X right, Y down',
        'pitch_mm':[.8,.65],'center_spans_mm':[8.8,13.65],'body_nominal_mm':[10,14.5],'body_maximum_mm':[10.1,14.6],
        'height_nominal_mm':1.0,'height_maximum_mm':1.1,'native_height_properties':height_properties,'native_3d_model_present':bool(kids(fp,'model')),
        'copper_mask_paste_mm':[.3,.4,.3],'paste_only_apertures':200,'source_qualified_PCB_land_pattern':False,
        'native_CAM':native['temporary_CAM'],'courtyard_mm':[10.6,15.1],'courtyard_process_qualified':False},
    'copied_candidates':copied,'check_count':len(checks),'checks':checks,'failures':[c for c in checks if not c['pass']],
    'metadata_notes':['FW maximum height 1.1 mm is recorded in package-metadata.json; the footprint has no native height property or 3D model. No collision-checkable height model or assembled-height claim follows.',
        'Copied BH153 F.Fab uses nominal 11.5 x 13.0 mm body, while source maximum is 11.6 x 13.1 mm. Its 12.0 x 13.5 mm courtyard is unqualified.',
        'Copied K230 F.Fab uses maximum 13.1 x 13.1 mm body with a 13.6 x 13.6 mm courtyard. Coordinates preserve missing A1, but the rectangular fabrication outline has no explicit pin-1 corner marker.'],
    'limits':['Copper/mask/paste are explicit engineering choices, not a Micron PCB-land recommendation. The package-side 0.40 mm SMD-pad note is not board-side copper approval.',
        'No stack, HDI/via process, stencil transfer, assembly reliability, thermal, DDR/PDN, full placement, or routed-fit qualification.',
        'This verifies standalone footprint geometry and temporary CAM only; no eight-layer routes were copied or used as six-layer evidence.',
        'No vendor PDF/images or temporary QA board/Gerbers are included in this report directory.'],
    'input_sha256':hashes}
(HERE/'independent-review.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'checks':len(checks),'failures':report['failures'],'height_properties':height_properties},indent=2))
