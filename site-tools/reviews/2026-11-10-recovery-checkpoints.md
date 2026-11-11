# Project 1 recovery checkpoints

No merge or deployment is authorized. Lance must approve both separately from testing.

## Stage 0 — recovered saved state

Recovered 10 November 2026 (America/New_York). Candidate: 549e1bd; main: 98d1993411c3650718ad6e1567d37ef162bfa3be. GitHub comparison confirmed one commit ahead, zero behind. No PR or branch workflow run existed at recovery.

Inspected canonical change notes, provenance contract, validation entry points and read-only PR workflow. Saved scope: eight relationship decisions and EVID-145 title; source-inspection attribution, private-briefing/date qualifications, regenerated projections. Three edges retired: REL-061, REL-065, REL-358. Expected 193 findings, 155 sources, 175 cases, 431 relationships, 35 founding terms, two withdrawals.

The prior thread reported 1,696 checks passed and local Chromium socket restriction. No retained execution log was found in the candidate worktree, so this is historical reported status, not fresh verification. Recovery testing will record each stage and exit status. Browser testing remains pending. Draft PR CI is the planned fallback; workflow has read-only permissions and no deploy step.

## Stage 1 — release integrity passed

Fresh execution: `/tmp/commons-check-env/bin/python site-tools/validate_release.py`, candidate 549e1bd, exit 0. Confirms founding definitions, schemas, withdrawals, references, exports, source annotations, static fallbacks and publication hashes. Initial attempt with the default Python stopped for missing markdown_it; reran with the recovered reviewed test environment.

Historical logs subsequently recovered from `/tmp/commons-review-*.log`: release, supported build, projection, security and remediation pass logs; browser launch log records a failure, not a pass. Those logs support prior reported status but fresh runs remain authoritative.
