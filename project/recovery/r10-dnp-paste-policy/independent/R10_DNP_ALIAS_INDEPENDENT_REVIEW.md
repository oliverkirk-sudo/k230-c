# R10 recovered-fixture alias review

**PASS — bounded independent review. No blocking findings.**

The normalized board exactly matches the original board text with only ten footprint FPID strings replaced. For each reference, the copied `Audit_Footprints` footprint file is byte-identical to its authoritative library file and matches the recorded SHA-256. This is explicit metadata normalization; the strict helper retains its exact FPID check.

Native population, pad-number and master-net parity passed on both normalized source and derived boards. Exactly two paste-only apertures are removed, both on R528. All other native board tokens remain unchanged. The original board hash is unchanged, and both review boards carry byte-identical copies of the original project settings.

The recorded F.Cu and F.Mask flash counts remain 18→18. F.Paste is 14→12; B.Paste remains empty. F.Cu, B.Cu, F.Mask, B.Mask, F.Fab and Edge.Cuts Gerber content matches after excluding the documented file-identity/timestamp/checksum metadata.

This covers the recovered ten-reference R7 fixture; 244 master references remain absent. Source-library file equality establishes alias equivalence, not an independent embedded-footprint geometry qualification. The exact board-text comparison confirms that normalization leaves embedded geometry unchanged. This review did not add drill or placement export tests and does not establish routing completion, DRC closure, circuit function or stencil/process qualification.

The review was read-only. No main CAD or source library was edited and no vendor was contacted. The companion [JSON evidence record](R10_DNP_ALIAS_INDEPENDENT_REVIEW.json) pins the inspected script, results, original/normalized/derived boards, master, population contract and strict helper. Its paths are relative to the R10 reconstruction checkpoint root.

## Required evidence hashes

- test_script: `270a20a45318a9b6335c3fdb78f68fc5d34bea980bbc7066ab5768e736a9d72c`
- results: `e6fe53be3c60937f01384d5cc3ccd2fdad3c269039b21bb049859338e1158355`
- original_source_board: `d7df5364ef2993fd5553162327767480a3aae625ffdfa658a47c0704f75bb1bd`
