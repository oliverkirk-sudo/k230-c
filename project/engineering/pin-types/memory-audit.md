# LPDDR4 and eMMC electrical pin-direction audit

Read-only audit of the compact integrated design. Baseline export: **2026-09-30T05:31:34-0700**. The full U2/U3 package maps, actual symbol pin types, and exported XML were checked. No CAD or source-map files were changed.

## Result

**27 proposed corrections:** 24 on U2 and 3 on U3. All corrections replace a generic bidirectional type with a source-supported direction or analog-reference model.

| Part | Full physical map | Proposed changes | Proposed type totals |
|---|---:|---:|---|
| U2 Samsung K4F8E304HB-MGCJ LPDDR4 | 200 | 24 | 110 power_in, 44 bidirectional, 23 input, 1 passive, 22 no_connect |
| U3 Samsung KLMAG1JETD-B041 eMMC | 153 | 3 | 20 power_in, 9 bidirectional, 2 input, 2 output, 120 no_connect |

### U2 exact change allowlist

- **input:** G2, H2, H4, H9, H10, H11, J2, J4, J8, J9, J11, P2, P4, P8, P9, P11, R2, R4, R9, R10, R11, T2, T11
- **passive:** A5 (ZQ_a)
- These 23 inputs comprise 12 CA, 4 differential CK, 2 CKE, 2 CS, 2 ODT_CA, and one RESET_n. Samsung p12 §4.5/Table 1 explicitly assigns all these groups the Input type

### U3 exact change allowlist

- **input:** M6 (CLK), K5 (RSTN)
- **output:** C2 (VDDI analog internal-regulator stabilization node)

M6 is explicitly a clock input on Samsung p5. K5 has an inward RESET arrow in p8 Figure 5. C2's output designation is a project-level analog-direction abstraction based on its position at the internal regulator output, rather than a literal digital-output pin classification supplied by Samsung.

## Preserved electrical meaning

### LPDDR4 data and reference pins

- DQ has 32 bidirectional pins; DQS has eight bidirectional pins; DMI has four bidirectional pins
- **DMI C3, C10, Y3, Y10 remain bidirectional.** Samsung p12 explicitly describes read/write inversion and write masking. Page 7 also lists read and write DBI. The short “Input Data Inversion” label on p11 must not override those descriptions
- **ZQ A5 is a reference node.** Samsung p12 requires 240 Ω ±1% to VDDQ. The present network is U2.A5 → R63 240R 1% REF → VDD1P1_DDR_IO, which also supplies U2 VDDQ. Passive is the available KiCad analog-reference abstraction; topology and resistance assertions must carry the requirement that a directional ERC check cannot express
- **ODT_CA G2/T2 remain inputs** even though their current bias comes through resistors. Each is pulled toward VDD1P1_DDR_IO through R61/R62, respectively, both marked 10k REF. Type-related drive reports after application should be assessed as resistor-bias topology cases. They must not be “fixed” by returning these genuine inputs to bidirectional/passive or by inventing drivers. Termination behavior and mode-register settings remain separate checks

### eMMC interface and regulator node

- CMD M5 remains bidirectional. Samsung p5 specifies open-drain initialization and push-pull command operation. A single open_collector class would lose the supported push-pull and receiving roles
- DAT0–7 remain bidirectional push-pull channels
- H5 remains an **output** with the existing intentionally-unused disposition for fixed HS200. It is an eMMC-to-host HS400 strobe, not a manufacturer NC/RFU ball. Samsung p23 §8.3.2 also describes high-impedance behavior while not outputting
- C2 VDDI should be **output**, with a clearly visible analog-regulator-node description. Do not use this type to imply a CMOS output or a usable external supply. The source does not give permission to draw an external load. In this project's model, avoiding power_out prevents VDDI from automatically satisfying unrelated power-input requirements
- The current VDDI net contains only U3.C2 and the two capacitor terminals C64.1/C65.1; their other terminals go to ground. C64 is marked 2.2uF/6.3V OLIMEX REF and C65 220nF OLIMEX REF. This topology is consistent with a stabilization node; **the exact capacitance, ESR, and behavior for the selected 1.8V VCCQ remain unqualified**. Samsung p8 labels the core regulator as required for 3.3V VDD. Direction typing does not close that application-data gap
- K5's input type does not establish its EXT_CSD RST_n_FUNCTION setting or safe reset timing

## NC, DNU, RFU, and absent balls

These distinctions remain explicit in every full-map row, even when the CAD electrical class is the same:

- U2: five **NC** (A8, H3, J5, P5, R3), 17 **DNU**, and 64 **NB** positions without physical balls
- U3: 107 **NC**, 13 **RFU**, and 43 positions without physical balls
- NC/DNU/RFU physical balls retain no_connect electrical types and their existing open-circuit dispositions. This is a documented no-use model, not proof that all such balls are unbonded
- DNU means Do Not Use. Samsung explicitly prohibits using RFU. The inspected sources do not grant alternative wiring of NC balls, so no permission to ground, route through, or reuse them is inferred
- NB/absent positions are excluded from the 200/153 pin maps and must not become physical pads merely because they occupy grid coordinates
- H5's functional-but-unused output remains a different category from manufacturer NC, DNU, and RFU

## Independent checks

- Re-extracted all **264 LPDDR4 grid cells** from the manufacturer PDF p10 by their geometric row/column locations. All functions and physical/absent classifications match the existing grid CSV
- Re-extracted all **153 eMMC ball circles** and 46 labels from PDF p5, and checked all **196 grid positions**. The 107 unlabeled circles match the figure's NC legend; 13 labeled balls are RFU. An exactly duplicated N12 circle is counted once
- Compared all **353 pins** between the actual Integrated.kicad_sym, exported XML, and the verified physical maps. Names and electrical types agree after normalizing the XML space-to-underscore spelling of Data Strobe
- Preserved all **130 supply/ground pin types**: U2 has eight VDD1 → VDD1P8, 24 VDD2 and 20 VDDQ → VDD1P1_DDR_IO, 58 VSS → GND; U3 has five VDD/VCCQ → VEMMC_IO, four VDDF/VCC → VDD_3V3, and 11 VSS → GND
- Checked that no NC/DNU/RFU ball has another endpoint attached in the baseline XML

## Machine-readable review files

- `lpddr4-all200-type-audit.csv`: all 200 physical balls, exact source pages, proposed type, current net, no-use category, and limitations
- `lpddr4-proposed-type-corrections.csv`: only the 24 U2 changes
- `emmc-all153-type-audit.csv`: all 153 physical balls with the same review fields
- `emmc-proposed-type-corrections.csv`: only the three U3 changes
- `memory-type-audit-manifest.json`: complete maps at `proposed_pin_types.U2` and `proposed_pin_types.U3`; exact allowlists at `changes.U2` and `changes.U3`; baseline/source hashes and count checks

## Sources and limits

Primary evidence is the Samsung-authored manufacturer documentation, obtained from public mirrors:

- [K4F8E304HB-MGCJ Rev.1.0](https://www.szyuda88.com/home/8/a/2lhtb2/resource/2021/05/26/60ade38424a32.pdf), PDF pp7, 10–12
- [KLMxGxJETD-B041 Rev.1.0](https://datasheet.lcsc.com/lcsc/2007011825_Samsung-KLMAG1JETD-B041_C499919.pdf), PDF pp5, 8, 23

Hashes are recorded in the manifest. Only derived facts and the review tables are included here; raw manufacturer PDFs and rendered page images are not bundled.

These proposed types have **not been applied or ERC-tested by this audit**. Application should use the exact allowlists, retain functional unused markers and analog annotations, then rerun ERC and review any new reports. Direction typing does not qualify package footprint geometry, SI/PI, calibration, voltage margins, memory initialization, supply sequencing, firmware, or the external reset contract.
