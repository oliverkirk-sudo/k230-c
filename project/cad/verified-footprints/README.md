# Drawing-verified TI footprint library

Date: 2026-09-30. KiCad 9.0.2. This is an isolated engineering library, not a manufacturing release. No module master CAD or original carrier land pattern was changed.

## Editable outputs

The `CMK230_Verified.pretty` directory contains four front-side footprints:

- `TI_RSV0016A_TMUX1574_1.8x2.6_P0.4_DrawingVerified`: TMUX1574RSVR, 16 numbered copper pads
- `TI_DBV0005A_SN74LVC1G32_SOT23_5_DrawingVerified`: SN74LVC1G32DBVR, 5 numbered copper pads
- `TI_DMQ0006A_TPS6282xA_1.5x1.5_SMD_DrawingVerified`: TPS62824A/25A/26A/27A DMQ family, 6 numbered copper pads
- `TI_YCG0015_TPS628640_1.05x1.78_P0.35_SMD_DrawingVerified`: TPS628640BYCGR, 15 numbered copper pads

`DrawingVerified` means the package outline, numbered copper positions, exposed-metal geometry and TI example stencil were checked against the actual official drawing. It does not mean the selected PCB/assembly process has approved them. Numeric copper overlap and mask expansions chosen within TI's limits, and courtyard clearances chosen by the project, are documented separately from manufacturer dimensions.

`fp-lib-table` resolves the library relative to this directory. `Footprint_Geometry_QA_ONLY.kicad_pcb` and `.kicad_pro` load all four footprints on an isolated test coupon. That board has isolated one-pad nets, no functional circuit, no escape routing and no actual module connector. It is only for footprint geometry/DRC inspection. Do not send its QA Gerbers to manufacturing.

## Critical editing convention

Each footprint has one explicit, unnumbered `F.Mask`-only aperture per electrical pad. DMQ and YCG additionally have one unnumbered `F.Paste`-only aperture per electrical pad. These are deliberate CAD primitives, not extra pins. Preserve them when importing or modifying the footprints.

Copper pads intentionally omit `F.Mask`, avoiding two superimposed mask openings. All explicit mask apertures have local mask margin zero. All paste apertures have local paste margin and ratio zero. This keeps global board defaults from changing the audited example geometry.

Why explicit mask apertures? KiCad's ordinary rounded-pad mask-margin calculation rescales the corner radius with pad dimensions. It does not preserve the exact constant-radius offset required to reproduce the TI examples. Separate apertures preserve the DMQ exposed R0.05 corners and the specified circular YCG opening; native Gerber export was checked directly.

Coordinates are millimetres in component-side view: origin at nominal body center, +X right, +Y down. Pin 1/A1 is at the upper-left orientation. `F.Fab` shows nominal body with an orientation chamfer; `Dwgs.User` shows maximum body excluding any noted additional flash; `F.CrtYd` is a project-selected assembly clearance. There is no thermal center pad on RSV or DMQ.

## What remains before board release

- PCB/assembly-house approval of copper tolerances, mask registration/overlap, soldermask web, stencil design and paste process
- YCG's selected minimum-overlap SMD copper has 0.085 mm neighbor clearance at 0.35 mm pitch. Validate the selected fabricator's fine-pitch/HDI and escape capabilities
- TI's YCG paste example assumes a 0.075 mm stencil; the other three examples assume 0.125 mm. A single top-side board process needs an approved common or stepped-stencil solution, not unreviewed mixing of those examples
- Complete selected MPN/symbol-to-pad audit after integrating these footprints into the real schematic/PCB
- Placement, signal/power integrity, routing, thermal, assembly and real-board checks
- RAM, eMMC and K230 copper/mask/paste land patterns and module castellation manufacturing geometry remain separate release gates

See `../../engineering/mechanical/README.md` and the accompanying reports, layer gallery and verification JSONs.

## Compact alternatives addendum

`compact-options/` adds separate drawing-checked DRL and DCK logic-package candidates and a TPS3808 DRV WSON candidate. This does not change the four footprints above. Read its README before assigning them: TPS3808 requires every signal to be remapped and exposed pad 7 connected to GND. The compact audit covers SN74AUP1G06/07/08/17 within each same base part. See `../../engineering/mechanical/compact-package-audit.md` for source/verification evidence and bounded area comparisons.
