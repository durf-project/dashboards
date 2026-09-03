# Agent conventions — DURF Dashboards

Read this before doing anything else in this repo.

## What this repo is

Six [Marimo](https://marimo.io) notebooks, one per DURF theme, each tracking
whether that theme's goal is being met across participating institutions.
Every notebook currently under `notebooks/` is a **placeholder**: it states
the goal, what to monitor, and what datapoints are needed, but has no real
data wired in yet, because the harvesting/reporting pipeline from
participating institutions doesn't exist yet. Filling one in means replacing
its placeholder query with a real one once that data is available — the
narrative markdown at the top of the notebook should not need to change.

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
(e.g. `theme02_metadata_quality_placeholder_data`), not the bare slug — keep
that prefix if you ever rename a theme's short name.

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

## A placeholder notebook is not an empty one

Every notebook here should already have, in its intro `mo.md()` cell:

1. **Goal** — the theme's goal, quoted from `durf-gantt`'s `themes.csv`.
2. **What we monitor** — the specific thing this dashboard tracks, drawn from
   the matching "health dashboard" activity in `durf-gantt`'s
   `activities.csv` where one exists.
3. **Datapoints needed from participating institutions** — a concrete list:
   per-institution counts, ratios, or status fields, not "relevant data".

Below that, a clearly marked placeholder query cell (commented `# TODO:` or
similar) that returns an empty/sample structure with the right columns,
so the chart and table cells below it render without error today and only
need the query swapped out once real data exists. Don't leave a placeholder
notebook that fails `marimo check` or `uv run` — "not yet filled in" means
the data source is missing, not that the notebook is broken.

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
