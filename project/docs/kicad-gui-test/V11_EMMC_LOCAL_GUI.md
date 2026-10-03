# v11 eMMC local-trial GUI test

The exact BH153_SPARSE_LOCAL_TRIAL.kicad_pcb was opened in cloud KiCad PCB Editor. The visible board statistics were153 pads,29 vias,16 track segments,136 nets and17 unrouted items.

A fresh GUI DRC run reported17 errors, all unconnected items, and32 dangling warnings. No tests were ignored. Schematic parity was not run for this local fragment. This matches the command-line/native validation; it does not prove complete core routing, timing, power-plane connectivity, capacitor placement or fabrication acceptance.

Screenshots: v11-emmc-local-open.png and v11-emmc-local-drc.png. The GUI operator did not save or alter the geometry. The earlier high-temp-* schematic GUI screenshots remain historical v9 evidence, not a GUI check of the current HT-DRAFT11 precision-resistor changes.
