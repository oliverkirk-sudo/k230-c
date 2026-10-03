# Compact startup/reset/isolation contract

This candidate deliberately separates normal startup supervision from strict per-rail fault protection. The extra eight-channel monitor topology is frozen in cad/instrumented-reference. No decoupling was removed to obtain this consolidation.

## Actual compact connections

- U21 CORE PG still enables the other five converters. It is NOT tied into the downstream PG wired-OR; doing so would create a startup deadlock
- U24 DDR, U25 1.8V and U26 3.3V PG outputs join FIXED_RAILS_PGOOD_3V3 through their open-drain outputs. Redundant old1.8V PG pullups were removed
- U89 TPS3808G01, powered from1.8V, monitors divided VIN. It can hold this PG node low when VIN disappears but1.8V is held up
- R527=10k addresses the low-1.8V guard sink limit. A3.3k pullup was rejected. Normal static leakage/high/low margins must use the final net, not old eight-monitor totals
- U94 SN74AUP1G97 is configured as Schmitt AND: B1=GND, A3=PG, C6=external RSTN. Thus the external100k/100nF RC is not applied to an ordinary CMOS gate with a limited input slew specification
- U90 TPS3808G01 delays RESET_DELAYED_1V8 release; R530100k pulls up only this intermediate node, and U91 SN74AUP1G17 Schmitt push-pull buffer drives SOC_RSTN. The earlier parallel open-drain bypass is removed. The external RSTN net itself remains input-only
- U92 is a second Schmitt AND combining PG and BOOT_VOLTAGE_QUALIFIED_1V8. U93 open-drain inversion generates GLOBAL_DISABLE at the existing3.3V pullup level
- R528 is DNP by default; R529 pulls the qualification input low. This enables safe fully-powered static isolation for review/bring-up, not proof of arbitrary power-ramp behavior

Both TPS3808 instances use the exact DRV pin remap with EP7 grounded. Do not reuse DBV pin numbers. The compact logic uses DRL5 for06/07 and the distinct DRL6 for97.

## Protection and timing limits

TPS6282x PG rising threshold can be94–98% of the setpoint and falling threshold90–94%. At DDR1.1196V, a94% indication is about1.0524V, below the RAM's1.06V minimum. Therefore this network is NOT a proof of minimum-voltage-before-reset protection. The reset delay supplies startup settling time, but actual cold/hot/load/input-ramp waveforms must establish operating margin. CPU/KPU ramp timing is considered through their common enable and delayed reset; they no longer have independent external voltage fault detectors in this compact variant.

The documented TPS3808 CT-open delay is12–28ms during its specified operating conditions. This is comfortably longer than the mux's35µs normal turn-on maximum, but does not bound all supply-ramp, brownout or deglitch delays. Never replace a typical assertion time with a guaranteed maximum.

Instrumented corner calculations remain useful diagnostics, not the compact reset trip thresholds. DDR setpoint1.1196V and low-DCR R220 remain in the common power candidate; actual voltage at memory balls must include distribution and noise through20MHz in Samsung's DC limits.

Required tests: monotonic and slow ramps, supply held up in each combination, external reset, regulator current-limit startup, hot/cold/full-load operation, wrong/missing qualifier link, both cold storage modes and TF insertion. No claim of such hardware testing is made.

Sources: TI TPS62827/TPS62864/TPS3808/SN74AUP1G97 data sheets, the linked source manifests and pin maps. No OTP or manufacturing command is authorized by this document.

## Post-v7 independent static review (old direct-reset topology superseded)

The current 10k R527 worst-case guard sink demand is approximately0.310mA, below the0.4mA TPS3808 guarantee at the low1.8V operating corner. Three converterPG outputs, one guard and two AND inputs sum to about1.6µA leakage, producing approximately16mV pullup loss. These are static estimates, not measured transient results.

R530 remains100k. A10k alternative would improve released-high leakage/RC margin but demands about61µA at0.8V/VOL0.2V, exceeding the TPS3808 low-supply15µA POR test load and AUP low-supply20µA condition. It was not adopted. The released-high worst-case budget still needs the K230 reset-pad leakage/threshold and a guaranteed powered-off-output leakage bound for the AUP open-drain output. The default storage interlock does not close this reset guarantee.

## Current buffered reset change

The following BUFFERED_RESET_REVIEW.md and buffered-reset-static-screen.json supersede the previous direct-reset R530 discussion. No SoC load is on the100k intermediate node. U91 now drives the SoC with guaranteed valid-supply output strength under the explicitly conditional generic10µA/19k input model. This removes reliance on unspecified powered open-drain leakage. It does not guarantee maximum assertion latency or arbitrary partial-power behavior. The external RSTN remains a Schmitt request input only.
