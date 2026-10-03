# Placement-only feasibility canvas

Open `CMK230_Placement_ONLY_NOT_FOR_FAB.kicad_pcb` in KiCad 9. This is an isolated 38 x 38 mm body-fit illustration, not the module master PCB or a fabrication file.

## What is on the canvas

All 13 represented ICs are on the front/top side:

- U1 K230, U2 K4F8E304HB LPDDR4, U3 KLMAG1JETD eMMC: mechanical placeholders with verified body dimensions and 390/200/153 ball-center cross marks. They contain **zero copper, mask, paste or drilled pads**
- U11-U13 TMUX1574RSVR and U14 SN74LVC1G32DBVR: the drawing-verified footprints
- U21 TPS62827ADMQ, U24/U26 TPS62826ADMQ, U25 TPS62825ADMQ: the drawing-verified DMQ footprint
- U22/U23 TPS628640BYCGR: the drawing-verified YCG footprint

Small-part counts and references come from the current component register. Their nets are intentionally isolated per pad, solely so local geometry DRC can detect spacing errors. Those dummy nets do not represent the schematic or any intended electrical connectivity. No schematic parity test is claimed.

The 743 BGA center crosses on Dwgs.User are dimensionless position markers, not ball outlines, PCB copper lands or drilling targets. The mechanical placeholders are excluded from BOM/position output. Their nominal body is on F.Fab, maximum body on Dwgs.User, and a project-selected 0.25 mm assembly clearance surrounds the maximum body on F.CrtYd. These clearances are not validated BGA routing/assembly rules.

## Bounded result

All selected assembly envelopes fit without overlap inside the 38 x 38 outline. The minimum chosen courtyard-to-outline distance is 2.45 mm; the minimum pair gap is 0.85 mm between U11 and U24. An illustrative 2 mm inset is on Dwgs.User only. It is not a castellation footprint, board cut, routing keepout, or verified manufacturing edge reserve.

Native KiCad DRC reports zero violations for this isolated drawing under its local geometry-test settings. There are no routes, vias, zones, drills, castellated pads or production BGA pads. Because each dummy net has one pad, zero unconnected DRC items has no implication for circuit connectivity.

## What this does not prove

- Final BOM fit: inductors, decoupling, passives, crystals, supervisors and test access are not placed
- Required regulator input/output capacitance or power-current loop fit
- Short DDR connections, signal integrity, escape routing, stackup, via fanout or layer count
- Power distribution, thermal design, assembly tolerance, yield or rework access
- The 140-contact module castellation drill/plating/edge geometry

The physical placement choices are illustrative. In particular regulator locations are not optimized for their loads or thermal paths. Do not treat open whitespace as proven routing or passive-component capacity.

Files in `../../../engineering/mechanical/`:

- `placement-only-canvas.png`: readable annotated review image
- `placement-only-native.svg` / `.png`: actual native KiCad rendering
- `placement-only-positions.csv`: editable instance-position list
- `placement-only-verification.json`: count/envelope/entity checks
- `placement-only-drc.json`: bounded native DRC result
- `build_placement_only_canvas.py` / `render_placement_only.py`: reproducible authoring and preview scripts

No Gerbers for this placement illustration were generated. Do not manufacture it.
