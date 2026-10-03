#!/usr/bin/env python3
"""Isolated reproducible fixture; never modifies the supplied source project."""
import argparse, collections, copy, csv, hashlib, json, os
from pathlib import Path
import re, subprocess, sys
import xml.etree.ElementTree as ET
import pcbnew as k
import derive_assembly_paste as policy


def save(b, path):
    if not k.SaveBoard(str(path), b): raise RuntimeError('SaveBoard failed')

def primitive(f, layer, x, y):
    s=k.PCB_SHAPE(f); s.SetShape(k.SHAPE_T_RECT); s.SetLayer(layer)
    s.SetStart(k.VECTOR2I(k.FromMM(x),k.FromMM(y)))
    s.SetEnd(k.VECTOR2I(k.FromMM(x+.18),k.FromMM(y+.18)))
    s.SetFilled(True); s.SetWidth(0); f.Add(s)

def paste_aperture(f, layer, x, y):
    p=k.PAD(f); p.SetNumber(''); p.SetAttribute(k.PAD_ATTRIB_SMD)
    p.SetShape(k.PAD_SHAPE_RECT); p.SetSize(k.VECTOR2I(k.FromMM(.2),k.FromMM(.2)))
    p.SetPosition(k.VECTOR2I(k.FromMM(x),k.FromMM(y)))
    ls=k.LSET(); ls.AddLayer(layer); p.SetLayerSet(ls); f.Add(p)

def make_fixture(project, out):
    master=project/'cad/recovery-physical-candidate/master.xml'
    components=policy.component_map(master)
    contract=policy.read_contract(project/'tools/population_contract.py')
    b=k.BOARD(); b.SetCopperLayerCount(2)
    net=k.NETINFO_ITEM(b,'POLICY_FIXTURE_ONLY'); b.Add(net)
    master_nodes={(node.get('ref'),node.get('pin')): n.get('name')
                  for n in ET.parse(master).findall('./nets/net') for node in n.findall('node')}
    native_nets={}
    for name in sorted(set(master_nodes.values())):
        native_nets[name]=k.NETINFO_ITEM(b,name); b.Add(native_nets[name])
    positions={'R528':(10,10), 'R45':(20,10), 'R47':(30,10),
               'R529':(10,20), 'R46':(20,20), 'JP1':(30,20), 'TP81':(10,30), 'TP82':(20,30)}
    fps={}; libs=[]
    for ref,(x,y) in positions.items():
        c=components[ref]; lib,name=c.findtext('footprint').split(':')
        sub='recovery-passive-candidates' if ref.startswith('R') else 'recovery-link-candidates'
        library=project/'cad'/sub/(lib+'.pretty'); libs.append(library/(name+'.kicad_mod'))
        f=k.FootprintLoad(str(library),name)
        f.SetFPIDAsString(c.findtext('footprint')); f.SetReference(ref); f.SetValue(c.findtext('value'))
        b.Add(f); f.SetPosition(k.VECTOR2I(k.FromMM(x),k.FromMM(y)))
        for p in f.Pads():
            if p.GetNumber(): p.SetNet(native_nets[master_nodes[(ref,p.GetNumber())]])
        contract.apply_population(c,f)
        if ref in {'R45','R46'}: f.Flip(f.GetPosition(),k.FLIP_DIRECTION_LEFT_RIGHT)
        fps[ref]=f
    # Deliberate synthetic graphic and standalone aperture cases on both fitted and DNP footprints.
    for ref,layer,x,y in [('R528',k.F_Paste,10,11),('R45',k.B_Paste,20,11),
                         ('R529',k.F_Paste,10,21),('R46',k.B_Paste,20,21)]:
        primitive(fps[ref],layer,x,y); paste_aperture(fps[ref],layer,x+.5,y)
    # Exercise removal of paste from a copper-connected pad as well as separate apertures.
    for ref,layer in [('R47',k.F_Paste),('R45',k.B_Paste)]:
        p=next(p for p in fps[ref].Pads() if p.GetNumber()=='1')
        ls=p.GetLayerSet(); ls.AddLayer(layer); p.SetLayerSet(ls)
    # Through-hole and copper-routing preservation controls, physically irrelevant fixture geometry.
    p=k.PAD(fps['TP81']); p.SetNumber('1'); p.SetAttribute(k.PAD_ATTRIB_PTH)
    p.SetShape(k.PAD_SHAPE_CIRCLE); p.SetSize(k.VECTOR2I(k.FromMM(.8),k.FromMM(.8)))
    p.SetDrillSize(k.VECTOR2I(k.FromMM(.4),k.FromMM(.4))); p.SetLayerSet(k.PAD.PTHMask())
    p.SetPosition(k.VECTOR2I(k.FromMM(11),k.FromMM(30))); p.SetNet(native_nets[master_nodes[('TP81','1')]]); fps['TP81'].Add(p)
    tr=k.PCB_TRACK(b); tr.SetStart(k.VECTOR2I(k.FromMM(5),k.FromMM(5)))
    tr.SetEnd(k.VECTOR2I(k.FromMM(6),k.FromMM(5))); tr.SetWidth(k.FromMM(.15)); tr.SetLayer(k.F_Cu); tr.SetNet(net); b.Add(tr)
    via=k.PCB_VIA(b); via.SetPosition(k.VECTOR2I(k.FromMM(6),k.FromMM(5)))
    via.SetWidth(k.F_Cu,k.FromMM(.6)); via.SetDrill(k.FromMM(.3)); via.SetLayerPair(k.F_Cu,k.B_Cu); via.SetNet(net); b.Add(via)
    for start,end in [((3,3),(34,3)),((34,3),(34,34)),((34,34),(3,34)),((3,34),(3,3))]:
        s=k.PCB_SHAPE(b); s.SetShape(k.SHAPE_T_SEGMENT); s.SetLayer(k.Edge_Cuts); s.SetWidth(k.FromMM(.05))
        s.SetStart(k.VECTOR2I(*[k.FromMM(v) for v in start])); s.SetEnd(k.VECTOR2I(*[k.FromMM(v) for v in end])); b.Add(s)
    # A DNP Fab graphic makes the hide-fab option observable on the intended layer.
    primitive(fps['R528'],k.F_Fab,11,11)
    save(b,out)
    return {str(p.relative_to(project)):policy.sha(p.read_bytes()) for p in sorted(set(libs))}

def run_cli(args, logfile):
    p=subprocess.run(['kicad-cli']+args, text=True,capture_output=True)
    logfile.write_text(p.stdout+p.stderr)
    if p.returncode: raise RuntimeError(f'KiCad CLI failed: {args}: {p.stderr}')

def normalized_gerber(p):
    # Only file identity/timestamp/checksum metadata varies between source and derived boards.
    lines=p.read_text().splitlines()
    return '\n'.join(s for s in lines if not any(x in s for x in ['CreationDate','ProjectId','MD5','G04 Created by']))

def layer_file(folder, layer):
    fs=list(folder.glob('*-'+layer.replace('.','_')+'.*'))
    if len(fs)!=1: raise RuntimeError(f'Expected one Gerber for {layer}: {fs}')
    return fs[0]

def plot(board, folder, flags=()):
    folder.mkdir()
    run_cli(['pcb','export','gerbers','--layers','F.Cu,B.Cu,F.Mask,B.Mask,F.Paste,B.Paste,F.Fab,Edge.Cuts',
             '--output',str(folder)+'/']+list(flags)+[str(board)],folder/'export.log')

def api_plot(board, folder):
    folder.mkdir(); b=k.LoadBoard(str(board)); c=k.PLOT_CONTROLLER(b); p=c.GetPlotOptions()
    p.SetOutputDirectory(str(folder)); p.SetHideDNPFPsOnFabLayers(True)
    p.SetSketchDNPFPsOnFabLayers(False); p.SetCrossoutDNPFPsOnFabLayers(False)
    for layer in [k.F_Paste,k.B_Paste]:
        c.SetLayer(layer); c.OpenPlotfile('API_'+b.GetLayerName(layer).replace('.','_'),k.PLOT_FORMAT_GERBER,'Review only')
        if not c.PlotLayer(): raise RuntimeError('API plot failed')
        c.ClosePlot()

def flashes(path):
    return len(re.findall(r'(?m)^X[^\n]*D03\*$',path.read_text()))

def main():
    a=argparse.ArgumentParser(); a.add_argument('--project',type=Path,required=True); a.add_argument('--out',type=Path,required=True); args=a.parse_args()
    project=args.project.resolve(); out=args.out.resolve(); out.mkdir(parents=True,exist_ok=False)
    for key in ['XDG_CACHE_HOME','XDG_CONFIG_HOME','XDG_DATA_HOME']:
        os.environ[key]=str(out/'runtime'/key.lower())
    source=out/'POLICY_FIXTURE_ONLY.kicad_pcb'; derived=out/'DERIVED_STENCIL_REVIEW_ONLY.kicad_pcb'
    master=project/'cad/recovery-physical-candidate/master.xml'; contract=project/'tools/population_contract.py'
    inputs={str(p.relative_to(project)):policy.sha(p.read_bytes()) for p in [master,contract]}
    inputs.update(make_fixture(project,source)); source_sha=policy.sha(source.read_bytes())
    report=policy.derive(source,derived,master,contract,True)
    (out/'derivation.json').write_text(json.dumps(report,indent=2)+'\n')
    checks=[]
    def check(name,condition):
        if not condition: raise AssertionError(name)
        checks.append({'check':name,'result':'PASS'})
    def rejected(name,src=source,dst=derived,m=master,mutate=None,reason=None):
        if mutate:
            dst=out/(name+'.kicad_pcb'); dst.write_text(mutate(derived.read_text()))
        try: policy.verify(src,dst,m,contract,True)
        except (policy.PolicyError,AssertionError) as e:
            expected_reason = reason or {'negative-copper-deletion':'Numbered electrical pad lacks copper: R528', 'negative-fitted-paste-loss':'differs beyond',
                               'negative-bare-testpad-paste':'Bare fabricated feature has paste: TP81',
                               'negative-dnp-attributes':'Population attribute mismatch: R528',
                               'negative-master-dnp':'Population attribute mismatch: R528',
                               'negative-unowned-paste':'Unowned board-level paste'}[name]
            if expected_reason not in str(e): raise AssertionError(f'Wrong rejection for {name}: {e}')
            checks.append({'check':name,'result':'REJECTED_AS_REQUIRED','reason':str(e)}); return
        raise AssertionError('Negative control accepted: '+name)
    for name,board,flags in [('default',source,()),('hide-fab',source,('--hide-DNP-footprints-on-fab-layers',)),
                             ('all-fab-controls',source,('--hide-DNP-footprints-on-fab-layers','--sketch-DNP-footprints-on-fab-layers','--crossout-DNP-footprints-on-fab-layers')),
                             ('derived',derived,())]: plot(board,out/name,flags)
    api_plot(source,out/'api-hide-fab')
    counts={}
    for layer in ['F.Paste','B.Paste']:
        base=layer_file(out/'default',layer); dst=layer_file(out/'derived',layer)
        for mode in ['hide-fab','all-fab-controls']:
            check(f'{layer}: {mode} does not suppress DNP paste',normalized_gerber(base)==normalized_gerber(layer_file(out/mode,layer)))
        ap=list((out/'api-hide-fab').glob('*API_'+layer.replace('.','_')+'.gbr'))[0]
        check(f'{layer}: Python hide-on-fab retains default flashes',flashes(ap)==flashes(base))
        fitted_ref={'F.Paste':'R529','B.Paste':'R46'}[layer]
        check(f'{layer}: Gerber component attribution is fitted only',set(re.findall(r'%TO\.C,([^*]+)\*%',dst.read_text()))=={fitted_ref})
        check(f'{layer}: fitted paste graphic remains as one region',dst.read_text().count('G36*')==1)
        counts[layer]={'default_flashes':flashes(base),'derived_flashes':flashes(dst),'api_hide_fab_flashes':flashes(ap)}
        check(f'{layer}: fitted native apertures + synthetic aperture retain 3 flashes',flashes(dst)==3)
    for layer in ['F.Cu','B.Cu','F.Mask','B.Mask','Edge.Cuts','F.Fab']:
        check(f'{layer}: full Gerber geometry preserved',normalized_gerber(layer_file(out/'default',layer))==normalized_gerber(layer_file(out/'derived',layer)))
    fab_hide_changed = normalized_gerber(layer_file(out/'default','F.Fab'))!=normalized_gerber(layer_file(out/'hide-fab','F.Fab'))
    # Drill outputs and position CSV preserve holes and assembly attributes independently.
    for name,board in [('source',source),('derived',derived)]:
        drill=out/(name+'-drill'); drill.mkdir()
        run_cli(['pcb','export','drill','--output',str(drill)+'/',str(board)],drill/'export.log')
        run_cli(['pcb','export','pos','--format','csv','--units','mm','--output',str(out/(name+'-pos.csv')),str(board)],out/(name+'-pos.log'))
    for p in (out/'source-drill').glob('*.drl'):
        q=out/'derived-drill'/p.name.replace(source.stem,derived.stem)
        def normdr(p):return '\n'.join(x for x in p.read_text().splitlines() if not x.startswith(('; #@! TF.CreationDate','; DRILL file')))
        check('Drill geometry preserved: '+p.name,normdr(p)==normdr(q))
    roundtrip=out/'NATIVE_ROUNDTRIP_REVIEW_ONLY.kicad_pcb'; save(k.LoadBoard(str(derived)),roundtrip)
    policy.verify(source,roundtrip,master,contract,True)
    check('Native roundtrip preserves allowed-only transformation',True)
    check('Default PnP byte-for-byte preserved',(out/'source-pos.csv').read_bytes()==(out/'derived-pos.csv').read_bytes())
    posrows=list(csv.DictReader((out/'derived-pos.csv').open())); posrefs={row['Ref'] for row in posrows}
    check('Only fitted R46/R529 in default PnP',posrefs=={'R46','R529'})
    dnp_strap=next(f for f in k.LoadBoard(str(derived)).GetFootprints() if f.GetReference()=='R528')
    check('R528 keeps distinct authoritative pin nets and inhibit population flags',
          {p.GetNumber():p.GetNetname() for p in dnp_strap.Pads()}=={'1':'VDD1P8','2':'BOOT_VOLTAGE_QUALIFIED_1V8'}
          and dnp_strap.IsDNP() and dnp_strap.IsExcludedFromPosFiles())
    def replace_item(text,ref,fn):
        root=policy.parse(text); fp=next(n for n in root.nodes('footprint') if policy.ref_of(n)==ref)
        replacement=fn(text[fp.start:fp.end])
        return text[:fp.start]+replacement+text[fp.end:]
    rejected('negative-copper-deletion',mutate=lambda text:replace_item(text,'R528',lambda t:t.replace('"F.Cu" "F.Mask"','"F.Mask"',1)))
    def remove_first_aperture(text):
        fp=policy.parse('(kicad_pcb '+text+')').nodes('footprint')[0]
        n=next(n for n in fp.nodes('pad') if policy.has_paste(n))
        prefix=len('(kicad_pcb ')
        return text[:n.start-prefix]+text[n.end-prefix:]
    rejected('negative-fitted-paste-loss',mutate=lambda text:replace_item(text,'R529',remove_first_aperture))
    # Mutate source for source-policy checks, and pass identical copy as derived; rejection must precede geometric comparison.
    bare=out/'negative-bare-testpad-paste.kicad_pcb'
    bare.write_text(replace_item(source.read_text(),'TP81',lambda t:t.replace('"F.Cu" "F.Mask"','"F.Cu" "F.Paste" "F.Mask"',1)))
    rejected('negative-bare-testpad-paste',src=bare,dst=bare)
    mismatch=out/'negative-dnp-attributes.kicad_pcb'
    mismatch.write_text(replace_item(source.read_text(),'R528',lambda t:t.replace(' dnp','',1)))
    rejected('negative-dnp-attributes',src=mismatch,dst=mismatch)
    altered=out/'negative-master-dnp.xml'; tree=ET.parse(master)
    c=next(c for c in tree.findall('./components/comp') if c.get('ref')=='R528')
    c.remove(next(p for p in c.findall('property') if p.get('name')=='dnp')); tree.write(altered)
    rejected('negative-master-dnp',m=altered)
    # Unsupported/unowned paste must not quietly escape suppression.
    orphan=out/'negative-unowned-paste.kicad_pcb'; b=k.LoadBoard(str(source))
    s=k.PCB_SHAPE(b); s.SetShape(k.SHAPE_T_RECT); s.SetLayer(k.F_Paste)
    s.SetStart(k.VECTOR2I(k.FromMM(5),k.FromMM(7))); s.SetEnd(k.VECTOR2I(k.FromMM(6),k.FromMM(8))); b.Add(s); save(b,orphan)
    rejected('negative-unowned-paste',src=orphan,dst=orphan)
    # Full pin/net parity is independent of reference coverage and transformation parity.
    # Repeated pad numbers are valid only when every native pad agrees with master.
    pcb = k.LoadBoard(str(derived))
    tp = next(f for f in pcb.GetFootprints() if f.GetReference() == 'TP81')
    check('Duplicate-number TP81 pads share the exact expected master net',
          len(list(tp.Pads())) == 2 and all(p.GetNumber() == '1' and p.GetNetname() == 'PMU_OUT0_STATUS' for p in tp.Pads()))
    for role, baseline in [('source', source), ('derived', derived)]:
        for ref, pin, wrong_net in [('R528', '1', 'GND'), ('R529', '2', 'VDD1P8')]:
            name = f'negative-{role}-net-{ref}'
            bad = out / (name + '.kicad_pcb'); board = k.LoadBoard(str(baseline))
            fp = next(f for f in board.GetFootprints() if f.GetReference() == ref)
            pad = next(p for p in fp.Pads() if p.GetNumber() == pin)
            pad.SetNet(board.FindNet(wrong_net)); save(board, bad)
            rejected(name, src=bad if role == 'source' else source,
                     dst=bad if role == 'derived' else derived,
                     reason=f'Pad/net binding mismatch: {ref}.{pin}')
    def source_mutation(name, ref, mutation, reason):
        board = k.LoadBoard(str(source)); fp = next(f for f in board.GetFootprints() if f.GetReference() == ref)
        mutation(board, fp); bad = out / (name + '.kicad_pcb'); save(board, bad)
        rejected(name, src=bad, reason=reason)
    source_mutation('negative-missing-numbered-pad', 'R528',
                    lambda board,fp: fp.Remove(next(p for p in fp.Pads() if p.GetNumber() == '1')),
                    'Missing numbered electrical pads: R528')
    source_mutation('negative-unknown-numbered-pad', 'TP81',
                    lambda board,fp: next(iter(fp.Pads())).SetNumber('999'),
                    'Unknown numbered electrical pad: TP81.999')
    source_mutation('negative-duplicate-number-wrong-net', 'TP81',
                    lambda board,fp: next(iter(fp.Pads())).SetNet(board.FindNet('GND')),
                    'Pad/net binding mismatch: TP81.1')
    source_mutation('negative-unnumbered-net', 'R529',
                    lambda board,fp: next(p for p in fp.Pads() if not p.GetNumber()).SetNet(board.FindNet('GND')),
                    'Unnumbered pad carries an undeclared net: R529')
    moved = out / 'negative-nonpaste-position.kicad_pcb'; board = k.LoadBoard(str(derived))
    fp = next(f for f in board.GetFootprints() if f.GetReference() == 'R529')
    fp.SetPosition(fp.GetPosition() + k.VECTOR2I(k.FromMM(1), 0)); save(board, moved)
    rejected('negative-nonpaste-position', dst=moved, reason='differs beyond permitted DNP paste changes')
    missing_node = out / 'negative-master-missing-pin-node.xml'; tree = ET.parse(master)
    for net in tree.findall('./nets/net'):
        for node in list(net.findall('node')):
            if node.get('ref') == 'R528' and node.get('pin') == '1': net.remove(node)
    tree.write(missing_node)
    rejected('negative-master-missing-pin-node', m=missing_node,
             reason='Master declared-pin/net-node mismatch: R528')
    check('Input board immutable',policy.sha(source.read_bytes())==source_sha)
    check('Published master, contract, library source files immutable',all(policy.sha((project/p).read_bytes())==h for p,h in inputs.items()))
    for kind,args_cli in [('gerbers',['pcb','export','gerbers','--help']),('pos',['pcb','export','pos','--help'])]:
        p=subprocess.run(['kicad-cli']+args_cli,text=True,capture_output=True); (out/(kind+'-help.txt')).write_text(p.stdout+p.stderr)
    api={cls:[n for n in dir(getattr(k,cls)) if any(t in n.lower() for t in ['dnp','paste','exclude','layer'])] for cls in ['PCB_PLOT_PARAMS','FOOTPRINT','PAD','LSET']}
    (out/'installed-api.json').write_text(json.dumps({'version':k.GetBuildVersion(),'api':api},indent=2)+'\n')
    summary={'status':'PASS_REVIEW_ONLY','kicad':k.GetBuildVersion(),'checks':checks,'flash_counts':counts,'input_hashes':inputs,'cli_hide_flag_changed_fab_output':fab_hide_changed,
             'tool_hashes':{p.name:policy.sha(p.read_bytes()) for p in [Path(__file__),Path(policy.__file__)]},
             'scope':'Synthetic two-sided policy fixture using source-library pad geometry; no main board edits or manufacturing qualification'}
    (out/'results.json').write_text(json.dumps(summary,indent=2)+'\n'); print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
