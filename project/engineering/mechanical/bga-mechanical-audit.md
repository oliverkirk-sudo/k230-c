# BGA mechanical and orientation audit

Date: 2026-09-30. Scope: nominal ball-center coordinates, physical occupancy, view/orientation, and package dimensions for the CM-K230 review draft. No master CAD was modified. These results do not qualify copper lands, solder mask, paste apertures, escape routing, assembly or fabrication.

## Result

All three physical-ball sets are independently corroborated by the manufacturer mechanical drawings:

| Device | Actual balls | Grid | Pitch X / Y | Center-to-center span X / Y | Package body |
|---|---:|---|---|---|---|
| Samsung K4F8E304HB-MGCJ | 200 | 12 columns x 22 named rows | 0.80 / 0.65 mm | 8.80 / 13.65 mm | 10.00 +/-0.10 x 15.00 +/-0.10 mm |
| Samsung KLMAG1JETD-B041, 16GB | 153 | 14 x 14 | 0.50 / 0.50 mm | 6.50 / 6.50 mm | 11.50 +/-0.10 x 13.00 +/-0.10 mm |
| Canaan K230, not K230D | 390 | 20 x 20 | 0.650 / 0.650 mm | 12.350 / 12.350 mm | 13.000 nominal; 12.900-13.100 mm on both axes |

Numeric pitch/span dimensions printed in basic-dimension boxes or nominal-only table entries are not independently asserted to have an unspecified +/- dimensional tolerance. Retain the package drawing's GD&T rather than inventing a pitch tolerance.

## Coordinate convention and deliverables

CSV coordinates are millimetres, origin at nominal package center, component-side/top view, +X right and +Y down. This is a useful KiCad front-footprint local-coordinate convention. A backend using Cartesian +Y up must invert Y explicitly. Bottom-layer placement must be handled by the CAD tool's layer transform, not an additional undocumented manual mirror.

- `bga-K4F8E304HB-physical-centers.csv`: 200 physical positions
- `bga-KLMAG1JETD-physical-centers.csv`: 153 physical positions
- `bga-K230-physical-centers.csv`: 390 physical positions
- `bga-coordinate-verification.json`: counts, full absent-position sets, source hashes and provenance
- `bga-verify-coordinates.py`: reproducible occupancy extraction and coordinate generation

Only existing source labels accompany the positions. This mechanical audit does not independently re-audit every electrical function label or approve net assignments. No missing-ball pad is emitted. NC, RFU, and DNU are physical positions where the source draws a ball, and are not collapsed into NO_BALL.

## Samsung LPDDR4

Source: [Samsung K4F8E304HB-MGCJ Rev1.0, mechanical p9 and explicit top-view ballout p10](https://www.szyuda88.com/home/8/a/2lhtb2/resource/2021/05/26/60ade38424a32.pdf#page=9), manufacturer-authored PDF hosted by a third-party mirror. Local `lp4.pdf` SHA-256 is recorded in the verification JSON.

Rows top-to-bottom: A B C D E F G H J K L M N P R T U V W Y AA AB. Columns increase left-to-right 1-12 in top view. Page9's ball drawing is explicitly BOTTOM VIEW, with 12 at left and 1 at right. Page10 is explicitly TOP VIEW, with 1 at left. The index mark is upper-left on the top package view and upper-right on the bottom ball view.

For zero-based row index r and one-based column c: x=(c-6.5)*0.80; y=(r-10.5)*0.65. Consequently A1=(-4.400,-6.825), A12=(+4.400,-6.825), AB1=(-4.400,+6.825), AB12=(+4.400,+6.825).

Exactly 64 absent grid locations: all 12 positions in each of rows L and M, plus columns 6 and 7 in each of the other 20 rows. This leaves 20 populated rows x 10 populated columns =200. The apparent gaps are integer-multiple spacings on a regular grid: columns5-to8 =2.40 mm; rowsK-toN =1.95 mm. Do not compress those gaps or substitute a square 0.65 mm grid.

Page9 dimensions also specify:

- Total package height 0.90 +/-0.10 mm
- Solder-ball stand-off dimension 0.22 +/-0.05 mm
- 200 post-reflow ball diameters 0.31 +/-0.05 mm; the parenthetical solder-ball diameter is 0.30 mm
- Coplanarity-type callout 0.10 MAX to datum C
- Ball-position callout diameter0.15 at maximum material condition relative to A/B

Verification: extracted exactly 200 closed four-Bezier circle subpaths from page9 and mapped its reversed column order to page10's top-view grid. The occupied-position set matches the existing 264-grid/200-physical CSV without differences. One circle shares a PDF drawing object with an unrelated line; treating whole-object bounds as circles would miss it. Pixel coordinates were used only to identify occupied sites; published dimensions determine the exported XY.

## Samsung eMMC

Source: [Samsung eMMC Rev1.1 family PDF including KLMAG1JETD-B041, ballmap p5 and 8/16GB package Figure2 on p6](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/791/Samsung-eMMC_2D00_2611204514.pdf#page=5), manufacturer-authored PDF hosted on TI's forum. The 32GB drawing lower on p6 is not the selected16GB package-height specification.

Rows top-to-bottom: A B C D E F G H J K L M N P. The p5 wording is "Ball-side down view": balls facing down, with the component viewed from above. It has column1 at left and A1 upper-left. This agrees with the p6 TOP VIEW index mark. The p6 mechanical BOTTOM VIEW has column14 at left and column1/index corner at right. Do not interpret the p5 wording as a bottom-surface view and mirror it again.

For zero-based row index r and one-based column c: x=(c-7.5)*0.50; y=(r-6.5)*0.50. Thus A1=(-3.250,-3.250), A14=(+3.250,-3.250), P1=(-3.250,+3.250), P14=(+3.250,+3.250).

The 43 absent locations are:

- D5-D11
- E4, E11
- F4, F6-F9, F11
- G4, G6-G9, G11
- H4, H6-H9, H11
- J4, J6-J9, J11
- K4, K11
- L4-L11

All other 153 sites contain balls. In particular D4 exists while D11 does not, so a symmetric central-void shortcut is wrong. Existing functional classifications count107 NC,13 RFU and33 explicitly functional/power/ground balls.

Figure2's actual 8/16GB drawing specifies:

- Total height 0.70 +/-0.10 mm; the section/caption's0.8 mm is consistent with the maximum height, not a separately supported0.8 mm nominal height
- Stand-off dimension 0.21 +/-0.05 mm
- 153 ball diameters 0.30 +/-0.05 mm
- Coplanarity-type callout0.08 MAX
- Ball-position callout diameter0.15 at maximum material condition relative to A/B

Verification: p5 contains154 circle paths at153 unique positions because N12 is drawn twice. Unique sites match the existing196-grid/153-physical CSV. Independent p6 Figure2 mechanical-circle extraction, after horizontal reflection, yields the same153 positions. No mismatched locations were found. Rasterized pages5-6 were also visually reviewed.

## Canaan K230

Official sources: [Hardware Design Guide, package section](https://github.com/kendryte/k230_docs/blob/main/en/00_hardware/K230_Hardware_Design_Guide.md), [Figure2-1 top/bottom drawing](https://raw.githubusercontent.com/kendryte/k230_docs/main/zh/00_hardware/images/HDG/image005.png), [Figure2-2 height/detail drawing](https://raw.githubusercontent.com/kendryte/k230_docs/main/zh/00_hardware/images/HDG/image006.png), [Figure2-3 dimension table](https://raw.githubusercontent.com/kendryte/k230_docs/main/zh/00_hardware/images/HDG/image007.png), [Figure2-6 function/occupancy map](https://raw.githubusercontent.com/kendryte/k230_docs/main/zh/00_hardware/images/HDG/image010.png).

Rows top-to-bottom: A B C D E F G H J K L M N P R T U V W Y. Figure2-1's BOTTOM VIEW has column20 at left and1 at right. Mirroring it horizontally yields the component-side/top map shown by Figure2-6: column1 at left. The top package index corner is upper-left, but A1 itself has NO BALL. Do not create an A1 pad as a marker or retain an old schematic-only A1=NC entry.

For zero-based row index r and one-based column c: x=(c-10.5)*0.650; y=(r-9.5)*0.650. Outer ball-center rows/columns are +/-6.175 mm. The A1 reference grid coordinate is(-6.175,-6.175), but is absent. First existing row-A ball A2=(-5.525,-6.175). A20=(+6.175,-6.175); Y1=(-6.175,+6.175); Y20=(+6.175,+6.175).

Exactly10 absent positions: A1, E5, F5, R4, R5, T4, T5, T6, U4, U5. Remaining20x20-10=390 physical balls match the existing390-ball table.

Dimension-table values in mm:

| Symbol | Minimum | Nominal | Maximum | Meaning supported by figures |
|---|---:|---:|---:|---|
| A | 0.770 | 0.870 | 0.970 | Overall height |
| A1 | 0.160 | 0.210 | 0.260 | Stand-off dimension; not ball-name A1 |
| A2 | 0.600 | 0.660 | 0.720 | Body thickness dimension |
| c | 0.180 | 0.210 | 0.240 | Substrate dimension c |
| D/E | 12.900 | 13.000 | 13.100 | Body sides |
| D1/E1 | - | 12.350 | - | Ball-center spans |
| e | - | 0.650 | - | Pitch |
| b | 0.250 | 0.300 | 0.350 | Ball diameter parallel to datum C |

The drawing's tolerance table also lists aaa0.100, bbb0.100, ddd0.080, eee0.150, fff0.080. Their actual GD&T frames remain in the cited drawings; they are not PCB fabrication dimensions. The ball count N is390 and MD/ME is20/20. A separate nominal ball-diameter entry is0.300 mm.

Verification: a dark-neutral-pixel/connected-component pass over the official bottom-view mechanical drawing detected390 ball-ring components. Converting bottom-view columns to top-view yielded exactly the same10 holes as the official function grid and the existing390-ball table, without mismatches. The three mechanical images were downloaded from the exact official links above and visually reviewed; their hashes are recorded.

## Land-pattern and release boundaries

These sources establish nominal package ball centers and package dimensions, not complete board land patterns. In particular the following remain UNVERIFIED and must not be marked manufacturer-qualified:

1. PCB copper land diameter, land tolerance, NSMD versus SMD choice and copper shape
2. PCB solder-mask opening/expansion, mask registration allowance and minimum mask web
3. Paste aperture diameter/shape/reduction, stencil thickness and area-ratio/process qualification
4. Via-in-pad size, filling/capping/plating and escape/drill rules
5. Courtyard/assembly clearances and board-specific manufacturability limits

For RAM and eMMC, their0.31/0.30 mm callouts describe balls, not PCB pads. The0.15 GD&T callout describes package ball positioning, not a pad or via diameter. Neither inspected Samsung package page provides an explicit board copper/mask/paste recommendation.

The K230 guide says "Ball Solder Mask Opening:0.270mm" directly below the package drawings, together with package-datum/ball-diameter notes. This establishes a package-context mask-opening statement. It does not identify a board-side land pattern, state PCB NSMD/SMD, or give a copper diameter or stencil design. Do not treat0.270 mm as a verified board solder-mask opening without manufacturer clarification. In particular it cannot by itself justify board copper0.270/0.300 mm or a matching paste aperture.

A manufacturing-release footprint still needs an explicit supplier land-pattern/application recommendation or an approved PCB/assembly-house land-pattern design, tied to the selected stackup and process. This audit resolves the occupancy/orientation/center-coordinate gate only.
