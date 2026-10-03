# 38 mm core: new edge, stackup and component-reservation proposal

Status: **reviewable engineering proposal; factory and module-assembly acceptance remain open**. The main design and its historical 2 mm area-screen band are unchanged. This proposal retains 140 numbered contacts, 35 per side at 1 mm pitch, and permits components only on the top side.

## Proposed geometry and its evidence

The editable [KiCad proposal](../../cad/castellation-proposal/CMK230_Castellation_NOMINAL_PROPOSAL.kicad_pcb) has a 38 × 38 mm outline, 140 plated holes centered on the outline, and oval pads measuring 0.80 mm along the edge by 1.80 mm normal to it. The pads exist on every copper layer and both mask layers. Unused inner annuli are retained. No paste apertures are included: the carrier stencil and solder volume belong to the later module-mounting process.

**Ø0.50 mm means the requested nominal finished plated opening before edge routing.** The KiCad drill value is this nominal request; it is not the production drill-tool diameter. Tool compensation, copper plating, residual barrel shape and their tolerances need one factory's combined approval.

[Cirtech's Rev 001/A design note, PDF page 3](https://www.cirtech-electronics.com/wp-content/uploads/2024/03/Edge-Plating-and-Castellations-web.pdf) lists nominal minima of 0.50 mm hole, 0.80 mm pad and 1.00 mm pitch. Cirtech identifies itself as a PCB supplier working with manufacturing partners. Its publication supports this candidate geometry but does not accept a specific factory, eight-layer build, pad extension or tolerance stack.

The original STEP investigation independently finds 140 nominal Ø0.50 mm edge cutouts at the same pitch. Its modeled board thickness is 1.538354 mm. Those findings support nominal shape and position; they do not establish copper lands, plating or fabrication tolerances. See [original STEP evidence](original-step-edge-evidence.json).

Nominal geometry gives 0.15 mm transverse annulus, 0.65 mm inward centerline copper beyond the hole, 0.20 mm adjacent copper gap and 0.50 mm hole-edge gap. A 0.05 mm mask expansion leaves a 0.10 mm mask web. End-hole centers sit 2 mm from the corner; copper leaves 1.6 mm of edge at either end. These are derived dimensions, not fabrication allowances.

## Published process limits prevent an unconditional release

The [16-source comparison](castellation-fab-source-review.json) preserves the contradictions rather than selecting convenient values:

- [JLCPCB's capability table](https://jlcpcb.com/capabilities/pcb-capabilities) lists 0.5 mm holes/gaps, but its [dedicated castellation article](https://jlcpcb.com/blog/castellated-pcbs-introduction-and-design-requirements) gives stricter hole, ring and corner limits. The candidate fails that stricter published envelope
- [PCBWay's dedicated half-hole page](https://www.pcbway.com/pcb_prototype/What_are_Plated_Half_Holes_Castellated_Holes_.html) allows smaller holes, while other pages differ on spacing and cost. Its post-routing size is not dimensioned clearly enough to infer a retained radial-depth requirement
- [PCBWay's manufacturing table](https://www.pcbway.com/pcb_prototype/PCB_Manufacturing_tolerances.html) distinguishes a normal 0.20 mm PTH ring from a 0.15 mm via ring. The candidate does not meet the former. Increasing pad width to 0.90 mm consumes the available mask separation
- The nominal 0.10 mm mask web is below a literal 4 mil (0.1016 mm) rule. A 0.05 mm opening is also slightly below 2 mil. Global mask registration moves openings together and does not itself narrow their web; opening-width and differential-position errors are separate unknowns
- Four densely contacted edges need a specific panel support and routing plan. The corner gaps are not proof that break tabs, clamping or depanelization are safe

Consequently the hypothesis is rejected as an already-qualified generic standard service. It remains a source-backed custom-process candidate. No vendor has been contacted, no design has been uploaded, and no fabrication order has been made.

## Derived component reservation

The proposed reservation is **1.30 mm from each nominal board edge**:

0.90 mm inward copper + 0.05 mm mask expansion + 0.0762 mm mask-position budget + 0.25 mm component separation = 1.2762 mm, rounded outward.

The 0.0762 mm figure comes from [PCBWay's standard quality table](https://www.pcbway.com/oem/quality-control.html). Using it here is an engineering budget, not a claim that PCBWay accepts the rest of the geometry. The 0.25 mm component-to-mask separation is an explicit assembly assumption. It is applied to actual body and exposed solder-land extents; courtyard conventions must not silently consume or double-count it.

This produces a conditional 35.4 × 35.4 mm region, **1253.16 mm²**, 97.16 mm² larger than the historical 34 × 34 mm screen. It does not make that area routable. BGA escape, local decoupling, power paths, thermal spreading, test access and component rework still consume it. Ordinary plane/trace edge clearance remains a separate rule. Bottom-side routing is possible, but exposed bottom copper outside the castellations must not contact the carrier.

## Mating proof and its limits

The original carrier lands are **ovals**, 1.599999 × 0.559994 mm, with the long axis normal to the edge. The source Altium file says `SHAPE=ROUND` with unequal dimensions; the existing converted carrier footprint agrees. The authoritative carrier center rows remain ±18.746 mm, while this module's hole centers are ±19 mm. The intended normal offset is therefore 0.254 mm. Microscopic coordinate-conversion noise is retained in the input record and normalized to the explicitly specified 1 mm module grid.

Exact oval cross-section integration gives nominal retained copper overlap of approximately **0.385866 mm² per contact**, excluding the half-hole void. A continuous interval proof gives at least 0.132499 mm² for any pure relative translation within ±0.15 mm on each axis, under nominal copper/hole/profile dimensions. Sampled full-shape minima are labeled as samples, not global proofs. A separate conservative calculation covers an illustrative ±0.10 mm translation plus ±0.10° module rotation by eroding an inscribed carrier rectangle and bounding contact displacement.

These are conditional geometric proofs. Carrier pad/mask tolerances, assembly capability, wetting, solder volume, warpage and post-reflow stand-off are unknown. A generic ±0.2 mm outline size tolerance is not a local drill-to-route specification. An intentionally conservative combination with generic ±0.075 mm hole position and ±0.08 mm bore tolerance can even fail to guarantee that the profile intersects a hole. That calculation demonstrates why a joint registration specification is required; it is not a claim about the actual factory's correlated process.

The [dimensional JSON](castellation-proposal-dimensional-proof.json), [contact CSV](castellation-proposal-contacts.csv) and [profile drawing](castellation-proposal-profile.svg) contain the parameters and proofs. No worst-case assembly acceptance is claimed.

## Eight-layer trial and escape gates

The [stackup/process proposal](core-stackup-process-proposal.json) selects PCBWay's published eight-layer, nominal 1.2 mm through-hole construction, catalog entry 13, as a simulation and escape-routing trial. At its stated 70% copper assumption, the seven pressed dielectric gaps are 0.1195 / 0.1300 / 0.1090 / 0.1300 / 0.1090 / 0.1300 / 0.1195 mm, with 1 oz finished copper per layer. The catalog finished thickness is 1.19 mm ±10%. The [source catalog](https://www.pcbway.com/multi-layer-laminated-structure.html) explicitly excludes blind/buried vias; its 50% copper entry changes the pressed thicknesses. Neither nominal board thickness nor these typical Dk values fixes an impedance geometry.

Proposed roles are signal / ground / signal / ground / power / signal / ground / signal. L1 carries all components. L6 routes require return-path review near L5 splits; L8 has no components. A named laminate appropriate for reflow, temperature, CTE and electrical loss remains to be selected. High Tg alone is not a thermal solution.

A 1.2 mm board changes the original STEP's nominal height; the separately listed 1.6 mm construction is an alternative. Filled, planarized, copper-capped vias may be needed inside solder lands. Tenting is not equivalent. Actual BGA land patterns and the functional-ball escape must be qualified before choosing this route. For example, at literal 4/4 mil width/clearance, one channel between equal 0.65 mm pitch lands requires land diameter at most 0.3452 mm; at 0.50 mm pitch the bound is 0.1952 mm. A through-via's inner-layer hole keepout can be more restrictive. The report includes a separately sourced HDI alternative; no blind-via geometry is silently added to the through-hole catalog stack.

Before any fabrication release, one factory and assembler must accept the whole combination: finished holes/tooling and all-layer annuli; drill-to-route/copper registration; masks and residual castellations; four-edge panel retention; final laminate/pressed stack and impedance; qualified BGA lands/vias and escape; mating alignment/soldering; and hot-condition PDN/thermal performance. This proposal closes the dimensional definition step, not those remaining acceptance gates.

## Independent verification

The [independent geometry review](castellation-proposal-independent-review.json) passes 47/47 checks, including all 140 library and board pads, contact mapping, the original carrier shape, exact-curve overlap, continuous translation/rotation bounds and final input hashes. The isolated KiCad 9.0.2 DRC reports zero violations with edge-clearance checks enabled and no exclusions. The approximately 8.35 × 10⁻⁹ mm² maximum numerical difference between separate integration methods is below the documented 10⁻⁷ mm² comparison tolerance. This verifies the nominal proposal and its calculations; it does not close the process gates above.
