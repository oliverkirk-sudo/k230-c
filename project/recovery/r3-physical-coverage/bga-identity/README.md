# Recovered BGA identity recheck

**Result: all 743 ball identities agree; manufacturing footprints and a six-layer escape remain unqualified.** This read-only check of restored v12-r2_1 passed 30 consistency checks on 2026-10-03. No main CAD was changed, and no vendor PDF or screenshot is included.

The complete check results and SHA-256 input inventory are in [bga-identity-recheck.json](bga-identity-recheck.json). [audit_bga_identity.py](audit_bga_identity.py) reproduces the checks with --project pointing to the verified restored v12+R2.1 project and writes only this directory.

## What is present and consistent

| Active part | Physical balls / full grid | Pitch X × Y | Exact source map and nominal centers | Active footprint binding |
|---|---:|---:|---|---|
| U1 Canaan K230 | 390 / 400 | 0.65 × 0.65 mm | Present; all labels and coordinates agree | Empty |
| U2 Micron MT53E256M32D2FW-046 AAT:B | 200 / 264 | 0.80 × 0.65 mm | Present; independent grid/mechanical evidence agrees | Empty |
| U3 Micron MTFC16GAPALBH-AAT | 153 / 196 | 0.50 × 0.50 mm | Present; physical occupancy and nominal centers agree | Empty |

Each source map matches the active master XML, native symbol library and pin-assignment CSV exactly. The functional analysis CSV agrees on all 743 labels and nominal coordinates. Historical coupon net names also match the active U1/U3 net assignments.

Coordinates use package-centered component top view, balls down, X right and Y down. K230 A1 is absent. FW200 retains its empty rows L/M and columns 6/7. BH153 retains the 153 solder-ball sites; its 56 additional package test contacts do not become PCB solder lands. NC/RFU/DNU/VSF balls remain distinct from absent sites.

The full K230 map is `data/k230-source-extraction/k230-390-balls.csv`; the older `engineering/k230-reference-balls.csv` is only a 163-pin reference subset. Micron maps are the two `engineering/high-temp-candidates/micron-*-ball-comparison.json` files, corroborated by the recovered package evidence.

## Conditional geometry, not production land patterns

Two standalone editable engineering footprints exist and agree with their source ball numbering and center coordinates:

| Footprint | Copper / mask / paste diameter | Verified pads |
|---|---:|---:|
| K230_390_NSMD027_ENGINEERING_ONLY | 0.27 / 0.37 / 0.27 mm | 390 |
| MTFC16GAPALBH_AAT_BH153_NSMD030_ENGINEERING_ONLY | 0.30 / 0.40 / 0.30 mm | 153 |

Both are front-side SMD circles and explicitly unqualified. No standalone FW200 footprint was found. Its 200 source coordinates and analytical land trials are present, including a separate 0.30 mm copper sensitivity in the historical two-package link study. This is enough to preserve a conditional candidate, not to bind it as qualified geometry.

The package-side SMD-pad/ball notes do not specify PCB copper, mask or paste. The older Samsung mechanical audit must not supply Micron body, height or ball dimensions. Exact-part land construction, mask registration, stencil, via filling/capping, drill/annulus tolerances and assembly reliability remain process gates.

One documentation discrepancy: the BH153 README says its standalone footprint carries pin functions, but the actual `.kicad_mod` contains numbered pads without `pinfunction` fields. The native coupon and source maps contain those functions. Pad identity and geometry are consistent.

## Historical routing boundary

Both native coupons have **eight copper layers**. The K230 coupon has 390 lands, 327 vias and 997 segments; the BH153 coupon has 153 lands, 29 vias and 16 segments. They are isolated local studies, not the required six-layer module. Their old DRC and analytical pass statements do not establish full-board connectivity, DDR timing, reference continuity, PDN or assembly approval.

The constraints remain **38 × 38 mm, 140 contacts, exactly six copper layers and top-only assembly**. A six-layer stack/process and complete escape must be evaluated explicitly before placement/routing can be accepted. Nothing in this audit imports or promotes historical geometry into the active design.

This pass checked restored engineering data and native file contents. It did not reread the original manufacturer documents, rerun routing/native DRC, or confirm current orderability. Historical source URLs/hashes remain provenance rather than new manufacturer verification.
