# R7 independent audit

2026-10-03. **Pass for the bounded identity/geometry and fabricated-feature change, with the assembly-stencil gate below remaining open.** No application, factory, thermal, lifetime, boot, routed-board or production qualification follows.

The audit compares the published R6 project with the R7 candidate. Main CAD was read-only; checked schematic, PCB, footprint, symbol and project-file hashes were unchanged by this audit. Native tests used KiCad 9.0.2 and separate input copies and output fixtures.

## Exact schematic delta

Fresh native netlist exports and an independent structural comparison of every active schematic confirmed:

- All 254 component values and all 1509 pin/net/function/type bindings are unchanged across 457 nets
- Exactly ten footprint fields changed: R205, R206, R220, R221, R401, R528, R561, JP1, TP81 and TP82
- Exactly three BOM flags changed from included to excluded: JP1, TP81 and TP82
- All on-board flags and DNP states are unchanged; JP1, R45, R47 and R528 remain DNP
- The root schematic's revision label changed from RCV-R6 to RCV-R7; this is the sole additional schematic metadata delta
- Assigned-reference coverage rises from 192/254 to 202/254, leaving 52 unassigned

The full schematic comparison normalized only those explicit fields and that one revision label. Everything else had to match. It did not rely on the implementation's assignment file to establish the changed-reference set. Fresh R7 ERC reports zero violations. See [independent-review.json](independent-review.json), [input-sha256.json](input-sha256.json), [r6-fresh.xml](r6-fresh.xml) and [r7-fresh.xml](r7-fresh.xml).

## Native land and feature checks

The actual library files were resolved from R7's footprint table and loaded with KiCad. The seven passive references retain their original value strings and the source-backed copper:

| Reference | Each pad x × y, mm | Pad center x, mm | Inner gap, mm |
|---|---:|---:|---:|
| R205/R206, existing TNPW | 0.55 × 0.60 | ±0.475 | 0.40 |
| R220, new WSL0603…9 | 1.01 × 1.01 | ±0.755 | 0.50 |
| R561, new WFZ0402 | 0.50 × 0.60 | ±0.450 | 0.40 |
| R221/R401/R528, existing CRCW | 0.28 × 0.43 | ±0.255 | 0.23 |

WSL's 1.80 × 1.02 mm fabrication body envelope conservatively contains the source's 1.774 × 1.014 mm maximum body; its courtyard is 3.12 × 1.62 mm. WFZ's body envelope is 1.10 × 0.60 mm and its courtyard is 2.00 × 1.20 mm. Both use 0.05 mm mask expansion and separate 1:1 paste apertures. These are explicit process candidates; the courtyards are project constructions, not manufacturer approval. Copper agrees with the earlier drawing review of [Vishay WSL p2](https://www.vishay.com/docs/30192/wsl-9.pdf), [WFZ p2](https://www.vishay.com/docs/30432/wfz-jumper.pdf), [TNPW source lands p1](https://www.vishay.com/doc?28950) and [CRCW p2](https://www.vishay.com/docs/20052/crcw0201e3.pdf).

JP1 has two 0.70 × 1.00 mm top pads at x = ±0.50 mm, leaving a 0.30 mm copper gap. There is no connecting copper, paste, track or zone in its definition. It remains DNP/open. Its pad nets remain MODE_TF and VDD_3V3. TP81/TP82 each have one circular 0.80 mm bare top pad, no paste and no drill, retaining PMU_OUT0_STATUS and PMU_OUT1_STATUS respectively. All three remain schematic-bound, on-board features, excluded from BOM and position files; none is marked BoardOnly.

## Actual copper, paste and placement exports

The independent fixture contains all ten reviewed references, including R528. It uses a deliberately isolated six-layer, 38 × 20 mm test outline with no routing; this is not the 38 × 38 mm module layout. Embedded footprints and copied source definitions are included solely for reproducible inspection.

Default native Gerber exports contain 18 copper flashes, 18 mask flashes and 14 paste flashes. JP1's two copper pads and both test pads remain present. No connecting copper line is emitted. JP1, TP81 and TP82 have no paste apertures.

**R528's two paste apertures remain in KiCad's default F.Paste export even though it is DNP and excluded from placement.** DNP/BOM/position attributes therefore do not establish a safe production stencil. A deliberate assembly/stencil variant, followed by inspection of its generated paste output, is required before manufacturing. The diagnostic Gerbers in this folder must not be released as production outputs.

Both [default placement export](positions_default.csv) and the export with `--exclude-dnp` include exactly R205, R206, R220, R221, R401 and R561. R528 and all three fabricated features are absent. Thus placement exclusion and copper retention work as intended, independently of the still-open stencil decision.

The [native copper preview](copper-review.svg) was inspected. JP1 is visibly open, R528's pads remain and the two test pads are present. The two unlabeled upper-row pairs are R205/R206, whose existing reference fields are on F.Fab rather than F.SilkS.

## Shared population helper

The helper preserves pad positions, sizes and net identities while applying the intended attributes. Independent negative controls rejected BoardOnly on an ordinary resistor and on JP1, removal of position exclusion from R528 or TP81, removal of JP1's DNP state, and reintroduction of TP82 to the BOM. These checks exercise actual native footprint attributes.

Native fixture DRC has zero rule violations and **three expected unrouted connections** on its retained shared nets: VDD_3V3, GND and VDD1P8. These are explicitly reported in [fixture-drc.json](fixture-drc.json); this is not a connected or fabrication-ready circuit. [native-checks.json](native-checks.json) records the commands and results.

## Remaining limits and reproduction

The previous precision/lifetime, hot-resistance/current, R401 firmware/input, R221 branch-current and R528 boot-voltage gates remain open. Assigning these footprints does not resolve them. The mechanical body/courtyard checks establish the geometry represented in this candidate, not top-side fit, escape routing, solder-process acceptance or six-layer production feasibility.

[validate_independent.py](validate_independent.py) accepts explicit `--baseline`, `--project`, `--output` and `--runtime` paths. Run it with the system Python that provides pcbnew. It copies input CAD into the runtime location, exports fresh netlists, checks the allowed deltas, loads native footprints, exercises population controls and creates the diagnostic fixture/exports. Its generated outputs belong in an audit directory, never the active board or manufacturing package.
