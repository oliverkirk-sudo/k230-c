# Capacitor candidate review

Status: manufacturer evidence and feasibility candidates only. No electrical release, manufacturing footprint, or routed fit is established. The frozen master and prior mechanical reports were not edited.

## Findings

The twelve 10 uF / 10 V input capacitors are on VIN_5V. The two three-capacitor 22 uF sets are on the 0.8 V CPU and KPU rails. The four nominal 47 uF positions serve 0.8 V, 1.1 V, 1.8 V and 3.3 V rails. The current baseline dense reservation total is 1028.21 mm2, including the latest L22/L23, R220, R561 and Y2 mechanical corrections; that total is not proof of routed fit.

Murata GRM188Z71A106MA73D verifies a 0603, 10 uF, 10 V X7R(MURATA) input option. Murata GRM21BZ70J226ME44L verifies a 0805, 22 uF, 6.3 V X7R(MURATA) output option. Both appear in the relevant TI application component tables, but their exact DC-bias curves were not recovered. Neither input nor output effective capacitance can therefore be signed off from the nominal values. The 22 uF maximum body width is 1.45 mm, already wider than the current 1.3 mm planning reservation.

Samsung CL32B476KQVVPNE provides a verified 47 uF, 6.3 V X7R 1210 option with an official numeric typical DC-bias curve. Its maximum body is 3.6 x 2.8 x 2.8 mm, exceeding the current 2.8 x 1.8 mm planar reservation before lands or clearance. This does not mean 47 uF nominal must be retained: effective capacitance is the controlling output requirement.

A smaller curve-bearing output alternative is Samsung CL31B226KPHNNNE, 22 uF / 10 V X7R in 1206. One part at 3.3 V yields 18.55 uF typical; separate 0.90 tolerance, 0.85 temperature and illustrative 0.90 aging factors leave 12.77 uF. Three parts at 0.8 V leave 46.22 uF under the same assumed factors. These are candidates, not guaranteed minima. The 0805 Murata 22 uF part could improve area further, once its bias data and combined-condition margin are established.

Input selection is a material risk. Two Samsung CL21B106KPQNNWE 10 uF / 10 V X7R 0805 parts yield only 9.684 uF typical at 5 V, falling to 6.668 uF after the same factors. At 5.5 V, initial tolerance alone leaves 7.963 uF, below the 8 uF TPS62864 input criterion. This larger package does not automatically solve DC-bias loss. A single 22 uF / 10 V 1206 candidate is included as an alternative sensitivity case; changing capacitor count requires new layout and ripple-current qualification.

Samsung CL03B104KP3NNWC verifies a 0201, 100 nF, 10 V X7R part. Its official typical curve retains about 56.81 nF at 5 V. Samsung CL03A224KQ3NNNC verifies a 0201, 220 nF, 6.3 V X5R part; no X7R version was verified. C65 is connected to EMMC_VDDI, whose actual internal voltage must be checked. An 85 C memory case limit does not establish board ambient, capacitor temperature or permission to substitute X5R.

Eleven C233-C238 and C240-C244 positions remain 100 nF reference/local-bulk-TBD parts. Their final bulk values, quantities and area remain unresolved. Keep them as an area risk rather than crediting 0.77 mm2 each as qualified bulk capacitance.

## Conservative package reservations

These planning rectangles use manufacturer maximum reflow lands or body, a provisional 0.25 mm clearance on each side, and rounding. They are intentionally conservative. They are not assertions of minimum possible assembly size, and are not released footprints.

| MPN | Nominal / rating | Case | Maximum body L x W x T, mm | Planning L x W, mm | DC-bias evidence |
|---|---|---|---|---|---|
| CL03B104KP3NNWC | 0.1 uF / 10 V | 0201 | 0.63 x 0.33 x 0.33 | 1.55 x 0.9 | Official typical curve |
| CL03A224KQ3NNNC | 0.22 uF / 6.3 V | 0201 | 0.63 x 0.33 x 0.33 | 1.55 x 0.9 | Official typical curve |
| CL32B476KQVVPNE | 47 uF / 6.3 V | 1210 | 3.6 x 2.8 x 2.8 | 5.5 x 3.5 | Official typical curve |
| CL31B226KPHNNNE | 22 uF / 10 V | 1206 | 3.4 x 1.8 x 1.8 | 4.9 x 2.4 | Official typical curve |
| CL10B475KQ8NFQC | 4.7 uF / 6.3 V | 0603 | 1.75 x 0.95 x 0.95 | 3 x 1.5 | Official typical curve |
| CL21B106KPQNNWE | 10 uF / 10 V | 0805 | 2.15 x 1.4 x 1.4 | 3.5 x 2 | Official typical curve |
| GRM188Z71A106MA73D | 10 uF / 10 V | 0603 | 1.8 x 1 x 1 | 3 x 1.5 | Exact curve missing |
| GRM21BZ70J226ME44L | 22 uF / 6.3 V | 0805 | 2.2 x 1.45 x 1.45 | 3.5 x 2 | Exact curve missing |
| GRM188Z71C475KE21D | 4.7 uF / 16 V | 0603 | 1.8 x 1 x 1 | 3 x 1.5 | Exact curve missing |
| GRM155R70J105KA12D | 1 uF / 6.3 V | 0402 | 1.05 x 0.55 x 0.55 | 1.9 x 1.1 | Exact curve missing |

The Samsung 1210 generic reflow table covers a +/-0.3 mm chip row; this exact part has +/-0.4 mm length tolerance. Its 5.5 x 3.5 mm box includes extra allowance, but exact footprint qualification remains open. Samsung's 0201 reflow table plus the stated clearance also produces a larger envelope than the current dense model. Smaller courtyards may be possible with a qualified assembly process; they have not been demonstrated here.

## Effective-capacitance sensitivity

Official Samsung data were extracted from the numeric DC-bias graph data embedded in the downloaded manufacturer product pages. Values at rail voltages use linear interpolation between adjacent published points. Bulk 22 uF and 47 uF data use 120 Hz, 0.5 Vrms and 25 C; other parts retain their individual measurement conditions in JSON.

The table applies three factors separately: initial tolerance 0.90, assumed temperature retention 0.85 and illustrative aging retention 0.90. The aging allowance has no established lifetime model. Typical-model and lot uncertainty are not bounded. Independent multiplication does not create a guaranteed combined-condition minimum; real AC amplitude, temperature under DC bias, aging, rail limits and transients need qualification.

| Case and MPN | Qty | Rail V | Bias-only typical uF | After tolerance uF | After temperature uF | After illustrative aging uF | Required uF |
|---|---:|---:|---:|---:|---:|---:|---:|
| Replace one nominal 47 uF output with one 22 uF candidate; CL31B226KPHNNNE | 1 | 0.8 | 22.379 | 20.141 | 17.120 | 15.408 | 10 |
| Replace one nominal 47 uF output with one 22 uF candidate; CL31B226KPHNNNE | 1 | 1.1 | 22.177 | 19.959 | 16.965 | 15.269 | 10 |
| Replace one nominal 47 uF output with one 22 uF candidate; CL31B226KPHNNNE | 1 | 1.8 | 21.352 | 19.217 | 16.334 | 14.701 | 10 |
| Replace one nominal 47 uF output with one 22 uF candidate; CL31B226KPHNNNE | 1 | 3.3 | 18.554 | 16.699 | 14.194 | 12.774 | 10 |
| CPU/KPU three 22 uF outputs; CL31B226KPHNNNE | 3 | 0.8 | 67.136 | 60.422 | 51.359 | 46.223 | 30 |
| Preserve nominal 47 uF output; CL32B476KQVVPNE | 1 | 0.8 | 48.655 | 43.789 | 37.221 | 33.499 | 10 |
| Preserve nominal 47 uF output; CL32B476KQVVPNE | 1 | 1.1 | 48.343 | 43.509 | 36.983 | 33.284 | 10 |
| Preserve nominal 47 uF output; CL32B476KQVVPNE | 1 | 1.8 | 46.785 | 42.106 | 35.790 | 32.211 | 10 |
| Preserve nominal 47 uF output; CL32B476KQVVPNE | 1 | 3.3 | 40.227 | 36.204 | 30.773 | 27.696 | 10 |
| VIN pair of 10 uF 0805 alternatives; CL21B106KPQNNWE | 2 | 5 | 9.684 | 8.716 | 7.409 | 6.668 | 8 |
| VIN pair of 10 uF 0805 alternatives; CL21B106KPQNNWE | 2 | 5.5 | 8.848 | 7.963 | 6.769 | 6.092 | 8 |
| Alternative one 22 uF 1206 input (new topology candidate only); CL31B226KPHNNNE | 1 | 5 | 15.093 | 13.584 | 11.546 | 10.391 | 8 |
| Alternative one 22 uF 1206 input (new topology candidate only); CL31B226KPHNNNE | 1 | 5.5 | 14.159 | 12.743 | 10.832 | 9.748 | 8 |

TI TPS6282xA table 8-3 includes 22 uF nominal and 47 uF nominal with 0.47 uH. Section 8.2.2.5 specifies a 10 uF effective minimum. U21 is the A version of TPS62827; the non-A version requires 20 uF and must not be conflated. TPS62864 table 9-3 includes 2 x 22 uF or 47 uF, 3 x 22 uF, and 150 uF nominal with 0.24 uH; its output floor remains 30 uF effective. Existing load transients, startup/inrush, candidate inductors and local placement are still open checks.

## Release blockers

1. Recover exact Murata 10 uF and 0805 22 uF bias/AC/temperature data or obtain a warranted lower-bound envelope. TPS62864 input capacitance must satisfy the requirement at the approved worst-case VIN.
2. Establish capacitor temperature and lifetime/aging requirements. Memory case rating is not evidence of system ambient or MLCC temperature.
3. Validate combined guaranteed capacitance, ripple current, ESR and transient response for each replacement of a nominal 47 uF output. C815's ESR <0.5 ohm has not been checked at the relevant frequency.
4. Generate and verify exact lands, courtyards and assembly tolerances before changing planning geometry. Preserve required effective capacitance and local decoupling placement obligations.

## Sources

Manufacturer originals are archived with SHA256 hashes in the companion JSON, together with full extracted DC-bias point arrays and the master net mapping. Each manufacturer's product page links its specification download.

- [samsung-CL03B104KP3NNW.html](https://product.samsungsem.com/mlcc/CL03B104KP3NNW.do)
- [samsung-CL03A224KQ3NNN.html](https://product.samsungsem.com/mlcc/CL03A224KQ3NNN.do)
- [samsung-CL32B476KQVVPN.html](https://product.samsungsem.com/mlcc/CL32B476KQVVPN.do)
- [samsung-CL31B226KPHNNN.html](https://product.samsungsem.com/mlcc/CL31B226KPHNNN.do)
- [samsung-CL10B475KQ8NFQ.html](https://product.samsungsem.com/mlcc/CL10B475KQ8NFQ.do)
- [samsung-CL21B106KPQNNW.html](https://product.samsungsem.com/mlcc/CL21B106KPQNNW.do)
- [GRM188Z71A106MA73-01A.pdf](https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM188Z71A106MA73-01A.pdf)
- [GRM21BZ70J226ME44-01A.pdf](https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM21BZ70J226ME44-01A.pdf)
- [GRM188Z71C475KE21-01A.pdf](https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM188Z71C475KE21-01A.pdf)
- [GRM155R70J105KA12-01A.pdf](https://search.murata.co.jp/Ceramy/image/img/A01X/G101/ENG/GRM155R70J105KA12-01A.pdf)

TI references: [TPS6282xA](https://www.ti.com/lit/ds/symlink/tps62827.pdf), [TPS62864](https://www.ti.com/lit/ds/symlink/tps62864.pdf).

## Coherent candidate BOM and area delta

One practical review candidate retains every master capacitor position. It changes the twelve regulator input parts to 22 uF / 10 V X7R 1206, uses the same CL31B226KPHNNNE for the nine existing 22 uF positions and four formerly 47 uF output positions, and uses CL10B475KQ8NFQC for the ten 4.7 uF local capacitors. The other 108 capacitor positions retain their existing provisional reservations. No count, master BOM or layout changes were made.

This option favors two 22 uF inputs per regulator. Three of the screened 10 uF 0805 parts save some area but leave only a small arithmetic margin after the chosen factors.

The following checks also include an explicit 0.90 model-margin factor after tolerance, temperature and aging. It is a planning allowance, not evidence that production or model error is bounded to 10%.

| Check | Bias V | Typical uF | After tolerance, temperature, aging and model factors uF | Required uF | Remaining arithmetic margin |
|---|---:|---:|---:|---:|---:|
| Each regulator input pair, worst converter VIN endpoint | 5.5 | 28.318 | 17.547 | 8 | 119.3% |
| CPU/KPU output bank at converter maximum programmable voltage | 1.675 | 64.562 | 40.006 | 30 | 33.4% |
| Single 22 uF output replacing nominal 47 uF | 0.8 | 22.379 | 13.867 | 10 | 38.7% |
| Single 22 uF output replacing nominal 47 uF | 1.1 | 22.177 | 13.742 | 10 | 37.4% |
| Single 22 uF output replacing nominal 47 uF | 1.8 | 21.352 | 13.231 | 10 | 32.3% |
| Single 22 uF output replacing nominal 47 uF | 3.3 | 18.554 | 11.497 | 10 | 15.0% |
| Single 22 uF output with illustrative +5% on 3.3 V | 3.465 | 18.209 | 11.283 | 10 | 12.8% |
| Rejected lower-margin alternative: three 10 uF 0805 inputs | 5.5 | 13.272 | 8.224 | 8 | 2.8% |

The 1.675 V check is the converter's programmable maximum and is used only to stress the capacitor calculation. It does not approve that voltage for the K230. The 3.465 V check is an illustrative +5% rail scenario. Actual voltage limits and the combined worst-case capacitance envelope remain release blockers.

| Group | Baseline count | Candidate count | Baseline area mm2 | Candidate area mm2 | Delta mm2 |
|---|---:|---:|---:|---:|---:|
| All six regulator input pairs: 12 nominal 10 uF become 12 nominal 22 uF | 12 | 12 | 34.32 | 141.12 | +106.80 |
| Nine existing nominal 22 uF including three memory decouplers | 9 | 9 | 25.74 | 105.84 | +80.10 |
| Four nominal 47 uF outputs become one nominal 22 uF each | 4 | 4 | 20.16 | 47.04 | +26.88 |
| Ten local nominal 4.7 uF remain 0603 X7R | 10 | 10 | 28.60 | 45.00 | +16.40 |

The 35 reviewed capacitors change from 108.82 to 339.00 mm2, a +230.18 mm2 sensitivity. All 143 capacitor reservations total 425.08 mm2 under this scenario. Keeping other board reservations unchanged gives 1258.39 mm2, which exceeds the provisional 1156 mm2 inside-perimeter area by 102.39 mm2. This conservative candidate does not establish a packing solution. It leaves local-bulk-TBD additions and all routing/escape requirements unresolved.

The rectangle method is a scenario choice, not a universal minimum. In particular, no blanket 0.25 mm courtyard requirement has been imposed on the existing 0201 population. An assembly-qualified compact land pattern or a smaller electrically qualified part could reduce these numbers.

## Manufacturer land midpoint and input-count sensitivities

Samsung's exact downloaded specifications contain the common reflow table on PDF page 33. For 1206 CL31B226KPHNNNE (+/-0.2 mm), the recommended ranges are a=1.64-1.76 mm, b=1.19-1.31 mm and c=1.74-1.86 mm. The copper span a+2b is 4.02-4.38 mm; its midpoint is 4.20 x 1.80 mm. For 0603 CL10B475KQ8NFQC (+/-0.15 mm), the ranges are a=0.65-0.75 mm, b=0.73-0.83 mm and c=0.90-1.00 mm; copper span is 2.11-2.41 mm and midpoint is 2.26 x 0.95 mm.

These midpoint lands lie within manufacturer ranges. The added clearances below are independent planning assumptions. Neither the 0.10 mm nor 0.25 mm option is a manufacturer mandated minimum or an assembly qualification.

A secondary count-reduction option keeps two 22 uF inputs on each TPS62864 but uses one on each of the four TPS6282xA rails. At 5.5 V, one selected 22 uF leaves 8.774 uF after all four chosen factors, versus the 3 uF TPS6282xA minimum. This would remove four physical input positions in a future revision, reducing all capacitors from 143 to 139. No such change was applied. Input ripple, transients and placement remain open. Under the conservative rounded maximum-land boxes, the full-board reservation would be 1211.35 mm2, still above the provisional 1156 mm2 region.

| Scenario | 1206 count | 0603 count | 1206 reservation mm | 0603 reservation mm | Full dense area mm2 | Remaining area to 1156 mm2 |
|---|---:|---:|---|---|---:|---:|
| All input pairs, manufacturer land midpoint +0.25 mm clearance | 25 | 10 | 4.70 x 2.30 | 2.76 x 1.45 | 1229.66 | -73.66 |
| All input pairs, manufacturer land midpoint +0.10 mm clearance | 25 | 10 | 4.40 x 2.00 | 2.46 x 1.15 | 1167.68 | -11.68 |
| Four single-input TPS6282xA rails, midpoint +0.25 mm clearance | 21 | 10 | 4.70 x 2.30 | 2.76 x 1.45 | 1186.42 | -30.42 |
| Four single-input TPS6282xA rails, midpoint +0.10 mm clearance | 21 | 10 | 4.40 x 2.00 | 2.46 x 1.15 | 1132.48 | 23.52 |

A positive area remainder is not proof of packing or routed fit. These sensitivities still omit resolved local-bulk additions, BGA escape, routing channels and thermal constraints. They leave the existing 0201 reservations untouched and do not establish a universal smallest package or courtyard.
