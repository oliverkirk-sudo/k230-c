# BGA land and escape engineering candidates

These files are a new, bounded investigation after the frozen v10 mechanical proposal. They do not change v10 or the main/high-temperature CAD. They establish candidate dimensions and local routing constructions, not manufacturer-qualified footprints or a fully routed core.

## Decision

**General primary assembly guidance is sufficient for explicit engineering comparisons. It is insufficient to release exact-part-qualified Micron FW/BH or K230 PCB footprints.** The selected generic eight-layer through-hole rules also cannot be assumed to work unchanged. A specific land, mask, via and local fabrication process must be chosen together before detailed placement.

The studies do **not** prove HDI is mandatory. Sparse functional-ball escape can avoid obstructions created by an unnecessary via beneath every physical ball. Ordinary unused signal-via annuli may be removed only when the selected process supports it. That is separate from the edge proposal's retained castellation annuli. Hole-to-copper clearance and drill registration still apply when an unused copper annulus is removed.

## Exact package evidence

- Micron MT53E256M32D2FW-046 AAT:B: verified 200-ball grid, 0.80 × 0.65 mm pitch, 10.0 × 14.5 mm nominal body and Ø0.436 ±0.050 mm post-reflow balls. Its Ø0.40 mm SMD ball-pad note describes the package-side condition
- Micron MTFC16GAPALBH-AAT: an independent mechanical extraction reconfirms all 153 physical positions. Its 56 additional Ø0.27 mm Au test contacts explicitly have no solder balls and receive no proposed PCB solder lands. The package's Ø0.319 mm ball callout has no printed diameter tolerance; Samsung's tolerance is not transferred. See [package evidence](micron-emmc-package-evidence.json)
- K230: the verified 390-ball, 0.65 mm grid remains authoritative. A1 is absent. The Ø0.30 mm ball and package-context Ø0.270 mm mask opening do not define PCB copper/mask/paste

Micron CSN-33 was not accessed or retried. No alternative endpoint or mirror was used to evade the earlier explicit rejection. Full manufacturer documents and inspected renders remain outside this project tree.

## Land, mask and stencil comparisons

The [assembly review](assembly-guidance-review.md) and [calculation matrix](assembly-guidance-evidence.json) contain eight unqualified cases. [TI SPRAA99C](https://www.ti.com/lit/an/spraa99c/spraa99c.pdf), especially Tables 2-1 and 3-4, supplies distinct PCB-land examples and reliability/assembly context. These examples are general guidance; none is represented as Micron or Canaan approval.

| Case | PCB copper / mask opening | Main coupling |
|---|---|---|
| FW NSMD comparisons | Ø0.35–0.40 / Ø0.45–0.50 mm | Ø0.35 leaves a 0.30 mm gap on the 0.65 mm axis: 100/100 µm routing reaches equality; literal 4/4 mil misses by 4.8 µm |
| BH NSMD comparisons | Ø0.27–0.30 / Ø0.37–0.40 mm | Ø0.27 leaves only 5 µm spare for nominal 75/75 µm; Ø0.30 does not pass that channel |
| BH separate SMD case | Ø0.40 / Ø0.30 mm | The mask defines the wettable area. Adjacent copper gap is exactly 100 µm; it fails literal 4 mil by 1.6 µm |
| K230 NSMD comparisons | Ø0.25–0.27 / Ø0.35–0.37 mm | Solder transfer and mask registration remain coupled to the smaller lands |

The SMD case is not a way to qualify the unsupported Ø0.35 mm NSMD control. Its larger copper, mask overlap, wettable shape and joint behavior are a different construction.

For circular paste apertures, the cited area-ratio screen is diameter divided by four times stencil thickness. A Ø0.27 mm aperture gives 0.675 at a 0.10 mm stencil but 0.5625 at 0.12 mm. A Ø0.25 mm aperture needs approximately 0.0947 mm or thinner for a 0.66 ratio. Mask offset, copper and opening dimensions, paste transfer, mixed-component stencil needs, reflow and hot-condition board reliability remain qualification inputs.

## Local escape evidence

The [functional escape analysis](memory-soc-functional-escape-analysis.json) is generated from exact grids and current net assignments. Its baseline Ø0.35 mm BH land is a deliberately hypothetical geometric control, not a source-backed NSMD selection. Read the separately labeled smaller-land and SMD variants alongside it.

A sparse eMMC construction keeps all 153 physical solder lands, including NC/RFU/vendor-specific positions, while routing the eleven required HS200 signals on two signal layers and representing all twenty supply/ground connections with vias. It includes VDDIM egress. The second-row DAT3–7 signals transition locally; no physical NC land is deleted to create a channel. Two source-comparison paths expose different unresolved process gates:

- Ø0.30 mm NSMD land with Ø0.30/0.15 mm via: local geometry works, but the nominal 0.075 mm annulus is 1.2 µm below the cited 0.0762 mm rule, before drill/etch registration
- Ø0.40/0.30 mm SMD construction with Ø0.35/0.15 mm via: local geometry works at literal 100/100 µm rules, but adjacent lands have zero nominal clearance margin. It does not pass the frozen literal 4 mil rule

Reducing a mechanical hole to Ø0.125 mm increases annulus but falls below the selected process's Ø0.15 mm hole limit. A filled/capped via does not erase its inner hole keepout, guarantee registration, or automatically approve a different solder-land size. These are process dependencies, not evidence that a particular factory accepts the candidate.

The annulus objection above belongs to the selected PCBWay rule set, not to the topology universally. A separate [JLCPCB primary capability table](https://jlcpcb.com/capabilities/pcb-capabilities/) publishes nominal multilayer vias down to Ø0.15/0.25 mm and prefers a 0.15 mm pad-diameter increase over the hole. Thus the same Ø0.30/0.15 mm geometry has a nominal published via path there. The [alternative-process check](alternate-via-process-check.json) applies its stricter 0.20 mm via-hole-to-copper rule to the existing sparse geometry: 5,474 added checks pass with 0.075 mm minimum margin. This does not transplant JLCPCB rules into the frozen PCBWay dielectric stack. JLCPCB's conflicting castellation guidance, a complete same-factory stack, actual drill/registration and Micron assembly qualification remain open.

K230 has 209 connected signal balls across six perimeter depths; the deepest live balls are J6 and L6. Its 65 SoC–RAM joins occupy five depths in the right-hand sector. FW has a rectangular pitch, broad absent-site channels, local ZQ/static ties and 65 live SoC joins; counting every physical non-supply ball as an independent high-speed route would overstate demand. Full sparse/staggered escape, reference continuity and local power-via placement remain to be solved.

The targeted J6/L6 construction uses staggered dogbones with Ø0.35/0.15 mm vias and literal 4/4 mil routes. Both Ø0.25 and Ø0.27 mm land comparisons preserve all 390 physical top lands and pass 2,341 local checks, with minimum margins of 0.0580194 and 0.0480194 mm respectively. Every other required via is explicitly unrouted/reserved. This verifies that local construction only; it does not solve the remaining 207 signal endpoints or the power/ground network. Details and coordinates are in [the escape review](MEMORY_SOC_ESCAPE_REVIEW.md).

A uniform Ø0.35 mm via-pad field at 0.65 mm pitch cannot pass a literal 4 mil trace with 4 mil clearance: only 0.0968 mm remains. Removing an unused annulus can improve the artwork corridor but leaves the drilled-hole constraint. The analysis separately reports nominal artwork margins and conservative drill/registration sensitivities; generic finished-bore dimensions are not silently relabeled as drill-tool sizes.

## Top-only bypass and DDR timing

All 77 grouped bypass allocations are present in the current candidate XML. [The reach analysis](topside-bypass-reach.json) covers the forty K230 power balls on those allocated rails. It does not pretend that all 77 capacitors belong solely to K230; several rails also serve memory.

With the maximum 13.1 mm K230 body and an explicit 0.25 mm external-component separation, central CORE balls K11/L11 are at least 6.475 mm laterally from an external capacitor/land extent. CPU/KPU examples reach 5.825 mm. These are geometric lower bounds, not route lengths or loop inductance. Top-only placement therefore needs local ball vias, power/ground planes and an actual PDN model; HDI alone cannot place a top-side capacitor beneath the package. The [drawing](topside-bypass-reach.svg) is a power-ball map, not a component placement claim.

The source-joined DDR ledger under `engineering/routing` adds package-length and timing constraints. PCB-only equal lengths are insufficient; one byte group has nearly 5 mm of internal SoC package spread. Micron package delays remain unavailable, and this study introduces no guessed length-to-delay conversion, timing closure or IBIS result.

## Practical next boundary

Before investing in dense full-board placement, select and qualify one of the local land/via/process constructions, then complete the K230/FW escape and jointly place the bypass network with its power/ground return geometry. A separately qualified HDI stack remains a fallback if those concrete escape/PDN attempts fail. More ordinary layers alone do not cure a local copper, mask or drill conflict.

This directory intentionally contains engineering dimensions, scripts, source provenance and partial fanout drawings. No manufacturing-release BGA footprint, full-board routing, or routed-fit claim is generated from missing exact-part assembly evidence.
