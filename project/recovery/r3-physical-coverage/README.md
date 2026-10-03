# R3 conditional footprint coverage

This revision binds L22/L23 to the existing Murata DFE201612E-R24M=P2 candidate lands, L24/L25/L26 to DFE201610E-R47M=P2, and R574 to a new source-derived Vishay CRCW0201 candidate. Values, component count, pin functions, net bindings, and DNP population are unchanged. The active entry remains cad/recovery-physical-candidate/CMK230_Core_REVIEW.kicad_sch.

155 of254 references now have footprints;99 remain unassigned. This is a schematic/library checkpoint. There is no active complete six-layer PCB. Preserve38×38mm,140contacts, top-only assembly; overall height need not match the original. R528 remains DNP and storage inhibited.

## R574 geometry and limits

[Vishay document20052](https://www.vishay.com/docs/20052/crcw0201e3.pdf), revision21-Sep-2022 page2, was visually inspected. Copper is0.28×0.43mm per land with0.23mm inner gap, centers±0.255mm. Maximum body outline is0.63×0.33mm; maximum component height0.26mm. These are source-derived dimensions.

The mask expansion25µm per edge, explicit1:1 paste apertures, and1.39×1.03mm courtyard are engineering process assumptions. Nominal inner mask web is180µm. The courtyard line center is275µm beyond the mask envelope (250µm to its inner stroke edge). They are not a fabricator/stencil approval. Use actual exported CAM and placement tolerances before production. R574 remains the conditional10kΩ clock bias: leakage, feedthrough, partial-power and timing gates from the TF clock review remain open.

## Inductor restrictions

Both Murata PDFs were retrieved again and match the archived source hashes. See engineering/inductor-footprint-review/INDUCTOR_FOOTPRINT_REVIEW.md. The maximum2.2×1.8mm body region must exclude unrelated copper and holes under the source restriction, including relevant inner layers. Existing Dwgs.User markers do not enforce this; ordinary DRC alone can pass a prohibited under-coil route. Full six-layer integration must explicitly audit all affected copper, vias and drills. Electrode-connected copper is the documented exception, not blanket permission for a ground plane.

L21 remains unassigned. Its old4.6mm reservation is not a manufacturer land pattern. The active master.xml and power matrix control L24–L26; the older component-register.csv has stale XFL4015 names and must not drive procurement. No exact ordering suffix, stock, hot current, saturation, loss, stability or thermal qualification is asserted by this revision.

## Validation

Fresh KiCad9.0.2 export checks all254 components and1509 pin/function/type/net bindings. Only the six declared footprint fields change. R528 DNP is checked explicitly. Wrong footprint, removed DNP, changed value and wrong clock-bias net controls are rejected. The six-layer R574 fixture is isolated geometry only: its two nodes are intentionally not a circuit. A0.24mm clearance negative control rejects the0.23mm land gap. Its layer count establishes no stackup or routing feasibility.

Run validate_coverage.py with --project pointing to this project, --baseline to verified v12+R2.1, and --runtime to a writable temporary directory, using the system Python with pcbnew. Keep native reports alongside this note. No vendor PDFs, source screenshots, runtime configuration or private notes are required for publication.
