# RCV-LOGIC1 reconstructed electrical candidate

This is the active reconstruction candidate; the verified v12 HT-DRAFT13 source and the intermediate RCV-TF1 branch remain unchanged. This is new, source-checked work, not recovery of the lost HT18 or HDI geometry.

Changes from v12:
- R574 adds a conditional 10 kΩ TF_HOST_CLK-to-GND idle bias. Its numerical CLKA leakage, switching/feedthrough and partial-power qualification remain open
- U14 becomes TI SN74LVC1G97DSFR with identical numbered nets. R33 remains 270k
- U92/U94 become one Nexperia74AUP2G97GUX using the exact ten-pin GU map. Both B inputs are grounded to form two AND functions. All passives, including C810/C813, remain
- R528 remains DNP; storage is inhibited by default

Fresh KiCad9.0.2 netlist export contains254 components and1,509 pin bindings. This count coincidentally matches v12; the actual changed pin map is explicitly tested. All1,493 bindings outside the three replaced logic references match RCV-TF1, including the R574 addition. Sixteen integrated PG/qualifier/reset/mode states and four corruption cases pass. A clean serial ERC rerun reports0 violations. Both changed logic sheets were exported and visually inspected.

U14 and U92 footprints are intentionally unassigned in this electrical branch. The reviewed TI land drawing still needs a generated-footprint check; the Nexperia drawing's visual/coordinate audit is incomplete. R574's footprint also remains unselected. There is no PCB file in this branch and no whole-board fit, routing, DFM or thermal acceptance.

See `../../recovery/compact-logic-review/REVIEW.md` for exact primary sources, hot leakage/logic budgets and remaining gates. The dual's output loading, discrete threshold rows, rail ramps and partial-power behavior must not be inferred from a truth table. Six-layer HDI construction and physical verification are still to be rebuilt.
