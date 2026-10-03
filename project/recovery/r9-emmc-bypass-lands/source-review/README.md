# eMMC bypass exact-part and land review

Status: **engineering candidates only**. This bounded review covers C64/C65/C69/C70/C71/C72 in the r7 physical-candidate netlist for Micron MTFC16GAPALBH-AAT. No CAD, component value, purchase, supplier inquiry or external publication was performed. The preserved values are three 2.2 uF capacitors and three 100 nF capacitors.

## Candidate decision

| References | Candidate | Nominal / rating | Body | Supplier catalog |
|---|---|---|---|---|
| C64, C69, C71 | Murata GRM188R71A225KE15D | 2.2 uF, +/-10%, 10 VDC, X7R, -55 to +125 C | 0603, 1.6 x 0.8 x 0.8 mm nominal | [JLC C86018](https://jlcpcb.com/partdetail/MurataElectronics-GRM188R71A225KE15D/C86018) |
| C65, C70, C72 | Murata GRM155R71C104KA88D | 100 nF, +/-10%, 16 VDC, X7R, -55 to +125 C | 0402, 1.0 x 0.5 x 0.5 mm nominal | [JLC C71629](https://jlcpcb.com/partdetail/MurataElectronics-GRM155R71C104KA88D/C71629) |

These exact parts preserve nominal values and provide manufacturer-backed temperature ratings and copper-land ranges. They have **not** been qualified for combined hot, biased and aged capacitance, memory power integrity, assembly yield or board fit. The reference sheets are dated 2021 and 2016 respectively; current approval-sheet and lifecycle status remain procurement checks.

## Actual nets and Micron requirements

| References | Net / device role | Table 13 symbols | Printed Min / Max / Typ (uF) |
|---|---|---|---|
| C64 / C65 | EMMC_VDDIM, U3.C2 internal node | C5 / C6 | 1 / 4.7 / 1; 0.1 / 0.1 / 0.1 |
| C69 / C70 | VEMMC_IO, U3 VCCQ | C1 / C2 | 2.2 / 4.7 / 2.2; 0.1 / 0.22 / 0.1 |
| C71 / C72 | VDD_3V3, U3 VCC | C3 / C4 | 2.2 / 4.7 / 2.2; 0.1 / 0.22 / 0.1 |

Every capacitor's pin 2 is GND. U3 VSS and VSSQ share GND. VEMMC_IO is fed from VDD1P8 through the R561 zero-ohm candidate, so the relevant VCCQ operating range is 1.70 to 1.95 V. The device also supports a separate 2.7 to 3.6 V VCCQ range; that does not make every intermediate voltage valid. VCC operates from 2.7 to 3.6 V. The reviewed source provides no numerical VDDIM output-voltage range: do not treat it as the VCCQ rail or attach an external supply to it. [Micron source, pp. 1, 7, 9, 27](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/234/EMMC_5F00_DATASHEET.pdf)

Table 13 does not explicitly say whether its capacitance columns represent nominal component choices or effective capacitance under operating conditions. It does not supply the needed voltage, tolerance, temperature or aging basis. The preserved nominals fit the printed ranges. **Neither nominal conformity nor the X7R rating establishes an all-effects operating margin.** The numerical columns must not silently become an asserted Micron effective-minimum requirement.

## Copper geometry proposal

The manufacturer's reflow table defines a = inner land gap, b = length of each land along the part, c = transverse land width. These are copper dimensions, not the body or courtyard. Both diagrams were inspected visually. Source tables are on page 26 of the two reference sheets; the reliability-test substrate lands are a different geometry and were not substituted.

| Candidate | Manufacturer a / b / c ranges (mm) | Proposed a / b / c (mm) | Each pad X x Y (mm) | Pad centers X (mm) | Outer span (mm) |
|---|---|---|---|---|---|
| GRM188R71A225KE15D | 0.6-0.8 / 0.6-0.7 / 0.6-0.8 | 0.70 / 0.65 / 0.70 | 0.65 x 0.70 | -0.675, +0.675 | 2.00 |
| GRM155R71C104KA88D | 0.3-0.5 / 0.35-0.45 / 0.4-0.6 | 0.40 / 0.40 / 0.50 | 0.40 x 0.50 | -0.400, +0.400 | 1.20 |

Pad-center Y is zero. The picks lie within the matching body-tolerance row. They are engineering choices within manufacturer ranges, not exact dimensions mandated by Murata. [2.2 uF reference](https://www.mouser.com/datasheet/2/281/1/GRM188R71A225KE15_04A-1985813.pdf), [100 nF reference via LCSC](https://www.lcsc.com/datasheet/C71629.pdf)

Corner treatment, mask expansion, paste apertures and courtyard are not established here. Placement must connect each pair close to its corresponding supply and return balls. These six planar land proposals do not prove placement, BGA escape, assembly feasibility or fit on the 38 mm, top-only, six-layer core.

## Conditional effective-capacitance budget

For sensitivity analysis only, write Ceff = Cnom x (1 + initial error) x (1 + no-bias temperature error) x k. The unknown k includes bias, AC excitation, aging, process, lot and their interactions. The separate +/-10% initial and +/-15% no-bias temperature limits do not certify a combined operating envelope.

If those separate reference limits apply and a combined residual bound k_min to k_max is independently validated, the resulting conditional intervals are:

- 2.2 uF part: 1.683 x k_min to 2.783 x k_max uF
- 100 nF part: 76.5 x k_min to 126.5 x k_max nF

If Table 13 were confirmed to demand effective minima, the C64 1 uF lower limit would require k_min >= 0.5942. The 2.2 uF lower limits for C69/C71 and 100 nF lower limits for C70/C72 would require k_min >= 1.3072 at the assumed lower tolerance/temperature corner. A loss-only residual factor cannot do that. Likewise, treating C65's 100/100 nF columns as a literal all-effects equality is incompatible with ordinary component tolerance. These are conditional engineering implications, not claimed Micron compliance failures.

No exact-part bias curve or hot/bias/aging bound was obtained. A manufacturer's generic illustrative curve and its post-treatment durability test cannot supply that missing bound. Do not count a companion 100 nF capacitor as a substitute for the separately specified larger capacitor without a reviewed requirement and impedance basis.

Use the actual CReg voltage, VCCQ up to 1.95 V and VCC up to 3.6 V in the eventual test or approved data request. Confirm the relevant AC measurement amplitude, ripple, frequency, lot/process corners and intended service life. Then test startup, supply transients and sustained memory operation. A separately reviewed 3.3 uF option may later be justified within Table 13's ranges; it is outside this nominal-preserving decision.

The provisional 85 C enclosure air is not capacitor surface temperature or local memory ambient. Capacitor surfaces must remain within +125 C including local heating and ripple losses. The AAT eMMC operating ambient limit is +105 C. The nominal 40 C/20 C differences from 85 C are not a validated thermal budget.

## Procurement exception

Both chosen JLC catalog pages resolve to the exact MPN. Their current visible public pages did not expose stock or MOQ, including a check using the cloud browser for C86018. The response metadata showed:

| JLC part | overseasStockCount | canPresaleNumber | preMinPurchaseNum | leastPatchNumber | lossNumber | First price tier |
|---|---:|---:|---:|---:|---:|---:|
| C86018 | 213,731 | 205,900 | 360 | 5 | 8 | 1 |
| C71629 | 1,101,623 | 1,031,905 | 1,920 | 20 | 12 | 1 |

Observed 2026-10-03 around 06:08 UTC. These are the site's field names, not assumed equivalents. The one-piece price tier is **not verified MOQ1**; pre-purchase minimum, assembly quantity, attrition and full-reel count differ. Treat both selections as procurement exceptions until the actual quantity/assembly quote is confirmed. The alternate J-package 2.2 uF SKU C2167658 did not resolve this ambiguity. Nothing was ordered, reserved, uploaded or submitted.

## Evidence and handoff

- `reference-map.json`: all six preserved labels, exact nets, table roles and input hash
- `exact-part-candidates.json`: exact MPN and package/rating facts
- `footprint-geometry.json`: source ranges and proposed copper coordinates
- `conditional-contract.json`: numerical assumptions, bounds and open qualification gates
- `procurement-observations.json`: timestamped observations and MOQ1 exceptions
- `source-manifest.json`: public source URLs, private-source SHA-256 hashes and page citations
- `verification.json`: consistency checks and stated limits
- `artifact-sha256.json`: review-file hashes

Raw vendor PDFs, HTML, extracted text and screenshots remain private and are not included in this directory. The Micron PDF carries a proprietary/confidential marking; this review contains only the required engineering facts and source reference, not copied document pages.
