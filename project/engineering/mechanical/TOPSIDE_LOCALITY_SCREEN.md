# Conditional full-core locality trial

This is a rejected heuristic placement trial, not evidence that the requested 38 mm core is impossible. It tests the stronger X7R capacitor-count sensitivity, distributed fixed buck positions, the three BGA reservations and all other current component envelopes. It includes top-side local bypass affinity rather than simply minimizing rectangle overlaps.

The conditional 1.30 mm edge band leaves 1253.16 mm². This trial's 262 rectangles total 1229.81 mm², already approximately 98% of that area. The bounded 30-seed corner-placement heuristic cannot place all rectangles: it places 211 and leaves 51 unplaced. Numerous regulator/local-bypass rectangles also miss the illustrative 3 mm nearest-envelope target. These are shortcomings of this component/position/packing trial, not a mathematical infeasibility proof. The target is an engineering search preference, not a manufacturer trace-length limit.

Do not turn the rejected coordinates into a layout. Large BGA and regulator locations need coordinated optimization, source-qualified smaller capacitance alternatives may change the result, and functional-ball fanout must be solved before committing corridors. A successful rectangle pack would still not establish effective capacitance, via availability, loop inductance, impedance, routing, thermal performance or assembly acceptance. The stronger X7R bank study is itself conditional and is not applied to the circuit.

The 1.30 mm band already budgets component-to-mask separation using actual extents. Placing full courtyards inside it is conservative and may double-count some edge margin; this does not justify arbitrarily removing that margin without an assembler's process review.
