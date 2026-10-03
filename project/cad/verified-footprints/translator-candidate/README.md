# NVT4858HK footprint candidate

Library identifier: `CMK230_Translator_Candidate:NXP_SOT1161-2_NVT4858HK_1.8x2.6_P0.4_DrawingVerified_CANDIDATE`

The footprint is derived from NXP's official **SOT1161-2** reflow soldering drawing, 26 January 2021, p3. NVT4858HKZ is XQFN16; **SOT1174-1 is a different 12-pin package and must not be used**. Pin numbering/orientation matches NVT4858 Rev2.4 p7–9, transparent top view, terminals down.

- 16 electrical copper pads; no exposed center pad
- Left pins 1–4, bottom 5–8, right 9–12, top 13–16 counterclockwise in top view
- Pin 1 copper 0.90×0.22 mm; other seven side pads 0.85×0.22 mm; eight top/bottom pads 0.22×0.55 mm
- Explicit rectangular mask openings expand copper by 0.05 mm per side; explicit paste apertures shrink copper by 0.025 mm per side
- Recommended stencil 0.10 mm; nominal copper gap 0.18 mm, mask web 0.08 mm
- Project courtyard 2.8×3.6 mm exceeds the vendor's 2.35×3.15 mm clearance outline and retains the current U95 area reservation

Keep the unnumbered mask-only and paste-only primitives when importing. They intentionally lock the source geometry; they are not extra electrical pins. The KiCad QA board uses one isolated dummy net per pin, so its zero-unconnected result is a geometry check only.

Derived coordinates, source URLs/hashes, native-parser and Gerber checks are in `engineering/mechanical/nvt4858-*`. Manufacturer originals remain outside the design package. These files are editable mechanical candidates; process, placement, routing, signal integrity and assembly release remain pending. These isolated generators do not change integrated CAD or edge/castellation geometry; integration is owned by the design lead.
