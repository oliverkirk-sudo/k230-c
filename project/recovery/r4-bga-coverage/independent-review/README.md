# Independent R4 BGA review

**PASS for source identity and conditional nominal geometry.** Thirty checks pass with no ball-map, coordinate, occupancy or native CAM discrepancy. This bounded review is complete; no main CAD was edited.

## FW200 source and orientation

The fresh Micron LPDDR4 PDF has SHA-256 `b29c808baa7e42fca9b7ccc54b673142d26b49a1fee6b3053cc8691c21832552`. Pages 21 and 24 were visually inspected. An independent row-by-row transcription of all 200 Figure 5 functions agrees with the restored source map and R4 coordinate contract. Independent extraction of the 200 Figure 7 ball circles, with its bottom-view columns reversed, gives the same occupancy.

The new `Micron_FW200_NSMD030_ENGINEERING_ONLY` footprint has exactly 200 electrical lands, retaining all physical NC/DNU balls and omitting the 64 absent sites. Coordinates correctly use component top view, balls down, X right and Y down. Pitch is 0.80 × 0.65 mm, with 8.80 × 13.65 mm center spans. The empty L/M rows and columns 6/7 remain uncompressed.

The upper-left F.Fab marker agrees with A1. The F.Fab rectangle centerline is the maximum 10.1 × 14.6 mm package projection. The 10.6 × 15.1 mm courtyard is an unqualified engineering clearance. Source height is 1.0 ±0.1 mm, hence 1.1 mm maximum; R4 `package-metadata.json` records that maximum. No native height property or 3D model is claimed.

## Native footprint and CAM result

KiCad 9.0.2 loads and round-trips 400 objects: **200 numbered copper/mask lands and 200 unnumbered paste-only apertures**, not 400 electrical balls.

| Exported layer | Unique circular flashes | Diameter |
|---|---:|---:|
| F.Cu | 200 | 0.30 mm |
| F.Mask | 200 | 0.40 mm |
| F.Paste | 200 | 0.30 mm |

Every exported center matches the source coordinate set. Copper lands have only F.Cu/F.Mask; each separate aperture has only F.Paste. Paste-only objects retain zero effective adjustment under the tested default, −0.02 mm global paste-margin and −10% global paste-ratio settings. No missing-site aperture or duplicated paste flash occurs. The temporary QA board and Gerbers were removed after checking.

## Copied candidates and boundaries

R4 U1/K230 and U3/BH153 footprint files are byte-identical to the already-audited restored candidates. Their conditional status is preserved.

- BH153 F.Fab depicts the nominal 11.5 × 13.0 mm body; source maximum is 11.6 × 13.1 mm. Its 12.0 × 13.5 mm courtyard remains unqualified
- K230 F.Fab depicts the maximum 13.1 × 13.1 mm body, with a 13.6 × 13.6 mm courtyard. Pad coordinates preserve missing A1, but the rectangular fabrication outline lacks an explicit pin-1 corner marker

These details do not invalidate ball identity. They must not be presented as assembly-marking, maximum-envelope or process qualification beyond the stated geometry.

The 0.30/0.40/0.30 mm FW construction is an explicit engineering choice. Micron's package-side 0.40 mm SMD-pad note does not approve PCB copper/mask/paste. Factory stack, via/HDI process, stencil, thermal, DDR, PDN, placement and routed fit remain open. The requirement remains 38 × 38 mm, 140 contacts, exactly six copper layers and top-only assembly. No eight-layer route is reused as proof.

## Reproduction and evidence

[independent-review.json](independent-review.json) records the 30 checks and input hashes; [native-results.json](native-results.json) records native counts and CAM results. Run `check_native.py` with system Python/KiCad, then `validate_r4.py` with Python/PyMuPDF. Source PDF/images remain outside this report directory.
