# K230 all-390 electrical pin-type audit

Read-only review of the compact integrated design, based on ERC export **2026-09-30T05:20:06-0700**. No CAD, generator, NC marker or connection was changed. The current model had zero ERC reports, but substantial direction information remained conservative.

## Result

All **390 physical balls** match the canonical source set, the official pinout workbook, the actual `Integrated.kicad_sym`, and the exported XML library pins. The independently parsed symbol and XML agree on all 390 current types. **90 type corrections** are proposed; these require review and a fresh ERC run, with no promise of preserving ERC0.

Files:

- `k230-all390-type-audit.csv`: one exact row per physical ball, including official worksheet/row, raw source DIR, current type, reusable type, proposed compact type, physical role, justification and exceptions
- `k230-proposed-type-corrections.csv`: only changed types
- `k230-type-audit-manifest.json`: exact source/snapshot hashes, full 390-entry proposed compact type map, and machine-readable changes

| Type | Current | Proposed compact |
| --- | ---: | ---: |
| power_in | 157 | 157 |
| bidirectional | 217 | 127 |
| input | 5 | 37 |
| output | 7 | 49 |
| passive | 1 | 8 |
| no_connect | 3 | 12 |

## Important reviewed exceptions

1. **GPIO capability is preserved.** All exposed GPIO2-63 and BOOT/GPIO0-1 remain bidirectional regardless of their default peripheral function. Private PMU GPIO65/66/67/69 also remain bidirectional for drive-low/release/read software I2C. A reusable K230 symbol should preserve bidirectional capability for all 72 GPIO-capable pads. Only the compact board's explicit PMU 64/68 input ownership and PMU 70/71 output-testpoint ownership use narrowed board-specific types.
2. **DSI lane 0 stays bidirectional.** Workbook rows 606/642 call W10/Y10 outputs, but TRM section 8.4.1, PDF p505, explicitly supports low-power reverse/turnaround operation on lane 0. Those two pins remain bidirectional. The other 8 DSI pins become outputs. The 18 CSI RX pins become inputs, supported by the package pinout and TRM 8.3.1 PDF p441. Generic PHY register IO/test descriptions do not override the documented normal receiver role; special PHY test/loopback modes need their own review.
3. **Analog signal direction is not a digital model.** ADC/MIC pins use input as their physical direction; HP outputs, MIC_BIAS, CODEC_VCM and temperature-reference VTEST use output. Neither classification asserts CMOS thresholds, arbitrary loading, power-delivery capability, or analog simulation. VCM/MIC_BIAS are not promoted to power_out.
4. **Analog resistor/reference nodes use passive modeling.** USB TXRTUNE, MIPI_REXT and DDR_ZN are calibration terminals; DDR_VREF is an external reference/divider node; USB VBUS uses the prescribed current-limiting resistor; MIPI_ATB is an unused analog test bus. A blanket I-to-digital-input or IO-to-bidirectional copy would lose their meaning. Each retains explicit external-network checks. USB ID becomes an analog sense input, supported by the guide and TRM PDF p1131, while recording workbook IO as a source simplification.
5. **Oscillator CIN/COUT direction is retained.** The four clock pins become input/output according to CIN/COUT, with analog crystal-amplifier roles recorded. This does not validate crystal gain, ESR, feedback, loading or startup, and it must not lead to adding a false digital clock driver merely to satisfy ERC.
6. **DDR controller command/clock/reset signals are outputs.** The workbook often gives coarse IO even for CA/CS/CKE/clock/reset. The LP4 circuit and device endpoint roles support explicit host outputs. DDR DQ, DQS and DMI remain bidirectional; DMI must support read DBI and write DM/DBI. The four unused rank 1 outputs keep output type plus intentional unused markers.
7. **NC scope is explicit.** A20/Y1/Y20 remain explicit named NC. Nine DDR balls are documented NC in both LP3/LP4 and can use a no_connect electrical classification without claiming they are physically unbonded. K20/L17/L18/L20/M20 are real LP3 CA/ODT functions unused in LP4: proposed type is output, with LP4-specific unused markers. They are never turned into intrinsic NC. D8 remains an unused functional output; U6 remains passive analog test, not intrinsic NC.

## Apply and validate

- Apply only after comparing current ball/name/type against the hashed snapshot. The compact generator was updated during this review; do not overwrite the frozen instrumented-reference variant.
- Preserve net names, physical balls, NC marker scope, GPIO ownership and exact source-backed connection assertions. A type correction alone authorizes no rewiring.
- Re-export XML and rerun ERC after applying reviewed changes. Inspect every new finding; do not add fictitious drivers or suppress errors to recover zero.
- Verify U2/U3 and external interface symbol directions separately. Typing U1 alone is not a full typed-system ERC. Passive switches also cannot model enabled/disabled state or voltage safety.
- Keep boot/OTP/MMC voltage policy, PMU lifecycle, reset interlock, analog bias correctness, clock startup, DDR training and SI/PI qualification as separate checks.

## Primary sources

[Official K230 pinout workbook](https://kendryte-download.canaan-creative.com/developer/k230/HDK/K230%E7%A1%AC%E4%BB%B6%E6%96%87%E6%A1%A3/K230_PINOUT_V1.2_20240822.xlsx), main pin sheet `1.K230&K230D管脚信息表`; exact rows are in every CSV record. The workbook was not redistributed.

[K230 TRM v0.3.1](https://kendryte-download.canaan-creative.com/developer/k230/HDK/K230%E7%A1%AC%E4%BB%B6%E6%96%87%E6%A1%A3/K230_Technical_Reference_Manual_V0.3.1_20241118.pdf), especially PDF p441 (CSI receive), p505 (DSI lane 0), p1131 (analog USB ID), and PMU mux/lifecycle sections.

[K230 Hardware Design Guide](https://www.kendryte.com/k230/en/main/00_hardware/K230_Hardware_Design_Guide.html), clock, LP4, USB, MIPI and analog interface circuits. [Samsung K4F8E304HB-MGCJ datasheet](https://www.szyuda88.com/home/8/a/2lhtb2/resource/2021/05/26/60ade38424a32.pdf), manufacturer-authored third-party mirror, pp7, 10-11 and DBI behavior.
