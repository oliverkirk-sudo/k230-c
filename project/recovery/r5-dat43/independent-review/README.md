# Independent R5 DAT43 review

2026-10-03. **PASS for the bounded eight-resistor delta against published R4.** This review reads the main CAD and does not modify it. It verifies the conditional resistance-range change, exact graph preservation and native schematic checks. It does not qualify lifetime, signal integrity, boot behavior or a complete PCB.

## Verified delta

Only **R563–R570** change from `47k DATA PULLUP` to `43k CRCW020143K0FKED DAT PULLUP CANDIDATE`, with assignments to the existing `CMK230_Recovery_Passive_Candidates:Vishay_CRCW0201_SourceLand_PROCESS_CANDIDATE` footprint. Its native library file is byte-identical to R4; no new land geometry was introduced.

The independent comparison covers all **254 components, 457 distinct nets and 1,509 pin/net/function/type bindings**. All net codes/names and node attributes are preserved. Apart from the eight specified values and their footprint fields, every exported component attribute is preserved, including population properties, symbol/library identities and UUIDs. DAT0–DAT7 remain on each resistor's pin 1; pin 2 remains on VEMMC_IO.

The only sheet with circuit changes is `14_EMMC_Local_Bias.kicad_sch`. Reversing its eight value/footprint edits reproduces the R4 sheet exactly after allowing the explicit title revision metadata change from RCV-PHYS1 to RCV-R5. The root schematic has only that title revision metadata change. Other schematic files are byte-identical. Coordinates, wires, labels, symbol population flags and pin maps are unchanged.

R33 remains 270 kΩ; R528 remains DNP. The previously reviewed 25 ordinary-bias positions remain unassigned. Coverage is therefore **158 → 166 assigned references**, with 88 unassigned, rather than an adoption of that separate bias batch. The six-layer, 38 × 38 mm, 140-contact, top-only contract is unchanged; this establishes no complete-board routing or fit.

## Bounded electrical result

The selected Micron MTFC16GAPALBH-AAT family allows DAT pullups of 10–50 kΩ. A **required ±10% total resistance envelope** around 43 kΩ gives **38.7–47.3 kΩ**, leaving 28.7 kΩ to the lower limit and 2.7 kΩ to the upper limit. The former 47 kΩ/±10% screen reaches 51.7 kΩ and exceeds the upper limit. [Micron automotive eMMC, Rev G, Table 1 p2 and Table 13 p27](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/234/EMMC_5F00_DATASHEET.pdf)

At the source VCCQ ceiling of 1.95 V and Rmin=38.7 kΩ, the conservative full-supply DC calculation is:

- Pullup contribution to a zero-volt sink: **50.3876 µA per resistor**
- Resistor dissipation: **98.2558 µW per resistor**

These values describe the incremental resistor load, not total driver current, guaranteed low-level drive capability, input leakage or an accepted voltage waveform. They do not establish DAT high/low thresholds, timing, signal integrity, partial-power behavior or ROM boot operation.

CRCW020143K0FKED is the manufacturer-schema candidate for 43 kΩ, F=1% initial tolerance, K=100 ppm/K. These nominal grade properties do not guarantee an arbitrary mission lifetime. The complete ±10% envelope must still be established over actual film temperature, mounting shift, environment and aging; independent manufacturer qualification tests cannot be added into such a guarantee. Exact orderability, stock and lifecycle are not verified. The existing footprint's mask, paste and courtyard remain process assumptions. [Vishay 20052, revision 21-Sep-2022](https://www.vishay.com/docs/20052/crcw0201e3.pdf)

## Independent verification

- Fresh KiCad 9.0.2 netlist export and ERC were run in a disposable copy, leaving main CAD untouched
- Fresh export matches both the stored R5 component graph and the exact permitted R4-to-R5 delta
- Fresh ERC reports **zero violations**; this is schematic validation, not PCB or functional acceptance
- The independent script checks all exported component attributes, source pin definitions, every net/node attribute, raw schematic text, DAT supplies, unchanged source lands and the unadopted ordinary-bias batch

`independent-review.json` contains the full bounded result and input hashes; `native-checks.json` records the isolated native runs. Reproduce with `validate_independent.py --baseline /path/to/r4/project --candidate /path/to/r5/project`, adding `--fresh-netlist` and `--fresh-erc` for separately generated native reports. `artifact-sha256.json` covers the deliverables. No vendor PDF or screenshot is redistributed.
