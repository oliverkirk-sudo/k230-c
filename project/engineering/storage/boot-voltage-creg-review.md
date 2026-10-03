# BootROM and VDDI: bounded primary-source review

2026-09-30 continuation. This pass inspected the existing exact-part Samsung Rev1.0 datasheet, an additional Samsung Rev1.1 family datasheet, their VDDI architecture figures, the Canaan eMMC reference schematic image, K230 TRM, official board-adaptation guide, and selected pinned CanMV U-Boot sources. It does not establish absence from all public/private documentation.

## Boot voltage: new material evidence
Canaan's official new-board adaptation guide explicitly lists SDIO0 IO voltage as an OTP boot-configuration setting, separately from U-Boot 1-8-v and Linux io_fixed_1v8 settings. It warns that incorrect OTP or voltage configuration may damage the chip. This is evidence that boot-voltage policy requires attention to OTP state, not just a cold external bus-select strap.

Source: https://www.kendryte.com/k230_linux/zh/main/advanced_adaptation_guide/new_board_adaptation_doc.html (section 开发板 OTP烧写, SDIO0 IO电压).
The linked configurator URL https://www.kendryte.com/zh/tools/otp_config_generation_tool returned generic home content to the retrieval tool; the linked example image returned a burning-tool screenshot rather than a useful voltage-selection table. No OTP file was generated or programmed.

The inspected snps_sdhci.c consumer still establishes only this software rule: read0x91213410, byte-swap as big-endian, low two bits equal3 -> use3.3V; otherwise -> use1.8V, when CONFIG_MMC_AUTO_DETECT_VOLTAGE is enabled. The inspected k230_boot.c, k230_spl.c, k230_platform.h, k230_atag.h and k230_image.py did not reveal the producer or a documented complete encoding. TRM maps this address into the0x91210000 security address region; calling it a proven standalone peripheral register would overstate the evidence.

The exact first driven voltage/timing at MMC0 after reset, OTP/default-state behavior, and whether the same programmed device can safely cold-select fixed1.8V eMMC or3.3V TF remain unresolved in this bounded pass. Do not infer those from the runtime consumer or generic controller reset value.

Conditional draft: preserve the isolation schematic and explicit ROM-voltage gate. Do not hardwire bus enable on the assumption of automatic voltage discovery. Qualification needs Canaan's default/programmed OTP behavior, readout of intended silicon configuration, and first-drive measurements in both modes. An alternate verified bootstrap medium followed by software-controlled bus enabling is a possible architectural investigation, not an approved modification or completed solution.

## VDDI/CReg
Samsung Rev1.0 exact-part PDF p5 identifies VDDI as an internal regulator-stabilization node. Its p8 Figure5 visually shows CReg to ground and labels the regulator required for3.3V VDD(VCCQ). It gives no numeric CReg capacitance, ESR window, nominal VDDI voltage or blanket permission to omit the capacitor at1.8V VCCQ.

An additional Samsung-authored Rev1.1 family datasheet including KLMAG1JETD-B041 was downloaded and searched. Its architecture section likewise did not resolve these numeric requirements.
Source: https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/791/Samsung-eMMC_2D00_2611204514.pdf
Local files: emmc-rev11.pdf / emmc-rev11.txt.

Canaan's actual hardware-guide Figure3-24 was downloaded and visually inspected. It connects C2 VDDI via C24=100nF/16V to ground. However its part is KLM4G1FETE-B041, not KLMAG1JETD-B041. This is genuine reference precedent for a different part, not a normative recommendation for the chosen16GB device.
Source: https://raw.githubusercontent.com/kendryte/k230_docs/main/zh/00_hardware/images/HDG/image035.png
Local image: canaan-emmc-image035.png.
An attempted exact-part FCC board-PDF retrieval returned a non-PDF page; no electrical claim was derived from it.

Conditional draft: retain a local C2-to-ground capacitor position with value/status explicitly pending exact-part manufacturer confirmation. If100nF/16V is shown as a provisional reference-based option, label its different-part provenance and keep it unqualified; do not label it Samsung's specified value. Do not tie VDDI to VCC/VCCQ or export it as a supply. Obtain exact required effective capacitance, ESR, rated-voltage margin and behavior at1.8V VCCQ before release.
