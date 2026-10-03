# v9数量更新

下文保存v8物理审查历史。本轮新增音频与eMMC局部旁路后，Samsung参考为253引用/246功能件/252矩形，密集1043.50mm²，0402情形1175.47mm²。当前JSON/拼排图已刷新；历史电容情形未冒称已重新计算。高温分支另有254引用，新增逻辑封装未核实，尚无完整实料布局结论。

# Current physical feasibility review

Updated 2026-09-30 after the lead's 246-reference master rebuild. **The design has not established routed or thermal feasibility.** The sealed enclosure is reported at 75–85°C maximum; whether this is air or a component-surface temperature remains unresolved. X5R optimization is excluded from selection pending clarification.

The current baseline contains **239 populated functional components and 245 footprint envelopes**, including 145 capacitors. The revised reservation sum is **1029.75 mm²** for the dense-small-passive scenario, versus the provisional 1156 mm² interior. The 0402-small-passive scenario is **1159.23 mm²**. The existing bounded rectangle algorithm places all 245 baseline rectangles with no overlaps; it does not enforce local bypass distances, switching loops, BGA escape, routing corridors, heat flow or real castellation geometry.

Source-backed changes applied to the baseline area tool are L22/L23 at 3.0×2.4 mm, R220 at 3.2×1.7 mm, the R561 WFZ0402 candidate at 2.0×1.2 mm, and the lead's Y2 crystal candidate at 4.2×3.5 mm. NVT4858HK now uses the verified SOT1161-2 candidate at the existing 2.8×3.6 mm courtyard. The two added MIPI bypass capacitors are C245 and C246. No external TF socket/card was included in the core-board area.

## What the passive evidence changes

Most ordinary 0201 pull resistors and low-voltage 100 nF bypass assignments are plausible, but remain assembly/PDN candidates. Exact 100 nF/10 V X7R 0201 parts exist; one recovered typical curve retains only about 56.8 nF at 5 V. The high-capacitance parts were already in larger bins, yet those bins are not proven manufacturing footprints: verified 22 µF X7R and 47 µF X7R examples require larger packages and lands. The actual constraint is minimum effective capacitance, including temperature, DC/AC bias, initial tolerance, lifetime and production variation.

The completed X7R review supplies a coherent source-backed candidate, using 22 µF/10 V X7R parts for regulator inputs and outputs instead of preserving arbitrary original nominal values. It passes the displayed arithmetic screen with explicit tolerance, temperature, aging and model allowances. The latter two allowances are unqualified assumptions; **there is no guaranteed worst-case capacitance signoff**. The conservative candidate requires much more area than the original bins.

The capacitor and candidate-packing reports deliberately retain their **earlier 243-envelope snapshot**. On that snapshot, the conservative paired-input X7R case totals 1258.39 mm². A four-single-input, manufacturer-midpoint-land, 0.10 mm-clearance sensitivity totals 1132.48 mm², but the bounded rectangle heuristic placed only 217/239 candidate rectangles. Adding optional ferrite and XEL3520 reductions gave 1122.24 mm² and 229/239 rectangles. These failures do not prove impossibility; the area sums do not prove packing either. Add the later MIPI capacitors before comparing any old total to the current design. No such candidate substitutions were applied to the master by this audit.

Reference PLL/VAA filters use 100 nF local capacitors. Earlier “local bulk TBD” wording was speculative; no missing required bulk has been established or removed. Future PI qualification can add or change parts, but eleven hypothetical extra bulk capacitors must not be counted as known requirements.

## Thermal constraint

TPS62864 has a 125°C recommended junction limit and a specific lifetime warning for continuous 4 A above 105°C junction. TPS6282xA also has a 125°C recommended junction limit. Murata DFE201612E's 125°C operating limit includes self-heating, with a 40°C maximum rise. These facts preclude accepting a compact package merely because its current label exceeds the intended load. See the complete limits and sources in `passive-hot-enclosure-review.md`.

R561's concrete WFZ040200000ZE66 power-feed candidate has 3 mΩ maximum resistance and a published 6.5 A current rating with derating. This gives substantially more resistance/current margin than an unspecified commodity 0201 link. Its layout, pulse current and local temperature still need qualification. The nine BLM15PX121SN1D ferrite candidates and smaller L21 alternatives are documented with explicit copper/thermal conditions; they remain optional review candidates.

## Verified NVT footprint

The editable library item is `CMK230_Translator_Candidate:NXP_SOT1161-2_NVT4858HK_1.8x2.6_P0.4_DrawingVerified_CANDIDATE`. It passed 244 native geometry assertions, 288 independent drawing checks, 16 copper/16 mask/16 paste native Gerber checks, all U95 pin-role comparisons and isolated KiCad DRC with zero violations. Its longer pin 1 land, top-view orientation, explicit mask/paste apertures and absence of a center pad are checked. The 0.08 mm mask web and 0.10 mm stencil remain assembly-process items.

## Files to use

- `full-bom-area-screen.json` and `full-envelope-packing-study.json/.svg/.png`: latest baseline
- `passive-physical-feasibility-status.json`: current counts, results and source hashes
- `passive-capacitor-candidate-review.md/.json`: dated X7R MPNs, bias curves, capacitance factors and area alternatives
- `passive-candidate-area-packing-scenarios.json`: dated isolated X7R rectangle sensitivities
- `passive-inductor-candidate-review.md` and `passive-small-parts-review.md`: exact inductor, resistor, jumper and ferrite evidence
- `passive-hot-enclosure-review.md`: thermal limits and open qualification needs
- `nvt4858-*`: footprint source manifest, coordinates, independent/native checks and visual gallery

Manufacturer originals remain outside the distributable project. The lead owns master changes, temperature-grade decisions and hardware release. Drawing checks and rectangle screens do not replace escape, thermal, PDN, assembly or functional validation.
