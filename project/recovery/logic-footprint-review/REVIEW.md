# Compact logic footprint recovery

2026-10-01. **One standalone TI DSF0006A source-example candidate is complete. Nexperia SOT1160-1 remains blocked for exact visual land review. Neither U14 nor U92 has been assigned a footprint in active CAD.**

The scope is a drawing transcription and isolated native CAD audit. It does not qualify assembly, placement/routing, a finished board, or the previously documented electrical and thermal gates.

## TI source and orientation

The exact [SN74LVC1G97 datasheet](https://www.ti.com/lit/ds/symlink/sn74lvc1g97.pdf) is retained at `/workspace/shared/k230-reference/sn74lvc1g97.pdf`, SHA-256 `53e8bc4d0f966f6e1d8d28987240f17a07e94bec6658ebc92ab322dccae7f416`. Datasheet SCES416N January 2017; appended DSF0006A drawing **4220597/B, 06/2022**, physical PDF pages 29-31. Those drawing pixels and the DSF top-view pin diagram on page 3 were independently inspected in this pass.

Component-side coordinates use the body center as origin, +X right and +Y down. Pin 1 is upper-left: left column 1/2/3, right column 6/5/4. The package underside drawing on page 29 must not be copied without mirroring. The component-side land and stencil examples on pages 30/31 confirm the chosen orientation.

| Pin | Function | X, Y mm | Frozen U14 net |
|---|---|---|---|
| 1 | In1 | -0.40, -0.35 | GLOBAL_DISABLE |
| 2 | GND | -0.40, 0 | GND |
| 3 | In0 | -0.40, +0.35 | VDD_3V3 |
| 4 | Y | +0.40, +0.35 | DISABLE_OR_TF |
| 5 | VCC | +0.40, 0 | VDD_3V3 |
| 6 | In2 | +0.40, -0.35 | MODE_TF |

The body is 0.95-1.05 mm square, midrange 1.00 mm; maximum height is 0.40 mm. The footprint has a chamfered fabrication outline and upper-left silk marker, a 1.05-mm maximum-body envelope on Dwgs.User, and a hidden HEIGHT_MAX_MM property. There is no invented exposed pad.

## Exact copper and separate apertures

The candidate is `cad/recovery-footprint-candidates/CMK230_Recovery_Logic_Candidates.pretty/TI_DSF0006A_SN74LVC1G97_1x1_P0.35_SourceExample_CANDIDATE.kicad_mod`.

| Layer | Count | Aperture per pad | Corner radius | Basis |
|---|---|---|---|---|
| F.Cu | 6 numbered electrical pads | 0.60 x 0.17 mm | 0.05 mm | TI board example |
| F.Paste | 6 unnumbered, non-copper apertures | 0.60 x 0.15 mm | 0.05 mm | TI stencil example |
| F.Mask | 6 unnumbered, non-copper openings | 0.70 x 0.27 mm | 0.10 mm | Project-selected +0.05 mm true offset |

All centers are identical on these three layers. Paste retains the 0.60-mm length: a uniform 0.01-mm shrink on every side would incorrectly shorten it to 0.58 mm. Local mask/paste margins and paste ratios are explicitly zero on the already-sized apertures. Native SVG and Gerber outputs preserve all three layers under deliberately nonzero board and footprint-wide margin/ratio settings. The actual copper/paste Gerber macros and six flash coordinates are independently checked against the source dimensions and radii. With the native 0.075-mm mask-web setup, mask Gerbers contain six separate polygons: their bounds, centers and all rounded-corner vertices are checked against the exact-radius source shape within 0.000002 mm output quantization. Native mask tessellation has a maximum 0.001922-mm arc chord inset; it is not a new pad-radius choice.

TI's NSMD opening note allows **at most 0.07 mm expansion**; it does not require that maximum. The selected 0.05-mm offset leaves **0.08 mm nominal same-column mask web** and 0.10 mm opposing-column opening separation. The 0.18-mm nearest copper clearance follows directly from 0.35-mm pitch minus 0.17-mm land width.

| Per-side mask expansion | Nominal minimum web | Status |
|---|---|---|
| 0.03 mm | 0.12 mm | Unbuilt conditional option |
| 0.04 mm | 0.10 mm | Unbuilt conditional option |
| 0.05 mm | 0.08 mm | Selected candidate |
| 0.06 mm | 0.06 mm | Unbuilt conditional option |
| 0.07 mm | 0.04 mm | Drawing maximum, not mandatory |

These are nominal geometry calculations, not mask registration, finished-web, pad exposure or factory capability acceptance. Decreasing expansion improves the nominal dam while reducing registration allowance. Do not choose a smaller opening without the selected factory's process and registration budget.

TI's **0.09-mm stencil is an example**, not an approved production process. Rounded aperture area is 0.087854 mm2; rounded copper land area is 0.099854 mm2; area coverage is 87.9825%. The simple vertical-wall aperture area/wall-area ratio is 0.690273 and minimum aperture width/thickness is 1.6667. Neither ratio establishes release or deposited volume. Stencil wall taper/coating, dimensional tolerance, paste, reflow, placement, inspection and rework remain open.

The **2.00 x 1.60 mm courtyard is a project choice**, not a TI drawing dimension. Its centerline is at least 0.25 mm beyond the applicable maximum-body/mask envelope, rounded outward to the 0.05-mm grid. The 0.05-mm courtyard stroke makes the closest inner stroke edge 0.225 mm from the mask. Reference text is 0.80 mm high to satisfy the native DRC text constraint.

## Validation and limits

The independent validator imports no builder/spec dimensions. It parses the persisted KiCad footprint and boards using KiCad 9.0.2, checks exact copper/mask/paste shapes and centers, pad numbering, layers, radii, body height, courtyard, and six U14 pin/net identities against the frozen electrical export.

- The unique-net intrinsic fixture has six distinct electrical nets, **0 native DRC violations and 0 unconnected items** at the provisional 0.15-mm clearance screen
- The separate actual-U14-net fixture has **0 native DRC violations and one expected unrouted connection**, VDD_3V3 between pins 3/5; this is a local source-bound fixture, not a routed system
- 0.181-mm and 0.20-mm copper-clearance challenges each produce four expected clearance findings, showing that the intrinsic 0.18-mm spacing is not hidden by net-zero or tied-pad suppression
- Six deliberately wrong geometries are rejected: underside mirroring, pins 1/6 swapped, uniform paste shrink, wrong copper radius, invented EP7 and a missing mask opening
- Independent native-geometry web checks accept 0.075/0.080-mm nominal limits and reject 0.081/0.10-mm limits against the actual 0.08-mm minimum; the native board mask-minimum settings are round-trip verified
- KiCad's native mask DRC fails to flag this explicit-mask-only construction under stricter web controls. **A clean DRC report cannot establish mask-web compliance.** Preserve the independent check and verify actual Gerber apertures in final CAM review
- Native SVG geometry, copper/paste Gerber macro/flash checks, and mask polygon checks pass for normal and deliberately conflicting global margin settings; persisted board/library geometry and the U14 electrical mapping match
- All 31 files in the frozen compact electrical branch remain byte-identical. Its master.xml SHA-256 remains `87e61363803398574579a628d9ed9235d0bc0903a1457c88b4b9b6054369bdbd`

See `validation.json`, native DRC/export logs and `freeze-manifest.json` for exact final artifact hashes. The unique-net fixture deliberately has no functional circuit; its empty native schematic-parity list is not a system schematic/PCB parity result. No thresholds here claim finished board process approval.

## Bounded area comparison

The previous drawing-backed standard-package review records 1.25 x 2.00 mm nominal body for SOT363-2, used by the frozen 74AUP1G97GW,125 alternatives. Those historic source originals are not revalidated in this pass; this is retained review evidence from `engineering/mechanical/nexperia-standard-footprint-spec.json`.

- U14 nominal body area falls from 2.50 to 1.00 mm2, a **1.50 mm2 / 60% body-area reduction**
- The prior two standard single gates total 5.00 mm2 nominal body; the official current SOT1160-1 page lists 1.40 x 1.80 mm, or 2.52 mm2, for the proposed dual. That is a 2.48 mm2 / 49.6% body-area reduction, conditional on the still-open exact footprint audit
- All three nominal bodies total 7.50 mm2 before and 3.52 mm2 after, a 3.98 mm2 / 53.07% reduction; this is **body area only**

For the built TI candidate, the copper bounding box is 1.40 x 0.87 mm, mask bounding box 1.50 x 0.97 mm, and project courtyard area 3.20 mm2. Actual copper area is 0.599124 mm2, distinct from its bounding box. No total courtyard-to-courtyard saving is claimed while the dual footprint remains unverified. These quantities do not establish placement, routing, local bypass, escape geometry, rework space, thermal behavior or complete-board fit.

## Nexperia exact visual gate

The [official SOT1160-1 page](https://www.nexperia.com/packages/SOT1160-1.html) was read this pass. It lists XQFN10, ten terminals, 0.4-mm pitch, 1.4 x 1.8 x 0.5-mm body and links the [manufacturer package-information PDF](https://assets.nexperia.com/documents/package-information/SOT1160-1.pdf), listed as 2022-06-07. The earlier review read web text but did not obtain inspectable drawing pixels; blocked download routes were not retried here. No further alternate-source search was made this pass.

**No SOT1160-1 footprint was generated.** Body size and pin count are insufficient to map the nonuniform corner lands, exact pin1 orientation, mask/paste shapes and registration. Prior text about 0.0625-mm mask expansion, 0.02-mm paste reduction and 0.10-mm stencil remains a lead for future visual verification, not geometry authority for a guessed pattern. Likewise, the reported 2.35 x 1.95-mm occupied envelope is not promoted to a verified CAD courtyard.

To close this gate, obtain a legitimate inspectable manufacturer-authored SOT1160-1 drawing, retain its bytes/hash and actual revision, visually reconcile complete outline/reflow pages and GU package pin1 orientation, transcribe every distinct copper land, mask and paste shape, then repeat native geometry/export/negative controls and process review. Keep U92's footprint field blank until that is complete.

## Inspect and reproduce

- Native layer gallery: `evidence/TI_DSF_native_layer_review.png` (with vector SVG beside it)
- Actual source pixels: `evidence/TI_DSF_page_29.png`, `TI_DSF_page_30.png`, `TI_DSF_page_31.png`, `TI_DSF_pin_map_page_3.png`
- Actual-net fixture: `cad/recovery-footprint-candidates/TI_DSF_U14_Pin_Parity_ONLY.kicad_pcb`
- Unique-net fixture: `cad/recovery-footprint-candidates/TI_DSF_Geometry_QA_ONLY.kicad_pcb`
- Run from project root: `/usr/bin/python3 recovery/logic-footprint-review/build_dsf_candidate.py`, then `audit_dsf_candidate.py`, then `render_review.py`

Keep the complete isolated candidate library and explicit mask/paste apertures together. Main CAD assignment, production CAM, supplier communication, uploads, purchases and manufacturing release were not performed.
