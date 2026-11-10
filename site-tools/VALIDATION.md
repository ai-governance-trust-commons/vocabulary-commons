# Evidence build and validation

Run from the repository root, with full Git history available:

```sh
python -m pip install -r site-tools/requirements.txt
python site-tools/build_machine_access.py
python site-tools/validate_release.py
python site-tools/test_projection_build.py
python -m pip install playwright
python site-tools/validate.py
```

The evidence builder preserves the existing release manifest's presentation
version and each existing generated page's header/footer. Site navigation or
presentation-version changes are separate reviewed edits; a data refresh must
not implicitly replace them with a generator's older template. New pages use
the generator's default chrome.

The release validator checks current counts, schemas, references, embedded data,
exports, hashes and local links. Founding glossary, schema and withdrawal guards
remain anchored to the historical baseline. It compares the HTML inventory,
navigation and presentation version against HEAD by default. To review a
committed branch, pass its reviewed base commit explicitly:

```sh
python site-tools/validate_release.py --baseline-ref BASE_COMMIT_SHA
```

The exact historical v0.5.6 candidate assertions remain available separately in
`validate_v056_candidate.py`. Those assertions intentionally depend on the
original prepared candidate, its 52 pages and its exact records; they are not
the current maintenance gate. Historical release reports are not rewritten.

Browser validation serves docs on a temporary loopback HTTP port so relative
URLs and deferred scripts execute normally. Chromium must be allowed to launch
and open local sockets. It uses system Chromium when available, otherwise the
Playwright-installed browser. Override with `--chromium /path/to/chromium`.
Screenshots are temporary unless `--screenshots /output/directory` is supplied.
A browser launch failure is a blocked check, not a passing test.

The regression test builds twice in a disposable copy, verifies that public
content stays byte-identical except timestamp/integrity metadata, and deliberately
introduces version and navigation regressions to verify rejection. It does not
change the working checkout's published files.

For an intentional presentation PR that adds a page or changes navigation,
keep the reviewed base and name each permitted path explicitly:

```sh
python site-tools/validate_release.py --baseline-ref BASE_COMMIT_SHA \
  --allow-new-page docs/considerations/index.html \
  --allow-navigation-page docs/index.html
```

Repeat `--allow-navigation-page` for each intentionally changed HTML page.
These allowances do not permit removed pages, other added pages, or navigation
changes on unlisted pages. Default evidence-only checks remain strict. After
reviewed changes are committed, ordinary HEAD-based validation works unchanged.
