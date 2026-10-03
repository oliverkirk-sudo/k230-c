# Compact package candidates: footprint audit only

Date: 2026-09-30. These editable KiCad candidates reduce selected package reservations. The integrated schematic, netlist, BOM and PCB have not been modified.


## Latest reset correction

U92/U94 require `TI_DRL0006A_AUP1G97_DrawingVerified_CANDIDATE`, the verified six-pad Schmitt configurable gate. B1 and GND2 connect GND; A3 and C6 are the signals; Y4 is the AND output; VCC5 is the supply. This is a logic/symbol change from 1G08, not a five-pad footprint swap. U96 was removed by the design lead. Previous five-AUP area scenarios are historical and do not describe the latest compact monitor topology.

DRL6 uses the same chosen 2.8 x 2.5 mm courtyard as DRL5, but has six 0.67 x 0.30 mm lands at x=±0.74 mm, y=-0.5/0/+0.5 mm. Pins 1/2/3 run down the left; 6/5/4 down the right. No exposed pad. Official source pp 1-3 and 18-20 were visually reviewed. Eight function-table rows and all four B=0 AND rows check correctly.

## Library and assignments

Library nickname: `CMK230_Compact_Candidates`. Paths are relative to this folder through `fp-lib-table`.

- `TI_DRL0005A_AUP_5P_DrawingVerified_CANDIDATE`: compact candidate for SN74AUP1G06DRLR, SN74AUP1G07DRLR, SN74AUP1G08DRLR and SN74AUP1G17DRLR. Replace the package of the **same base part**, not one logic function with another. The DRL pin numbering matches that part's DBV/DCK numbering
- `TI_DCK0005A_AUP_5P_DrawingVerified_CANDIDATE`: SC70 alternative. Its smaller body does not improve the current optimistic area-screen reservation under the conservative courtyard method used here
- `TI_DRV0006A_D_TPS3808_6P_EP7_DrawingVerified_CANDIDATE`: TPS3808G01DRVR WSON candidate. DRV0006A and DRV0006D official example copper/mask/stencil geometry match. This is **not a footprint-only swap** from DBV: every signal changes pin number, and exposed pad 7 must be added and connected to GND

Exact mappings and the bounded current U89/U90 net adaptation are in `../../../engineering/mechanical/compact-package-pin-remap.csv` and `compact-TPS3808-proposed-net-remap.csv`. The latter is a snapshot, not an integration approval. Preserve intentional open CT on new DRV pin 3 if retaining the current20ms timing option.

## Geometry and process boundaries

All footprints are component-side/top view, with +X right and +Y down. F.Fab is the midpoint of the drawing's body range, not an additional manufacturer tolerance. Dwgs.User is the specified maximum body. Courtyard is a project-chosen envelope and includes stated mold flash plus at least 0.25 mm around body/mask/lands, rounded outward to 0.05 mm.

Chosen courtyard dimensions: DRL 2.8x2.5 mm (7.00 mm²); DCK 3.8x3.2 mm (12.16 mm²); DRV 3.0x2.6 mm (7.80 mm²). These are candidates requiring assembly/process review.

As in the main verified library, mask openings are explicit unnumbered F.Mask-only pad primitives. Keep these. Local mask margin is zero to avoid changing the audited shapes with board defaults. The chosen NSMD expansion is 0.05 mm per side, within TI's drawing limits. Paste margin and ratio are locked to zero. All signal-pad copper/stencil corners are R0.05; mask corners are R0.10.

DRV exposed copper pad 7 is 1.0x1.6 mm. Two 1.0x0.7 mm paste windows, R0.05, are centered at y=-0.45/+0.45 mm. TI labels the example 88% paste coverage. Thermal-pad soldering and GND connection are required. Optional thermal vias shown in the TI example are not instantiated because stackup/fill/drill choices remain open.

DRL's official stencil example is 0.100 mm thick. DCK/DRV examples are 0.125 mm. Existing YCG examples use 0.075 mm. Those must be reconciled by the assembly house; package downsizing does not automatically qualify one common stencil/process.

## Verification

`Compact_Package_Geometry_QA_ONLY.kicad_pcb` is an isolated geometry coupon, with dummy single-pad nets. Its zero DRC violations/unconnected items do not establish a connected or manufacturable module. Native parser tests check 302 dimensions/layer/radius conditions. Native Gerber checks independently verify 23 copper, 23 mask and 24 paste apertures. Actual source drawings and KiCad-rendered outputs were visually inspected. No production Gerbers are produced.

Full analysis: `../../../engineering/mechanical/compact-package-audit.md`. Rendered layer gallery: `compact-footprint-layer-gallery.png` in that folder. Source PDFs/images remain outside the distributable tree; URLs, page references and hashes are supplied.
