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

## Status: live, usually sparse

Each dashboard's intro section states the theme's **goal**, what it's meant
to **monitor**, and the concrete **datapoints needed from participating
institutions**. Below that, the table and chart read that theme's
`data.csv` straight from GitHub on every page load — so a dashboard with no
submissions yet just renders an empty table, not an error, and a new
submission needs no site rebuild to appear, only a page reload (GitHub's
raw-file cache can lag a few minutes).

## Submitting data (institutions)

Each theme has a
[GitHub Issue Form](https://github.com/durf-project/dashboards/issues/new/choose)
with one field per datapoint that theme's dashboard needs. Open one, fill in
what you know for your institution or repository, and submit — no account
setup beyond a free GitHub login, no code.

From there it's fully automatic: `.github/workflows/ingest-submission.yml`
parses the issue, appends one row to the matching `notebooks/<slug>/data.csv`
(recording the submitter's GitHub username, the issue number, and a
timestamp alongside the data), commits it to `main`, and closes the issue —
no manual transcription step. Every row keeps its `submitted_by`; sort or
filter on it in the dashboard's table to spot bad or malicious entries. To
correct a mistake, edit the CSV directly and open a PR — see `AGENTS.md` for
the full pipeline and how to add validation later if spam becomes a problem.

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
