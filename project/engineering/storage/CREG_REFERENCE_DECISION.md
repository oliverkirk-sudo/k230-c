# CReg candidate now has same-base-part board evidence

OLIMEX official A20-OLinuXino-MICRO RevN circuit names U26 KLMAG1JETD-B041003. Its e16Gs16M populated BOM dated2024-03-13 explicitly includes U26 and both VDDI capacitors: C2512.2uF/6.3V (0603) and C250220nF (0402). Visual review traced both from C2 VDDI to GND, not from the external VCCQ rail. The extra003 suffix is retained as the board's published identifier; it is not silently discarded as an exact ordering equivalence.

Our C64=2.2uF/6.3V and C65=220nF are now marked reference-derived candidates. This is a stronger basis than the earlier100nF reference for a different Samsung family. It is NOT a Samsung normative capacitor/ESR guarantee: OLIMEX connects both VCC and VCCQ to its3.3V eMMC rail, whereas this proposal targets1.8V VCCQ. Exact required effective capacitance, ESR and startup behavior at1.8V still need manufacturer or qualified bench evidence. No full vendor schematic is redistributed.

Sources and hashes: creg-reference-evidence.json. Official repository: https://github.com/OLIMEX/OLINUXINO/tree/master/HARDWARE/A20-OLinuXino-MICRO/1.%20Latest%20hardware%20revision
