> 更新：用户已接受存储二选一；本文件保留前期调查记录。当前新隔离子电路和剩余BootROM门槛见SELECTOR_DESIGN_CN.md，不能把下面历史阻塞项理解为尚未询问模式选择。

# CM-K230 TF / eMMC pin-function review

Date: 2026-09-30. This review is primary-source research, not a measured module netlist.

## Result

The 01Studio CM-K230 product PinOUT explicitly identifies edge pins 17/18/19/20/21/22 as MMC0 D0/D1/D2/D3/CLK/CMD. The prior generic Canaan CanMV MMC1/IO54–59 example is not the correct source for these edge pin functions. Keep these two groups distinct.

The 01Studio firmware eMMC variant uses controller 0: RT-Smart enables SDIO0 eMMC, 1.8 V, HS200 and 8-bit width; U-Boot's corresponding device tree enables mmc0 with 1-8-v. Its shared I/O mux labels IO54–59 as MMC1 -> WIFI. This is corroborating board-family firmware evidence, not proof of the original CM-K230 module's resistor/switch/assembly topology.

The published edge function maps to the Canaan reference SoC balls as follows: 17/D0/D5, 18/D1/C5, 19/D2/B5, 20/D3/C6, 21/CLK/A5, 22/CMD/D6. SoC ball identities are independently supplied by the local authoritative Canaan reference extraction. These are function-derived endpoints, not verified continuity through the original module.

## Remaining release blocker

Public sources inspected do not establish whether the eMMC-equipped module's TF edge pins are connected directly, through resistors/switches, depopulated, or otherwise isolated from the MMC0 eMMC bus. They do not establish simultaneous eMMC plus external SD-card support or the TF edge I/O voltage in every assembly variant. An eMMC 1.8-V configuration cannot justify exposing these nets to a 3.3-V SD circuit. Do not short TF pins to IO54–59, connect an external SD card to an eMMC bus, or mark this topology electrically compatible without verification.

The product documentation contains apparent unrelated transcription errors (e.g. pin119 GPIO23 where the verified symbol says GPIO13), so retain its six-pin MMC0 mapping as explicit manufacturer-declared function and require hardware evidence before fabrication release.

## Exact powered-off sample test plan

1. Record module SKU, PCB revision, eMMC marking and populated parts; inspect both faces under magnification. Disconnect all power, USB, battery, carrier and memory cards. Verify rails are discharged before resistance testing. Use an ESD-safe meter with a documented low test voltage/current suitable for semiconductor assemblies. Do not use a megohmmeter or force current into inaccessible BGA balls.
2. Confirm edge numbering from mechanical artwork, not symbol graphic coordinates. Measure lead resistance. For each of edge17..22, measure resistance in both polarities to each of edge28..33 (full 6x6 matrix). Priority same-function test pairs are 17↔30, 18↔31, 19↔32, 20↔33, 21↔29, 22↔28. These are hypothesis tests only, not proposed wiring. A beep alone does not establish copper continuity; record ohms, polarity, settling and lead-compensated result. Semiconductor and pull-up paths may conduct asymmetrically.
3. Trace each TF edge signal to accessible series-resistor pads/test vias. Identify the actual eMMC part/package and pinout from its manufacturer data before testing to eMMC-side breakout vias or series components for DAT0..3/CLK/CMD. Label component side and photograph every verified endpoint. No blind BGA probing. Where no physical access exists, leave UNKNOWN, or use professional X-ray/netlist extraction rather than guessing.
4. For each TF pin, also log resistance to GND, VOUT_3V3 (edge7), VOUT_1V8 (edge8), BANK4_VDDIO (edge23) and any identified MMC0/eMMC VCCQ regulator output, in both polarities. These results can reveal pull-ups or protection paths but do not alone prove I/O voltage or direct net identity. Repeat on SD-only and 16GB-eMMC samples if both variants are required.
5. If a populated switch/buffer is present, powered-off open circuit does not establish operational isolation. Identify its part, circuit and control. Only after passive mapping, arrange separately controlled powered tests of supply/VCCQ, boot source and host initialization. Never insert a 3.3-V SD card as an exploratory test into an unverified 1.8-V eMMC path.

Acceptance requires a reviewed schematic for TF edge behavior in the intended eMMC assembly, plus documented voltage/boot behavior and the required simultaneous-use cases. If edge pins intentionally become unavailable in the source eMMC variant, document that precisely rather than promising simultaneous storage.

## Sources and searched scope

See sources.json for direct URLs, pinned RT-Smart and U-Boot commits, and SDK config selection. Local evidence copies preserve original licensing comments where present; SHA256SUMS covers those files. The original Chinese module PinOUT is saved as 01studio-module-doc.md; English HTML retrieval is supplementary.

Examined: 01studio-lab/CanMV-K230 repository landing page and hardware package already supplied in /workspace/shared/cm-k230-repo (module symbol, footprint and carrier schematic); 01Studio Chinese source and English product documentation; kendryte/canmv_k230 BUILD.md; official manifest; kendryte/k230_rtos_sdk 01studio configs; canmv-k230/rtsmart 01studio configs and pinmux; canmv-k230/u-boot 01studio DTS/config/mux. Searches included exact CM-K230/TFCARD plus 01studio eMMC/defconfig queries. GitHub API tree retrieval rate-limited; direct official git clones and raw source succeeded. No external contact made.

The only unresolved part of the six-pin question is physical original-module topology and variant behavior, not the documented controller assignment.
