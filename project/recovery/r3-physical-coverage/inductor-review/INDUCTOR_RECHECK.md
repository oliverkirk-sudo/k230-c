# CM-K230 inductor footprint recovery recheck

Audit: 2026-10-03 UTC. Baseline: `restored-v12-r2_1`, active `cad/recovery-physical-candidate/master.xml`. The main report describes that immutable baseline; the final addendum records bounded checks of the separate R3 assignments and R574 footprint.

**Five references, L22–L26, have matching existing Murata land-pattern candidates suitable for conditional footprint assignment. L21 does not.** This is a geometry and connectivity finding; electrical, thermal, assembly and manufacturing acceptance remain open. No CAD was modified.

## Exact six-reference disposition

All six active footprint fields are empty. All symbol pins below are passive. Preserve each complete schematic Value string and each pin-to-net connection when assigning geometry.

| Ref | Exact active Value | Pin 1 | Pin 2 | Existing candidate |
|---|---|---|---|---|
| L21 | `0.47uH XFL4015-471MEB REF` | SW_CORE | VDD0P8_CORE | None for this MPN in the audited library; keep unassigned |
| L22 | `0.24uH DFE201612E-R24M REF` | SW_CPU | VDD0P8_CPU | DFE201612E-R24M=P2 candidate |
| L23 | `0.24uH DFE201612E-R24M REF` | SW_KPU | VDD0P8_KPU | DFE201612E-R24M=P2 candidate |
| L24 | `0.47uH DFE201610E-R47M=P2 CANDIDATE` | SW_DDR | VDD1P1_DDR_IO | DFE201610E-R47M=P2 candidate |
| L25 | `0.47uH DFE201610E-R47M=P2 CANDIDATE` | SW_1V8 | VDD1P8 | DFE201610E-R47M=P2 candidate |
| L26 | `0.47uH DFE201610E-R47M=P2 CANDIDATE` | SW_3V3 | VDD_3V3 | DFE201610E-R47M=P2 candidate |

The candidate manifest explicitly maps L22/L23 to full ordering code DFE201612E-R24M=P2; the active Value omits `=P2`. Preserve the original Value and carry the exact candidate ordering code as separate sourcing metadata until BOM release. Geometry assignment must not silently substitute a part or turn a reference/candidate into an approved item.

Candidate library IDs:

- L22/L23: `CMK230_Inductor_Candidates:Murata_DFE201612E-R24M_P2_SOURCE_LAND_PROCESS_CANDIDATE`
- L24/L25/L26: `CMK230_Inductor_Candidates:Murata_DFE201610E-R47M_P2_SOURCE_LAND_PROCESS_CANDIDATE`

The active project's `fp-lib-table` does **not** register `CMK230_Inductor_Candidates`. A later authorized assignment must add a project-local library entry resolving to `../verified-footprints/inductor-candidates/CMK230_Inductor_Candidates.pretty`. The legacy `engineering/component-register.csv` still lists XFL4015 for L24–L26; it conflicts with the active master and current power pin matrix and must not drive those assignments.

## Geometry, tolerances and height

Both persisted footprints loaded successfully in native KiCad 9.0.2 and match their archived SHA-256 hashes. A fresh native read verified the pad numbers, positions, sizes, layers, mask margin and closed outlines.

| Property | Both Murata candidates |
|---|---|
| Electrical pads | Exactly two rectangular SMD pads, 1 at (−0.8, 0), 2 at (+0.8, 0) mm; F.Cu and F.Mask only |
| Copper | Each 0.8 × 1.8 mm; 0.8 mm inner gap; 2.4 × 1.8 mm overall envelope |
| Paste | Two separate unnumbered F.Paste-only apertures, each 0.8 × 1.8 mm at the same centers |
| Mask | +0.05 mm per edge; each aperture 0.9 × 1.9 mm; nominal internal mask web 0.7 mm |
| Body | Source page 1 rechecked: 2.0 ±0.2 × 1.6 ±0.2 mm; 2.2 × 1.8 mm maximum outline on F.Fab |
| Courtyard | Closed 3.0 × 2.4 mm rectangle with 0.05 mm line; 0.25 mm from nominal mask edge to line center |
| Under-coil marker | Closed 2.2 × 1.8 mm rectangle on Dwgs.User; zero embedded rule areas |
| Height | DFE201612E: 1.2 mm maximum; DFE201610E: 1.0 mm maximum, freshly confirmed from page 1 |

Pad numbers 1 and 2 are CAD connectivity labels. Fresh visual review of both manufacturer page 1 drawings confirms no body marking and establishes no winding-start polarity for either Murata part. Keep the existing pin mapping; do not infer an EMI orientation rule from the assigned left/right numbers.

Both page 1 drawings give terminal depth 0.5 ±0.3 mm. Neither drawing establishes an additional terminal thickness or coplanarity tolerance. Manufacturer land dimensional tolerances, mask expansion, paste/stencil prescription, courtyard and placement tolerance are unavailable in the reviewed pattern. The current +0.05 mm mask, 1:1 paste and courtyard are explicit process assumptions. Fresh page 2 inspection confirms DFE201612E-R24M=P2 is 0.24 µH ±20%, 19 mΩ maximum DCR, and DFE201610E-R47M=P2 is 0.47 µH ±20%, 32 mΩ maximum DCR. Inductance is specified at 1 MHz, 0.5 V. These initial tolerances do not replace biased/hot application qualification.

For L21, the current area screen contains only a 4.6 × 4.6 mm reservation explicitly labeled as unselected and not manufacturing geometry. A separate archived comparison reports XFL4015 height of 1.60 mm maximum, but this audit has no recovered XFL4015 source drawing, source hash, land pattern, tolerance stack or winding-start evidence sufficient to assign a footprint. The compact Murata/XEL3520 alternatives discussed in older reports are alternative parts, not footprints for the current XFL4015 MPN.

## Required process gates

1. **Assignment integrity:** work in a writable successor of the immutable restoration; add the project-local library entry, assign only L22–L26, retain complete Values and all twelve pin/net pairs, and verify exported schematic/PCB parity. The footprint's default Value is an MPN, so check that any update workflow preserves the schematic's electrical Value.
2. **Under-coil restriction:** both freshly reviewed Murata page 7 sources prohibit through-holes and unrelated copper below the coil, with an exception for copper to its electrodes; it gives no layer exemption. Apply the conservative full-body, all-relevant-layer interpretation until manufacturer clarification. Implement reviewed net-aware rules or a specific copper/hole audit. Dwgs.User provides no enforcement. Also verify neighboring parts cannot touch the body under assembly tolerances.
3. **Fabrication/assembly:** agree copper and mask registration tolerances, stencil thickness/apertures, placement and rework clearances; inspect actual exported copper, mask and paste. Source page 5 permits at most two reflow cycles; keep its complete temperature/time profile in the assembly process review. Native DRC alone cannot qualify the process assumptions.
4. **Electrical/thermal:** confirm each rail's peak/RMS current, biased inductance, saturation, hot DCR, AC/DC loss, stability/transients and temperature rise in the finished module. Fresh page 2 review distinguishes DFE201612E-R24M's 6.6 A inductance-drop criterion from 5.0 A at 40°C rise, and DFE201610E-R47M's 4.8 A criterion from 3.6 A at 40°C rise. These are different test criteria, not unrestricted continuous-current approval. The 125°C Murata operating limit includes self-heating; enclosed-air assumptions do not establish component temperature.
5. **Release:** resolve exact sourcing and application limits, update stale component records, prove top-only module placement/routing/height fit, and complete final board checks. Footprint assignment closes only a CAD binding gap.

## Evidence and provenance limits

The retained 2026-09-30 audit records 92 numeric assertions; its baseline and nonzero-paste controls passed DRC, its 0.81 mm clearance negative control produced two errors, and its deliberately invalid unrelated B.Cu loop under a coil passed DRC. The last result demonstrates the unenforced restriction. This audit rechecked the current native footprint geometry and file hashes; it did not rerun those historical DRC/plot controls.

The original PDF paths recorded by the restoration are absent, but both manufacturer PDFs were freshly retrieved into a separate private source directory during the recovery. This audit independently rehashed those replacement files and visually inspected pages 1, 2, 5 and 7 of both; exact hashes match the archived sources. Body tolerances, height, lands, initial inductance tolerance and the under-coil restriction are reconfirmed. No vendor PDF, page image or screenshot is included in this deliverable. The URLs below identify the source documents; this worker inspected the local replacement bytes and performed no external retrieval.

- DFE201612E, J(E)TE243A-0006D-01, pages 1/2/5/7: [manufacturer reference](https://search.murata.co.jp/Ceramy/image/img/P02/J%28E%29TE243A-0006.pdf). Reverified PDF SHA-256: `6fbbdccedc9f58904a3e60d7e9c0e33917a03b7dd0d96716821988e89e4fb8ad`
- DFE201610E, J(E)TE243A-0001E-01, pages 1/2/5/7: [manufacturer reference](https://pim.murata.com/asset/pim4/inductor/J%28E%29TE243A-0001_PDF_INDUCTOR). Reverified PDF SHA-256: `5c02415289b2b9d2c0ceb283cfe004a986d9e729dadbfe92917a381db5eae84e`
- Fresh DFE201612E footprint SHA-256: `979b4131e18048ce01e1d6ff2daad4857b669ffb46e5126ebbd19e34d2e2e3c8`
- Fresh DFE201610E footprint SHA-256: `cfe2b57a3dde4b85fe0bfc5236f7729e5a8bd953b39eb37605d8b12586b0d3f7`
- Fresh active master.xml SHA-256: `d6410392ae3f65d1b86c47aea0ec6adce01d70b7d07208b87036491a19af9a26`

`recheck-evidence.json` contains the native geometry results, exact values and pin/net pairs, source provenance and hashes of all 26 scoped input files. Those files were unchanged during the recheck.

## Bounded R3 implementation addendum

The separate `reconstruction-r3/project` active master was independently spot-checked after the audit. L22/L23 and L24–L26 now carry exactly the two candidate library IDs above; L21 remains empty. All six complete Value strings and all twelve inductor pin/net pairs match R2.1. The R3 project table registers the inductor library. This verifies the assignment step, with the process and application gates above still open.

**R574 also passes its independent source-land geometry check.** Fresh Vishay document 20052, revision 21-Sep-2022, page 2 was visually inspected and locally hashed. The new `CMK230_Recovery_Passive_Candidates:Vishay_CRCW0201_SourceLand_PROCESS_CANDIDATE` loads natively in KiCad 9.0.2 with two 0.28 × 0.43 mm copper pads centered at X = ±0.255 mm, producing the source's 0.23 mm inner gap and 0.79 mm outer copper span. Numbered pads 1/2 use F.Cu and F.Mask; two unnumbered 1:1 apertures use F.Paste only. The 0.025 mm mask expansion gives a nominal 0.18 mm inner mask web. The closed courtyard is 1.39 × 1.03 mm; mask, paste and courtyard are engineering candidates.

The source body is 0.60 ±0.03 × 0.30 ±0.03 mm, height 0.23 ±0.03 mm (0.26 mm maximum). Native F.Fab correctly marks the maximum 0.63 × 0.33 mm body. Source terminal dimensions are T1 = 0.15 ±0.05 mm and T2 = 0.10 ±0.05 mm. This page supplies no land dimensional tolerance or qualified mask/stencil/placement process.

R574's complete Value remains `10k CRCW020110K0FKED IDLE BIAS CANDIDATE`; pin 1 remains TF_HOST_CLK and pin 2 GND. Those fields match R2.1 exactly, while R3 adds the stated footprint. Geometry assignment does not qualify its clock loading or bias behavior. The existing native QA and clearance negative-control runs were not rerun by this bounded check.

- Fresh Vishay PDF SHA-256: `390a5effad7c3b526afb7faba340e29176261bfa4c041a128effc87b941a61ea`
- R574 footprint SHA-256, unchanged during this check: `00770fdbeeff2cee7e6ed26e54558d92aff4c3f93f4190d88988a2be0bee642b`

The R3 checks and R574 native pad/outlines results are appended in `recheck-evidence.json`; vendor pages remain outside the deliverable.
