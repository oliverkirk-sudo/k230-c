# CM-K230 local decoupling basis review

Audit date: 2026-09-30 UTC. Scope: the 77 entries in `engineering/decoupling-allocation.csv`, their connectivity in `cad/high-temp-candidate/master.xml`, and the actual reference circuits. This is a source/connectivity audit, not PDN, component, thermal, assembly, or 38 x 38 mm top-side fit qualification. No CAD, BOM, allocation, or generator was changed. Input hashes are in `source-manifest.json`.

## Finding

The 33 capacitors labelled **NEW per-power-ball baseline** are new design assumptions. Neither examined reference specifies one 100 nF per repeated digital supply ball. The references have different local value mixes and, critically, join CPU/KPU to the common 0.8 V supply. Their counts cannot be copied onto the candidate's independent CPU/KPU regulators without a fresh rail-by-rail PDN and transient design.

The 30 DRAM capacitors and six SoC DDR-IO capacitors reproduce the **01studio LPDDR4** groups exactly by count/value. That establishes provenance, not qualification of the replacement Micron part, placement, or the selected capacitors at temperature. Keep these requirements/groups intact while resolving manufacturer and layout requirements. No removal or substitution is authorized or justified by this review.

All 77 allocated capacitors exist in the audited master and have the stated rail-to-GND connection. The allocation totals 64 x 100 nF, 10 x 4.7 uF, and 3 x 22 uF. It is not the complete board capacitor inventory: regulator capacitors, analog filters, VREF, eMMC and support-IC bypass are elsewhere. In particular, **C233 adds a fifth 100 nF on VDD0P8_DDR_CORE beyond the four in this allocation**.

## 1. Digital-domain source counts

PDF page numbers below are physical PDF pages, starting at 1. Capacitors in the following table are the depicted local banks, excluding regulator output capacitors, PLL/MIPI branches, and 1.1/1.2 V DDR-IO.

| Circuit | Net names exactly as drawn | Local references and values | Meaning |
|---|---|---|---|
| 01studio, p3, U12.1 | VDD_0V8; aliases VDD0V8_CORE, VDD0V8_KPU, VDD0V8_CPU, VDD0V8_DDRCORE | C52-C53: 2 x 4.7 uF; C54-C65: 12 x 100 nF; C68-C73: 6 x 100 nF | **20 capacitors on one shared net**. The four aliases are explicitly joined at the top of p3. No separate CPU or DDR-core capacitor count is drawn |
| Canaan CanMV V1.0, p3, U1.1 | CORE_0V8 | C56: 22 uF; C57: 4.7 uF; C58-C72: 15 x 100 nF | **17 capacitors**. CORE_0V8 feeds VDD0P8_CORE, VDD0P8_CPU and VDD0P8_DDR_CORE balls |
| Canaan CanMV V1.0, p3, U1.1 | KPU_0V8 | C73-C74: 2 x 22 uF; C75: 4.7 uF; C76-C79: 4 x 100 nF | **7 capacitors**. KPU_0V8 feeds the six KPU balls; it is explicitly joined to CORE_0V8 and VDD_0V8 at the top of p3 |

Canaan's combined local 0.8 V population is therefore **24 parts: 3 x 22 uF + 2 x 4.7 uF + 19 x 100 nF**. The CORE_0V8 and KPU_0V8 row labels describe intended load groups but do not create independent electrical rails. The six KPU balls with four 100 nF capacitors are a direct counterexample to an asserted universal one-capacitor-per-ball rule. The source schematic still does not reveal each capacitor's physical loop or establish a suitable minimum for a different layout.

| Current candidate group | Allocation references | Current local population | Source assessment |
|---|---|---|---|
| VDD0P8_CORE | C501-C516 | 2 x 4.7 uF + 14 x 100 nF | New allocation; 14 matches the number of CORE balls, not an explicit reference requirement |
| VDD0P8_CPU | C517-C520 | 1 x 4.7 uF + 3 x 100 nF | New independent-CPU allocation; both sources share CPU with CORE |
| VDD0P8_KPU | C521-C528 | 2 x 4.7 uF + 6 x 100 nF | New independent-KPU allocation; not Canaan's 2 x 22 uF + 1 x 4.7 uF + 4 x 100 nF mix |
| VDD0P8_DDR_CORE | C529-C533 | 1 x 4.7 uF + 4 x 100 nF | New load-side allocation. Candidate connects this rail to CORE through R220, and C233 is an additional local 100 nF |

These counts total 33, versus source totals of 20 and 24. **The numerical difference is not a removable-parts budget.** Likewise, absence of a local 22 uF in a current CPU/KPU row is not proof of insufficient bulk without accounting for the candidate's own output banks and their actual placement.

## 2. DDR and other entries in the 77-part allocation

| Current entries | Actual primary basis | Assessment |
|---|---|---|
| C534-C539, VDD1P1_DDR_IO | 01studio p3 C74 = 4.7 uF and C75-C79 = 5 x 100 nF, all on VDD_1V1 | Exact count/value match to the SoC DDR-IO local bank |
| C540-C551, allocation labelled DRAM VDD2 | 01studio p2 C20 = 22 uF, C21 = 4.7 uF, C22-C31 = 10 x 100 nF, on VDD_1V1 | Exact row reproduction |
| C552-C561, allocation labelled DRAM VDDQ | 01studio p2 C40 = 22 uF, C41 = 4.7 uF, C42-C49 = 8 x 100 nF, on VDD_1V1 | Exact row reproduction |
| C562-C569, DRAM VDD1 | 01studio p2 C32 = 22 uF, C33 = 4.7 uF, C34-C39 = 6 x 100 nF, on VDD_1V8 | Exact row reproduction |
| C570-C575, one 100 nF on each BANK0_VDDIO through BANK5_VDDIO | 01studio p1 has C13-C17 = 5 x 100 nF on common VDD_3V3; banks 0-4 use VDD_3V3, bank 5 uses VDD_1V8. Canaan p1 uses distinct VDDIO_BANK0 through VDDIO_BANK5 aliases, ties banks 0/1/2/3/5 to VDD_1V8 and bank 4 to VDD_3V3, and draws no capacitor beside each bank | Per-bank assignment is a design interpretation, not six explicitly isolated reference banks |
| C576-C577, VDD1P8 | 01studio p3 C117-C119 = 3 x 100 nF on shared VDD_1V8; Canaan p3 C90-C92 = 3 x 100 nF on VDD_1V8, C93-C94 = 2 x 100 nF on VDD_1V8_RTC, which is joined to VDD_1V8 | Two generic-SoC capacitors are a baseline, not an exact isolated source requirement. The source 1.8 V rail also feeds other loads |

The VDD2 and VDDQ allocation labels preserve intended DRAM grouping. Electrically, both 01studio rows are named **VDD_1V1**, and both candidate rows plus the SoC bank are on **VDD1P1_DDR_IO**. Their common net does not establish that one physical bank can replace another. 01studio C50/C51 are marked 100 nF/NC with 1G/2G annotations; they are not silently counted as fitted members of C20-C49. Its C18/C19 are the VREF network, outside those local banks.

**Do not conflate the Canaan DDR circuit with 01studio LPDDR4.** Canaan p5 is headed “DDR - LPDDR3 / LPDDR4”, but U2.1/U2.2 are drawn as LPDDR3 with 1.2 V operation. Its p3 SoC bank is C80 = 22 uF, C81 = 4.7 uF, C82-C86 = 5 x 100 nF on **DDR_1V2**. On p5, C10-C21 and C22-C33 are each 22 uF + 4.7 uF + 10 x 100 nF; both rows are explicitly labelled **DDR_VDDQ**. C36-C43 are 22 uF + 4.7 uF + 6 x 100 nF on **DDR_VDD1_1V8**. Its connection block joins **VDD_1V2**, **VDD2_VDDCA**, **DDR_VDDQ**, and **DDR_1V2**. Preserve these source names; do not relabel the first row or import this LPDDR3 supply/termination recipe into the candidate.

## 3. Official guide and manufacturer constraints

The local `K230_Hardware_Design_Guide.md` requires matching the K230 DDR PHY and each DRAM reference circuit, including decoupling (lines 245 and 284). It also points to EVB capacitor selection and placement (line 771). Its core-power tables give current/regulator recommendations, not a one-capacitor-per-power-ball count. DDR supply/noise requirements appear at lines 654-656, and the same-network requirement for external DDR at line 719. These are requirements to satisfy, not a waiver based on aggregate capacitance.

The guide's linked Figure 3-13 (`image024.png`) shows DDR power pins/nets **DDR_VDDQ_1V1**, **DDR_CORE_0V8**, and **DDR_VAA_1V8** without a capacitor bank. The linked Figure 3-16 (`image027.png`) displays ground/NC units rather than a countable supply-capacitor network. Both were retrieved from the official repository and inspected; neither supports inventing a numerical local-cap minimum. The [official guide](https://github.com/kendryte/k230_docs/blob/main/en/00_hardware/K230_Hardware_Design_Guide.md) and hashed local images remain the traceable sources.

The present DRAM is **MT53E256M32D2FW-046 AAT:B**, not a generic LPDDR4. The manufacturer-authored Micron 200-ball automotive LPDDR4/LPDDR4X Rev. F 10/2020 source is separately hashed. Preserve its applicable supply, ramp, initialization, refresh/temperature, timing and noise requirements. Table 15 (p40) and Table 18 (p43) constrain supply relationships during ramp/power-down; read-timing notes on p258 and write-timing notes on p260 include supply-noise assumptions at the package. Do not replace those conditions by a nominal capacitance sum. No exact external decoupling count for this ordering code was established by this audit; retaining the 01studio groups does not close that manufacturer-application review. Do not transfer LPDDR4X's 0.6 V I/O conditions to this 1.1 V LPDDR4 implementation.

The provisional 85 C enclosed-air screen does not establish capacitor temperature, DRAM case temperature, or device junction temperature. DC bias, tolerance, aging, operating temperature and mounting parasitics must be applied to the actual MPNs. The 22 uF DRAM capacitors and regulator bulk remain generic/unassigned in this audited master; the named 100 nF/4.7 uF candidates are not thereby qualified.

## 4. Output bulk versus local bulk: exact current connectivity

| Current load net | Regulator output capacitors, rail to GND | Local bulk in the 77-part allocation | Electrical result |
|---|---|---|---|
| VDD0P8_CORE | C201, nominal 47 uF | C501-C502, 2 x 4.7 uF | Same exact net |
| VDD0P8_CPU | C206-C208, 3 x 22 uF | C517, 4.7 uF | Same exact net; independent CPU regulator |
| VDD0P8_KPU | C212-C214, 3 x 22 uF | C521-C522, 2 x 4.7 uF | Same exact net; independent KPU regulator |
| VDD1P1_DDR_IO | C218, nominal 47 uF | C534/C541/C553, 3 x 4.7 uF; C540/C552, 2 x 22 uF | Same exact net, shared by SoC DDR IO and DRAM VDD2/VDDQ |
| VDD1P8 | C223, nominal 47 uF | C562, 22 uF; C563, 4.7 uF | Same exact net, with several additional loads |
| VDD0P8_DDR_CORE | No regulator-output bulk directly on this XML net | C529, 4.7 uF; C530-C533 and additional C233, 100 nF | Connected to VDD0P8_CORE through R220, a specified low-resistance 0-ohm link; not the same XML net and not an ideal high-frequency short |

C202/C219/C224 are feed-forward capacitors from the output to feedback, **not** rail-to-GND bulk. Analog load capacitors downstream of FB202-FB209 have different nets; an upstream capacitor cannot be assumed to replace the downstream filter capacitor.

The reference schematics also keep distinct local banks and output banks on shared electrical nets: 01studio p3 has C85-C87 on VDD_0V8, C92-C94 on VDD_1V1 and C106-C108 on VDD_1V8, each 3 x 22 uF/10 V; Canaan p3 has C138-C140, C142-C144 and C150-C152 on VDD_0V8, DDR_1V2 and VDD_1V8 respectively, each 3 x 22 uF. This establishes coexisting roles, not their placement or interchangeability.

### Criteria before any proposed combined role

A capacitor could serve both regulator-output and load-local bulk roles only where the actual geometry and electrical model satisfy both duties. A separate proposal must demonstrate:

1. The same supply and return path, or an explicit model of every intervening link/plane neck/via/bead; independent CPU/KPU outputs must remain independent.
2. The regulator's specified output-filter combination, minimum **effective** capacitance, feedback/sense connection, and control-loop/transient behavior. TI TPS6282xA source: section 8.2.2.3/Table 8-3 (p13), section 8.2.2.5 (p14: 10 uF effective minimum for the applicable A variants), and section 8.4.1 (p22). TPS62864 source: Table 9-3 (p21), section 9.2.1.2.5 (p22: recommended minimum 30 uF effective), and section 11.1 (p28). Minimum capacitance alone is insufficient; extra distributed capacitance also affects the output network.
3. Placement close enough to both regulator output loop and relevant package supply/return balls, with extracted connection/plane inductance and ESR/ESL. The TI layouts require input/output capacitors and inductor close to the IC, proper ground returns, and a quiet sense/feedback connection. Moving an output capacitor to the far side of a BGA merely to rename it “local” is not justified.
4. A frequency-dependent PDN assessment, including anti-resonances, and load-step/ripple/overshoot validation at the package across operating states, DVS and relevant voltage/temperature corners. Set impedance and transient limits from allowed rail noise and credible load steps; capacitance arithmetic cannot establish them.
5. Retention of DDR manufacturer's and K230 reference/application requirements, followed by routed-board validation with the top-only placement/escape constraints actually applied.

**Disposition:** retain the existing population as an unqualified baseline; replace its per-ball rationale with a source-aware PDN requirement before proposing any edits. The audit creates no permission to remove capacitors and makes no PCB-fit claim.

## Evidence files

- `reference-capacitor-inventory.csv`: individual reference designators, exact source nets, values, roles and PDF pages
- `current-allocation-audit.csv`: all 77 allocation-to-master comparisons, current values and footprints
- `current-net-evidence.json`: actual output-capacitor, feed-forward and R220 net pairs
- `source-manifest.json`: source-file and retrieved-guide-figure hashes
- `evidence/`: rendered primary schematic pages, extracted searchable text, and the two guide figures
