# Cold-selected MMC0 storage: independent voltage/boot review

Status: candidate architecture, not electrically or boot-ROM qualified. User-approved default is eMMC; selection only with power removed. No external GPIO repurposing is authorized.

## Verified primary evidence

1. K230 hardware guide specifies VDD3P3_SD at 2.7–3.63 V, nominal 3.3 V. This is not a rail to switch to 1.8 V. MMC0 uses dedicated pads, distinct from the ordinary bank I/O supply selection.
Source: https://github.com/kendryte/k230_docs/blob/main/en/00_hardware/K230_Hardware_Design_Guide.md

2. K230 TRM v0.3.1 PDF page 890 describes HOST_CTRL2 SIGNALING_EN bit 3: reset zero corresponds to 3.3 V; setting one initiates 1.8 V signal-regulator switching. This states the controller reset default, not what voltage BootROM actually drives first. PDF page 9 labels BOOT1/BOOT0=10 as eMMC and 11 as SD, whereas the hardware guide identifies the controller paths as MMC0 and MMC1. This does not justify selecting BOOT=11 for a TF card connected to MMC0.
Source: https://kendryte-download.canaan-creative.com/developer/k230/HDK/K230%E7%A1%AC%E4%BB%B6%E6%96%87%E6%A1%A3/K230_Technical_Reference_Manual_V0.3.1_20241118.pdf
Actual complete PDF downloaded, text read: trm.pdf/trm.txt in this directory.

3. The inspected CanMV U-Boot snps_sdhci.c has optional CONFIG_MMC_AUTO_DETECT_VOLTAGE. It reads 0x91213410, converts big-endian, and selects 3.3 V when its low two bits are 3; otherwise selects 1.8 V. Without that option it reads the DTS 1-8-v property. It writes HOST_CONTROL2 and PHY pad configuration; this is not evidence of an external rail-select GPIO. The origin and BootROM meaning of that SRAM value remain unverified.
Source: https://github.com/canmv-k230/u-boot/blob/87041d630cdcd545dacfec19f1e90a093689dada/drivers/mmc/snps_sdhci.c
Extracted actual source: snps_sdhci.c in this directory.

4. RT-Smart drv_sdhci.c sets the same controller bit and uses separate 1.8/3.3 V PHY pad settings. RT_SDIO0_1V8 is a build-time software policy. Changing it alone does not prove safe first-stage boot.
Source: https://github.com/canmv-k230/rtsmart/blob/ff6b90f500683f1ef66664ea19e4e8a2294042d3/kernel/bsp/maix3/drivers/interdrv/sdio/drv_sdhci.c

## Recommended constraints / release gates

- Preserve VDD3P3_SD at its specified supply and use documented MMC0 pad controls, not speculative supply switching.
- Three TMUX1574 devices remain a plausible isolation candidate, subject to the separate TI review. They do not translate voltage. eMMC VCCQ remains 1.8 V and TF signaling 3.3 V in the proposed cold modes.
- Keep complete isolation of eMMC CMD/CLK/DAT0–7; handle reset separately so the inactive powered eMMC can remain reset. Do not leave DAT4–7 directly exposed to a 3.3 V host state merely because TF uses only four data bits.
- Hardware selection must be stable before any bus connection. A default-disabled mux is necessary but cannot remain disabled until U-Boot if BootROM must read that same storage. This circular dependency needs a proved pre-ROM enable/voltage policy.
- Establish BootROM first-drive voltage, mode discovery, MMC0 SD boot support, and reset-time behavior using authoritative Canaan guidance or oscilloscope measurements on a known-good reference. Runtime code is insufficient proof.
- Demonstrate cold boot in each mode and reset/power-collapse behavior with the final power/control circuit. Firmware images must agree with selected device, width, voltage and timing.
- HS200 requires board-level timing/SI validation; 2 GHz switch bandwidth alone is not a qualification.
