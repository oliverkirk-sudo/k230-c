# BGA land and assembly guidance: bounded engineering comparison

Status: **ENGINEERING CANDIDATES ONLY — NOT MANUFACTURER-QUALIFIED PCB FOOTPRINTS**. Reviewed 2026-09-30. No released CAD, frozen v10 files, orders, or vendor communications changed.

The accessible guidance supports a useful comparison of land constructions. It does not establish an approved Micron FW200, Micron BH153, or Canaan K230 footprint. Package solder-ball dimensions, package pad openings, PCB copper, PCB mask, and solder-paste apertures remain separate quantities.

## Primary evidence and limits

1. [Texas Instruments, SPRAA99C, nFBGA Packaging, May 2021](https://www.ti.com/lit/an/spraa99c/spraa99c.pdf), PDF pp6–7, 11, 15. The complete official PDF was downloaded; these pages were rendered and visually reviewed. Page 7 separates copper, mask opening, paste aperture, and stencil thickness. Selected NSMD examples are below. Its SMD counterparts exchange the copper and mask diameters. Page 6 balances package-interface and board-land dimensions; p11 refines NSMD copper to approximately 90% of the package interface. Page 15 makes mounted joint geometry dependent on paste, land, reflow, and package mass; reducing lands solely to increase standoff can worsen fatigue. Table examples and prose use different stencil thicknesses: they are process starting points, not one universal specification. The document recommends stencil area ratio at least 0.66. This is TI package guidance, not qualification of the reviewed parts.

| TI example pitch | PCB copper diameter | PCB mask opening diameter | Circular paste aperture | Stencil thickness | Area ratio, calculated |
|---:|---:|---:|---:|---:|---:|
| 0.50 | 0.300 | 0.400 | 0.300 | 0.100 | 0.750 |
| 0.65 | 0.350 | 0.450 | 0.350 | 0.127 | 0.689 |
| 0.80 | 0.400 | 0.500 | 0.400 | 0.152 | 0.658, rounded to 0.66 in TI |

2. [Infineon, Recommendations for Board Assembly of xWLy Packages, V03, 2016-01-11](https://www.infineon.com/dgdl/Infineon-Recommendations_Board_Assembly_xWLy_Packages-AP-v03_00-EN.pdf?fileId=db3a3043163797a6011681c8e8cd1637), PDF pp8–9. Complete official PDF downloaded and those pages visually reviewed. NSMD exposes the pad sidewall; mask registration must leave the copper unobscured. Its 0.300 mm ball example uses 0.275 copper, 0.375 mask, 0.275 paste, and 0.100 stencil. Its prose mentions 0.075 mm mask clearance, while that table's diameter difference gives 0.050 mm per side: neither can be treated as a universal fabrication allowance. It warns that open vias drain solder and recessed microvia tops can increase voiding. Paste volume, print inspection, supplier capability, and component-specific routing matter. These wafer-level packages differ materially from molded memory BGAs, so use the document only as supporting process evidence. Search-result metadata described a newer revision, but the actual downloaded body is V03/2016; this report uses the body.

3. [Cypress/Infineon, AN98508, 001-98508 Rev. *D](https://community.infineon.com/gfawx74859/attachments/gfawx74859/KnowledgeBaseArticles/3788/1/Infineon-AN98508_Infineon_Serial_Peripheral_Interface_%28SPI%29_FL_Flash_Layout_Guide-ApplicationNotes-v05_00-EN.pdf), PDF p26 §4.1. Its official-hosted PDF text was accessible through the web tool before a subsequent local download returned HTTP 403. Retrieval stopped; no alternate endpoint or mirror was attempted. The inspected text gives an NSMD copper heuristic of 80–100% of solder-ball diameter and mask diameter 0.15 mm larger than copper. Its concrete examples concern Cypress SPI flash packages, not either Micron part or K230. This limited evidence is a secondary comparison only; it is not required to instantiate any candidate below. No complete local PDF was obtained and no rendered page was inspected.

NXP AN4982 was not obtained (web internal error; direct official request HTTP 404). It supplies no numeric evidence here. Micron CSN-33 was deliberately not accessed, retried, or obtained from any mirror. The older search-index quotation in existing mechanical work is not evidence used by this review.

Downloaded complete PDFs, source renders, and retrieval records reside outside the redesign deliverable tree at `/workspace/shared/k230-reference/mechanical/bga-engineering-candidates/`. Exact URLs, hashes, inspection pages, and failures are in `assembly-guidance-evidence.json`.

## Exact-package inputs, kept separate from the PCB

| Part | Verified physical grid | Package ball diameter | Package-side interface condition | Consequence |
|---|---|---|---|---|
| MT53E256M32D2FW-046 AAT:B | 200 balls; 0.80 X / 0.65 Y pitch | 0.436 ±0.050 | Post-reflow on 0.400 SMD ball pads | Tight 0.65 axis controls escape; package note does not authorize 0.400 PCB copper |
| MTFC16GAPALBH-AAT | 153 balls; 0.50 pitch | 0.319 nominal; no explicit diameter tolerance shown in inspected figure | Post-reflow on 0.300 SMD ball pads | 56 additional 0.270 test pads have no solder balls; never generate corresponding PCB solder lands |
| K230, escape comparison only | 390 balls; 0.65 pitch | 0.300 nominal, 0.250–0.350 | Guide lists 0.270 ball solder-mask opening in package context | A pitch-only 0.350 PCB land is not justified by this much smaller ball/interface |

Micron inputs come from the existing verified FW mechanics and LP4 grid review, and BH Figure 5, PDF p11 of the supplied automotive eMMC datasheet. K230 inputs come from the parent audit's verified package review. No exact-part PCB land-pattern instruction was found in these inputs. None establishes assembled standoff, paste volume, reflow recipe, or service-life qualification.

## Engineering candidates and calculated constraints

All dimensions below are millimetres. Every row is a **conditional nominal geometry for engineering evaluation**, not a recommended production footprint. Use only real solder-ball centers; preserve absent, NC, DNU, and VSF distinctions from the independent grid/net review.

| Evaluation case | NSMD copper | Mask opening | Circular paste aperture | Stencil thickness | Area ratio | Narrowest copper gap | Narrowest nominal mask web |
|---|---:|---:|---:|---:|---:|---:|---:|
| FW, pitch-table comparison | 0.350 | 0.450 | 0.350 | 0.100–0.120 | 0.875–0.729 | 0.300 | 0.200 |
| FW, interface-ratio comparison | 0.360 | 0.460 | 0.360 | 0.100–0.120 | 0.900–0.750 | 0.290 | 0.190 |
| FW, larger-land comparison | 0.400 | 0.500 | 0.400 | 0.100–0.120 | 1.000–0.833 | 0.250 | 0.150 |
| BH, interface-ratio comparison | 0.270 | 0.370 | 0.270 | 0.100 | 0.675 | 0.230 | 0.130 |
| BH, pitch-table comparison | 0.300 | 0.400 | 0.300 | 0.100 | 0.750 | 0.200 | 0.100 |
| K230, smaller-land comparison | 0.250 | 0.350 | 0.250 | 0.080–0.090 | 0.781–0.694 | 0.400 | 0.300 |
| K230, interface-size comparison | 0.270 | 0.370 | 0.270 | 0.100 | 0.675 | 0.380 | 0.280 |

FW spans 0.350–0.400 copper; 0.360 is 90% of its 0.400 package opening, conditionally treating that opening as the relevant wettable interface. BH 0.270 similarly compares 90% of its 0.300 interface with TI's 0.300 pitch example. K230 0.250–0.270 is only an escape sensitivity range near its smaller interface; the 90% arithmetic point is 0.243, not a selected land. The numerical resemblance of package and PCB dimensions does not convert a hypothesis into manufacturer approval.

Calculations are independent geometry:

- For a cylindrical aperture, area ratio = diameter / (4 × stencil thickness). At a 0.66 screening floor, maximum thickness = diameter / 2.64. Thus 0.270 allows at most 0.1023, while 0.250 allows at most 0.0947. A common 0.120 stencil gives only 0.5625 for 0.270; a 0.100 stencil gives 0.625 for 0.250. Those combinations fail this screen, although passing it still does not prove print yield.
- A nominal 0.050 radial NSMD mask clearance means mask diameter = copper diameter + 0.100. Evaluating 0.075 radial clearance instead adds 0.150 to the copper. BH then has only 0.080 web at 0.270 copper or 0.050 at 0.300 copper. These larger-mask variants are sensitivity checks requiring explicit fabrication capability; they are not interchangeable defaults.
- Straight escape between equal circular lands requires trace width + 2 × clearance ≤ pitch − copper diameter, before all tolerances. FW with 0.350 lands fits nominal 0.100/0.100 exactly, leaving no tolerance budget; 0.400 lands need finer rules. BH with 0.300 lands cannot fit even 0.075/0.075; 0.270 lands leave just 0.005 nominal spare. K230 at 0.270 leaves 0.080 spare with 0.100/0.100. Via capture pads, solder-mask-covered trace exposure, layer transitions, and signal integrity still require a routed study.
- For the limited ball-percentage heuristic, FW nominal 0.436 gives 0.3488–0.436. If one incorrectly required the rule to hold over every stated ball extreme, the lower bound would be 0.8 × 0.486 = 0.3888 and upper bound 0.386, leaving no intersection. K230 similarly produces 0.280 > 0.250. This demonstrates why a nominal ratio cannot replace toleranced solder-joint validation. BH lacks the ball tolerance needed even for that sensitivity exercise.

For an SMD comparison, TI's 0.500 copper / 0.400 opening and 0.400 copper / 0.300 opening are useful construction examples. The opening bounds the top wettable area; copper is larger underneath. Applying those to FW/BH would reduce nominal copper escape gaps to 0.150/0.100 respectively. Do not swap SMD and NSMD dimensions without rebuilding routing, mask registration, paste, and reliability assumptions.

### Additional BH SMD engineering case

**BH_SMD_CU0400_SM0300** is included as a separate, unqualified SMD evaluation case. Its geometry reproduces TI SPRAA99C Table 2-1's 0.50 mm-pitch SMD example: 0.400 copper diameter, 0.300 mask opening, 0.300 circular paste aperture, and 0.100 stencil. Its provenance is this general TI example; it is not a Micron land-pattern recommendation. All 153 physical solder-ball sites remain required, and the 56 bare package test pads remain excluded.

The BH package-side 0.300 SMD opening and this PCB-side 0.300 SMD opening give a nominal wettable-interface diameter ratio of 1.00. The copper diameter itself is 1.333 times the package opening, but 0.050 of copper is covered radially by mask. This distinction explains why the 0.400 SMD copper can be a supported generic comparison even though a 0.350 NSMD copper proposal falls outside the present NSMD comparison. That unsupported NSMD proposal does not become qualified by a sparse routing proof.

Calculated checks for the SMD case:

- Adjacent copper edge gap: 0.500 − 0.400 = **0.100 mm**. Literal 4 mil is **0.1016 mm**, so the nominal geometry fails a 4 mil copper-clearance rule by **0.0016 mm / 1.6 µm**. A separately specified 100 µm rule reaches equality, with zero nominal spare. Do not relabel 4 mil as 100 µm or imply that equality budgets copper-size/position tolerances.
- Mask opening edge gap: 0.500 − 0.300 = **0.200 mm**. This is mask web, not copper spacing; it cannot be used to claim a 0.200 mm electrical clearance.
- Mask overlap: (0.400 − 0.300) / 2 = **0.050 mm per side** nominally. To preserve SMD construction over the whole pad, the minimum copper radius minus maximum opening radius must exceed the worst-case relative registration displacement, with any required residual overlap. No fabrication tolerance budget has yet demonstrated this. Local loss of overlap creates unintended mixed SMD/NSMD geometry.
- Paste area ratio: 0.300 / (4 × 0.100) = **0.750**. This clears the 0.66 geometry screen; SPI transfer, aperture registration/sealing, flux, solder volume, wetting and reflow still require process validation.
- The 0.100 copper gap cannot carry a 0.075 trace with 0.075 clearance on both sides; that needs 0.225. VIPPO can avoid an inter-pad top-layer escape, but its drill, capture/annular ring, filling, capping, planarity, layer escape and full 153-site layout need their own fabrication/routing checks. A sparse proof does not establish those outcomes.

The covered pad edge changes wetting and the solder-joint neck relative to NSMD. Mask dimensional control, adhesion, thickness, registration and thermal/mechanical behavior therefore join the qualification inputs; do not inherit NSMD reliability results or treat the nominal interface ratio as life prediction. Higher-temperature operation makes representative board-level validation material, but does not itself select SMD or prove it unacceptable. The defensible outcome is an explicit SMD option for DFM/process review, conditional on a **separate literal 100 µm copper process** and a demonstrated tolerance budget; it cannot pass an unchanged literal 4 mil clearance check.

## Qualification still required

Release needs exact supplier/device/package revision applicability, finished copper and mask-registration tolerances, minimum surviving mask web, stackup and escape/via capability, planar filled/capped via treatment where needed, pad finish and paste/alloy compatibility, stencil transfer validation across the entire BOM, and an instrumented reflow process inside every component's limits. FW's supplied SACQ alloy must not silently become SAC305 in the process assumptions.

The high-temperature part ratings do not establish solder-joint life on this module. A representative assembly should demonstrate wetting, opens/bridges/voids and standoff through suitable inspection/cross-sections, electrical operation, and thermal/mechanical stress representative of the application. PCB thickness, CTE, package warpage, board support, copper balance, rework, and any underfill materially affect the outcome. Define acceptance criteria and mission profile before declaring a geometry qualified. No universal void percentage, reflow peak, underfill requirement, or lifetime is asserted here.

No proposed range closes the exact manufacturer land-pattern gap. It provides traceable choices and explicit constraints for a separate engineering candidate, preserving the current release boundary.
