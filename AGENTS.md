# Agent conventions — DURF Dashboards

Read this before doing anything else in this repo.

## What this repo is

Six [Marimo](https://marimo.io) notebooks, one per DURF theme, each tracking
whether that theme's goal is being met across participating institutions.
Every notebook states the goal, what it monitors, and what datapoints are
needed, then reads that theme's `data.csv` live from GitHub on every page
load — so a dashboard with zero submissions yet just renders an empty table,
not an error. New data arrives fully automatically: an institution submits
a GitHub Issue Form, `.github/workflows/ingest-submission.yml` appends it to
the CSV, and the next page load picks it up — see "Data submission" below.

This repo was seeded from
[`surf-ori/ori-ai-crashcourse`](https://github.com/surf-ori/ori-ai-crashcourse),
which trains people to build exactly this shape of notebook against the SURF
ORI DuckLake catalog. Only what's needed to build and maintain these six
dashboards was carried over: the notebook template, the skills below, and
this convention doc. The workshop scaffolding (facilitator scripts,
onboarding docs, submission flow) was deliberately left behind — DURF's
dashboards aren't a workshop deliverable.

The six themes, their goals, and the source data behind the Gantt view of the
whole project live in
[`durf-project/durf-gantt`](https://github.com/durf-project/durf-gantt)
(`data/csv/themes.csv` and `data/csv/activities.csv` — the activities sheet
names most of the "health dashboard" deliverables these notebooks implement).
Treat that repo as the source of truth for goal wording; if a theme's goal or
scope changes there, update the matching notebook's intro cell to match.

```
notebooks/<slug>/
├── notebook.py       # PEP 723 header, marimo.App(width="full", ...)
├── metadata.json      # title, image, authors[]
├── data.csv           # submitted data; appended to by the ingest workflow
└── public/            # screenshots, static assets referenced by metadata.json
```

Start every new notebook with `./scripts/new-notebook.sh <slug>` — it copies
`notebooks/_template/` and substitutes the title. Don't hand-roll a notebook
directory from scratch.

The six slugs already in `notebooks/` map to the six DURF themes. Each slug
is prefixed with its zero-padded theme number (`01-`…`06-`) so the
directories, the exported `.html` filenames, and the index page all sort in
project order instead of alphabetically:

| Slug | Theme # | Theme |
| --- | --- | --- |
| `01-governance` | 1 | Governance of the Federation and Netherlands Research Portal |
| `02-metadata-quality` | 2 | Metadata Quality Improvement |
| `03-full-text-capture` | 3 | Full Text Capture |
| `04-edepot-archiving` | 4 | KB National Library e-Depot Archiving |
| `05-distribution-discovery` | 5 | Metadata Distribution & Discovery Optimization |
| `06-nl-research-portal` | 6 | NL Research Portal Update |

Don't rename these slugs — other docs and the Gantt link to them by name.
The same numbering also appears in each notebook's displayed title (e.g.
`app_title="2. Metadata Quality Improvement"` and its `# 2. ...` heading) and
in `metadata.json`'s `title` field, so the number stays visible even
somewhere that only shows the title text (a browser tab, the index card),
not just the directory listing. Because cell/variable names inside
`notebook.py` can't start with a digit, they use a `themeNN_` prefix instead
(e.g. `theme02_metadata_quality_data`), not the bare slug — keep that prefix
if you ever rename a theme's short name.

## Running a notebook preview

Nothing in this environment has `marimo` on `PATH` directly; it's a
`uvx`-managed ephemeral install driven by the PEP 723 header at the top of
each `notebook.py`. Preview one with:

```bash
uvx marimo edit --sandbox --watch notebooks/<slug>/notebook.py
```

`--sandbox` is required, not optional — without it marimo runs in an
environment containing only its own dependencies, and the first `import
duckdb` (or `altair`, `pandas`, `pyarrow`) fails with `ModuleNotFoundError`
even though the PEP 723 header is correct. If you're starting this detached
in a sandboxed/headless environment for someone else to view in a browser,
see `.claude/skills/marimo-notebook/SKILL.md` for the host/port pitfalls —
they're the same ones that bit the crash-course repo this was seeded from.

Before calling a notebook done, run both of these yourself — don't just read
the diff and assume it works:

```bash
uvx marimo check notebooks/<slug>/notebook.py
uv run notebooks/<slug>/notebook.py
```

`marimo check` is a static linter; it won't catch a missing dependency or a
runtime `AttributeError`. Only `uv run` actually imports the notebook's cells.

## Marimo notebook conventions

- **Name every cell** (`def dutch_institutions_query(...):`, not `def _():`)
  so a `git diff` and a reviewer can tell what a cell is for without opening
  the browser UI.
- **Keep SQL cells pure SQL.** `mo.sql(f"""...""", engine=con, output=False)`
  should contain only the query; build any Python control flow in a
  preceding cell.
- **Underscore-prefix cell-local throwaway output** (`_ = mo.md(...)`) —
  reusing a plain name like `heading` across two cells is exactly how you get
  `MultipleDefinitionError`.
- **Name a proxy when you use one.** Several of these themes don't have a
  direct, ground-truth column for what they want to monitor (e.g. "is this
  record in Google Scholar's index" has no field anywhere) — see
  `notebooks/_template/notebook.py`'s commented-out proxy example for the
  pattern: name the proxy, say what it misses, don't hide it.

`.claude/skills/marimo-notebook/` has the full reference (SQL cells, reactivity,
state, WASM export, deployment).

## A notebook with zero rows is not a broken one

Every notebook here should already have, in its intro `mo.md()` cell:

1. **Goal** — the theme's goal, quoted from `durf-gantt`'s `themes.csv`.
2. **What we monitor** — the specific thing this dashboard tracks, drawn from
   the matching "health dashboard" activity in `durf-gantt`'s
   `activities.csv` where one exists.
3. **Datapoints needed from participating institutions** — a concrete list:
   per-institution counts, ratios, or status fields, not "relevant data".

Below that, the data cell fetches that theme's `notebooks/<slug>/data.csv`
straight from `raw.githubusercontent.com` on every load, wrapped in a
`try/except` that falls back to an empty DataFrame with the right columns on
any failure (network error, 404, malformed CSV) — so a theme with no
submissions yet renders an empty table, not a crash. Numeric columns are
coerced with `pd.to_numeric(..., errors="coerce")` after fetch, since
`ingest_issue.py` writes whatever the submitter typed without validating it;
a bad value becomes `NaN` in that row, not a broken notebook. Don't leave a
notebook that fails `marimo check` or `uv run` — "no data yet" means the CSV
is empty, not that the fetch/coercion logic is broken.

The table below the data cell (`mo.ui.table(..., label="Submitted data")`)
doubles as the moderation view: it includes `submitted_by` (the submitter's
GitHub username), `submitted_via_issue`, and `submitted_at` for every row,
sortable and filterable right there — that's how a maintainer spots a bad or
malicious entry. The chart cell reads the table's current *selection*
(`table.value`, falling back to the full dataset when nothing is selected)
rather than the raw data directly, which is what makes selecting rows in the
table filter the chart — keep that wiring if you touch either cell.

## Data submission: GitHub Issue Forms, auto-ingested

Each theme has a matching Issue Form in `.github/ISSUE_TEMPLATE/`
(`01-governance-data.yml` … `06-nl-research-portal-data.yml`), one field per
datapoint listed in that notebook's "Datapoints needed from participating
institutions" section. Field `id`s match the corresponding `data.csv`
column names exactly (e.g. `02-metadata-quality-data.yml`'s `compliance_pct`
field ↔ `notebooks/02-metadata-quality/data.csv`'s `compliance_pct` column).

**The `repo` field (themes 2–5) and `institution` field (theme 1) are
closed dropdowns, not free text** — this is deliberate: it's what stops "TU
Delft Repository," "TU Delft," and "Delft University of Technology" from
being recorded as three different things. Each has an `"Other / not listed
here"` fallback, last in the list, for anything missing from its source:

- `repo` — 149 options: the 148 unique `Name` values from
  [`surf-ori/dutch-sources`](https://github.com/surf-ori/dutch-sources)'s
  `data/nl_orgs_openaire_datasources.xlsx` (HTML entities decoded,
  non-breaking spaces and stray whitespace normalized, deduplicated).
- `institution` (theme 1 only — **theme 6 still uses free text**, not yet
  asked for) — 62 options: the 61 organisations with `is_surf_member = True`
  in
  [`surf-ori/nl-research-organisations`](https://github.com/surf-ori/nl-research-organisations)'s
  `data/nl_research_orgs.csv`.

To refresh either list after its source changes: re-download the source,
rebuild the option list with the same filter/normalization, keep the
`"Other / not listed here"` fallback last, and update every `options:` block
that uses that list identically (four files for `repo`, currently one for
`institution`) — there's no script for this, each was a one-off Python
transform run by hand.

This is fully automated, on purpose (no manual curation step):
`.github/workflows/ingest-submission.yml` fires on every opened issue
carrying the `data-submission` label, runs `.github/scripts/ingest_issue.py`
to parse the issue-form body (GitHub renders each field as a `### <label>`
heading followed by the response) back into columns via the exact label
text, appends one row — plus `submitted_by`, `submitted_via_issue`, and a
UTC `submitted_at` timestamp — to the matching `data.csv`, commits and
pushes straight to `main`, then comments on and closes the issue. No PR, no
review gate, by design.

If you touch either half of this pipeline, keep both in sync:

- **The label→column mapping** lives in two places that must agree:
  `ingest_issue.py`'s `THEME_FIELDS` (label text → column id) and each
  notebook's data cell (the column list and which ones get numeric
  coercion). Adding a form field means adding it to both, plus regenerating
  `data.csv`'s header (see the generator note below) unless you edit it by
  hand.
- **Test the parser, not just the notebook.** `ingest_issue.py` has no test
  suite; when you change it, run it locally against a fabricated issue body
  (set `ISSUE_BODY`, `ISSUE_NUMBER`, `ISSUE_AUTHOR`, `ISSUE_LABELS_JSON`,
  `GITHUB_OUTPUT` as env vars, per the workflow) before trusting it against
  a real issue.
- **This workflow only ever runs the copy of itself on `main`** — GitHub
  evaluates `issues`-triggered workflows from the repository's default
  branch, not from a PR branch, so you cannot test a change to
  `ingest-submission.yml` or `ingest_issue.py` by opening a PR alone. Get it
  right locally first, merge, then open a real test issue to confirm.
- **No spam/validation gate exists yet.** A bad submission lands in the
  chart automatically; the only defense today is that every row carries
  `submitted_by` for a maintainer to spot and, if needed, delete by hand
  (edit the CSV, open a PR). If that becomes a real problem, the next step
  is adding a review gate (route the commit through a PR instead of pushing
  straight to `main`) or basic shape validation in `ingest_issue.py` — don't
  build either speculatively before it's actually needed.

There's no `notebooks/<slug>/notebook.py` generator script checked into this
repo (the six were built with one, then hand-maintained) — when adding a
form field to an existing theme, edit the notebook's data cell, the Issue
Form YAML, and `ingest_issue.py`'s `THEME_FIELDS` together, and add the new
column to `data.csv`'s existing header by hand (don't touch existing rows).

## Skills live in `.claude/skills/`, and only there

Same rationale as the crash-course repo this was seeded from: Claude Code
discovers `.claude/skills/<name>/SKILL.md` natively, and this is the only
skills directory here — no `.agents/skills/` duplicate, no symlinks.

Skills were vendored once (copied from `surf-ori/ori-ai-crashcourse`, which
itself vendored them via `npx skills add`), and are tracked in git — not
fetched at install time. See `skills-lock.json` for provenance (source repo,
hash) of each one. Only the skills actually needed to build and maintain
these six dashboards were carried over:

- `marimo-notebook`, `wasm-compatibility`, `anywidget-generator` — writing
  and exporting the notebooks themselves.
- `duckdb-fundamentals`, `ori-ducklake`, `polars` — querying the SURF ORI
  DuckLake catalog and shaping the result.
- `oai-pmh`, `urn-nbn` — harvesting metadata from and resolving persistent
  identifiers at participating institutions, which several themes'
  real datapoints will need directly (Theme 3's full-text capture, Theme 4's
  URN:NBN resolver, Theme 2's OAI compliance validation).

`duckdb-fundamentals` has no `skills-lock.json` entry, deliberately — it's
hand-written upstream, not vendored. Don't add one without checking why, in
the upstream repo's `AGENTS.md`, that's the case.

The general workshop-process skills from the source repo (`brainstorming`,
`ponytail*`, `writing-plans`, `systematic-debugging`, `using-git-worktrees`,
`using-superpowers`, etc.) were intentionally **not** carried over — they're
about running a workshop, not about building or maintaining a dashboard.
Add one back only if a real need for it shows up here.

## Data access

The `ori-ducklake` MCP server (configured in `.mcp.json`) is the primary way
to query the SURF ORI DuckLake catalog (OpenAlex, OpenAIRE, CRIS, OpenAPC) —
useful for cross-checking institution-level facts that are already public,
but it does **not** hold the participation data (compliance checks, PID
presence, e-Depot backup ratios, etc.) these dashboards ultimately need —
that has to come from the participating institutions themselves, per theme,
as scoped in each notebook's intro cell. The `ori-ducklake` skill has the
schema cheat-sheet and query patterns; `describe_table` is slow on large
tables, prefer `catalog_stats` first.

Never `UNNEST` authorships on `openalex.works` unfiltered — it's 364M rows.
Filter first, aggregate second.

## Conventions

- Commit per concern; keep diffs reviewable.
- Before any commit, grep the staged diff for anything resembling a
  credential and abort if found.
