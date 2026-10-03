# R11: 22 µF source-land identities

This conditional footprint checkpoint follows published R10, commit05b3254a3c19f15cf78588ed8095e06ab68f32da. It adds no completed core placement, routing or manufacturing qualification.

## Exactly nine assignments

C206/C207/C208 remain the CPU output bank, and C212/C213/C214 remain the KPU output bank. C540/C552 retain their respective DRAM VDD2/VDDQ local roles on VDD1P1_DDR_IO; C562 remains local VDD1 decoupling on VDD1P8. Their shared footprint does not merge these physical or electrical duties.

Each receives the conditional source-land identity for Samsung CL31B226KPHNNNE, nominal22µF, ±10%,10V,X7R,1206. No nominal value, component count, net, pin type/function, DNP or BOM flag changes. The full graph remains254 references,1509 bindings and457 nets. Coverage becomes230 assigned and24 missing. R528 remains DNP and default storage is inhibited.

## Geometry and process distinction

The exact manufacturer's metric3216±0.20mm reflow row is applicable. Its allowed gap/land-length/width ranges are1.64–1.76 /1.19–1.31 /1.74–1.86mm. The selected midpoint is two1.25×1.80mm rectangular copper pads centered at x=±1.475mm:1.70mm inner gap and4.20mm outer span. These are engineering selections within manufacturer ranges, not a prescribed unique land.

The maximum body is3.40×1.80mm, maximum height1.80mm. Mask expansion+0.05mm and separate1:1 paste apertures are project assumptions. The4.85×2.45mm courtyard uses a0.05mm stroke, leaving0.25mm from the nominal mask envelope to the courtyard's inner stroke edge. This construction is explicitly distinct from a manufacturer courtyard or factory approval. Assembly placement/etch/mask/stencil tolerances, solder transfer and reliability remain open.

The47µF candidate reviewed alongside this part has no matching exact±0.40mm-length reflow row. Its separate engineering proposal remains unselected and unassigned. The FLOW table is not substituted for a reflow recommendation. Input-capacitor bank count/value options also remain unapplied.

## Electrical and validation scope

The current CPU/KPU output banks retain the adopted30µF effective-capacitance design criterion per bank. Assigning22µF nominal parts does not establish combined biased/hot/aged Ceff or converter stability. DRAM local capacitors retain their own allocation, locality, return and PDN obligations; they do not automatically count as remote regulator capacitance.

Fresh KiCad9.0.2 ERC and exact graph/population comparison pass. The isolated20×13mm six-layer one-footprint fixture has no routing and unique diagnostic nets; its DRC has zero rule/unconnected items, with two copper/mask/paste flashes each. It is not the38×38mm module. Negative controls detect CPU/KPU or DRAM rail mixups, nominal changes and wrong pad geometry. Independent source/native review accompanies the final checkpoint.

Remaining24 footprint gaps comprise12 input capacitors, four47µF outputs, four oscillator load capacitors, C815, two oscillator feedback resistors and the RTC crystal. Complete top-only placement, a coherent six-layerHDI process, routing, startup/boot, clock accuracy, SI/PDN, sourcing and physical thermal/electrical testing remain unfinished. This source identity does not release production files.

The native [copper/mask comparison](bulk22-copper.svg) was visually checked. Independent review reports77 checks and six negative controls passing, including a real native clearance failure. This remains isolated geometry evidence.
