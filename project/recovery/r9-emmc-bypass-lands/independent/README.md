# Independent R9 audit

**PASS, bounded to schematic identity and isolated footprint geometry.**

The candidate was compared with the exact R8 project supplied for this audit. No substantive implementation defect was found. The six footprint assignments are the only component changes: C64/C65/C69/C70/C71/C72. The root schematic revision text changes from RCV-R8 to RCV-R9 and is explicitly allowed separately.

## Verified

- All 254 physical component references, values, library identities, sheet identities, BOM/on-board/DNP states and other schematic attributes are preserved. The full schematic syntax trees match after only the six footprint properties and root revision text are adjusted. The candidate BOM CSV is byte-identical.
- All 1,509 pin bindings and their net/node attributes match R8; there are 457 distinct nets. Fresh KiCad netlist export matches the saved candidate graph. Coverage is 221 assigned and 33 unassigned.
- C64/C65 remain on EMMC_VDDIM; C69/C70 on VEMMC_IO; C71/C72 on VDD_3V3. All six returns remain GND. VEMMC_IO still connects to VDD1P8 through R561.
- The 0603 copper lands are 0.65 x 0.70 mm at X +/-0.675 mm. The 0402 lands are 0.40 x 0.50 mm at X +/-0.400 mm. Both match the applicable Murata reflow ranges and their exact-part body-tolerance rows.
- Maximum body outlines are 1.70 x 0.90 mm and 1.05 x 0.55 mm. Courtyards are 2.60 x 1.50 mm and 1.80 x 1.20 mm. Courtyard, +0.05 mm mask expansion and separate 1:1 paste pads remain engineering choices without assembly qualification.
- Saved and newly exported native CAM both contain four correctly sized and positioned flashes on each of F.Cu, F.Paste and F.Mask. Mask outer dimensions are copper plus 0.10 mm on each axis; their 0.05 mm corner expansion is included in the checked RoundRect aperture calculation.
- Independent native KiCad 9.0.2 checks: ERC 0 violations; isolated fixture DRC 0 violations and 0 unconnected items. Input CAD hashes were unchanged after the audit.

## Negative controls

Seven deliberate defects were rejected by the same checks used for the candidate:

1. C64 CReg rail changed to VEMMC_IO
2. C69 VCCQ rail changed to VDD_3V3
3. C71 VCC rail changed to EMMC_VDDIM
4. C69 nominal value changed to 3.3 uF
5. C65 population changed by adding DNP
6. A 0603 copper pad changed to 0.40 x 0.50 mm
7. A saved native fixture with C64 pad 2 moved to leave 0.10 mm copper clearance

The last control generated a native clearance error against the 0.20 mm rule and exit code 5. It also generated the expected library-footprint mismatch warning caused by the mutation. Detection therefore does not rely only on a library mismatch, a filename or an assertion that two files differ. The negative fixture and native report are included for reproducibility.

## Sources and limits

The copper and maximum-body facts were checked against the prior manufacturer-authored exact-part review and its visually inspected drawings: [Murata GRM188R71A225KE15-04A](https://www.mouser.com/datasheet/2/281/1/GRM188R71A225KE15_04A-1985813.pdf), pp. 1 and 26, and [Murata GRM155R71C104KA88-01 via LCSC](https://www.lcsc.com/datasheet/C71629.pdf), pp. 1 and 26. The respective +/-0.10 mm and +/-0.05 mm L/W tolerances both use the reflow table row for tolerance within +/-0.10 mm. Raw manufacturer files remain excluded.

This is a two-footprint fixture with synthetic separate nets. It is not a module layout, six-layer routing proof, BGA escape review, assembly qualification, thermal validation or effective-capacitance qualification. Micron Table 13's nominal/effective interpretation, actual hot/bias/aging performance and JLC MOQ1 remain open as recorded in the source review.

## Re-run

Run the included portable argparse validator using a Python environment with the installed KiCad pcbnew bindings and kicad-cli:

    /usr/bin/python3 validate_r9_independent.py --baseline /path/to/r8/project --candidate /path/to/r9/project --output /path/to/separate/audit-output

The output must be outside both input projects. The script checks inputs read-only, creates and modifies native control fixtures only in temporary storage, normalizes execution paths in reports, and writes the review outputs. Runtime caches and Python bytecode are excluded from the handoff. The validator is independently implemented and does not invoke the candidate's validate_coverage.py.

See independent-review.json, footprint-geometry.json, cam-verification.json, population-states.json, fresh-master.xml, fresh-erc.json, fresh-fixture-drc.json, negative-clearance-drc.json, native-command-log.json and artifact-sha256.json for machine-readable evidence.
