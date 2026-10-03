# New castellation proposal, not fabrication release

Open `CMK230_Castellation_NOMINAL_PROPOSAL.kicad_pcb` to review the editable 38 × 38 mm edge geometry. The library contains 140 plated, all-layer castellated pads at 1 mm pitch, Ø0.50 mm requested nominal finished opening, and 0.80 × 1.80 mm oval copper. Both mask layers have 0.05 mm expansion; there are no paste apertures. The board has eight copper layers and a proposed 1.2 mm nominal thickness. No dielectric stack or impedance width is invented in this CAD file.

This is a new module fabrication proposal. The original carrier's 1.6 × 0.56 mm oval lands at normal coordinates ±18.746 mm are a different geometry. The proposed module drill rows lie at ±19 mm. The inner drawing rectangle is a conditional 1.30 mm component reservation, not a fabrication keepout rule accepted by a factory.

Read the [source-backed review](../../engineering/mechanical/castellation-stackup-proposal-review.md), [dimensional proof](../../engineering/mechanical/castellation-proposal-dimensional-proof.json), [source comparison](../../engineering/mechanical/castellation-fab-source-review.json) and [stackup proposal](../../engineering/mechanical/core-stackup-process-proposal.json). The main CAD and committed area-screen baseline are unchanged.

Do not use this footprint as the carrier mating footprint, order fabrication from it, or infer factory acceptance from a clean KiCad DRC. Run `engineering/mechanical/build_castellation_proposal.py` with the system Python/KiCad environment to reproduce the proposal. Generated native UUIDs may change while geometry remains identical.
