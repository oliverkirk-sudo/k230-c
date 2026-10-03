# Mechanical and footprint audit

Date: 2026-09-30. Scope: selected TI footprints and BGA package coordinates for the 38 x 38 mm top-component CM-K230 review. No master CAD edited. No module castellation geometry inferred from the existing carrier mating footprint.

## Outcomes

- Four editable TI footprints in `../../cad/verified-footprints/CMK230_Verified.pretty`
- 42 numbered copper pads; 42 explicit mask openings; 42 paste apertures
- 568 independent numeric checks through KiCad's parser, including pin positions, sizes, corners, layer membership, mask/paste and courtyard enclosure
- Native KiCad DRC on the isolated footprint QA board: 0 violations, 0 unconnected items. Its 0.075 mm local clearance rule is a geometry-test setting, not evidence a PCB vendor can manufacture the module
- Native Gerber verification: all 42 flashes on each of F.Cu/F.Mask/F.Paste match independently transcribed positions, dimensions, shapes and corner radii
- Independent manufacturer-source extraction corroborates 200 RAM, 153 eMMC and 390 K230 physical-ball centers with no occupancy mismatches

## TI drawing results

| Package | Body nominal / maximum, mm | Drawing-verified exposed pattern | Chosen copper / mask details | Courtyard, mm |
|---|---|---|---|---|
| RSV0016A | 1.80 x 2.60 / 1.85 x 2.65 | 0.4 pitch; 15 lands 0.6 x 0.2; pin1 0.7 x 0.2 | NSMD; copper = exposed land; explicit 0.05 expansion; constant-offset corners | 2.80 x 3.60 |
| DBV0005A | 1.60 x 2.90 / 1.75 x 3.05 | 1.1 x 0.6 lands; x=+/-1.3; y=0,+/-0.95 | NSMD; chosen 0.05 expansion within TI 0.07 max | 4.30 x 4.10 |
| DMQ0006A | 1.50 square / 1.55 square | left 0.6 x 0.25 at x=-0.65; right 1.0 x 0.2 at x=+0.45; y=0,+/-0.5 | TI-preferred SMD; chosen minimum 0.05 copper overlap each side; copper 0.70 x 0.35 / 1.10 x 0.30; exposed R0.05 | 2.50 x 2.10 |
| YCG0015 | 1.05 x 1.78 / 1.07 x 1.80 | 3 columns x 5 rows at 0.35 pitch; 0.200 circular exposed opening | TI-preferred SMD; chosen minimum 0.0325 overlap; copper diameter 0.265; aperture diameter 0.200 | 1.60 x 2.30 |

Courtyards are project-selected: at least 0.25 mm beyond maximum body/copper/mask envelope, rounded outward to 0.05 mm. DBV additionally accounts for the drawing's possible 0.25 mm body flash per side. Courtyards are not vendor package dimensions or an approved module placement density rule.

RSV pin1 center is (-0.75,-0.60), while the other left-side centers are x=-0.80. Its longer land shares the same outer edge as the other left lands. The RSV top-view functional pinout differs from the TSSOP package. DMQ's data-sheet function diagram is a bottom view; the footprint is transformed to the component-side pattern with pin1 upper-left. YCG A1 is (-0.35,-0.70), A3 (+0.35,-0.70), E1 (-0.35,+0.70).

The YCG stencil aperture is a 0.21 mm rounded square with R0.05 corners, not a 0.21 mm circular aperture. Its TI example stencil is 0.075 mm thick. RSV/DBV/DMQ examples are 0.125 mm. Those are assembly examples rather than automatically compatible selections for one board; obtain a reviewed common or stepped stencil.

Selected drawn minimum copper / mask gaps: RSV 0.200 / 0.100 mm; DBV 0.350 / 0.250 mm; DMQ 0.150 / 0.250 mm; YCG 0.085 / 0.150 mm. These are nominal geometric gaps, not guaranteed post-fabrication tolerances. SMD overlaps at the minimum must still be qualified for registration and etch tolerances.

## Existing KiCad library comparison

The installed libraries were read and preserved unchanged. Their common package names are not exact replacements for these TI examples:

- `SOT-23-5`: IPC-generated pads at x=+/-1.1375, size 1.325 x 0.6, rather than the TI example x=+/-1.3, size 1.1 x 0.6
- `UQFN-16_1.8x2.6mm_P0.4mm`: different IPC land lengths/centers (pin1 0.9 x 0.2 at -0.8,-0.6; others 0.8 long), rather than the exact RSV board example
- `WSON-6_1.5x1.5mm_P0.5mm`: TLV702-derived generic geometry; cannot substitute for DMQ's asymmetric short/long contacts
- A same-body QFN with a center exposed pad is not valid for RSV. No such pad was added

The installed-library JSON records actual parsed dimensions and rotations. Different IPC land dimensions are not themselves proof an installed footprint is unsafe; they simply do not reproduce the selected official TI land examples.

## Evidence and reproduction

- `small-parts-footprint-spec.json`: package dimensions, exact sources, process choices and build data
- `small-parts-pad-coordinate-audit.csv`: electrical pad positions and functions
- `small-parts-verification.json`: native-parser checks and footprint hashes
- `native-gerber-verification.json`: independently checked KiCad-exported aperture geometry
- `footprint-geometry-qa-drc.json`: native DRC result
- `TI-footprint-layer-gallery.png`: copper/mask/paste layers rendered from actual loaded footprint objects
- `native-svg/`, `native-render/`: KiCad's own footprint exports, visually reviewed
- Official PDF page/image evidence is retained outside this distributable tree in the reference workspace; source manifest records URLs and hashes
- `ti-source-manifest.json`: official URLs, local reviewed source hashes and pages
- `installed-kicad-library-comparison.json`: installed package comparisons
- `bga-mechanical-audit.md` and `bga-*-physical-centers.csv`: independent BGA findings, sources, centered coordinates and release boundaries

Run `python3 build_verified_footprints.py`, then `/usr/bin/python3 validate_verified_footprints.py`. Export the isolated QA board F.Cu/F.Mask/F.Paste through `kicad-cli pcb export gerbers`, then run `python3 check_native_gerbers.py`. The validator deliberately does not import the generator's spec; the Gerber validator uses a separate transcription. Native KiCad Python is available in `/usr/bin/python3`.

If regenerating exports, point XDG_CONFIG_HOME, XDG_CACHE_HOME and XDG_DATA_HOME to writable temporary locations. The footprint library uses explicit local mask/paste settings; keep the unnumbered mask/paste primitives when integrating.

Original manufacturer PDFs and source-image copies are research evidence, not new licensed package deliverables; preserve their attribution/usage terms and use source links in any externally distributed package. This audit does not expand source redistribution rights.

## Remaining release boundaries

The three large BGA sources establish occupancy, ball-center pitch, body envelope and orientation, not a complete PCB copper/mask/stencil design. Never use the published ball diameter as an automatic PCB pad diameter. K230's 0.270 mm mask statement is package-context evidence; it does not alone establish a board land pattern. Module castellations, drill/plating/edge offsets and the manufacturing edge definition remain unverified separately from the original carrier land pattern.

## Placement-only continuation

`../../cad/verified-footprints/placement-only/` contains an isolated 38 x 38 mm editable KiCad canvas with the 3 BGA mechanical placeholders and the actual 10 small-IC instances of the four verified TI footprint types. All are top-side. `placement-only-canvas.png` is the annotated preview. The 13 chosen assembly envelopes fit without overlaps (minimum pair gap 0.85 mm; outline gap 2.45 mm). There are no BGA copper/mask/paste pads, routes, vias, drills, zones or edge contacts. See the canvas README for the explicit omissions: this is body-fit evidence only, not proof of escape, passive fit, thermal/PDN performance or manufacturing feasibility.

## Compact-package alternatives, 2026-09-30 continuation

The expanded BOM makes the original 13-IC body canvas insufficient as a full-fit result. `compact-package-audit.md` reviews pin-equivalent DRL/DCK choices for SN74AUP1G06/07/08/17 and the exact TPS3808 DBV-to-DRV remap, with three new editable candidate footprints in `../../cad/verified-footprints/compact-options/`. Five AUP DRL instances plus two TPS3808 DRV instances recover 30.04 mm² against seven rough 11.52 mm² DBV reservations. The compact candidate coupon passes 226 native numeric checks and independent copper/mask/paste Gerber checks; no master integration was done.

`compact-inductor-mechanical-review.md` records the official DFE201610E-R47M drawing and 6.67 mm² body/land or 7.20 mm² hypothetical mask-sensitive reservations, pending electrical/thermal selection. `compact-area-scenarios.json` freezes the old area-screen hash and keeps the proposed savings separate from a latest full-BOM estimate. A limited U96-only update leaves essentially no arithmetic margin even before complete routing and support-part changes. These remain area-screen candidates, not proof of manufacturable single-sided fit.

Latest correction: U92/U94 use the six-pad SN74AUP1G97 DRL Schmitt-AND footprint; U96 and its capacitor are removed by the design lead. The older five-AUP area scenarios are historical, as is the optional eight-rail monitor assumption. See the first section of `compact-package-audit.md` and `compact-AUP1G97-status.json`. The expanded compact library now passes 302 numeric checks and 23/23/24 copper/mask/paste Gerber checks.
