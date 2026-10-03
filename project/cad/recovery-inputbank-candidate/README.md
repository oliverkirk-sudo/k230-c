# RCV-INBANK-R12 conditional sibling

Open CMK230_Core_REVIEW.kicad_sch to inspect the alternative eight-part22µF input-bank circuit. The preferred comparison baseline remains ../recovery-physical-candidate; every existing R11 project file is unchanged.

Exactly eight input values/footprints change and four named input capacitors are removed. All six100nF bypasses remain. No other values, pin/net/function/type bindings or population states change. The candidate is250 components/1501 bindings, with238 footprint identities and12 gaps. Fresh ERC and generator/graph checks pass within that scope.

See ../../recovery/r12-input-bank-candidate/README.md for exact references, current source evidence, Ceff assumptions,120→176µF nominal input increase, inrush/VIN-fall gates and34–36mm² matched-area cost. No full PCB, physical fit, operating qualification or production release follows from this candidate. R528 remains DNP and storage qualification remains inhibited.
