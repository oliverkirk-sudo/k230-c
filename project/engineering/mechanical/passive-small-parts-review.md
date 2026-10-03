# Dense small passives: electrical and mounting screen

2026-09-30; compact 237-populated-part, 243-envelope design snapshot. The 0201 scenario contains 106 capacitor and 49 resistor envelopes at 1.1 × 0.7 mm. It already assigns larger boxes to all 1–47 µF capacitors, the precision feedback/sense resistors, the high-current R220 link, ferrites and power inductors. There is no basis to reject every 0201 assignment merely from the package name.

## Capacitors and unreserved bulk

Later source clarification from the design lead: the reference PLL/VAA filters use 100 nF local capacitors; the old “local bulk TBD” labels were speculative. No missing required bulk has been established or removed. The lead has added two source-backed MIPI 100 nF capacitors to the newer design. The counts and eleven-position sensitivity below describe this report's earlier snapshot, not a claim that eleven extra capacitors are required.

Six 100 nF bypass capacitors C205/C209/C215/C222/C227/C232 are directly on VIN_5V. A 6.3 V rating alone leaves limited supply-overshoot margin; a concrete 10 V option is preferable for the screening candidate. Official Samsung CL03B104KP3NNWC is a 0201 100 nF, 10 V X7R option; the separate capacitor review records its dimensions and typical bias curve. At 5 V it is approximately 56.8 nF, so “100 nF nominal fits” does not mean “100 nF effective is provided.” Most other 100 nF parts sit on 0.8/1.1/1.8/3.3 V rails, and still need rail-specific PDN acceptance.

C233–C238 and C240–C244 explicitly say “100nF REF / local bulk TBD.” Their present small boxes do not reserve additional bulk. If an additional 0603-like 2.2 × 1.3 mm capacitor is needed at each of these eleven sites, keeping the existing bypass parts adds **31.46 mm²** and eleven placements; an additional 0402-like 1.6 × 1.0 mm part each adds **17.60 mm²**. These are sensitivity cases, not recommendations to add eleven parts or to replace/remove the existing bypass capacitors. Filter impedance, load steps and analog-noise results determine actual need.

System ambient and local component temperature limits have not been established. The memory devices' case-temperature specification is not an 85°C board-ambient specification. An X5R alternative must not be substituted for the frozen X7R wording without a justified temperature range and effective-capacitance margin.

## Resistors and jumpers

Vishay CRCW0201 e3 provides a concrete ordinary-resistor family: 50 mW rating at 70°C, 30 V limiting element voltage, 1% grades, and a zero-ohm option CRCW02010000Z0ED specified at 50 mΩ maximum and 1 A maximum at 70°C. Its official 2022-09-21 drawing (document 20052 p2, inspected visually) gives body 0.60±0.03 × 0.30±0.03 × 0.23±0.03 mm; recommended copper pads 0.28 × 0.43 mm with 0.23 mm inner gap. The outer copper envelope is 0.79 × 0.43 mm, fitting the current 1.1 × 0.7 reservation with 0.155/0.135 mm per-side allowance. Mask, stencil and assembly clearance remain unqualified. A blanket 0.25 mm courtyard convention would enlarge even these small parts; the dense boxes are explicitly a denser assembly assumption.

For ordinary pull-ups/pull-downs, rated voltage is ample: 5.5 V across 10 kΩ is 3.03 mW; 3.3 V across 10 kΩ is 1.09 mW. The 1.1 V, two-240 Ω DDR_VREF divider dissipates approximately 1.26 mW in each resistor. This supports plausibility, not lifetime or signal-integrity qualification. R63/R64/R69–R71 calibration resistors need their actual pin currents and temperature accuracy checked; assigning the entire rail voltage to a calibration pin is not a valid substitute for that check. Existing total-error≤0.15% feedback and guard-divider parts are already excluded from the generic 0201 bin; a commodity 1% resistor cannot satisfy that budget.

**R561 is a supply feed, not a logic pull-up.** The lead's visually checked Samsung eMMC Table 33 gives 180 mA controller and 50 mA NAND for the 16 GB device under x8 HS400, using 100 ms RMS averaging. It does not guarantee transient peak current. At 180 mA, a 50 mΩ link contributes up to 9 mV and 1.62 mW using the published room-condition resistance, before PCB drop and temperature. A 0201 jumper is therefore not ruled out by that RMS figure, but peak/inrush, thermal derating and the 1.70 V minimum VCCQ margin must be qualified. If later enlarged to the existing 0402 reservation convention, R561 adds 0.83 mm².

R221 feeds the K230 VDD3P3_SD branch, for which the lead reports a 50 mA guide budget; it does not supply an external TF card's main supply. At 50 mA and 50 mΩ, link drop is 2.5 mV and dissipation 0.125 mW. Do not reject its 0201 reservation based on an assumed external-card load. A 0402 sensitivity for both R221 and R561 together is +1.66 mm², not a required correction established by this audit. R220 remains the separately selected 0603 low-ohmic power link.

## Concrete power-feed candidate and R220 correction

For a coherent conservative power-feed candidate, use **Vishay WFZ040200000ZE66** at R561 for review: 0402 metal-foil jumper, 3 mΩ maximum, 6.5 A published current rating with temperature derating (power derating begins at 70°C). Its body is 1.00±0.10 × 0.50±0.10 × 0.40±0.10 mm. The official p2 drawing gives two 0.50 × 0.60 mm pads with 0.40 mm gap, a 1.40 × 0.60 mm land envelope. Adding hypothetical 0.05 mm mask and 0.25 mm clearance gives a **2.0 × 1.2 mm reservation**, +1.63 mm² over R561's current box. At 180 mA and 3 mΩ, the room-condition link drop is 0.54 mV and loss 0.0972 mW. PCB and contact resistance, peak/inrush and operating temperature still require system acceptance. This exact MPN is listed on Vishay's product quality page; no purchase or procurement commitment was made.

**R220's reservation correction:** its already specified WSL060300000ZEA9 has two recommended 1.01 × 1.01 mm pads and 0.50 mm gap, hence a 2.52 × 1.01 mm copper envelope. This cannot fit the old 2.2 × 1.3 mm box. With the same hypothetical mask/clearance convention, round outward to **3.2 × 1.7 mm**, adding 2.58 mm². Vishay's 2026-08-24 WSL-9 p2 drawing was inspected visually. The lead subsequently authorized this reservation correction and R561's 2.0×1.2 mm candidate reservation in the current area tool. R220's circuit was not changed by this audit; do not add these already-applied deltas to the current baseline a second time.

## Concrete smaller ferrite candidate

Murata **BLM15PX121SN1D** is a 0402 DC-power-line ferrite with 120 Ω ±25% at 100 MHz; initial DCR≤0.055 Ω, post-test limit 0.070 Ω; rated current 2.0 A at 85°C, linearly derated to 1.1 A at 125°C. Body is 1.00±0.05 × 0.50±0.05 mm, height 0.50±0.05 mm. This meets the nominal impedance/DCR wording of FB202–FB210, but is not a complete electrical selection: biased impedance, noise attenuation, DC voltage drop, filter resonance and branch current must be reviewed.

Official drawing JENF243A_0018AR-01 pp3/4/9 was visually inspected. Recommended pad opening dimensions are gap a=0.4, outer span b=1.2, width c=0.5 mm. The manufacturer's power-line copper extension dimension d depends on current class and copper thickness. For the 2.2-A-or-lower row, d is 1.2 mm at 18 µm foil, 0.7 mm at 35 µm, and 0.5 mm at 70 µm. Thus a generic two-pad 0402 footprint must not erase the copper/current condition.

Using a **hypothetical** 0.05 mm mask expansion and 0.25 mm clearance around the union of maximum body, mask and local copper, then rounding outward, gives these provisional reservations:

| Foil thickness | Reservation | Area per bead | Delta for nine versus current 2.2×1.3 |
|---|---:|---:|---:|
| 18 µm | 1.8×1.7 mm | 3.06 mm² | +1.80 mm² |
| 35 µm | 1.8×1.2 mm | 2.16 mm² | −6.30 mm² |
| 70 µm | 1.8×1.1 mm | 1.98 mm² | −7.92 mm² |

These figures exclude the continuing power traces and route space. They do not authorize changing all nine parts, copper thickness or the PCB stackup. No ferrite footprint or master edit is made.

## Sources

- [Vishay CRCW0201 e3](https://www.vishay.com/docs/20052/crcw0201e3.pdf), SHA-256 `95854b1c87ad23bded6a4bc3f6c09c1d6fedb230cada90c6c80b39376ad35af1`; [exact jumper order code](https://www.vishay.com/en/product/20052/tab/quality/)
- [Vishay WFZ jumper specification](https://www.vishay.com/docs/30432/wfz-jumper.pdf), SHA-256 `e848e86d529942d7992878b21873481261d0f01f8511f236cb1ed8ad4b178352`; [exact WFZ040200000ZE66 listing](https://www.vishay.com/en/product/30432/tab/quality/); [WSL-9 existing power jumper](https://www.vishay.com/docs/30192/wsl-9.pdf)
- [Murata BLM15PX121SN1 current product page](https://pim.murata.com/en-us/pim/details/?partNum=BLM15PX121SN1%23); [official detailed specification](https://pim.murata.com/asset/pim4/ferriteBeadInductortypefilter/ENFA0018_PDF_FERRITEBEADINDUCTORTYPEFILTER?lastModifiedDatetime=20260520151432), SHA-256 `26e3632f29268632a2ae03ce1b86b971044e76f3b1ad7dbe24eb5c39f4f6c5ee`
- Existing project source Samsung `emmc.pdf` p25, Table 33, provided by the lead; power/signal roles checked against the frozen integrated `master.xml`

Manufacturer originals remain outside the distributable design tree. This report identifies plausible candidates and unresolved requirements; it establishes neither full-board fit nor routed/thermal/PDN feasibility.
