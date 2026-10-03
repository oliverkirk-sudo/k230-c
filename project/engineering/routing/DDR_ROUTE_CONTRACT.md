# DDR physical routing contract inputs

The 65 actual high-temperature SoC-to-LPDDR4 joins have been joined by **physical SoC ball** to the official package-length table. All 64 high-speed nets have a numeric package length; asynchronous RESET is absent from that table. The guide's known duplicated DQSB aliases are recorded as hazards and never used to rename or reconnect the audited nets.

The live Micron pins define four data-byte groups of 11 signals each (8 DQ, DMI and both DQS), two 10-signal command/clock groups, and RESET. Automated checks enforce those cardinalities. This follows the present source-derived mapping; it does not authorize arbitrary byte/CA swaps or establish training compatibility.

The visually checked official LPDDR4 routing figure recommends DQ-to-DQ arrival mismatch below 20 ps, DQ relative to DQS within ±10 ps, command/address relative to CK within ±10 ps, and DQS relative to CK within ±60 ps without write leveling. The larger training deskew ranges are not substituted as routing allowances. The text calls for 50-ohm single-ended / 100-ohm differential routing, 3W spacing, equal via counts for comparable signals and no more than two layer changes.

The package's physical lengths already differ by almost 5 mm across one data-byte group. Therefore blindly matching only board copper length would be wrong. The exact Micron package delays and the final PCB propagation/via delays are not available here, so the CSV deliberately leaves total flight-time fields unresolved. It does not turn micrometres into picoseconds using an invented velocity. Final constraints must use the actual manufactured stack and applicable package timing model, with SI and DDR training verification.

This is a constraint input ledger, not a routed PCB or timing pass. Source links and source-netlist hashes are in high-temp-ddr-route-contract-validation.json. The proprietary K230 IBIS model was neither run nor redistributed.
