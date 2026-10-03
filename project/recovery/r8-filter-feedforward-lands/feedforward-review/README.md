# Feedforward capacitor source review

**Conditional recommendation:** KEMET **C0402C122J5GACTU**, quantity four for C202/C219/C224/C229. It is exactly 1.2 nF, C0G/NP0, ±5%, 50 VDC, −55°C to +125°C, EIA 0402. This closes a bounded part-and-land source question. It does not qualify converter loop stability or release the board for manufacturing.

## Why all four values are 1.2 nF

[TI SLVSEF9I](https://www.ti.com/lit/ds/symlink/tps62827.pdf), revised March 2024, §8.2.2.2 p12, gives C3[F] = 12e−6 / R2[Ω]. All four lower divider resistors are 10 kΩ, so the nominal result is 1.2 nF. TI's 120 pF example uses R2 = 100 kΩ. Section 8.2.2.5 p14 requires feedforward capacitance for the adjustable versions used here. Section 5 p3 confirms FB is pin 3.

Read-only XML checks found each capacitor across its regulator's upper divider resistor:

| Capacitor | Regulator | Output / cap pin 1 | FB / cap pin 2 / regulator pin 3 | Upper resistor | Lower resistor |
|---|---|---|---|---|---|
| C202 | U21 TPS62827ADMQ | VDD0P8_CORE | FB_CORE | R201 3.32 kΩ | R202 10 kΩ |
| C219 | U24 TPS62826ADMQ | VDD1P1_DDR_IO | FB_DDR | R207 8.66 kΩ | R208 10 kΩ |
| C224 | U25 TPS62825ADMQ | VDD1P8 | FB_1V8 | R210 20 kΩ | R211 10 kΩ |
| C229 | U26 TPS62826ADMQ | VDD_3V3 | FB_3V3 | R213 45.3 kΩ | R214 10 kΩ |

Lower resistor pin 2 is GND in each case. All four capacitor footprints remain unassigned. Ideal nominal outputs from these actual resistors are 0.7992, 1.1196, 1.8000 and 3.3180 V respectively. These are calculated setpoints, not measured rail voltages or rail-accuracy acceptance results.

## Manufacturer dimensions and selected source lands

The [exact-part manufacturer specification](https://search.kemet.com/component-documentation/download/specsheet/C0402C122J5GACTU), generated 2026-10-03, gives body L = 1.00 ±0.05 mm, W = 0.50 ±0.05 mm and T = 0.50 ±0.05 mm; termination band B = 0.30 ±0.10 mm; terminal separation S ≥0.30 mm.

The [manufacturer family datasheet](https://search.kemet.com/component-documentation/download/datasheet/C0402C122J5GACTU.pdf), C1003_C0G dated 2025-02-20, p12 Table 3, supplies IPC-7351-based lands. Use **density B as a process candidate**:

- Two rectangular 0.62 × 0.62 mm copper pads centered at (−0.45, 0) and (+0.45, 0) mm
- Pad center pitch 0.90 mm; inner copper gap 0.28 mm; outside copper span 1.52 mm
- Manufacturer grid-placement courtyard 1.90 × 1.00 mm, centered on the part
- Top-side reflow mounting; part is nonpolar

The source drawing was visually checked: **C = 0.45 mm is the origin-to-pad-center distance**, not full pitch. X and Y are pad dimensions. V1 and V2 describe the courtyard, not copper.

The table also offers density C: 0.52 × 0.52 mm pads at x = ±0.40 mm, 1.60 × 0.80 mm courtyard. It is recorded but not selected because the manufacturer requires process qualification before using minimum lands. Mask expansion, paste reduction, stencil thickness and roundrect radii are not defined by this land table and remain assembler decisions. No library footprint or CAD file was created or modified.

## Electrical applicability and limits

At nominal regulation the capacitor DC voltages calculated across the upper resistors are 0.1992, 0.5196, 1.2000 and 2.7180 V. The 50 VDC working rating provides ample nominal voltage headroom; this calculation does not bound startup, shutdown, fault, ringing or coupled switching transients. The 125 V dielectric-withstand test rating is not a working rating.

Manufacturer C0G TCC is ±30 ppm/°C relative to 25°C, with zero specified aging rate. Initial ±5% gives 1140–1260 pF at 25°C. Multiplying initial tolerance and TCC limits gives 1136.58–1263.78 pF at 125°C. The cited TI recommendation does not state a permissible Cff tolerance window, so the ±5% choice remains conditional on verification with the real regulator, resistor errors, inductor, effective output capacitance, load and layout.

The provisional 85°C enclosure-air requirement leaves a numerical 40°C difference to the capacitor's 125°C maximum. That is not measured component thermal margin. Local board heating, self-heating and neighboring regulators still have to keep the component within its rating. A 38 × 38 mm, six-layer, top-only assembly is preserved as a constraint; this review does not establish full-board fit or thermal performance.

TI §8.4.1 p22 calls for output sensing at the output capacitor and keeping FB routing away from SW noise. Respect those conditions when implementing these lands.

## Procurement snapshot and preference gap

[LCSC C22402196](https://www.lcsc.com/product-detail/C22402196.html) is the exact part. The opened web snapshot showed 220 pieces, **minimum 20 and multiple 20**. An older search snippet showed a different stock count; neither is a reservation or real-time inventory guarantee. JLC assembly-library availability was not independently established.

The [same exact part at DigiKey](https://www.digikey.com/en/products/detail/kemet/C0402C122J5GACTU/3316991) has a cut-tape quantity-one price tier (399-C0402C122J5GACTUCT-ND); the opened snapshot showed 104,698 units and $0.52 at quantity one. This is a MOQ1 alternative supplier, not a changed electrical part. Verify current stock at ordering. No purchase, cart action or outreach occurred.

## Files and verification

- `conditional-contract.json`: exact part, formula, application limits and release holds
- `footprint-geometry.json`: exact density B copper/courtyard coordinates and unselected density C alternative
- `reference-map.json`: all four pin nets, dividers and nominal calculations
- `source-manifest.json`: primary manufacturer URLs, PDF SHA-256 hashes and page references
- `procurement-observations.json`: explicit LCSC MOQ exception and same-part MOQ1 alternative
- `verification.json`: read-only net checks and bounded verification results

Raw vendor PDFs, complete extracted text and source page images are retained separately and are not redistributed in this directory. Source XML SHA-256 remained da6a33fa5ccc36897785d1b443d49979f0a37690e5fd8da6ff8ad566f3e59ec9.
