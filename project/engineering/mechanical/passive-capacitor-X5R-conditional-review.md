# X5R conditional research archive

Status: historical conditional evidence only. X5R is excluded from current selection pending thermal clarification. The lead reports a sealed enclosure and a maximum of 75-85 C; whether that refers to air or chip surface is unresolved. No 85 C ambient assumption, thermal margin or X5R approval is implied. Optimization stopped when this information arrived. The active priority returns to X7R / 125 C parts and hotspot qualification.

No master BOM or geometry was changed. The current regenerated master has 246 XML references. The completed X7R report remains unchanged. Any area calculation below is explicitly a historical sensitivity against the earlier 243-envelope baseline, not a new current-board total.

## Material findings already recovered

- Official Samsung curves exist for 22 uF / 6.3 V and 22 uF / 10 V X5R 0402 parts. Three of the 6.3 V part do not reach 30 uF even at 0.8 V under the stated four-factor screen. Three of the 10 V part pass that startup screen but fall short at the converter's 1.675 V capability endpoint
- Five of the 10 V 0402 part screen above 30 uF, but their 85 C surface-temperature ceiling and the new sealed-enclosure information block selection
- A 47 uF / 10 V X5R 0805 part has enough typical-model arithmetic margin for the considered input and output roles. That does not resolve its temperature or lifetime limitations
- TI's exact GRM155R60J226ME11 22 uF / 6.3 V X5R 0402 example remains a reference only. The current direct Murata PDF fetch failed, and exact numeric bias data were not recovered. Samsung data cannot be substituted as evidence for the Murata part

## Recovered exact parts

| MPN | Rating | Case | Maximum L x W x T, mm | Selection |
|---|---|---|---|---|
| CL05A226MQ5NUNC | 22 uF / 6.3 V, X5R | 0402 | 1.2 x 0.7 x 0.7 | Not selected |
| CL05A226MP6NUNC | 22 uF / 10 V, X5R | 0402 | 1.2 x 0.7 x 0.8 | Not selected |
| CL21A476MPYNNNE | 47 uF / 10 V, X5R | 0805 | 2.2 x 1.45 x 1.45 | Not selected |
| CL21A226MAYNNNE | 22 uF / 25 V, X5R | 0805 | 2.2 x 1.45 x 1.45 | Not selected |

The exact CL05A226MP6NUNC specification page 18 defines the temperature used in its derating guide as MLCC surface temperature including self-heating. The rating is not an allowable enclosure ambient. An enclosure air temperature approaching 85 C leaves no demonstrated margin for local conduction or ripple heating.

## Historical capacitance screen

The calculation retains all factors separately in JSON: official typical DC-bias capacitance at 25 C, then 0.80 tolerance, 0.85 temperature retention, 0.90 illustrative aging and 0.90 unqualified model margin. These are arithmetic assumptions, not a guaranteed combined-condition minimum. The table is retained to explain the investigation, not to recommend X5R.

| Historical check | Qty | Bias V | Typical uF | After all four factors uF | Required uF |
|---|---:|---:|---:|---:|---:|
| Three 6.3 V 0402 capacitors at startup | 3 | 0.8 | 54.142 | 29.821 | 30 |
| Three 10 V 0402 capacitors at startup | 3 | 0.8 | 58.596 | 32.275 | 30 |
| Three 10 V 0402 capacitors at converter maximum | 3 | 1.675 | 41.144 | 22.662 | 30 |
| Five 10 V 0402 capacitors at converter maximum | 5 | 1.675 | 68.573 | 37.770 | 30 |
| Two 47 uF input parts at maximum converter VIN | 2 | 5.5 | 27.751 | 15.285 | 8 |
| One 47 uF input on a TPS6282xA | 1 | 5.5 | 13.876 | 7.643 | 3 |
| One 47 uF output at nominal 3.3 V | 1 | 3.3 | 23.165 | 12.759 | 10 |
| One 47 uF output at illustrative +5% rail | 1 | 3.465 | 22.153 | 12.202 | 10 |
| Two 22 uF / 25 V alternative inputs | 2 | 5.5 | 17.548 | 9.665 | 8 |

The 1.675 V endpoint is a capacitor stress calculation using converter capability, not permission to apply it to the K230. The 3.465 V point is an illustrative +5% rail check. Five 22 uF parts give 110 uF nominal; that lies within the span of TI's listed 66 uF and 150 uF examples, but the exact combination is not directly marked as tested in the LC matrix.

## Historical area hypothesis, rejected for current selection

One coherent hypothesis had two 47 uF inputs per TPS62864, one per TPS6282xA, five 22 uF 0402 outputs per CPU/KPU, three 22 uF 0402 memory parts, four 47 uF 0805 output parts and ten retained 4.7 uF X7R 0603 parts. Four hypothetical input removals and four new CPU/KPU output positions would cancel, leaving 143 capacitors on the earlier snapshot. No such edits were applied.

| Group | Earlier count | Hypothetical count | Earlier area mm2 | Hypothetical area mm2 | Delta mm2 |
|---|---:|---:|---:|---:|---:|
| Regulator inputs | 12 | 8 | 34.32 | 56.00 | +21.68 |
| CPU/KPU and memory nominal 22 uF | 9 | 13 | 25.74 | 36.56 | +10.82 |
| Four regulator output positions | 4 | 4 | 20.16 | 28.00 | +7.84 |
| Ten local 4.7 uF positions, retained X7R | 10 | 10 | 28.60 | 45.00 | +16.40 |

This historical calculation adds 56.74 mm2 to the 1028.21 mm2 snapshot, giving 1084.95 mm2. It is not the current board total. The planning rectangles use manufacturer maximum reflow lands/body and an assumed 0.25 mm margin, not universal manufacturer minimum courtyards. Local bulk, BGA escape, routing, PI and heat remain unresolved.

## Blocking decision

Keep X5R unselected. Clarify the reported temperature location, establish the maximum local capacitor surface temperature and thermal margin, then qualify voltage/temperature derating, lifetime and combined-condition capacitance. No positive arithmetic or area result overrides this gate.

## Primary sources

- [CL05A226MQ5NUNC](https://product.samsungsem.com/mlcc/CL05A226MQ5NUN.do)
- [CL05A226MP6NUNC](https://product.samsungsem.com/mlcc/CL05A226MP6NUN.do)
- [CL21A476MPYNNNE](https://product.samsungsem.com/mlcc/CL21A476MPYNNN.do)
- [CL21A226MAYNNNE](https://product.samsungsem.com/mlcc/CL21A226MAYNNN.do)

[TI TPS62864](https://www.ti.com/lit/ds/symlink/tps62864.pdf) supplies the reference component and output-capacitance context. Manufacturer HTML/specification originals and source hashes are recorded in the JSON; complete numeric DC-bias points are retained there.
