# Remaining PDN voltage budgets

The current high-temperature fixed-rail static tolerance model leaves combined budgets of approximately 44.30 mV for CORE, 31.37 mV for DDR IO, 64.48 mV for 1V8 and 175.13 mV for 3V3. The 3V3 lower boundary uses the K230 USB PHY's 3.07 V requirement, not merely the eMMC's looser 2.7 V minimum; its upper boundary uses the memory's 3.6 V limit.

These are residual common-rail budgets, not independent allowances for each effect. Every distribution loss, filter drop, regulator ripple, load transient, noise and unmodeled error must share them. Each filtered branch needs its own audit. CPU/KPU DVFS rails are not covered by this fixed-rail calculation.

As a deliberately zero-reserve illustration, spending the entire CORE budget on a hypothetical 3 A load change would require about 14.77 mΩ target impedance. The 3 A comes from the official recommended converter capacity; it is not a measured current waveform. Actual frequency-dependent target impedance requires the real load-step spectrum and a sensible split of the remaining budget. No DDR amperage or package ESL was invented.

All components remain on top. The center of a BGA cannot receive a directly adjacent bottom-side capacitor, so local power/ground ball vias and suitable continuous planes must connect the external bypass parts. A short projected package-edge distance alone is not loop inductance. Conversely, distance alone cannot prove failure if a suitable low-inductance plane structure exists. The proposed stack has not been extracted or simulated, and mounted capacitor models/lot-temperature bounds remain incomplete.

The machine-readable file preserves inputs and hashes. It is a design budget, not a PI simulation, PDN impedance measurement, or power-integrity pass. No restricted IBIS data were used.
