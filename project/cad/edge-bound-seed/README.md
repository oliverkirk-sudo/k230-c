# Edge-bound electrical PCB seed — incomplete

This is the new core's own castellated copper, not the carrier's mating footprint. Every pad 1–140 is assigned the corresponding J1 net from the current high-temperature master.xml. The high-temperature schematic now includes J1 on-board and assigns this proposed footprint; J1 is excluded only from the purchasable component BOM. The Samsung reference remains unchanged.

The board contains only those 140 castellations and the mechanical proposal. It has no internal components, tracks or vias. It is not a full schematic-to-PCB parity result, a finished layout, or a fabrication deliverable. Footprint/schematic UUID association for an interactive update and import of the internal components remain to be completed. The deterministic binding script and JSON validate net names and numbered contact positions against the exported master netlist.

The separate mechanical-only proposal remains frozen, with its independent 47-check review. Factory acceptance, 1.30mm reservation, BGA lands/escape, pressed stack, panel supports, assembly tolerances, SI/PI and thermal gates all remain applicable. DRC on this seed is unsuppressed and retains expected unrouted repeated-net contacts. Missing internal devices cannot be discovered by a PCB-only DRC; do not confuse it with full netlist parity.

Fresh PCB-only DRC: 0 geometry violations, 12 unconnected repeated-net items. Schematic parity was not run and internal component absence is not a pass.
