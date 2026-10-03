# R4 BGA physical identity candidates

This revision assigns U1/U2/U3 native footprints without changing any component value, pin function, net or population attribute. Coverage is158 assigned references and96 unassigned out of254. All1509 electrical bindings are preserved and R528 remains DNP, with storage inhibited. The active schematic remains cad/recovery-physical-candidate/CMK230_Core_REVIEW.kicad_sch.

## Source and geometry boundary

The K230390-ball and Micron BH153153-ball copper/mask/paste pad subtrees are byte-identical to the recovered candidates; their original source/process warnings remain. The new library adds an engineering A1-corner cue on K230 F.Fab (A1 remains absent) and corrects BH153 to the maximum11.6×13.1mm F.Fab envelope, with12.1×13.6mm courtyard. Original legacy footprints remain unchanged. These are drawing/assembly-envelope corrections, not copper edits or claims about a physical manufacturer marking. This imports their footprint geometry only, with no eight-layer board, fanout, vias or tracks. Their recovered source-map consistency was audited in R3.

For MT53E256M32D2FW-046 AAT:B, the Micron Rev.F10/2020 manufacturer PDF was freshly retrieved from its [published distributor source](https://www.mouser.com/datasheet/2/671/200b_z00m_sdp_ddp_auto_lpddr4_lpddr4x-3193603.pdf). SHA256 b29c808baa7e42fca9b7ccc54b673142d26b49a1fee6b3053cc8691c21832552 matches the recovered evidence. Figures5/7 were visually inspected again. Top view, balls down, has0.80mm column pitch and0.65mm row pitch; rowsL/M and columns6/7 are absent. All200 physical sites, including NC/DNU sites, are retained. Body maximum is10.1×14.6mm; package maximum height is1.1mm. There is no3D model; height is recorded in package-metadata.json.

The new RAM footprint uses engineering NSMD copper diameter0.30mm, mask opening0.40mm and200 separate0.30mm paste-only apertures. These are provisional PCB-process choices, not Micron land recommendations. The source's post-reflow ball dimensions under a specified SMD-pad condition must not be reinterpreted as validation of our NSMD PCB land. The10.6×15.1mm courtyard is an explicit250µm project allowance around maximum body, not assembly-process approval.

K230 copper/mask/paste diameters remain0.27/0.37/0.27mm; eMMC remains0.30/0.40/0.30mm. Preserve the existing eMMC candidate's filled/planarized/capped via-in-pad warnings where such vias are later proposed. No vias are added here and no HDI construction is chosen by a footprint assignment. Copper etch, mask registration, paste/stencil, ball/joint tolerances, placement, reliability and lifecycle/sourcing remain open. Raw manufacturer PDF and rendered pages are not redistributed.

## Checks and limits

Fresh KiCad9.0.2 export preserves the254-component/1509-binding circuit with exactly three reference-level footprint changes across21 symbol units. All743 numbered pads match the source ball identities, coordinates and active pin functions. Wrong mirroring, missing unused ball and incorrect row pitch are rejected by controls. No NC/DNU ball becomes an absent solder site.

BGA_IDENTITY_GEOMETRY_ONLY is an isolated66×32mm six-copper-layer fixture, with unique single-pad test nets. Its0.1016mm nominal clearance check passes with no DRC findings. It is deliberately not the38mm core, not electrically interconnected, and not a fit/escape/timing/impedance/return-plane witness. A six-layer count alone does not define a manufacturable stack. No whole-board DRC or DDR timing pass is claimed. The required core remains38×38mm,140original contacts and top-only assembly.

Re-run validate_coverage.py with explicit --project, --baseline (verified R3) and --runtime directories using Python with pcbnew. Native reports accompany this revision. Full physical integration still needs the96 other footprint gaps resolved and then placement, PDN, six-layer/HDI fanout, matching, manufacturing review and physical high-temperature/startup testing.

The eMMC manufacturer PDF at https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/234/EMMC_5F00_DATASHEET.pdf was freshly recovered with SHA25652ad8018f63554d3e34f970b1516e488543c6a25bd144bcbf33d666fa2a82d71; mechanical page11 was visually inspected. Its56 package test contacts have no solder balls and are not added as PCB lands.
