# High-Signal Report Archive

Separate research-report collection at `docs/reports/`, linked from the Library.
Reports reflect assessments at the time; they are not validated evidence findings.
This does not upgrade the Evidence Library's own provisional standing.

## Preservation and publication

The existing High-Signal AI Incident Watch retains its research threshold and schedule.
Its capture instruction saves each issued report immediately in the private
`Governance and Trust Project/High-Signal Watch Archive` folder, before delivery.
Use a dated JSON envelope: date (America/New_York), title, description,
preservation (capture time, run ID when available, format/provenance), markdown
(complete report with durable source URLs and all qualifications).
A successful save receipt is required; a chat response alone is not preservation.
Capture failures must be disclosed in the report, not silently treated as saved.
No-report runs need no public archive entry. Retried runs must reuse identical saved
content or retain a separately dated correction, never silently replace originals.

Public promotion is separate: retrieve a saved envelope, then run
`python site-tools/import_report.py /path/to/capture.json` on a review branch.
Review source URLs, report/event dates, privacy, qualifications and duplicate status.
Add related published EVID IDs with an explicit comparison note in `index.json`.
Do not link unpublished candidates or imply comparisons corroborate the report.
Run the supported build, report tests, full validation and browser CI; obtain
approval before merge/deploy. No automatic public publication is configured.

Append corrections to the report's `corrections` array in `index.json`, with an ISO
date and note. Do not edit preserved report Markdown or recompute its hash to hide
changes. A date may be the archival recording date when the original correction
date is unknown; say so. Git history and the original hash preserve the prior text.

## Initial source audit

November 10–13: the private reading copy (SHA-256
cb5f281483b0534f2f3fed76b629e0a34a0746b96de0b0dad1884410aa516453)
was split by its four dated headings. These are reconstructions, not verbatim originals.
The Australia correction was already in that copy and is surfaced above the report.
November 14: complete, untruncated recorded result of run
299dc139-5ff8-8329-a0fa-bb4dcaf44bc0, completed 2026-11-14T13:09:07.856850Z.
Chat display tags and ephemeral citation IDs were converted to portable Markdown
and the explicit WorkOS source URL. Claims were not reverified in this archival pass.
Earlier index: selected October 3–November 9 summaries, not full reports. The
private ChatGPT conversation pointer is described rather than made a public link.
