# Independent direct-via DDR candidate audit

This directory is separate from every router and main CAD artifact. Inputs are read-only.

## Run

From this directory:

```sh
python audit_joint_links.py ../link-pair-preserved-flex/best-search-candidate.json
PYTHONDONTWRITEBYTECODE=1 python -m unittest -v test_audit_joint_links.py
```

The CLI accepts another candidate path, `--baseline` and `--output-dir`. It writes JSON and CSV reports under `results/<candidate-directory>/` by default. Exit 2 means the audited candidate was rejected; it is not a crashed computation. Exit 0 means the source/structure and nominal analytic geometry gates passed, **not** that production/native/SI/timing gates passed. `accepted_DDR_links` remains zero until a separate native audit and release process qualifies the route.

## Verified scope

- Exact 65 source net/SoC-ball/DRAM-ball joins and package-length identities
- Both real L1 ball-to-via dogbones, actual via identifiers and functional layers
- Direct via-to-via path endpoints, one common routing layer per path and two actual transitions
- All six differential pairs on common layers with equal two-via/two-transition topology
- All 590 physical lands and 502 physical vias retained
- Only the 65 former DDR via-to-exit tracks removed; all 646 other source routes retained
- Independent nominal pad, via, drill and track clearances using the original analytic audit function, without search occupancy masks
- Original Figure 054 2H/3H and separate edge/center 3W screens, with explicit unqualified stackup assumptions

The frozen 146-event candidate has 65 candidate paths, 23 analytic geometric failures across 12 net pairs/19 nets and zero accepted links. The 7,806,969 geometric checks find only trace-to-trace failures. All six differential pairs retain their topology but planar skew is 5.85–7.6375 mm. The 120 Figure 054, 116 edge-3W and 55 center-3W misses are screening failures rather than a timing analysis.

## Source reconciliation

The candidate's frozen source hashes are never rewritten. Its original pin-assignment CSV was recovered from the existing local review ZIP and verified byte-identical by SHA256 before being copied into `frozen-reference/`. Current U1/U2/U3 function/net assignments are compared independently against both current CSV and current XML (390/200/153 pins). All 743 currently match. Whole CSV/XML hashes changed; the pin-map changes are confined to U14. The audit reports those changes separately. Footprint/component-value changes outside the DDR geometry are not qualified by this comparison. All other route-input hashes, including the DDR route contract, must remain identical.

## Unresolved qualification

Candidate paths are not electrically accepted connections when geometry conflicts exist. Native CAD audit has not run here. Common byte-layer allocation is an explicitly relaxed engineering target; mixed L3/L8 delay matching remains unresolved. Pair coupling, impedance, reference planes, continuous return paths, SI/PI, package-delay matching, training, fabrication tolerances, full-board routing, local bias/PDN completion, top-only assembly and enclosed 75–85 °C thermal operation are not qualified. The three local RAM bias balls remain unrouted. No production release claim is made.
