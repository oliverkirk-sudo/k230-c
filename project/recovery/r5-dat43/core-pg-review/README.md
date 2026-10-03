# CM-K230: CORE PG → EN electrical review

2026-10-03 · Read-only R3 review · No CAD/BOM/population changes

**Finding: the published limits give zero positive low-noise budget, not proof of functional failure.** Equality between a maximum output-low voltage and a maximum recognized input-low voltage is inclusive DC compatibility when the limits' conditions apply. It does not place the receiver in its unspecified input region. It leaves no positive allowance for ground displacement, coupled noise, or interconnect drop. Keep that distinction in subsequent reports; the earlier phrase “functional gap” must not be read as an observed failure.

TI expressly describes connecting TPS6282x PG to other converters' EN for sequencing. That supports the topology, but does not qualify this board's noise, ramps, wiring, loading or timing. No circuit change is mandatory solely because the limits meet at 0.4 V. Conversely, a requirement for positive worst-case margin cannot be declared met. [TI SLVSEF9I, §7.4.2, p10](https://www.ti.com/lit/ds/symlink/tps62827.pdf)

## Actual circuit

The active R3 `cad/recovery-physical-candidate/master.xml` has 254 references, 457 nets and 1,509 nodes. The net is named `CORE_PGOOD_5V`, not `PG_CORE`.

| Connection | Actual device/pin |
|---|---|
| Driver | U21 TPS62827ADMQ, pin 2 PG |
| Pullup | R203, 100 kΩ, to VIN_5V |
| CPU enable | U22 TPS628640BYCGR, E1 |
| KPU enable | U23 TPS628640BYCGR, E1 |
| DDR enable | U24 TPS62826ADMQ, pin 1 |
| 1.8 V enable | U25 TPS62825ADMQ, pin 1 |
| 3.3 V enable | U26 TPS62826ADMQ, pin 1 |

All six converters' VIN pins share VIN_5V. U21 EN is a separate CORE_ENABLE net with R204=10 kΩ to VIN_5V. There are no other receivers on CORE_PGOOD_5V. The extracted pin graph and exact input hash are in `review.json`.

## Applicable limits and calculation

- U21 PG: VOL ≤0.4 V at 1 mA. Recommended PG sink ceiling: 1 mA. EN: VIL ≤0.4 V, VIH ≥1.0 V. The electrical table covers −40…125°C and VIN 2.4…5.5 V, but U21's recommended VIN minimum is **2.5 V**. U24–U26 permit 2.4 V. No separate regulator-output-load restriction appears on the PG VOL row. PG leakage is ≤0.1 µA **at VPG=5.0 V**; the EN leakage limit of 0.1 µA is **at EN high**. [TI SLVSEF9I, pp4–5](https://www.ti.com/lit/ds/symlink/tps62827.pdf)
- U22/U23: VIL ≤0.4 V, VIH ≥1.0 V, EN leakage ≤0.1 µA; no row-specific leakage condition. The header applies VIN 2.4…5.5 V and −40…125°C. Their recommended VIN falling slew is limited to 10 mV/µs when crossing below UVLO. [TI SLVSEI1C, pp5–6](https://www.ti.com/lit/ds/symlink/tps62866.pdf)

Thus the common recommended static VIN envelope is 2.5…5.5 V, subject also to each converter's operating/thermal limits. Rated output-current ceilings for U21…U26 are respectively 4, 4, 4, 3, 2 and 3 A; this review does not establish actual rail demand or junction temperatures. This is a component envelope, not a claim that the carrier supplies that whole range correctly.

At the published endpoints, the low budget is **0.4 − 0.4 = 0 V**. The maximum is not the typical low voltage and is not proof that any actual sample reaches 0.4 V. No typical RON, linear current scaling, or improved low-current VOL is used.

Using the previous screen's conditional ±10% total resistor band, R203 is 90–110 kΩ. Its pullup alone can demand at most **61.111 µA** at 5.5 V, leaving 938.889 µA before the 1 mA sink ceiling. Receiver current sourced into a low net and board leakage still need bounds; the three TPS6282xA high-state leakage specifications cannot silently supply them.

A conditional sum of five 0.1 µA EN loads plus 0.1 µA PG leakage gives 66 mV drop through 110 kΩ. This is a useful screen, **not a full-VIN guarantee**: the PG test point is 5.0 V. More generally, at VIN=2.5 V the allowable total current drawn from the node before it falls to VIH=1.0 V is 13.636 µA. That is the required bound to establish, not a newly asserted leakage specification.

## Startup and partial power

The manufacturer's state table holds PG low in shutdown and UVLO above 0.7 V and releases it below 0.7 V. Its numerical VOL table must not be extended to every undervoltage point or to temperatures above 125°C. The shared VIN means there is no separately powered upstream pullup when the common input is truly absent. Receiver UVLO blocks conversion at low input voltage; this does not prove that every EN voltage is low throughout a ramp. [TI SLVSEF9I, §7.4 and Table 7-1](https://www.ti.com/lit/ds/symlink/tps62827.pdf)

U22/U23 have rising UVLO bounds 2.2–2.4 V and falling bounds 2.1–2.3 V. UVLO stopping/automatic restart is documented. [TI SLVSEI1C, §7.5 and §8.3.5](https://www.ti.com/lit/ds/symlink/tps62866.pdf)

An arbitrary-ramp proof still needs local VIN/GND tracking, source and receiver behavior between UVLO and recommended operation, any externally sustained residual rails/backpower, capacitance/rise time, and a required maximum response to a CORE fault. Typical blanking/deglitch delays are not guaranteed upper bounds. Reset/storage interlocks must be assessed separately from this enable-chain DC check.

## One bounded improvement candidate, held for qualification

If a positive margin requirement is adopted, the sole topology evaluated here is **TPS389001 powered directly from VIN_5V**, with existing U21 PG/R203 driving SENSE, MR tied to VIN_5V, CT open, and local 0.1 µF bypass. Its open-drain RESET would drive **all five** EN receivers through a new 220 kΩ pullup to VIN_5V. U21 PG and the receiver EN node must be separated. It has no dependency on delayed 1.8/3.3 V rails.

The source gives 1.15 V nominal falling / 1.157 V rising thresholds, ±1%; VOL ≤0.25 V at 0.4 mA for VDD≥1.5 V; operation over 1.5–5.5 V and −40…125°C; POR ≤0.8 V with VOL≤0.2 V at 15 µA. SENSE and RESET tolerate 0–5.5 V independent of supply. Below POR, RESET is undefined. Published startup and sense-response delays have no guaranteed maxima. [TI TPS3890, SLVSD65A, pp3–5,12,14](https://www.ti.com/lit/ds/symlink/tps3890.pdf)

The resulting **conditional static** budgets are 738.5 mV at SENSE low and 150 mV at receiver low. With ±10% on 220 kΩ, pullup-only sink is ≤27.778 µA at 5.5 V and ≤7.576 µA below 1.5 V; the POR budget leaves 7.424 µA for all other sources. At VIN=2.5 V, total output-node leakage must remain below 6.198 µA, and PG/SENSE leakage below 12.104 µA, to meet their respective high thresholds. These low budgets retain the published VOL maximum, without claiming a smaller VOL at the lighter load. Supply current must also be budgeted: the supervisor gives 6.5 µA maximum at VDD=5.5 V with zero RESET current, plus the separate pullup paths and bypass-capacitor charging; do not silently extend that supply-current test point. Exact conditions are retained in the JSON.

**This candidate is not an approved fix.** Its source leakage rows are also voltage-specific, low/undervoltage receiver loading remains open, and adding a supervisor changes fault and release timing. Guaranteed startup/partial-power behavior for every requested condition is not established. Its small package does not demonstrate physical fit or routing. Do not adopt it merely to turn a zero into a positive number.

## Disposition and reproducibility

Retain the existing circuit while recording the zero-margin gate precisely. Before changing it, define the required noise and timing budgets and close the listed supply/loading conditions. No vendor outreach is requested or performed.

Run `python build_review.py --project /path/to/r3/project`. The script reads the netlist, asserts the complete receiver graph/common VIN, reproduces arithmetic and verifies the netlist hash is unchanged. `verification.json` records those checks; it is not circuit simulation or hardware qualification. Source-table columns were visually checked. This package contains no vendor PDFs/screenshots.

The six-layer, 38 × 38 mm, 140-contact, top-only contract and default storage inhibit remain untouched. This review establishes no PCB placement, routing, assembly readiness, OTP action, or purchase.
