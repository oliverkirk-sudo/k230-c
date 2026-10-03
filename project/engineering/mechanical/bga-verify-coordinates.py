#!/usr/bin/env python3
"""Read-only source audit; emit only bga-* mechanical audit artifacts.

Coordinates are package-centered, component-side (top) view, +X right,
+Y down, millimetres. They are ball centers, NOT a qualified PCB land pattern.
PDF/image pixels identify occupancy only; published dimensions determine XY.
"""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
import fitz
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path('/workspace/shared/cm-k230-redesign')
OUT = ROOT / 'engineering/mechanical'
SRC = Path('/workspace/shared/k230-memory-review')
EVIDENCE = Path('/workspace/shared/k230-reference/mechanical')
RAM_ROWS = 'A B C D E F G H J K L M N P R T U V W Y AA AB'.split()
EMMC_ROWS = 'A B C D E F G H J K L M N P'.split()
K230_ROWS = 'A B C D E F G H J K L M N P R T U V W Y'.split()
RAM_URL = 'https://www.szyuda88.com/home/8/a/2lhtb2/resource/2021/05/26/60ade38424a32.pdf'
EMMC_URL = 'https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/791/Samsung-eMMC_2D00_2611204514.pdf'
K230_BASE = 'https://raw.githubusercontent.com/kendryte/k230_docs/main/zh/00_hardware/images/HDG/'

def csvrows(path):
    with path.open(newline='') as f:
        return list(csv.DictReader(f))

ram_table = csvrows(ROOT / 'engineering/memory/K4F8E304HB_grid264_physical200.csv')
emmc_table = csvrows(ROOT / 'engineering/memory/KLMAG1JETD_grid196_physical153.csv')
k230_table = csvrows(ROOT / 'data/k230-source-extraction/k230-390-balls.csv')
ram_expected = {x['ball_or_grid'] for x in ram_table if x['physical_ball'].lower() == 'true'}
emmc_expected = {x['ball_or_grid'] for x in emmc_table if x['physical_ball'].lower() == 'true'}
k230_expected = {x['soc_ball'] for x in k230_table}

# RAM p9, mechanical bottom view: circles are four consecutive closed Beziers.
# A12 shares a drawing object with an unrelated line, so inspect subpaths rather
# than the whole drawing's bounding rectangle. K1 has a minor artistic offset;
# do not turn that pixel offset into an asserted physical coordinate offset.
ram_detected = []
ram = fitz.open(SRC / 'lp4.pdf')
for d in ram[8].get_drawings():
    items = d['items']
    for i in range(len(items) - 3):
        v = items[i:i+4]
        if not all(z[0] == 'c' for z in v):
            continue
        if any(v[j][4] != v[(j+1) % 4][1] for j in range(4)):
            continue
        pts = [p for z in v for p in z[1:]]
        x0, x1 = min(z.x for z in pts), max(z.x for z in pts)
        y0, y1 = min(z.y for z in pts), max(z.y for z in pts)
        if 7 < x1-x0 < 8 and 7 < y1-y0 < 8 and 100 < x0 < 275 and 440 < y0 < 635:
            x, y = (x0+x1)/2, (y0+y1)/2
            row = round((y - 444.045) / 9.015)
            col = 12 - round((x - 112.59) / 14.515)
            ram_detected.append(RAM_ROWS[row] + str(col))

# eMMC p5, ball-side-down/top-equivalent view: eight-item filled circle paths.
# The source PDF draws N12 twice. Count unique occupied grid sites, not paths.
emmc = fitz.open(SRC / 'emmc-rev11.pdf')
emmc_detected = []
for d in emmc[4].get_drawings():
    r = d['rect']
    if len(d['items']) == 8 and 279 < r.x0 < 484 and 235 < r.y0 < 460 and 10 < r.width < 15:
        x, y = (r.x0+r.x1)/2, (r.y0+r.y1)/2
        col = round((x - 285.25) / 14.83) + 1
        row = round((y - 246.5) / 15.92)
        emmc_detected.append(EMMC_ROWS[row] + str(col))

# Independent check against p6's 8/16GB mechanical BOTTOM view. A circle may
# have multiple outline paths; all candidates must map to the same 153 sites.
emmc_mechanical = []
for d in emmc[5].get_drawings():
    r = d['rect']
    if 388 < r.x0 < 490 and 182 < r.y0 < 286 and 4.5 < r.width < 7 and 4.5 < r.height < 6:
        x, y = (r.x0+r.x1)/2, (r.y0+r.y1)/2
        col = 14 - round((x - 392.9) / 7.23)
        row = round((y - 186.3) / 7.38)
        if 0 <= row < 14 and 1 <= col <= 14:
            emmc_mechanical.append(EMMC_ROWS[row] + str(col))

# Official K230 bottom-view drawing. Remove red dimension lines by retaining
# dark neutral pixels, then find ball-ring components. At A20 a dimension line
# splits off a 4x4 fragment; the 7x7-or-larger ring component remains detectable.
im = np.array(Image.open(EVIDENCE / 'bga-k230-image005.png').convert('RGB'))
labels, _ = ndimage.label(im.max(axis=2) < 220, np.ones((3, 3)))
k230_detected = []
for i, b in enumerate(ndimage.find_objects(labels), start=1):
    yy, xx = b
    x0, y0 = xx.start, yy.start
    w, h = xx.stop-xx.start, yy.stop-yy.start
    if 690 < x0 < 959 and 100 < y0 < 368 and 7 <= w <= 10 and 7 <= h <= 10:
        cy, cx = ndimage.center_of_mass(labels[b] == i)
        x, y = x0+cx, y0+cy
        col = 20 - round((x - 698.7) / 13.4)
        row = round((y - 105.8) / 13.4)
        k230_detected.append(K230_ROWS[row] + str(col))

assert len(ram_detected) == len(set(ram_detected)) == 200
assert set(ram_detected) == ram_expected
assert len(emmc_detected) == 154 and len(set(emmc_detected)) == 153
assert {k: v for k, v in Counter(emmc_detected).items() if v > 1} == {'N12': 2}
assert set(emmc_detected) == set(emmc_mechanical) == emmc_expected
assert len(k230_detected) == len(set(k230_detected)) == 390
assert set(k230_detected) == k230_expected

def export(name, rows, cols, px, py, occupied, functions, source, page):
    allsites = [r+str(c) for r in rows for c in range(1, cols+1)]
    ordered = [b for b in allsites if b in occupied]
    def xy(ball):
        row = ball.rstrip('0123456789')
        col = int(ball[len(row):])
        return round((col-(cols+1)/2)*px, 6), round((rows.index(row)-(len(rows)-1)/2)*py, 6)
    path = OUT / f'bga-{name}-physical-centers.csv'
    with path.open('w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['ball', 'source_function_label', 'x_mm', 'y_mm', 'view', 'xy_convention', 'geometry_source', 'source_page_or_figure', 'status'])
        for ball in ordered:
            w.writerow([ball, functions[ball], *xy(ball), 'COMPONENT_SIDE_TOP', 'origin=package_center;+x=right;+y=down', source, page, 'NOMINAL_BALL_CENTER_ONLY_NOT_PCB_LAND_PATTERN'])
    missing = [b for b in allsites if b not in occupied]
    return {'physical_ball_count': len(ordered), 'grid_positions': len(allsites),
            'absent_positions': missing, 'pitch_x_mm': px, 'pitch_y_mm': py,
            'row_order': rows, 'coordinate_file': path.name,
            'coordinate_extent_x_mm': [min(xy(b)[0] for b in ordered), max(xy(b)[0] for b in ordered)],
            'coordinate_extent_y_mm': [min(xy(b)[1] for b in ordered), max(xy(b)[1] for b in ordered)]}

result = {'coordinate_frame': 'Nominal package-centered component-side/top view, +X right, +Y down; millimetres. Bottom-view geometry is horizontally mirrored. Not copper/mask/paste dimensions.', 'parts': {}}
result['parts']['K4F8E304HB-MGCJ'] = export('K4F8E304HB', RAM_ROWS, 12, .8, .65, ram_expected, {x['ball_or_grid']: x['function'] for x in ram_table}, RAM_URL, '9 dimensions;10 top-view ballout')
result['parts']['KLMAG1JETD-B041'] = export('KLMAG1JETD', EMMC_ROWS, 14, .5, .5, emmc_expected, {x['ball_or_grid']: x['function'] for x in emmc_table}, EMMC_URL, '5 ballmap;6 figure2 dimensions')
result['parts']['K230'] = export('K230', K230_ROWS, 20, .65, .65, k230_expected, {x['soc_ball']: x['soc_signal'] for x in k230_table}, K230_BASE+'image005.png', 'HDG figures2-1;2-2;2-3;2-6')
result['verification'] = {
    'ram_p9_physical_circles': len(ram_detected), 'ram_p9_vs_p10_table_mismatches': [],
    'emmc_p5_circle_paths': len(emmc_detected), 'emmc_p5_unique_positions': len(set(emmc_detected)),
    'emmc_p5_duplicate_path_site': 'N12', 'emmc_p6_mechanical_unique_positions': len(set(emmc_mechanical)),
    'emmc_p5_p6_vs_table_mismatches': [], 'k230_mechanical_circle_components': len(k230_detected),
    'k230_mechanical_vs_existing_390_table_mismatches': [],
    'visual_review': 'Inspected RAM pp9-10, eMMC pp5-6, Canaan HDG image005/006/007/010; orientation, numeric dimensions, and absent-region patterns agree with extraction.'}
result['sources'] = []
for p, url in [(SRC/'lp4.pdf', RAM_URL), (SRC/'emmc-rev11.pdf', EMMC_URL), *[(EVIDENCE/f'bga-k230-image{i}.png', K230_BASE+f'image{i}.png') for i in ['005','006','007']], (Path('/workspace/shared/k230-reference/image010.png'), K230_BASE+'image010.png')]:
    result['sources'].append({'local_file': str(p), 'url': url, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
(OUT/'bga-coordinate-verification.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps({'verified': {k: v['physical_ball_count'] for k, v in result['parts'].items()}, 'output_files': [v['coordinate_file'] for v in result['parts'].values()]}, indent=2))
