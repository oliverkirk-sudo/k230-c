# R7: links and fabricated core features

This is a conditional schematic/footprint reconstruction checkpoint, not a routed or production-ready core. The published R6 checkpoint is its exact predecessor.

## Verified change

Ten references receive footprint identities: R205/R206, R220/R221/R401/R528/R561, JP1 and TP81/TP82. JP1 and both test pads become BOM-excluded fabricated copper features. All 254 values, 1,509 pin/function/type/net bindings across 457 nets, on-board flags and population states remain unchanged. Coverage is now 202 assigned and 52 unassigned. JP1, R45, R47 and R528 remain DNP.

The source-derived WSL and WFZ copper lands are accompanied by explicit engineering body, courtyard, mask and paste assumptions. R205/R206 use the existing TNPW land option; ordinary links use the existing CRCW land. Exact part current, hot resistance, tolerance drift and assembly limits remain conditional. See source-review and the independent audit for source URLs, dimensions and applicability limits. The source review records the earlier unassigned footprint state; this checkpoint adds geometry without changing those seven references' electrical identities or values.

JP1 is an intentionally open two-pad solder bridge. Open selects the eMMC mode intent; a manual bridge selects TF mode intent. It is serviceable only with power removed and discharged. Neither state establishes BootROM/OTP or storage-voltage qualification. TP81/TP82 are bare, top-side observation pads on their original PMU status nets, without paste or drills; they are not external drive ports. These are engineering proposals, not factory land recommendations.

## Validation and assembly limits

Fresh KiCad 9.0.2 ERC reports zero violations. The five-reference 26 x 12 mm geometry-only fixture has zero DRC items; its copper/mask/paste exports contain 8/8/4 flashes. The separate independent ten-reference fixture preserves shared net names and therefore reports three unrouted connections, with zero rule violations. It exports 18/18/14 flashes and only six fitted resistors in the position file. Neither fixture is the 38 x 38 mm module or proves connected circuitry.

The population helper preserves native copper and net identity while excluding fabricated features from BOM/position output. Negative controls catch lost DNP, lost copper, wrong test-pad net, inappropriate BoardOnly and position/BOM reinclusion. R528 remains electrically inhibited by default.

IMPORTANT: R528's two paste apertures remain in KiCad's default paste export despite DNP and placement exclusion. Production needs an explicit assembly/stencil variant and inspection of the resulting paste output. Diagnostic Gerbers here are not manufacturing releases. The same policy must cover other DNP parts; DNP alone is not a stencil rule.

## Remaining work

The 52 footprint gaps comprise 40 capacitors, nine ferrites, two oscillator feedback resistors and the RTC crystal. Combined hot/bias/aging effective capacitance, clocks, reset/PG margins, storage boot policy, sourcing and thermal limits remain open. Full top-only 38 x 38 mm placement and a complete six-layer PCB remain unfinished. No prior lost layout geometry is recreated by this checkpoint. Factory stackup, copper/mask/stencil tolerances, routing/SI and physical electrical/thermal tests are release gates.

Reproduce the lead checks with validate_coverage.py and explicit --project, --baseline, --runtime arguments using system Python with pcbnew. The independent validator similarly accepts explicit input/output paths. Keep diagnostic outputs apart from production exports.
