# CM-K230 DDR impedance feasibility screen

**30 September 2026 — analytical screening only. No fabricated-impedance, SI, routability or factory-acceptance claim.**

The current 1.2 mm catalog stack does **not** support promoting a universal 0.1016 mm (4 mil) DDR width on L3 and L8. Finite-copper equations put L3 near **42–43 Ω** and uncoated L8 near **65–68 Ω**, against the guide's 50 Ω nominal target. A different layer name or a router's clearance pass cannot close this difference.

The already documented **1.6 mm catalog alternative is the useful next stack to field-solve**: L3 screens near **0.126–0.129 mm for 50 Ω**. L6 has the same mirrored cross section if L5 becomes continuous GND. For nominal 100 Ω pairs, a **0.30 mm pair gap with about 0.110–0.115 mm width** is a plausible analytical starting region above 4 mil. These are screening inputs, not released routing rules. No extra vendor stack search or invented custom factory offering was necessary.

## Inputs and model conventions

The existing [stack proposal](../mechanical/core-stackup-process-proposal.json) supplies PCBWay catalog entry 13 (1.2 mm) and entry 1 (1.6 mm), 70% copper-density assumptions and 0.035 mm finished copper. The [DDR contract](../routing/DDR_ROUTE_CONTRACT.md) and [official K230 guide](https://github.com/kendryte/k230_docs/blob/main/en/00_hardware/K230_Hardware_Design_Guide.md) supply 50/100 Ω targets. No target tolerance was retrieved; **no ±5% or ±10% acceptance window is invented**.

| Cross section | Copper-surface dielectric gaps | Catalog Dk | Ground references |
|---|---:|---:|---|
| 1.2 mm L3 | 0.130 mm above / 0.109 mm below | 4.6 / 4.45 | L2 / L4 |
| 1.2 or 1.6 mm L8 | 0.1195 mm toward L7 | 4.45 | L7 |
| 1.6 mm L3 | 0.230 mm above / 0.175 mm below | 4.6 / 4.74 | L2 / L4 |
| Conditional 1.6 mm L6 | 0.175 mm above / 0.230 mm below | 4.74 / 4.6 | **L5 changed to GND** / L7 |

Signal copper is included once: L3 plane separation is 0.274 mm for the 1.2 mm stack and 0.440 mm for 1.6 mm. Width and pair gap mean **finished copper width and edge gap**, not guaranteed artwork dimensions. No plane-copper thickness is added to those reference-surface distances. Finite copper and inversion conventions matter; see [Polar AP160](https://www.polarinstruments.com/support/cits/AP160.html).

The models are uniform, rectangular, lossless/quasi-static cross sections. L3 uses both references through the finite-thickness centered-strip expressions and offset harmonic construction documented in [KiCad's stripline implementation](https://docs.kicad.org/doxygen/common_2transline__calculations_2stripline_8cpp_source.html). L8 uses [Hammerstad–Jensen as documented by Qucs](https://qucs.sourceforge.net/tech/node75.html), including the nonzero-thickness width correction. Results were evaluated locally by Python, not obtained from an installed electromagnetic field solver or from the KiCad GUI.

An independent coarse comparison uses the offset-stripline and microstrip equations in [NI Ultiboard's manual, printed pages 6-9 through 6-13](https://download.ni.com/support/manuals/374488e.pdf). Its documented user-defined-Z0 differential expressions are evaluated with both NI's own Z0 and the KiCad/Hammerstad–Jensen Z0. The latter is expressly a **screening hybrid**. These empirical coupling factors do not independently solve copper-sidewall fields, layered odd/even modes, or nearby conductors. Their error is not certified here.

## Numerical outcome

Ranges in this table are **model spread**, not production tolerances. All pair results assume equal widths and constant edge gap.

| Stack / layer | Z0 at 4 mil width | Zdiff at 4 mil width / 4 mil gap | Width for 50 Ω | Width for 100 Ω at 4 mil gap |
|---|---:|---:|---:|---:|
| 1.2 mm L3 | 42.2–42.5 Ω | 74.4–75.0 Ω | 0.0658–0.0680 mm | 0.0438–0.0454 mm |
| L8, **uncoated** | 65.3–68.4 Ω | 102.8–107.8 Ω | 0.1785–0.2003 mm | 0.1090–0.1218 mm |
| 1.6 mm L3 / conditional L6 | 54.1–55.1 Ω | See paired sweep below | 0.1259–0.1288 mm | 0.0709–0.0766 mm |

The original 1.2 mm L3 would need roughly 2.6 mil single-ended copper, and still narrower tightly coupled pairs, within these models. That contradicts the selected 1 oz process proposal's 4 mil trial floor. **Do not convert these calculated sub-4-mil widths into fabrication rules.** Converting L5 to GND on the 1.2 mm construction merely repeats this L3 problem on L6.

For L3 at 4 mil, even the isolated-pair limit is only about 85 Ω differential. Increasing pair gap cannot raise it to 100 Ω in this model. An additional conservative geometry/material screen moves both reference planes to the nearer or farther catalog gap and fills the cross section with each catalog Dk extreme. It gives **40.3–45.0 Ω** at 4 mil and **0.0569–0.0764 mm** for 50 Ω. This includes the offset geometry between the substituted symmetric cases, but excludes equation error and manufacturing variation; it is not a rigorous total-error bound. Keeping the actual geometry and varying only homogeneous Dk from 4.45 to 4.6 gives 42.2–42.9 Ω.

L8 4 mil/4 mil is plausibly near the differential target as an **uncoated analytical candidate**, while being far from the single-ended target. Neither the 102.8–107.8 Ω estimates nor possible mask loading establishes acceptance. At 4 mil width, these bare models solve 100 Ω at gaps around **0.072–0.090 mm**, below 4 mil; keeping a 4 mil minimum gap instead calls for the wider 0.109–0.122 mm traces shown above. Mask and actual pair fields must determine the production choice.

### Pair widths for a nominal 100 Ω screen

| Pair edge gap | 1.2 mm L3 width | L8 uncoated width | 1.6 mm L3 / conditional L6 width |
|---:|---:|---:|---:|
| 0.1016 mm | 0.0438–0.0454 mm | 0.1090–0.1218 mm | 0.0709–0.0766 mm |
| 0.2000 mm | 0.0580–0.0601 mm | 0.1479–0.1643 mm | 0.0964–0.1017 mm |
| 0.2500 mm | 0.0612–0.0634 mm | 0.1582–0.1761 mm | 0.1043–0.1094 mm |
| 0.3000 mm | 0.0631–0.0653 mm | 0.1650–0.1841 mm | 0.1100–0.1148 mm |

The 1.6 mm construction therefore offers a useful >=4 mil region without assigning sub-process widths. A 0.25 mm pair gap has little width margin; **0.30 mm is the more useful initial comparison geometry**. At exactly 4 mil width, the two models instead predict 100 Ω gaps of 0.199–0.231 mm. Do not equate either solution family with a toleranced factory result.

For the 1.6 mm single-ended case, homogeneous catalog Dk 4.6–4.74 changes the KiCad-equation 50 Ω width to 0.1235–0.1284 mm. The deliberately much wider moved-plane/material screen gives 0.1040–0.1519 mm. Even this nominal geometric screen clears 4 mil, though actual etch/process tolerances and model error remain unknown.

## Why mask, material and process still matter

The catalog Dk values lack a supplied frequency, test method and material tolerance. The midpoint values 4.525 and 4.67 are named homogeneous surrogates only. They are not measured effective Dk and do not turn two different dielectrics into an exact layered model. Glass weave/resin fraction, anisotropy and actual copper coverage matter; the separate 50% and 70% catalog stacks must not be averaged together.

Finite copper is material here: original 4 mil L3 changes from 44.2 to 41.2 Ω when the hypothetical copper thickness changes from 25 to 45 µm with dielectric gaps fixed. The equivalent L8 range is 70.0 to 67.1 Ω. The attached calculation ledger also includes Dk 4.0–4.8, dielectric-gap ±10%, and width ±10 µm **what-if** cases. None is a supplier tolerance. Finished-board ±10% thickness is not a tolerance assigned to every ply.

The specified L8 coating must be modeled. [Polar AP122](https://www.polarinstruments.com/support/cits/AP122.html) distinguishes coated microstrip and requires coating Dk plus the thickness around the trace. As an intentionally loose conditional limiting-media check, if every overcoat region has Dk between 1 and 4.45, with no nearby conductor, filling all surrounding space with Dk 4.45 would lower the H–J 4 mil value from 68.4 to about 55.4 Ω. This is **not a real mask estimate**. The actual mask is finite and its Dk unknown. A carrier ground/power plane close below this top-components-only module changes the outer fields further and invalidates the isolated-microstrip assumption.

There is no approved frequency-dependent laminate model or DDR edge spectrum in this screen. It does not predict loss, timing, training margin, via impedance or stub resonances. All-through vias and their pads/antipads, reference transitions, copper pours, breakout neckdowns and plane apertures require the actual layout.

## Figure 054, 2H/3H and 3W

The [official spacing figure](https://raw.githubusercontent.com/kendryte/k230_docs/main/zh/00_hardware/images/HDG/image054.png) was visually checked. It labels 2H within a byte and 3H to a DQS group, between byte and CA groups, to CK, and to supply/Vref conductors. Those neighbor-to-pair clearances **are not the gap between the two complementary DQS or CK traces**; that gap is set by differential impedance.

The text's 3W does not define edge versus center spacing. The figure does not fully define H for offset stripline. For a conservative planning envelope only, use the larger surface-to-reference gap as H and treat 3W as an edge gap: ordinary within-byte clearance = max(2H,3W), group/strobe/clock/supply/Vref clearance = max(3H,3W). If 3W is eventually confirmed as center-to-center, its equal-width edge gap is 2W instead. These interpretations need SI/design-authority closure, not silent rule substitution.

| Planning case | 2H | 3H | 3W edge interpretation | Within-byte / group envelope |
|---|---:|---:|---:|---:|
| Original L3, 4 mil | 0.260 mm | 0.390 mm | 0.3048 mm | 0.3048 / 0.390 mm |
| L8, 4 mil | 0.239 mm | 0.3585 mm | 0.3048 mm | 0.3048 / 0.3585 mm |
| L8, 0.2003 mm SE width | 0.239 mm | 0.3585 mm | 0.6010 mm | 0.6010 / 0.6010 mm |
| 1.6 mm L3/L6, 0.1259 mm SE width | 0.460 mm | 0.690 mm | 0.3778 mm | 0.460 / 0.690 mm |

Thus a 4 mil **fabrication clearance** is not a DDR crosstalk-spacing approval. The thicker stack eases the trace-width/process conflict but consumes more routing area under the height-based separation screen. That tradeoff must enter the 38 mm placement/routing trial before claiming feasibility.

## Concrete next gate

Carry the existing 1.6 mm catalog construction into an **isolated** L3/L6 feasibility proposal with continuous L2/L4/L5/L7 GND. Use approximately 0.127 mm SE width and the 0.110–0.115 mm / 0.30 mm pair-width/gap region as analytical starting points, together with explicit group-spacing envelopes. L8 can be evaluated primarily for power and other signals; making L5 GND removes the original power plane and therefore requires a new rail-current, copper-cross-section, return-loop and decoupling/PDN review. Top-side component assembly is unchanged as a constraint, and a thicker board needs mechanical/height approval. Wider traces and gaps still must escape the actual BGA lands and through-via fields.

Before any production geometry is promoted, obtain:

1. The named laminate and exact pressed prepreg/core construction for actual copper coverage, with frequency-qualified design Dk/Df and agreed dielectric tolerances
2. Finished copper thickness, etched top/bottom trace widths, roughness, trace/gap tolerances, and cured mask profile/Dk; assembled carrier separation where L8 is used
3. Factory 2D field solutions for the **actual mixed-dielectric, finite/trapezoidal-copper** L3/L6 and coated L8 cross sections, 50 Ω SE and 100 Ω differential; agree an impedance acceptance tolerance explicitly
4. Actual geometry analysis of through-via transitions/stubs/antipads and uninterrupted return paths, then timing/SI/crosstalk and PDN review
5. Same-process impedance coupons and a measured acceptance plan; [Polar AP124](https://www.polarinstruments.com/support/cits/AP124.html) explains matching coupon construction to the production board

No supplier was contacted, no design was uploaded, no agreement was accepted, no K230 IBIS was run, and no main CAD was edited. The bounded search stops here: a useful numerical distinction between the two published stacks and the exact missing manufacturing evidence have been established.

## Reproducibility

[assumptions.json](assumptions.json) records conventions, sources and exclusions. [calculations.json](calculations.json) contains unrounded-detail tables and source-input hashes. Run `python calculate_screen.py` in this directory to reproduce them (Python plus SciPy). Twelve algebraic/behavior checks passed, covering inversion, centered limit, monotonicity, separated-pair limits and inverse target solutions. These checks establish implementation consistency, **not electromagnetic calibration**.

The calculator adapts KiCad's finite-strip expressions and is supplied under **GPL-2.0-or-later**, with source attribution and the license copy; see [NOTICE.md](NOTICE.md). It is not covered by a presumed MIT license from the original module repository.
