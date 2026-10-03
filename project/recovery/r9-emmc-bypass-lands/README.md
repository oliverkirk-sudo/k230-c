# R9: eMMC bypass footprint candidates

This conditional checkpoint assigns six previously empty footprints. Its predecessor is published R8, commit f5181cb06de490fb23de0e79c619210a664b3212. No complete PCB, assembly release or operating qualification is claimed.

## Preserved circuit

C64/C65 remain on EMMC_VDDIM, the eMMC internal regulator capacitor node at U3.C2. C69/C70 remain on VEMMC_IO, the VCCQ rail fed from VDD1P8 through R561. C71/C72 remain on VDD_3V3, the VCC supply. Every capacitor's pin2 remains GND. The internal regulator node must not be treated as VCCQ or driven by an external supply.

All 254 component values, 1,509 pin/function/type/net bindings across 457 nets, population and BOM flags remain unchanged. The six footprint identities are the only component-attribute changes. Coverage becomes 221 assigned, 33 unassigned. JP1/R45/R47/R528 remain DNP, and default storage qualification remains inhibited.

## Source-based geometry, conditional component choice

C64/C69/C71 use the candidate Murata GRM188R71A225KE15D: 2.2µF, ±10%, 10V, X7R, 0603, −55…125°C. Copper pads are 0.65×0.70mm at x=±0.675mm, giving a0.70mm inner gap. This is a midpoint engineering selection inside the manufacturer reflow ranges, not a mandated exact pattern. Maximum body is1.70×0.90mm, maximum height0.90mm. The project courtyard is2.60×1.50mm.

C65/C70/C72 use the candidate GRM155R71C104KA88D:100nF, ±10%,16V,X7R,0402,−55…125°C. Copper pads are0.40×0.50mm at x=±0.40mm, with0.40mm inner gap. Maximum body is1.05×0.55mm, height0.55mm. The project courtyard is1.80×1.20mm.

Both use rectangular copper, +0.05mm mask expansion and separate1:1 paste apertures. Mask/stencil/placement tolerances and courtyards are explicit engineering process choices. Current manufacturer approval sheets, lifecycle, procurement quantity and actual factory acceptance remain open. JLC catalog identity was found, but MOQ1 was not verified. No components were ordered.

## Capacitance qualification remains open

Micron Table13 gives capacitor Min/Max/Typ values but does not explicitly define their operating effective-capacitance basis, bias, tolerance, temperature or aging conditions. These preserved nominal choices fit the printed table. That is not a guaranteed hot/bias/aging margin. Conversely, interpreting the columns as absolute effective minima would be an additional unverified assumption, not an established Micron compliance failure.

The source review retains conditional numerical budgets and the unknown residual effects. Do not infer a numerical VDDIM voltage from VCCQ; the inspected Micron source gives no such range. A different nominal capacitance, if later justified, requires a separate coherent electrical revision. No such change is made here.

## Verification scope

Fresh KiCad9.0.2 ERC reports zero violations. Full exported graph and population comparison allows only the six footprint fields to change. The two-footprint geometry fixture is20×13mm with six copper layers, unique diagnostic nets and no interconnects. It has zero rule violations and four copper/mask/paste flashes per layer. It is not the38×38mm core or evidence of local BGA bypass placement.

Mutation checks catch a wrong CReg net, an unauthorized nominal-value change and wrong land geometry. Independent source/native checks accompany the checkpoint. The prior default-DNP paste export gate remains open for actual assembly; these diagnostic outputs are not a production stencil.

The remaining33 gaps include30 capacitors, two oscillator feedback resistors and the RTC crystal. Top-only full placement, six-layerHDI stack/routing, PDN/SI, cold-storage boot policy, clock startup/accuracy, thermal behavior and physical validation remain unfinished.

The native [copper/mask preview](bypass-copper.svg) was visually checked: left0603, right0402. It omits identification and drawing-sheet layers for clarity; all source CAD remains editable. This is an isolated geometry comparison.
