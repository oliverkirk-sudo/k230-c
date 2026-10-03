# Y2 crystal land-pattern candidate

YXC X322524MOB4SI is the official reference BOM candidate. Manufacturer-authored Rev B.0 p3 was read and visually checked. The four suggested lands are 1.4×1.2 mm, centered at X±1.1 / Y±0.85 mm. Top-view pin1 is bottom-left, pin2 bottom-right, pin3 top-right, pin4 top-left; pins2/4 are grounded. Copper coordinates/numbering/sizes were checked through KiCad's parser and an isolated QA board has DRC0. This is not full-board DRC.

Solder-mask expansion0.05 mm, 1:1 paste and courtyard4.2×3.5 mm are explicit process assumptions, not qualified fabrication instructions. The marker denotes pin1 and is outside the mask. Assembly stencil and process still need review.

Electrical facts: 24MHz fundamental, CL12pF, ESR≤50Ω, C0≤3pF, initial±10ppm, temperature±20ppm, aging±3ppm/year, operating−40..85°C. The source calls100µW “maximum drive” but places it in the typical column; resolve that presentation rather than treating it as an independently guaranteed limit.

Existing two12pF load capacitors contribute approximately6pF in series. Actual parasitic capacitance, drive, negative resistance, startup and frequency require board-specific verification. Do not assume the nominal crystal CL equals either individual capacitor value. No oscillator hardware testing has occurred.

Source: https://atta.szlcsc.com/upload/public/pdf/source/20230512/FCFA71FC9F356FF871B9CC5C5DAC5D5F.pdf (YXC-authored, public distributor mirror). Raw manufacturer PDF is not included; derived facts and geometry are retained.
