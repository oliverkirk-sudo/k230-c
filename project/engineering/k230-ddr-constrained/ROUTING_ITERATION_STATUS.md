# DDR routing iteration status — 2026-09-30

No complete electrically qualified DDR connection has been produced. The original local escape and actual-link trials are retained as separate evidence; they do not replace the module PCB.

The initial fixed-anchor two-package trial reached 38 of 65 links without nominal geometric conflicts. All 27 failed nets were independently routable when prior-route occupancy was removed, identifying congestion/order rather than isolated static traps. Joint via-to-via routing then retained all physical lands/vias and all non-DDR copper. Differential pairs remain on common layers with two actual transitions per leg; per-byte common layers were relaxed as an engineering target, not waived as a manufacturer rule.

The frozen pair-preserving L3/L8 candidate contains 65 paths but 146 conflict events. Independent analytic checking found 23 nominal geometry failures across 12 net pairs involving 19 nets, with 7,806,969 checks. Those 19 nets exactly match the router conflict list. It also found 120 Figure054 spacing misses and differential planar skews of 5.85–7.6375 mm. Thus path existence is not accepted connectivity, and no timing pass is asserted.

A resumed trial reduced the event score to 106 but remains rejected and has not received the same independent full geometric audit. It was deliberately stopped after the independent impedance screen found the catalog L3/4mil combination incompatible with the intended nominal50ohm screen. Continuing to tune this width/stack would not resolve the electrical requirement. The separately attempted third-layer allocation is also rejected and has no qualified reference-plane/PDN case.

Next geometry must begin with an impedance-consistent stack/width proposal, continuous ground references, appropriate spacing and physical capacitor/other-component constraints. Then revise SoC/RAM anchors or fanout and reroute. Package delays, coupled pairs, phase/flight-time matching, fabrication tolerances, PDN, thermal behavior and hardware training remain independent gates.

See ../impedance-screen for analytical source assumptions and limits; see joint-link-audit for independent path, geometry, source identity and spacing checks. Frozen route-file hashes identify their actual generation inputs. Later U14 control changes are unrelated to DDR identities and require explicit semantic reconciliation rather than silently replacing historical hashes.

The final independent auditor includes nine mutation regressions; all pass. It reconciles all743 SoC/RAM/eMMC endpoints against the exact frozen CSV and current CSV/XML without rewriting old source hashes.
