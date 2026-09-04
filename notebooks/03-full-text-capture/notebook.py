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
app = marimo.App(width="full", app_title="3. Full Text Capture")


@app.cell
def imports():
    import altair as alt
    import pandas as pd
    import marimo as mo

    return alt, mo, pd


@app.cell
def intro(mo):
    mo.md("""
    # 3. Full Text Capture

    ## Goal

    Comprehensive full-text availability in Dutch repository/CRIS systems, primarily for preservation, and secondarily for text-mining, AI usage and Taverne-mechanisms.

    ## What this dashboard monitors

    "Digital sovereignty health": the ratio of metadata records that link to a full-text PDF hosted on the institution's own domain (rather than only a publisher's), per repo, over time.

    ## Datapoints needed from participating institutions

    - Repository / CRIS name
    - Total metadata records
    - Records with a full-text PDF link hosted on the institution's own domain
    - Snapshot date

    ---

    **Status: live, usually sparse.** The table and chart below read
    `data.csv` straight from GitHub on every page load -- a new submission
    needs no site rebuild, just a page reload (GitHub's raw-file cache can
    lag a few minutes behind). Data arrives through the
    [03-full-text-capture Issue Form](https://github.com/durf-project/dashboards/issues/new?template=03-full-text-capture-data.yml),
    auto-ingested by `.github/workflows/ingest-submission.yml` -- no manual
    transcription step. `submitted_by` on each row is the submitter's GitHub
    username; sort or filter that column in the table to spot bad entries.
    Select rows in the table to filter the chart to just those. See
    `AGENTS.md` for the full pipeline.
    """)
    return


@app.cell
def theme03_full_text_capture_data(pd):
    # Fetched fresh on every load from the data.csv that
    # .github/scripts/ingest_issue.py appends to -- see the intro above.
    # No validation happened on the way in, so coerce numeric columns with
    # errors="coerce" (bad values become NaN) rather than trust the input.
    _url = (
        "https://raw.githubusercontent.com/durf-project/dashboards/main/"
        "notebooks/03-full-text-capture/data.csv"
    )
    _empty = pd.DataFrame(
        {
            "repo": pd.array([], dtype="string"),
            "total_records": pd.array([], dtype="Int64"),
            "records_with_local_pdf": pd.array([], dtype="Int64"),
            "snapshot_date": pd.array([], dtype="string"),
            "submitted_by": pd.array([], dtype="string"),
            "submitted_via_issue": pd.array([], dtype="Int64"),
            "submitted_at": pd.array([], dtype="string")
        }
    )
    try:
        theme03_full_text_capture_data = pd.read_csv(_url, dtype="string")
    except Exception:
        theme03_full_text_capture_data = _empty
    else:
        for _col, _dtype in {"total_records": "Int64", "records_with_local_pdf": "Int64", "submitted_via_issue": "Int64"}.items():
            theme03_full_text_capture_data[_col] = pd.to_numeric(
                theme03_full_text_capture_data[_col], errors="coerce"
            ).astype(_dtype)
        theme03_full_text_capture_data = theme03_full_text_capture_data.reindex(columns=_empty.columns)
    return (theme03_full_text_capture_data,)


@app.cell
def theme03_full_text_capture_table(theme03_full_text_capture_data, mo):
    theme03_full_text_capture_table = mo.ui.table(theme03_full_text_capture_data, label="Submitted data")
    theme03_full_text_capture_table
    return (theme03_full_text_capture_table,)


@app.cell
def theme03_full_text_capture_chart(alt, theme03_full_text_capture_data, theme03_full_text_capture_table, mo):
    _shown = (
        theme03_full_text_capture_table.value if len(theme03_full_text_capture_table.value) else theme03_full_text_capture_data
    )
    theme03_full_text_capture_chart = (
        alt.Chart(_shown)
        .mark_bar()
        .encode(
            x=alt.X("repo:N", title=None),
            y=alt.Y("records_with_local_pdf:Q"),
        )
        .properties(title="Records with a locally-hosted full text, by repo")
    )
    mo.ui.altair_chart(theme03_full_text_capture_chart)
    return


@app.cell
def outro(mo):
    mo.md("""
    ## Add or correct data

    Submit new data via the
    [03-full-text-capture Issue Form](https://github.com/durf-project/dashboards/issues/new?template=03-full-text-capture-data.yml).
    To fix a mistake in an existing row, edit `notebooks/03-full-text-capture/data.csv`
    directly and open a PR -- see `AGENTS.md`.
    """)
    return


if __name__ == "__main__":
    app.run()
