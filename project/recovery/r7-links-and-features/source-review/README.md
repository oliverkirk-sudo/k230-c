# Precision resistors and zero-ohm links: source and land review

Reviewed 2026-10-03 against the R5 physical-candidate netlist. This is a read-only identity/geometry review of seven still-unassigned references. No schematic, PCB, electrical value, population, or library file was changed. The 38 × 38 mm outline, 140 contacts, six-layer/top-only scope and high-temperature target remain constraints. R528 remains DNP and storage remains inhibited.

The next geometry-only stage has concrete source-backed candidates for all seven references: reuse the existing TNPW lands at R205/R206, create separate WSL and WFZ land definitions for R220/R561, and reuse the CRCW source lands for the three role-specific zero links. These are conditional candidates, not electrical, assembly, lifetime, hot-operation or production approval.

## Reference mapping

| Reference | Preserved circuit role | Candidate identity | Copper geometry key | Remaining application gate |
|---|---|---|---|---|
| R205 | CPU VSET/PG–GND, 56.2 kΩ, 0.8 V startup, address 0x49 | TNPW040256K2BYED | TNPW0402_IPC | Total resistance throughout the actual startup/mission conditions |
| R206 | KPU VSET/PG–GND, same selection | TNPW040256K2BYED | TNPW0402_IPC | Same as R205 |
| R220 | VDD0P8_CORE → VDD0P8_DDR_CORE | WSL060300000ZEA9 | WSL0603_9 | Actual branch peak/inrush, hot resistance/drop, solder and PCB heating |
| R561 | VDD1P8 → VEMMC_IO, eMMC VCCQ and local pulls | WFZ040200000ZE66 | WFZ0402 | Actual Micron load/peak/inrush, hot resistance/current and total rail drop |
| R221 | VDD_3V3 → K230 VDD3P3_SD | CRCW02010000Z0ED | CRCW0201_ZERO | Supply-branch hot current/drop; 50 mA guide entry is not a peak limit |
| R401 | AVDD1P8_PMU → GPIO68/INT4 | CRCW02010000Z0ED | CRCW0201_ZERO | PMU input/internal-pull current and firmware ownership |
| R528 | VDD1P8 → qualification input, default DNP | CRCW02010000Z0ED, if subsequently qualified for population | CRCW0201_ZERO | Preserve DNP; fitted hardware does not verify OTP/first-boot voltage |

Exact current value strings, pin-to-net bindings and DNP state are in [reference-map.json](reference-map.json). The active U3 is **MTFC16GAPALBH-AAT**, not the Samsung device in an earlier mechanical review. Do not carry that older Samsung 180 mA illustration into a qualification claim for this snapshot.

## Explicit land geometry

All dimensions below are millimeters, with the resistor's length along x, origin at its center and pads numbered 1 at negative x and 2 at positive x. The parts are nonpolar. Body sizes are supplied separately in [footprint-geometry.json](footprint-geometry.json).

| Geometry key | Each rectangular pad x × y | Centers x | Inner gap | Total copper span x × y | Drawing |
|---|---:|---:|---:|---:|---|
| TNPW0402_IPC | 0.55 × 0.60 | ±0.475 | 0.40 | 1.50 × 0.60 | Vishay 28950 p1, IPC-7351 reflow row |
| TNPW0402_IEC_ALTERNATE | 0.35 × 0.55 | ±0.450 | 0.55 | 1.25 × 0.55 | Same page, IEC 61188-6-2 alternative |
| WSL0603_9 | 1.01 × 1.01 | ±0.755 | 0.50 | 2.52 × 1.01 | Vishay 30192 p2 |
| WFZ0402 | 0.50 × 0.60 | ±0.450 | 0.40 | 1.40 × 0.60 | Vishay 30432 p2 |
| CRCW0201_ZERO | 0.28 × 0.43 | ±0.255 | 0.23 | 0.79 × 0.43 | Vishay 20052 p2 |

The [TNPW pad source](https://www.vishay.com/doc?28950) makes IPC and IEC rows separate alternatives. Use the existing IPC candidate for consistency; do not average them. The WSL numbers use the drawing's printed metric dimensions, which are rounded relative to its inch dimensions. In the WFZ drawing, **a is the gap, b is each pad's x length, and c is its y width**; treating a/b/c as three pad dimensions would produce the wrong land.

The existing TNPW footprint has 0.05 mm mask expansion, 1:1 paste and a 2.1 × 1.2 mm courtyard. The existing CRCW footprint has 0.025 mm mask expansion, separate 1:1 paste apertures and a 1.39 × 1.03 mm courtyard. These remain project process assumptions. WSL/WFZ mask, stencil and courtyard construction still need process decisions. Their existing planning reservations of 3.2 × 1.7 and 2.0 × 1.2 mm are not manufacturer courtyards. Source copper dimensions alone do not establish heat flow, solder quality or board fit.

## R205/R206 grade and tolerance applicability

[TI SLVSEI1C, Table 8-1 p12](https://www.ti.com/lit/ds/symlink/tps62864.pdf) specifies the 56.2 kΩ selection with ±1% accuracy. Preserve the current 56.2 kΩ/1% circuit requirement. The tighter proposed component grade does not change its nominal value, startup voltage or I²C address. The allowable ±1% interval is 55.638–56.762 kΩ; the existing conditional ±0.70% target is 55.8066–56.5934 kΩ.

[Vishay 28758, revision 10-Apr-2026](https://www.vishay.com/docs/28758/tnpw_e3.pdf), pp3–4, supports the ordering construction **TNPW0402 + 56K2 + B + Y + ED**: 56.2 kΩ, ±0.1%, ±10 ppm/K, lead-free ED packaging. This is manufacturer-schema support, not a stock/lifecycle check or an independently located exact catalogue row. Page 15 delegates lands to document 28950.

A linear TCR screen from 20°C to 125°C, compounded with initial tolerance and rounded conservatively, gives about ±0.206%, leaving about 0.494 percentage points within the existing ±0.70% target. This is only a screening calculation. Film temperature, soldering shift, moisture, aging and operating duration must fit the total budget. The source's general/power/advanced operating modes have different dissipation, film-temperature and finite-duration drift conditions; none establishes arbitrary-life ±0.70% accuracy.

The active regulators are TPS628640B variants. TI §8.4.5 describes the VSET/PG high state as driven toward VIN. Using 5.5 V and the 1% lower resistance gives approximately 0.544 mW and 98.9 µA as a DC stress illustration. This does not replace startup testing or thermal qualification. A 125°C air temperature must not be mistaken for a 125°C resistor-film temperature with finite dissipation.

## Power-link limits

**R220:** [WSL-9, revision 24-Aug-2026](https://www.vishay.com/docs/30192/wsl-9.pdf), pp1–2, supports the exact WSL0603/00000/Z/EA/9 construction. Use the **0603 row's 0.25 mΩ**, not the generic heading's 0.20 mΩ. It lists 45 A and a rated-current curve falling above 70°C to zero at 170°C. The TCR is nominal 3900 ppm/°C. Therefore neither 45 A nor 0.25 mΩ is established as a simultaneous guarantee throughout the hot range. Its [exact order row](https://www.vishay.com/en/product/30192/tab/quality/) is present, with tin termination and Non-Automotive qualification labeling. No commodity-jumper substitution is supported.

**R561:** [WFZ, revision 12-Jun-2025](https://www.vishay.com/docs/30432/wfz-jumper.pdf), pp1–3, supports WFZ/0402/00000/Z/E66, 3 mΩ and 6.5 A. The graph is **power ratio**, falling above 70°C to zero at 155°C. It is not a direct current-ratio curve. The source says electrical characterization was not performed and identifies copper's 3900 ppm/°C TCR. The inspection/test limits measured after exposure are not guaranteed in-situ hot resistance. The missing evidence is a characterized R(T)/hot-current limit under defined mounting conditions, plus this board's load and thermal conditions; no exact hot current is asserted here. The family datasheet mentions AEC-Q200, but the [exact order row](https://www.vishay.com/en/product/30432/tab/quality/) says Non-Automotive. Preserve that qualification ambiguity rather than claiming an automotive ordering grade.

## Separate treatment of the other zero links

[CRCW0201, revision 21-Sep-2022](https://www.vishay.com/docs/20052/crcw0201e3.pdf), pp1–2, explicitly supports 50 mΩ maximum and 1 A **at 70°C**, with ordering construction CRCW0201/0000/Z/0/ED. The [exact order row](https://www.vishay.com/en/product/20052/tab/quality/) is present. Nonzero-resistor TCR grades and a resistor power graph do not provide a separately guaranteed hot-jumper R(T)/I limit.

R221 feeds only the SoC branch seen in this netlist: C244 and U1.E10. The [Canaan hardware guide](https://github.com/kendryte/k230_docs/blob/main/en/00_hardware/K230_Hardware_Design_Guide.md) identifies VDD3P3_SD as MMC output/pre-buffer IO supply and gives a 50 mA entry. At 50 mA and 50 mΩ, the illustrative drop is 2.5 mV and dissipation 0.125 mW. The external TF card's supply must not be assigned to this link; actual peaks, hot resistance and total branch margin are still open.

R401 is a direct rail-to-input strap, so firmware must not drive the strapped input low. R528 connects to R529 and U92.2 only on its qualification side; its DNP state is part of the default inhibit mechanism. Geometry for either strap does not resolve its functional gate.

## Evidence and verification

[source-manifest.json](source-manifest.json) records document revisions, URLs and downloaded-PDF hashes. Manufacturer originals and rendered pages remain outside this report package. Relevant pad, body, ordering and VSET-selection pages were inspected visually; geometry arithmetic, seven-reference extraction and R528 DNP were checked. [verification.json](verification.json) records those checks and the input hashes. No whole-board placement, routing, DRC, power-integrity, boot or thermal test was performed by this source review.
