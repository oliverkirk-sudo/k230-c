# R12: separate 22 µF input-bank candidate

This is a coherent alternative circuit, not the preferred or production-qualified core. The baseline at cad/recovery-physical-candidate is preserved byte-for-byte from published R11. Open cad/recovery-inputbank-candidate/CMK230_Core_REVIEW.kicad_sch to inspect this alternative. No full PCB or manufacturing output is produced.

## Exact revision

Eight existing positions become22µF CL31B226KPHNNNE input candidates: C203,C210,C211,C216,C217,C220,C225,C230. Only C204,C221,C226,C231 are removed. U22/U23 retain two local bulk capacitors each; U21/U24/U25/U26 have one each. C205,C209,C215,C222,C227,C232 retain their100nF bypass duties and values. All other nominal values, component population/BOM flags and numbered pin/function/type/net identities remain unchanged.

The candidate contains250 components and1501 bindings across457 nets. It has238 assigned footprints and12 gaps. The physical baseline remains254/1509 with230 assigned and24 gaps. JP1,R45,R47 and R528 remain DNP. Default storage qualification is still inhibited.

## Evidence and cost

Fresh manufacturer curves, not the archived result alone, support a conditional screen of6.925µF per selected part at5.5V. The pairs screen at13.849µF against the adopted8µF TPS628640B input criterion; the singles screen at6.925µF against the3µF TPS6282xA criterion. Initial tolerance, normalized typical AC response, temperature, aging and model reserve are individually identified in source-review. Separate typical curves and illustrative reserves do not establish a guaranteed combined minimum or lifetime qualification.

Nominal input bulk capacitance rises from120 to176µF. The same six100nF bypasses are retained and excluded from those bulk totals. Charging/inrush, source impedance, VIN ringing, input RMS current and ripple heating require review. TPS628640B's VIN falling-rate requirement below UVLO remains a hard integration gate; the favorable Ceff screen does not demonstrate compliance.

Matched source geometry comparisons add approximately34.40–36.08mm² despite removing four parts. The actual selected R11 footprint has a4.85×2.45mm engineering courtyard; eight rectangles total95.06mm² before routes, loops and access. That exact reservation and the earlier matched-clearance comparisons are different metrics. Neither proves38mm board fit. Continuing actual copper, local return and inductor/sense constraints remain required.

## Coherent source and checks

The alternative is regenerated from its sibling build_review.py with guarded original10µF values and exact VIN_5V/GND pin mappings. Source generator declarations and libraries shared with the baseline are not edited. A historical sidecar field is clarified as exclusion from generic Samsung bypass reassignment; it is not a claim that later Murata eMMC footprints are absent.

validate_candidate.py accepts explicit project, baseline and runtime directories. It verifies all remaining component properties and the complete pin/function/type/net graph, the generated pin CSV, symbol pin library, mandatory bypasses, DNP safeguards and exact source footprint identities. Fresh ERC reports zero violations. A separate runtime regeneration reproduces the same electrical contract. Negative controls reject an undeleted reference, removed100nF bypass, wrong survivor value/footprint, populated R528 and a capacitor moved from input to output.

All1417 already-published project files remain byte-identical; only the sibling and its review directory are new. Source review was originally bound to R10; the explicit R10→R11 scope bridge confirms the reviewed input/regulator/divider/bypass scope is unchanged, without claiming equal whole-master hashes.

## Remaining release boundaries

This alternative does not qualify combined Ceff, VIN collapse behavior, startup, current/thermal stress, stability, PDN, routing or placement. It does not resolve the47µF land gap, RTC startup/accuracy, BootROM/OTP storage policy, memory procurement or full-board process acceptance. The original baseline remains the comparison source. Promotion requires the relevant electrical and physical validation; no production readiness is claimed.
