# Compact-package audit: Schmitt correction and alternatives

Date: 2026-09-30. Scope: package-only alternatives for selected AUP logic, TPS3808 supervisors, and mechanical inductor reservations. This is a derived engineering review, not a production release or master-CAD edit. No capacitors were removed or values changed to force an area result.


## Latest correction: SN74AUP1G97 Schmitt AND

This supersedes the earlier proposed 1G08/1G17 reset arrangement and its area scenarios. U92/U94 now use SN74AUP1G97DRLR, U91/U93 retain SN74AUP1G07/06 DRL5, and U89/U90 retain TPS3808 DRV with grounded EP7. U96 and its capacitor are removed by the design lead. The optional eight-rail monitor network is omitted from the latest topology. No old area total below describes that latest BOM.

The 100 kΩ / 100 nF external-reset RC creates slow edges, so this is an electrical Schmitt-input correction, not a pin-equivalent package change from 1G08. Official SN74AUP1G97 pp1-3 show B=pin1, GND=pin2, A=pin3, Y=pin4, VCC=pin5, C=pin6. All inputs are Schmitt-trigger. Page2's eight truth rows and page3's Figure4 confirm Y=(C?A:B); tying B pin1 to GND gives Y=A AND C. Pin2 must also connect GND. Both signal inputs therefore enter A3 and C6. No input is left floating.

New footprint: `CMK230_Compact_Candidates:TI_DRL0006A_AUP1G97_DrawingVerified_CANDIDATE`. It is in the same compact library. Six-pad drawing DRL0006A, 4223266/F, 11/2024, pp18-20: each copper land is 0.67 x 0.30 mm R0.05; x=±0.74 mm; y=-0.50,0,+0.50 mm. Pins 1/2/3 run down the left; 6/5/4 run down the right. Body X 1.1-1.3 mm, Y1.5-1.7 mm; height 0.6 mm max; allowed extra body flash 0.15 mm per side. The chosen courtyard remains 2.8 x 2.5 mm (7.00 mm²). Explicit NSMD mask openings use selected +0.05 mm per side, R0.10. Paste is 1:1 with copper; TI example stencil 0.100 mm. No exposed pad is present.

Updated verification covers all four compact alternatives: 302 native numeric checks, 23 copper/23 mask/24 paste Gerber apertures checked, zero isolated geometry-DRC violations. `compact-AUP1G97-status.json`, function-pin CSV and truth-table CSV preserve the specific logic evidence. No integrated master was edited by this footprint audit. Other compact footprints remain alternatives; they are not authorization to restore the obsolete reset topology.

## Historical decision-level result (superseded for latest BOM)

DRL is the useful logic-package candidate. The same SN74AUP1G06/07/08/17 base part can move from DBV to DRL without changing numbered signals. TPS3808G01 can use2x2 mm DRV WSON, but all six signals must be remapped and the grounded exposed pad added. Neither change selects the other logic functions or changes the intended supply/logic role.

For five AUP instances (U91, U92, U93, U94, U96) plus two TPS3808 instances (U89, U90), the chosen candidate envelopes recover 30.04 mm² compared with seven 11.52 mm² boxes in the rough screening convention. The DFE201610E-R47M inductor mechanical alternative can recover another 43.47 mm² for L24/L25/L26, or 41.88 mm² with the separately labeled mask-margin sensitivity. Electrical/thermal inductor qualification remains the design lead's task.

Those savings do not establish full-board fit. On the frozen 269-part area-screen baseline, then adding only the new U96 in DRL, the combined optimistic arithmetic is 1156.51 mm² against a provisional 1156 mm² interior. The mask-margin sensitivity gives 1158.10 mm². These limited counterfactual sums omit any other BOM updates and the new gate's support parts; they are not the latest full-design estimate. A zero/negative area difference would still not prove packing, local decoupling, fanout, routing, thermal or PDN feasibility.

## Exact electrical-pin equivalence

Official pin-function pages are page 3 of each AUP PDF, visually inspected:

- SN74AUP1G06: pin 1 NC,2 A,3 GND,4 Y (inverting open drain),5 VCC for DBV/DCK/DRL
- SN74AUP1G07: pin 1 NC,2 A,3 GND,4 Y (noninverting open drain),5 VCC for DBV/DCK/DRL
- SN74AUP1G08: pin 1 A,2 B,3 GND,4 Y (AND),5 VCC for DBV/DCK/DRL
- SN74AUP1G17: pin 1 NC,2 A,3 GND,4 Y (noninverting Schmitt buffer),5 VCC for DBV/DCK/DRL

This supports package-only substitution within each named base part. The functions are not interchangeable across these part numbers. Different package parasitics/thermal behavior and the application's voltage/temperature limits still require design review. All four DRLR ordering codes appear in their official package-option addenda; no stock or procurement guarantee is made.

Official TPS3808 pin table, page 4, requires DBV→DRV remapping:

| Function | DBV pin | DRV pin |
|---|---:|---:|
| RESET_N |1|6|
| GND |2|5|
| MR_N |3|4|
| CT |4|3|
| SENSE |5|2|
| VDD |6|1|
| Exposed thermal pad, connect GND | none |7|

The drawing labels the exposed land7. Data-sheet instructions require connecting the thermal pad to the ground plane; the package drawing requires soldering it. Add an explicit EP7 symbol pin and verify the real netlist after substitution. Renumbering only footprint pads to hide the package difference is not the recommended audit trail.

Current source assignments intentionally leave DBV CT pin 4 open for 20 ms timing. Retain that intentional open condition on DRV pin 3 if the same timing is retained. A current U89/U90 net adaptation is provided, but the supervisor circuit is being consolidated; recheck against the latest master before editing. This audit made no integration changes.

## Official drawings and chosen envelopes

The actual PDF pixels were inspected, not just extracted text. The full original PDFs and rendered source images remain outside this distributable directory. `compact-TI-source-manifest.json` records exact local hashes, official URLs and pages.

### AUP DRL0005A

Source drawing 4220753/E,11/2024. SN74AUP1G08 pp34-36;1G06 pp49-51;1G07 pp45-47;1G17 pp35-37.

- Body X 1.1-1.3 mm, Y1.5-1.7 mm; maximum height 0.6 mm; overall lead span1.5-1.7 mm
- Body drawing excludes mold flash/protrusions/gate burrs up to0.15 mm per side
- Five exposed metal lands 0.67x0.30 mm, R0.05. Centers x=±0.74; left y=-0.50,0,+0.50; right pin 4 y=+0.50, pin 5 y=-0.50
- NSMD preferred; selected explicit0.05 mm mask expansion equals the drawing maximum. Stencil 1:1 with lands, example 0.100 mm thick
- Chosen courtyard 2.8x2.5 mm=7.00 mm². Copper/mask drives X; body maximum plus flash drives Y. Source does not prescribe this courtyard

### AUP DCK0005A

Source drawing 4214834/G,11/2024. SN74AUP1G08 pp50-52;1G06 pp33-35;1G07 pp32-34.

- Body X 1.1-1.4 mm, Y1.85-2.15 mm; maximum height1.1 mm; overall lead span1.8-2.4 mm
- Up to0.25 mm body flash/protrusion per side is excluded from body dimensions
- Five 0.95x0.40 mm exposed lands, R0.05. Centers x=±1.10, left y=-0.65,0,+0.65; pin 4 lower right, pin 5 upper right
- NSMD preferred; selected 0.05 mm expansion is within TI 0.07 mm maximum. Stencil 1:1, example 0.125 mm thick
- Chosen courtyard 3.8x3.2 mm=12.16 mm². It does not beat the current 11.52 mm² rough DBV box because the latter is an optimistic screening assumption. It is not evidence that a DCK body is larger than DBV

### TPS3808 DRV0006A / DRV0006D

TPS3808 RevN PDF pp30-35 contains DRV0006D 4225563/A12/2019 and DRV0006A 4222173/C11/2025. Their board and stencil examples are geometrically identical; optional side-wall/wettable-flank package details do not change these board lands.

- Body 1.9-2.1 mm on both axes, maximum height0.8 mm
- Six 0.45x0.30 mm side lands, R0.05, x=±0.975; y=-0.65,0,+0.65. Component-side numbering1/2/3 down left,6/5/4 down right
- Exposed pad 7:1.0x1.6 mm copper, R0.05, center0,0
- NSMD preferred, chosen0.05 mm mask expansion within TI 0.07 mm maximum. Explicit mask pad 7 is1.1x1.7 mm
- Side lands use1:1 paste. EP7 uses two1.0x0.7 mm R0.05 apertures at 0,±0.45. The nominal rectangular area ratio is87.5%, rounded to88% in the TI drawing; rounding corners gives approximately87.35%. Do not replace this with one full-area EP paste aperture
- TI example stencil0.125 mm. Optional0.2 mm thermal vias shown in the drawing are not instantiated; via fill/cap/stackup/process choices remain unqualified
- Chosen courtyard 3.0x2.6 mm=7.80 mm²

## Area comparison and its limits

All candidate courtyards add at least 0.25 mm outside the relevant maximum body/flash, copper and selected mask aperture envelope, rounded outward to 0.05 mm. They are project assumptions, not TI specifications or routing keepouts.

| Alternative | Rough existing reservation each | Candidate each | Saving each |
|---|---:|---:|---:|
| AUP DBV→DRL |11.52|7.00|4.52|
| AUP DBV→DCK |11.52|12.16|-0.64|
| TPS3808 DBV→DRV |11.52|7.80|3.72|
| L24/L25/L26→DFE201610E, body/land reservation |21.16|6.67|14.49|
| Same inductor, hypothetical mask sensitivity |21.16|7.20|13.96|

Units aremm². The existing rough DBV box is not a verified same-policy footprint area: for example the prior official DBV0005A reconstruction using full flash/mask allowance occupied 17.63 mm². Therefore the savings above are modifications to the documented optimistic screen, not a comprehensive remeasurement of all 269+ components. More exact choices can increase other reservations.

`compact-area-scenarios.json` preserves baseline hash and the limited scenario arithmetic. No original baseline file was overwritten. Do not present its frozen sums as the latest consolidated BOM or infer spare routing area.

## Inductor mechanical review

See `compact-inductor-mechanical-review.md` and JSON. Murata's official J(E)TE243A-0001E-01 source gives body2.0±0.2x1.6±0.2 mm, height≤1.0 mm and recommended land envelope2.4x1.8 mm, gap0.8 mm. The provisional 2.9x2.3 mm envelope includes 0.25 mm around maximum body/lands only. Mask/stencil/land tolerances are not supplied and were not invented.

The source prohibits copper/through holes below the coil except electrode-connection copper and says adjacent parts must not contact the coil. No layer exemption is stated; obtain clarification before assuming inner-layer copper is allowed. This condition can affect PDN/escape feasibility even where the body fits. TI's table lists a candidate, not approval for each rail's peak/RMS current or operating temperature. No inductor footprint was released by this mechanical-only audit.

## CAD evidence and manufacturing boundary

Library: `../../cad/verified-footprints/compact-options/CMK230_Compact_Candidates.pretty`.

- Four editable footprints with explicit mask apertures; keep the unnumbered mask/paste primitives
- Independent native-parser verification: 302 numeric checks passed
- Independent native Gerber verification: 23 copper, 23 mask and 24 paste aperture positions, dimensions and corner radii passed
- Native KiCad DRC on isolated candidate coupon: 0 violations, 0 unconnected items. Dummy one-pad nets make this geometry-only, not circuit connectivity evidence
- `compact-footprint-layer-gallery.png` and native exports were visually reviewed
- Installed SOT-553, SC70 and DFN library footprints were compared; their IPC/example pad dimensions and EP stencil patterns differ from these exact TI examples. They were not silently substituted or edited

New DRL stencil 100 µm, existing YCG 75 µm and other TI examples 125 µm require a reviewed common or stepped-stencil process. Geometry checking does not approve mask registration at the minimum overlaps, actual assembly yield, thermal performance, supplier stock or the selected board stackup. The original 13-body canvas remains historical body-fit evidence only.
