# Hardware reset/storage interlock: reviewed topology, not yet integrated

A passive RC reset alone does not establish rail validity. The candidate below works before firmware and does not depend on loading U-Boot through a disabled storage bus. It has unresolved worst-case constraints, so it has deliberately NOT been drawn as an approved complete circuit or connected to GLOBAL_DISABLE.

## Concrete candidate and pin contract

Two TPS386000RGP supervisors, powered by VIN_5V, could monitor eight independent nodes: CORE, CPU, KPU, DDR I/O, local DDR CORE, 1.8 V, 3.3 V, and VIN_5V. The external bank supplies remain carrier inputs and would need a separate external-supply qualification policy. Each channel uses a resistor divider into a 0.4 V sense input. Ground SENSE4H for undervoltage-only channel4 use. Pin table: MR1; CT4=2; CT3=3; CT2=4; CT1=5; SENSE4H6; SENSE4L7; SENSE3=8; SENSE2=9; SENSE1=10; NC11 (TI recommends ground); GND12; VREF13; VDD14; RESET1..4=15..18; WDO19; WDI20; exposed pad ground. MR must be tied high; WDI can be tied low while WDO remains explicitly unused; VREF unused. CT open is a documented fixed delay selection, not an accidental floating logic input.

Eight RESET open-drain outputs wire together as ALL_RAILS_GOOD, pulled up to 3.3 V with at least10 kΩ. SN74LVC1G06DBV open-drain inverter: A2=ALL_RAILS_GOOD, GND3, Y4=GLOBAL_DISABLE, VCC5=3.3 V, NC1 unused. Existing GLOBAL_DISABLE pullup keeps switches disabled when this gate is high impedance. TI specifies Ioff at VCC=0, but this must NOT be generalized to every brownout voltage.

TPS3808G01DBV delay stage: VDD6=3.3 V, GND2, MR3=ALL_RAILS_GOOD, SENSE5 held above its0.405 V threshold, CT4 left open, RESET1 to1.8 V RSTN. Its20 ms typical delay is12–28 ms specified, providing separation from the TMUX1574 maximum35 µs normal turn-on time. Existing reset100 nF must be re-evaluated/optionally DNP when this stage is adopted; its added sink load cannot be ignored in brownout timing.

## Ideal powered truth sequence

- Any monitored rail below its configured threshold: ALL_RAILS_GOOD=0; storage disabled; RESET asserted
- All rails become valid: channel delays elapse; ALL_RAILS_GOOD rises; inverter enables the selected storage path
- After the additional reset-stage delay: RSTN releases and BootROM may access storage
- Any rail fails: reset asserts and storage disables, subject to specified propagation/pullup/load timing

This sequence does not establish that the selected bus voltage is correct. OTP/ROM policy and TF translation are separate requirements.

## Why component choice/thresholds are not frozen

TPS386000 full-temperature VIT is0.396–0.404 V, sense current±25 nA, and positive-going hysteresis can be10 mV. The 1% threshold bound and2.5% maximum hysteresis are significantly larger than typical headline values.

Current DDR regulator nominal1.107 V has calculated static minimum1.094927 V, excluding distribution and ripple. The K230 DDR I/O minimum is1.06 V. Even with an ideal divider, guaranteeing undervoltage trip no later than1.06 V requires nominal trip at least1.06/0.99=1.070707 V. Its worst-case rising threshold is at least1.070707*(1.01+0.010/0.4)=1.108182 V, ABOVE the regulator's static minimum. Resistor tolerance, input bias and ripple worsen this. Therefore this supervisor cannot meet both strict DDR undervoltage protection and guaranteed restart with the current regulator corner budget. Do not pick a convenient nominal resistor pair and claim the gate closed.

Possible engineering resolutions requiring further verified design (not a user capacity/performance decision): a sufficiently tighter-threshold/hysteresis monitor for this rail; a better-controlled regulator and distribution budget; or a explicitly weaker fault-detection specification while separately proving startup validity. Arbitrarily raising the DDR supply to suit a supervisor consumes maximum-voltage/ripple margin and has not been adopted.

VIN-off while downstream rails are held up is another blocker: TPS386000 RESET is defined only above0.9 V supply, normal operation≥1.8 V; TPS3808 RESET is undefined below0.8 V. A hold-up/back-power analysis or independently powered fail-safe circuit is required. Ordinary powered truth-table simulation cannot prove this state safe.

## Sources

- TI TPS386000 SBVS105F, pin/functions pp4–5, full electrical limits p7, output behavior§8.3.4: https://www.ti.com/lit/ds/symlink/tps386000.pdf
- TI TPS3808 SBVS050N, SOT23 pin table, full electrical/switching limits: https://www.ti.com/lit/ds/symlink/tps3808.pdf
- TI SN74LVC1G06 SCES295AB, DBV pin table and Ioff/operating limits: https://www.ti.com/lit/ds/symlink/sn74lvc1g06.pdf
- Canaan hardware guide§3 power requirements: https://github.com/kendryte/k230_docs/blob/main/en/00_hardware/K230_Hardware_Design_Guide.md

Only derived design facts and links are distributed; vendor PDFs remain external evidence.
