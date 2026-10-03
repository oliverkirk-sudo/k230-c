# Physical candidate RCV-PHYS1

Active reconstruction candidate: this schematic binds U14 and U92 to independently audited manufacturer land examples. Frozen RCV-LOGIC1 remains the electrical reference. No PCB has been reconstructed in this branch. Exactly six copper layers, 38 mm outline, 140 contacts and top-only assembly remain requirements.

TI mask expansion is an engineering choice with an 80 µm nominal web. NXP source mask expansion produces a 55 µm web; KiCad merges these openings when global minimum mask web is 75 µm. Use actual exported CAM verification. Neither geometry is factory-approved. Do not globally relax unrelated mask rules to make these packages pass. Copper, etch, mask registration, stencil and assembly tolerances require a coherent process contract.

R574 remains without a qualified footprint. Default R528 is DNP and storage remains inhibited. Footprint assignment and ERC do not qualify thermal behavior, startup, DDR routing, timing, or manufacturing.
