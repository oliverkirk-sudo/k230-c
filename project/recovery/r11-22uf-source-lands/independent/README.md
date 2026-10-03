# R11 independent read-only audit

**PASS within the footprint-only review boundary.** The supplied R11 candidate was independently compared with the supplied published R10 project snapshot. All 77 checks passed. Main CAD was unchanged by this audit; native runs used an isolated copy.

## Verified result

- All 254 component identities and all 1509 pin-to-net/type/function/class bindings are preserved across 457 nets
- Exactly nine formerly blank footprint fields receive the CL31B226 source-land identity: C206–C208, C212–C214, C540, C552 and C562
- Values, complete non-footprint component XML, DNP/BOM/on-board flags, source symbol identities and schematic wiring are unchanged
- The only source-schematic changes are the nine footprint properties and root title revision RCV-R9 → RCV-R11
- The generator retains its existing AST except for the same revision, the exact nine-reference assignment map and the new library-table append
- One new library owner resolves to exactly one new footprint; previous ownership declarations are unchanged
- 230 references have assigned footprints; 24 remain unassigned
- Fresh native netlist agrees with saved R11 master; fresh ERC has zero violations
- Saved isolated geometry fixture has one matching source footprint; fresh DRC has zero rule violations and zero unconnected items

## Geometry and saved CAM

Copper is two 1.25 × 1.80 mm pads centered at x = ±1.475 mm, with 1.70 mm gap. The maximum-body outline centerline is 3.40 × 1.80 mm. Separate unnumbered paste pads are exactly 1:1. Nominal mask expansion is +0.05 mm, giving a 4.30 × 1.90 mm overall mask envelope.

The 4.85 × 2.45 mm courtyard centerline with 0.05 mm stroke leaves **0.25 mm from the mask envelope to the courtyard stroke's inner edge on all four sides**. This check includes stroke width, not just nominal rectangle dimensions.

The saved copper, paste and mask Gerbers match independent native exports after removing creation timestamps only. Each has two flashes at the expected coordinates. Copper/paste apertures are 1.25 × 1.80 mm; rounded mask apertures have 1.35 × 1.90 mm bounds. The source specification SHA256 is742b9759b46abf22af1f61562aac31870345cf654ca240911f98fda44cf58167; its applicable3216±0.20 mm reflow range remains distinct from mask/paste/courtyard engineering choices.

## Negative controls

All six detect their intended fault: CPU→KPU, KPU→CPU, DDR→1.8 V and 1.8 V→DDR pin1 misbindings; a courtyard reduced to0.20 mm actual mask clearance; and a real native copper-gap reduction to0.05 mm against the0.20 mm fixture rule. The last produces a native clearance violation and exit code5. These mutations exist only in memory or isolated runtime copies.

## Resolved finding and limits

The copied source-evidence manifest initially referenced a missing build_review.py. The lead restored that script byte-for-byte, and the final audit confirms every source manifest entry resolves with its expected hash. The active README's sole addition is the bounded R11 status paragraph. No remaining defect was found in the audited scope.

Mask, paste, courtyard, assembly tolerances, Ceff, PDN, stability, thermal behavior and manufacturing remain unqualified. The47 µF proposal stays unselected and unassigned; the input-bank option is unapplied. Historical source rail-budget ranges are screening inputs, not complete aggregate voltage limits for every filtered branch. The20 ×13 mm one-footprint fixture and its six-layer setting are not a38 ×38 mm core layout or approved production stack. This review does not independently reverify remote publication state.

## Reproduce

Use KiCad9.0.2 and its pcbnew Python module. The portable runner takes explicit project/output/runtime arguments and refuses output paths inside either input project:

    /usr/bin/python3 audit_r11.py --baseline R10/project --candidate R11/project --out audit-output --runtime audit-runtime

Outputs are normalized JSON: summary,77 individual checks, native ERC/DRC, saved-CAM geometry, six negative controls, source-tree diff and hashes. Raw runtime copies are separate from this report directory. No original vendor documents are redistributed.
