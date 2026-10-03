# Cold storage firmware integration contract

This is a source-based integration plan and executable requirements model, not a patched/compiled BSP. It cannot repair BootROM behavior or verify OTP. Never execute OTP programming from this contract.

## Source baseline

RT-Smart repository https://github.com/canmv-k230/rtsmart at ff6b90f500683f1ef66664ea19e4e8a2294042d3, `kernel/bsp/maix3/drivers/interdrv/sdio/drv_sdhci.c`. Inspected local source is clean at that revision.

- Lines 296–301: `io_fixed_1v8` selects the host 1.8 V signaling setting
- Lines 832–834: same property selects the SDHCI power-control code; this is a controller-register setting, not an external GPIO regulator switch
- Lines 1659–1673: compile-time eMMC/1.8 V selections
- Lines 1697–1715: bus width, eMMC-only HS200 and nonremovable flags, plus OCR derived directly from the host voltage property
- Current driver advertises High-Speed for SD but does not thereby prove UHS support or timing

Samsung KLMxGxJETD-B041 Rev1.0 §7.1/Table22 has a device-specific distinction: its OCR describes **VDD/VCCQ**, while VDDF/VCC must remain 2.7–3.6 V regardless of OCR. Therefore keep its low-voltage OCR selection for the 1.8 V eMMC. Do not “fix” this eMMC to a 3.3 V OCR merely because flash VCC is 3.3 V. Source: https://datasheet.lcsc.com/lcsc/2007011825_Samsung-KLMAG1JETD-B041_C499919.pdf

## Separate physical and protocol attributes

| Attribute | eMMC assembly/image | TF assembly/image |
|---|---|---|
| Host physical pads | fixed 1.8 V | fixed 1.8 V |
| Device main supply | 3.3 V flash VCC | external card 3.3 V |
| Device signal side | 1.8 V VCCQ | 3.3 V via NVT4858 |
| OCR requested window | Samsung low-voltage bit7, VDD1.70–1.95 V | 3.2–3.4 V supported card supply window |
| Data width | 8 | 4 |
| Performance target | HS200 after tuning | Default25/High-Speed50 MHz after negotiation |
| UHS voltage switching | not applicable | disabled; no card-side 1.8 V rail |
| Removable | no | yes, subject to carrier detect/power contract |

The TF build needs host-pad voltage independent of card OCR. Simply enabling RT_SDIO0_1V8 in the existing generic TF path causes incorrect low-voltage card OCR. Keep the host PHY at 1.8 V while selecting the TF 3.3 V OCR; audit every related reset/reinitialization path and SDHCI POWER_CONTROL interpretation. Do not change the working eMMC low-voltage OCR behavior without source justification.

## Explicit mode and startup prerequisite

JP1 is a power-off hardware choice, with no assigned SoC sensing pin. Until a documented automatic mechanism exists, use two explicit images/manufacturing configurations matched to that assembly. Do not steal an exposed GPIO or infer physical mode from driver defaults. Wrong image/mode is a failed acceptance condition.

Both modes require verified pre-ROM host voltage. A U-Boot or RT-Smart patch runs too late to protect the first BootROM transaction. Public OTP form options alone do not guarantee first-drive behavior. Evidence/readback plus first-drive waveform qualification is still required before populating R528. Default R528 DNP means this prototype cannot load boot code through the inhibited storage path.

Local inspected U-Boot `snps_sdhci.c` uses either `1-8-v` DT property or CONFIG_MMC_AUTO_DETECT_VOLTAGE with a read at 0x91213410; it maps low two bits equal3 to non-1.8V. That existing automatic path is not evidence that the new external translator topology can use it unchanged. Freeze its integration until the producer/meaning and reset-stage behavior are established. Changing boot straps to a generic “SD” value is also not justified when the selected card remains on MMC0.

## Required implementation and validation

1. Introduce separately reviewed board policy for host pad voltage, device OCR, width and capabilities in both U-Boot and RT-Smart; ensure recovery/reset paths reuse it
2. Preserve eMMC HS200 capability and tuning; exclude TF HS200/UHS/8-bit negotiation and limit its requested maximum to50MHz
3. Match cold hardware selection to explicit image variant. Determine how each image is loaded before assuming TF cold boot works
4. Verify carrier socket power, card detect and hot insertion behavior; this authorization permits cold mode selection only
5. Bench-check identification clock, OCR exchange, bus-width transition, tuning, read/write integrity, reset and power cycling in each mode, with all corner rails and representative cards
6. The standalone `storage_policy_model.py` checks 64 prerequisite combinations and mode attributes. It has no hardware/register access and is not a BSP test or proof of bootability


## Separate unresolved ROM media-protocol gate

Same OTP voltage compatibility does not establish that BootROM recognizes both SD and eMMC on the same physical MMC0. The hardware guide Table3-2 names BOOT1/0=10 as MMC0 and11 as MMC1; TRM §1.4.2 labels these as eMMC and SD. The inspected official burning-tool documentation says SDIO0/1 may connect to either device, but a USB-loaded programming path is not proof of autonomous boot auto-detection. No inspected primary source closes this ambiguity. Do not change BOOT straps or claim two images resolve it.

Required acceptance evidence: authoritative ROM protocol-selection/auto-detection description for both devices on MMC0 under the same reviewed immutable OTP profile, followed by cold-start validation of both physical selections without rewriting OTP. If this is unsupported, the architecture needs a reviewed alternative boot path or a user-visible functional decision; runtime drivers alone cannot repair it. The executable model now requires `rom_media_protocol_verified` separately and defaults it false.

Sources: [official hardware guide](https://github.com/kendryte/k230_docs/blob/main/en/00_hardware/K230_Hardware_Design_Guide.md), [TRM V0.3.1](https://kendryte-download.canaan-creative.com/developer/k230/HDK/K230%E7%A1%AC%E4%BB%B6%E6%96%87%E6%A1%A3/K230_Technical_Reference_Manual_V0.3.1_20241118.pdf), [official burning-tool guide](https://github.com/kendryte/k230_docs/blob/main/en/01_software/pc/burntool/K230_SDK_Burntool_User_Guide.md). These were checked 2026-09-30; no hardware operation was performed.
