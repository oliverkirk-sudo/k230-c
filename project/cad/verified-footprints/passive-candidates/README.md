# TNPW0402 source-land candidates

The current TNPW e3 datasheet (Vishay document 28758) delegates recommended solder pads to document 28950. Its 12-Jul-2022 page 1, visually checked, offers two different reflow patterns:

- IPC-7351-based: pad 0.55 × 0.60 mm, inner gap 0.40 mm, total copper span 1.50 mm
- IEC 61188-6-2-based: pad 0.35 × 0.55 mm, inner gap 0.55 mm, total copper span 1.25 mm

The drawings define these as alternatives, not manufacturing tolerances around one pattern. They supersede reliance on an older 1.30 mm span for this current source review. The larger IPC-based pattern is assigned to19 precision-resistor positions in HT-DRAFT11 as a conditional placement candidate; the IEC-based pattern remains unassigned. the denser IEC-based option requires the intended assembly process to accept it.

Copper geometry is source-backed. The 0.05 mm mask expansion, 1:1 paste and 0.25 mm separation beyond mask are explicit unqualified process choices. No power, thermal/lifetime or sourcing claim follows from this land-pattern check. Eight feedback resistors would consume 1.92 mm² more in the larger pattern than the previous 1.9 × 1.2 mm rectangular planning allowance. That small correction does not resolve the much larger capacitor and BGA escape uncertainties.

Sources: https://www.vishay.com/docs/28758/tnpw_e3.pdf and https://www.vishay.com/doc?28950
