# Independent R12 input-bank candidate audit

**PASS within the requested implementation scope. No circuit, population, net-binding or source-footprint defect was found.** The published R11 baseline remains unchanged and unpromoted. This result does not qualify operating capacitance, VIN collapse behavior, board fit or manufacturing.

The independent runner uses fresh KiCad exports, native schematic parsing and a new runtime project. It does not import or run the implementation's validator. All native tool writes and deliberate mutations are confined to that runtime copy.

## Verified result

| Check | Independent result |
|---|---|
| Exact revision | Eight input value/footprint changes; only C204/C221/C226/C231 removed |
| Candidate graph | 250 components, 1501 numbered bindings, 457 nets |
| Footprint coverage | 238 assigned, 12 gaps; all assigned identities resolve across 29 unique files |
| Preservation | All 1,417 published R11 project files byte-identical |
| Native ERC | Zero violations before and after regeneration |
| Generator | Reproduces exact expected electrical, native population, no-connect, library and pin-CSV contract |
| Source bridge | R10→R11 equality independently verified for all 34 reviewed input/regulator/divider/bypass references; whole-file hashes remain distinct |
| Protection | Six local 100 nF bypasses, four DNP safeguards and 26 non-hardware source declarations preserved |
| Negative controls | All 16 rejected, including three actual schematic/generator mutations passed through fresh KiCad exports |

The changed positions are C203, C210, C211, C216, C217, C220, C225 and C230. All retain pin 1=VIN_5V and pin 2=GND. C205, C209, C215, C222, C227 and C232 retain their original 100 nF values, footprints and pin bindings.

All other component fields, properties, native instance attributes, pin numbers/functions/electrical types, named nets, symbol libraries and explicit no-connects match the predecessor contract. JP1, R45, R47 and R528 remain DNP. J1/JP1/TP81/TP82 remain board features excluded from the BOM. The 26 source declarations remain non-BOM/non-board, carry no footprint, and do not appear as physical netlist components. The power-source-path and memory-type sidecars remain unchanged.

The remaining footprint gaps are C41–C44, R41/R42, Y1, C201, C218, C223, C228 and C815. Their existence is not concealed by the improved candidate coverage.

## Footprint and area check

The candidate reuses the exact unchanged R11 footprint for Samsung CL31B226KPHNNNE. Its manufacturer-derived midpoint copper is two 1.25×1.80 mm pads at x=±1.475 mm, forming a 4.20×1.80 mm envelope. Native KiCad import confirms exactly two numbered copper/mask pads and two separate unnumbered paste-only apertures; there is no anonymous copper.

The explicit +0.05 mm mask margin, 1:1 paste and courtyard remain engineering process assumptions. They are not supplied or qualified by the manufacturer land row.

The footprint courtyard centerline rectangle is 4.85×2.45 mm. Eight such rectangles total **95.06 mm²**. The outer envelope including the 0.05 mm drawn stroke is a separate **98.00 mm²** figure. Neither is the earlier **34.40–36.08 mm² matched-clearance delta**, which compares different assumed reservations against the unassigned baseline. The implementation correctly distinguishes its 95.06 mm² rectangle total from that delta. None of these area metrics demonstrates placement, current-loop quality, routing or 38 mm board fit.

## Negative controls

The checker rejects a reintroduced removed capacitor, a missing local bypass, wrong input value/footprint/net, changed regulator electrical pin type, changed library pin function, populated R528, a board feature added to the BOM, a source declaration made physical, incorrect pad pitch, paste made copper, and unreviewed mask expansion.

Three additional checks exercise real source paths in the runtime copy:

1. Move C203 from VIN_5V to an output rail without relying on a count change, then export with KiCad
2. Populate R528 while leaving topology intact, then export with KiCad
3. Omit C230 from the generator's survivor selector, regenerate, then export with KiCad

Each fresh result is rejected against the independently constructed predecessor-plus-authorized-delta contract.

## Documentation and remaining limits

The current candidate and recovery READMEs correctly identify RCV-INBANK-R12, 238/12 coverage and the preserved R11 baseline. Their hashes are recorded separately. The copied PHYSICAL_STAGE.md is historical RCV-PHYS1 context and is not the current candidate description.

The source-review arithmetic was separately recomputed from its recorded primary-curve values and declared factors: at 5.5 V it remains **6.9246 µF per part / 13.8492 µF per pair**. Its status remains typical data plus explicit assumptions, not a combined guaranteed minimum. This audit does not validate those assumptions or establish capacitor life, ripple-current rating, temperature, startup/transient behavior or the TPS628640B falling-VIN requirement below UVLO.

## Reproduce

Requirements: Python 3, `kicad-cli`, and a Python installation containing `pcbnew`. The tested native version is KiCad 9.0.2. The runner has no workspace-specific input paths.

```sh
python3 audit_r12.py \
  --project /path/to/R12/project \
  --predecessor /path/to/published-R11/project \
  --review-baseline /path/to/published-R10/project \
  --runtime /path/to/a/new/runtime-directory \
  --out /path/to/audit-results \
  --pcbnew-python /path/to/python-with-pcbnew
```

The runtime directory must be new and outside the source trees. It is intentionally retained for investigation. The runner verifies source-tree inventories before and after all checks. `--kicad-cli` can specify an alternate executable.

Artifacts: `audit_r12.py`, `audit-results.json`, `negative-controls.json`, `source-footprint-check.json`, `native-checks.json`, `preservation-manifest.json`, and `source-review-arithmetic-check.json`. Logs normalize source/runtime paths. No raw manufacturer documents, source screenshots or full characteristic arrays are included.
