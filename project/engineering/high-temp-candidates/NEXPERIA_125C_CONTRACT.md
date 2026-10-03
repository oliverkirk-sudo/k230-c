# Nexperia 125°C logic replacement contract

2026-09-30. Bounded review of current buffered-reset topology exported in master.xml. Verdict: conditional candidate accepted for a separately reviewed high-temperature variant; no main CAD changes made. This is not approval of arbitrary ramps or a125°C board operating point.

## Exact proposed parts and pins
- U92/U94: 74AUP1G97GXZ, X2SON6/SOT1255-2, body1.0×0.8×0.32mm. Pins1=B,2=GND,3=A,4=Y,5=VCC,6=C. GroundB to implement AND. Keep existing logical assignments,1V8 supply and local bypass.
- U91: 74AUP1G17GX,125, X2SON5/SOT1226-3, body0.8×0.8×0.32mm. Pins1=NC,2=A,3=GND,4=Y,5=VCC. A=RESET_DELAYED_1V8; Y=SOC_RSTN. R530100k remains upstream of this buffer. Alternative74AUP1G17GX4Z is smaller0.6×0.6mm but has DIFFERENT pins1=A,2=GND,3=Y,4=VCC; do not mix the symbols.
- U93: 74AUP1G06GX,125, X2SON5/SOT1226-3, body0.8×0.8×0.32mm. Pins1=NC,2=A,3=GND,4=open-drainY,5=VCC. A=STORAGE_ENABLE_1V8; Y=GLOBAL_DISABLE. Keep10k pullup to3V3.
Exact orderable codes were checked against Nexperia product pages in candidate-manifest.json research. New footprints, stencil rules and assembly capability remain required; these are not TI DRL footprint replacements.

## Manufacturer limits relevant to125°C
All three specify−40…125°C ambient,0.8–3.6V supply and3.6V input tolerance. Input leakage is±0.75µA over the specified voltage range. Ioff atVCC=0 is±0.75µA; additional leakage atVCC0–0.2V is separately±0.75µA. Do not infer deterministic logic from these leakage limits in the unqualified0.2–0.8V interval.

97/17 at125°C: light-load VOH≥VCC−0.11V and VOL≤0.11V at20µA; at1.65V and1.9mA, VOH≥1.17V and VOL≤0.39V. Schmitt VT+ is0.91–1.31V and VT−0.47–0.84V at1.65V. TI85°C comparison was0.10V light-load loss,1.30/0.35V loaded levels,VT+maximum1.29V and input leakage0.5µA. Thus the existing margins must be recalculated, not copied.

06 at125°C: forVCC0.9–1.95V, VIH=0.70VCC and VIL=0.30VCC, rather than0.65/0.35. At1.65V,1.9mA its VOL limit is0.39V. Powered high-impedance output leakage IOZ is explicitly±0.75µA with inputlow and output0–3.6V. Its ordinary CMOS input requires transition time≤200ns/V; drive it from the Schmitt gate output, never directly from the raw RC/PG node.

The threshold tables use discrete supply test points. Quoted1.65V Schmitt/loaded-output margins are checks at that published point; do not invent guaranteed linear interpolation across the actual1.778–1.822V rail. Full-range interpretation remains a signoff item.

## Recalculated circuit budgets
Assume previously declared valid rails1V8=1.778441…1.821641V and3V3=3.276760…3.359428V, pullup resistance±1%, applicable device supply/temperature conditions, and no additional board leakage.
- RAW PG: three regulator outputs0.1µA each + U89RESET0.3µA + two97 inputs0.75µA each =2.1µA. R52710k causes≤21.21mV high loss. U89 sink current remains below0.4mA. PG VOL0.4V versus tabulated Schmitt minimum0.47V leaves70mV.
- R530 delayed-reset node:0.3+0.75=1.05µA; high loss≤106.05mV; high≥1.672391V. Against tabulated VT+maximum1.31V, margin362mV. U90 low≤0.4V has70mV tabulated margin. Slow intermediate rise is handled by the Schmitt input.
- U91 final reset: with provisional generic K23010µA leakage, high margin above0.65VDD is≥512mV using the20µA VOH limit. If its default PU were as strong as19k, low load including10µA leakage is≤105.9µA;0.39V low leaves232mV against0.35*VDDminimum. Numeric dedicated-RSTN applicability remains conditional.
- U94 MR drive: MR pullup helps high state; low current from its70k minimum is≤26.1µA. Loaded0.39V is below MR VIL0.3*VDDminimum=0.5335V. There is no external weak pullup on this output.
- U92→U93: light-load levels leave≥423mV high/low margin versus the06's0.70/0.30VCC limits. Verify loaded edge speed against200ns/V during physical validation.
- GLOBAL_DISABLE: output sink demand remains<0.35mA, including2µA per TMUX control input and5µA LVC1G32 input allowance. Using conservative0.39V loaded VOL leaves60mV against TMUX VIL0.45V; this is the narrow normal-state logic margin. Released-high leakage including06IOZ totals9.75µA, causing≤98.5mV loss at10k/1%; high remains≥3.178V.
- R529100k DNP qualification pulldown:0.75µA can raise the input≤75.75mV, comfortably low at valid supply. Default storage inhibition remains intact.

## Limits and additional thermal gates
No strict brownout or maximum assertion-time claim: TPS3808 MR assertion150ns remains typical-only; buffer replacement does not change that. At very low supply the SoC internal pullup can exceed the buffer's small specified drive. Ioff is not a reset-state guarantee.
NVT4858HKZ/UKZ are specified−40…85°C AMBIENT, not125°C. Any TF translator variant using them retains that endpoint and needs local-air margin assessment. This differs from the Samsung DRAM85°C CASE constraint.
Y2 X322524MOB4SI remains−40…85°C per manufacturer RevB0. Its±10ppm initial,±20ppm thermal and±3ppm/year aging terms must not be reported as total≤20ppm. A higher-temperature clock candidate/total-frequency-budget review remains open.
Regulators'125°C JUNCTION rating still needs actual self-heating calculations. This logic substitution alone does not qualify the enclosure.

## Sources
Nexperia97 Rev14, static tablespp6–8 and transferp11: https://assets.nexperia.com/documents/data-sheet/74AUP1G97.pdf
Nexperia17 Rev14, staticpp5–7 and transferpp10–11: https://assets.nexperia.com/documents/data-sheet/74AUP1G17.pdf
Nexperia06 Rev12, electricalpp5–7: https://assets.nexperia.com/documents/data-sheet/74AUP1G06.pdf
TI TPS3808, TPS62827, TMUX1574 RevC and SN74LVC1G32 manufacturer PDFs already in project references. NXP NVT4858 Rev2.4 ordering/operating tables; YXC X322524MOB4SI RevB0 manufacturer PDF inspected locally. No original PDF bodies included here.
