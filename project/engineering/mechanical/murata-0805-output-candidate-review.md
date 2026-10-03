# GRM21BZ70J226ME44L output-bank screen

2026-09-30. Keep as a QUANTIFIED CONDITIONAL candidate; do not select it or shrink the actual bank yet. Exact regulator reference supports relevance, but combined effective capacitance at application conditions is not qualified. No regulator, rail, performance, BOM or CAD changes made.

## Evidence and access limits
TI's TPS62864 reference itself lists this exact22µF6.3V0805 part; TPS62868 also uses it. Those nominal application examples do not replace the project's30µF effective-bank minimum or temperature/transient checks. The current0.24µH/3×22µF topology is preserved for this screen.
Official Murata exact-part PDF and product-detail endpoints returned403 and were not repeated. Publicly hosted manufacturer-authored2021 reference/characteristic sheets were inspected instead. Current manufacturer lifecycle/status was not established; neither a sibling nor distributor inventory is used as proof.
Exact reference identifies22µF±20%,6.3V,0805 body2.0×1.25×1.25mm, each dimension±0.2mm,−55…125°C and Z7/X7R(MURATA). The actual temperature test uses3.15V bias. Crucially its change calculation is [C(T,bias)−C(25°C,bias)]/C(25°C,no bias), so±15% is not simply±15% of the biased capacitance. A0.85 multiplier at0.8–1.675V is an assumption, not this exact guarantee.

## Curves actually inspected
The archived manufacturer sheet's25°C DC plot is approximately flat around0.8V, roughly5–10% lower by1.675V, and about60% lower near6.3V. Its separate0V-DC AC-amplitude plot falls about20% below reference near very small AC amplitude. These are visual approximate readings, not guaranteed lower limits. Do not multiply them blindly: their reference/test conditions differ, and the DC-curve AC label is clipped in this archive. The sheets have no combined bias/temperature/AC surface or application-temperature C curve. Ripple-heating curves are at80/400/800kHz and cannot certify this converter's actual ripple spectrum or capacitor temperature. The PDF renderer reported stream warnings; visible graphs were inspected, but missing data must not be treated as zero effect.

## Component-specification gates
For30µF final effective capacitance per rail:

| Parts per rail | Required each | All-effects retention of nominal | Remaining retention after20% tolerance | After tolerance plus HYPOTHETICAL0.85 temperature factor |
|---|---|---|---|---|
|2|15µF|68.18%|85.23%|100.27%|
|3|10µF|45.45%|56.82%|66.84%|
|4|7.5µF|34.09%|42.61%|50.13%|

The last column is sensitivity arithmetic only. It does not apply the Z7 test as a universal multiplicative bound. DC bias, small ripple amplitude, temperature, aging, lot variation and assembly must jointly satisfy the appropriate gate with design margin. Two parts cannot pass that hypothetical tolerance/temperature screen even before other losses. Three or four remain plausible candidates, not proven compliant. Four parts also require loop/transient validation because it is not the exact nominal table row.
The1.675V endpoint is capacitor-stress screening only, not an approved K230 operating voltage. Test the actual permitted CPU/KPU voltage range and transient overshoot.

## Physical opportunity
Manufacturer reference reflow row for this±0.2mm0805 body: gap1.0–1.4mm, each pad length0.6–0.8mm, pad width1.2–1.4mm. Land envelope is2.2–3.0mm long; midpoint2.6×1.3mm. This is copper geometry, not a routed courtyard guarantee.
Using the same planning conventions as the existing Samsung1206 study:
- Midpoint land plus0.10mm each side:4.20mm² per Murata versus8.80mm² per Samsung.
- Maximum land plus0.25mm each side:6.65mm² per Murata versus11.76mm² per Samsung.
Across CPU+KPU, three Murata parts each reserve25.20/39.90mm² in those two scenarios, versus52.80/70.56mm² for three Samsung parts each. Four Murata parts each reserve33.60/53.20mm². Thus a fourth0805 could still save17.36mm² in the conservative scenario, if electrically qualified. Routing, hot-loop locality, escape and thermal separation can consume that benefit.

## Thermal and qualification decision
At85°C enclosure air,125°C part rating leaves only an arithmetic40°C ceiling difference, not demonstrated margin. Measure local case temperature, self-heating and conducted heat. Preserve the30µF effective minimum and output-ripple/transient limits. Required closure is an exact-part combined lower-bound model or measurements covering voltage/ripple/temperature/aging/lot conditions, current lifecycle evidence, and layout/loop validation. No unbounded alternative-part search was performed.

Sources: TI https://www.ti.com/lit/ds/symlink/tps62864.pdf and https://www.ti.com/lit/ds/symlink/tps62868.pdf . Murata-authored reference archive https://www.mouser.com/datasheet/2/281/1/GRM21BZ70J226ME44_01A-1987068.pdf ; characteristic archive https://static.mercateo.com/20/0ba581d7d9db4b0489666a9ef094c411/pdf/3410970.pdf?v=56 . Official denied endpoints and exact file hashes are recorded in screen.json. Existing Samsung land comparison comes from passive-capacitor-X7R-regulator-sensitivity.json. Original PDFs are retained as internal evidence, not a redistributed deliverable.
