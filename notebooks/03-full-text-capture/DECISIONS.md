# DURF Full Text Monitor — decision log & handoff notes

Companion doc for `03-full-text-capture.html` (also delivered as `durf_fulltext_monitor.html`).
Written for a code agent picking this up next — covers what was decided, why, what's
known-imperfect, and what's still open.

---

## 1. What this is

An interactive, single-file HTML dashboard on file/open-access status of Dutch CRIS
repository publications. Built as the outcome of discussions with the DURF Theme 3
("Full Text Capture") and Theme 2 leads (Pascal, Rutger). Intended to sit at
`durf-project.github.io/dashboards/03-full-text-capture.html`, replacing whatever is
there now.

Theme 3 goal/outcome it maps to (as given):

- **Goal:** comprehensive full-text availability in Dutch repository/CRIS systems
  (preservation primarily; text-mining, AI usage, Taverne mechanisms secondarily).
  Establish baseline metrics and a reporting system for full-text uptake.
- **Outcome:** a "Digital Sovereignty Health" CRIS/Repo dashboard — ratio of metadata
  records containing a link to a file (PDF) on the institutional domain, per repo,
  over time.

Marked as a **Proof of Concept** (chip next to the title) — this is a demonstration
of what's possible from the ORI DuckLake data, not a finished monitoring product.

---

## 2. Data source & extraction

- **Catalog:** SURF ORI DuckLake, public/no-auth "Frozen DuckLake" pattern.
  `ducklake:https://objectstore.surf.nl/cea01a7216d64348b7e51e5f3fc1901d:sprouts/catalog.ducklake`
- **Connection:** DuckDB ≥1.5.2, `INSTALL/LOAD ducklake` + `INSTALL/LOAD httpfs`, then
  `ATTACH ... AS lake (READ_ONLY, CREATE_IF_NOT_EXISTS false)`.
- **Table used:** `cris.publications` only (2,368,535 rows across 18 institutions).
  Other schemas exist in the same lake (`openalex`, `openaire`, `openapc`) but weren't
  used here.
- **Method:** queried directly from a sandbox with a live DuckDB connection (not
  through any dashboarding tool), aggregated in Python/pandas, then embedded the
  aggregate as dictionary-encoded JSON inside the HTML file. **No live connection
  exists from the page itself** — see §6.
- **Snapshot timing (important, see §7):**
  - The `cris.publications` table was last (re)loaded into the DuckLake catalog on
    **2026-03-04** (from `ducklake_snapshots('lake')`, `tables_altered` containing
    table_id `2`).
  - Per-institution, the source repositories' own OAI-PMH `header.datestamp` values
    range up to **2026-04-15**.
  - These two dates are in the wrong order relative to each other (harvest dates are
    *after* the catalog's last load date) — flagged, not resolved. See §7.

---

## 3. Data model decisions

Aggregated fact table, one row per unique combination of:

`institution × publication type × year × open access status × file status × license × publisher`
→ `count`

Encoded in the HTML as `{"dims": {...}, "rows": [[institution_id, pubtype_id, yr,
oa_status_id, file_status_id, license_id, publisher_id, n], ...]}` (96,361 rows,
~2.2 MB). All filtering/aggregation for the charts happens client-side in JS against
this array — no server, no live query.

### Field-by-field derivation logic (also embedded as literal SQL in the dashboard's
own query tooltips — see §5)

| Field | Source | Logic |
|---|---|---|
| `institution` | `repository_info.institution` | used as-is |
| `pubtype` | `"pubt:Type"."#text"` (COAR resource_type URI) | top-10 URIs mapped to readable labels (Journal article, Journal, Book part, Conference paper, Doctoral thesis, Book, Report, Review article, Review, Working paper); everything else → **"Other"** |
| `oa_status` | `"ar:Access"` (COAR access_right URI) | c_abf2→Open access, c_14cb→Metadata only, c_f1cf→Embargoed, c_16ec→Restricted, NULL/other→**"Unknown"** |
| `file_status` | `"cerif:FileLocations"` | NULL → **"No file"**; else if any `cerif:Medium[].ar:Access` = c_abf2 → **"Open file"**; else → **"Embargoed file"**. (There is no "closed" flag at file level — every file in this data is either open or embargoed; "closed" is inferred from having no file at all.) |
| `license` | first file's first `cerif:License."#text"` | no file → "No file"; raw value is a `cc_*` code or `taverne` → passed through as-is; raw value present but not recognized → "Unknown"... *(see note)*; no license on an existing file → "Unknown"; anything else → "Other license" |
| `publisher` | first `cerif:Publishers."cerif:Publisher"[1]."cerif:OrgUnit"."cerif:Name"[1]."#text"` | NULL → "No publisher"; else run through a ~25-branch `CASE`/`LIKE` normalizer merging spelling variants (e.g. "Elsevier B.V." / "Elsevier Inc." / "Elsevier Ltd" → "Elsevier"); if the normalized name is in the top-35-by-volume list, keep it, else → "Other publisher" |

Year range used throughout: **1995–2025** (2026 excluded as an in-progress year;
pre-1995 records exist in the raw data but are sparse/noisy and were dropped).

### Known simplifications / things a careful reviewer should question

- **File presence ≠ PDF on institutional domain.** The Theme 3 outcome text specifically
  asks for "a link to a file (PDF) on the institutional domain." What's implemented is
  "has at least one `cerif:FileLocations.cerif:Medium` entry, regardless of MIME type or
  URI domain." `cerif:MimeType` and `cerif:URI` are both available in the source data and
  were **not** used to narrow this down. **This is probably the single most important
  thing to fix if this dashboard needs to match the Theme 3 KPI definition exactly.**
- **License bucketing is per-publication, first-file-only.** A publication can have
  multiple files with different licenses (~12,556 of ~667k publications-with-files have
  mixed access across their files); only the first file's license is used.
- **Publisher normalization is a hand-built alias list**, not a proper authority match.
  Long tail (58,689 distinct raw publisher strings) is real; only the top 35 by volume
  get merged, the rest fall into "Other publisher."
- **`file_status` is similarly first/any-file logic**: "Open file" means *at least one*
  file is open, even if others attached to the same record are embargoed.

---

## 4. UI/UX decisions (iterative, in the order they came up)

1. Filters: institution, publication type, open access status, file status, license,
   publisher, year range. Multi-select via checkbox "chips."
2. Each filter group got a **search box** (filters the visible chip list) and
   **all/none** quick buttons, because with 18 institutions / 35 publishers,
   manually unchecking everything else to isolate one value was painful.
3. **Double-click a chip → "solo select"** (selects only that value, deselects
   everything else in that group) — the fast path for "I only care about Elsevier"
   type questions.
4. Charts, in the order added:
   - Publications per institution (bar)
   - File status per institution (100% stacked bar)
   - Trend: % with open file per year (line)
   - File status per year (100% stacked bar) — added specifically to track progress
     on the backlog over time
   - Open access status (doughnut)
   - License of the file (bar, Taverne highlighted)
   - Publication type: total vs. with file (grouped bar)
   - File status per publication type (100% stacked bar)
   - Publishers: % with file, sorted low→high, red→green color scale, min. 100
     publications to qualify — explicitly a "find problem publishers" view
5. **KPI cards** at the top: total publications (in selection), % open file,
   % embargoed file, % no file, count with Taverne license.
6. **Info badges (ⓘ)** on every KPI, chart title, and filter-group heading. Hover
   shows the underlying SQL query in a tooltip; click opens that exact query, live,
   in the [ORI DuckLake overview tool](https://surf-ori.github.io/ducklake-overview/overview.html)
   against `cris.publications`.
   - Chart/KPI badges reflect the **currently active filters** (dynamically rebuilt
     on every filter change).
   - Filter-group badges show "what values remain, given your *other* active
     filters" (excludes that dimension's own filter, includes the rest) —
     effectively faceted search preview.
   - **Known gap:** the Publisher filter's *own* selection is never reflected in
     any query tooltip, because reproducing the 25-branch normalizer inline in every
     query was judged not worth the length/complexity. Tooltips add an explicit
     comment when Publisher is filtered, telling the user this.
7. Language: **English** throughout (was originally built in Dutch, translated in
   full — UI strings, chart legend values, SQL comments in tooltips, number format
   switched from `nl-NL` to `en-US`).
8. **"Proof of Concept" chip** next to the H1.
9. **Background + Data currency merged into one `<details>` accordion**, collapsed
   by default, click-to-expand. Contains:
   - The Theme 3 background/goal/outcome text and a link to the
     [DURF Gantt roadmap](https://durf-project.github.io/durf-gantt/gantt.html).
   - An explicit "no live connection" disclaimer (see §6).
   - The data-currency dates from §2/§7, with its own info-badge query.
10. Dark/light theme support via `prefers-color-scheme`, safe-area padding for
    mobile, all charts via Chart.js (pinned `4.5.1` from jsdelivr).

---

## 5. Where the SQL "source of truth" lives

The dynamic query-tooltip system in `app.js` (inside the published HTML) is the most
complete, current documentation of the exact aggregation logic — more so than this
file, since it's literally the SQL run to reproduce every number on screen. Key
pieces, if extracting logic for a rebuild:

- `FS_CASE` — file status derivation
- `OA_CASE` — open access status derivation
- `LICENSE_CASE` — license bucketing
- `PUBTYPE_CASE` / `PUBTYPE_URI_TO_LABEL` — publication type mapping
- `QUERY_BUILDERS` — one function per info-badge, takes current filter `state` and
  returns the exact SQL string, used to build the `ducklake-overview` links
- `CLAUSE_BUILDERS` / `activeClauses()` — turns the live filter selection into SQL
  `WHERE` fragments

Publisher normalization (the ~25-branch `LIKE` CASE) only exists in the Python build
scripts used to generate the embedded JSON — **it is not reproduced in `app.js`**
(that's the gap noted in §4.6). If this needs to become source-of-truth-queryable,
that CASE needs to be ported into `app.js` too, or the build script needs to be
checked into the repo.

---

## 6. "No live connection" — what would it take to change that

Currently: static snapshot, Python/DuckDB build step → JSON embedded in HTML → pure
client-side JS filtering. Nothing calls out to the DuckLake catalog at view time.

Options if live (or at least "refresh on load") is wanted later:
- **Simplest — scheduled rebuild:** keep the current architecture, add a CI job
  (GitHub Action) that re-runs the Python extraction against the DuckLake catalog on
  a schedule (e.g. nightly/weekly) and commits the regenerated HTML. No new
  infrastructure, just automation of the manual step done here.
- **DuckDB-WASM in-browser:** DuckDB has a WASM build; in principle it could attach
  to the same `ducklake:https://...` catalog via `httpfs` directly from the browser,
  making this genuinely live. Not attempted here — unverified whether the `ducklake`
  extension is available/stable in the WASM build, and whether SURF's object store
  CORS policy allows browser-side fetches. Worth a spike before committing to this
  path.
- **Small server-side API:** a thin backend (could be a scheduled function) that runs
  the DuckDB query and serves pre-aggregated JSON, fetched by the page on load. Middle
  ground between the two above.

---

## 7. Open questions / follow-ups

1. **Snapshot-date discrepancy (unresolved):** catalog `tables_altered` for
   `cris.publications` says 2026-03-04; per-record `header.datestamp` values go up to
   2026-04-15 (i.e., *after* the catalog's own last-load date). That shouldn't be
   possible if the load reflects a harvest that happened before it. Worth asking
   whoever manages ORI DuckLake ingestion whether the snapshot log or the harvest
   pipeline is the one telling the truth here — this dashboard just reports both
   numbers as found, without resolving the contradiction.
2. **Should "file" mean "PDF on institutional domain" specifically?** (See §3.) If
   yes, this is a rework of `file_status`/`FS_CASE`, the underlying Python
   aggregation, and the JSON data — not a small tweak, since it touches most of the
   dashboard's charts.
3. **Push to `durf-project/dashboards`:** no GitHub connector was available in the
   session that built this, so the file was handed over manually rather than
   committed. Needs `03-full-text-capture.html` copied into the `dashboards/` folder
   of that repo and pushed. This doc is meant to go alongside it.
4. **Publisher filter → query tooltip gap** (§4.6) — low priority, cosmetic/trust
   issue rather than a data-correctness one.
5. **Refresh cadence** — no decision made yet on how often this should be
   regenerated once it's not just a PoC. Depends on how DURF wants to use it
   (one-off report vs. living dashboard).
6. **OA Switchboard business case is a first pass, not a validated figure.** The
   370k/216k numbers in §9 rest on an approximate publisher-name match and a cost
   rate sourced from one institution's experience with a different workflow
   (Taverne retro-opt-out, not publisher-PDF-capture specifically). Treat the
   dashboard's cost estimates as a starting point for discussion, not a number to
   put in a funding request without someone sanity-checking the assumptions below.

---

## 9. OA Switchboard automation business case (added 2026-10-01)

Added to investigate whether OA Switchboard could build a PDF-capture service for
CRIS/repositories, and whether the volume from its partner publishers would justify
the engineering and legal effort (publisher agreements) versus just leaving that
slice of the backlog to manual capture.

### What was added
- **Filter: "Automation exploration routes" → "via OA Switchboard"** — a single
  on/off toggle (off by default, unlike every other filter which is a multi-select
  defaulting to "everything selected"). When on, restricts the whole dashboard to
  publications whose first listed publisher matches an OA Switchboard participant.
- **New data dimension: `oa_switchboard`** (`"OA Switchboard partner"` /
  `"Not a partner"`), added to the aggregated fact table alongside the existing six
  dimensions (now 8 total, `dashboard_data_v4.json`, 100,566 pre-aggregation rows →
  the same dictionary-encoding approach as before).
- **KPI: "Est. manual capture cost"** — inserted between "No file" and "Taverne
  license". Shows hours and an indicative € figure for the currently-filtered
  "no file" backlog, with a live-editable €/hour input (defaults to €50) so a given
  institution can plug in its own rate.
- **Chart: "Estimated manual capture cost per year"** — same cost math, broken out
  by publication year, so an institution can decide how many years of backlog fit a
  given budget, filtered the same way as the KPI.
- Both the KPI and the chart force `file_status = "No file"` internally regardless of
  what the File status filter is set to (there's no sensible "capture cost" for
  records that already have a file), while still respecting every other active
  filter (institution, publication type, year range, open access status, license,
  publisher, and the new OA Switchboard toggle).
- Query tooltips updated throughout: the OA Switchboard toggle is now a first-class
  entry in the dynamic `WHERE`-clause builder (`CLAUSE_BUILDERS.oa_switchboard`), so
  *every* existing chart's tooltip correctly reflects the toggle when it's on, not
  just the two new ones.

### Publisher matching logic
`OASB_PATTERNS` in `app.js` (51 case-insensitive substrings, one per OA Switchboard
participant — live and "preparing to go live" are **not** distinguished, both count)
is matched against the same raw `cerif:Publishers` first-name field used elsewhere.
Source: <https://www.oaswitchboard.org/participants>, checked 2026-10-01. This is
independent of, and uses a different (coarser) matching strategy than, the existing
top-35 Publisher-bucket normalization — a publication can be tagged
"OA Switchboard partner" even if its specific publisher isn't one of the 35 broken
out individually in the Publisher filter/chart.

### Headline numbers (full dataset, 1995–2025, no other filters applied)
- 370,199 publications (19.4% of all 1,912,504 in-scope records) matched an OA
  Switchboard partner.
- Of those, 216,576 have no file — **~17% of the entire NL "no file" backlog**
  (1,277,665 records) sits with publishers OA Switchboard already has a
  relationship with.
- 11 of the 51 OA Switchboard participants were already in the dashboard's
  top-35-by-volume Publisher bucket: Wiley, Oxford University Press,
  Taylor & Francis, IEEE, American Chemical Society, BMJ Publishing Group,
  Cambridge University Press, Frontiers Media, PLOS, Brill, American Institute of
  Physics. The other 40 participants (eLife, PNAS, Royal Society of Chemistry,
  De Gruyter, MDPI, etc.) only show up through the new `oa_switchboard` flag, not
  as individually-named bars in the Publisher chart.

### Cost assumption — read this before quoting the numbers anywhere
7 minutes/record, and the resulting €/hr figures, come entirely from one
institution's account of their 2023 Taverne retro-opt-out project (~450 journal
articles ≈ 52 hours of OA-team time) — see the pasted Dutch conversation this
feature was built from. Important caveats carried into the dashboard's own
tooltips and background panel, but worth restating here:
- That was a *different workflow* (opt-out notice + manual deposit of
  already-licensed material) from what's being costed here (sourcing a PDF from a
  publisher relationship, which is what an OA Switchboard service would actually
  do). Treat the rate as a rough proxy, not a direct measurement of the thing being
  proposed.
- It's evidenced for **journal articles only**. The source conversation explicitly
  flags that book chapters take "much more effort" per record, with no number
  given. Applying 7 min/record to non-journal-article types (the dashboard doesn't
  stop you from doing this) will understate the true cost — use the Publication
  type filter to scope to journal articles for a defensible number.
- It's one institution's internal estimate, not a sector benchmark. No attempt was
  made to find a second data point.

### Still open
- Should "preparing to go live" OA Switchboard participants (6 of the 51) be
  excluded or shown separately, rather than merged into the same toggle as the
  45 already-live ones? Currently merged.
- The manual-capture rate needs a better source, or at least a second institution's
  numbers, before this goes into an actual funding ask.
- No attempt was made to estimate the *automation* side of the cost-benefit (what
  it would cost OA Switchboard to build and maintain this, or what licensing
  renegotiation with 51 publishers would take) — only the manual-alternative side is
  quantified here. The business case needs both sides before it's actually a
  business case.

---

## 10. Files

- `03-full-text-capture.html` / `durf_fulltext_monitor.html` — the dashboard itself
  (identical content, two filenames for convenience). Self-contained, no external
  data files needed at runtime.
- This file (`DECISIONS.md`) — handoff notes only, not referenced by the HTML.
