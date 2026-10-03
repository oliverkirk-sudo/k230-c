# R8 independent audit

**PASS for this bounded footprint-assignment stage. No concrete implementation defect found.** This is not production, thermal, filter, loop-stability, sequence or complete-board routing approval.

The baseline is the exact published R7 project. R8 has exactly thirteen new assignments: FB202–FB210 use the explicitly conditional Murata BLM15PX121 18 µm variant; C202/C219/C224/C229 use the KEMET 0402 density-B candidate. All 254 component identities outside the footprint field, 1,509 pin bindings, 457 named nets and all population/BOM flags are unchanged. JP1/R45/R47/R528 remain DNP. Every active schematic is byte-identical after removing the thirteen new footprint strings and normalizing the root revision label. Coverage is **215 assigned, 39 gaps**. A fresh native netlist matches the saved R8 netlist; fresh ERC reports zero violations.

## Independent geometry and CAM evidence

KiCad 9.0.2 loaded all four library variants. Their embedded fixture pads match the libraries, survive native save/reload unchanged and produce the same aperture shapes, dimensions, reference identities and flash coordinates as the lead's saved CAM. This verifies actual output geometry, beyond counting flashes.

- Murata pad centers are x=±0.4 mm. Copper sizes are 0.4 × 1.2, 0.4 × 0.7 and 0.4 × 0.5 mm for the 18/35/70 µm variants. Mask openings and paste apertures remain 0.4 × 0.5 mm for all three. Thus 18/35 µm copper shoulders remain masked and receive no paste
- KEMET density-B copper is 0.62 × 0.62 mm at x=±0.45 mm, with the 1.90 × 1.00 mm source courtyard. The implemented +0.05 mm mask assumption exports as 0.72 × 0.72 mm rounded openings with 0.05 mm corner radius; paste is 1:1 to copper
- All geometry is on top. The diagnostic fixture has six copper layers and fresh DRC reports zero violations. It is a spaced 20 × 13 mm geometry test, not the 38 × 38 mm core layout. Its separate one-pad diagnostic nets deliberately imply no required routes; zero unconnected items does not establish routing completeness

The Murata page-9 drawing and KEMET page-12 density-B table were independently viewed. Exact primary-source hashes and URLs are recorded in `source-checks.json`; originals and screenshots are not included. KEMET C=0.45 mm is half the pad pitch, not full pitch. Its copper/courtyard source contract is included in the project's `feedforward-review` directory. Manufacturer mask/paste process approval is not inferred from that contract.

## Negative controls

Eight rejection checks passed. Wrong 18 µm copper width, exposed copper shoulders and paste on the shoulders were each applied to real native board copies, saved/reloaded, exported to Gerber, and rejected independently at both saved-geometry and CAM levels. A KEMET half-pitch interpretation error was rejected. A separate physical negative placed different-net pads at 0.05 mm edge spacing against the 0.20 mm rule: native DRC reported two clearance errors and one courtyard overlap. None of these mutations touched the main CAD.

## Conditions retained

The Murata mask openings are exact nominal dimensions with **zero registration allowance**. The 18 µm assignment is a conservative conditional local reservation, not an approved six-layer stack. Local rectangles do not establish the continuing copper cross-section or heat-removal path. Actual currents and inrush, hot DCR, bias-dependent impedance, filtering/resonance, effective capacitance, sequence and local temperature remain unresolved. FB206 still requires its R401/pad load in addition to the PMU table subtotal. KEMET mask/paste/stencil and ±5% Cff applicability remain process/loop conditions.

The older ferrite source-stage `build_review.py` is historical acquisition provenance and should be omitted from the public subset. The runner below is the portable R8 audit entry point. Source-review statements that footprints were unassigned describe their hash-identified pre-R8 snapshot.

## Reproduce

Use a Python interpreter with KiCad's `pcbnew` module:

```text
python3 audit_r8.py --project /path/to/r8/project --baseline /path/to/published/r7/project --output /path/to/audit-output --runtime /path/to/separate-runtime
```

All four paths are required. The runner writes only to output/runtime, retains self-contained copies of the four original project footprints for saved-board DRC, and verifies input hashes afterward. Generated reports use PROJECT_ROOT, BASELINE_ROOT, OUTPUT_ROOT and RUNTIME_ROOT logical prefixes. Native fixtures and deliberately broken negative fixtures are diagnostic artifacts, not fabrication data.

`identity-check.json`, `saved-geometry-and-cam.json`, `negative-controls.json`, `input-integrity.json` and `native-command-log.json` contain the evidence. `artifact-sha256.json` hashes the delivered files. Input checks establish that the reviewed main CAD and libraries were unchanged by the audit.
