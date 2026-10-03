# Separate conditional process model

This duplicates the current partial/unplaced import for an explicit rule experiment. It is not the production board or an accepted manufacturing recipe. The original 0.20mm-default diagnostic remains in ../high-temp-candidate/partial-pcb-drc-parity.json.

General copper clearance and minimum track width are 0.1016mm. Exactly30 enumerated pad pairs,15 each in U22 and U23, have a0.0762mm conditional pad-to-pad clearance based on source YCG geometry and published advanced process capability. No pad-to-track or arbitrary adjacent copper receives that allowance. The source lands have0.085mm nominal separation, only8.8µm above the proposed local minimum; etch tolerance, mask registration, stencil, assembly and the combined stack/castellation process require acceptance.

The model reports0 geometry violations while retaining138 unrouted items and199 reported missing-footprint issues. The complete source import ledger contains216 missing references. No severity or exclusion was changed. Positive controls confirm both a deliberately intruding listed pad pair and a foreign nearby track are still rejected by their intended rules.

Published advanced fine-line conditions do not automatically apply to the proposed1oz stack or guarantee manufacturing tolerance. Use process-model-manifest.json for exact assumptions and ../engineering references from the project root for the source evidence. Do not treat this as a finished-board DRC pass.
