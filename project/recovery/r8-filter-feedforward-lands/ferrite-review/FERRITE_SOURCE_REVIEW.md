# FB202–FB210: bounded ferrite source review

2026-10-03. Read-only review of the active recovery physical candidate. Constraints remain 38 × 38 mm, six layers, components on top, and provisional 85°C enclosed air. No CAD, BOM or placement change was made.

**Murata BLM15PX121SN1D can be retained as one conditional source-land candidate for FB202, FB203, FB204, FB205, FB206, FB207, FB208, FB209 and FB210. No reference is electrically qualified.** Available evidence does not require a second MPN. Actual branch maximum, transient and hot-current envelopes are not established; the K230 guide supplies design-current budgets only. FB206 has an additional identified load that the guide subtotal does not bound.

## Branch-specific DC screen

Connections and capacitor refs below were extracted from the active master, not the older triage tables. MIPI currents are taken once per named supply/module row, not multiplied by the two package balls; their peak envelope still needs confirmation. The PMU value sums its separate RTC and LDO rows.

The upstream static minima are CORE 0.788299 V, 1V8 1.764477 V and 3V3 3.245130 V. They were recalculated from the active 3.32k/10k, 20k/10k and 45.3k/10k dividers using the existing conditional total resistor error ±0.70%, PWM feedback ±1% and conservatively signed ±50 nA FB leakage model. They reproduce the existing screen to 10⁻¹² V. PWM operation, load regulation and the total mission-profile resistor allowance remain conditions, not board measurements.

| Ref | Downstream net / SoC balls | Guide mA | Local caps | Before bead, mV | Bead drop, mV | Residual, mV |
|---|---|---:|---|---:|---:|---:|
| FB202 | AVDD0P8_PLL / G11 | 120 | C234 | 68.299 | 8.400 | 59.899 |
| FB203 | AVDD0P8_MIPI / N6,R8 | 100 | C235,C246 | 44.299 | 7.000 | 37.299 |
| FB204 | VAA_DDR / K15 | 10 | C236 | 90.477 | 0.700 | 89.777 |
| FB205 | AVDD1P8_USB / F9 | 60 | C237 | 90.477 | 4.200 | 86.277 |
| FB206 | AVDD1P8_PMU / F14,F15 | 20 + unknown | C238,C239 | 90.477 | 1.400 + unknown | 89.077 − unknown |
| FB207 | AVDD1P8_MIPI / N7,R9 | 30 | C240,C245 | 90.477 | 2.100 | 88.377 |
| FB208 | AVDD1P8_ADC / F8 | 10 | C241 | 144.477 | 0.700 | 143.777 |
| FB209 | AVDD1P8_CODEC / F7 | 100 | C242 | 144.477 | 7.000 | 137.477 |
| FB210 | AVDD3P3_USB / E9 | 50 | C243 | 175.130 | 3.500 | 171.630 |

“Before bead” is regulator static minimum minus the branch's minimum allowed voltage. Drop uses the published 0.070 Ω post-test DCR at the manufacturer's ordinary measurement conditions. **It is not an 85°C/125°C DCR guarantee.** Residuals must jointly cover shared upstream loss, local wiring, ripple, load steps, filter response and unmodeled error. No portion has been allocated solely to the bead. Do not add these margins to the existing shared-rail budgets or spend them independently. The JSON also carries 0.055 Ω initial and a purely conditional 0.100 Ω hot-ceiling scenario.

FB202 and especially FB203 require separate low-voltage drop/noise review. FB204 is the K230 DDR PLL supply, not external DRAM power. FB205/FB210 are PHY rails, not USB VBUS. FB206 additionally supplies R401 → PMU_INT4_AUTO_START → U1.C12 GPIO68/INT4; its pad/pull-down current is not bounded here. FB203/FB207 retain MIPI 0.8 V-before-1.8 V sequencing; FB206 retains the common RTC/LDO filtered net. ADC/PLL/CODEC noise and precision requirements remain distinct even though the physical candidate is common. All listed capacitors are currently nominal 100 nF candidates; effective capacitance and filter adequacy remain unqualified.

## Exact source geometry and thermal limits

Murata reference specification JENF243A_0018AR-01 pp3/4/9 was visually rechecked. The exact MPN has 120 Ω ±25% at 100 MHz, initial/post-test DCR maxima 0.055/0.070 Ω, body 1.00±0.05 × 0.50±0.05 × 0.50±0.05 mm and no polarity. Its published rating is 2 A at 85°C ambient, linearly derated to 1.1 A at 125°C. Neither rating qualifies operation beside the K230 in an 85°C enclosure. Local heat from nearby components, copper heating and actual current/inrush remain gates. The source warns against large inrush beyond rating and calls for heat management near hot parts.

Page 9's power-family drawing gives inner gap a=0.4 mm, outer span b=1.2 mm and exposed width c=0.5 mm. Derived exposed lands are 0.4 × 0.5 mm at x=±0.4 mm. **Copper width d is separate from exposed width c:** use the 2.2-A-or-lower row for this 2 A part: d=1.2/0.7/0.5 mm for 18/35/70 µm copper. Preserve resist-covered shoulders and continuing adequate copper. Do not select the smaller current row merely because the application table says 120 mA.

The JSON preserves all three foil cases. Mask expansion, exact paste aperture, courtyard and process approval are unset. The historical 1.8 × 1.7 / 1.8 × 1.2 / 1.8 × 1.1 mm reservations are explicitly hypothetical assembly sensitivities, not manufacturer courtyards. No six-layer copper thickness was selected. The older eight-layer, 35 µm proposal is not evidence approving this six-layer board.

Quantitative biased complex impedance is still missing. The exact SimSurfing page was reached in the cloud browser, but its explicit software-license AGREE was not accepted. The PDF supplies no guaranteed impedance-vs-bias/temperature curve. No attenuation, resonance/damping or switching-ripple pass is inferred from the 100 MHz nominal rating. This is the stopping point for electrical selection until actual load bounds and those data/models or measurements exist.

## Sources and deliverables

- [Murata exact-family reference specification](https://pim.murata.com/asset/pim4/ferriteBeadInductortypefilter/ENFA0018_PDF_FERRITEBEADINDUCTORTYPEFILTER?lastModifiedDatetime=20260520151432), SHA-256 26e3632f29268632a2ae03ce1b86b971044e76f3b1ad7dbe24eb5c39f4f6c5ee, matches the previously archived report
- [K230 hardware guide](https://github.com/kendryte/k230_docs/blob/main/en/00_hardware/K230_Hardware_Design_Guide.md), retrieved Markdown SHA-256 19e7243c50197a4835b9f85ca51c3fc9abd52ca9d353c6a92ddc8eaf9a3384f4; power recommendations and power-up sequence
- [TI TPS6282x](https://www.ti.com/lit/ds/symlink/tps62827.pdf), SHA-256 8a309f2a40486a380242d3f178eb4bda3ef4dca3deca647fa82f763d14866f63; p5 and §8.2.2.2
- [JLCPCB C88970 exact listing](https://jlcpcb.com/partdetail/MurataElectronics-BLM15PX121SN1D/C88970) is searchable. MOQ1 and live stock were not exposed in the retrieved page and are not verified; no order was placed
- [Murata exact model page](https://ds.murata.com/simsurfing/blm.html?oripartnumbers=%5B%22BLM15PX121SN1D%22%5D&partnumbers=%5B%22BLM15PX121SN1%22%5D&rgear=suaykx&rgearinfo=com), quantitative bias data not acquired

`source-manifest.json` records source hashes and boundaries. `geometry-contract.json` describes conditional manufacturer geometry without generating a footprint. `branch-contracts.json` includes exact nodes, voltage windows, uncertainty and all three DCR scenarios; `branch-summary.csv` provides the short screen. `validation.json` and `build_review.py` record reproducible endpoint, blank-footprint, source-hash and arithmetic checks. Manufacturer originals/screenshots are excluded from this deliverable directory.
