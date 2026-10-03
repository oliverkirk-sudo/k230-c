# L21 exact-part land-pattern review

Review date: 2026-10-03 UTC. Status: **source geometry established for a conditional footprint; no manufacturing or application release**.

L21 remains `0.47uH XFL4015-471MEB REF`, with passive pin 1 on `SW_CORE`, passive pin 2 on `VDD0P8_CORE`, and no assigned footprint in the inspected R4 master. The previous 4.6 x 4.6 mm area reservation is not source land geometry. The older component register is not authoritative for other inductor references. No main CAD was edited in this review.

## Geometry and identity

The [Coilcraft XFL4015 datasheet](https://www.coilcraft.com/getmedia/84927b8b-f089-421b-a7f4-a0fa23afe908/xfl4015.pdf), Document 769-2, revised 03/10/26, page 2, was visually inspected. Its printed metric values are:

| Feature | mm |
|---|---:|
| Body, each axis | 4.0 +/-0.3 |
| Maximum body envelope | 4.30 x 4.30 |
| Maximum height | 1.60 |
| Recommended copper, each of two rectangular lands | 0.98 x 3.40 |
| Land center-to-center distance | 2.37 |
| Terminal width, for reference | 0.82 +/-0.05 |
| Terminal inner gap, for reference | 1.57 +/-0.25 |
| Terminal transverse extent | 3.25 typical |

The 2.37 dimension ends at dashed **pad centerlines**, not inner edges. Using the printed metric dimensions gives pad centers at x = +/-1.185 mm, inner copper gap 1.39 mm, and copper union 3.35 x 3.40 mm. These are arithmetic derivations. Use one metric transcription consistently; rounded inch values are not an alternative set to mix into it. Recommended-land tolerances, body corner radius, and full terminal-location/coplanarity limits are not specified.

The [exact XFL4015-471 product page](https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xfl/xfl4015/xfl4015-471/) identifies B as the former less-than-full-reel packaging code and directs ordering with C instead. M and E retain their tolerance and tin-silver termination meanings. This supports the same family land drawing for the existing MEB reference; it does not authorize a BOM rename or procurement release.

## Orientation

The marked **component top view** has a bar along its right edge. The bar identifies the right-hand start/short-lead terminal; Coilcraft recommends connecting the high-dv/dt node there. Preserve that shown orientation:

- Project pad 1: (+1.185, 0), `SW_CORE`, bar side
- Project pad 2: (-1.185, 0), `VDD0P8_CORE`, opposite side

The manufacturer does not number the terminals. These pad numbers implement the project's existing net mapping. Do not mirror the top-marking view as though it were an underside view. A reflected underside view reverses apparent left/right; the specified PCB top-view mapping does not. If the library orientation is rotated, rotate the bar and both numbered lands together. This is winding-start control for EMI, not functional DC polarity.

## Assembly assumptions and spacing

Neither the XFL4015 drawing nor its linked [soldering note, Document 362, revised 06/15/18](https://www.coilcraft.com/getmedia/06a8e448-75f0-480e-a120-e1ea952fecf4/Doc362_SolderingSMT.pdf), specifies numerical solder-mask openings, stencil thickness, paste reduction, or courtyard. Document 362 recommends establishing solder quantity experimentally and keeping solder quantity, placement and heating even at both joints. Its warning about narrowly spaced inductor lands is explicitly framed around **unshielded** inductors; it is not a numeric XFL4015 spacing requirement.

For compatibility with the project's existing provisional convention, a separately declared scenario is calculated in `derived-dimensions.json`: mask expansion 0.05 mm per edge, provisional 1:1 paste, and courtyard 0.25 mm outside the union of maximum body and mask. The body controls the envelope, producing **4.80 x 4.80 mm**, or 23.04 mm². This is 1.88 mm² more than the old reservation. Fabricator/assembler acceptance remains required; these are not Coilcraft dimensions.

No explicit under-coil routing ban, copper keepout, via prohibition, or layer-specific rule was found in the inspected family datasheet, product page, soldering note or [official FAQ](https://www.coilcraft.com/en-us/faq/). Do not inherit Murata's restrictions. This absence also does not qualify arbitrary routing beneath the part. Any project keepout must be named as an engineering choice, and all board copper/vias and neighboring parts remain subject to layout review.

The FAQ declines a universal inductor-spacing number, because interaction depends on current waveform/frequency, orientation and distance. It describes shielding as reducing stray fields and recommends measuring the finished circuit. Its ground-plane discussion is specifically framed for RF inductors and supplies no exact XFL4015 layer rule.

## Integration and release gates

The next authorized integration can use the source copper and explicit start-lead mapping, together with clearly flagged process assumptions. Preserve the 38 mm / 140-contact / six-layer / top-only project constraints. Do not infer a new height limit, change L21 to a smaller part, or mark the core rail qualified from this review.

Open gates include stencil/mask/courtyard acceptance, terminal-to-land tolerance review, placement/orientation inspection, under-body and adjacent-part EMI review, hot current and thermal loss, saturation, regulator stability, and final ordering-code/supply acceptance. Geometry does not settle those questions.

## Provenance

`source-manifest.json` records exact URLs, document revisions, SHA-256 hashes, acquisition date, visual inspection and recovered-project source hashes. `derived-dimensions.json` is the machine-readable transcription and arithmetic. `derived-land-top.svg` is an original explanatory sketch; it is not a vendor image or fabrication output.

Primary drawing SHA-256: `6535ab70d0ef65ba03d4b0800e206fc7867f26464e2d9dfd5dd931a2bcb0c7c1`.

Vendor originals and rendered source images are excluded from this deliverable. No vendor was contacted, and no upload, order, alternative selection or CAD assignment was performed.
