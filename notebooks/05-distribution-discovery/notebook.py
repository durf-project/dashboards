# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "altair",
#     "pandas",
#     "pyarrow",
# ]
# ///

import marimo

__generated_with = "0.20.4"
app = marimo.App(width="full", app_title="5. Metadata Distribution & Discovery Optimization")


@app.cell
def imports():
    import altair as alt
    import pandas as pd
    import marimo as mo

    return alt, mo, pd


@app.cell
def intro(mo):
    mo.md("""
    # 5. Metadata Distribution & Discovery Optimization

    ## Goal

    Increase the visibility of Dutch research content in major international indexes.

    ## What this dashboard monitors

    "Discoverability health": implementation of the Google Scholar inclusion guidelines, per repo, over time -- plus the DOI-minting rate for grey literature that has a locally attached PDF but no DOI.

    ## Datapoints needed from participating institutions

    - Repository / CRIS name
    - Google Scholar inclusion-guideline compliance status/score
    - Grey-literature records with a local PDF but no DOI
    - Of those, records that have since had a DOI minted
    - Snapshot date

    ---

    **Status: live, usually sparse.** The table and chart below read
    `data.csv` straight from GitHub on every page load -- a new submission
    needs no site rebuild, just a page reload (GitHub's raw-file cache can
    lag a few minutes behind). Data arrives through the
    [05-distribution-discovery Issue Form](https://github.com/durf-project/dashboards/issues/new?template=05-distribution-discovery-data.yml),
    auto-ingested by `.github/workflows/ingest-submission.yml` -- no manual
    transcription step. `submitted_by` on each row is the submitter's GitHub
    username; sort or filter that column in the table to spot bad entries.
    Select rows in the table to filter the chart to just those. See
    `AGENTS.md` for the full pipeline.
    """)
    return


@app.cell
def theme05_distribution_discovery_data(pd):
    # Fetched fresh on every load from the data.csv that
    # .github/scripts/ingest_issue.py appends to -- see the intro above.
    # No validation happened on the way in, so coerce numeric columns with
    # errors="coerce" (bad values become NaN) rather than trust the input.
    _url = (
        "https://raw.githubusercontent.com/durf-project/dashboards/main/"
        "notebooks/05-distribution-discovery/data.csv"
    )
    _empty = pd.DataFrame(
        {
            "repo": pd.array([], dtype="string"),
            "scholar_guideline_compliance_pct": pd.array([], dtype="Float64"),
            "grey_lit_without_doi": pd.array([], dtype="Int64"),
            "grey_lit_doi_minted": pd.array([], dtype="Int64"),
            "snapshot_date": pd.array([], dtype="string"),
            "submitted_by": pd.array([], dtype="string"),
            "submitted_via_issue": pd.array([], dtype="Int64"),
            "submitted_at": pd.array([], dtype="string")
        }
    )
    try:
        theme05_distribution_discovery_data = pd.read_csv(_url, dtype="string")
    except Exception:
        theme05_distribution_discovery_data = _empty
    else:
        for _col, _dtype in {"scholar_guideline_compliance_pct": "Float64", "grey_lit_without_doi": "Int64", "grey_lit_doi_minted": "Int64", "submitted_via_issue": "Int64"}.items():
            theme05_distribution_discovery_data[_col] = pd.to_numeric(
                theme05_distribution_discovery_data[_col], errors="coerce"
            ).astype(_dtype)
        theme05_distribution_discovery_data = theme05_distribution_discovery_data.reindex(columns=_empty.columns)
    return (theme05_distribution_discovery_data,)


@app.cell
def theme05_distribution_discovery_table(theme05_distribution_discovery_data, mo):
    theme05_distribution_discovery_table = mo.ui.table(theme05_distribution_discovery_data, label="Submitted data")
    theme05_distribution_discovery_table
    return (theme05_distribution_discovery_table,)


@app.cell
def theme05_distribution_discovery_chart(alt, theme05_distribution_discovery_data, theme05_distribution_discovery_table, mo):
    _shown = (
        theme05_distribution_discovery_table.value if len(theme05_distribution_discovery_table.value) else theme05_distribution_discovery_data
    )
    theme05_distribution_discovery_chart = (
        alt.Chart(_shown)
        .mark_bar()
        .encode(
            x=alt.X("repo:N", title=None),
            y=alt.Y("scholar_guideline_compliance_pct:Q"),
        )
        .properties(title="Google Scholar guideline compliance, by repo")
    )
    mo.ui.altair_chart(theme05_distribution_discovery_chart)
    return


@app.cell
def outro(mo):
    mo.md("""
    ## Add or correct data

    Submit new data via the
    [05-distribution-discovery Issue Form](https://github.com/durf-project/dashboards/issues/new?template=05-distribution-discovery-data.yml).
    To fix a mistake in an existing row, edit `notebooks/05-distribution-discovery/data.csv`
    directly and open a PR -- see `AGENTS.md`.
    """)
    return


if __name__ == "__main__":
    app.run()
