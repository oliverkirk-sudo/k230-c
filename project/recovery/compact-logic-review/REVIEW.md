# Compact control logic recovery review

2026-10-01. **Validated conditional delta: U14 may use TI SN74LVC1G97DSFR, and U92/U94 may be consolidated into one Nexperia 74AUP2G97GUX. Keep R33=270k.** This review changes no CAD. It verifies the source baseline, exact functions/pin assignments and bounded electrical screens; it does not qualify startup, routing, manufacturing or hardware.

## Baseline and recovery status

The verified HT-DRAFT13 netlist is `cad/high-temp-candidate/master.xml`, SHA-256 `96108059ca509bbde234565dcda46a2a0273dd2cb296a5d3a95aac812d08976b`, with 254 references and 1509 pin/net nodes. U14, U92 and U94 are **74AUP1G97GW,125**. R33 is **270k**. U91 is **74AUP1G17GW,125**, a push-pull Schmitt reset buffer; U93 is **74AUP1G06GW,125**, an open-drain inverter.

The recovered compact TI manifest and AUP1G97 status describe older alternatives, including a superseded U91 open-drain arrangement. They are evidence of earlier source review, not current BOM authority. Do not restore that topology or the old ordinary-CMOS LVC1G32.

Nexperia currently identifies **74AUP2G97GUX**, 12NC **935304484115**, as active in XQFN10/SOT1160-1. Its package-specific pin map independently matches the retained ten-pin mapping lead. No surviving lost-branch netlist proves its old BOM identity. This is a source-backed reconstruction candidate, not recovered CAD. The minimal two substitutions, retaining all passives, would give **253 refs / 1507 nodes**, not the remembered 258/1517; other changes must be reconstructed separately.

## Exact electrical delta

All three 97 devices implement `Y = C ? A : B`. TI calls these inputs In2=C, In0=A, In1=B. All eight datasheet truth rows were checked in `truth-table.csv`.

U14 ordinary OR requires **A/In0=1**, yielding B OR C. Tying B high instead yields A OR NOT C and is wrong. Keep all numbered nets:

| Pin | TI DSF function | U14 net |
|---|---|---|
| 1 | In1 | GLOBAL_DISABLE |
| 2 | GND | GND |
| 3 | In0 | VDD_3V3 |
| 4 | Y | DISABLE_OR_TF |
| 5 | VCC | VDD_3V3 |
| 6 | In2 | MODE_TF |

OR input/output states are 00→0, 01→1, 10→1, 11→1. Keep C34's local 100nF bypass. Same numbered nets do not imply interchangeable footprints.

Consolidate the two AND gates into proposed U92=74AUP2G97GUX. Tie both B inputs low. The actual **GU** pin map is different from the DP/TSSOP drawing used in the datasheet's configuration figures:

| GU pin | Function | Net |
|---|---|---|
| 1 | 1B | GND |
| 2 | 1C | BOOT_VOLTAGE_QUALIFIED_1V8 |
| 3 | 2Y | RESET_RELEASE_REQUEST_1V8 |
| 4 | GND | GND |
| 5 | 2A | FIXED_RAILS_PGOOD_3V3 |
| 6 | 2B | GND |
| 7 | 2C | RSTN |
| 8 | 1Y | STORAGE_ENABLE_1V8 |
| 9 | VCC | VDD1P8 |
| 10 | 1A | FIXED_RAILS_PGOOD_3V3 |

Both ANDs have states 00→0, 01→0, 10→0, 11→1. Remove the old U94 logical component only when integrating. Keep C810/C813 in the minimal delta; the final placement must provide effective local bypass at pin9. Do not float any configuration input or add an invented exposed pad. U91/U93, supervisor DRV EP7 grounding, R527=10k, R530=100k, and default R528 DNP remain part of the current contract. Sixteen PG/qualifier/RSTN/mode combinations preserve both logical outcomes; external RSTN remains a request input rather than a direct connection to SOC_RSTN.

## Supply and 125°C electrical screens

Use the latest declared static rail bounds: **1V8=1.764476615–1.836094613V; 3V3=3.245129532–3.392164299V**. These are circuit assumptions, not measured rails. Use total resistance acceptance ±10% for the following screen; initial 1% resistor tolerance does not establish that lifetime envelope.

| Quantity at −40…125°C | Baseline Nexperia 1G97 / proposed 2G97 | Proposed TI LVC1G97 |
|---|---|---|
| Operating supply | 0.8–3.6V | 1.65–5.5V |
| Recommended input voltage | 0–3.6V | 0–5.5V |
| Continuous-range light-load output | VOH≥VCC−0.11V, VOL≤0.11V, ±20µA | VOH≥VCC−0.10V, VOL≤0.10V, ±100µA |
| Input leakage | ±0.75µA, VI=0–3.6V, VCC=0–3.6V | ±5µA, VI=5.5V or GND, VCC=0–5.5V |
| Power-off leakage | ±0.75µA at VCC=0, VI/VO=0–3.6V | ±10µA at VCC=0, VI/VO=5.5V |
| Additional power-off row | ±0.75µA at VCC=0–0.2V | No equivalent row found |
| Static ICC, unloaded | 1.4µA per package, inputs at GND or VCC | 10µA, inputs at GND or5.5V |
| Additional ICC test | 75µA, one input VCC−0.6V, VCC=3.3V | 500µA, one input VCC−0.6V, VCC=3–5.5V |

Nexperia 1G97/2G97 have identical relevant 125°C thresholds: at the **1.65V test point**, VT+=0.91–1.31V, VT−=0.47–0.84V, hysteresis=0.27–0.66V; loaded output at ±1.9mA is VOH≥1.17V / VOL≤0.39V. At **3.0V**, VT+=1.88–2.32V, VT−=0.88–1.24V. TI at **3.0V** gives VT+=1.50–1.87V, VT−=0.84–1.19V, hysteresis=0.53–0.87V. **These are discrete supply rows. Full-rail threshold and loaded-output interpretation remains open; no interpolation is claimed.**

### U14 valid-supply input and output budgets

R31/R32 each span 9–11kΩ. TI's higher input-leakage allowance is included with every connected TMUX control input; use the hot limits rather than typical leakage.

| Net / state | Leakage contributors | Result before extra board/carrier leakage |
|---|---|---|
| MODE_TF, JP1 open | U14.In2 5µA + U11.SEL 2µA + U12.SEL 2µA = **9µA** | R31 gives low≤**0.099V**; **351mV** below TMUX VIL=0.45V; **741mV** below TI discrete-3V VT−min=0.84V |
| GLOBAL_DISABLE released | U93 IOZ 0.75µA + U14.In1 5µA + U11.EN 2µA + U12.EN 2µA = **9.75µA** | R32 drop≤107.25mV; high≥**3.137879532V**; **1.937879532V** above TMUX VIH=1.2V; **1.267879532V** above TI discrete-3V VT+max=1.87V |
| MODE_TF, JP1 closed | Direct cold-only strap to 3V3; R31 pulls against the strap | Nominal logic high follows the valid rail; verify switch/contact drop and supply ramp separately |
| DISABLE_OR_TF low | R33min=243k plus one U13.EN 2µA | Maximum sink screen **15.959524µA**, below TI100µA guarantee; VOL≤0.1V, TMUX low margin **350mV** |
| DISABLE_OR_TF high | One U13.EN 2µA; pullup assists | VOH≥**3.145129532V**; TMUX high margin **1.945129532V** |

Thus the R31/R32 voltage budgets remain positive under the declared hot leakage/resistance assumptions. The voltage calculations do not erase the discrete-threshold caveat. TI's leakage tests are at the stated endpoints; treating them as conservative allowances at intermediate 3V3 signal levels is an explicit source-condition interpretation. The TMUX ±2µA control-input entries are tested at VSEL=0, 1.8V or VDD; no additional worst-case board leakage is included. Keep these provenance limits with the screen.

**Retain R33=270k.** A lower resistor is not required to obtain the valid-supply light-load guarantee or to make this device Schmitt-compatible. The generator records a 43k sensitivity for comparison only; it is not the proposed delta.

### Dual gate budgets

The dual retains two PG inputs, so PG leakage remains **2.1µA**; R527 high≥**3.222029532V**, sink screen≈**0.379007mA** versus TPS3808's0.4mA row. PG low≤0.4V retains only **70mV** versus the discrete1.65V VT−min. The qualification pulldown gives ≤**82.5mV**. The dual's3.6V input ceiling leaves only207.836mV above the modeled3V3 maximum; include overshoot and ground offset. Do not substitute historical ±1% resistor results.

Storage-enable drives only U93's ordinary input: the ±20µA output row and 0.70/0.30VCC receiver levels give ≥**419.343mV** high/low margin across the declared1V8 range at a common local supply. Actual local supply/ground drop and U93's **200ns/V** input slew requirement still apply. Reset-release drives TPS3808.MR: its70k minimum internal pullup demands up to **26.230µA**, so it exceeds the20µA light-load row. The discrete1.65V loaded VOL0.39V screen leaves **139.343mV** to0.3×VDDmin. Retain the full-rail loaded-row signoff gate; do not silently call this a continuous-supply proof.

## Slow inputs, power collapse and timing

TI LVC1G97 has characterized VT+/VT−/hysteresis, no transition-rate restriction in recommended conditions, and TI's own product clip explicitly identifies slow-transition-compatible Schmitt inputs. The datasheet's generic application text points to nonexistent VIH/VIL and slew rows; use its actual electrical tables, not the old **LVC1G32 10ns/V** limit. Nexperia2G97 likewise has characterized transfer thresholds and no operating slew row. The Nexperia handbook supports slow inputs on such specified Schmitt devices. These facts support stable-valid-supply operation, not arbitrary ramps or a bound on supply current throughout every slow crossing.

Reject **74AUP2G08GXX** as a direct reset-RC replacement: despite advertised Schmitt action, its operating table requires **≤200ns/V**. The nominal100k/100nF RC has a10ms time constant. Do not confuse unspecified Schmitt action with the characterized97 inputs.

Keep partial-power separate. U14/R33 share3V3, so a high disable level is not guaranteed when that rail collapses. TI has no deterministic output guarantee below1.65V. Nexperia does not guarantee logic below0.8V; Ioff/ΔIoff do not establish a reset state, including0.2–0.8V. A hypothetical separately live270k pullup with TI10µA Ioff + TMUX2µA gives a negative linear high screen, hence **no guaranteed high**; that is not the present topology and is not a measured negative voltage. Do not carry forward the AUP's more favorable powered-off margin as a TI result.

TI's125°C propagation maximum is7.3ns at3.3V±0.3V in its specified50pF/500Ω, fast-input test. Nexperia2G97 at1.65–1.95V gives7.2/8.2/9.1/11.8ns for5/10/15/30pF, measured with input tr=tf≤3ns and1MΩ load. These are propagation test limits, not output-rise limits or guaranteed end-to-end slow-RC/reset timing. TPS3808 MR assertion150ns remains typical only; CT-open release12–28ms applies only under its stated conditions.

## Package, factory and thermal gates

TI DSF0006A drawing4220597/B,06/2022 was visually checked in the downloaded PDF, physical pages29–31. Body0.95–1.05mm square, height≤0.4mm; 0.35mm pitch. Source example: six0.60×0.17mm copper lands, centers x=±0.40mm, y=−0.35/0/+0.35mm; component-side1/2/3 left and6/5/4 right. Paste is six0.60×0.15mm apertures on the same centers withR0.05mm corners and example0.09mm stencil. NSMD drawing allows mask expansion≤0.07mm. At its maximum, adjacent0.35mm-pitch mask web is only0.04mm. Paste release, mask registration/dams, stencil process and placement/rework capability are factory acceptance items, not source guarantees. Do not reuse a global paste shrink or a different package's geometry.

Nexperia SOT1160-1 is1.4×1.8mm nominal,0.4mm pitch,≤0.5mm height; ten terminals without an extra EP. Official package PDFp3 supplies the reflow land, +0.0625mm mask and −0.02mm paste-per-side rules with0.1mm stencil; its complete drawing governs nonuniform corner lands. Source occupied/clearance footprint envelope is2.35×1.95mm. Web text was read, but local original download returned403 and no inspectable web screenshot reached this tool session. **The package's coordinate/paste/registration visual audit remains open.** No production footprint is furnished here.

A still smaller U14 electrical-preservation alternative is **74AUP1G97GXZ**, active12NC935307123147,1.0×0.8×0.32mm SOT1255-2. It preserves all six numbered functions and the AUP leakage/supply characteristics; its exact multi-shape manufacturer lands/paste require separate review. It is an alternative, not the reconstructed TI choice.

−40…125°C is the logic ambient rating, not an enclosure or board qualification. Nexperia2G97GU's250mW absolute power limit derates7.1mW/K above115°C, giving179mW at125°C; this is not a desired operating dissipation. TI's DSF θJA is absent from the inspected datasheet thermal table: do not borrow DBV/DCK/DRL values. Include slow-input current, switching/load dissipation and local heating; satisfy junction constraints. The earlier regulator junction, memory case, TF-translator ambient and oscillator temperature gates remain unchanged.

## Acceptance/test plan

1. Integrate into a separate candidate, compare the exact pin/net map and all unaffected refs, export actual schematic netlist, and rerun ERC plus storage/reset truth checks. Distinguish new counts from the lost branch's unproven count. Keep R528 DNP and cold-only mode selection.
2. Complete Nexperia original/visual land verification and independent pin1 orientation check. Compare generated copper, mask and paste against exact drawings; verify factory minimum mask web, registration, aperture release, stencil thickness, placement/rework and assembly yield. Body-area savings are not routing-space proof.
3. Resolve full-rail threshold and loaded-output row applicability. Add carrier/board contamination leakage and actual resistor mission-profile error. Verify R31/R32 measured high/low at rail extremes and hot temperature; measure U93 low against the narrow TMUX0.45V ceiling.
4. Bench slow/fast/nonmonotonic supply ramps; each relevant rail held up separately; short interruptions, brownouts and repeated cycling. Observe PG, qualifier, raw RSTN, MR, delayed reset, SOC_RSTN, GLOBAL_DISABLE and DISABLE_OR_TF. Test default DNP, deliberate qualifier, both cold modes and TF insertion. Establish actual reset assertion/release timing and absence of hazardous enable glitches.
5. Sweep the resetRC/input edges and noise, inspect Schmitt chatter/current, measure U92-output slew into U93 and U14-output edges into TMUX with actual load/probe capacitance. Validate local bypass, hot/cold full-load and current-limit startup. Do not infer output edges from R33×C while U14 is actively driving.

## Evidence

- [TI LVC1G97 RevN](https://www.ti.com/lit/ds/symlink/sn74lvc1g97.pdf): pp3–10 electrical/pins/function; physical PDFpp29–31 DSF drawing. [Exact orderable](https://www.ti.com/product/SN74LVC1G97/part-details/SN74LVC1G97DSFR)
- [TI97 product clip](https://www.ti.com/lit/ml/scyb010a/scyb010a.pdf): p1 slow-input statement
- [Nexperia2G97 Rev4](https://assets.nexperia.com/documents/data-sheet/74AUP2G97.pdf): p2 GU pins; pp3–4 function/ratings; pp5–7 static/thresholds; pp8–10 timing. [Exact orderable](https://www.nexperia.com/products/analog-logic-ics/logic/gates/configurable-gates/serie/74aup2g97)
- [SOT1160-1 package information](https://assets.nexperia.com/documents/package-information/SOT1160-1.pdf): pp1–3 package and reflow
- [Nexperia1G97 Rev14](https://assets.nexperia.com/documents/data-sheet/74AUP1G97.pdf), [1G06 Rev12](https://assets.nexperia.com/documents/data-sheet/74AUP1G06.pdf), [2G08 Rev12](https://assets.nexperia.com/documents/data-sheet/74AUP2G08.pdf), [logic handbook](https://assets.nexperia.com/documents/brochure/Nexperia_LOGIC_Handbook_201029.pdf)
- [TMUX1574 RevC](https://www.ti.com/lit/ds/symlink/tmux1574.pdf): p6 control-input limits; [TPS3808 RevN](https://www.ti.com/lit/ds/symlink/tps3808.pdf): pp6–7 MR/output/timing conditions

Run `python recovery/compact-logic-review/verify_review.py` against the frozen baseline. `validation.json`, `proposed-pin-map.csv`, `truth-table.csv`, and `integrated-logic-states.csv` are review artifacts only. Originals successfully retrieved remain outside the project in `/workspace/shared/k230-reference`; `source-manifest.json` records actual availability and hashes. No manufacturing, purchasing, supplier communication, OTP or access bypass was performed.
