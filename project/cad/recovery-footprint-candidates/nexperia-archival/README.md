# NXP SOT1160-1 archival-source candidate

Read `../../../recovery/logic-footprint-review/nexperia-archival/REVIEW.md`. This isolated footprint is based on visually inspected NXP archival outline/reflow drawings cross-checked against current primary web text. It is process-unqualified, and no active CAD assignment was made.

Preserve the long pin1 copper land, component-side numbering, and all ten separate mask/paste apertures. Actual package supply pins are VCC9/GND4; grounded logic inputs1/6 do not replace the supply return for bypass placement.

The source-exact mask geometry has a 0.055-mm nominal web. The 0.05-mm diagnostic native setting preserves ten separate openings; 0.075 mm merges them into one complex CAM region even while native mask DRC stays clear. The Process fixture and its merged-mask export are deliberate negative controls, not production data.

The actual-net fixture leaves three expected local ties unrouted. The unique-net fixture exposes intrinsic clearance defects. Runtime caches and vendor originals are not deliverables.
