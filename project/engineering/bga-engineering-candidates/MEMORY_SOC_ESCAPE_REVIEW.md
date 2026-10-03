# Functional-ball escape study: Micron FW200, Micron BH153 and K230

2026-09-30. **Engineering candidates only. No production footprint, completed PCB route, assembly approval, or eight-layer release.** No frozen v10 file or CAD was edited. No vendor was contacted and no design was uploaded. The rejected Micron CSN-33 URL was neither accessed nor retried.

## Findings that affect the process decision

1. **The selected 8-layer process is not yet qualified for the BH153 solder lands.** Ordinary 0.27–0.30 mm NSMD copper cannot contain the proposed 0.35 mm via copper. A 0.30/0.15 mm through via would fit 0.30 mm copper but its nominal 0.075 mm ring is 1.2 µm below the selected PCBWay process's published 0.0762 mm minimum, before registration. This is a supplier/process-specific comparison, not a universal through-via limit. Reducing the hole to 0.125 mm restores nominal ring width but is outside the selected 0.15 mm mechanical-hole minimum.
2. **The eMMC functional map does not force HDI on layer-count grounds.** A concrete sparse fanout sends all 11 HS200 host signals out of the package projection using L1 and L3, while retaining every physical land and including all 20 power/ground via locations. Four explicitly conditional geometries pass local collision checks. The remaining gates are real: exact-part land/mask assembly qualification, attainable drill/annulus/registration, reference-plane continuity, capacitor placement, and complete routing.
3. **Do not substitute a drilled-hole-only corridor calculation for a via-pad calculation.** At 0.65 mm pitch, retained 0.35 mm via copper leaves only 0.0968 mm for a track at 0.1016 mm clearance. Literal 4-mil trace width fails by 4.8 µm. Removing an ordinary via's unused annuli can help if accepted by the selected fabricator, but the drill and its clearance remain. This restriction does not apply the mandatory castellation annuli rule to ordinary signal vias.
4. **The K230 remains the board's larger unproved escape problem.** Its current candidate map has 209 named non-power signal/bias endpoints, with signals six rings deep, rather than a uniformly populated 390-signal array. All 65 live DDR joins lie in the right-hand seven columns. Sparse/offset fanout, selective unused-annulus removal and real decoupling placement must be tested together. No global K230 fanout was solved here, so neither eight-layer sufficiency nor mandatory HDI is established.
5. **All 77 top-side bypass parts need local routing space.** Body fit alone does not allocate that space. Signals, vias, returns and capacitors compete for exterior package-edge regions. The historical 13-body canvas is not a current placement and no interbody gap or full-board fit is inherited from it.

## Inputs and source limits

Exact candidates are MT53E256M32D2FW-046 AAT:B and MTFC16GAPALBH-AAT. The calculation reads the independently verified FW200 grid, FW mechanics, verified BGA coordinates, the candidate Micron eMMC CSV, the high-temperature candidate's pin assignments, the 77-capacitor allocation, and the new 65-net DDR route contract. Input SHA-256 values are recorded in each JSON output.

- [Micron automotive LPDDR4/4X datasheet, Rev. F 10/2020](https://www.mouser.com/datasheet/2/671/200b_z00m_sdp_ddp_auto_lpddr4_lpddr4x-3193603.pdf), Figure 5 p21 and Figure 7 p24; local independent review is `../mechanical/micron-lp4-independent-grid-verification.json` and `micron-fw-independent-mechanics.json`
- [Micron automotive eMMC datasheet, Rev. G 10/2018](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/234/EMMC_5F00_DATASHEET.pdf), Figure 3 p9 and BH Figure 5 p11; the source is a Micron-authored PDF hosted on TI's forum. The grid's independent text extraction agrees with the first visual transcription; this is not an additional independent assembly qualification
- `../mechanical/core-stackup-process-proposal.json` is the unchanged process input. It supplies literal 4/4 mil, 0.35/0.15 mm fine through vias, and advanced 0.1524 mm hole-to-other-copper clearance; all remain conditional
- [TI nFBGA Packaging, SPRAA99C, Table 2-1 p7](https://www.ti.com/lit/an/spraa99c/spraa99c.pdf) independently distinguishes copper from mask openings. Its 0.5 mm examples include NSMD copper/mask 0.300/0.400 mm and SMD copper/mask 0.400/0.300 mm, with 0.100 mm stencil and 0.300 mm aperture. These are TI package examples, not Micron BH land approval
- [TI AM570x BGA Escape Routing, SPRUIP9](https://www.ti.com/lit/ug/spruip9/spruip9.pdf), pp4–7, 10–13 and 18–21, is a general primary-source cross-check that actual functional grouping, via placement, return planes and PDN occupy routing resources. Its example uses different lands, vias, package voids and bottom-side capacitors; its layer count cannot be transferred to this module

Micron's FW drawing uses a package-side 0.40 mm SMD pad condition and the BH drawing uses a package-side 0.30 mm SMD pad condition. Neither is silently relabeled a PCB land recommendation. BH's drawing also shows 56 unballed package test pads; any board-side mask/keepout implication remains an assembly-review gate.

## Analytical bounds, with literal 4/4 mil

Let W = C = 0.1016 mm, P be the center pitch, D the round land diameter, V the via copper diameter, H the actual applicable drill/hole diameter, and Ch the fabrication hole-edge clearance.

- One straight trace between two equal lands requires `P - D >= W + 2C`
- A cell-center via between rectangular-grid lands has nearest center distance `R = sqrt(Px² + Py²)/2`; copper gap is `R - (D+V)/2`, and hole-to-land gap is `R - H/2 - D/2`
- Between equal retained via pads, maximum track width is `P - V - 2C`
- With unused annuli removed, the hole-limited maximum is `P - H - 2Ch`. On a layer where copper pads remain, take the smaller of the pad and hole limits
- For an unrelated plane, a conditional exclusion diameter is at least `max(V+2C, H+2Ch)` with the annulus retained, or the qualified hole exclusion with that annulus removed. Same-net plane connections and required thermal/current geometry are separate

| Grid | Maximum D for one 4-mil trace on X / Y | Maximum D for a cell-center 0.35 mm via at 4-mil copper clearance |
|---|---:|---:|
| FW200, 0.80 × 0.65 mm | 0.4952 / 0.3452 mm | 0.477576 mm |
| K230, 0.65 × 0.65 mm | 0.3452 / 0.3452 mm | 0.366039 mm |
| BH153, 0.50 × 0.50 mm | 0.1952 / 0.1952 mm | 0.153907 mm |

These are bounds, not suggested land diameters. For example, FW200 trial D=0.40 mm and V=0.35 mm have 0.140388 mm cell-center copper gap, nominally passing C by 0.038788 mm, while that same 0.40 mm land cannot pass a 4-mil track between 0.65 mm-spaced rows. K230 trial D=0.35 mm gives 0.109619 mm dogbone copper gap, only 0.008019 mm over C; D=0.40 mm fails. BH trial D=0.30 mm with V=0.35 mm leaves only 0.028553 mm at the cell center. A uniform every-ball dogbone scheme fails badly there.

The BH outer physical ring still has copper at NC/RFU/VSF balls. With D=0.27–0.30 mm, a trace cannot pass between adjacent 0.50 mm-pitch lands at 4/4 mil. DAT3–7 at B2–B6 therefore need a qualified layer transition in their local trapped region; deleting NC copper or pretending all 153 balls are signals gives the wrong result.

### Inner-layer sensitivity

| Pitch | Retained V=0.35 mm pad: max W at C=0.1016 | Annuli removed, H=0.15 / Ch=0.1524 | Annuli removed, H=0.20 / Ch=0.1524 |
|---|---:|---:|---:|
| 0.50 mm | −0.0532 mm | 0.0452 mm | −0.0048 mm |
| 0.65 mm | 0.0968 mm | 0.1952 mm | 0.1452 mm |
| 0.80 mm | 0.2468 mm | 0.3452 mm | 0.2952 mm |

These values describe a pair of present vias, not the whole functional ballmap. They cannot prove a sparse layout impossible. In particular, the eMMC witness does not ask any trace to pass between the five B-row vias: all five traces leave that row in parallel toward the north.

At 0.65 mm pitch with H=0.20 mm, Ch must be at most 0.1742 mm to pass a 4-mil track after removing unused pads. Choosing Ch=0.1778 mm instead leaves only 0.0944 mm and fails. The normal 0.2286 mm eight-layer hole clearance is still more restrictive. Therefore merely saying “advanced process” is insufficient; the exact accepted combination matters.

The proposed 0.35/0.15 mm geometry has a nominal 0.1000 mm ring and only 0.0238 mm of radial geometric budget before reaching a 0.0762 mm retained ring. This is not an approved drill-registration tolerance. A 0.20 mm compensated tool yields a 0.0750 mm ring, failing that minimum even at zero registration error in the conservative concentric-circle model. The finished-bore/tool convention, registration, etch and permitted breakout must be resolved together. VIPPO filling and capping change solder behavior; they do not erase barrel exclusion or unused annuli.

## Concrete sparse BH153 witness

The Python script constructs polylines and checks segment-to-circle, segment-to-segment, via-to-land, drill-to-land, via-to-via and all physical-land-pair distances. It writes every source point, via center, route and failed check to JSON. Each variant executes **22,031 checks**. Minimum margins below are geometric margins over the declared rule, not fabrication tolerances.

Nominal inequality comparisons use an arithmetic epsilon of 10⁻¹² mm solely to handle binary floating-point representation at exact equality. This does not relax fabrication rules or create a manufacturing tolerance. The 0.200 mm hypothetical BH land in the 100/100 µm arithmetic table therefore correctly passes its exactly 0.100 mm available-width test, with zero nominal margin.

Physical frame is component top view with origin at package center, X right, Y down. B2–B6 are `(-2.75,-2.75)` through `(-0.75,-2.75)` at 0.50 mm spacing. Each has a via in its own qualified hypothetical copper and a straight L3 trace to Y=-7.0 mm. DAT0–2 (A3–A5) leave north on L1. The A6 ground via is moved to `(0,-4.5)` via a top trace so it does not obstruct B6's L3 exit. CMD and CLK use the genuinely absent L5/L6 positions, `(-1.25,1.75)` and `(-0.75,1.75)`, for their vias, then leave west/east on L3. RST_n K5 exits west on L3 at Y=1.25. VDDIM C2 exits west on L3 at Y=-2.25. It is a regulator-capacitor node, not an external supply.

There are 29 modeled vias: 20 power/ground, 8 host-signal and 1 VDDIM. DS H5 remains a physical land but has no HS200 signal via. All 109 NC, 4 RFU and 7 vendor-specific physical lands remain present. No external function was assigned to VSF. Plane connections, the VDDIM return/capacitor transition at its remote end, stitching vias and the final signal destinations have not been routed.

| Case | BGA copper / via copper / assumed drill | Trace / clearance | Geometric result | Independent process or assembly blocker |
|---|---|---|---|---|
| Hypothetical large land, default | 0.35 / 0.35 / 0.15 | 0.1016 / 0.1016 | Pass; min margin 0.0484 mm | 0.35 mm BH NSMD solder land is not source-backed adoption and is outside the 0.27–0.30 mm assembly comparison |
| NSMD-shaped candidate | 0.30 / 0.30 / 0.15 | 0.1016 / 0.1016 | Pass; min margin 0.0984 mm | Ring 0.0750 mm is 0.0012 mm below published minimum before registration |
| Smaller mechanical hole sensitivity | 0.30 / 0.30 / 0.125 | 0.1016 / 0.1016 | Pass; min margin 0.0984 mm | Hole 0.025 mm below selected minimum; new through-hole process unsupported; nominal ring 0.0875 mm |
| Separate SMD process candidate | 0.40 / 0.35 / 0.15 | **0.1000 / 0.1000** | Pass; min margin 0 at adjacent physical lands | Requires separately accepted 100 µm copper clearance, exact-part SMD/mask/reliability validation and fabrication tolerance review; does not pass frozen 4-mil clearance |

For the final row, the conceptual mask/paste diameter is 0.300 mm and stencil thickness 0.100 mm from the generic TI example. Mask and paste are not included in the copper collision checker. Nominal mask web is 0.200 mm; nominal radial copper overlap under the mask is 0.050 mm. Mask registration, cap geometry/flatness, thermal-cycle reliability, stencil transfer and package test-pad behavior remain open. Copper gap is exactly 0.1000 mm, **1.6 µm short of literal 4 mil**. No rounding of the frozen rule was performed.

This establishes a useful conditional result: tighter qualified ordinary through-via/land construction can avoid HDI for the local eMMC escape. It does not establish that any of the four constructions is approved for manufacturing. If the acceptable exact-part land remains NSMD 0.30 mm and no compatible filled through-via annulus/hole process is available, a qualified via-in-pad microvia/HDI construction becomes the appropriate branch to test.

## FW200 and K230 functional demand

FW200 contains 200 physical balls: 58 VSS, 52 power, 22 NC/DNU, and **68 non-supply functional balls**. There are **65 live SoC-to-RAM joins**, not 68 high-speed off-package signals. ZQ0 A5 and ODT_CA_A/B G2/T2 are local calibration/static-control circuits. The 65 joins occupy the four physical quadrants as NW 15, NE 17, SW 15, SE 18. Two entirely absent columns provide a 2.40 mm center gap and two absent rows provide a 1.95 mm center gap. At 0.40 mm lands and 4-mil width/clearance these correspond to optimistic unobstructed straight-channel capacities of 9 and 7 traces respectively. Adding dogbone vias, rail vias, ZQ/ODT connections and trace turns consumes those corridors.

This package does not have the eMMC's fully closed 0.50 mm geometry. Its 0.80 mm axis and large true voids support plausible sparse ordinary through-via escape. However, the 0.65 mm axis still blocks a 4-mil track between 0.40 mm lands or between retained 0.35 mm via pads. Blindly filling its center void with power vias can remove the needed cross-package lanes. A full 65-join layer assignment with the 110 supply/ground balls has not been solved here; no LPDDR signal-layer count is certified.

K230's candidate map consists of 209 named signal/bias endpoints, 53 power endpoints, 105 ground-net endpoints (104 VSS plus the grounded TEST_EN strap) and 23 intentionally open endpoints. Some named-net dispositions remain candidate-level, including the strobe; this is a routing-demand screen of the current design, not new functional approval. Signal counts from outer ring zero inward are **56, 59, 42, 34, 16, 2**. The two deepest are J6/BANK3_GPIO43 and L6/BANK1_GPIO24. Rings 6–9 contain only power and ground.

The 65 DDR joins have ring counts **16, 17, 16, 12, 4** and occupy columns 14–20. Thus 33 DDR joins lie in the outer two rings; 32 remain farther in. At a qualified 0.30 mm K230 land a single 4-mil top track can pass between neighbors, and the cell-center 0.35 mm dogbone has nominal copper clearance. At 0.35 mm lands that top channel closes by 4.8 µm; some local dogbones still fit. At 0.40 mm lands those centered dogbones fail too, but qualified VIPPO plus sparse/offset placement could still be an option. None of these observations proves the whole package route.

A separate bounded witness checks the deepest live J6 and L6 endpoints with **all 390 physical top lands retained**, first at 0.25 mm and then 0.27 mm trial copper. Both use the unchanged 0.35/0.15 mm via and 4/4-mil rules. J6 `(-2.925,-0.975)` takes a northwest dogbone to `(-3.250,-1.300)`; L6 `(-2.925,0.325)` takes a southwest dogbone to `(-3.250,0.650)`. Each then exits west on L3 to X=-7.2 mm. Each case passes 2,341 local checks. Minimum margin is 0.058019 mm at D=0.25 mm and 0.048019 mm at D=0.27 mm, controlled by via-to-neighbor-land clearance. These are copper comparison trials, not exact K230 land adoption. **Every other required signal/power/ground via is unrouted/reserved and may obstruct these exits**; the witness proves only that those two deep balls do not intrinsically require HDI for their initial transition. Coordinates and controlling neighbors are in `K230_deepest_local_witness` in each JSON.

The unchanged eight-layer allocation provides L1/L3/L6/L8 as candidate signal layers. L6 remains conditional for DDR because of its proximity to split L5 power; until reference continuity is resolved it must not be counted as an automatically usable fourth DDR layer. L2/L4/L7 stay ground. Increasing ordinary layer count cannot repair a trapped ball-to-via land geometry; HDI can remove selected full-depth obstacles, but an L1–L2 laser via alone reaches the proposed ground layer. Its signal landing/transfer path must be designed with a new approved stack.

## Local egress and top-side decoupling

The 77 allocated capacitors are grouped as 16 CORE, 4 CPU, 8 KPU, 5 DDR_CORE, 28 DDR_IO, 10 1.8 V, and six bank-rail capacitors. Their current allocation explicitly has no geometry. These counts are not a placement or PDN pass.

Geometric lower bounds from power-ball centers to outside the **maximum body projection** are:

| Device | Range over power-ball locations |
|---|---:|
| K230, maximum 13.1 × 13.1 mm body | 2.975–6.225 mm |
| FW200, maximum 10.1 × 14.6 mm body | 0.475–3.850 mm |
| BH153, maximum 11.6 × 13.1 mm body | 3.300–5.050 mm |

These are lower bounds on reaching an exterior top-side capacitor area, not electrical loop-length predictions. Add the capacitor's actual copper/courtyard, body/assembly clearance and route/via detours. The central BGA void is space for copper/vias, not top-side capacitors under the package body. The eMMC VDDIM C2 center alone is at least 3.00 mm from the nominal left body edge, or 3.05 mm from the maximum outline; its two-capacitor network therefore needs an explicit short-loop exterior placement and cannot be declared “close” solely because a trace escaped.

No current full-board placement is assigned by this study. The historical body-only canvas and its gaps are not used as route-area evidence. A present-day package orientation and placement, with real capacitor footprints and transition locations, is required before any interbody cross-section or board-level layer-capacity claim. The 0.1016 mm escape width is not a released 50-ohm width.

In the eMMC witness, dense B-row signal antipads can merge into a local plane slot when annuli are retained: at 0.50 mm pitch, 0.35 mm pads and 4-mil clearance, the conditional antipad diameter is 0.5532 mm. Removing unused annuli changes the hole-limited exclusion to 0.4548 mm for the stated 0.15/0.1524 mm case, leaving only 0.0452 mm nominal plane web. Plane continuity, fabricator minimum retained web, return-current detours and nearby stitches need explicit inspection. Filling the vias does not resolve this.

## Release gates and reproducibility

Before detailed full-board placement, select an exact-part land/mask/paste construction and a single accepted through-via or HDI process that meets it. Re-run these cases using the actual compensated drill and retained-annulus rules. Preserve space for the 77 capacitors and their power/ground via pairs while routing the K230 DDR sector and its other functional rings. Do not place passives by unconstrained rectangle packing and then assume their loops will fit.

Use `../routing/high-temp-ddr-route-contract.csv` and `DDR_ROUTE_CONTRACT.md` for the 65 joins: four 11-net byte groups, two 10-net CA/CK groups, and asynchronous RESET. All 64 high-speed joins have SoC package lengths joined by physical ball; Micron package delays remain unavailable. One byte group already has almost 5 mm of internal SoC length spread. The official timing inputs include DQ mismatch below 20 ps, DQ/DQS and CA/CK within ±10 ps, and DQS/CK within ±60 ps without leveling. Equal PCB length or successful local fanout does not close those constraints. Final flight-time matching requires both package models, manufactured-stack/via delay, SI and training verification.

Reproduce the cases with the sibling script:

```sh
python evaluate_memory_escape.py
python evaluate_memory_escape.py --land 0.30 --via 0.30 --hole 0.15 --suffix=-cu030-via030-hole015
python evaluate_memory_escape.py --land 0.30 --via 0.30 --hole 0.125 --suffix=-cu030-via030-hole0125
python evaluate_memory_escape.py --land 0.40 --via 0.35 --hole 0.15 --width 0.100 --clearance 0.100 --suffix=-smd-cu040-100um
```

Outputs are the `memory-soc-functional-escape-analysis*.json` files, the functional-ball CSVs, and `emmc-sparse-through-via-conditional-witness*.svg`. PNG renders were visually checked. Only this engineering-candidate directory is written. The script's checked local geometry has no design-rule waiver; the explicitly listed process/assembly gates remain unresolved rather than being hidden by its PASS status.
