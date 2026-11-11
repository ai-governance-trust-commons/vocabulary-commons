# Publication build and validation

The reviewed static HTML, styles and scripts under `docs/` are maintained
presentation sources. The founding Markdown and glossary JSON remain fixed.
`docs/evidence/evidence.json` is the canonical public evidence input. Use this
one supported publication build, with full Git history available:

```sh
python -m pip install -r site-tools/requirements-lock.txt
python site-tools/build_machine_access.py
python site-tools/validate_release.py
python site-tools/test_projection_build.py
python site-tools/test_publication_security.py
python -m playwright install chromium
python site-tools/validate.py --chromium ''
```

The old `build_site.py` entry point is retired and refuses before writing files.
It must not be restored as a shortcut: its older templates overwrite reviewed
presentation. Historical implementation remains in Git history.

The supported build refreshes embedded browser data from canonical JSON,
escapes inline JSON as data rather than HTML, rebuilds machine/coverage/research
projections, preserves reviewed chrome, applies the shared CSP/referrer policy,
and finally regenerates machine and presentation integrity metadata. It does
not change source inspection dates, evidence standing, publication decisions,
founding definitions or the reviewed presentation version. Data changes still
require editorial review; a build is not publication authorization.

All shared HTML, CSS and JavaScript are inventoried in
`release-manifest.json` under `presentation_security`. The validator checks
that inventory, policy declarations, local runtime assets, safe inline JSON,
current data counts, schemas, references, embedded data, exports, hashes and
local links. It rejects inline executable code/styles. The policy page's old
inline stylesheet is now `docs/evidence/policy.css`.

A hash proves byte consistency, not working behavior or source truth. The
browser suite tests glossary filtering/card navigation, Library search/export,
all HTML pages under CSP, guide/discussion routes, persistent navigation,
320px/390px layouts, and navigation with JavaScript disabled or the shared
script blocked. CSP console violations and application exceptions fail tests.
Physical iPad/Safari and assistive-technology review remain separate checks.

## Automated PR gate

`.github/workflows/publication-validation.yml` runs on PRs and pushes to main.
It uses read-only repository permissions, no persisted checkout credential,
commit-pinned official actions and a reviewed Python 3.12 dependency lock.
The stable job/check name is **publication-validation**.

After its first successful PR run, add that exact check to the existing
**Protect main** ruleset as a required status check. Verify the ruleset is active
and accepts the GitHub Actions check source. A workflow file alone does not
make a check required. Do not require a nonexistent second maintainer or change
human-review roles without a separate decision. GitHub settings are outside this
repository change and their activation must be reported separately.

Review applies to a specific PR head. CI runs the committed candidate using
HEAD as its reviewed presentation baseline, then separately rebuilds twice and
rejects unintended drift. When reviewing an uncommitted change against an older
base, use an explicit baseline and any intentionally changed page paths:

```sh
python site-tools/validate_release.py --baseline-ref BASE_COMMIT_SHA \
  --allow-new-page docs/considerations/index.html \
  --allow-navigation-page docs/index.html
```

Repeat `--allow-navigation-page` for each intentionally changed HTML page. These
allowances do not permit removed pages, other added pages or navigation changes
on unlisted pages. Defaults remain strict. Founding glossary/schema/withdrawal
guards retain their historical baseline independently of these presentation
allowances. Historical v0.5.6 assertions remain in `validate_v056_candidate.py`.

Browser tests use an HTTP loopback server so relative URLs, deferred scripts and
CSP behave normally. Screenshots are temporary unless `--screenshots DIRECTORY`
is supplied. `--chromium ''` selects Playwright's matching installed browser;
`--chromium /path/to/chromium` overrides it. A launch restriction blocks the
browser check; it does not count as a pass. CI installs matching Chromium and
its system dependencies on its ephemeral runner.

## Browser policy boundaries

The meta CSP permits only local scripts, styles, images, fonts and connections,
blocks objects/frames and base-URL changes, and limits form actions to this
origin. Ordinary outbound reference/participation links and Blob CSV downloads
remain usable. All pages declare `no-referrer` consistently.

GitHub Pages response headers are outside this static implementation. This
change does not claim X-Frame-Options, X-Content-Type-Options or HTTP
frame-ancestors enforcement; frame-ancestors cannot be supplied by a meta tag.
Do not add unsupported header configuration files or weaken CSP to hide a
failed test. Any future external embed/runtime service needs explicit policy
review. CSP supplements safe encoding; it does not replace it.
