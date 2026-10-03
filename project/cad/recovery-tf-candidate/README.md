# RCV-TF1 electrical candidate

This separate, newly reconstructed schematic adds only R574, a candidate 10 kΩ idle pull-down from TF_HOST_CLK to GND at the translator input. It does not claim recovery of the lost HT18 files. No PCB is assigned to this branch.

Fresh KiCad 9.0.2 export and ERC pass with zero reported violations. All 1,509 baseline pin/function/type/net bindings and all 254 baseline component values, footprint assignments and properties remain identical; the result has 255 components and 1,511 bindings. Four negative controls catch a missing or miswired pull-down and loss of the default R528 DNP setting. The changed sheet was exported and visually inspected.

The official NXP datasheet confirms that CLKA has no internal bias. The 10 kΩ value remains a conditional engineering candidate: no maximum CLKA leakage is published, off-channel clock feedthrough and edge timing require validation, and CLKB is high impedance in translator shutdown. The exact resistor footprint remains unselected. Read `../../recovery/tf-clock-review/README.md` and its source/implementation reports.

Six-layer HDI, full-board physical integration, boot qualification and high-temperature acceptance have not been reconstructed or passed. R528 remains DNP and storage remains inhibited by default.
