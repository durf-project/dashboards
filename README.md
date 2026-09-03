# DURF Dashboards

Progress-monitoring dashboards for the **DURF (Dutch Repository Federation)**
project — six [Marimo](https://marimo.io) notebooks, one per project theme,
each tracking whether that theme's goal is being met across the
participating institutions.

The DURF project itself, its six themes, timeline and budget, are documented
in [`durf-project/durf-gantt`](https://github.com/durf-project/durf-gantt).
This repo is the operational companion to that roadmap: where the Gantt
chart shows what's planned, these dashboards are meant to show what's
actually happening.

## Status: placeholders

**None of the six dashboards has real data wired in yet.** Each one states,
in its own intro section:

1. the theme's **goal**,
2. what this dashboard is meant to **monitor**, and
3. the concrete **datapoints needed from participating institutions** to do
   that monitoring.

...and then a clearly-marked placeholder query that returns an empty/sample
table with the right shape, so the notebook runs end-to-end today. Filling
one in is a matter of pointing that query at a real data source once the
corresponding harvesting or reporting pipeline exists — the goal/monitor/
datapoints narrative shouldn't need to change.

## Submitting data (institutions)

Rather than build a harvesting pipeline before any real data exists, the
first cut is deliberately manual: each theme has a
[GitHub Issue Form](https://github.com/durf-project/dashboards/issues/new/choose)
with one field per datapoint that theme's dashboard needs. Open one, fill in
what you know for your institution or repository, and submit — no account
setup beyond a free GitHub login, no code.

Submissions are triaged by hand for now: a maintainer transcribes accepted
issues into the matching notebook's placeholder data as a pull request, which
is easy to review and keeps a clear paper trail (issue → PR → dashboard).
Automating that transcription — or the harvesting itself — is future work,
once it's clear the manual version is worth the automation.

## The six dashboards

| Theme | Notebook | Goal |
| --- | --- | --- |
| 1. Governance of the Federation and NL Research Portal | [`notebooks/01-governance/`](notebooks/01-governance/notebook.py) | A sustainable governance framework for the Dutch federated research information ecosystem. |
| 2. Metadata Quality Improvement | [`notebooks/02-metadata-quality/`](notebooks/02-metadata-quality/notebook.py) | Repository/CRIS systems adopt updated metadata and exchange standards for high-quality, internationally compliant research metadata. |
| 3. Full Text Capture | [`notebooks/03-full-text-capture/`](notebooks/03-full-text-capture/notebook.py) | Comprehensive full-text availability in Dutch repository/CRIS systems, for preservation, text-mining, AI use and Taverne. |
| 4. KB National Library e-Depot Archiving | [`notebooks/04-edepot-archiving/`](notebooks/04-edepot-archiving/notebook.py) | Comprehensive preservation of Dutch scientific output in the KB e-Depot. |
| 5. Metadata Distribution & Discovery Optimization | [`notebooks/05-distribution-discovery/`](notebooks/05-distribution-discovery/notebook.py) | Increase the visibility of Dutch research content in major international indexes. |
| 6. NL Research Portal Update | [`notebooks/06-nl-research-portal/`](notebooks/06-nl-research-portal/notebook.py) | A fully-functional, user-centered Netherlands Research Portal as the primary discovery point for Dutch research outputs. |

Notebook directories carry the theme number so they sort in project order
everywhere — filesystem, exported `.html` filenames, and the index page —
not alphabetically. Goal wording is quoted from `durf-gantt`'s
`data/csv/themes.csv`; treat that file as the source of truth if a goal
changes.

## Running a dashboard

Each notebook is self-contained (a [PEP 723](https://peps.python.org/pep-0723/)
header declares its own dependencies) and runs via [`uv`](https://docs.astral.sh/uv/):

```bash
uvx marimo edit --sandbox --watch notebooks/01-governance/notebook.py
```

Swap in any of the six paths above. `--sandbox` is required — it's what makes
`uv` install the notebook's declared dependencies before running it.

To start a new dashboard from the same template these six were built from:

```bash
./scripts/new-notebook.sh my-new-dashboard
```

## Live site (GitHub Pages)

Every push to `main` runs `.github/workflows/deploy.yml`, which exports each
notebook to HTML/WebAssembly and publishes them as a static site — no server,
runs entirely in the visitor's browser via [Pyodide](https://pyodide.org).
This follows marimo's own
[WebAssembly + GitHub Pages template](https://github.com/marimo-team/marimo-gh-pages-template),
adapted for this repo's per-notebook `metadata.json` layout (see
`.github/scripts/build.py`).

**One-time setup, before the first deploy will work:** in this repo's GitHub
Settings → Pages, set **Source** to **GitHub Actions**. After that, the site
publishes automatically on every push to `main` (or via **Actions → Deploy to
GitHub Pages → Run workflow** for a manual run) at
`https://durf-project.github.io/dashboards/`.

To build and preview the site locally before pushing:

```bash
uv run .github/scripts/build.py
python3 -m http.server -d _site
```

## Skills, vendored once

`.claude/skills/` carries the subset of skills from
[`surf-ori/ori-ai-crashcourse`](https://github.com/surf-ori/ori-ai-crashcourse)
needed to build and maintain these notebooks: writing/exporting Marimo
notebooks, querying the SURF ORI DuckLake catalog, and harvesting/resolving
identifiers from participating institutions (OAI-PMH, URN:NBN). See
`AGENTS.md` for the full list and rationale, and `skills-lock.json` for each
skill's upstream source and hash.

## License

Licensed under the [EUPL v1.2](LICENSE).
