# Physical candidate RCV-PHYS1

Active reconstruction candidate: this schematic binds U14 and U92 to independently audited manufacturer land examples. Frozen RCV-LOGIC1 remains the electrical reference. No PCB has been reconstructed in this branch. Exactly six copper layers, 38 mm outline, 140 contacts and top-only assembly remain requirements.

TI mask expansion is an engineering choice with an 80 µm nominal web. NXP source mask expansion produces a 55 µm web; KiCad merges these openings when global minimum mask web is 75 µm. Use actual exported CAM verification. Neither geometry is factory-approved. Do not globally relax unrelated mask rules to make these packages pass. Copper, etch, mask registration, stencil and assembly tolerances require a coherent process contract.

R3 binds R574 to a source-derived Vishay0201 land candidate and L22–L26 to existing Murata land candidates. These six added assignments preserve all values and nets;155 references now have footprints and99 remain unassigned. See ../../recovery/r3-physical-coverage/README.md for current validation and process limits. None of these footprints is factory-qualified. Default R528 is DNP and storage remains inhibited. Footprint assignment and ERC do not qualify thermal behavior, startup, DDR routing, timing, or manufacturing.

R4 adds all three BGA engineering footprint identities:158 assigned,96 unassigned. See ../../recovery/r4-bga-coverage/README.md. No full six-layer layout or factory-qualified BGA construction is implied.

R5 conditionally changes only eight DAT pullups to43k and assigns their source-land candidates:166 assigned/88unassigned. See ../../recovery/r5-dat43/README.md. Resistance-budget compliance is distinct from lifetime, signaling, boot and production qualification.

R6 assigns25 conditional bias-resistor footprints and the exact L21 source-land candidate, preserving all values and nets:192 assigned/62 gaps. See ../../recovery/r6-passive-coverage/README.md. Its correct winding-start orientation and larger maximum-body reservation do not establish a power-loop or board-fit pass.
