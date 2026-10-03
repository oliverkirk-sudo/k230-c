# R6: passive footprint coverage

This physical-only revision assigns source-derived footprint candidates to 25 ordinary bias resistors and L21. All 254 component values, 1,509 pin/function/type/net bindings and population attributes remain unchanged from R5. R45/R47 and R528 remain DNP; storage remains inhibited. The eight DAT pullups stay at the R5 43k value. Coverage is 192 assigned references and 62 gaps. There is still no complete active six-layer PCB.

## Bias resistor batch

The exact 25 references are listed in assignments.json. They use the already checked Vishay CRCW0201 land candidate: 0.28×0.43mm lands, 0.23mm gap, with declared process-only mask/paste/courtyard choices. No precision VSET, zero-ohm/high-current, or oscillator-feedback part is swept into this batch. Two of the25 positions are DNP boot options and stay unpopulated.

The included bias-review was performed on R3; r6-applicability.json confirms that these25 actual values, terminal nets and population attributes still match. Its old47k DAT hold is historical and was addressed separately by the conditional R5 change. Its hypothetical180-reference coverage is not the current R6 inventory. Candidate order codes do not establish stock, one-piece orderability, lifecycle or mission-life qualification.

The source screen's worst steady DC stress is3.361mW on R204 under its stated assumptions, versus17.647mW from the125°C derating graph. This does not prove actual film temperature or transient behavior. CORE PG→EN noise/ramp limits, private-I²C drive/leakage and RC limits, reset/PMU/boot timing, and R571/R572 idle-state guarantees remain open. A footprint assignment cannot close them. R33 stays270k with its existing total-resistance acceptance requirement.

## Exact L21 geometry

The unchanged part is0.47µH XFL4015-471MEB. The official Coilcraft Document769-2, revised2026-03-10, supplies the recommended copper geometry: two0.98×3.40mm rectangles with2.37mm center spacing, hence1.39mm inner gap. Component-top-view pad1 is at(+1.185,0), on the marked right-hand start/short-lead side, and maps to SW_CORE. Pad2 at(−1.185,0) maps to VDD0P8_CORE. The numeric pin convention is ours; the source identifies the marked terminal. Do not mirror a bottom-view drawing or treat this as a generic pin1-left inductor.

Maximum body is4.30×4.30mm and height1.60mm for the reviewed E termination. The full maximum-body F.Fab rectangle and positive-X assembly cue are included. The cue's drawn size is an engineering illustration, not a manufacturing mark dimension. Mask expansion50µm per edge, separate1:1 paste apertures and4.80×4.80mm courtyard are process assumptions. The courtyard is1.88mm² larger than the old4.60mm reservation; this increase is retained. Neither etch/placement tolerance nor stencil/process capability is qualified.

Coilcraft does not state the Murata-specific blanket under-coil prohibition in the reviewed sources. No such automatic keepout is added to L21. This does not approve arbitrary routing beneath it: switching-loop, return, sensing, coupling and EMI review remain required. L22–L26 retain their separate Murata restrictions. The MEB→MEC product-page note concerns packaging; no suffix or electrical part is silently substituted here. Hot inductance/current/saturation/loss, solder profile, thermal rise and module fit are not qualified.

## Native validation

Fresh KiCad9.0.2 export/ERC checks exactly26 Footprint changes and no other component/graph/population changes. The isolated10×10mm L21 fixture has six copper layers and no route or plane; its two single-pad nets only prove the intended terminal identity. Its nominal geometry DRC passes. Mirrored winding-start numbering, wrong SW/output mapping, altered PG resistor and populated boot DNP controls are rejected. A deliberately1.40mm clearance control rejects the actual1.39mm land gap. This is not a whole-board or power-loop pass.

Run validate_coverage.py with explicit --project, --baseline (published R5 project) and --runtime paths using Python with pcbnew. Keep the38×38mm outline,140contacts,top-only assembly and six layers as the final integration requirements. Source PDFs and raw vendor images are excluded from this deliverable.
