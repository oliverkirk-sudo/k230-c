# Nine-reference 22 µF geometry applicability

2026-10-03. **Conditional geometry evidence only; no library, CAD, value or count change.** The 47 µF engineering proposal remains unselected.

Active source: `cad/recovery-physical-candidate/master.xml`, SHA256 `bbb9c482b05e066ba6d9ee046218abe1227d5e7918d8ebe4e1a7bcb358256183`. All nine footprint fields are currently unassigned.

| References | Exact value field | Pin 1 | Pin 2 | Distinct role |
|---|---|---|---|---|
| C206, C207, C208 | 22uF X7R / total Ceff>=30uF | VDD0P8_CPU | GND | CPU regulator output bank |
| C212, C213, C214 | 22uF X7R / total Ceff>=30uF | VDD0P8_KPU | GND | KPU regulator output bank |
| C540 | 22uF | VDD1P1_DDR_IO | GND | DRAM VDD2 local bulk; 01studio p2 C20 / C20-C31 group |
| C552 | 22uF | VDD1P1_DDR_IO | GND | DRAM VDDQ local bulk; 01studio p2 C40 / C40-C49 group |
| C562 | 22uF | VDD1P8 | GND | DRAM VDD1 local bulk; 01studio p2 C32 / C32-C39 group |

The same CL31B226KPHNNNE exact source-land identity is a defensible conditional geometry candidate for all nine. It preserves 22 µF nominal, uses a 10 V ±10% X7R part with maximum body 3.40 × 1.80 × 1.80 mm, and its exact specification p33 supplies the applicable 3216 ±0.20 mm reflow row. Midpoint pads are 1.25 × 1.80 mm at x = ±1.475 mm, gap 1.70 mm, total copper 4.20 × 1.80 mm. The original manufacturer ranges and hash remain in the companion JSON and source review.

The three local positions are on the active Local_Decoupling sheet. Their role labels come from the preserved allocation and source inventory, independently checked against current values and pin nets. The source population is 01studio LPDDR4 provenance; it does not qualify the active Micron MT53E256M32D2FW-046 AAT:B implementation. C540 and C552 share a net but retain separate load-local roles. Top-side placement near their relevant power/return balls remains required by the allocation.

This identity does not establish Ceff, PDN impedance, transient noise, ESR/ESL, aging, thermal/ripple performance or assembly qualification. The CPU/KPU requirement remains ≥30 µF effective per three-part output bank. No numerical DDR local-capacitance minimum is established here. Do not count the local positions as interchangeable with regulator-output positions merely because their nets match. The generic local22uF fields are not changed into exact-MPN/X7R commitments.

No library was generated. Any later source-library generation remains gated on current R10 publication.
