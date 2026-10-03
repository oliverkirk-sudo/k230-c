# TF clock idle-bias recovery review

2026-10-01. Scope: restored v12 compact archive, schematic revision **HT-DRAFT13**. The lost HT18 proposal is background, not design evidence. This review changes no CAD, component population, firmware, OTP or external interface.

## Decision

**The floating CLKA defect is independently confirmed. R574 = 10 kΩ from TF_HOST_CLK to GND is a supportable candidate correction, but the official sources do not close its worst-case electrical acceptance.** Restore it only as a documented candidate if the design owner proceeds. Do not label this a recovered, validated HT18 result.

The minimal proposal and exact preservation rules are in `proposed-netlist-delta.json`. Freshly downloaded official NXP NVT4858 Rev. 2.4 bytes match the historical source SHA-256 exactly: `860baa17e52fb658dcd98bf911f81600ecbd4f3133b560c9e4696af17bc28385`. Source identifiers, URLs, revisions, page references and local evidence hashes are in `source-manifest.json`. Raw vendor PDFs are separately under `/workspace/shared/k230-reference/tf-clock-review/`.

## Restored circuit evidence

Both the restored master XML and the fresh recovery export agree:

| Net or pin | Exact recovered connection |
|---|---|
| TF_HOST_CLK | U11.1 (TMUX1574 S1B), U95.5 (NVT4858 CLKA), nothing else |
| MMC0_CLK | U1.A5, U11.2 (D1) |
| EMMC_CLK | U11.16 (S1A), U3.M6, R571.1 |
| TFCARD_CLK | U95.8 (CLKB), J1.21 |
| U95 supply | pin 15 VDD1P8; pin 14 VDD_3V3; pin 7 GND |
| U11 supply/control | pin 14 VDD_3V3; pin 6 GND; pin 13 GLOBAL_DISABLE; pin 15 MODE_TF |
| U95.6 CLK_FB | Explicit no-connect; singleton unconnected net |
| R574 | Absent |

The selector's S1B branch opens with MODE_TF=0 or GLOBAL_DISABLE=1. U95 is not mode-disabled: its supply pins remain on the ordinary 1.8 V and 3.3 V rails. Thus an active translator can be left with an undriven CLKA in eMMC mode, during storage inhibition, and whenever the selected host clock is itself high impedance. This is a topology defect, not evidence that a real board has emitted a spurious clock.

The broad “integrated pull-up and pull-down resistors” feature line does not supply an idle bias for CLKA. Figure 2 shows no CLKA shunt; the explicit CLKA footnote controls that interpretation. Automatic bidirectional CMD/DAT behavior must not be applied to the clock channel.

## Manufacturer contract

The following is a compact source ledger; derived consequences are separated below.

| Authority | Relevant contract |
|---|---|
| NXP NVT4858, Rev. 2.4, pp. 6, 8–11, 20 | HK/XQFN16: CLKA pin 5 input; CLKB pin 8 output; CLK_FB pin 6 output. Clock channels are unidirectional, without the data-channel holding mechanism. CLKA is high impedance; no internal bias is specified. |
| Same, pp. 10–15 | VCCA 1.08–1.98 V, VCCB 1.62–3.6 V. Input low ≤0.35 VCCA; high ≥0.65 VCCA. No maximum CLKA input-leakage parameter is given. CMD/DAT pulls are 49–91 kΩ. |
| Same, pp. 10–14 | VCCB auto-enable/disable thresholds: 1.62/0.8 V with valid VCCA. Shutdown makes CLKA, CLK_FB and CLKB high impedance. Host/card input voltages remain supply-referenced. |
| Same, pp. 16–18, 22 | At 1.8/3.3 V: host-to-card delay 5 ns maximum under stated conditions. Test loads: card ≤15 pF, host ≤7 pF, 1 MΩ load, 50 Ω source. Transition rows are condition-specific; not an unconditional CLKA slew specification. |
| Same, p. 4 | NVT4858HKZ ambient operating range −40 to +85°C. |
| TI TMUX1574, SCDS391C, pp. 6–7, 24 | EN=1 disconnects all channels. EN=0 selects A/B with SEL=0/1. Switch-OFF leakage ±100 nA at specified test voltages; VDD=0 leakage ±2 µA over specified range. RON maximum 4.5 Ω at the stated 8 mA test. |
| Vishay CRCW0201 e3, document 20052, 21-Sep-2022, pp. 1–3 | CRCW020110K0FKED follows the manufacturer code: 10 kΩ, F ±1%, K ±100 ppm/K, ED packaging. 50 mW at 70°C with derating and film-temperature limits; 30 V maximum element voltage. |

Official sources: [NXP](https://www.nxp.com/docs/en/data-sheet/NVT4858.pdf), [TI](https://www.ti.com/lit/ds/symlink/tmux1574.pdf), [Vishay](https://www.vishay.com/docs/20052/crcw0201e3.pdf). Source-family suitability is distinct from exact orderability, stock, life-cycle and assembled-board qualification.

## Conditional static proof and missing leakage bound

Use the existing project screening requirement of **9–11 kΩ total resistance** for this 10 kΩ candidate. That ±10% band is an acceptance requirement including initial tolerance, temperature, assembly, aging and environment; it is not a manufacturer-guaranteed mission-life result. It is deliberately broader than the initial ±1%/100 ppm grade.

For total positive current injected into the idle node, the necessary DC condition is:

`I_total_positive × R_max + V_ground_error < 0.35 × VCCA_min`.

With ground error set to zero only for calculation:

| Calculation | Full NVT operating range | Existing upstream 1V8 static-rail screen |
|---|---:|---:|
| VCCA minimum | 1.08 V | 1.764476615 V |
| VIL ceiling | 0.378 V | 0.617566815 V |
| Total allowable positive injection at 11 kΩ, zero remaining margin | 34.3636 µA | 56.1424 µA |
| Remainder after a provisional 100 nA switch term | 34.2636 µA | 56.0424 µA |
| Resistor high-state current upper bound | 220 µA at 1.98 V/9 kΩ | 204.011 µA at 1.836094613 V/9 kΩ |
| Resistor full-high DC power | 0.4356 mW | 0.374583 mW |

The 100 nA TI contribution alone develops 1.1 mV across 11 kΩ. TI specifies it at VS/VD=0.2/0.8 VDD; using it at the actual near-zero idle node is an explicit applicability assumption, not a separately characterized endpoint bound. The rail screen excludes distribution drop, ripple and transients. Finite noise margin and ground movement reduce every listed current budget.

**The missing term is U95 CLKA leakage over the operating and partial-power corners.** NXP's Table 11 gives no IIH/IIL/Ioff limit. Its 15 µA static supply-current row is measured with all inputs HIGH and cannot be relabeled as CLKA leakage with this input LOW. The 7 µA standby row is likewise not that guarantee. Neither the words “high impedance” nor a drawing establish a numerical leakage maximum. Board contamination/leakage and input protection paths are additional terms. The result is therefore a useful available-current budget, not proof that actual worst-case injection fits it.

Even the candidate resistor's low dissipation does not establish a sealed-85°C board temperature. U95 remains an 85°C ambient-rated component; the resistor does not make it a 105/125°C solution.

## Active source loading and edge-rate limits

R574 is a shunt pull-down on the host branch, not a series termination. In selected TF mode the K230 clock driver must source its high-state current plus NVT input leakage and dynamic capacitive charging. A provisional 4.5 Ω TMUX path at 220 µA adds only 0.99 mV DC drop, but the published RON test conditions and the K230 pad's actual VOH/current/drive setting still need applicability checks. This review does not invent a K230 minimum drive guarantee.

An ideal rail-to-rail Thevenin driver would require total source resistance below 4.846 kΩ merely to reach 0.65 VCCA against a 9 kΩ shunt. That is an algebraic DC ceiling, not an acceptable clock-driver impedance or edge-rate target. Actual high/low waveforms at U95.5 and J1.21 must satisfy receiver thresholds with noise margin, duty-cycle, pulse-width, rise/fall, overshoot and propagation constraints.

During active push-pull clocking the time constant is approximately `(R_source + R_switch) || R574` times node capacitance. Do not calculate normal clock rise time as `10k × C`; conversely, do not assume the small DC current proves timing. Added footprint/stub capacitance, NVT input capacitance, TMUX capacitance and interconnect remain relevant.

When a HIGH source disconnects, R574 alone may discharge the node slowly. Illustrations with 11 kΩ and **assumed**, not measured, total capacitance:

| Total C | Time constant | Fall from VCCA to 0.35 VCCA, no leakage | Transit 0.65 to 0.35 VCCA |
|---|---:|---:|---:|
| 10 pF | 110 ns | 115.48 ns | 68.09 ns |
| 20 pF | 220 ns | 230.96 ns | 136.19 ns |

TI's COFF maximum 6 pF and NXP host I/O maximum 4 pF under their individual measurement conditions are not a finished-board capacitance extraction or a clock-input hysteresis guarantee. For nonzero leakage use `V(t)=I_leak R + (V0−I_leak R) exp(−t/RC)`; decay time diverges as the final voltage approaches the low threshold. Stop the clock LOW before opening a live path wherever the eventual sequencing allows, and retain cold-only selection. No glitch-free switching claim follows from a pull-down or TMUX break-before-make.

During eMMC traffic, off-channel capacitive feedthrough from MMC0_CLK is also material. A 10 kΩ bias removes an indefinite floating DC state but is not a low-impedance high-frequency clamp. TI off-isolation values use a 50 Ω load and cannot certify this 10 kΩ/CMOS node. Verify induced excursions at CLKA and unintended pulses at J1.21 with worst-case eMMC activity, rails and temperature. CLKA Schmitt hysteresis is not specified in this NXP datasheet.

The NXP transition-time rows on pp. 16–18 must be kept with their stated supply, temperature and threshold definitions. Figure 6 describes output transitions; the table does not establish that a slowly discharged CLKA is guaranteed glitch-free. Similarly, the 5 ns propagation row at 25°C does not close complete K230+switch+translator+carrier timing over temperature. CLK_FB may remain no-connect when unused, as NXP permits, but bypassing feedback leaves the end-to-end read timing budget to be proved. Keep TF at the existing fixed-3.3 V Default/High-Speed 25/50 MHz policy; this resistor authorizes no UHS change.

## Partial power and the external core interface

With both translator supplies valid, an adequately low CLKA should produce a driven-low CLKB by the documented clock channel. This is the intended eMMC-mode idle behavior after adding and qualifying R574. It remains a core-board obligation because U95 drives the exposed **J1.21 TFCARD_CLK** net; the external TF card/socket is not placed on this core and must not be silently counted as an internal component.

With either NVT supply at GND in the documented shutdown cases, CLKB is **high impedance**, not driven LOW. An upstream pull-down cannot cross a disabled buffer to guarantee the output's DC voltage. If all-power-state LOW is required at the connector, that needs a separate reviewed output-bias/isolation contract, with its own active loading and card-power consequences. No such additional resistor or interface change is proposed here.

Shutdown does not equal unrestricted fail-safe input tolerance. NXP's recommended input range is −0.3 V to the respective supply +0.3 V, with host-side steady-state voltage additionally limited to 1.98 V. It does not publish a numerical partial-power Ioff contract. Do not infer arbitrary externally powered card signals are safe while a translator rail is absent, or that the TMUX's wider signal range makes CLKA 3.3 V tolerant. Intermediate rail ramps, reset/brownout, card power independent of the core, and reverse leakage need acceptance evidence. TI's VDD=0 leakage term would contribute 22 mV at 11 kΩ by itself, but that is not an active-translator logic proof. U11 VDD and U95 VCCB share VDD_3V3, so a permanently powered U95 card rail alongside a separately dead switch supply is not a normal independent stable state of this netlist.

The restored R528 qualification strap stays DNP. Its storage-release inhibition does not disable powered U95 or itself cure the CLKA float. This review closes neither first-ROM voltage behavior nor ROM media selection, carrier power/detect, hot insertion, physical layout, bootability or the overall temperature gate.

## Minimal implementation proposal and acceptance checks

If adopted as a candidate, add exactly one populated resistor **R574.1=TF_HOST_CLK, R574.2=GND**, nominal 10 kΩ, candidate CRCW020110K0FKED. Place it on the core top side near U95.5 with a short ground return. Keep all existing nets/pins, U95 supplies, CLK_FB NC, J1.21 mapping, DNP straps and cold-mode behavior unchanged. The restored project has no source-validated CRCW0201 native footprint; physical land-pattern and assembly acceptance remain open rather than borrowing an unrelated resistor footprint.

`python3 recovery/tf-clock-review/verify_review.py` checks the original topology, exact in-memory two-pin proposal, negative controls, source-derived arithmetic and byte preservation of all 367 CAD files. It writes `review-verification.json`. It is a design-review test, not a fabricated-board measurement, SPICE validation or actual CAD implementation. A future exported XML can be checked with `--candidate PATH`; that optional route has not been run on an implemented candidate.

Before electrical acceptance, require:

1. Bound total positive leakage at U95.5 against the budget with explicit operating-range, ground-noise and resistor-life margin; close NXP's missing leakage term through acceptable evidence or qualified measurements and a justified coverage plan
2. Check active K230 high/low drive and CLKA/CLKB waveforms, timing and load at identification, 25 MHz and 50 MHz; include low/high rail and temperature corners, representative cards and the actual carrier
3. With eMMC selected and worst-case eMMC activity, verify CLKA stays below its low threshold with margin and J1.21 has no unintended clocks; include startup, inhibition, reset and brownout observations
4. Validate documented shutdown high impedance and actual partial-power injection limits; explicitly record which interface states are guaranteed LOW and which are only high impedance
5. Keep production/boot/thermal release gates open until separately closed. No hardware testing occurred in this recovery review
