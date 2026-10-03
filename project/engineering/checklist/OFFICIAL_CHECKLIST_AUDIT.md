# Official checklist audit ledger

Every numbered section covered; model-level passes only. No submission/contact/simulation/fabrication.

Source: https://kendryte-download.canaan-creative.com/developer/k230/HDK/%E5%8E%9F%E7%90%86%E5%9B%BEPCB%E8%AE%BE%E8%AE%A1CHECKLIST.pdf

| Clause | Page | Requirement | Status | Target | Evidence / next action |
|---|---:|---|---|---|---|
| 1.1a | 1 | I/O voltage | unresolved | BANK0..5_VDDIO; U95; carrier peripherals | Six external bank supplies require matched carrier voltages and startup order. OTP/readback and translation SI remain open. |
| 1.1b | 1 | Power ordering | unresolved | U21 CORE_PGOOD_5V; U24..26; MIPI rails | CORE enables dependent converters. External banks and filtered-rail ramps require measured sequencing; PG structure alone is insufficient. |
| 1.1c | 1 | RTC/LDO order | passed_model | U1 F14/F15; AVDD1P8_PMU | Both pins intentionally share the filtered PMU node. This closes relative net ordering, not ramp/PI qualification. |
| 1.1d | 1 | All supplies/grounds | passed_model | All U1 power_in balls; ADC/CODEC | Every modeled power ball has a named network; external bank sources remain explicit board-boundary requirements. |
| 1.1e | 1 | Analog filters | unresolved | FB202/203/204/207; C231 onward | PLL/VAA/MIPI L-filter topology present. Reference uses120Ω while checklist gives100Ω; impedance/DC-bias/PI and exact approved part require reconciliation. |
| 1.2a | 1 | Boot selection | unresolved | BOOT0/BOOT1; R44..R47; J1 | PhysicalMMC0 baseline retained. Same-OTP SD/eMMC protocol selection and earliest voltage remain unverified. |
| 1.2b | 2 | Boot button | external_boundary_only | Carrier BOOT pins | Core handoff requirement only; no peripheral circuit designed. No button added on core. Carrier must produce a different sampled boot state for recovery; verify actual carrier wiring and reset timing. |
| 1.3a | 2 | 24MHz accuracy | unresolved | Y2; C43/C44; R42 | Exact candidate initial/temp/aging budget does not establish whole-condition20ppm.85°C grade also under review. |
| 1.3b | 2 | Passive feedback | passed_model | R42 between24M pins | 1M feedback present; load/negative-resistance/drive testing remains open. |
| 1.3c | 2 | Active clock option | not_applicable_current_variant | Y1/Y2 passive | No active oscillator is fitted. A later active substitution must revisit supply, XOUT disposition and waveform requirements. |
| 1.3d | 2 | RTC accuracy | unresolved | Y1; C41/C42; R41 | MPN/full-temperature drift and startup not qualified; feedback source is Canaan2023 reference, not01Studio RTC drawing. |
| 1.4 | 2 | DDR mapping | unresolved | U1/U2;65-join matrix | 65 source-exact joins pass against01Studio reference. Recommended Lushan mapping equivalence and proposedMicron training require review; no vendor submission made. |
| 1.5a | 2 | Persistent PMU power | unresolved | AVDD1P8_PMU | Common supply exists while main1V8 runs. Required off/sleep/wake semantics and isolation are not implemented in BSP. |
| 1.5b | 2 | PMU inputs | passed_model | PAD68/R401; PAD64/R402 | INT4 shares PMU supply through0Ω; INT0 is inactive bias rather than local button. Firmware ownership/startup measurement remains open. |
| 1.6a | 3 | Sensor routing/control | external_boundary_only | CSI edge nets; GPIO controls | Core handoff requirement only; no peripheral circuit designed. Physical aliases retained. Sensor pinmux, voltage and carrier connector assignment must be validated for selected peripherals. |
| 1.6b | 3 | Sensor ground contacts | unresolved_compatibility_exception | CSI pairs;140-pin edge contract | Original fixed edge pinout has adjacent pairs without intervening ground (CSI58–63;DSI79–88). Preserve numbering; explicitly review return path/crosstalk, not a claimed checklist pass. |
| 1.7a | 3 | Display routing/control | external_boundary_only | DSI edge nets; GPIO controls | Core handoff requirement only; no peripheral circuit designed. Pin contract retained; software/panel voltage and MIPI lane configuration remain untested. |
| 1.7b | 3 | Display ground contacts | unresolved_compatibility_exception | DSI pairs; edge contract | Original fixed edge pinout has adjacent pairs without intervening ground (CSI58–63;DSI79–88). Preserve numbering; explicitly review return path/crosstalk, not a claimed checklist pass. |
| 1.8a | 3 | MMC assignment/voltage | unresolved | MMC0 selector; U95; externalTF | Intentional departure from default MMC1SDIO: both storage choices useMMC0 to preserve edge contract. ROM-stage support needs evidence. |
| 1.8b | 3 | eMMC pulls | passed_model | R562;R563..570;R572 | CMD22k/DAT47k local pulls and host strobe100k bias present. Unused eMMC H5 output stays open. |
| 1.8c | 3 | SD pulls | external_boundary_only | U95; externalTF socket | Core handoff requirement only; no peripheral circuit designed. Translator internal pulls are documented, but carrier external-pull population and combined strength/RC require confirmation; do not blindly double pullups. |
| 1.9 | 4 | USB ESD | external_boundary_only | USB0/1 edge pairs; carrier sockets | Core handoff requirement only; no peripheral circuit designed. Protection belongs near actual external connector; no socket/ESD device is presumed present from the core netlist. Require low-capacitance selected part and carrier evidence. |
| 1.10a | 4 | MICBIAS setting | external_boundary_only | MIC_BIAS; BSP codec settings | Core handoff requirement only; no peripheral circuit designed. Output setting must match external microphone supply; no active microphone design was selected. |
| 1.10b | 4 | MICBIAS decoupling | corrected_model | C67/C68; U1 E3 | Added4.7uF+100nF locally. Actual effective capacitance and near-pin placement still required. |
| 1.10c | 4 | Microphone AC coupling | external_boundary_only | MICPL/MICNL/MICPR/MICNR edge pins | Core handoff requirement only; no peripheral circuit designed. Raw compatible core signals retained. Determine series100nF placement on carrier; adding it silently inside core could change DC interface behavior. |
| 1.10d | 4 | Headphone AC coupling | external_boundary_only | HPOUTL/HPOUTR edge pins | Core handoff requirement only; no peripheral circuit designed. Carrier coupling/load/amplifier input must be verified. Never connect two driven outputs based on ambiguous prose. |
| 1.10e | 4 | VCM decoupling | corrected_model | C63/C66; U1 F3 | Added missing4.7uF alongside100nF. Near-pin placement and effective value remain open. |
| 1.11a | 4 | PDM wiring/voltage | external_boundary_only | GenericGPIO edge contract; futureMIC carrier | Core handoff requirement only; no peripheral circuit designed. No PDM microphone fitted on core. Selected pinmux, left/right sharing and voltage belong to BSP/carrier acceptance. |
| 1.11b | 4 | I2S wiring/voltage | external_boundary_only | GenericGPIO edge contract; futureaudio carrier | Core handoff requirement only; no peripheral circuit designed. No I2S microphone fitted on core. Selected clock/WS/data and shared-channel policy require integration testing. |
| 1.12 | 5 | SPI flash wiring/pulls | not_applicable_current_variant | No SPIflash fitted | ExposedGPIO remain unaltered. Any carrier flash needs its own pinmux, voltage and pulls; not implicitly provided by core. |
| 2.1a | 5 | Digital PDN placement | deferred_to_layout | CORE/CPU/KPU/DDR_CORE groups | Split rails intentionally differ from merged reference. Local ball-to-cap loops, return paths and total effective capacitance unqualified. |
| 2.1b | 5 | DDR PDN placement | deferred_to_layout | U1 DDR IO; U2 VDD2/VDDQ | Keep SoC-side and memory-side local groups; rectangular packing does not satisfy proximity. |
| 2.1c | 5 | 1.8V PDN placement | deferred_to_layout | VDD1P8; USB; PMU; bank supplies | Common/filtered domain layout and external-bank source boundary must be reviewed. |
| 2.1d | 5 | 3.3V PDN placement | deferred_to_layout | USB3V3; SD; VOUT; externalbanks | Route/load compatibility and carrier power-return paths remain open. |
| 2.2 | 6 | Clock shielding | deferred_to_layout | Y1/Y2 XIN/XOUT | Ground shielding and uninterrupted reference plane required; no routed PCB exists. |
| 2.3 | 6 | DDR layout review | deferred_to_layout | 65 DDR joins; package lengths | Source topology alone is not length/impedance/escape validation. Full SI/PI and qualified review needed; no vendor upload authorized. |
| 2.4 | 6 | eMMC routing | deferred_to_layout | EMMC DAT/CMD/CLK; selector | Apply source length/matching goals, then evaluate added switch discontinuities. No length or HS200 pass claimed. |
| 2.5a | 6 | USB matching/impedance | deferred_to_layout | USB0/1 D+/D- | 90Ω differential and pair-length objectives must include core plus carrier. |
| 2.5b | 6 | USB return/length | deferred_to_layout | USB paths/connector | Continuous ground, via companions, connector distance and neighbor spacing need routing audit. |
| 2.6 | 7 | MIPI RX routing | deferred_to_layout | CSI lanes | 100Ω differential, within-pair/intergroup matching and total-length goals require core+carrier budget. |
| 2.7 | 7 | MIPI TX routing | deferred_to_layout | DSI lanes | Checklist repeats RX-style group names; resolve the intendedTX grouping rather than invent constraints. Preserve continuous return paths. |
| 2.8 | 8 | Audio shielding | deferred_to_layout | MIC/HPOUT/MICBIAS | Ground reference, shielding and stitching require layout and carrier audit. |
| 2.9 | 8 | TF routing | deferred_to_layout | TF_HOST;U95;TFCARD;external socket | Include translation delay and external carrier route; raw trace matching alone cannot prove timing. |
| 2.10 | 8 | SPI routing | not_applicable_current_variant | No coreSPIflash | Carrier SPI use remains application-specific and outside current core routing validation. |
