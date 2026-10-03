# R6 L21 independent native review

**Pass for conditional source-footprint integration. Manufacturing and application qualification remain open.** Reviewed 2026-10-03 using KiCad 9.0.2+dfsg-1. All inspected project inputs remained byte-identical during this review. Only this independent report directory and its separate runtime were written.

## Actual active design parity

The comparison uses R5 and R6 `cad/recovery-physical-candidate/master.xml`. A fresh native export of the R6 `CMK230_Core_REVIEW.kicad_sch` was written to this review directory and agrees with the current R6 master. The older `cad/integrated` source snapshot is not the integration authority.

- 254 components, 457 distinct nets and 1,509 pin/net nodes
- All component values, properties and symbol-library identities unchanged from R5
- All pin-to-net bindings, pin functions and pin electrical types unchanged from R5
- Exactly the 26 footprint assignments recorded by R6 changed
- L21 value remains `0.47uH XFL4015-471MEB REF`
- L21.1 remains passive on `SW_CORE`; L21.2 remains passive on `VDD0P8_CORE`
- The previously empty L21 footprint is now `CMK230_Recovery_Inductor_Candidates:Coilcraft_XFL4015_StartPin1_RIGHT_SOURCE_CANDIDATE`
- The active project library table registers that library exactly once; its project-relative URI resolves to the inspected local library

## Native geometry and source alignment

The exact candidate loads through `pcbnew.FootprintLoad`. Two numbered, rectangular F.Cu/F.Mask lands are 0.98 x 3.40 mm, centered at (+1.185, 0) for pad 1 and (-1.185, 0) for pad 2. The pad spacing is 2.37 mm center-to-center and 1.39 mm edge-to-edge. Pad numbering agrees with the previously inspected Coilcraft top-view start mark: the right-hand +X terminal connects to `SW_CORE`.

The F.Fab rectangle spans +/-2.15 mm, or 4.30 x 4.30 mm maximum body. The start bar is on +X, at x = 1.95 mm. The F.Courtyard rectangle spans +/-2.40 mm, giving 4.80 x 4.80 mm line-center geometry with a 0.05 mm stroke. Body and start-mark placement agree with the source review; the courtyard remains a declared project process assumption.

Each copper pad has explicit 0.05 mm mask expansion, giving a 1.08 x 3.50 mm opening. Each has a separate, unnumbered F.Paste-only 0.98 x 3.40 mm rectangle at the same center. Numbered copper pads do not include F.Paste.

The independent paste control saved and reloaded two separate fixture copies: zero global margins and global margin -0.02 mm / ratio -0.10. The requested override survived reload. Actual native F.Paste SVG exports have identical geometry in both cases, and both aperture bounds measure **0.98 x 3.40 mm**. Unset local paste properties do not imply global shrink of these non-copper apertures. The earlier tentative concern was rejected by this test.

Source: [Coilcraft Document 769-2, revised 03/10/26](https://www.coilcraft.com/getmedia/84927b8b-f089-421b-a7f4-a0fa23afe908/xfl4015.pdf), PDF SHA-256 `6535ab70d0ef65ba03d4b0800e206fc7867f26464e2d9dfd5dd931a2bcb0c7c1`. Raw vendor content is excluded.

## Controls and limits

The supplied native fixture loads with six copper layers, pad 1 on SW_CORE at (6.185, 5) and pad 2 on VDD0P8_CORE at (3.815, 5). Independently rerun native DRC reports zero violations and zero unconnected items. The clearance negative control reports exactly one violation: a 1.3900 mm gap against a deliberately raised 1.4000 mm minimum. An independently mirrored numbered-land control is rejected by the source-geometry check. These controls verify local geometry and the stated start-lead mapping.

No explicit Coilcraft under-coil/layer prohibition is added, and no Murata restriction is inherited. The 1.60 mm source height is metadata, not a new height constraint or a validated 3D assembly. These results do not prove complete-board routing, assembly yield, current rating in the enclosure, thermal loss, saturation, stability, EMI, or factory acceptance. Mask, paste quantity/stencil, courtyard and placement remain conditional process choices.

## Evidence

- `native-review.json`: source hashes, loaded pad/outline geometry, active R5/R6 parity, library registration, controls and limitations
- `native-runs.json`: fresh export and independent DRC commands/results
- `normal_drc.json`, `negative_clearance_drc.json`: native DRC outputs
- `paste-override-review.json`, `paste-override-runs.json`: persisted override settings and measured native SVG aperture geometry
- `native-paste-zero.svg`, `native-paste-override.svg`: actual native paste exports
- `check_native.py`, `check_paste_override.py`: bounded read-only-source verification scripts
