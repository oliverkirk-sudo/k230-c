# K230 DDR-constrained local fanout checkpoint

**Nominal local geometry and requested layer/via topology pass. DDR spacing, coupling, timing, reference continuity and PDN do not pass release qualification.** This is a separate engineering coupon. It does not replace the frozen generic control or any module PCB.

## What is physically present

- All 390 source-identified K230 lands: 209 signal/bias, 53 power, 105 ground including TEST_EN, and 23 intentional opens
- 209 continuous signal exits, with no unsolved local signals
- 327 real plated-through vias with all eight copper annuli retained: 169 signal and 158 power/ground
- 16 newly routed outer DDR ball transitions, each with an actual top dogbone and internal escape; no dummy vias or NC markers
- All 64 high-speed DDR paths have exactly one physical L1-to-escape transition; RESET also has one
- All six differential pairs use the same layer for both legs and equal physical via counts
- All four 11-net bytes and both 10-net CA/CK groups each use one layer, an additional engineering topology target

| DDR group | Internal escape layer | Routed paths | Actual vias per path |
| --- | --- | ---: | ---: |
| A_BYTE0 | L3 | 11 | 1 |
| A_BYTE1 | L8 | 11 | 1 |
| B_BYTE0 | L8 | 11 | 1 |
| B_BYTE1 | L3 | 11 | 1 |
| A_ADDRESS_COMMAND | L3 | 10 | 1 |
| B_ADDRESS_COMMAND | L8 | 10 | 1 |
| RESET_ASYNCHRONOUS | L3 | 1 | 1 |

The search commits DDR differential pairs first, then related DDR signals, RESET and general signals. DDR never uses L6. L3 is intended to reference L2/L4 ground and L8 to reference L7 ground, but actual planes, antipads and return stitching have not been modeled. General signals still use L6, which remains unqualified for high-speed operation near L5 power splits.

## Verification and process limits

The independent analytic audit checked 2,336,694 emitted circle/circle, point/segment and segment/segment comparisons with zero nominal geometric violations. It verifies all 209 continuous exits, 158 power/ground ball-to-via ports, and 23 opens. The maximum 13.1 × 13.1 mm package projection is used: exits reach ±7.15 mm, 0.6 mm beyond the maximum body, and the complete copper envelope is 14.4016 × 14.4016 mm.

The conditional PCBWay advanced sensitivity uses 0.270 mm top copper lands, 0.325 mm via copper, 0.150 mm nominal hole, 0.1016 mm traces and copper clearance, and 0.1524 mm hole-to-other-net copper. The 0.0875 mm nominal annulus exceeds the selected 0.0762 mm minimum, but compensated drill tool, registration, retained annulus, solder land and assembly qualification remain open. The separate 0.200 mm hole-clearance sensitivity fails 641 comparisons; it is not mixed into the baseline and is not evidence of JLC acceptance.

The native coupon round-trip preserves all 390 lands, 327 vias and 997 actual segments. Native geometric DRC has zero violations. The raw report still contains 158 dangling power/ground vias, 199 dangling tracks and 135 missing power/ground interconnections because there are no planes or external loads. No severities are ignored and no DRC exclusions are added. The coupon is not DRC-clean as a complete board.

## DDR requirements and unresolved spacing

The [official guide](https://github.com/kendryte/k230_docs/blob/main/en/00_hardware/K230_Hardware_Design_Guide.md) explicitly calls for equal via counts for comparable signal types, at most two layer changes, package-aware matching, 50 Ω single-ended and 100 Ω differential routing, plus 3W spacing. The common-layer assignment for a whole byte is an added engineering target; it is not stated as a universal requirement by the cited text.

The guide's [spacing figure](https://raw.githubusercontent.com/kendryte/k230_docs/main/zh/00_hardware/images/HDG/image054.png) visually specifies edge-to-edge 2H within a byte and 3H to DQS/CK groups, byte-to-CA and supply/Vref conductors. It does not define the P–N gap within a differential pair. The standalone 3W sentence does not define edge versus centerline convention, so both readings are separately screened. P/N members of one pair are excluded from these crosstalk spacing checks.

The H screens use the unqualified catalog stack: L3 H = 0.130 mm conservatively from the two ground gaps of 0.130/0.109 mm, and L1/L8 H = 0.1195 mm. They distinguish segments under the maximum body from the short outside-body extension. The detailed CSV retains all violations. Some violations remain outside the package; topology completion must not be promoted to DDR compatibility. Trace guidelines are not automatically applied as pad/via DRC rules: supply-via proximity is an explicitly separate advisory diagnostic. The source states no breakout exception, and any permitted local exception needs SI/FAE qualification.

The routed pairs are not coupled or impedance-controlled. Their internal minimum P–N edge gaps are 0.2234 mm for five pairs and 0.5484 mm for CLKB; this is a measurement, not a 100 Ω design. Five local pairs also differ by 0.975 mm of copper. Unequal SoC package lengths are joined by ball, not aliases; Micron package delays are unavailable. The local exits stop outside K230, not at RAM. No board-only equal-length or timing claim is made.

All 158 real power/ground ball vias are present independently of the 77 allocated decouplers. Thirteen power balls are outside that decoupler rail subset. Capacitor placement, both sides of their local loops, planes, current capacity, IR drop, target impedance, thermal and full-core placement remain unmodeled.

## Files and reproduction

- `trial-groups-outer-21.json`: complete physical model, source hashes, search order, exact vias/routes and empty local unsolved list
- `trial-groups-outer-21-audit.json`: independent exact nominal geometry and separate 0.20 mm sensitivity
- `all390-ball-via-route-inventory.csv`, `all327-vias.csv`, `all-route-segments.csv`, `ddr65-local-layer-via-inventory.csv`, `unsolved-nets.csv`: complete reviewable inventories
- `local-envelope-ddr-pdn-audit.json`: topology, package lengths, actual envelope and PDN gates
- `ddr-spacing-screen.json` and `ddr-spacing-screen-violations.csv`: explicit source/sensitivity conventions and geometric zones
- `native-validation.json`, `native-drc.json`: native round-trip and unfiltered DRC
- `source-semantic-parity.json`: relevant U1 ball/grid/net/DDR mapping comparison, including passive-only whole-XML hash change
- `trial-groups-outer-21.svg` and `.png`: four-layer local preview
- `../../cad/bga-engineering-candidates/k230-ddr-constrained/K230_DDR_CONSTRAINED_LOCAL_TRIAL.kicad_pcb`: native isolated coupon

Run from this directory:

```sh
python route_constrained.py groups outer 21
python audit_geometry.py trial-groups-outer-21.json
python report_constrained.py
/usr/bin/python3 export_native_trial.py
/usr/bin/python3 verify_native_trial.py
```

`geometry_core.py` is an unchanged copy of the generic router implementation. The generic control remains untouched. This checkpoint uses no restricted IBIS or Micron CSN33 content, no vendor contact/upload/order, and no claim of full-core placement, SI, PDN, manufacturing or release approval.

The separately authorized actual two-package link experiment is isolated under `link-trial/`; its results and limitations do not alter this local checkpoint.
