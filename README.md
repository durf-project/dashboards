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

## The six dashboards

| Theme | Notebook | Goal |
| --- | --- | --- |
| 1. Governance of the Federation and NL Research Portal | [`notebooks/governance/`](notebooks/governance/notebook.py) | A sustainable governance framework for the Dutch federated research information ecosystem. |
| 2. Metadata Quality Improvement | [`notebooks/metadata-quality/`](notebooks/metadata-quality/notebook.py) | Repository/CRIS systems adopt updated metadata and exchange standards for high-quality, internationally compliant research metadata. |
| 3. Full Text Capture | [`notebooks/full-text-capture/`](notebooks/full-text-capture/notebook.py) | Comprehensive full-text availability in Dutch repository/CRIS systems, for preservation, text-mining, AI use and Taverne. |
| 4. KB National Library e-Depot Archiving | [`notebooks/edepot-archiving/`](notebooks/edepot-archiving/notebook.py) | Comprehensive preservation of Dutch scientific output in the KB e-Depot. |
| 5. Metadata Distribution & Discovery Optimization | [`notebooks/distribution-discovery/`](notebooks/distribution-discovery/notebook.py) | Increase the visibility of Dutch research content in major international indexes. |
| 6. NL Research Portal Update | [`notebooks/nl-research-portal/`](notebooks/nl-research-portal/notebook.py) | A fully-functional, user-centered Netherlands Research Portal as the primary discovery point for Dutch research outputs. |

Goal wording is quoted from `durf-gantt`'s `data/csv/themes.csv`; treat that
file as the source of truth if a goal changes.

## Running a dashboard

Each notebook is self-contained (a [PEP 723](https://peps.python.org/pep-0723/)
header declares its own dependencies) and runs via [`uv`](https://docs.astral.sh/uv/):

```bash
uvx marimo edit --sandbox --watch notebooks/governance/notebook.py
```

Swap in any of the six slugs above. `--sandbox` is required — it's what makes
`uv` install the notebook's declared dependencies (`marimo`, `duckdb`,
`altair`, `pandas`, `pyarrow`) before running it.

To start a new dashboard from the same template these six were built from:

```bash
./scripts/new-notebook.sh my-new-dashboard
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
