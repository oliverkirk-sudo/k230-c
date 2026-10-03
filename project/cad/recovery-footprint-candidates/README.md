# Isolated compact logic footprint candidate

Read `../../recovery/logic-footprint-review/REVIEW.md` before use. This directory contains the TI DSF0006A source-example footprint and local geometry/electrical-map fixtures only. It is not a board design or fabrication release.

U14 and U92 remain unassigned in the frozen active electrical candidate. No Nexperia SOT1160-1 footprint is supplied because its exact visual land audit remains blocked.

Preserve the TI footprint's six electrical copper pads, six explicit mask-only openings and six explicit paste-only openings. The 0.08-mm nominal mask web requires independent geometry/process review because native DRC does not reliably cover this construction. The stencil thickness is a TI example, not factory approval.

`TI_DSF_U14_Pin_Parity_ONLY` uses actual U14 net names and deliberately leaves the one VDD_3V3 tie unrouted. `TI_DSF_Geometry_QA_ONLY` gives every pad a distinct net to expose intrinsic clearance defects. The Negative/Process boards are deliberately stricter diagnostic fixtures; never use them as production settings.
