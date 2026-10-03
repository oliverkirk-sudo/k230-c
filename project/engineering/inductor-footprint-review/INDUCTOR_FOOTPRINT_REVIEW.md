# Murata inductor footprint independent review

2026-09-30 UTC. **Both footprints pass as conditional source-land geometry candidates.** This is not production, hot-current/loss, thermal, assembly or module-fit approval. The two source PDFs, persisted footprints, independent native boards and native plots were examined. No main CAD, source library or parent's generator was edited.

## Sources and exact geometry

Sources: DFE201612E specification **J(E)TE243A-0006D-01**, and DFE201610E specification **J(E)TE243A-0001E-01**. Source hashes agree with `cad/verified-footprints/inductor-candidates/source-land-validation.json`:

- DFE201612E: `6fbbdccedc9f58904a3e60d7e9c0e33917a03b7dd0d96716821988e89e4fb8ad`
- DFE201610E: `5c02415289b2b9d2c0ceb283cfe004a986d9e729dadbfe92917a381db5eae84e`

Page 5 of each source shows a 2.4 mm overall copper span, 0.8 mm inner gap and 1.8 mm pad height. Equal terminal lands therefore each have width (2.4-0.8)/2 = **0.8 mm**, centered at X = **+/-0.8 mm**. Native loaded footprints match exactly. Page 1 specifies nominal 2.0 +/-0.2 by 1.6 +/-0.2 mm bodies: the drawn 2.2 x 1.8 mm maximum-body envelopes are correct. Maximum heights are respectively 1.2 and 1.0 mm. These sources show no body marking; this review does not infer winding-start polarity from the assigned left/right pad numbers.

| Persisted footprint property | Both candidates |
|---|---|
| Numbered electrical pads | Exactly 2, numbers 1 and 2, SMD rectangular, F.Cu + F.Mask only |
| Copper pads | 0.8 x 1.8 mm, centers (-0.8,0) and (+0.8,0) mm |
| Paste apertures | Exactly 2 additional unnumbered pads; F.Paste only; no copper layer; 0.8 x 1.8 mm at the same centers |
| Mask | Explicit +0.05 mm per edge; aperture bounding dimensions 0.9 x 1.9 mm; nominal internal web 0.7 mm |
| Courtyard | Closed 3.0 x 2.4 mm rectangle; 0.05 mm line |
| Courtyard margin | 0.25 mm from nominal mask boundary to line center; 0.225 mm to visible inner line edge |
| Maximum body / restriction marker | Closed 2.2 x 1.8 mm rectangles on F.Fab / Dwgs.User |
| Embedded rule areas | None |

The copper lands are source-derived. Mask expansion, 1:1 paste and courtyard margin are declared process candidates, not manufacturer-prescribed assembly tolerances. This review passed **92 independent numeric assertions**, plus structural, layer, pad-number and hash checks. The check script uses independently transcribed dimensions; it does not import or execute the footprint generator.

## Paste behavior under a nonzero board setting

Baseline board paste settings are zero. A separate native control board changes the absolute board paste margin to **-0.02 mm** and its ratio to **-0.10 (-10%)**. The explicit non-copper paste-only pads retain effective (0,0) margin in the KiCad API, while the numbered copper pads are excluded from F.Paste.

The saved control contains both nonzero settings. Native CLI F.Paste exports were compared geometrically against the baseline: **all native geometry elements are identical**, and all four apertures remain 0.8 x 1.8 mm. This verifies that the explicit-aperture implementation avoids the inherited copper-pad paste scaling identified in the Samsung review. It does not establish that 1:1 is the optimal stencil design or that any stencil thickness is qualified.

## Native DRC and source restriction control

KiCad **9.0.2**; isolated 14 x 8 mm two-layer board; L1 and L2 are separated at (4,4) and (10,4) mm. Each electrical pad has a distinct single-pad net, so intra-footprint clearance checks are active. Baseline clearance is 0.20 mm, copper-edge clearance 0.25 mm, nominal minimum mask web 0.10 mm, and courtyard error checks enabled. No exclusions were added. The native library table references the existing candidate library read-only.

| Board/control | Native result | Interpretation |
|---|---|---|
| Murata_Geometry_QA_ONLY | Exit 0; 0 violations, 0 unconnected items | Conditional geometry passes the declared trial rules |
| Murata_Negative_Clearance_081 | Exit 5; exactly 2 clearance errors | Both footprints report actual 0.8000 mm against required 0.8100 mm; negative control works |
| Murata_Paste_Override_Control | Exit 0; 0 violations, 0 unconnected items | Nonzero inherited paste settings do not alter the explicit apertures |
| Murata_Undercoil_Unenforced_Control | Exit 0; 0 violations, 0 unconnected items | Deliberately source-invalid unrelated B.Cu loop below L1 is not caught by the marker |

**Under-coil restriction is NOT enforced.** Page 7 of both sources prohibits through-holes and copper patterns beneath the coil, with an exception for copper connected to its electrodes; it also requires other components not to touch the product. The source gives no explicit layer exemption. Conservatively retaining the full maximum-body restriction until manufacturer clarification is appropriate.

The footprint description correctly says the restriction is not automatically enforced, and its corresponding rectangle exists only on **Dwgs.User**. That layer has no keepout semantics. In the deliberate control, an unrelated closed 0.10 mm B.Cu track loop crosses beneath the full-width body region of L1 and native DRC still reports zero. The closed loop prevents irrelevant dangling-end warnings from obscuring this test. **This board is a negative demonstration, never a permitted placement example.** No embedded rule area or external `.kicad_dru` constraint implements the under-coil prohibition. Before routing/release, enforce it through reviewed geometry/net-aware rules or an explicit placement/copper audit covering the relevant layers and holes; a green ordinary DRC report alone cannot verify it.

Native F.Cu, F.Mask, F.Paste, outlines and the deliberate B.Cu control were exported, rasterized and visually inspected. Pad pairs and mask windows are symmetric and separate; baseline/override paste panels match; body/courtyard outlines are closed. The gallery shows the deliberate unrelated copper crossing below the annotation, illustrating the unenforced condition.

## Disposition and limits

Suitable to continue as **conditional source-land candidates** for DFE201612E-R24M=P2 and DFE201610E-R47M=P2, provided the source restriction and process assumptions remain explicit. No assignment to a main schematic/PCB was performed by this audit. No fabrication output was released.

This check does not establish inductance under bias, saturation current, hot DCR, AC/DC loss, regulator stability, temperature rise, capacitor/PDN interaction, solder-process yield, nearby-part clearance under assembly tolerances, or top-only 38 x 38 mm fit. Source page 7 specifically requires temperature-rise confirmation in the actual end product. The provisional 85 C enclosed-air screen is not proof of inductor component temperature. Single-pad trial nets and zero unconnected items do not demonstrate a routed circuit.

## Artifacts

- `audit_inductor_footprints.py`, `geometry-audit.json`: independent expectations, native checks, source/footprint hashes and paste behavior
- `native-drc-runs.json`, four `*-drc.json` reports: commands, exit codes and native findings
- `paste-native-svg-comparison.json`, `native-svg-runs.json`: exact native plot comparison and export commands
- `evidence/`: source pages 1/5/7, native SVGs/PNGs and inspected `native-layer-gallery.png`
- `cad/inductor-footprint-review/`: baseline and three native control boards/projects, plus a read-only source library table
