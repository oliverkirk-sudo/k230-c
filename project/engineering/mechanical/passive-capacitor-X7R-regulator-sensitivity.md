# X7R regulator capacitor sensitivity

Status: unqualified screening candidate only. No CAD, BOM or geometry change. All proposed parts are X7R, rated through 125 C; X5R is excluded under the provisional 85 C enclosure-air condition.

The source snapshot has 253 references and 152 capacitors. Its dense reservation is 1043.50 mm². This report evaluates only the six regulator input and output banks; other reservations remain provisional.

## Finding

One 22 µF CL31B226KPHNNNE per TPS6282xA input retains the 3 µF effective-capacitance floor in the extended arithmetic screen. The two TPS62864 inputs retain two of that part each. A tempting pair of 10 µF 0603 outputs fails once the manufacturer’s AC-amplitude curve is included. The coherent candidate therefore uses 17 of the 22 µF 1206 parts and four CL10B106MQ8NRNC 10 µF 0603 parts, the latter in parallel on 3.3 V. This changes the reviewed group from 22 to 21 capacitors; total capacitor count would become 151.

The candidate’s weakest screened margin is only 2.74%. It is a useful area and capacitance sensitivity, not a release-ready selection. A stronger count fallback is included below.

## Manufacturer evidence and factors

- [CL31B226KPHNNNE](https://product.samsungsem.com/mlcc/CL31B226KPHNNN.do): 22 µF, 10 V, ±10%, X7R, 1206; body 3.2 × 1.6 × 1.6 mm, ±0.2 mm.
- [CL10B106MQ8NRNC](https://product.samsungsem.com/mlcc/CL10B106MQ8NRN.do): 10 µF, 6.3 V, ±20%, X7R, 0603; body 1.6 × 0.8 × 0.8 mm, ±0.2 mm. TI lists this exact part in TPS62864 table 9-2 as an input component.

The original four-factor screen used temperature retention of 0.85. The official temperature-under-bias curves show retention ratios of 0.8272 at 5 V for the 22 µF part and 0.8126 at 3.15 V for the 10 µF part, relative to their 25 C bias curves. This sensitivity uses 0.80 for temperature instead. It is not a proven worst-case bound over all voltages.

The separate official AC-amplitude curves reach −16.22% and −20.52%. The DC-bias curves were measured at 0.5 Vrms/120 Hz and 1 Vrms/1 kHz respectively, so their values should not be assumed to hold at small switching ripple. Apply illustrative AC factors of 0.83 and 0.79 in addition to initial tolerance, 0.80 temperature, 0.90 aging and 0.90 model reserve. The two 10% reserves are unqualified assumptions. Separate typical curves do not form a guaranteed combined-condition model; lifetime, lot spread, actual AC level and frequency remain open.

## Coherent candidate screening

| Bank | Parts | Stress voltage | Screened µF | Floor µF | Margin |
|---|---|---:|---:|---:|---:|
| Each TPS6282xA input | 1 × 22 µF | 5.500 V | 6.854 | 3 | 128.5% |
| Each TPS62864 input bank | 2 × 22 µF | 5.500 V | 13.707 | 8 | 71.3% |
| Each CPU/KPU output bank; capacitor-only converter endpoint | 3 × 22 µF | 1.675 V | 31.252 | 30 | 4.2% |
| 0.8 V output with illustrative +5% | 1 × 22 µF | 0.840 V | 10.826 | 10 | 8.3% |
| 1.1 V output with illustrative +5% | 1 × 22 µF | 1.155 V | 10.709 | 10 | 7.1% |
| 1.8 V output with illustrative +5% | 1 × 22 µF | 1.890 V | 10.274 | 10 | 2.7% |
| 3.3 V output with illustrative +5% | 4 × 10 µF | 3.465 V | 10.697 | 10 | 7.0% |

The 1.675 V endpoint is a capacitor stress screen, not permission to drive K230 at that voltage. The +5% fixed-output screens are illustrative voltage budgets. At 1.155 V, the two-10 µF option falls to 7.987 µF with the extended factors and is rejected. A single 22 µF at 3.465 V falls to 8.814 µF and is also rejected.

## Exact land evidence and assembly sensitivities

| Part | Recommended total copper span | Pad width | Midpoint copper envelope | Max land + 0.25 mm each side, rounded | Midpoint + 0.10 mm each side |
|---|---|---|---|---|---|
| 22 µF 1206 | 4.02–4.38 mm | 1.74–1.86 mm | 4.20 × 1.80 mm | 4.90 × 2.40 mm | 4.40 × 2.00 mm |
| 10 µF 0603 | 2.15–2.45 mm | 0.95–1.05 mm | 2.30 × 1.00 mm | 3.00 × 1.55 mm | 2.50 × 1.20 mm |

These are the manufacturer’s reflow tables for the exact body-tolerance rows, visually checked in the specification PDFs, pages 33 and 34. The 0603 ±0.20 mm row differs from the previous 4.7 µF ±0.15 mm row. Midpoint actual copper-pad areas are 4.500 and 1.580 mm²; bounding land envelopes include the gap and are 7.560 and 2.300 mm². Courtyard clearances are stated assumptions, not universal manufacturer minima.

| Group | Count before → candidate | Baseline mm² | Conservative candidate mm² | Delta mm² |
|---|---:|---:|---:|---:|
| Four TPS6282xA input pairs become one 22 uF each | 8 → 4 | 22.88 | 47.04 | +24.16 |
| Two TPS62864 input pairs retain two 22 uF each | 4 → 4 | 11.44 | 47.04 | +35.60 |
| CPU and KPU output banks retain three 22 uF each | 6 → 6 | 17.16 | 70.56 | +53.40 |
| 0.8 V, 1.1 V and 1.8 V outputs use one 22 uF each | 3 → 3 | 15.12 | 35.28 | +20.16 |
| 3.3 V output uses four 10 uF 0603 in parallel | 1 → 4 | 5.04 | 18.60 | +13.56 |

| Area method | Reviewed group mm² | Delta against group baseline | Whole-board partial-population sensitivity |
|---|---:|---:|---:|
| conservative rounded maximum land plus 0p25 | 218.52 | +146.88 | 1190.38 mm² |
| midpoint land plus 0p10 | 161.60 | +89.96 | 1133.46 mm² |
| manufacturer midpoint copper envelope only | 137.72 | +66.08 | Not a courtyard total |

The available area after the assumed perimeter band is 1156 mm². These totals retain every other current provisional reservation; they do not constitute a complete source-qualified capacitor BOM or routed-fit result. Memory bulk, local decoupling and unresolved added bulk may still enlarge them.

## Stronger count fallback

A fallback keeps the same eight 22 µF inputs, uses four 22 µF per CPU/KPU, and uses three, three, four and five 10 µF on 0.8, 1.1, 1.8 and 3.3 V. Its weakest output screen margin is 19.81%. It raises the reviewed group from 22 to 31 parts and the total capacitor count to 161.

- conservative rounded maximum land plus 0p25: 257.91 mm² for the reviewed group, +186.27 mm² delta, 1229.77 mm² partial-population board total
- midpoint land plus 0p10: 185.80 mm² for the reviewed group, +114.16 mm² delta, 1157.66 mm² partial-population board total

This fallback is not asserted to be an area optimum. Its different nominal output totals are not exact tested rows in TI’s LC tables. The arithmetic shows the cost of a stronger screen; it does not establish stability or qualification.

## Qualification limits

[TPS6282xA section 8.2.2.5](https://www.ti.com/lit/ds/symlink/tps62827.pdf) specifies 3 µF effective input and 10 µF effective output for these A variants. [TPS62864 section 9.2.1.2.5](https://www.ti.com/lit/ds/symlink/tps62864.pdf) says 8 µF effective input is sufficient for most applications and recommends at least 30 µF effective output. The project retains those floors. Nominal LC table entries do not guarantee an application whose combined derating exceeds the footnote range. Four 10 µF at 3.3 V, and the stronger fallback banks, require actual loop-stability and transient checks.

Capacitor surface temperature includes self-heating and nearby heat sources. A 125 C rating does not prove thermal margin in an 85 C sealed enclosure. Apply the manufacturer’s voltage/temperature derating guide and verify local temperatures, peak voltage, ripple current, lifetime, layout, and installed capacitance. Neither candidate is selected for manufacture.

The older X7R and historical X5R reports remain unchanged and retain their own earlier snapshots. The separate 254-reference high-temperature variant is outside this area comparison. Source URLs, original-file hashes, complete numeric curves, factor sequences, and source-master hash are retained in the accompanying JSON.
