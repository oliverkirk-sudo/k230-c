# Internal PMU GPIO66/67 bus review

Finding: the K230 provides programmable GPIO functionality on PMU pads66/67. This is a supported candidate for an internal software I2C bus, not an existing validated DVFS implementation.

## Concrete mapping
- GPIO66 / INT2: ball A10 in the extracted official reference; PMU pad config 0x91000088; GPIO1 portB bit2.
- GPIO67 / INT3: ball A11 in the extracted official reference; PMU pad config 0x9100008c; GPIO1 portB bit3.
- GPIO1 base 0x9140c000. PortB DR offset0x0c, DDR0x10, CTL0x14, EXT_PORTB0x54. Group2 is this portB, not a separate third base.
- TRM12.9.2.3 pad reset0x1124: PMU function2, input enabled, output disabled, pulldown. Select GPIO function1 using IO_SEL[12:11]=01; preserve reserved bits. The BSP models an extra selector bit; do not blindly overwrite reserved bit13.
- Disable internal pullup/pulldown for external-pullup bus operation; ensure appropriate pad input-enable, output-enable, and software GPIO control.

## PMU ownership
Mask INT2/3 bits6/5 in PMU interrupt routing at offsets0x40,0x44,0x48, and detection0x4c; clear stale pending conditions through W1C0x54 bits3/2 after disabling detection. Use targeted read/modify/write, preserving unrelated wake and sequencer sources. Disable RT_PMU_SHUTDOWN_WAKEUP_PAD66 and PAD67 configuration: the PMU shutdown driver otherwise remuxes these pads. Keep64/68 startup sources and70/71 sequencer outputs unaffected.

## Open-drain implementation caution
The inspected BSP's GPIO_DM_OUTPUT_OD is not a safe write-high/release abstraction: kd_pin_write can set output mode and write a1. Implement explicit release (DDR=0, output disabled) and sink (preloadDR=0, enable output); never drive1. Read the actual external input register for ACK and clock-state checking. Serialize register updates against both cores and PMU/pinmux drivers. Verify glitch-free initialization and bus behavior on hardware.

## Regulator observations
TPS62864 Table8-1 confirms56.2k1% gives0.8V/address0x49;86.6k gives0.9V/address0x41. LogicVIH1.0V permits a1.8V bus, subject to confirming PMU pad supply and startup/power-off leakage. VSET/PG is fault-high, valid-output-low, and shares resistor sampling; do not treat it as conventional power-good or load it without checking sampling constraints.

Stopgate: KPU0.9V cold start is not justified merely by a unique address. Canaan's basic electrical table gives0.88V maximum, while its DVFS section lists0.9/1.0V operating nodes. Resolve that conflict with Canaan for the intended silicon/OPP/boot conditions. Prefer an architecture that permits bothCPU/KPU to start0.8V without address collision, pending review. This review does not approve any altered rail limit.

Sources actually read:
- K230 TRM v0.3.1 sections12.5,12.9.2.3/4,14; localtrm.pdf/trm.txt from officialCanaanURL in cold-storage-voltage-review.md.
- https://github.com/canmv-k230/rtsmart/blob/ff6b90f500683f1ef66664ea19e4e8a2294042d3/kernel/bsp/maix3/drivers/interdrv/gpio/drv_gpio.c
- Samecommit: fpioa/drv_fpioa.c,pmu/drv_pmu.c,pmu/pmu_priv.h underinterdrv.
- https://www.ti.com/lit/ds/symlink/tps62864.pdf
- Officialreferenceball extraction /workspace/shared/cm-k230-redesign/engineering/k230-reference-balls.csv (ball locations should receive final independent symbol/pad check).
