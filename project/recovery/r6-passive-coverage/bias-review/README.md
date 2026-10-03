# CM-K230 R3: next bias-resistor source-land screen

2026-10-03. **25 unassigned ordinary-bias positions are conditional candidates for the existing Vishay CRCW0201 source-land footprint, preserving every nominal resistance.** This is a read-only package/part and bounded DC review. It does not qualify the electrical functions, resistor lifetime, assembly process, board fit or procurement. No CAD, BOM, population or selected MPN was edited.

The active input is `cad/recovery-physical-candidate/master.xml`: **254 references, 457 distinct nets and 1,509 pin/net nodes**. It contains 62 resistor references, of which 20 have assigned footprints and 42 do not. The unchanged module contract is six layers, 38 × 38 mm, 140 contacts and top-only assembly. R33 remains 270 kΩ; R528 remains DNP. There is no complete active PCB whose manufacturability or routing is established by this report.

## Candidate batch and holds

The 25-ref conditional bias batch is:

- R31, R32, R33, R34
- R43, R44, R45, R46, R47
- R61, R62
- R203, R204, R216, R217, R218, R219
- R402, R527, R529, R530
- R562, R571, R572, R573

These are **23 populated positions plus R45/R47 DNP**. Adding a land candidate must never change DNP population. R61/R62 are ODT_CA input bias pullups; they are distinct from precision ZQ/calibration resistors. Source-based leakage and threshold evidence supports their bounded bias screen, with rank/ODT configuration and local rail distribution still open.

| Disposition | Refs | Reason |
|---|---|---|
| Separate oscillator candidates | R41, R42 | 1 MΩ is supported by the family, but crystal feedback needs gain/startup/drive/parasitic assessment; keep outside this bias batch |
| Hold existing 47 kΩ DAT pullups | R563–R570 | Preserve 47 kΩ; prove the complete resistance envelope remains within 10–50 kΩ |
| Exclude precision startup selection | R205, R206 | Preserve 56.2 kΩ, 0.8 V/address 0x49, and TI's ±1% selection-accuracy requirement |
| Exclude zero links | R220, R221, R401, R528, R561 | Supply/current/strap roles require separate treatment; preserve WSL060300000ZEA9, WFZ040200000ZE66 and R528 DNP |
| Preserve already assigned parts | 19 TNPW refs and R574 | Preserve existing grades, exact values, selected MPNs and footprints; they are not new coverage |

The 19 TNPW refs are R63–R71, R201/R202, R207/R208, R210/R211, R213/R214 and R525/R526. Their 0.1% initial, 10 ppm/K and conditional ≤0.70% total requirements must not be weakened. R574 remains CRCW020110K0FKED with its existing conditional TF-clock review.

Binding the 25 candidates in a separately authorized revision would change schematic footprint coverage from 155/254 to 180/254, leaving 74 unassigned. **That change is hypothetical and has not been made.** Coverage would still describe schematic/library assignments, not a routed PCB.

## Grade, geometry and DC stress

Use the CRCW0201 **F/K grade: 1% initial tolerance and 100 ppm/K**, supported for 47 Ω–1 MΩ. The JSON gives schema-derived candidate MPNs at the unchanged values: 4.7 kΩ, 10 kΩ, 22 kΩ, 47 kΩ, 100 kΩ and 270 kΩ. Exact orderability, lifecycle and stock were not verified. An unspecified original grade is recorded as unspecified; this review does not silently relax a stated requirement. [Vishay 20052, revision 21-Sep-2022, pp1–2](https://www.vishay.com/docs/20052/crcw0201e3.pdf)

The fresh PDF and the existing R3 footprint agree on two 0.28 × 0.43 mm copper lands, 0.23 mm inner gap, centers at ±0.255 mm, and a 0.79 × 0.43 mm copper envelope. Maximum body/height is 0.63 × 0.33 × 0.26 mm. The R3 footprint's 25 µm mask expansion per edge, 1:1 paste apertures, 180 µm nominal mask web and 1.39 × 1.03 mm courtyard centerline are **engineering process assumptions**. They are not manufacturer or fabricator approval, and this review does not edit them.

The family has 50 mW at 70°C, a 30 V limiting element voltage and a 155°C film limit. Its visually checked derating graph falls linearly to zero at 155°C: 41.176 mW at 85°C, 29.412 mW at 105°C and 17.647 mW at 125°C. Permissible working voltage is the smaller of 30 V and √(Pallowed × R). Actual PCB heat flow and solder-point/film temperatures remain necessary evidence. Enclosure air is not a measured local resistor temperature. [Vishay pp1,3](https://www.vishay.com/docs/20052/crcw0201e3.pdf)

Every ordinary nonzero ref has a numerical Vmax/Rmin and Vmax²/Rmin screen in the JSON. The conditional working band is ±10% total resistance. It is neither a guaranteed life model nor permission to relax tighter requirements. Supply bounds are the existing project regulator static corners: 1.764476615–1.836094613 V, 3.245129532–3.392164299 V, and DDR 1.100816374–1.138630968 V. VIN is screened at the converters' 5.5 V recommended-operating ceiling. Distribution, ripple, load steps, external drive, overshoot and partial-power states are outside those bounds.

The largest stress in the 25-ref batch is R204: 5.5 V across 9 kΩ gives **0.611 mA and 3.361 mW**, 19.046% of the 125°C graph limit. Thus the bounded DC stress does not force a larger package. It does not establish actual temperature, transient survivability or logic behavior. DNP calculations describe a hypothetical fitted condition only.

## Required 47 kΩ DAT resistance bound

The active eMMC is **MTFC16GAPALBH-AAT**, explicitly listed in the reviewed Micron family document. Table 13 specifies DAT pullups of **10–50 kΩ**. Therefore the existing 47 kΩ choice permits at most **+6.3829787% total positive error**, or the same ceiling for a symmetric total-error specification. The exact admissible resistance interval remains 10–50 kΩ; the upper bound is limiting. The ±10% illustrative band reaches 51.7 kΩ and fails by 1.7 kΩ. [Micron Rev G, Table 1 p2 and Table 13 p27](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/234/EMMC_5F00_DATASHEET.pdf)

**Hold R563–R570 for a complete temperature/assembly/aging/environment resistance-budget proof.** Initial 1% plus a nominal TCR is insufficient evidence. A band that reaches 50 kΩ exactly has no extra resistance-window margin. No 43 kΩ substitution is proposed or assumed. CMD R562=22 kΩ and reset R34=10 kΩ satisfy Micron's 4.7–50 kΩ windows under the conditional ±10% screen; DS R573=47 kΩ satisfies 10–100 kΩ. Those window checks do not qualify bus timing or idle-state behavior.

R205/R206 are a different constraint: TI requires 56.2 kΩ with ±1% selection accuracy, meaning 55.638–56.762 kΩ. CRCW's initial ±1% leaves no demonstrated room for additional shifts. The prior separate TNPW040256K2BYED candidate and its conditional ±0.70% total path remain separate; neither is assigned by this report. [TI TPS62864/TPS62866 Table 8-1, p12](https://www.ti.com/lit/ds/symlink/tps62866.pdf)

## Electrical gates retained per role

- **R33:** keep 270 kΩ and its ≤10% total contract. The current TI LVC97 topology gives a 15.9595 µA sink screen against the 100 µA/0.1 V source row, preserving 350 mV to TMUX's 0.45 V low ceiling. Shared-rail collapse and partial-power behavior remain open
- **R527:** the inherited worst sink screen is 379.007 µA against 400 µA, leaving only 20.993 µA. The tabulated low-level margin is 70 mV. Source test-point interpretation and board leakage remain gates
- **R530/R43/R529:** preserve 100 kΩ and R530's stated 1% initial grade. Conditional known-load screens remain favorable, but reset timing, C45/carrier leakage, the discrete Schmitt threshold test points and arbitrary supply ramps remain open. The ±10% stress band is not an exact delay-tolerance specification
- **R61/R62:** Micron's ±4 µA ODT_CA leakage through 11 kΩ gives 44 mV drop. Under the same-local-VDD2 assumption, the margin to 0.75 VDD2 is 231.204 mV. These are input pulls, not approval of termination configuration
- **R203:** published PG VOL=0.4 V equals downstream EN VIL=0.4 V, so the guaranteed low-noise margin is zero. CRCW candidacy does not close this functional gap
- **R216–R219:** regulator-side input leakage is bounded, but PMU-pad applicability, both directions of low-level drive and rise-time/capacitance remain unresolved. TI's 2 mA absolute maximum is not an output-drive guarantee
- **R571/R572:** keep physical candidacy separate from a guaranteed idle low. The inherited generic 10 µA host-strobe model would make 100 kΩ fail; dedicated pin limits and internal-pull state remain unverified
- **Boot/PMU pulls and oscillator feedback:** preserve values and DNPs; boot sampling, pin-specific leakage, internal pulls, firmware ownership and oscillator behavior remain separate gates

The JSON preserves the inherited source limits and caveats with their evidence paths. Not every device PDF was re-fetched in this pass. Fresh checks covered the CRCW source, Micron eMMC identity/resistance windows, local Micron LPDDR4 ODT_CA tables, and TI VSET selection. The old LVC32/R33 and unadopted 43 kΩ DAT results are not used to select any current value.

Vishay's separate endurance, solder-heat and environmental tests do not compose into an arbitrary guaranteed mission lifetime. Film temperature, duration, humidity and mounting shift need an application acceptance plan before any part is qualified.

## Reproduction and verification

Run `python build_screen.py --project /path/to/immutable-r3/project`. Outputs are `bias-resistor-screen.json` and `verification.json`; the script only reads the project. The JSON records all 62 resistor roles, values, population states, nets, dispositions, candidate codes and per-ref DC screens, together with input hashes and source links. The final immutable-project comparison covers 995 files. No source PDFs or screenshots are included in this deliverable.
