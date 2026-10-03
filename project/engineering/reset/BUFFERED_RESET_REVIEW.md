# Buffered reset alternative: independent bounded review

2026-09-30. Verdict: YES as a conditional valid-supply candidate. This removes the two weak-node loading uncertainties; it is not a complete brownout guarantee. No CAD changes made.

## Proposed net contract
U90 TPS3808G01DRVR pin6 RESET -> RESET_DELAYED_1V8; R530100k connects this node to VDD1P8. Replace U91 with SN74AUP1G17DRLR: pin1 NC, pin2 RESET_DELAYED_1V8, pin3 GND, pin4 SOC_RSTN, pin5 VDD1P8. Keep its local100nF bypass. No other load or external connection belongs on the intermediate node. Remove the former parallel bypass connection. External carrier RSTN stays a request input, not connected to the push-pull output.

## Source facts
TI AUP1G17 RevJ pages3–7: DRL pin map above; supply0.8–3.6V; input leakage0.5uA maximum; VOH>=VCC−0.1V at20uA; VOL<=0.35V at1.9mA, VCC1.65V. Schmitt thresholds at1.65V are VT+<=1.29V and VT−>=0.47V. Temperature range is−40 to85C. Ioff atzero supply does not establish all intermediate-supply behavior.
TI TPS3808 RevN: RESET leakage<=0.3uA, CT-open delay12–28ms, MR-to-RESET150ns typical with no maximum listed. Its low-supply POR output guarantee uses15uA.
K230 workbook independently read: B9 RSTN is VDD1P8/LVCMOS18/input; default-state sheet says PU/input. Visually inspected datasheet pages29–30 show general-IO VIH0.65*VDDIO, VIL0.35*VDDIO, leakage±10uA and pullup19–39k. Dedicated RSTN applicability of these numerical limits is not explicitly established by the inspected material. PU presence is supported independently; its resistance is conditional.

## Calculated margins under those declared assumptions
Intermediate leakage is0.8uA. With100k/1%, maximum loss80.8mV and rail minimum1.778441V, intermediate high is>=1.697641V. This is407.6mV above the tabulated1.65V Schmitt VT+ maximum. U90 low output<=0.4V leaves70mV against the tabulated VT− minimum. Do not label interpolated Schmitt thresholds as guaranteed: final full-rail-range signoff must accept/verify the manufacturer's discrete supply-point interpretation.
Final high output with10uA sink leakage meets the20uA test load: at the same rail, margin above0.65*VDD is0.35*VDD−0.1, at least522mV. The internal PU helps high state and is not needed for this calculation.
For low state, even assigning19k PU and10uA adverse leakage, load is at most1.821641/19000+10uA=105.9uA, well below the1.9mA test load. VOL0.35V is below0.35*1.778441=0.622454V, leaving272mV of conditional low margin. This avoids treating the old100k alone as the complete SoC load.

## Explicit tradeoffs and remaining gates
The fast parallel clamp is removed. A maximum asynchronous assertion time cannot be derived from150ns typical MR delay; buffer propagation does not fix that omission. CT-open timing applies only under specified operating conditions. Intermediate RC adds release time; exact capacitance/rise behavior must be accounted for.
At0.8V, intermediate100k load atVOL0.2V is about6.06uA plus buffer input leakage, fitting the supervisor15uA test load. However final-buffer low-supply load may include the SoC PU and exceed its0.8V20uA drive condition. Thus final low-supply reset assertion remains unqualified. Fully powered operation, partial-power operation and arbitrary brownout must not be conflated.
Numeric reset-pad applicability, full supply/temperature corners, external reset pulse requirements, actual capacitance and power-ramp measurements remain qualification items. No further part search is required for this candidate checkpoint.

Sources: https://www.ti.com/lit/ds/symlink/sn74aup1g17.pdf ; https://www.ti.com/lit/ds/symlink/tps3808.pdf ; K230_PINOUT_V1.2_20240822.xlsx (official Canaan workbook); manufacturer-authored K230 datasheet mirrored at https://atta.szlcsc.com/upload/public/pdf/source/20240304/CED0BDC8B8BEDC72BFC23F1C8A2ED83A.pdf .
