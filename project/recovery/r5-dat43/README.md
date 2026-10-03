# R5: eight eMMC DAT pullups, conditional43k candidate

R563–R570 change from 47k to 43k CRCW020143K0FKED candidates and receive the existing source-derived CRCW0201 footprint. These are the only eight component-value changes. Their DAT0–7 to VEMMC_IO connections, all 1509 pin/function/type/net bindings and all population attributes remain unchanged. R33 stays 270k; R528 remains DNP and storage inhibited. Coverage is 166 assigned references and 88 gaps out of 254. No ordinary-bias batch, oscillator change, boot-medium change or performance downgrade is included.

## Why change the candidate

The active Micron MTFC16GAPALBH-AAT family specifies DAT pullups between 10k and 50k in Table 13 of Rev. G 10/2018. Fresh source bytes have SHA25652ad8018f63554d3e34f970b1516e488543c6a25bd144bcbf33d666fa2a82d71, retrieved from https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/234/EMMC_5F00_DATASHEET.pdf.

Under the existing conditional ±10% total-resistance acceptance budget, 47k spans 42.3–51.7k and exceeds the upper limit.43k spans 38.7–47.3k, leaving 2.7k upper headroom. The proposed Vishay F/K grade specifies 1% initial tolerance and 100ppm/K; the family supports 43k. Its current manufacturer document20052, revision21-Sep-2022, has SHA256390a5effad7c3b526afb7faba340e29176261bfa4c041a128effc87b941a61ea, https://www.vishay.com/docs/20052/crcw0201e3.pdf. Exact ordering availability is unverified.

The 10% band is an application acceptance requirement covering initial error, operating temperature, assembly, aging and environment. Separate manufacturer tests do not prove an arbitrary combined mission lifetime. This change closes the nominal-value-versus-budget conflict conditionally; it does not qualify lifetime.

## Loading and unresolved guarantees

At 1.95V and the 38.7k lower bound, each pullup draws at most 50.39µA with a LOW node and dissipates 98.26µW; all eight LOW sum 403.10µA. Relative to 47k at the same negative 10% corner, additional sink demand is 4.288µA per line. These arithmetic screens assume the stated valid 1.8V-class VCCQ domain. They do not authorize 3.3V signaling or resolve pre-ROM/OTP policy.

No receiver-high guarantee is inferred without complete leakage/internal-pull/ground-error limits. No drive-strength, edge-rate, stub/load, HS200 timing, off-channel feedthrough or partial-power result follows from the small DC current. Keep pullups on the eMMC side of isolation and preserve the cold-only selector policy. Full routing, interface validation, real startup/high-temperature tests, exact component sourcing and memory lifecycle remain release gates.

## Evidence and use

Fresh KiCad 9.0.2 ERC reports 0 findings. The native netlist comparison permits exactly the eight declared Value and Footprint fields; all other component properties and the complete electrical graph must match R4. Negative controls reject a retained 47k, unrelated R33 change, populated R528,wrong 3V3pullup rail,missingfootprint and invalid resistance budgets. The edited eMMC sheet was exported and visually checked; the eight labels and nets remain readable.

Use cad/recovery-physical-candidate/master.xml and this revision's validator as the active authority. Historical tools/generate_emmc_support.py and older checklist/component-register reports retain47k for the frozen older branches. The active build_review.py explicitly overrides only these eight refs; the older audit_official_checklist.py hardcodes47k and is not an R5 acceptance checker. No old report is relabeled as newly passing.

Run validate_dat43.py with --project, --baseline pointing to publishedR4/project, and a writable --runtime directory. No complete six-layer 38×38mm PCB or manufacturing release exists in this checkpoint. The 140-contact contract and top-only assembly remain required. Manufacturer PDFs and page images are not redistributed.

The accompanying CORE PG review confirms manufacturer-supported direct cascading, with zero positive guaranteed low-noise budget at the cited limits. It does not demonstrate a functional failure or adopt the supervisor alternative. Its R3 source graph remains unchanged in R5, as scoped applicability checks record; ramp/noise/timing qualification remains open.
