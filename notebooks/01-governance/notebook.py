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
app = marimo.App(width="full", app_title="1. Governance of the Federation and NL Research Portal")


@app.cell
def imports():
    import altair as alt
    import pandas as pd
    import marimo as mo

    return alt, mo, pd


@app.cell
def intro(mo):
    mo.md("""
    # 1. Governance of the Federation and NL Research Portal

    ## Goal

    A sustainable governance framework established for the Dutch federated research information ecosystem, including parties maintaining Repository/CRIS systems, the KB e-Depot and the OpenAIRE Graph.

    ## What this dashboard monitors

    Federation membership and agreement status across participating institutions -- NaMeCo consortium membership, signed Federation Rule Book agreements, and governance framework review cadence -- plus attendance at the annual National Symposium / General Assembly.

    ## Datapoints needed from participating institutions

    - Institution name and NaMeCo membership status (member / pending / not joined)
    - Federation Rule Book agreement signed (yes/no) and signature date
    - Attendance at the National Symposium / General Assembly, per year
    - Date of the most recent governance framework review affecting the institution

    ---

    **Status: live, usually sparse.** The table and chart below read
    `data.csv` straight from GitHub on every page load -- a new submission
    needs no site rebuild, just a page reload (GitHub's raw-file cache can
    lag a few minutes behind). Data arrives through the
    [01-governance Issue Form](https://github.com/durf-project/dashboards/issues/new?template=01-governance-data.yml),
    auto-ingested by `.github/workflows/ingest-submission.yml` -- no manual
    transcription step. `submitted_by` on each row is the submitter's GitHub
    username; sort or filter that column in the table to spot bad entries.
    Select rows in the table to filter the chart to just those. See
    `AGENTS.md` for the full pipeline.
    """)
    return


@app.cell
def theme01_governance_data(pd):
    # Fetched fresh on every load from the data.csv that
    # .github/scripts/ingest_issue.py appends to -- see the intro above.
    # No validation happened on the way in, so coerce numeric columns with
    # errors="coerce" (bad values become NaN) rather than trust the input.
    _url = (
        "https://raw.githubusercontent.com/durf-project/dashboards/main/"
        "notebooks/01-governance/data.csv"
    )
    _empty = pd.DataFrame(
        {
            "institution": pd.array([], dtype="string"),
            "nameco_status": pd.array([], dtype="string"),
            "rule_book_signed": pd.array([], dtype="string"),
            "rule_book_signed_date": pd.array([], dtype="string"),
            "symposium_attendance": pd.array([], dtype="Int64"),
            "last_governance_review": pd.array([], dtype="string"),
            "submitted_by": pd.array([], dtype="string"),
            "submitted_via_issue": pd.array([], dtype="Int64"),
            "submitted_at": pd.array([], dtype="string")
        }
    )
    try:
        theme01_governance_data = pd.read_csv(_url, dtype="string")
    except Exception:
        theme01_governance_data = _empty
    else:
        for _col, _dtype in {"symposium_attendance": "Int64", "submitted_via_issue": "Int64"}.items():
            theme01_governance_data[_col] = pd.to_numeric(
                theme01_governance_data[_col], errors="coerce"
            ).astype(_dtype)
        theme01_governance_data = theme01_governance_data.reindex(columns=_empty.columns)
    return (theme01_governance_data,)


@app.cell
def theme01_governance_table(theme01_governance_data, mo):
    theme01_governance_table = mo.ui.table(theme01_governance_data, label="Submitted data")
    theme01_governance_table
    return (theme01_governance_table,)


@app.cell
def theme01_governance_chart(alt, theme01_governance_data, theme01_governance_table, mo):
    _shown = (
        theme01_governance_table.value if len(theme01_governance_table.value) else theme01_governance_data
    )
    theme01_governance_chart = (
        alt.Chart(_shown)
        .mark_bar()
        .encode(
            x=alt.X("institution:N", title=None),
            y=alt.Y("symposium_attendance:Q"),
        )
        .properties(title="Symposium attendance by institution")
    )
    mo.ui.altair_chart(theme01_governance_chart)
    return


@app.cell
def outro(mo):
    mo.md("""
    ## Add or correct data

    Submit new data via the
    [01-governance Issue Form](https://github.com/durf-project/dashboards/issues/new?template=01-governance-data.yml).
    To fix a mistake in an existing row, edit `notebooks/01-governance/data.csv`
    directly and open a PR -- see `AGENTS.md`.
    """)
    return


if __name__ == "__main__":
    app.run()
