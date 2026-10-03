# Compact-inductor mechanical reservation review

Status: mechanical candidate only, not electrically selected or approved for manufacture. Scope is L24/L25/L26. No integrated CAD, BOM, netlist, or baseline-area file has been changed.

Latest-status note: the area scenarios below are frozen historical comparisons. The subsequent Schmitt-AND correction removes U96 and changes the optional monitor topology; no total below describes the latest consolidated BOM. Per-inductor mechanical dimensions and candidate reservation deltas remain applicable.

## Result

Murata DFE201610E-R47M=P2 permits a substantially smaller *candidate reservation*. A provisional 0.25 mm clearance around the union of maximum body and recommended lands produces 2.9 x 2.3 mm = 6.67 mm² per inductor. Replacing the existing 21.16 mm² reservation for each of L24/L25/L26 would save 14.49 mm² each, 43.47 mm² total.

Applied only to the frozen area-screen snapshot cited below, the dense full-BOM area sum would be 1175.03 mm², still 19.03 mm² above its provisional 1156 mm² inner region. This is not the latest full-design total: the parent reports that a fifth AUP U96 has since been added and other packages are under review. This alternative alone does not clear the optimistic area screen. Even an area sum below the region would not establish packing, BGA escape, routing, decoupling, thermal, EMI, or single-side assembly feasibility.

## Official drawing reviewed

- [Murata reference specification](https://pim.murata.com/asset/pim4/inductor/J(E)TE243A-0001_PDF_INDUCTOR), document J(E)TE243A-0001E-01, 10 pages. The legacy official URL redirects here. Exact DFE201610E-R47M=P2 row is on page 2. Source is marked Reference Only; its ordering note requires confirmation of product specifications before ordering.
- Page 1 physical drawing: body length 2.0 +/- 0.2 mm; width 1.6 +/- 0.2 mm; height 1.0 mm maximum. Maximum XY body is 2.2 x 1.8 mm. End-terminal depth callout is 0.5 +/- 0.3 mm along the length; opposed end terminals are shown. The document does not furnish an additional terminal thickness or coplanarity tolerance in this view.
- Page 5 recommended PCB pattern: outer span 2.4 mm, width 1.8 mm, gap between the two equal rectangular pads 0.8 mm. Therefore pad length is (2.4 - 0.8)/2 = 0.8 mm and pad-center pitch is 1.6 mm. Centering the drawing gives centers (-0.8, 0) and (+0.8, 0) mm for 0.8 x 1.8 mm pads. These are a mechanical interpretation, not an issued fabrication footprint.
- Body and PCB-pattern drawings were visually reviewed from the downloaded PDF, rather than inferred from nominal case code or PDF text. Pages 1, 5, and 7 were rendered and inspected. Page 1 had also been inspected in dot's cloud browser.
- [TI TPS62827 family datasheet](https://www.ti.com/lit/ds/symlink/tps62827.pdf), SLVSEF9I, March 2024 revision, page 13 Table 8-5, names DFE201610E-R47M and nominal 2.0 x 1.6 x 1.0 mm dimensions. This is candidate provenance, not rail qualification or a source for package tolerances. The supplied local TI page was visually reviewed.

## Courtyard assumptions and area sensitivity

The manufacturer does not define a courtyard in the reviewed source. Start with the bounding union of maximum physical body (2.2 x 1.8 mm) and recommended lands (2.4 x 1.8 mm): 2.4 x 1.8 mm. Add the stated margin on every side. No board-routing corridor or thermal-spreading area is included.

| Assumed clearance per side | Candidate reservation | Each | Three | Savings vs existing three | Dense full-BOM sum | Excess over provisional inner area |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 0.25 mm | 2.90 x 2.30 mm | 6.67 mm² | 20.01 mm² | 43.47 mm² | 1175.03 mm² | 19.03 mm² |
| 0.30 mm | 3.00 x 2.40 mm | 7.20 mm² | 21.60 mm² | 41.88 mm² | 1176.62 mm² | 20.62 mm² |
| 0.50 mm | 3.40 x 2.80 mm | 9.52 mm² | 28.56 mm² | 34.92 mm² | 1183.58 mm² | 27.58 mm² |

Existing area basis is full-bom-area-screen.json: three 21.16 mm² reservations = 63.48 mm², dense sum 1218.50 mm². Values remain unselected reservations. The primary scenario leaves 19.03 mm² of *excess*, not spare area. The 0402-passive sum becomes 1312.81 mm² in the same primary scenario, 156.81 mm² above the provisional inner region. The region assumes a 2 mm perimeter band inside 38 x 38 mm; it is not recovered original mechanical geometry.

### Separate hypothetical solder-mask sensitivity

If a later board process chooses +0.05 mm mask expansion at every copper-land edge and 0.25 mm assembly clearance outside the resulting mask envelope, the hypothetical 2.5 x 1.9 mm mask span leads to a 3.0 x 2.4 mm = 7.20 mm² reservation. Savings would be 13.96 mm² per instance or 41.88 mm² for three. This is a separately labeled sensitivity case. It happens to equal the second table row, whose 0.30 mm margin was applied directly to the body/land union. No final mask geometry is chosen or claimed; the manufacturer source supplies none.

## Layout conditions and unresolved details

- Murata page 7 prohibits through holes and copper below the coil except copper to its electrodes. The source does not specify a layer exemption; do not assume inner copper or vias are permitted without clarification. A land-pattern-only area calculation does not remove this layout constraint.
- Murata page 7 also requires that neighboring components not contact this product. The selected clearance is an explicit screening assumption and needs assembly/rework approval.
- No manufacturer courtyard, paste/stencil dimensions, solder-mask expansion, land dimensional tolerance, or placement tolerance is supplied in the reviewed pattern. These remain open.
- This review makes no electrical selection. In particular, TI's 4.8 A table entry must not be read as continuous-current approval: Murata page 2 separately lists 4.8 A at its inductance-change criterion and 3.6 A at its temperature-rise criterion. Actual rail peak/RMS current, loss, temperature, saturation, stability/transients and qualification require separate analysis.
- Final supply status, ordering specification and application qualification are outside this mechanical review.

## Evidence and reproduction

The source PDF and rendered manufacturer pages are kept outside the distributable design tree in the shared reference directory. Their precise paths and source hash are in compact-inductor-mechanical-review.json. PDF SHA-256: 5c02415289b2b9d2c0ceb283cfe004a986d9e729dadbfe92917a381db5eae84e.

Arithmetic is recomputed from the existing area-screen JSON using exact decimal values. Only the three specified inductor reservations change in the hypothetical sums; all other assumptions remain as stated by that baseline. The JSON includes 0.25, 0.30, and 0.50 mm per-side sensitivity cases.

Frozen baseline SHA-256: f0e43cb06da1f73f0a66e424a0af90c178ac351d479c2cade8481b321131c3a6. File modification time recorded at review: 2026-09-30T11:54:18.679739+00:00. Snapshot first read for this review: 2026-09-30T12:00:54Z. Per-instance and three-instance savings can be reapplied to a future verified full-BOM baseline; the hypothetical historical totals must not be presented as latest design fit.
