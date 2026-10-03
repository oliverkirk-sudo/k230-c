# Reviewed 22 µF input-bank option, bound to R10

**The proposed eight-capacitor option has useful arithmetic margin and is a plausible validation candidate. It is not electrically qualified or adopted.** Fresh primary-data calculations give **6.925 µF per part at the 5.5 V screen** after the explicit allowances below. Two parts therefore screen at **13.849 µF against 8 µF** for U22/U23; one part screens at **6.925 µF against 3 µF** for each other regulator.

This result is an engineering sensitivity using typical curves and assumptions, not a guaranteed combined-condition minimum. Baseline CAD, BOM, count and values remain unchanged.

## Exact scope and proposed reference plan

The decision baseline is the published **R10 master**, SHA256 `eb25c89c243242b4279e56600216a079ab8e12baf595730085ec45f3da8655b4`. The original R8 master hash `bbb9c482b05e066ba6d9ee046218abe1227d5e7918d8ebe4e1a7bcb358256183` is retained separately. Their whole files differ. A scoped equality bridge confirms identical values, symbol identities, footprints and pin nets for all **28 input capacitors, regulators and divider/VSET resistors**; the six local 100 nF bypass components also match.

Only one exact candidate was assessed: **Samsung CL31B226KPHNNNE, 22 µF ±10%, 10 V, X7R, 1206/3216, −55 to +125°C**.

| Regulator / output rail | Baseline | Proposed surviving refs, each 22 µF | Proposed removal | Local Ceff criterion |
|---|---|---|---|---:|
| U21 TPS62827ADMQ / VDD0P8_CORE | C203/C204, 2×10 µF | C203 | C204 | 3 µF |
| U22 TPS628640BYCGR / VDD0P8_CPU | C210/C211, 2×10 µF | C210/C211 | None | 8 µF |
| U23 TPS628640BYCGR / VDD0P8_KPU | C216/C217, 2×10 µF | C216/C217 | None | 8 µF |
| U24 TPS62826ADMQ / VDD1P1_DDR_IO | C220/C221, 2×10 µF | C220 | C221 | 3 µF |
| U25 TPS62825ADMQ / VDD1P8 | C225/C226, 2×10 µF | C225 | C226 | 3 µF |
| U26 TPS62826ADMQ / VDD_3V3 | C230/C231, 2×10 µF | C230 | C231 | 3 µF |

This plan changes twelve input components to eight, all retaining pin 1=VIN_5V and pin 2=GND. It preserves C205/C209/C215/C222/C227/C232 and every output capacitor. The lower-numbered survivor is an administrative proposal; physical placement and current-loop quality must determine the eventual implementation.

[TI TPS6282x SLVSEF9I](https://www.ti.com/lit/ds/symlink/tps62827.pdf), §8.2.2.5 p14, recommends the 3 µF minimum for most applications. [TI TPS62864 SLVSEI1C](https://www.ti.com/lit/ds/symlink/tps62864.pdf), §9.2.1.2.5 p22, describes 8 µF as sufficient for most applications; it is retained here as the design floor, not recharacterized as a universal silicon minimum.

The actual fixed dividers give ideal nominal outputs of **0.7992, 1.1196, 1.8000 and 3.3180 V** for U21/U24/U25/U26. These are distinct from rounded rail names. Existing 56.2 kΩ VSET resistors select 0.80 V startup for U22/U23, with later I²C changes possible. All input capacitance calculations use **VIN**, not those output voltages. No divider or output-bank changes are proposed.

## Fresh primary evidence and factor status

The [Samsung product page](https://product.samsungsem.com/mlcc/CL31B226KPHNNN.do) supplies the exact packaging suffix and embedded numeric curves. Same-day source files were shared with the output-capacitor review, independently reparsed and recomputed here. The exact specification supplied by the manufacturer is issued **April 15, 2021**; its body and land drawings were visually checked. Document hashes and retrieval information are in `source-manifest.json`. The older 6.85 µF screen was not used as an input or guarantee.

| Factor or evidence | This assessment | Evidentiary limit |
|---|---|---|
| DC bias | 15.093 µF typical at 5 V; 14.159 µF at 5.5 V | 25°C, 120 Hz, 0.5 Vrms; 5.5 V interpolated from nearby primary points |
| Initial tolerance | ×0.90 | Manufacturer initial ±10%; combining it with typical curves is still screening |
| Temperature | ×0.80 | Explicit allowance; observed worst ratio within the 5 V biased-temperature curve is 0.83466, but no corresponding guaranteed 5.5 V bound exists |
| AC amplitude | ×0.838587 | Separate zero-DC typical curve minimum normalized to its 0.5 Vrms value; independence from bias/temperature is unproven |
| Aging | ×0.90 | Illustrative allowance; no application lifetime/aging model established |
| Model and lot reserve | ×0.90 | Illustrative reserve; no statistical production guarantee |

The AC curve minimum is −16.220% at 22.14 mVrms. Its interpolated value at 0.5 Vrms is −0.094%; normalization gives the factor above. Using its value at 1 Vrms would mismatch the DC-bias test condition. The unbiased temperature curve uses **0.35 Vrms**, another reason not to interchange all graphs.

The **5 V biased-temperature curve** is direct combined typical evidence at 120 Hz/0.5 Vrms: its worst point at 125°C corresponds to 12.485 µF. It supports investigation of this part, but does not cover 5.5 V, small-ripple AC, lifetime and production corners together. Separate 25°C curves differ slightly in normalization.

| Illustrative result | 5 V | 5.5 V |
|---|---:|---:|
| One 22 µF part after all listed factors | 7.381 µF | 6.925 µF |
| Two parts after all listed factors | 14.763 µF | 13.849 µF |
| Single margin above 3 µF | 146.0% | 130.8% |
| Pair margin above 8 µF | 84.5% | 73.1% |

The baseline Murata 10 µF part still lacks a combined Ceff bound. No numerical improvement ratio over its actual operating capacitance is claimed. The proposed option has margin within the declared screen; hardware/model qualification remains open.

## Source lands, body and matched area cost

The exact part body is **3.20±0.20 × 1.60±0.20 × 1.60±0.20 mm**, with maximum dimensions 3.4×1.8×1.8 mm. The source's **p33 metric 3216 / ±0.20 mm reflow row** gives a=1.64–1.76, b=1.19–1.31, c=1.74–1.86 mm. Its midpoint yields two **1.25×1.80 mm pads at x=±1.475 mm**, with a **4.20×1.80 mm copper envelope**. Reliability-test substrate dimensions are not the assembly land recommendation.

Baseline footprints remain unassigned. For a matched comparison, use the independently verified Murata 0603 midpoint/body reservation from the original input-cap review, with the same illustrative clearance q around body plus lands:

| Clearance q per side | Baseline: 12 Murata reservations | Option: 8 Samsung reservations | Net increase |
|---|---:|---:|---:|
| 0.10 mm | 36.00 mm² | 70.40 mm² | **+34.40 mm²** |
| 0.25 mm | 50.40 mm² | 86.48 mm² | **+36.08 mm²** |

Maximum body-only area grows from 21.60 to 48.96 mm²; maximum height rises from 1.0 to 1.8 mm. Fewer parts do not mean less occupied area. Mask expansion, paste aperture/stencil, courtyard, flexure controls and assembly yield remain unqualified process choices. These rectangles do not demonstrate packing or routing.

## Operating constraints before adoption

- **VIN and UVLO:** Check actual VIN at every IC, including ripple, ringing, startup and source removal. U21 requires at least 2.5 V; the other regulators require at least 2.4 V, with output headroom additionally required. All have a 5.5 V operating ceiling. A 5.5 V screening endpoint leaves no upward transient allowance. UVLO thresholds are not valid operating-voltage targets
- **TPS628640B falling VIN:** TI §10 p27 requires a fall **slower than 10 mV/µs when VIN drops below UVLO**. Test source/cable disconnection, brownout and all discharge/backfeed paths. More nominal capacitance alone does not prove compliance. The rising/falling UVLO ranges are 2.2–2.4 V / 2.1–2.3 V, respectively
- **Inrush and ramp:** Nominal input capacitance increases from **120 to 176 µF, +46.7%**. These capacitors load VIN before switching; regulator output soft-start does not limit their direct charging current. Validate source current limit, hotplug, overshoot, recovery and actual voltage-dependent charge
- **Ripple and transients:** Four banks would use one capacitor carrying the local pulse current. Verify RMS/peak current, ESR/ESL, frequency-dependent impedance, surface heating, simultaneous startup/load steps, CPU/KPU voltage changes and current-limit recovery. Equal Ceff is not equal current sharing or transient behavior
- **Current loops:** Preserve the six 100 nF bypass positions. Keep each local bank close to its regulator, with short/wide VIN and GND/PGND paths; use PGND correctly on U22/U23 and protect FB/VOS sensing from SW coupling. Shared remote capacitance cannot automatically replace local decoupling
- **Temperature and lifetime:** Validate actual MLCC surface temperature including self-heating and the intended life profile. Enclosure air or memory case temperature does not determine capacitor temperature. Samsung typical ripple graphs do not establish a guaranteed current rating at the converter's complete frequency spectrum

Parameterized ideal CCM ripple estimates using the actual divider values are in `proposed-reference-plan.json`; they are stress screens, not measured load budgets or capacitor-current qualification. Detailed supply and process gates are in `operating-constraints.json`.

**Decision:** retain this as a reviewable, margin-bearing input option. Adopt the eight-part reference/value plan only after an explicit decision and appropriate combined-capacitance, supply/current-loop, thermal and assembly validation. This review performed no CAD changes, purchase, supplier outreach or Library action.
