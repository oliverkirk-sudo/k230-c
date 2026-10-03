# TPS628681A QFN process alternative: bounded comparison

Verdict: retain as a conditional alternative to the two TPS628640BYCGR CPU/KPU converters. It removes their unusually narrow source-land spacing with modest IC area growth. It is not approved as a performance-equivalent replacement: its high-temperature output accuracy is worse. Existing TPS62864 remains the baseline; no CAD changed.

## Exact candidate and electrical contract

Candidate ordering code **TPS628681ARQYR**, 4 A, RQY0009A nine-pin VQFN-HR. Do not substitute TPS628680A (different voltage range) or the fixed-start C variants. The official downloaded orderable addendum lists this exact code active/production, with Level-2-260C-1 YEAR moisture classification; the baseline addendum lists Level-1-260C-UNLIM. Thus assembly moisture handling becomes a new process consideration.

- Input 2.4–5.5 V; output 0.4–1.675 V, 5 mV increments
- 56.2 kΩ from pin 9 to AGND selects nominal 0.8 V and seven-bit address 0x49; keep both private I2C buses
- Startup resistor table requires ±1% accuracy; use the already reviewed total-error treatment. No extra current path or more than 30 pF on this pin during sampling
- Pin 9 is VSET/VID on this variant. After sampling its current source turns off; retain resistor to ground and use VOUT register 1. It does not reproduce the baseline B variant's fault-output behavior. The current design does not use that output for sequencing
- Pin map, top-view numbering: 1 AGND, 2 PGND, 3 VIN, 4 EN, 5 SDA, 6 SCL, 7 SW, 8 VOS, 9 VSET/VID. VOS goes directly to the output-capacitor sense node, away from SW. No invented tenth exposed-pad pin
- EN stays connected to existing CORE PG. Minimum high 0.84 V, maximum low 0.4 V; the existing 1.8 V I2C pullups remain within the interface range. Open-drain bus implementation and rise-time checks remain required

## Firmware comparison

VOUT1 = 0x01 and VOUT2 = 0x02 use the same 400 mV + code × 5 mV encoding as the baseline for this factor-one variant; 0.8 V command is 0x50. CONTROL 0x03 has the same 0x6F default and reset, FPWM-during-change, software enable, FPWM, discharge, hiccup and ramp-speed bit allocation. STATUS 0x05 retains thermal-warning, hiccup and UVLO flags and clears on read/reset. The CONTROL table is labeled write-only; do not implement read-modify-write based on assumed readable state.

Do not confuse the listed factory VOUT register default 0x64 (0.9 V) with the resistor-selected startup voltage. Section 8.4.3 says the output first ramps to the startup setting and changes to a new register value when changed through I2C; together with the current-source shutoff and resistor-held-low VID, this supports retaining 0.8 V before the first I2C change. No automatic pre-I2C jump to 0x64/0.9 V is described, and CONTROL 0x6F does not choose VOUT2. Preserve the startup flow, explicitly program the intended DVFS code after startup, verify readback and measured output. Initial I2C STOP after pullup power-up is recommended. Register reset on EN falling or loss of input means firmware must restore intended policy after those events. No register above the independently approved K230 operating voltage is authorized merely because the converter can generate it.

## Decisive temperature/accuracy tradeoff

TPS628681A specifies −40…125°C operating junction temperature, not 125°C enclosure air. Continuous 4 A operation above 105°C junction reduces lifetime. Both points also appear in the existing TPS62864 family conditions.

However, QFN full-temperature FPWM/no-load output accuracy is **±2%**; its ±1% applies only 0…85°C. Existing TPS628640B specifies ±1% for VOUT ≥0.59 V at 25…125°C. At nominal 0.8 V, QFN accuracy alone gives 0.784–0.816 V, versus 0.792–0.808 V for the baseline under that hot specification. Recheck every approved CPU/KPU voltage against K230 limits, ripple, load regulation and distribution drop before substitution. PFM and dynamic behavior are not covered by the quoted no-load FPWM guarantee. Typical 130°C warning and 150°C shutdown do not extend the recommended temperature limit.

## Source land and stencil comparison

Visually inspected the actual RQY0009A source land figure, PDF page 39, drawing 4225639/A:

- Six signal lands: 0.25 × 0.55 mm; adjacent signal pitch 0.50 mm gives 0.25 mm copper gap
- Three power lands: 0.95 × 0.20 mm; adjacent vertical center separation 0.40 mm gives minimum 0.20 mm copper gap at the touching/overlapping horizontal extents
- Bounding copper envelope: 1.90 × 2.90 mm = 5.51 mm², before courtyard, routing or assembly reserve
- Body: 1.5 × 2.5 mm = 3.75 mm², maximum height 1 mm. Baseline body 1.05 × 1.78 mm = 1.869 mm². Pair grows by 3.762 mm² of body area; board-fit cost still requires placement
- Source stencil example uses matching apertures and 0.10 mm thickness. For a 0.25 × 0.55 mm rectangular aperture the nominal area ratio is 0.859 before rounded-corner adjustment

The derived minimum 200 µm gap exceeds the baseline native-DRC measurement of 85 µm and the proposed generic 90 µm comparison. This removes that particular WLCSP copper-clearance exception. It does not certify whole-board routing, mask registration, stencil transfer or assembly yield. TI calls NSMD preferred and directs mask tolerances to the fabricator; confirm the imported footprint and actual board DRC rather than treating body pitch alone as clearance proof.

## BOM and power integrity

Keep the output effective-capacitance floor at **30 µF per rail**. TI says 8 µF effective input is sufficient for most applications; keep that existing project floor and validate ripple. There is no capacitor-count or capacitance saving.

The existing 0.24 µH DFE201612E-R24M appears explicitly in the QFN recommended-inductor list (6.6 A listed saturation, 13 mΩ listed DCR, 2 × 1.6 × 1.2 mm). Its actual hot saturation/loss and transient suitability still require checking. Source filter matrix accepts 0.24 µH with 2 × 22/47 µF, 3 × 22 µF or 150 µF nominal with stated derating bounds; other banks require stability verification. Do not blindly copy the 6 A application example's larger 4 × 4 mm Coilcraft inductor. Source-listed Murata 0805 output capacitors retain their separate, unresolved combined-condition capacitance gate.

No extra functional IC or GPIO is needed. Rebuild the package symbol and lands, reroute both converters, preserve short VIN/PGND loops and sense routing, update BOM/moisture handling, verify startup/reset and DVFS, and recalculate hot rail margins. VIN falling below UVLO is constrained to no faster than 10 mV/µs; arbitrary input collapse remains unqualified. Typical switch resistance is not a worst-case thermal-loss bound.

Primary sources actually read: [TI TPS62868 Rev B](https://www.ti.com/lit/ds/symlink/tps62868.pdf), device options, pin table, electrical conditions, §§8.4–8.6, output filter/BOM tables, and package land/stencil drawings; [TI TPS62864 Rev C](https://www.ti.com/lit/ds/symlink/tps62864.pdf), corresponding electrical and register tables. Full PDFs/text are preserved in the shared reference directory; the QFN source land drawing was rendered and visually checked.
