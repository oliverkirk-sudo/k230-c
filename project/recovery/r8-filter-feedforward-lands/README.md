# R8: conditional analog-filter and feedforward lands

This checkpoint adds thirteen footprint identities to the recovered core schematic. It is not a complete layout or a production release. The exact predecessor is published R7, commit 1fddab33bbd0a6d00e7c53c8f09ba6f72e5ada13.

## Electrical identity and coverage

FB202–FB210 receive a conditional Murata BLM15PX121SN1D source-pattern option. C202/C219/C224/C229 receive KEMET C0402C122J5GACTU density-B source lands. No values, pin/net/function/type bindings, BOM flags or population states change. There are 254 components, 1,509 bindings, 457 nets, 215 assigned footprints and 39 gaps. JP1/R45/R47/R528 remain DNP. Source contracts nominate exact parts; assigning a footprint does not silently qualify generic value strings as a final procurement BOM.

## Ferrite copper is process-dependent

The exact Murata drawing specifies exposed lands 0.4 x 0.5 mm centered at x=±0.4 mm, but its power-family copper extends beneath solder resist. For the exact part's 2 A rating class, copper width d is 1.2/0.7/0.5 mm for 18/35/70 µm copper. Three distinct footprint variants preserve this distinction. The schematic uses the explicitly named 18 µm option as the larger conditional reservation. This does not choose or approve the six-layer factory stack.

Each numbered copper pad is 0.4 x d mm. Separate unnumbered mask apertures expose only the nominal 0.4 x 0.5 mm source opening; separate paste apertures use the same nominal dimensions as an engineering assumption. No expansion or registration allowance is included in that exact mask model. Factory acceptance must establish mask/copper registration and actual process margins. The engineering courtyard is 1.8 mm wide and at least 1.2 mm tall, increasing to1.8 mm for the 18 µm variant. These courtyards are not manufacturer assembly approval.

The rectangles implement only the local source pattern. They do not prove the continuing trace cross-section, heat spreading, filter impedance under DC bias, or current qualification. Initial55 mΩ and post-test70 mΩ are room-condition limits, not guaranteed hot DCR. Guide currents are reference module budgets, not measured peak loads. FB206 additionally feeds the R401 startup strap, whose pad current is not closed. The source-based branch screens and residual voltage budgets remain conditional; noise, transient, sequencing and thermal validation are still necessary.

## Feedforward source applicability

TI's Cff=12µ/Rbottom equation gives1.2 nF for each actual10 kΩ lower divider resistor. The four capacitor pin2 terminals reach the regulator FB pins; pin1 remains on the respective output side of the upper feedback resistor. KEMET density-B lands use0.62 mm square copper pads at x=±0.45 mm and the published1.90 x1.00 mm courtyard. Maximum body envelope is1.05 x0.55 mm, maximum height0.55 mm. Mask expansion+0.05 mm and separate1:1 paste are explicit unqualified process choices.

The nominated part is1.2 nF±5%,50 V,C0G,−55…125°C. This preserves nominal values but does not establish loop stability over all regulator/load/temperature conditions. LCSC C22402196 was verified searchable with minimum/multiple20, a user-preference exception; the same exact part has a quantity-one DigiKey cut-tape option. No purchase or stock reservation has occurred.

## Verification and remaining limits

Fresh KiCad9.0.2 netlist comparison preserves the complete electrical graph and all population attributes. ERC reports zero violations. The diagnostic20 x13 mm, six-layer fixture compares the three ferrite variants and one capacitor footprint. It uses unique diagnostic nets and has zero rule violations/unconnected items; all four parts remain isolated. Native exports have eight copper, eight mask and eight paste flashes. It is not the module and is not an assembly or routing pass.

Mutation controls detect wrong thickness-dependent copper width, accidentally exposed ferrite shoulders and an incorrect FB terminal net. Independent source/native review is retained separately when complete. The existing R528 DNP stencil gate remains: default paste export still includes its apertures. No manufacturing outputs are released.

The39 remaining footprint gaps are36 capacitors, two oscillator feedback resistors and the RTC crystal. Full38 x38 mm top-only placement, six-layerHDI construction, routing, SI/PDN, clocks, boot behavior, thermal testing and factory qualification remain unfinished. Historical lost geometry is not reconstructed by these source lands.

The native [copper/mask comparison](filter-copper.svg) was visually checked: top row18/35/70µm ferrite variants, bottom density-B capacitor. Drawing-sheet and text layers are omitted for clarity; the source footprints retain their identification. This preview does not add process tolerances.
