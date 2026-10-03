#!/usr/bin/env python3
"""Derive a review-only KiCad 9 stencil board. Never edit a source or library.

Run with KiCad's Python (commonly /usr/bin/python3). Every non-paste token is
preserved exactly. Unsupported paste ownership fails closed. This is an export
policy check, not stencil/process qualification or a production release gate.
"""
from __future__ import annotations
import argparse
import dataclasses
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import pcbnew as k

PASTE = {'F.Paste', 'B.Paste'}
GRAPHICS = {'fp_line', 'fp_rect', 'fp_arc', 'fp_circle', 'fp_poly', 'fp_curve',
            'fp_text', 'fp_text_box'}
TOKEN = re.compile(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+')

class PolicyError(ValueError):
    pass

@dataclasses.dataclass
class Node:
    value: str | None
    start: int
    end: int
    children: list['Node'] = dataclasses.field(default_factory=list)
    @property
    def tag(self):
        return self.children[0].value if self.children else None
    def nodes(self, tag):
        return [c for c in self.children if c.tag == tag]
    def one(self, tag):
        items = self.nodes(tag)
        if len(items) != 1:
            raise PolicyError(f'Expected exactly one {tag}, got {len(items)}')
        return items[0]

def parse(text):
    ts = list(TOKEN.finditer(text))
    def rec(i):
        t = ts[i]
        if t.group() == '(':
            children = []; start = t.start(); i += 1
            while i < len(ts) and ts[i].group() != ')':
                n, i = rec(i); children.append(n)
            if i == len(ts): raise PolicyError('Unclosed expression')
            return Node(None, start, ts[i].end(), children), i + 1
        if t.group() == ')': raise PolicyError('Unexpected closing parenthesis')
        raw = t.group()
        value = json.loads(raw) if raw.startswith('"') else raw
        return Node(value, t.start(), t.end()), i + 1
    root, end = rec(0)
    if end != len(ts) or root.tag != 'kicad_pcb': raise PolicyError('Expected one KiCad board')
    return root

def tokens(text):
    return [m.group() for m in TOKEN.finditer(text)]

def layer_names(item):
    return {c.value for n in item.nodes('layer') + item.nodes('layers') for c in n.children[1:]}

def has_paste(item):
    return bool(layer_names(item) & PASTE) or '*.Paste' in layer_names(item)

def ref_of(fp):
    p = [n for n in fp.nodes('property') if n.children[1].value == 'Reference']
    if len(p) != 1: raise PolicyError('Footprint lacks one Reference property')
    return p[0].children[2].value

def sha(data):
    return hashlib.sha256(data).hexdigest()

def read_contract(path):
    spec = importlib.util.spec_from_file_location('review_population_contract', path)
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode = True
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module

def component_map(master):
    cs = ET.parse(master).getroot().findall('./components/comp')
    refs = [c.get('ref') for c in cs]
    if len(refs) != len(set(refs)) or not all(refs): raise PolicyError('Duplicate/empty master references')
    for c in cs:
        props = [p.get('name') for p in c.findall('property')]
        if len(props) != len(set(props)): raise PolicyError(f'Duplicate properties for {c.get("ref")}')
        for p in c.findall('property'):
            if p.get('name') in {'dnp', 'exclude_from_bom', 'exclude_from_pos_files'} and p.get('value') not in {None, ''}:
                raise PolicyError(f'Ambiguous population property value for {c.get("ref")}: {p.attrib}')
    return dict(zip(refs, cs))

def master_bindings(master, components):
    """Require explicit, unambiguous pin/net intent, including no_connect pins.

    No implicit virtual-pin, NC-net-zero, or mechanical numbered-pad exemption is
    inferred. Such a project needs a separately reviewed explicit policy first.
    """
    root = ET.parse(master).getroot()
    libparts = {}
    for lp in root.findall('./libparts/libpart'):
        key = (lp.get('lib'), lp.get('part'))
        if key in libparts: raise PolicyError(f'Duplicate master libpart: {key}')
        pins = [p.get('num') for p in lp.findall('./pins/pin')]
        if not pins or not all(pins) or len(pins) != len(set(pins)):
            raise PolicyError(f'Missing/ambiguous master pin declarations: {key}')
        libparts[key] = set(pins)
    bindings = {ref: {} for ref in components}
    for net in root.findall('./nets/net'):
        name = net.get('name')
        if not name: raise PolicyError('Master has an unnamed net')
        for node in net.findall('node'):
            ref, pin = node.get('ref'), node.get('pin')
            if ref not in components or not pin:
                raise PolicyError(f'Unknown/empty master net node: {ref}.{pin}')
            if pin in bindings[ref]:
                raise PolicyError(f'Duplicate or conflicting master net node: {ref}.{pin}')
            bindings[ref][pin] = name
    for ref, component in components.items():
        ls = component.find('libsource')
        if ls is None: raise PolicyError(f'Master libsource missing: {ref}')
        key = (ls.get('lib'), ls.get('part'))
        if key not in libparts: raise PolicyError(f'Master libpart missing: {ref}')
        if libparts[key] != set(bindings[ref]):
            raise PolicyError(f'Master declared-pin/net-node mismatch: {ref}; NC/virtual exceptions require explicit review')
    return bindings


def check_native_bindings(footprint, expected):
    ref = footprint.GetReference(); present = set()
    for pad in footprint.Pads():
        pin, net = pad.GetNumber(), pad.GetNetname()
        if not pin:
            if net or pad.GetNetCode() != 0:
                raise PolicyError(f'Unnumbered pad carries an undeclared net: {ref}')
            continue
        if pin not in expected:
            raise PolicyError(f'Unknown numbered electrical pad: {ref}.{pin}')
        if not pad.IsOnCopperLayer():
            raise PolicyError(f'Numbered electrical pad lacks copper: {ref}.{pin}')
        if net != expected[pin]:
            raise PolicyError(f'Pad/net binding mismatch: {ref}.{pin}; expected {expected[pin]!r}, got {net!r}')
        # Repeated numbers are permitted only because EVERY copy passed the same
        # expected-net comparison above, not just the first or last copy.
        present.add(pin)
    missing = set(expected) - present
    if missing:
        raise PolicyError(f'Missing numbered electrical pads: {ref}: {sorted(missing)}')


def check_declared_pad_identity(board_path, bindings):
    # KiCad can normalize away net/number data on non-copper pads at load time.
    # Reject those inconsistent declarations before the native comparison.
    for fp in parse(Path(board_path).read_text()).nodes('footprint'):
        ref = ref_of(fp)
        if ref not in bindings: raise PolicyError(f'Unknown PCB reference: {ref}')
        for pad in fp.nodes('pad'):
            pin = pad.children[1].value
            if pin and pin not in bindings[ref]:
                raise PolicyError(f'Unknown numbered electrical pad: {ref}.{pin}')
            if pin and not any(n == '*.Cu' or n.endswith('.Cu') for n in layer_names(pad)):
                raise PolicyError(f'Numbered electrical pad lacks copper: {ref}.{pin}')
            if not pin:
                for net in pad.nodes('net'):
                    values = [n.value for n in net.children[1:]]
                    if values != ['0', '']:
                        raise PolicyError(f'Unnumbered pad carries an undeclared net: {ref}')


def check_population(board_path, components, contract, allow_subset, bindings):
    check_declared_pad_identity(board_path, bindings)
    board = k.LoadBoard(str(board_path))
    fps = list(board.GetFootprints()); refs = [f.GetReference() for f in fps]
    if len(refs) != len(set(refs)): raise PolicyError('Duplicate PCB references')
    unknown = set(refs) - components.keys(); missing = components.keys() - set(refs)
    if unknown or (missing and not allow_subset):
        raise PolicyError(f'PCB/master coverage mismatch: unknown={sorted(unknown)}, missing_count={len(missing)}')
    for f in fps:
        c = components[f.GetReference()]
        expected = contract.expected_attributes(c, f.GetAttributes())
        if f.GetAttributes() != expected:
            raise PolicyError(f'Population attribute mismatch: {f.GetReference()}')
        master_dnp = any(p.get('name') == 'dnp' for p in c.findall('property'))
        if bool(f.IsDNP()) != master_dnp: raise PolicyError(f'DNP sources disagree: {f.GetReference()}')
        if f.GetFPIDAsString() != c.findtext('footprint'):
            raise PolicyError(f'Footprint binding mismatch: {f.GetReference()}')
        check_native_bindings(f, bindings[f.GetReference()])
    return board, set(refs), missing

def transform(text, components, contract):
    root = parse(text); edits = []; changes = []
    bare = set(contract.FABRICATED_FEATURE_REFS)
    dnp_all = {r for r, c in components.items() if any(p.get('name') == 'dnp' for p in c.findall('property'))}
    for n in root.children:
        if n.tag != 'footprint' and has_paste(n):
            raise PolicyError('Unowned board-level paste item requires ownership review')
    for fp in root.nodes('footprint'):
        ref = ref_of(fp)
        for item in fp.children:
            if not has_paste(item): continue
            if ref in bare:
                raise PolicyError(f'Bare fabricated feature has paste: {ref}')
            if ref not in dnp_all: continue
            if item.tag == 'pad':
                layers = item.one('layers')
                old = [c.value for c in layers.children[1:]]
                if '*.Paste' in old: raise PolicyError('Wildcard paste needs an explicit reviewed layer mapping')
                new = [v for v in old if v not in PASTE]
                if new:
                    replacement = '(layers ' + ' '.join(json.dumps(v) for v in new) + ')'
                    edits.append((layers.start, layers.end, replacement))
                    action = 'remove_pad_paste_layers'
                else:
                    # An independent paste aperture has no copper, net, number, or hole.
                    # KiCad cannot retain a pad with an empty layer set.
                    if item.children[1].value or item.nodes('net') or item.nodes('drill'):
                        raise PolicyError(f'Paste-only pad has electrical/drill identity: {ref}')
                    edits.append((item.start, item.end, '')); action = 'remove_paste_only_aperture'
            elif item.tag in GRAPHICS:
                if layer_names(item) - PASTE:
                    raise PolicyError(f'Mixed-layer graphic cannot be removed: {ref}')
                edits.append((item.start, item.end, '')); action = 'remove_paste_graphic'
            else:
                # Properties retain metadata; zones/groups/new types need their own verified semantics.
                raise PolicyError(f'Unsupported DNP paste object {item.tag}: {ref}')
            changes.append({'ref': ref, 'kind': item.tag, 'action': action,
                            'uuid': item.one('uuid').children[1].value if item.nodes('uuid') else None,
                            'layers_removed': sorted(layer_names(item) & PASTE)})
    deleted_uuids = {c['uuid'] for c in changes if c['action'] != 'remove_pad_paste_layers'}
    def check_groups(node):
        if node.tag == 'group':
            for members in node.nodes('members'):
                if {n.value for n in members.children[1:]} & deleted_uuids:
                    raise PolicyError('Group references a removed paste aperture; ownership review required')
        for child in node.children:
            check_groups(child)
    check_groups(root)
    for start, end, replacement in sorted(edits, reverse=True):
        text = text[:start] + replacement + text[end:]
    return text, changes

def verify(source, derived, master, contract_path, allow_subset=False):
    components = component_map(master); contract = read_contract(contract_path)
    bindings = master_bindings(master, components)
    _, refs, missing = check_population(source, components, contract, allow_subset, bindings)
    derived_board, refs2, missing2 = check_population(derived, components, contract, allow_subset, bindings)
    original = Path(source).read_text(); actual = Path(derived).read_text()
    expected, changes = transform(original, components, contract)
    for fp in derived_board.GetFootprints():
        if not fp.IsDNP(): continue
        for item in list(fp.Pads()) + list(fp.GraphicalItems()) + list(fp.Zones()) + list(fp.GetFields()):
            if item.IsOnLayer(k.F_Paste) or item.IsOnLayer(k.B_Paste):
                raise PolicyError(f'Native KiCad sees residual DNP paste: {fp.GetReference()}')
    if refs != refs2 or missing != missing2 or tokens(expected) != tokens(actual):
        raise PolicyError('Derived board differs beyond permitted DNP paste changes')
    # Native load succeeded above; also prove derived DNP footprints have no paste left.
    remaining, repeated = transform(actual, components, contract)
    if repeated or tokens(remaining) != tokens(actual): raise PolicyError('DNP paste remains')
    return {'status': 'PASS_REVIEW_ONLY', 'kicad': k.GetBuildVersion(),
            'scope': 'subset_fixture' if allow_subset else 'complete_master_reference_set',
            'source_sha256': sha(Path(source).read_bytes()),
            'derived_sha256': sha(Path(derived).read_bytes()),
            'master_sha256': sha(Path(master).read_bytes()),
            'population_contract_sha256': sha(Path(contract_path).read_bytes()),
            'source_name': Path(source).name, 'derived_name': Path(derived).name,
            'board_reference_count': len(refs), 'master_missing_count': len(missing),
            'native_binding_check': 'source and derived exact master pin/net parity; all duplicate-number copies checked',
            'unique_master_pins_on_board': sum(len(bindings[r]) for r in refs),
            'numbered_pads_on_derived_board': sum(bool(p.GetNumber()) for f in derived_board.GetFootprints() for p in f.Pads()),
            'nc_virtual_exceptions': [],
            'dnp_refs_on_board': sorted(r for r in refs if any(p.get('name') == 'dnp' for p in components[r].findall('property'))),
            'changes': changes, 'preservation': 'All other native board tokens unchanged; native KiCad load, population and exact pin/net parity passed',
            'qualification': 'No manufacturing or stencil-process qualification; no production release'}

def derive(source, output, master, contract_path, allow_subset=False):
    source = Path(source); output = Path(output)
    if source.resolve() == output.resolve() or output.exists(): raise PolicyError('Output must be new and distinct from source')
    source_hash = sha(source.read_bytes())
    components = component_map(master); contract = read_contract(contract_path)
    bindings = master_bindings(master, components)
    check_population(source, components, contract, allow_subset, bindings)
    expected, _ = transform(source.read_text(), components, contract)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x') as f: f.write(expected)
    try:
        report = verify(source, output, master, contract_path, allow_subset)
        if sha(source.read_bytes()) != source_hash: raise PolicyError('Source changed during derivation')
        return report
    except BaseException:
        output.unlink(); raise

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', required=True, type=Path)
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--master', required=True, type=Path)
    p.add_argument('--population-contract', required=True, type=Path)
    p.add_argument('--report', required=True, type=Path)
    p.add_argument('--allow-subset-fixture', action='store_true', help='Review fixture only; waive completeness, never parity')
    p.add_argument('--verify-only', action='store_true')
    a = p.parse_args()
    if a.report.exists() or a.report.resolve() == a.output.resolve():
        p.error('Report must be new and distinct from the board output')
    report = (verify if a.verify_only else derive)(a.source, a.output, a.master, a.population_contract, a.allow_subset_fixture)
    with a.report.open('x') as f: f.write(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'status': report['status'], 'changes': len(report['changes']), 'scope': report['scope']}))
if __name__ == '__main__': main()
