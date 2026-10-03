KiCad 9.0 actual cloud desktop GUI test, 2026-09-30 UTC

Test target: immutable extracted D0 CAD copy, not a finished internal core-board design.

Schematic loads: four symbol units, 140 module pins.
GUI ERC: 139 Pin not connected errors, 0 warnings. No errors were suppressed. Four default ignored test types are visible in erc-ignored.png: single-use global label, four-way junction, SPICE model issue, footprint filter mismatch.

PCB outline loads. Board status: 0 pads,0 vias,0 track segments,0 nets. GUI DRC:0 errors,0warnings,0unconnected items; schematic parity not run. A blank-outline DRC is not validation of a functioning circuit or manufacturing readiness.

Carrier mating footprint imports and displays140pads. Initial GUI Footprint Checker:1error (no courtyard defined),0warnings. The conservative assembly courtyard correction is complete. GUI retest:0 errors,0 warnings. The temporary import filename f is byte-identical to the delivered footprint, SHA256 4fcfaf56d54d20161bed00568c61657c48e143d964af848d7b44a9133fcd10ad. This footprint is a carrier land pattern, not a fabricated castellated core-board pad/drill design.

Screenshots were captured directly from the applications. No physical simulation, signal integrity/DDR timing analysis, firmware test or real hardware test was performed.


Final integrated update (2026-09-30): final13-root/power/erc.png show actual GUI on frozen thirteen-sheet master. Final GUI ERC51 =50errors+1warning, matching CLI. integrated-*.png are earlier ten-sheet/223-issue checkpoint, not final. No fabricated PCB/hardware qualification is implied.
