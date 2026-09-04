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
app = marimo.App(width="full", app_title="4. KB National Library e-Depot Archiving")


@app.cell
def imports():
    import altair as alt
    import pandas as pd
    import marimo as mo

    return alt, mo, pd


@app.cell
def intro(mo):
    mo.md("""
    # 4. KB National Library e-Depot Archiving

    ## Goal

    Comprehensive preservation achieved of Dutch scientific output in the KB e-Depot.

    ## What this dashboard monitors

    "Backup health": the ratio of PDFs archived in the KB e-Depot versus PDFs present in the source repository, per repo, over time -- plus whether the URN:NBN resolver is functioning for the institution's identifiers.

    ## Datapoints needed from participating institutions

    - Repository / CRIS name
    - PDFs present in the source repository
    - PDFs confirmed archived in the KB e-Depot
    - URN:NBN resolution success rate for the institution's identifiers
    - Snapshot date

    ---

    **Status: live, usually sparse.** The table and chart below read
    `data.csv` straight from GitHub on every page load -- a new submission
    needs no site rebuild, just a page reload (GitHub's raw-file cache can
    lag a few minutes behind). Data arrives through the
    [04-edepot-archiving Issue Form](https://github.com/durf-project/dashboards/issues/new?template=04-edepot-archiving-data.yml),
    auto-ingested by `.github/workflows/ingest-submission.yml` -- no manual
    transcription step. `submitted_by` on each row is the submitter's GitHub
    username; sort or filter that column in the table to spot bad entries.
    Select rows in the table to filter the chart to just those. See
    `AGENTS.md` for the full pipeline.
    """)
    return


@app.cell
def theme04_edepot_archiving_data(pd):
    # Fetched fresh on every load from the data.csv that
    # .github/scripts/ingest_issue.py appends to -- see the intro above.
    # No validation happened on the way in, so coerce numeric columns with
    # errors="coerce" (bad values become NaN) rather than trust the input.
    _url = (
        "https://raw.githubusercontent.com/durf-project/dashboards/main/"
        "notebooks/04-edepot-archiving/data.csv"
    )
    _empty = pd.DataFrame(
        {
            "repo": pd.array([], dtype="string"),
            "pdfs_in_repo": pd.array([], dtype="Int64"),
            "pdfs_in_edepot": pd.array([], dtype="Int64"),
            "urn_nbn_resolution_pct": pd.array([], dtype="Float64"),
            "snapshot_date": pd.array([], dtype="string"),
            "submitted_by": pd.array([], dtype="string"),
            "submitted_via_issue": pd.array([], dtype="Int64"),
            "submitted_at": pd.array([], dtype="string")
        }
    )
    try:
        theme04_edepot_archiving_data = pd.read_csv(_url, dtype="string")
    except Exception:
        theme04_edepot_archiving_data = _empty
    else:
        for _col, _dtype in {"pdfs_in_repo": "Int64", "pdfs_in_edepot": "Int64", "urn_nbn_resolution_pct": "Float64", "submitted_via_issue": "Int64"}.items():
            theme04_edepot_archiving_data[_col] = pd.to_numeric(
                theme04_edepot_archiving_data[_col], errors="coerce"
            ).astype(_dtype)
        theme04_edepot_archiving_data = theme04_edepot_archiving_data.reindex(columns=_empty.columns)
    return (theme04_edepot_archiving_data,)


@app.cell
def theme04_edepot_archiving_table(theme04_edepot_archiving_data, mo):
    theme04_edepot_archiving_table = mo.ui.table(theme04_edepot_archiving_data, label="Submitted data")
    theme04_edepot_archiving_table
    return (theme04_edepot_archiving_table,)


@app.cell
def theme04_edepot_archiving_chart(alt, theme04_edepot_archiving_data, theme04_edepot_archiving_table, mo):
    _shown = (
        theme04_edepot_archiving_table.value if len(theme04_edepot_archiving_table.value) else theme04_edepot_archiving_data
    )
    theme04_edepot_archiving_chart = (
        alt.Chart(_shown)
        .mark_bar()
        .encode(
            x=alt.X("repo:N", title=None),
            y=alt.Y("pdfs_in_edepot:Q"),
        )
        .properties(title="PDFs archived in the e-Depot, by repo")
    )
    mo.ui.altair_chart(theme04_edepot_archiving_chart)
    return


@app.cell
def outro(mo):
    mo.md("""
    ## Add or correct data

    Submit new data via the
    [04-edepot-archiving Issue Form](https://github.com/durf-project/dashboards/issues/new?template=04-edepot-archiving-data.yml).
    To fix a mistake in an existing row, edit `notebooks/04-edepot-archiving/data.csv`
    directly and open a PR -- see `AGENTS.md`.
    """)
    return


if __name__ == "__main__":
    app.run()
