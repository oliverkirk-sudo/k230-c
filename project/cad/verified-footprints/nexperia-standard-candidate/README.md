# Nexperia standard logic footprint candidates

These editable candidates use the exact current **SOT353-1** and **SOT363-2** Nexperia package documents and their recommended reflow PCB drawings. They are separate from the TI DRL and older unsuffixed SOT353/SOT363 footprints.

| References | Exact candidate part | Footprint in `CMK230_Nexperia_Standard_Candidates` |
|---|---|---|
| U91 | 74AUP1G17GW,125 | `Nexperia_SOT353-1_AUP1G17_06_DrawingVerified_CANDIDATE` |
| U93 | 74AUP1G06GW,125 | `Nexperia_SOT353-1_AUP1G17_06_DrawingVerified_CANDIDATE` |
| U92, U94 | 74AUP1G97GW,125 | `Nexperia_SOT363-2_AUP1G97_DrawingVerified_CANDIDATE` |

All dimensions are in mm. The component top view puts pins 1/2/3 down the left side at X = −0.975, Y = −0.65/0/+0.65. Right-side pins are 5/4 for the five-pin package and 6/5/4 for the six-pin package, from top to bottom, at X = +0.975.

Both drawings specify 0.75 × 0.40 rectangular copper lands, 0.85 × 0.50 mask openings and 0.65 × 0.30 paste apertures at common centers. These are represented explicitly on separate layers so global margin settings do not silently change the source geometry. Minimum copper gap is 0.25, mask web 0.15, and paste gap 0.35. Recommended stencil thickness is 0.125; paste aperture area is 65% of land area. There is no exposed pad.

The project courtyard is **3.4 × 3.1**, or **10.54 mm² each**, including at least 0.25 beyond the manufacturer's occupied bounding box and the maximum body including the outline drawing's excluded 0.2-per-side protrusions. The nominal body is 1.25 × 2.0 in this orientation. The occupied bounding box is 2.9 × 2.35, but it does not cover the worst-case protruded body length of 2.6. This is why the project courtyard is taller than a simple 0.25 expansion of the occupied box.

Four instances use 42.16 mm² of courtyard reservations. Their published occupied bounding boxes total 27.26 mm², versus 5.04 mm² for the four earlier X2SON candidates, a 22.22 mm² increase on that same basis. X2SON courtyards remain unverified, so this is not an exact courtyard-to-courtyard comparison or a board fit result.

Numbered electrical functions match the GX alternatives. Current manufacturer tables publish the same family DC, timing and Schmitt specifications for GW and GX. The 06's stated Schmitt action does **not** waive its 200 ns/V input transition limit. Full circuit and temperature qualification remains open.

## Source and validation

- [SOT353-1 package information, 15 November 2022](https://assets.nexperia.com/documents/package-information/SOT353-1.pdf): outline p2, recommended PCB lands/mask/paste p3
- [SOT363-2 package information, 21 November 2022](https://assets.nexperia.com/documents/package-information/SOT363-2.pdf): outline p2, recommended PCB lands/mask/paste p3
- Derived geometry, source hashes and area basis: `engineering/mechanical/nexperia-standard-footprint-spec.json`
- Electrical/package identity review: `engineering/mechanical/nexperia-standard-logic-variant-review.json`
- Native geometry assertions, independent review, isolated DRC and Gerber checks are in the matching `nexperia-standard-*` review files

The QA board has isolated one-pin nets for geometry checks only. It is not a circuit board or manufacturing deliverable. Footprint geometry verification does not qualify solder paste, assembly yield, board tolerances, routing, SI/PI, thermal operation or the full BOM. No main or high-temperature candidate CAD was edited. Complete manufacturer PDFs remain outside this distributable project.
