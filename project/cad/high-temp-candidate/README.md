# Conditional high-temperature core variant

Open CMK230_Core_REVIEW.kicad_pro. This is a separate candidate; cad/integrated retains the Samsung reference. The user requested only the core, including its140-pin electrical handoff. No socket, carrier or external cooling system is designed here.

Current model:18 sheets,254 XML references;247 populated functional components after excluding non-purchasable edge copper J1, fourDNP options and twoobservation points. ERC0 and source/netlist checks are model results. DefaultR528 isDNP and storage remains inhibited. This is not a bootable or temperature-qualified board and contains no manufacturing PCB.

## Explicit substitutions

- U2 MT53E256M32D2FW-046 AAT:B,1GiB LPDDR4,105°C case grade. Its200 physical/64 absent positions are independently checked. CS0/CKE0 names and fiveDNU→NC changes are explicit. FW body10×14.5mm differs from Samsung10×15mm; package balls are not a PCB land pattern
- U3 MTFC16GAPALBH-AAT,16GB eMMC,105°C ambient grade. VCC/VCCQ and allground balls are explicitly mapped. SevenVSF positions are functional bidirectional pins intentionally unused, not unbondedNC
- Micron VDDIM hasC64 2.2µF andC65 100nF as aTable13-based candidate; C69/C70 andC71/C72 provide localVCCQ/VCC pairs. Exact effective capacitance, ESR, thermal and placement review remain open. No Samsung capacitor claim is transferred
- U3 H5 DS has its own47k pulldownR573; it is not connected to the unused host strobe. HS200 remains thetarget; HS400 is not claimed
- U91/U93 now use Nexperia 74AUP1G17GW,125 / 74AUP1G06GW,125; U14/U92/U94 use 74AUP1G97GW,125. U14 implements OR with A tied high; U92/U94 retain AND with B tied low. These 125°C-ambient standard-package candidates have source-verified SOT353-1 / SOT363-2 lands in the separate Nexperia library. No TI DRL geometry or tiny GX land is reused

## Remaining temperature limits

Provisional screening assumes85°C enclosure air, pending clarification. This is not a declared operating qualification. NVT4858 is still85°C ambient-rated, Y2 is still85°C-rated, and K230/package/regulator heat paths remain unvalidated. The narrower Nexperia06-to-TMUX static low margin is60mV; actual ground noise and full supply/ramp behavior need validation.

A higher grade does not remove self-heating or guarantee package temperature. No external cooling implementation or performance throttling has been assumed.

## Firmware intrinsic to memory selection

Micron MR4 controls required refresh intervals. Above85°C case, shorter intervals and potentially timing derating are required. The current Samsung initialization cannot be called compatible merely because ball positions match. DDR training, MR settings, refresh polling/handling, boot image and eMMC initialization require a reviewed port. No such firmware has been flashed or claimed validated.

## Validation files

- netlist-validation.json:743 electrical pin types,65DDR joins,131 memory power/reference endpoints,62 exposedGPIO checks
- interlock-validation.json:34 structural assertions and16 steady-state combinations
- buffered-reset-static-screen.json:conditional125°C screening assumptions
- checklist/:all22 official checklist sections,44 review items,11 automated assertions, core-only boundaries
- master.xml / master-pin-assignments.csv / review.pdf:actual exported candidate

Unresolved immutableOTP/first-drive and same-OTP dual-media boot requirements remain independent of runtime firmware. No OTP operation is authorized or performed. Pin/function compatibility, SI/PI, assembly, component sourcing and physical validation remain release gates.

## Revision HT-DRAFT10

The four fixed-buck feedback dividers are scaled by 1/10, with 10k bottom resistors and 1.2nF C0G feed-forward capacitors (previously 100k/120pF). This preserves nominal ratios and RC products while reducing feedback-bias error. TNPW0402 0.1%/10ppm candidates are screened with a conservative conditional ±0.70% total resistance budget. This is not a lifetime guarantee or final passive BOM. See scaled-feedback-validation.json and the source review. All 8 resistor values and 4 companion capacitors are asserted against the actual netlist.

The current high-temperature area screen is 1041.62mm² with optimistic dense small-passive reservations, or 1174.42mm² with the stated 0402 reservations. Both still contain unqualified bulk-capacitor assumptions. The separate 1.30mm castellation reservation yields a conditional 1253.16mm² interior; it is a new manufacturing proposal requiring acceptance, not an automatic fit pass. X7R capacitor studies increase the required area and leave effective-capacitance and loop/transient gates. No complete placed/routed PCB is provided.

Current revision was exported and checked with KiCad CLI; root/reset PDF pages were visually inspected. The high-temp-* actual GUI captures are the earlier v9 state, before these package/divider edits, and are preserved as historical evidence only.

The J1 edge contract now has an explicit proposed core footprint and is included on-board, while excluded from the purchasable BOM. All 140 contact nets are bound in ../edge-bound-seed. That separate seed omits every internal device and route; it is not full PCB parity or a production layout.

## HT-DRAFT11 work in progress

Nineteen precision-resistor positions now have conditional TNPW0402 candidates and current source-derived IPC lands. This includes the unchanged88.7k/10k VIN divider, whose total-resistance screening budget is now±0.70%; its modeled~4V role remains, but hot loaded dropout and reset latency remain open. Calibration/VREF/VBUS nominal values and nets are unchanged. Actual calibration-pin dissipation and mission-profile drift still require qualification.

Historical HT-DRAFT11 import contained38 footprints and341 pad-net bindings. The current import figures appear below; it remains incomplete and unplaced. ERC0 is solely a schematic-model result.

## HT-DRAFT13: Schmitt storage-disable OR

U14 is now74AUP1G97GW,125 on the already-reviewed SOT363-2 footprint. Its exact map is1 B=GLOBAL_DISABLE,2 GND,3 A=VDD_3V3,4 Y=DISABLE_OR_TF,5 VCC=VDD_3V3,6 C=MODE_TF. A=1 gives B OR C; tying B high would implement the wrong function. R33 is now270k CRCW0201 1%/100ppm, under an explicitly conditional±10% total resistance acceptance requirement; its footprint remains unassigned. C34 stays local100nF on3V3. R528 remains DNP and default storage remains inhibited.

The change addresses the previous LVC gate's unclosed10ns/V input limit on the10k/open-drain GLOBAL_DISABLE release. With R33min243k, modeled low-state current is15.9595µA including2µA receiver leakage, within Nexperia's20µA continuous-supply-range output row. VOL≤0.11V leaves340mV to TMUX VIL0.45V; valid high leaves1.93513V above VIH1.2V. This is a bounded static screen. Actual output capacitance/edges, exact threshold behavior across the selected rail, leakage beyond the declared budget, slow-input current, supply ramps and thermal/lifetime behavior remain gates. Neither propagation-delay tables nor the pullup alone guarantee actual output rise time. See [source/slew review](../../engineering/passive-resistor-candidates/U14_SLEW_ADDENDUM.md).

Fresh schematic/netlist/PDF exports and ERC0 accompany passing interlock, power, precision, bypass and U14 regressions. `u14-or-validation.json` verifies all6 pins,4 OR rows,8 storage combinations,1503 unchanged non-U14 pin/net assignments and40 unchanged Samsung/source-file hashes. This is not hardware qualification.

The refreshed partial PCB has150 imported footprints,566 verified pad/net bindings and149 internal footprints parked outside the outline;104 references still lack footprints. Native parity reports exactly those104 missing footprints, with no imported-footprint mismatch. Native DRC retains58 clearance violations and351 unrouted items, including the new U14 high-tie connection. No board rule or violation was suppressed, and no placement/routing completion is claimed.
