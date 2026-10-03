# Output-capacitor source and land review

Reviewed 2026-10-03. **Candidate evidence only; no capacitor, BOM or CAD changes.** Four 47 µF X7R positions and six 22 µF X7R positions retain their values and counts. No smaller Murata 0805 substitution is selected.

The authoritative input for this review is `cad/recovery-physical-candidate/master.xml`, SHA256 `bbb9c482b05e066ba6d9ee046218abe1227d5e7918d8ebe4e1a7bcb358256183`. Historical `cad/integrated/master.xml` and older power documents are not the active snapshot.

## Findings

- **22 µF CL31B226KPHNNNE:** exact body and an applicable manufacturer reflow row are verified. A midpoint choice has two 1.25 × 1.80 mm pads at x = ±1.475 mm, with a 1.70 mm gap and a 4.20 × 1.80 mm total copper envelope. This is a selection inside the published range, not an assembly-qualified footprint.
- **47 µF CL32B476KQVVPNE:** exact body is verified, but the downloaded specification has no reflow row covering its ±0.40 mm length tolerance. The ±0.30 mm row is inapplicable. The ±0.40 mm **FLOW** row and recommended **TEST PCB** drawings are not production reflow land recommendations. An explicitly engineering-derived proposal is documented below; manufacturer reflow qualification remains open.
- **Both parts remain electrically unqualified.** Recovered typical DC-bias curves do not establish combined capacitance at actual voltage, ripple amplitude/frequency, temperature, aging and lot variation. Keep the 10 µF single-output and 30 µF CPU/KPU bank floors, plus actual stability/transient validation.

## Exact manufacturer geometry

| Part | Nominal / rating | Body L × W × T, mm | Maximum body, mm | Termination BW |
|---|---|---|---|---|
| CL32B476KQVVPNE | 47 µF ±10%, 6.3 V, X7R, 1210 | 3.20 ±0.40 × 2.50 ±0.30 × 2.50 ±0.30 | 3.60 × 2.80 × 2.80 | 0.60 ±0.30 mm |
| CL31B226KPHNNNE | 22 µF ±10%, 10 V, X7R, 1206 | 3.20 ±0.20 × 1.60 ±0.20 × 1.60 ±0.20 | 3.40 × 1.80 × 1.80 | 0.50 ±0.30 mm |

Samsung's current product pages list both parts as Mass Production. The exact downloaded reference specifications are dated June 26, 2024 and April 15, 2021 respectively; current access does not make their issue dates newer. Both PDFs are byte-identical to the hashes in the historical project review.

For the 22 µF part, specification PDF page 33, section 5-4, 3216 ±0.20 mm reflow row gives inner gap a = 1.64–1.76 mm, each pad length b = 1.19–1.31 mm, pad width c = 1.74–1.86 mm. Total copper span a+2b = 4.02–4.38 mm. The maximum-range choice is two 1.31 × 1.86 mm pads at x = ±1.535 mm, gap 1.76 mm. The drawing was visually inspected to verify that a is the pad gap and b is each pad's axial length.

For the 47 µF part, page 34 contains only 3225 ±0.20 and ±0.30 mm reflow rows. The next page's ±0.40 mm row is explicitly for flow soldering. Pages 3–4 show substrates for termination adhesion, bending and reliability tests. None closes the exact reflow applicability gap.

## Engineering-derived 47 µF proposal

**UNSELECTED. This is not Samsung's recommended land pattern. Do not mark it manufacturer-verified or released.** It is a deliberately generous starting point for assembly review using the exact body's and termination's ranges.

| Parameter | Proposal |
|---|---:|
| Pad centers | (−1.675, 0), (+1.675, 0) mm |
| Each pad | 1.65 × 3.20 mm |
| Inner copper gap | 1.70 mm |
| Nominal copper envelope | 5.00 × 3.20 mm |
| Maximum body height | 2.80 mm |

The explicit assumed process bounds are ±0.10 mm placement translation on each axis, no rotation, and ±0.05 mm independent copper-edge error. With the exact L/W/BW extrema, 64 terminal/corner combinations give at least 0.30 mm axial terminal overlap, 0.55 mm toe extension, 0.05 mm side extension and a 1.60 mm minimum copper gap. `derived-47uF-corner-checks.csv` records the enumeration. These bounds do not cover rotation, solder volume or wetting.

If a provisional 0.25 mm clearance is added outside the fabrication-expanded copper envelope, the planning rectangle is 5.60 × 3.80 mm. That clearance is an engineering assumption, not a manufacturer requirement. It supersedes no existing CAD or area model. The earlier 5.50 × 3.50 mm reservation is not enough to contain this particular expanded proposal. Large pads can increase solder volume and stress; paste, mask, rotation, flex, thermal cycling, tombstoning and solder-joint reliability must be reviewed before use.

The minimum missing input to approve a 47 µF land is either (a) a manufacturer-authored reflow drawing explicitly covering CL32B476KQVVPNE, including its ±0.40 mm L, ±0.30 mm W/BW tolerances and metal-epoxy termination, or (b) an accountable assembly-engineering approved copper/mask/paste drawing and documented process tolerance stack validated for this exact component. That review must cover placement rotation, paste volume/reflow, joint wetting and mechanical reliability. A new manufacturer drawing would close source applicability; production assembly validation would still be required. No contact or external approval was requested in this task. The independently verified 22 µF manufacturer range above remains separate from this unselected proposal.

## Active rails and electrical limits

| Output positions | Regulator | Active nominal voltage | Converter current rating | Effective output floor |
|---|---|---:|---:|---:|
| C201 | U21 TPS62827ADMQ | 0.7992 V | 4 A | 10 µF |
| C218 | U24 TPS62826ADMQ | 1.1196 V | 3 A | 10 µF |
| C223 | U25 TPS62825ADMQ | 1.8000 V | 2 A | 10 µF |
| C228 | U26 TPS62826ADMQ | 3.3180 V | 3 A | 10 µF |
| C206–C208 | U22 TPS628640BYCGR | 0.8000 V startup | 4 A | 30 µF bank |
| C212–C214 | U23 TPS628640BYCGR | 0.8000 V startup | 4 A | 30 µF bank |

The active fixed dividers use 10 kΩ lower arms with upper arms 3.32 kΩ, 8.66 kΩ, 20 kΩ and 45.3 kΩ. Each carries the active candidate's total-error limit ≤0.70%; each feedforward capacitor is 1.2 nF. CPU/KPU use 56.2 kΩ startup-selection resistors. These nominal voltages are not worst-case peaks; include regulator error, divider error, ripple and overshoot in the final voltage envelope. Converter current ratings are not MLCC ripple-current ratings or demonstrated installed rail capacity. TI also notes a lifetime reduction for TPS62864 at continuous 4 A when junction temperature exceeds 105°C.

TI TPS6282x Rev I section 8.2.2.5 (PDF p14) supports the 10 µF floor for all four exact A variants; the non-A TPS62827's 20 µF floor does not apply. Table 8-3 (p13) includes the existing 0.47 µH / 47 µF nominal combination and anticipates capacitance variation of +20%/−35%. For 47 µF, that row's lower anticipated capacitance is 30.55 µF. This is separate from the device's 10 µF minimum; clearing only the minimum does not prove the nominal-row stability result survives a larger combined derating.

TI TPS62864 Rev C section 9.2.1.2.5 (PDF p22) recommends at least 30 µF effective output. Table 9-3 (p21) includes 0.24 µH / 3×22 µF and anticipates +20%/−30% capacitance variation, a 46.2 µF lower edge for that nominal bank. A combined envelope outside the table's assumed range requires application stability/transient verification even if it remains above 30 µF.

The existing project rail-budget values provide high-end screening points of 0.88, 1.17, 1.98 and 3.63 V for the fixed rails and 0.88 V for CPU/KPU. They are not a substitute for verifying all loads' permitted voltages. The converter's 1.675 V register endpoint is outside the project's K230 0.72–0.88 V screen and is only a capacitor stress example, never approval to program the SoC to that voltage.

Fresh typical-curve spot checks at 25°C, 120 Hz and 0.5 Vrms give 47 µF-part capacitances of 48.626, 48.227, 46.213 and 38.481 µF at those four high-end screen points. A three-part 22 µF bank gives 67.046 µF typical at 0.88 V and 64.562 µF at the converter-only 1.675 V endpoint. No independent derating multipliers turn these into guaranteed minima. Samsung also supplies separate AC, biased-temperature and ripple-heating curves; they are not a combined guaranteed lower-bound surface.

A single 47 µF part must retain at least 21.28% of nominal to meet 10 µF; a three-part 22 µF bank must retain at least 45.45% of nominal to meet 30 µF. After the specified −10% initial tolerance, the respective remaining all-effect retention gates are 23.64% and 50.51%. These are acceptance arithmetic, not measured retention.

## Sources and deliverables

- [Samsung 47 µF exact product](https://product.samsungsem.com/mlcc/CL32B476KQVVPN.do), linked Specsheet; SHA256 `65dbb462997163abc75cd1d29c19f0a90227978cafa5e35e8186698901897391`
- [Samsung 22 µF exact product](https://product.samsungsem.com/mlcc/CL31B226KPHNNN.do), linked Specsheet; SHA256 `742b9759b46abf22af1f61562aac31870345cf654ca240911f98fda44cf58167`
- [TI TPS6282x Rev I](https://www.ti.com/lit/ds/symlink/tps62827.pdf); SHA256 `8a309f2a40486a380242d3f178eb4bda3ef4dca3deca647fa82f763d14866f63`
- [TI TPS62864 Rev C](https://www.ti.com/lit/ds/symlink/tps62864.pdf); SHA256 `f49cda50b21c8a84ea153120043efd31a5c4a58d2c0465909ea7f804806b8919`

`source-manifest.json` records current HTML hashes and download provenance. `geometry-review.json` separates manufacturer evidence from the engineering proposal. `active-master-snapshot.json` and `electrical-limits.json` preserve exact active references and qualification limits. `verification.json` records read-only checks. `build_review.py` reproduces numerical evidence from caller-supplied local sources; original vendor files are deliberately excluded from this deliverable.

No vendor contact, upload, purchase, board change, smaller-part selection, electrical qualification or manufacturing release was performed.
