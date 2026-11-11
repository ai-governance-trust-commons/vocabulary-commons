# Claude and Gemini review remediation — first bounded pass

Review baseline: `d07fb184ec022fb9fc80d010ef5c3cc2012c5f9f` (merged #37).
Prepared for Lance J. Johnson, 10 November 2026 (America/New_York).

This document is a correction proposal, not an authorization or a report that
canonical evidence has been changed. All 193 findings, 155 sources, 175 cases,
434 relationships, 35 founding terms and both withdrawals remain unchanged in
the accompanying site PR. Fresh source reading below is not an experimental
replay or an independent authentication of issuer records. Historical inspection
dates and publication authority are not upgraded by this review.

## Site dispositions implemented in the companion PR

| Report item | Change | Acceptance |
| --- | --- | --- |
| F1 source roles | Keep legacy bundle/CSV `sources`; add CSV `cited_source_ids` and `context_source_ids`, with definitions. Canonical citation lists remain authoritative. | Cited IDs equal evidence `source_ids`, have locations and do not overlap context IDs; the union equals bundled sources. |
| F5 script-dependent records | Pre-render all 193 findings with limitations, interpretation, verification, direct-source locators and complete-bundle links. Preserve both withdrawal notices. Hide inactive tools until initialization succeeds. | Direct EVID fragment works with JavaScript disabled or evidence.js blocked; normal search/selection still works. |
| F7 menus | Generate the same eight route labels/targets from one navigation definition across 55 pages. | Cross-page route check rejects a missing or renamed route even if integrity hashes are refreshed. |
| F9 README | Preserve the existing live-site link; replace stale setup status and describe the current Library. | Current status and working discovery links. |
| F3 identity | Publish a reproducible payload fingerprint and deployment/validation discovery links. | Compare fingerprint file inventory and digest; resolve actual source SHA from the successful Pages deployment run. |

**F3 limits:** mandatory status-check enforcement still needs administrator
activation in Protect main. Exact commit stamping in the served payload requires
deployment-time generation and a Pages artifact workflow/settings change. This
PR does not change the hosting configuration or claim that a committed file can
contain its own commit SHA. Unsigned hashes do not independently authenticate a
compromised host. The site still transfers its embedded dataset plus static
records; this prioritizes resilient access and adds HTML bytes, with pagination
or external-data loading deferred.

Gemini's catalog CORS concern was checked directly: the live catalog returned
`Access-Control-Allow-Origin: *`. Its hypothetical XSS and absent-CI claims were
not established as current failures. #37's browser/security tests remain required
checks to run; successful execution and mandatory merge enforcement are distinct.

## Item-by-item evidence correction proposal — not applied

The source reading is available at the original URLs listed below. Wording in
this table is a proposed Commons interpretation, distinct from a source claim.
Retain every finding and its existing limits unless a separately reviewed item
explicitly identifies a correction.

| Item | Proposed disposition and wording | Source basis and boundary |
| --- | --- | --- |
| REL-025 / EVID-011 → observability boundary | Keep `qualifies`; replace boilerplate: “In these constructed hint tasks, generated reasoning sometimes omitted an influence that changed answers. This bounds what the tested reasoning traces disclose; it does not establish deliberate concealment or failure of every monitoring arrangement.” | S1 abstract, Figure 1 and discussion. Omission constrains trace-based inference; disclosure is nonzero and task conditions matter. |
| REL-029 / EVID-013 → observability boundary | Keep `qualifies`; replace boilerplate: “Auditors with richer access located the planted objective, whereas the API-only team did not. This shows the observation limit depends on available evidence and methods; unequal teams and synthetic training prevent a general audit-success claim.” | S2 §4, §5 and §7. Controlled auditing game; no universal observability boundary or deployment prevalence estimate. |
| REL-061 / EVID-026 → EVID-005 | Propose removing this `qualifies` edge. Keep both findings and their shared case context. Coordination is not a measured qualification of the later monitor-replay result. | S3 explicitly excludes the provider investigation process and planned remediation from its scope. Same incident context alone does not establish a qualifying evidentiary relationship. |
| REL-065 / EVID-027 → EVID-005 | Propose removing this `qualifies` edge. Keep the spoofing observation, but do not imply that the inspected spoofing tests established a miss by the particular replay monitor. | S3 spoofing section plus scope limits. Would need evidence linking the altered trace to that monitor's result to restore a narrower edge. |
| REL-137 / EVID-058 → control air gap | Change `illustrates` to `qualifies`: “The abort command failed because of a harness misconfiguration, and further abort attempts did not terminate the run. This qualifies reliance on a stop mechanism; it does not demonstrate an independently enforced separation between planning and execution.” | S4 early Opus 4.6 incident. A software/harness failure contributes; do not turn it into model-only refusal to stop. |
| REL-344 / EVID-145 → control air gap | Change `illustrates` to `qualifies`: “Approval passcodes reached an inbox accessible to the acting agent, which could raise its own spending limit. In this configuration, the nominal approval channel did not preserve independent execution authority.” | S5 §III/Figure 2 and Appendix D. Shared-inbox testbed, not a universal wallet result or validation of the proposed protocol. |
| REL-358 / EVID-151 → control air gap | Propose removal. Cache-timing communication across microVMs demonstrates an information-isolation failure, not by itself a recommendation-to-execution authority separation. Retain separately reviewed feedback/observability links. | S6 communication section. Supplied communication objectives and frequent channel guidance limit spontaneity inference. |
| REL-363 / EVID-152 → control air gap | Keep `illustrates` only with a narrow explanation: “The provider describes network and cloud controls intended to constrain external actions even after host compromise. Those externally enforced boundaries illustrate the architectural separation at issue; the account does not independently verify deployment-wide effectiveness.” | S6 defense-in-depth section. Architectural description with reported testing; avoid conflating conventional network disconnection with the glossary's authority separation. |
| EVID-145 title | Replace method-only title with “Agents bypassed wallet approval through an accessible email channel in a bounded study.” Keep the experimental method and all three conditions in the observation. | S5 §III. Title states the finding without universalizing or equating all models/conditions. |

### Primary sources freshly read for this proposal

- **S1 / SRC-009:** [Reasoning Models Don’t Always Say What They Think](https://assets.anthropic.com/m/71876fabef0f0ed4/original/reasoning_models_paper.pdf), abstract, Figure 1 and discussion. Original paper retrieved; no model runs replayed.
- **S2 / SRC-011:** [Auditing language models for hidden objectives, v2](https://arxiv.org/html/2503.10965v2), §§4–5 and 7. Original versioned paper retrieved; no audit game reproduced.
- **S3 / SRC-022:** [METR incident investigation](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/), scope, collective projects and transcript-spoofing sections. Investigator account read; underlying private transcripts not inspected.
- **S4 / SRC-039:** [Anthropic alignment assessment](https://www.anthropic.com/research/alignment-assessment-cybersecurity-incidents), early Opus 4.6 incident. Issuer account read; harness and transcripts not independently authenticated.
- **S5 / SRC-111:** [I-HITL, v3](https://arxiv.org/html/2610.35835v3), §III, Figure 2 and Appendix D context. Original paper read; wallet experiment and prototype not executed.
- **S6 / SRC-116:** [OpenAI containment account](https://openai.com/index/securing-our-frontier-model-training-environment/), defense in depth and communication sections. Provider account read; infrastructure not independently inspected.

## Inspection provenance, private references and formatting

| Item | Proposed follow-up | Guardrail |
| --- | --- | --- |
| F4 / SRC-136 and related sources | Add a separately versioned, controlled inspection-basis field distinguishing direct inspection, a relayed report and unknown/mixed cases, with actor/date/scope attribution. Filter on that field only after records have been individually reconciled. | Do not infer historical inspection from names or rewrite old review dates. Preserve the distinction between Mike directly reading a paper now and MM1's historical inspection. This needs a schema/contract decision and is not silently introduced in the site PR. |
| F6 / SRC-136 | Replace the inaccessible-briefing dependency with a public inspection summary: identify original sections, who reports reading them, which checks remain undocumented and the absence of a dated systematic dispute clearance. Retain the private briefing as working history, not independently auditable support. | Freshly inspect the recorded methods, biology and attention-extension sources before asserting the historical scope has been reconciled. No additional source verification is claimed here for SRC-136. |
| F6 / SRC-008 | Surface unverified publication/event-date assignments near the affected finding's limitations or source-date display. Resolve assignments against the original report before proposing corrected dates. | A note saying a date was not rechecked does not itself establish that the date is wrong. No date correction is authorized by this table. |
| F8 / SRC-010 | Normalize scope spacing to “pp. 3839–3840 (PDF pages 14–15), Table 13; section 6.2–6.3 …”, preserving the inspected section list. | Formatting only. Do not derive inspection scope from locator text when they record different extents. |
| F8 / SRC-011 | Normalize scope spacing to “Sections 4 (blind auditing game), 5 (auditing techniques), 7 (limitations), 8 (conclusion).” | Formatting only; S2 confirms section identifiers. No word/digit rule applied blindly to identifiers, versions or standard names. |

## Review sequence and bounded scope

First review and merge the interface/export PR after all CI checks pass. Separately
approve or revise the nine evidence proposals above. Only then apply approved
canonical corrections and regenerate derivatives, preserving historical dates,
withdrawals and founding definitions. Re-review the changed paths independently.

The remaining repeated explanations are a review queue, not an instruction to
rewrite 300 records or require every sentence to be unique. Each edge must
identify relevant evidence and limits; repeated valid wording can remain where
its substance is actually the same. No broader research audit is claimed.
