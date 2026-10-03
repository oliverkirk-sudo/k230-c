# DNP stencil export policy review

**Result: PASS_REVIEW_ONLY on KiCad 9.0.2+dfsg-1.** The installed Gerber CLI and Python plot API do not expose a paste-specific “suppress DNP” option. A reversible, separately named assembly-board derivation successfully removes DNP paste while preserving copper, mask, holes, electrical bindings, placement and population attributes. This review does not qualify a stencil, assembly process, or production release.

## Installed controls and evidence

The local `kicad-cli pcb export gerbers --help` exposes these DNP controls:

- `--hide-DNP-footprints-on-fab-layers`
- `--sketch-DNP-footprints-on-fab-layers`
- `--crossout-DNP-footprints-on-fab-layers`

Their names and help scope them to fabrication layers. The installed `PCB_PLOT_PARAMS` has corresponding `Get/SetHideDNPFPsOnFabLayers`, `Get/SetSketchDNPFPsOnFabLayers` and `Get/SetCrossoutDNPFPsOnFabLayers` methods, but no DNP paste filter. `FOOTPRINT.IsDNP/SetDNP`, BOM/PnP exclusion flags, `PAD.Get/SetLayerSet`, and `LSET.RemoveLayer` are separate APIs. Position export independently has `--exclude-dnp`.

The installed evidence is retained in [Gerber help](final-evidence/gerbers-help.txt), [position help](final-evidence/pos-help.txt), and [API inventory](final-evidence/installed-api.json). The [official KiCad 9 CLI documentation](https://docs.kicad.org/9.0/en/cli/cli.html) corroborates the documented scope. The conclusion is bounded to the inspected 9.0.2 runtime, not other KiCad releases or third-party exporters.

Actual default CLI, hide-on-Fab CLI, combined Fab controls, and native Python `SetHideDNPFPsOnFabLayers(True)` plotting all retain the same DNP paste flashes in the fixture. In this build the tested CLI hide flag also left the fixture Fab output unchanged; this review does not claim that those Fab controls were effective or diagnose that separate behavior.

## Population source and immutable inputs

Authoritative inputs are the supplied project's `cad/recovery-physical-candidate/master.xml` and `tools/population_contract.py`. Their hashes and the source footprint-library hashes are in [results.json](final-evidence/results.json). The master marks **JP1, R45, R47 and R528 DNP**. JP1, J1, TP81 and TP82 are fabricated features in the population contract.

DNP is taken from the native master property and reconciled against board attributes, not inferred from value text, a generic BOM exclusion, or a reference prefix. Native BOM/PnP/board-only attribute parity, footprint library identity and every numbered electrical pad/net binding must agree with the master before derivation and on the derived board. Reference coverage alone is never sufficient electrical parity. Duplicate references, duplicate/ambiguous population properties, and unexplained board/master differences are errors. The master symbol pin declarations must exactly match its net-node pin set. Every included footprint must contain all expected numbered electrical pads, with no unknown numbers; each native pad must carry the exact expected net name. Multiple physical pads with one number are allowed only when every copy matches that same expected net. Both source and derived boards undergo these checks, including when subset-fixture mode is enabled.

The current master explicitly supplies a net node for every declared symbol pin, including NC pins. There are no NC or virtual-pin exceptions in this policy. An NC pad with an explicit master net must match that net; an importer that substitutes net zero needs a separately reviewed explicit rule. Missing master nodes, implicit virtual pins and unrecognized numbered mechanical pads fail closed rather than being guessed. File-level checks also reject electrical identity on non-copper pads and nonzero net declarations on unnumbered pads before native KiCad can normalize those declarations away.

The published master, population contract and footprint-library sources remained byte-identical. No published main-board or current R8 CAD was edited. The fixture deliberately represents only eight master references; the 246 absent references are explicitly reported, not silently treated as complete coverage.

## Derived-board procedure

1. Pin a source board, master XML and population contract by SHA-256. Keep the source as the canonical design. Require complete master reference coverage and exact per-reference pin/net parity by default; `--allow-subset-fixture` is an explicit review-only exception.
2. Generate a new, separately named native `.kicad_pcb` file. The helper refuses to overwrite the source or an existing output. Do not update footprint libraries, run footprint replacement, recalculate placement, or refill zones.
3. For each reconciled DNP footprint, remove only `F.Paste` and `B.Paste` layer membership from pads that retain other layers. Preserve the pad number, UUID, copper geometry, net, mask settings, position and every other field.
4. Remove a paste-only pad object only when it has no number, net declaration or drill. The CRCW0201 source footprint uses two such standalone apertures, so removing paste from its numbered copper pads alone would do nothing. Numbered/net-bound/drilled paste-only objects fail for review instead of being discarded.
5. Remove footprint-owned paste-only graphics from DNP footprints. All other footprint tokens remain unchanged. Paste-layer properties, zones, wildcard paste layers, unowned board paste, and groups referencing removed apertures fail closed for ownership/format review. These unsupported constructs are not guessed or silently dropped.
6. Reject paste on any contract-declared bare fabricated feature, including JP1 and TP81/TP82. A missing fitted-part aperture is likewise an error, not an acceptable side effect.
7. Verify that all remaining native board tokens exactly match the expected allowed-only edit; reload with native KiCad; check that DNP pads, graphics, fields and zones have no native paste membership; confirm native save/reload preserves the edit. Keep hashes and a per-object change manifest. Source and derived pin/net checks are independent of the allowed-only token comparison, so faithfully preserving a wrong source net does not pass.
8. Export **only F.Paste and B.Paste from the derived board** for the population variant. Continue taking copper, solder mask, outline and drill deliverables from the canonical source. Preserve the existing reconciled BOM/PnP process independently. Regenerate the derived artifact whenever the board, population variant, library binding or source contract changes.

The helper uses a bounded native S-expression patch instead of a full-board rewrite for the initial derivation. This preserves every non-paste token verbatim; KiCad itself then loads, saves and plots the result. A whitespace-insensitive token comparison allows native formatting while rejecting changes to values. The source plus the manifest makes the operation reversible: discard the derived board and regenerate; never copy it back into the canonical project.

R528 remains DNP and placement-excluded, and its original separated copper/net assignments remain unchanged. Removing its paste is one assembly safeguard; maintaining its electrical inhibit also requires the no-fit assembly instruction and the existing electrical/interlock review. This fixture does not certify circuit behavior.

## Reproduced results

The small two-sided fixture loads the existing source-library CRCW0201, bare bridge and bare testpad geometry. It adds clearly synthetic paste graphics/apertures, a mixed copper/paste pad case, a same-number/same-net plated-hole pad on TP81, track and via to exercise export semantics. The TP81 duplicate pad is a deliberate fixture control, not a source footprint-library change. Original numbered pads retain their authoritative master pin-net bindings; R528 retains VDD1P8 on pin 1 and BOOT_VOLTAGE_QUALIFIED_1V8 on pin 2, plus DNP and placement exclusion. It is not a production layout or a replacement netlist.

| Measurement | Default / Fab hide | Derived stencil |
|---|---:|---:|
| F.Paste flashes | 9 | 3 |
| B.Paste flashes | 7 | 3 |
| F.Paste component attribution | DNP and fitted | R529 only |
| B.Paste component attribution | DNP and fitted | R46 only |
| Fitted paste graphic regions | 1 per side | 1 per side |

Each surviving side has the fitted resistor's two source-library apertures plus one synthetic test aperture. The tested default DNP paste includes intentionally added test geometry; these counts must not be quoted as production-board aperture counts.

All **42 checks** pass, including sixteen intentional rejected controls:

- Copper deletion from R528 is rejected
- Fitted R529 aperture loss is rejected
- Paste added to bare TP81 is rejected for the bare-feature rule
- R528 board DNP-attribute removal is rejected
- R528 master-DNP removal is rejected independently
- Unowned board-level paste is rejected
- Wrong-net R528 and fitted R529 pads are rejected independently on source and derived boards (four controls)
- Missing R528 numbered pads and unknown TP81 pad numbers are rejected
- A duplicate-number TP81 pad with the wrong net is rejected, while both same-net copies pass
- A nonzero net declaration on an unnumbered pad is rejected
- Non-paste footprint position changes are rejected by the allowed-only token comparison
- A master missing a declared pin's net node is rejected without inventing an NC/virtual exception

Full F.Cu, B.Cu, F.Mask, B.Mask, Edge.Cuts and F.Fab Gerber content compares equal after removing only creation timestamp, file identity and checksum metadata. Excellon drill geometry compares equal after timestamp removal. Default PnP CSV is byte-identical and contains only fitted R46 and R529; DNP and bare features remain excluded. BOM attributes and master inputs are unchanged; no independent purchasing BOM regeneration is claimed.

The manifest records 14 unique expected pins and 15 numbered physical pads for the eight-reference fixture. This includes the deliberate same-number TP81 duplicate. It records an empty NC/virtual exception list. The results file also pins both executed Python scripts by SHA-256.

Machine-readable evidence: [checks and hashes](final-evidence/results.json), [per-object derivation manifest](final-evidence/derivation.json), [derived native board](final-evidence/DERIVED_STENCIL_REVIEW_ONLY.kicad_pcb), [native roundtrip](final-evidence/NATIVE_ROUNDTRIP_REVIEW_ONLY.kicad_pcb). Negative fixtures are deliberately invalid and must never be used as manufacturing inputs.

## Reproduce with parameterized paths

Requires the installed KiCad CLI and the Python interpreter that provides `pcbnew` (here `/usr/bin/python3`). No additional package installation is required. The output directory must be new.

```sh
/usr/bin/python3 test_policy.py --project "$PROJECT_ROOT" --out "$REVIEW_RUN_DIR"
```

Run an independent review derivation on a complete board:

```sh
/usr/bin/python3 derive_assembly_paste.py \
  --source "$SOURCE_BOARD" \
  --output "$DERIVED_BOARD" \
  --master "$MASTER_XML" \
  --population-contract "$POPULATION_CONTRACT" \
  --report "$DERIVATION_REPORT"

kicad-cli pcb export gerbers \
  --layers F.Paste,B.Paste \
  --output "$STENCIL_REVIEW_DIR/" \
  "$DERIVED_BOARD"
```

Supply only trusted project code as the population-contract argument. For a deliberately incomplete isolated fixture, explicitly add `--allow-subset-fixture`. To recheck an existing derived board, use `--verify-only` and a new report destination.

**Boundary:** CAD export policy is demonstrated for the supported constructs on this runtime. There is no claim about stencil thickness, area ratio, transfer efficiency, paste chemistry, print registration, mask-process limits, reflow or assembly yield. Those require a separate manufacturing/process review. No vendor was contacted and no production output was issued.

## R10 integration on the recovered project

R10 adds only this review/tool directory to exact published R9. Every existing project file remains byte-identical: the circuit revision remains RCV-R9, with221 assigned footprints and33 gaps. The42-check fixture suite was rerun against this exact project, not merely copied from the earlier R7 review.

The actual recovered R7 ten-reference native fixture was also tested. It uses an Audit_Footprints library alias, which strict source/master checking initially rejected as intended. A separate copy normalizes only those ten FPID strings after confirming every copied .kicad_mod is byte-identical to its authoritative current library file. The original fixture is preserved. This does not waive electrical parity.

[test_recovered_fixture.py](test_recovered_fixture.py) reproduces that normalization and derivation using explicit --project and --out arguments. [The actual-fixture result](recovered-fixture/recovered-fixture-results.json) confirms copper/mask18→18 flashes and paste14→12, removing only R528's two apertures. All non-paste CAM layers remain equal; all numbered pad/net identities and population flags agree with the current master. This is a recovered fixture, not the complete core board.

The synthetic two-sided fixture deliberately exercises both front and back paste. It does not change the user's top-only core assembly requirement. Deliberately corrupted negative fixtures and all diagnostic Gerbers are review artifacts, never production inputs. The bounded export-policy defect is addressed by the verified derivation, while full-board application and stencil/process qualification remain open.
