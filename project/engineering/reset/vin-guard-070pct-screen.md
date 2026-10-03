Integration note: this independent review made no CAD edits. Its conditional divider budget was subsequently adopted in the HT-DRAFT11 high-temperature candidate; nominal values and nets are unchanged.

# Compact VIN guard: conditional 0.70% resistor screen

Accept as a conditional procurement/design screen, preserving the approximately 4 V VIN-loss role. It does not establish an exact loaded brownout boundary. No CAD was changed. Reviewed current generator: U89 TPS3808G01DRVR is powered by VDD1P8; R525 = 88.7 kΩ, R526 = 10 kΩ, R527 = 10 kΩ.

## Derived corners

For current into SENSE defined positive, VIN_trip = V_SENSE × (1 + R525/R526) + I_SENSE × R525. Independent resistor extremes are used, with total error ±0.70% each, threshold 0.405 V ±2%, and bias ±25 nA.

- Nominal falling threshold: 3.997350 V
- Falling minimum: 3.866257 V
- Falling maximum: 4.131190 V
- Rising maximum using 3% hysteresis: 4.255059 V
- No minimum hysteresis is specified; conservative rising lower screen is the falling minimum

The rising calculation applies 1.03 to the actual maximum comparator threshold, then adds the positive bias term. Its bias bound is CONDITIONAL: the electrical table specifies ISENSE at VSENSE = VIT, not explicitly at VIT + VHYS. Confirm extension to the release point before treating 4.255059 V as a guaranteed release limit. With zero bias that upper release value is 4.252826 V; the assumed bias contributes 2.233 mV.

Compared with the old ±0.15% resistor screen, the falling range expands from 3.904643–4.090527 V and maximum rising from 4.213176 V. The approximate 4 V function is preserved.

## Supply and headroom implications

TPS62824/25/26 and TPS62864 minimum input is 2.4 V; TPS62827 minimum is 2.5 V. The earliest loss boundary in this screen is still 1.366 V above the largest of those minima. This does not replace each converter's output-specific dropout requirement.

The previously derived 3V3 maximum is 3.392164 V using scaled 45.3 kΩ/10 kΩ feedback, ±0.70% resistor error, ±1% PWM reference and FB leakage. Thus minimum VIN guard threshold leaves 0.474092 V static difference. At a hypothetical full 3 A this corresponds to a 0.158 Ω total series-drop budget before reserving ripple, wiring and dynamics. This is a budget, not a verified regulator capability: TPS6282x's 100%-mode dropout equation uses switch resistance that is only characterized typically. Hot maximum switch loss, inductor DCR, load, PCB/input drops and transient behavior remain required checks.

A delivered VIN above 4.255059 V plus margin would satisfy the modeled startup threshold. Input-source minimum and distribution drop must be established; calling the source “5 V” alone does not guarantee this. Upper VIN must also stay within the converters' 5.5 V limit; this guard does not detect overvoltage.

## Resistor feasibility

Vishay TNPW0402 covers both values with 0.1% initial tolerance and 10 ppm/K. Manufacturer order-code construction gives candidate TNPW040288K7BYED and TNPW040210K0BYED (ED packaging); these are schema-supported candidates, not an independent stock/lifecycle verification.

Keep ±0.70% explicitly as a total mission-profile screen, not the initial tolerance. At 100 K, 10 ppm/K consumes 0.10%, leaving additional reserve versus the earlier 25 ppm/K allocation. Film temperature, assembly shift, aging duration, humidity and mechanical stress still require an actual allocation. A manufacturer endurance test does not establish an arbitrary product lifetime. At 5.5 V the divider dissipates roughly 0.31 mW total, so self-heating from this divider is small but enclosure/board temperature still applies.

## Retained qualification gates

The U89 supply must remain within its specified range for this accuracy to apply. Held-up 1V8 can sustain VIN-loss indication, but simultaneous collapse cannot be inferred from static corners. SENSE assertion delay is 20 µs typical without a maximum; CT-open release is 12–28 ms. Rail slew rate, short dips, PG loading, input/rail startup order, stored energy and downstream reset latency require characterization. No strict minimum-rail protection under arbitrary falls is claimed.

Sources read: [TI TPS3808 Rev N](https://www.ti.com/lit/ds/symlink/tps3808.pdf), tables 4-1, 6.5, 6.6 and §7.3; [TI TPS6282x](https://www.ti.com/lit/ds/symlink/tps62827.pdf), recommended conditions, electrical table and §7.3.3; [TI TPS62864](https://www.ti.com/lit/ds/symlink/tps62864.pdf), recommended conditions; [Vishay TNPW e3, 10-Apr-2026](https://www.vishay.com/docs/28758/tnpw_e3.pdf), resistance/TCR and ordering tables. Local full PDF text, not search snippets, was used for the numerical checks.
