# BH153 sparse local native trial

Open `BH153_SPARSE_LOCAL_TRIAL.kicad_pro` in KiCad 9. This project is an **unqualified local analysis window**, not the 38 mm CM-K230 module or a fabrication release.

Exact candidate: MTFC16GAPALBH-AAT. All 153 physical lands and 29 modeled vias are retained. NSMD copper/mask/paste diameters are 0.30/0.40/0.30 mm. Filled, planarized, copper-capped VIPPO is required; 0.10 mm stencil and 1.2 mm board thickness are reference assumptions only. No dielectric stack, PDN or complete routing is claimed.

Native DRC is deliberately unsuppressed: **17 connectivity errors and 32 dangling-item warnings**. There are no other nominal-geometry violations. Eleven host signals have local exits only. DS remains unused, and all 120 NC/RFU/VSF lands remain individually open.

The `preview` directory contains native SVG plots and PNG renders. Red is L1/F.Cu, orange is L3/In2.Cu; the overview projects both onto one image, so overlapping projections must be read with the separate layer views. White via centers depict KiCad's nominal drills, not physically open holes in the required capped process.

The detailed discrepancy report, raw DRC JSON, active-rule positive controls, source/net mapping, validation and generator are under `../../../engineering/bga-native-trial` from the project root: [engineering report](../../../engineering/bga-native-trial/NATIVE_DRC_DISCREPANCY_REPORT.md).

The `.pretty` library contains a reusable editable engineering footprint. It carries physical pin functions but no board-specific nets. It is not manufacturer-qualified.
