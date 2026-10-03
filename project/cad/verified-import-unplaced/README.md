# Partial core PCB import, unplaced

150 assigned source-reviewed candidate footprints have been imported from the current high-temperature schematic, including the 140-pad core edge. All 566 numbered electrical copper pads match their actual master-netlist nets. Unnumbered mask/paste-only apertures are retained and are not treated as electrical contacts. Schematic UUID paths are stored for continued KiCad editing.

All 149 internal footprints are parked outside the board outline. They are **not placed**, and no internal routing exists. 104 remaining component references still have no imported footprint. In particular, the main BGA land/escape candidates remain separate process studies. Missing footprints are not excluded from the schematic to hide this incompleteness.

The high-temperature project's same-named PCB is a copy of this partial import so the editable project can continue into layout. It is not a physical-fit, full parity or fabrication pass. Existing geometric DRC results for isolated footprints and the mechanical-only edge must not be applied to this board. Its parking arrangement intentionally violates normal finished-board expectations.

The source netlist hash, imported references and missing-reference list are recorded in import-validation.json. The source edge proposal is preserved separately.

## Native full-parity diagnostic on this incomplete import

Fresh HT-DRAFT13 checking reports 58 copper-clearance violations under the unqualified 0.20 mm default, 351 unrouted items, and 104 missing-footprint parity issues. The complete independent import ledger also lists 104 missing references. The extra sixth pin on the corrected U14 Schmitt OR increases the unrouted count by one; it is not a new short or missing logical net. All 566 imported numbered pads retain actual master-netlist bindings.

The older v11 diagnostic had 38 footprints, 341 bound pads, 138 unrouted items and 199 reported missing footprints versus 216 in its complete ledger. That historical report is preserved separately under engineering/process-rule-controls/default-v11-diagnostic.json. It does not describe the current 150-footprint import.

The tightest imported source land gap is0.085mm at U22/U23 (TPS62864 WLCSP), followed by0.15mm at the four TPS6282xA regulators and0.18mm at NVT4858. No rule was relaxed or violation excluded to obtain a pass. The source-reviewed footprint dimensions do not guarantee that the eventual board factory accepts those dimensions. A coherent process-specific rule set and complete layout remain necessary.
