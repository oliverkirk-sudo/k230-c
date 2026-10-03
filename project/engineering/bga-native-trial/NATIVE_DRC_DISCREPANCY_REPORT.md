# BH153 native local fanout trial

The frozen analytical witness was reproduced in editable KiCad 9.0.2 geometry for **MTFC16GAPALBH-AAT**. Native DRC reports **17 connectivity errors and 32 warnings**. It reports **no copper-clearance, drill, hole-clearance, annulus or mask-bridge violations at the declared nominal rules**. This is a local geometry result, not a routed module or manufacturing release.

## What is represented

The board contains one U3 footprint, all 153 physical 0.30 mm circular copper lands, 29 plated through vias of nominal 0.30/0.15 mm, and 16 track segments implementing the frozen witness. The 11 host signals have local exits on F.Cu (L1) and In2.Cu (L3); the VDDIM exit is also retained. A6 is VSS/GND with the remote ground via. M6 is CLK. DS remains on EMMC_DS_UNUSED without a route or via.

There are eight copper layers and a 1.2 mm reference thickness. No dielectric stack is supplied. The square 20 mm Edge.Cuts boundary is explicitly a computational analysis window, not the 38 mm module outline or proposed component placement. There are no additional components, port footprints, copper zones or invented plane connections.

Every U3 function and current net identity was checked against master-pin-assignments.csv and master.xml. VSS and VSSQ are GND; VCC is VDD_3V3; VCCQ is VEMMC_IO. The 109 NC, 4 RFU and 7 VSF lands retain distinct pin-function metadata and the XML's 120 unique unconnected net identities. None are joined. The 43 absent grid sites and 56 unsoldered package test contacts receive no PCB land, mask or paste aperture.

## Declared candidate rules

| Feature | Selected native rule / nominal geometry |
| --- | --- |
| Copper clearance | minimum 0.1016 mm |
| Track width | minimum / actual 0.1016 mm |
| Via land | minimum / maximum / actual 0.30 mm |
| Via hole | minimum / maximum / nominal request 0.15 mm |
| Via annulus | minimum / nominal 0.075 mm |
| Hole to other-net copper | minimum 0.20 mm |
| Hole to hole | minimum 0.20 mm |
| Front mask | 0.40 mm land aperture; minimum web 0.10 mm |
| Paste | 0.30 mm circular aperture |
| Stencil | 0.10 mm analysis assumption, unqualified |

The source-reviewed alternative JLCPCB table's 0.15/0.25 mm minimum via pair implies a 0.05 mm nominal annulus. This candidate instead uses the preferred +0.15 mm diameter increase and explicitly enforces the resulting 0.075 mm minimum. Those via-specific values do not replace generic component PTH or castellation rules. The original analytical file still records the earlier 0.1524 mm hole-to-copper assumption; alternate-via-process-check.json and this native trial apply the stricter 0.20 mm rule.

Filled, planarized, copper-capped VIPPO is **required**. The native through-via symbols display a nominal drill; they do not model the physical cap. Via tenting flags omit separate mask apertures, while each physical BGA land supplies its own 0.40 mm aperture. Tenting is not a substitute for filled/capped processing. Nominal mask web and annulus meet their chosen limits with zero tolerance margin. Mask registration, physical drill/tool diameter, plating, etch, registration/breakout, reflow and high-temperature reliability remain unqualified.

## Why the analytic and native results differ

| Native finding | Count | Explanation |
| --- | ---: | --- |
| Unconnected items, error | 17 | GND needs 10 joins, VDD_3V3 needs 3, and VEMMC_IO needs 4. The local witness supplies individual escapes, not a PDN |
| Dangling via, warning | 20 | All 20 PG escapes end without an attached inner plane or additional routing |
| Dangling track, warning | 12 | Eleven host signal exits plus the VDDIM exit deliberately end in the local window |
| Other native violations | 0 | No additional violations under the stated nominal settings |

The analytical proof screened separation of its modeled geometry. It did not claim board connectivity. KiCad adds these explicit unfinished-connectivity findings. Preserving real PG net identities is what lets KiCad report the missing connections. No severity was ignored, no DRC exclusion was added, and in-footprint solder-mask bridges are not allowed.

A single-pad net with a local trace stub is not a connection to the SoC. Native DRC cannot report a missing component absent from this deliberately isolated board. Full schematic parity is therefore not claimed or run; the standalone window's one U3 footprint is checked pin-by-pin against the source CSV/XML instead. All 11 host endpoints, supply distribution, VDDIM stabilization and bypass/return networks remain unfinished outside the window.

## Positive controls prove the checks are active

Separate copies under rule-controls intentionally tighten one rule at a time. The candidate's files remain unchanged during these checks.

| Positive control | Expected native error | Findings |
| --- | --- | ---: |
| Annulus minimum 0.080 mm | annular_width | 29 |
| Hole-to-other-net copper 0.280 mm | hole_clearance | 199 |
| Hole-to-hole minimum 0.360 mm | hole_to_hole | 21 |
| Mask web minimum 0.110 mm | solder_mask_bridge | 200 |

These counts demonstrate enforcement, not additional candidate violations. See rule-control-results.json and the raw control reports. The real candidate retains 0.075/0.20/0.20/0.10 mm respectively.

## Editable files, evidence and reproduction

- Board, project and custom rules: ../../cad/bga-engineering-candidates/bh153-sparse-trial/BH153_SPARSE_LOCAL_TRIAL.kicad_pcb, .kicad_pro and .kicad_dru
- Footprint library: ../../cad/bga-engineering-candidates/bh153-sparse-trial/BH153_Engineering.pretty
- Native SVG exports and PNG renders: ../../cad/bga-engineering-candidates/bh153-sparse-trial/preview
- Unfiltered DRC output: native-drc.json, native-drc.log and native-drc-command.json
- Source and pin identities: source-manifest.json and native-net-mapping.csv/.json
- Re-import checks: native-validation.json
- Independent native parser audit: native-independent-review.json and verify_native_emmc_independent.py; all 1,009 checks passed on the final annotated board, including corroboration of the four raw control reports

Run with the installed distribution Python and KiCad 9: first generate_bh153_native_trial.py, then check_native_rule_controls.py, then verify_native_trial.py. Each script configures the requested temporary KiCad XDG directories. The generator also runs native SVG export and Inkscape rasterization. No external vendor upload, contact or order is performed; the restricted Micron CSN-33 source was not accessed or retried.

KiCad rule semantics: https://docs.kicad.org/9.0/en/pcbnew/pcbnew.html. Process-rule source and limitations are preserved in the frozen alternate-via-process-check.json. Exact Micron package geometry comes from the already reviewed package evidence; the 0.30/0.40/0.30 NSMD footprint is an engineering candidate, not a manufacturer-qualified land pattern.
