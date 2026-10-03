# PMU automatic-start conditional circuit

The integrated draft now straps K230 C12/PAD68/INT4 to its own AVDD1P8_PMU domain through R401=0Ω. Unlike an assumed10k pull-up, a direct same-domain input strap does not depend on an undocumented internal pulldown resistance to achieve a valid high. C10/PAD64/INT0 is held inactive by R402=10k toground. B11/PAD70 and C11/PAD71 are outputs brought to observation points TP81/TP82; they do NOT drive the rail enables or external RSTN in this iteration.

This is supported by TRM cold-start semantics: PAD68 high-level detection is enabled at reset. PMU_INT_DETECT_EN reset0x810 enablesINT4; PMU_INT_DETECT_TYP reset0 selects effective-high, level-trigger behavior. The official pinout assigns PAD68 to AVDD1P8_LDO, which this design has already combined with RTC in the same filtered AVDD1P8_PMU net.

The permanent-high strap is an intentional internal function allocation, not a connection to an exposed140-pin GPIO. Firmware MUST leave PAD68 as PMU input, never drive it low or repurpose it as output. Verify the input current/pad limits and actual local supply ramp at bring-up. R401 can be depopulated for isolated debug. No firmware patch is yet claimed implemented.

## Firmware and reset obligations

- Observe PMU startup state before accessing GPIO65/66/67/69 for the two private DVFS buses
- Configure the required PMU/Normal ISO control. Normal-to-PMU isolation removal is tied to the PMU startup lifecycle, not merely the presence of voltage
- Mask/acknowledge sustainedINT4 activity after startup as appropriate; an always-high source cannot be treated as an ordinary momentary button. Sleep/wake/shutdown behavior must be explicitly adapted and tested
- Preserve PAD64/68/70/71 ownership. Existing notes on disabling conflictingPAD65/66/67/69 shutdown wake routes still apply
- Do not connect PAD71 into a reset feedback loop until external RSTN/PMU reset-domain coupling is established
- CPU may have its own external-reset/rail boot path; this circuit establishes PMU startup intent, not proof of complete BootROM or DDR initialization

TRM cold-reset flow includes about1second PMU oscillator stabilization. The roughly50ms POR and60ms isolation timings both referencePAD70 and are not a documented fixed110ms delay. The circuit therefore does not fabricate a fixed reset delay from those numbers.

## Evidence

Official K230 TRM v0.3.1 §14.3 (PDFp1169) and cold-reset flow (PDFp1183); PMU register reset tables. Exact source URLs/hashes and workbook rows are preserved in ../erc-triage-v5-source-evidence.json. Official K230_PINOUT_V1.2_20240822.xlsx main pin sheet row62 supplies C12/INT4 domain and input type. Canaan guide PMU section: https://github.com/kendryte/k230_docs/blob/main/en/00_hardware/K230_Hardware_Design_Guide.md

The previously open analog test output D8 is intentionally unused per the official pinout/reference schematic. Its symbol remains a functional output with an explicit unused marker, not a fictitious unbonded NC pad.
