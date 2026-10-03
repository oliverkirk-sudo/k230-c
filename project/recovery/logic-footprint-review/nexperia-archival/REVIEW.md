# SOT1160-1 archival-source footprint audit

2026-10-01. **The exact NXP SOT1160-1 land reconstruction is complete as an isolated, process-unqualified candidate.** Archival manufacturer-authored drawing pixels close the previous coordinate/orientation gap; current Nexperia web text corroborates the drawing identifiers and annotated dimensions. Current PDF byte or revision identity is not claimed. U14/U92 assignments in active CAD remain blank; all previously frozen TI deliverables are preserved.

## Evidence and provenance

- [NXP reflow drawing, archived document page](https://www.datasheetarchive.com/datasheet/SOT1160-1/NXP-Semiconductors?term=sot116&version=1): `sot1160-1_fr`, copyright 2010 NXP, no explicit issue date printed. PDF SHA-256 `3aba5537e19187d51c9c8494937482a1e8f376b4a8ee977cc2be10288faa9e91`, 216108 bytes
- [NXP outline drawing, archived document page](https://www.datasheetarchive.com/datasheet/SOT1160-1/NXP-Semiconductors?term=sot116&version=3): `sot1160-1_po`, effective issue **2009-12-29**, preceding 2009-12-28 visibly struck through. PDF SHA-256 `1cf1d5a02ef2ac5086c67892f8e00020de084d5d2cfe602539a228cd0722e692`, 222134 bytes
- [Current manufacturer package page](https://www.nexperia.com/packages/SOT1160-1.html) links the [2022-06-07 package information](https://assets.nexperia.com/documents/package-information/SOT1160-1.pdf). Historical independent review of current primary web text matches identifiers `sot1160-1_fr` / `sot1160-1_po`, outline dates, and all reflow annotations used here: 1.95, 1.7 CU, 1.25, 0.45, 0.4 (6x), 0.22 CU (10x), 0.85, 1 CU, 2.1 CU, 2.35, 0.5 CU, 0.6 CU, mask +0.0625, paste -0.02 and stencil 0.1

Both archival page images were independently inspected in this footprint audit. These are legitimate manufacturer-authored archived drawings obtained through separately accessible public archive pages; the blocked current manufacturer download was not retried. Local originals, raw source-page images, and provenance download records remain outside the deliverable directories under `/workspace/shared/k230-reference`. `source-acceptance.json` records their paths/hashes and the exact limit of the current-text cross-check. Copyright year is not treated as a drawing revision date.

This report supersedes the earlier unavailable-drawing status for an **archival-source reconstruction**. Release still requires acceptance of the intended orderable/package revision and the factory process.

## Pin orientation and mechanical limits

The outline's terminal-side view places 3/4/5 at top, 10/9/8 at bottom, 2 above long 1 at left, and 6 above 7 at right. Reflecting vertically gives the component-side reflow orientation: **top 10/9/8; left long 1 above 2; right 7 above 6; bottom 3/4/5**. The top-side index area is upper-left. Copying the terminal-side view directly would be wrong.

Origin is body center; +X right and +Y down. Body D/E dimensions are nominal **1.40 x 1.80 mm**, minimum 1.30 x 1.70 and maximum **1.50 x 1.90 mm**; maximum height 0.50 mm. The source explicitly excludes plastic/metal protrusions up to **0.075 mm per side**. The total envelope is therefore **1.65 x 2.05 mm**, recorded separately on Cmts.User; Dwgs.User shows the unexpanded maximum body. Courtyard construction accounts for both.

## Exact asymmetric copper and separate apertures

The native footprint is in `cad/recovery-footprint-candidates/nexperia-archival/CMK230_NXP_Archival_Candidates.pretty`. All pads are rectangular; no undocumented corner radius or exposed pad is added. Copper geometry follows the actual dimension arrows and visible land arrangement:

| Pin | Function | X, Y mm | Copper W x H mm | Frozen U92 net |
|---|---|---|---|---|
| 1 | 1B | -0.525, -0.20 | 0.65 x 0.22 | GND |
| 2 | 1C | -0.575, +0.20 | 0.55 x 0.22 | BOOT_VOLTAGE_QUALIFIED_1V8 |
| 3 | 2Y | -0.40, +0.775 | 0.22 x 0.55 | RESET_RELEASE_REQUEST_1V8 |
| 4 | GND | 0, +0.775 | 0.22 x 0.55 | GND |
| 5 | 2A | +0.40, +0.775 | 0.22 x 0.55 | FIXED_RAILS_PGOOD_3V3 |
| 6 | 2B | +0.575, +0.20 | 0.55 x 0.22 | GND |
| 7 | 2C | +0.575, -0.20 | 0.55 x 0.22 | RSTN |
| 8 | 1Y | +0.40, -0.775 | 0.22 x 0.55 | STORAGE_ENABLE_1V8 |
| 9 | VCC | 0, -0.775 | 0.22 x 0.55 | VDD1P8 |
| 10 | 1A | -0.40, -0.775 | 0.22 x 0.55 | FIXED_RAILS_PGOOD_3V3 |

The 1.70 x 2.10-mm copper envelope and 1.00-mm top/bottom inner gap give top/bottom land length (2.10-1.00)/2 = 0.55 mm. The ordinary side inner gap is 0.60 mm, giving (1.70-0.60)/2 = 0.55 mm. At the upper pair, the gap narrows to 0.50 mm because the visible left land extends 0.10 mm farther inward; its length is 0.65 mm and its center shifts to -0.525 mm. The right land stays 0.55 mm. Neither center symmetry nor making all ten lands identical reproduces this drawing.

There are **10 numbered copper-only pads, 10 explicit unnumbered mask-only openings, and 10 explicit unnumbered paste-only apertures**, with zero local margins/ratios on the already-sized apertures:

| Land class | Copper mm | Mask opening mm | Paste aperture mm |
|---|---|---|---|
| Pin 1 | 0.65 x 0.22 | 0.775 x 0.345 | 0.61 x 0.18 |
| Other horizontal | 0.55 x 0.22 | 0.675 x 0.345 | 0.51 x 0.18 |
| Vertical | 0.22 x 0.55 | 0.345 x 0.675 | 0.18 x 0.51 |

These follow source mask **+0.0625 mm per side** and paste **-0.02 mm per side**. The source's **0.10-mm stencil is an example**, not factory acceptance. Nominal aperture area/wall-area ratio is 0.69494 for pin 1 and 0.66522 for the other lands; geometric paste/copper coverage is 76.7832% and 75.8678%. These quantities do not establish paste release, deposited volume, registration, yield or rework suitability.

**Physical bypass pins matter:** U92's actual supply/return are **VCC9/GND4**. Grounded configuration inputs 1 and 6 are not substitutes for the package return. For TI U14, the actual pair is **VCC5/GND2**; pin 3 is a tied-high input. Future bypass affinity and power-return review must follow these physical pins, not the nearest pad sharing a net name.

## Native checks and the mask-export trap

The independent validator imports no builder dimensions. **1,577 numeric assertions pass**, plus source coordinate/radius-shape/layer checks, saved-board/library parity, exact frozen U92 pin/net mapping, and six invalid-geometry rejection controls: wrong terminal-side mirror, lost long-pin1 asymmetry, swapped pins 1/2, missing front-mask opening, 1:1 paste, and invented EP11.

- Minimum copper gap is **0.18 mm**; minimum nominal mask web is **0.055 mm**; minimum paste gap is **0.22 mm**
- Unique-net intrinsic fixture: **0 DRC violations / 0 unconnected items**, with provisional 0.15-mm copper clearance and 0.05-mm native mask-web setting
- Actual-U92-net fixture: **0 geometry violations and three expected unrouted connections**: two GND ties and one FIXED_RAILS_PGOOD_3V3 tie. It is a local footprint fixture, not a routed board or full schematic/PCB parity proof
- 0.181-mm copper-clearance control reports six expected findings; the 0.20-mm control reports ten
- Independent native-geometry checks accept 0.050/0.055-mm nominal web requirements and reject 0.056/0.075 mm; all native mask settings are saved and round-trip verified
- Base and deliberately conflicting global margin/ratio exports preserve every copper/mask/paste center and rectangle dimension at the 0.05-mm mask-web setting. The actual native Gerber flashes/regions are checked, not only the screen rendering

**Global minimum mask width can change the delivered CAM geometry even with explicit mask pads.** The same footprint produces:

| Native minimum mask-web setting | Actual F.Mask Gerber | Source-aperture check |
|---|---|---|
| 0.050 mm | Ten separate exact rectangular openings | Pass |
| 0.075 mm | One complex merged region | Rejected |

Native mask DRC reports no bridge for either setting. The 0.075-mm output is a deliberately rejected **merged-mask diagnostic control**, not the source-exact release. It is retained only to make this failure visible and reproducible. Do not publish that CAM file as approved production data. No gang-mask acceptance, reduced-expansion alternative, or factory waiver is granted by this audit.

The selected source-exact candidate's 55-micron nominal web remains a factory gate. A factory requiring a larger finished web cannot be satisfied by merely changing KiCad's minimum-web setting. Registration, finished mask/land dimensions, stencil, assembly and actual CAM must be resolved explicitly. Native DRC alone is insufficient.

## Area and release bounds

NXP copper bounding area is 1.70 x 2.10 = **3.57 mm2**, actual copper area **1.232 mm2**, and mask bounding box **1.825 x 2.225 mm**. The drawing's clearance/placement bounding dimensions are **1.95 x 2.35 mm** (4.5825 mm2). These are different quantities.

The **2.50 x 2.90-mm project courtyard** (7.25 mm2) is a conservative project choice at least 0.25 mm beyond the source clearance/placement envelope to its centerline, rounded outward on a 0.05-mm grid. Its 0.05-mm stroke is included in the documented margin interpretation; it is not a manufacturer land dimension. The 1.65 x 2.05-mm body-plus-protrusion envelope fits within that basis.

Compared with the retained prior standard-package review, two nominal 1.25 x 2.00-mm bodies total 5.00 mm2; the dual nominal body is 2.52 mm2, a **49.6% body-area reduction**. Across U14 plus the dual, nominal body area falls from 7.50 to 3.52 mm2 (**53.07%**). TI and NXP project courtyards total 3.20 + 7.25 = **10.45 mm2**; the retained three-standard-part courtyard total was 31.62 mm2. This is a comparison of declared project envelopes with different package sources/process choices, not recovered usable board area. It proves no board placement, routing, local bypass, thermal, rework or complete-board fit.

No active schematic, PCB, BOM order, supplier communication, upload or production release was performed. All 61 frozen TI deliverables and 31 frozen electrical files remain byte-identical. Previously documented electrical, startup, full-rail, thermal and bench-validation gates remain open.

## Review artifacts and reproduction

- `evidence/NXP_native_layer_review.png`: generated labeled review of actual native layer plots
- `evidence/NXP_mask_export_control.png`: actual native Gerber output at 0.05 versus 0.075-mm mask settings
- `validation.json`, `native-drc-runs.json`, `native-export-runs.json`: exact test outcomes and commands
- `source-acceptance.json`: archive provenance, original hashes and current-text cross-check boundaries
- `freeze-manifest.json`: final candidate, fixture, report and render hashes; raw vendor pages excluded
- `integration-contract.json`: physical supply/return affinity and pending integration/process gates

From the project root run `/usr/bin/python3 recovery/logic-footprint-review/nexperia-archival/build_candidate.py`, then `audit_candidate.py`, then `render_review.py` in that directory. The build refuses to proceed if source evidence acceptance is absent or if the frozen TI/electrical snapshot no longer matches. Coordinate/geometry validation and source-acceptance metadata must accompany any later integration.
