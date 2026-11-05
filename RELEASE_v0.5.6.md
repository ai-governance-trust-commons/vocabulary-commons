# Evidence Library v0.5.6 — final independent review candidate

Prepared for Mike’s final independent review. No merge, deployment, publication or remote write was performed for these corrections. Previous candidate commit 4a8364e is retained in history.

## Final corrections

- EVID-189 is preserved and narrowed to the reported internal AI-tool compromise. REL-435 now qualifies reference environment integrity: the report does not establish manipulation of information used for operational or assurance judgments.
- New EVID-195 records that withdrawal suspension and hot-wallet service shutdown did not automatically revoke on-chain EIP-7702 authority; separate revocation was needed. It reuses SRC-152, CASE-172 and the Binance source family. REL-445 illustrates governability through the practical reach of corrective authority.
- The records are two observations from one issuer account, not independent corroboration. Both remain provisional, Reported observation, and not independently verified.
- No control-air-gap link is asserted: that definition specifically concerns separation between an agent’s planning/recommendation and consequential execution authority, which this report does not establish. No inference of continuing AI activity, agent trajectory persistence or system-level autonomy is made from delegated authority persisting.
- The release manifest generated_at is now refreshed by the existing exporter on each build, rather than retaining the 1 November timestamp.

## Release counts

193 active findings; 155 sources; 175 cases; 438 active relationships; 35 unchanged terms; two unchanged withdrawals.

Manifest generated_at: 2026-11-04T23:30:39.105429+00:00.
Dataset SHA-256: f40b5230fc052016c7bd747d6cf1221fa280b64dc3afd57f9b19078c0f9bc9d2.

## Validation

PASS: 383 automated assertions, including complete JSON-schema validation of the dataset, glossary and all record/source bundles; unique IDs and references; embedded website data; machine/export and manifest checksums; derived views; CSV counts including withdrawal rows; source/case equality with the prepared candidate; and distinct Binance observations sharing their existing provenance.

PASS: all 52 HTML pages have valid local targets and unchanged navigation markup. JavaScript syntax checks passed for the evidence, coverage and research-path scripts. Whitespace checks passed with existing CSV/RIS formatting conventions retained.

PASS: founding Markdown, glossary JSON and four schema files remain byte-identical; all 35 term objects unchanged. EVID-139 and EVID-144 retain their withdrawal notices and empty public tombstone bundles. The four MM1 qualifying mappings are unchanged; REL-283 and REL-366 remain absent from active mapping. Their exact prior wording remains in release-support/previous-release-notes.md and the preserved Git history. All prepared relationships other than REL-435 are unchanged; only REL-445 was added. All prepared findings other than EVID-189 are unchanged; only EVID-195 was added.

BLOCKED: the existing site-tools/validate.py browser suite was invoked but could not launch because /usr/bin/chromium is unavailable. Earlier browser downloads failed; system package installation was also unavailable. Desktop/mobile rendering and interactive browser checks therefore remain outstanding. This is not a fully browser-validated release. The failure log is included.

The existing machine implementation release remains 0.5.5 and contract remains 1.0, preserving schema constants. Dataset and presentation are 0.5.6; all affected machine exports carry the corrected dataset hash. No structural, schema or navigation changes were made.

## Remaining evidence qualifications

The previous candidate’s access/version qualifications and historical holds remain unchanged: Era relies on MM1’s original-source inspection; PoPLi’s arXiv-version equivalence is unverified; withdrawal reinstatement conditions and historical research holds remain open. These final corrections are not a new source audit or independent verification of the underlying incident.

## Package and reproduction

Complete docs/ and site-tools/ paths are preserved, including docs/.nojekyll. The package includes the unchanged founding source, this report, validation results, prior notes, exact correction history, a cumulative patch and a Git recovery bundle. No deletion is required.

In a checkout retaining b4d26d5 and 4a8364e, install site-tools/requirements.txt; run python site-tools/build_machine_access.py, then python site-tools/validate_release.py. Run site-tools/validate.py in an environment with Playwright and Chromium at its configured path. Do not replace the evidence build with the unrelated base-site generator.
