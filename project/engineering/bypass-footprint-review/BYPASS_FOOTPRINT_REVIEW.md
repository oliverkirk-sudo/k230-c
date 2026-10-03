# Samsung bypass footprint independent review

2026-09-30 UTC. Result: **source-land geometry checks pass for both conditional candidates; paste has an inherited-setting limitation**. No production CAD, generator or footprint library was edited. This review does not qualify capacitance, PDN, temperature, assembly yield, or module fit.

## Source and geometry

Independently read exact-part datasheet page 1 and MLCC manual physical page 33. Page 33's diagram defines **a = copper gap, b = individual pad length, c = pad width**. Its sizes are metric: select **0603 +/-0.03 mm** for CL03B104KP3NNWC (0201 inch), and **1608 +/-0.15 mm** for CL10B475KQ8NFQC (0603 inch). Confusing inch/metric designations would select the wrong row.

| Dimension, mm | CL03B104KP3NNWC | CL10B475KQ8NFQC |
|---|---:|---:|
| Source a range / selected midpoint | 0.22-0.28 / 0.25 | 0.65-0.75 / 0.70 |
| Source b range / selected midpoint | 0.31-0.37 / 0.34 | 0.73-0.83 / 0.78 |
| Source c range / selected midpoint | 0.30-0.36 / 0.33 | 0.90-1.00 / 0.95 |
| Actual pad centers X | +/-0.295 | +/-0.740 |
| Actual copper pad, length x width | 0.34 x 0.33 | 0.78 x 0.95 |
| Copper outer span a+2b | 0.93 | 2.26 |
| Explicit mask expansion per edge | 0.05 | 0.05 |
| Effective mask aperture bounding dimensions | 0.44 x 0.43 | 0.88 x 1.05 |
| Nominal internal mask web a-0.10 | 0.15 | 0.60 |
| Closed courtyard, centerline dimensions | 1.23 x 0.63 | 2.56 x 1.25 |
| F.Fab rectangle = source maximum body | 0.63 x 0.33 | 1.75 x 0.95 |
| Nominal 100 um stencil area ratio, with 1:1 paste | 0.837313 | 2.141618 |

All midpoint/range, pad number, SMD attribute, copper/mask/paste layer, position, size, symmetry, mask, body and closed-courtyard checks passed against the persisted files: **84 numeric assertions**, plus structural assertions. The courtyard calculation is max(copper span+0.30, maximum body length+0.20) by max(pad width+0.30, maximum body width+0.20). It has 0.10 mm from the nominal mask boundary to courtyard centerline; its 0.05 mm line makes the visible inner-stroke gap 0.075 mm. This is a declared dense courtyard choice, not a manufacturer courtyard or rework-spacing requirement.

The mask expansion, midpoint choice, dense courtyard and 100 um stencil are engineering choices. Samsung expressly calls for evaluation with the actual set and board. Formula correctness and source range membership do not establish factory copper/mask registration tolerance, solder-joint formation, stencil release, tombstoning or rework access. F.Fab uses maximum dimensions rather than nominal dimensions. Its default 1.27 mm reference text is oversized for these packages; C2 text overlaps the body outline in the untouched native rendering. That is a documentation presentation issue, not a copper/paste geometry failure.

## Paste limitation, verified independently

Each copper pad includes F.Paste, but **local paste absolute/ratio overrides are unset (native API returns None)**. There are no separate paste-only apertures. With the isolated project's zero board paste margin and ratio, native F.Paste equals copper 1:1, as intended. With only the in-memory board absolute paste margin changed to -0.02 mm, every pad's effective paste margin becomes (-0.02, -0.02) mm. Thus the apertures would become 0.30 x 0.29 mm and 0.74 x 0.91 mm respectively.

The generator's 1:1 statement is conditional on the consuming board/footprint settings. Either preserve and verify zero inherited paste settings in the final project or implement and independently verify explicit paste aperture geometry in a separately authorized edit. This review did not modify the library. The explicit +0.05 mm mask margin did resolve correctly in the baseline.

## Native trial and negative controls

KiCad **9.0.2** loaded the saved footprint files into an isolated 10 x 6 mm two-layer board. C1 and C2 sit well apart at (3,3) and (7,3) mm. Each of the four copper pads has its own distinct single-pad net, so inter-pad clearance checks are live without creating fake routing. There are no tracks, vias or functional schematic. The local project links the existing candidate library read-only.

| Native DRC trial | Clearance requirement | Result |
|---|---:|---|
| Bypass_Geometry_QA_ONLY | 0.20 mm | Exit 0: 0 violations, 0 unconnected items |
| Bypass_Negative_Clearance_026 | 0.26 mm | Exit 5: exactly 1 error, C1 actual gap 0.25 mm |
| Bypass_Negative_Clearance_071 | 0.71 mm | Exit 5: exactly 2 errors, C1 actual gap 0.25 mm and C2 actual gap 0.70 mm |

The baseline uses 0.25 mm copper-edge clearance, nominal 0.10 mm minimum mask web, no allowed footprint mask bridges, and enabled missing/malformed/overlapping courtyard errors. These are isolated QA settings, not a chosen PCB fabricator's capabilities. No DRC exclusions were added. The deliberate failures show that checking is active and the two actual pad gaps reach the native engine. Zero unconnected items follows from single-pad nets and does not demonstrate functional connectivity. Schematic parity and routed-board performance were not tested.

Native CLI exports of F.Cu, F.Mask, F.Paste, F.CrtYd and F.Fab were rasterized and visually inspected. Copper/paste pairs are symmetric, mask openings remain separate, courtyards are closed, and body outlines have the expected relative sizes. The native paste and copper silhouettes match under zero paste settings. The gallery preserves identical geometry/scale across layers; its titles are review annotations.

## Artifacts and reproducibility

- `audit_bypass_footprints.py`: independent source expectations, footprint load/check, isolated board creation, paste-inheritance experiment and three DRC runs
- `geometry-audit.json`: dimensions, source/footprint hashes and numerical results
- `native-drc-runs.json` and three `*-drc.json` reports: exact commands, exit codes and native results
- `native-svg-runs.json`, `evidence/native-*.svg`, `evidence/native-*.png`, `evidence/native-layer-gallery.png`: native plots and inspected rendering
- `evidence/samsung-land-page33.png`: inspected source diagram/table
- `cad/bypass-footprint-review/`: all three isolated native KiCad boards/projects and read-only library table

Source PDFs are in `k230-reference/mechanical/passive-review/`; source hashes are in the geometry record. The reviewed footprint SHA-256 values are CL03 **e2e0ab433ac92493e44b56ca4b8eb8c09719c5feef1d446e6da7252f528121e6** and CL10 **59decef44ea75e5c28e3f50992a7ab65a4e1b16060076b76efa08aa4efb56499**. Approval as a production footprint still needs the actual assembly and fabricator process plus electrical qualification; a geometry-pass label must remain conditional.
