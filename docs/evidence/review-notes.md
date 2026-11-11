# Review corrections — candidate 0.5.6-review.1

Prepared 11 November 2026 against main revision
98d1993411c3650718ad6e1567d37ef162bfa3be. This candidate is separate from the
unreconciled v0.5.7 research queue. It is not a claim that all relationships or
historical inspections have been audited. Publication approval remains separate.

## Relationship and title decisions

| Identifier | Candidate change | Reason |
| --- | --- | --- |
| REL-025 | Retain qualifies; replace generic rationale. | Hint-driven answer changes can be missing from reasoning traces; this bounds trace-based inference. |
| REL-029 | Retain qualifies; replace generic rationale. | Audit success depended on evidence access and methods; unequal teams and constructed training limit generalization. |
| REL-061, REL-065 | Remove edges to EVID-005. | Shared incident context does not establish that coordination or tool-output spoofing qualified the particular monitor replay. Findings and case context remain. |
| REL-137 | Change illustrates to qualifies. | A misconfigured abort mechanism failed; this is not independent enforcement of a planning/execution separation. |
| REL-344 | Change illustrates to qualifies. | Agent access to approval email undermined the nominal authority boundary in the tested wallet configuration. |
| REL-358 | Remove control-air-gap edge. | A cache-timing information channel alone does not establish a planning/execution authority separation. |
| REL-363 | Retain illustrates; narrow rationale. | Externally enforced network/cloud layers are an architectural illustration, not independently verified effectiveness. |
| EVID-145 | Replace method-only title with the bounded wallet-approval finding. | The observation, experimental conditions and limitations remain intact. |

Removed relationship IDs are retired, not reassigned. The candidate retains 193
active findings, 155 sources, 175 cases, 35 fixed founding terms and both evidence
withdrawals; relationships fall from 434 to 431. Historical publication records
and source inspection dates are preserved; this note records the new editorial
review rather than retroactively changing their meaning.

Source passages revisited by Mike AI for these decisions: [reasoning hints,
abstract and Figure 1](https://assets.anthropic.com/m/71876fabef0f0ed4/original/reasoning_models_paper.pdf);
[auditing game, sections 4–5 and 7](https://arxiv.org/html/2503.10965v2);
[METR investigation, scope and tool-output spoofing](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/);
[Anthropic assessment, early Opus 4.6 incident](https://www.anthropic.com/research/alignment-assessment-cybersecurity-incidents);
[wallet study, section III and Figure 2](https://arxiv.org/html/2610.35835v3);
[OpenAI containment, defense in depth and isolated-task communication](https://openai.com/index/securing-our-frontier-model-training-environment/).
Reading these public accounts does not reproduce their experiments, inspect
private logs or independently authenticate their underlying claims.

## Inspection provenance

The separately versioned source-inspection.json annotation index classifies the
attribution actually recorded for every source. It does not change the four
existing JSON schemas or certify that an inspection occurred. Its dataset hash
binds the annotations to the exact canonical input. Source and evidence CSVs
include the annotations; evidence rows include directly cited sources only.

- Direct reading explicitly attributed to the preparing assistant: 14 sources.
- Relayed original-source inspection reports: 20 sources.
- Direct publisher extract plus relayed full-article inspection: 1 source.
- Abstract and metadata only: 1 source.
- Preparing-assistant inspection route not established: 119 sources.

The last category includes older generic inspection claims and worker-attributed
readings that do not establish whether the preparing assistant also read the
original. These remain unresolved, rather than being promoted to direct access.
The Library filter matches any directly cited source with the selected basis;
it does not assert that every source in a multi-source finding has that basis.
Without JavaScript the source-level labels, scope and dispute limits remain
readable with each finding. Historical dates are not replaced with this review's
classification date. Individual human source review is not newly claimed.

## Private briefing and date qualifications

SRC-123–141 now explicitly disclose that their historical bounded-search notes
refer to an unpublished working briefing. A public query/result log and a reason
for withholding the briefing are not recorded. Those notes cannot serve as an
auditable dispute clearance. The historical search claims are not silently
deleted or upgraded, and a new systematic dispute search is not claimed.

For SRC-136, Mike AI revisited the public [methods and limitations](https://transformer-circuits.pub/2025/attribution-graphs/methods.html),
[planning, reasoning-faithfulness and intervention discussion](https://transformer-circuits.pub/2025/attribution-graphs/biology.html),
and [July attention extension](https://transformer-circuits.pub/2025/attention-qk/index.html).
The extension adds attention-pattern analysis to the programme; it is not
independent corroboration of the March studies. This reading does not recover
or authenticate MM1's historical search log. Other SRC-123–141 original sources
were not freshly reinspected in this bounded pass.

The [SRC-008 public report](https://alignment.openai.com/misalignment-reports/suppressing-misalignment-monitoring-alerts-and-disabling-misalignment-monitoring/)
currently assigns alert suppression to October 3 (Sol), monitoring removal to
October 6 (Astra), and the report update to October 20, 2026. The source version
note records this recheck. First-publication date remains unverified and is now
also explicit in the affected findings' limitations. Case dates retain month
precision; no historical inspection timestamp is rewritten.

SRC-010 and SRC-011 inspection-scope spacing is normalized without changing the
listed locations or claiming additional inspection.

## Remaining scope

Repeated relationship wording elsewhere still needs substantive triage; sentence
uniqueness alone is not an acceptance test. Historical inspection routes still
need individual reconciliation where unspecified. Mandatory GitHub check
enforcement, independent reassessment and the Explore ideas card change remain
separate tasks. No new evidence, founding definition or human-review claim is
introduced by this candidate.
