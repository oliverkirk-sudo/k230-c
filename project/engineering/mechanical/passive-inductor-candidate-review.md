# Inductor reservations for the compact 237-part design

Audit dated 2026-09-30. These are placement reservations and selection candidates, not approved magnetic components or manufacturing footprints. The frozen master is unchanged.

## Verified correction: L22 and L23

The official Murata DFE201612E reference specification J(E)TE243A-0006D-01, pages 1, 2, 5 and 7, was downloaded and visually inspected. DFE201612E-R24M=P2 has a 2.0 ±0.2 × 1.6 ±0.2 mm body, 1.2 mm maximum height. Its recommended PCB pattern is two 0.8 × 1.8 mm lands with a 0.8 mm gap, hence a 2.4 × 1.8 mm outer land envelope. Land centers are at ±0.8 mm along the long axis.

The old 2.6 × 2.2 mm rectangle leaves 0.10 mm beyond the copper at each end. Use the same explicit convention already used for L24–L26: hypothetical 0.05 mm mask expansion followed by 0.25 mm clearance, giving **3.0 × 2.4 mm**. This changes two reservations from 5.72 to 7.20 mm² each, **+2.96 mm²** total. The mask expansion and clearance are review assumptions, not Murata specifications. No copper, mask or paste footprint is released here.

Murata specifies maximum DCR 19 mΩ, 6.6 A at 30% inductance decrease, and 5.0 A at 40°C rise on its six-layer test PCB. The current limit for the component is the smaller applicable criterion. Temperature rise and biased inductance need evaluation on this board. This is consistent with TI listing the part for TPS62864, but listing does not validate this module's peak/RMS current or cooling.

Murata prohibits unrelated copper and through holes below the coil and requires nearby components not to touch it. The source does not give a layer exemption for the copper restriction. Preserve this as a routing constraint until the manufacturer clarifies any intended interpretation.

## Smaller L21 candidates worth evaluating

**DFE201612E-R47M=P2** is in the same official Murata drawing and electrical table: 0.47 µH ±20%, 26 mΩ maximum DCR, 5.5 A at 30% inductance drop, 4.5 A at 40°C rise; same 3.0 × 2.4 mm reservation. Against current L21's 4.6 × 4.6 mm box, the area saving is **13.96 mm²**. This is a candidate requiring lead electrical review, not a TI-listed replacement in the currently cited table. At a hypothetical 4 A DC, I²R using room-temperature maximum DCR is 0.416 W before ripple, AC loss, temperature rise and DCR increase. The original XFL4015 is much lower resistance. This tradeoff cannot be decided from fit alone.

**XEL3520-471MEC** is explicitly TI-listed for TPS6282x. Official Coilcraft document 1340, revised 2026-06-25, gives 0.47 µH, 10.85 mΩ maximum DCR; 3.7/5.7/8.0 A at 10/20/30% inductance drop. Its reference thermal currents are 9.2/12.1 A at 20/40°C rise at 25°C ambient, with application-dependent PCB thermal behavior explicitly noted. The current document differs from older catalog thermal figures; use the dated source rather than mixing editions.

Coilcraft's page 3 drawing was inspected visually. Body maxima are 3.35 × 3.65 mm (nominal 3.2 × 3.5), height 2.0 mm maximum. Recommended lands are 0.81 × 3.2 mm each with 1.80 mm inner gap, yielding 3.42 × 3.2 mm. A 0.05 mm hypothetical mask expansion plus 0.25 mm clearance around the union of mask and maximum body yields 4.02 × 4.15 mm; round outward to a **4.1 × 4.2 mm reservation**, 17.22 mm², **3.94 mm² less** than the current L21 box. This increases height from the existing XFL4015's 1.60 mm maximum and still requires loss, peak-current and EMI review. Connect the indicated start/short lead to the high-dv/dt node as Coilcraft recommends.

L24–L26's existing DFE201610E-R47M=P2 3.0 × 2.4 mm reservations already incorporate the earlier land/mask sensitivity. There is no further saving to take for those three in the current baseline. Its 3.6 A thermal criterion must remain distinct from its 4.8 A inductance-drop criterion; see `compact-inductor-mechanical-review.md`.

## Evidence

- [Murata DFE201612E official reference specification](https://search.murata.co.jp/Ceramy/image/img/P02/J%28E%29TE243A-0006.pdf), SHA-256 `6fbbdccedc9f58904a3e60d7e9c0e33917a03b7dd0d96716821988e89e4fb8ad`
- [Coilcraft XEL3520 official datasheet](https://www.coilcraft.com/getmedia/585e5286-b75b-4755-99e9-56d067dcf62b/xel3520.pdf), SHA-256 `01b09f645259780911dca3d8cc967f3d76c94f74d835ae70346874314bbe7490`
- [TI TPS6282x datasheet](https://www.ti.com/lit/ds/symlink/tps62827.pdf), Table 8-5, p13; [TI TPS62864 datasheet](https://www.ti.com/lit/ds/symlink/tps62864.pdf), Table 9-4, p22

Downloaded manufacturer originals and page images are outside the distributable project under `/workspace/shared/k230-reference/mechanical/passive-review`. No part count, required capacitance, circuit connection, or master CAD file was changed by this audit. Source note supports the separately authorized L22/L23 area-screen correction only.
