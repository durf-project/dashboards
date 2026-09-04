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
app = marimo.App(width="full", app_title="2. Metadata Quality Improvement")


@app.cell
def imports():
    import altair as alt
    import pandas as pd
    import marimo as mo

    return alt, mo, pd


@app.cell
def intro(mo):
    mo.md("""
    # 2. Metadata Quality Improvement

    ## Goal

    Repository/CRIS systems have adopted the updated metadata- and exchange-standards for high-quality research metadata that comply with international guidelines and meet national requirements.

    ## What this dashboard monitors

    Two health signals per repo, over time: (1) validation results against the oai_cerif_openaire_NL / oai_dc_openaire_NL application profiles ("Compliancy health"), and (2) presence of ROR, ORCID and DOI identifiers in records ("PID health").

    ## Datapoints needed from participating institutions

    - Repository / CRIS name
    - Share of records passing OAI application-profile validation, with snapshot date
    - Share of records with a ROR-identified institution
    - Share of records with an ORCID for at least one author
    - Share of records with a DOI

    ---

    **Status: live, usually sparse.** The table and chart below read
    `data.csv` straight from GitHub on every page load -- a new submission
    needs no site rebuild, just a page reload (GitHub's raw-file cache can
    lag a few minutes behind). Data arrives through the
    [02-metadata-quality Issue Form](https://github.com/durf-project/dashboards/issues/new?template=02-metadata-quality-data.yml),
    auto-ingested by `.github/workflows/ingest-submission.yml` -- no manual
    transcription step. `submitted_by` on each row is the submitter's GitHub
    username; sort or filter that column in the table to spot bad entries.
    Select rows in the table to filter the chart to just those. See
    `AGENTS.md` for the full pipeline.
    """)
    return


@app.cell
def theme02_metadata_quality_data(pd):
    # Fetched fresh on every load from the data.csv that
    # .github/scripts/ingest_issue.py appends to -- see the intro above.
    # No validation happened on the way in, so coerce numeric columns with
    # errors="coerce" (bad values become NaN) rather than trust the input.
    _url = (
        "https://raw.githubusercontent.com/durf-project/dashboards/main/"
        "notebooks/02-metadata-quality/data.csv"
    )
    _empty = pd.DataFrame(
        {
            "repo": pd.array([], dtype="string"),
            "compliance_pct": pd.array([], dtype="Float64"),
            "ror_pct": pd.array([], dtype="Float64"),
            "orcid_pct": pd.array([], dtype="Float64"),
            "doi_pct": pd.array([], dtype="Float64"),
            "snapshot_date": pd.array([], dtype="string"),
            "submitted_by": pd.array([], dtype="string"),
            "submitted_via_issue": pd.array([], dtype="Int64"),
            "submitted_at": pd.array([], dtype="string")
        }
    )
    try:
        theme02_metadata_quality_data = pd.read_csv(_url, dtype="string")
    except Exception:
        theme02_metadata_quality_data = _empty
    else:
        for _col, _dtype in {"compliance_pct": "Float64", "ror_pct": "Float64", "orcid_pct": "Float64", "doi_pct": "Float64", "submitted_via_issue": "Int64"}.items():
            theme02_metadata_quality_data[_col] = pd.to_numeric(
                theme02_metadata_quality_data[_col], errors="coerce"
            ).astype(_dtype)
        theme02_metadata_quality_data = theme02_metadata_quality_data.reindex(columns=_empty.columns)
    return (theme02_metadata_quality_data,)


@app.cell
def theme02_metadata_quality_table(theme02_metadata_quality_data, mo):
    theme02_metadata_quality_table = mo.ui.table(theme02_metadata_quality_data, label="Submitted data")
    theme02_metadata_quality_table
    return (theme02_metadata_quality_table,)


@app.cell
def theme02_metadata_quality_chart(alt, theme02_metadata_quality_data, theme02_metadata_quality_table, mo):
    _shown = (
        theme02_metadata_quality_table.value if len(theme02_metadata_quality_table.value) else theme02_metadata_quality_data
    )
    theme02_metadata_quality_chart = (
        alt.Chart(_shown)
        .mark_bar()
        .encode(
            x=alt.X("repo:N", title=None),
            y=alt.Y("compliance_pct:Q"),
        )
        .properties(title="OAI application-profile compliance by repo")
    )
    mo.ui.altair_chart(theme02_metadata_quality_chart)
    return


@app.cell
def outro(mo):
    mo.md("""
    ## Add or correct data

    Submit new data via the
    [02-metadata-quality Issue Form](https://github.com/durf-project/dashboards/issues/new?template=02-metadata-quality-data.yml).
    To fix a mistake in an existing row, edit `notebooks/02-metadata-quality/data.csv`
    directly and open a PR -- see `AGENTS.md`.
    """)
    return


if __name__ == "__main__":
    app.run()
