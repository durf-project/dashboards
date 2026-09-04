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
app = marimo.App(width="full", app_title="6. NL Research Portal Update")


@app.cell
def imports():
    import altair as alt
    import pandas as pd
    import marimo as mo

    return alt, mo, pd


@app.cell
def intro(mo):
    mo.md("""
    # 6. NL Research Portal Update

    ## Goal

    Deliver a fully-functional, user-centered Netherlands Research Portal that serves as the primary discovery point for Dutch research outputs.

    ## What this dashboard monitors

    Portal adoption and release cadence: SURFconext single sign-on enablement per institution, the portal release version each institution is integrated with, and stakeholder needs-assessment feedback scores.

    ## Datapoints needed from participating institutions

    - Institution name
    - SURFconext SSO enabled (yes/no) and enablement date
    - Portal release version the institution is integrated with
    - Customer value / needs-assessment score, per survey round
    - Snapshot date

    ---

    **Status: live, usually sparse.** The table and chart below read
    `data.csv` straight from GitHub on every page load -- a new submission
    needs no site rebuild, just a page reload (GitHub's raw-file cache can
    lag a few minutes behind). Data arrives through the
    [06-nl-research-portal Issue Form](https://github.com/durf-project/dashboards/issues/new?template=06-nl-research-portal-data.yml),
    auto-ingested by `.github/workflows/ingest-submission.yml` -- no manual
    transcription step. `submitted_by` on each row is the submitter's GitHub
    username; sort or filter that column in the table to spot bad entries.
    Select rows in the table to filter the chart to just those. See
    `AGENTS.md` for the full pipeline.
    """)
    return


@app.cell
def theme06_nl_research_portal_data(pd):
    # Fetched fresh on every load from the data.csv that
    # .github/scripts/ingest_issue.py appends to -- see the intro above.
    # No validation happened on the way in, so coerce numeric columns with
    # errors="coerce" (bad values become NaN) rather than trust the input.
    _url = (
        "https://raw.githubusercontent.com/durf-project/dashboards/main/"
        "notebooks/06-nl-research-portal/data.csv"
    )
    _empty = pd.DataFrame(
        {
            "institution": pd.array([], dtype="string"),
            "surfconext_sso_enabled": pd.array([], dtype="string"),
            "surfconext_sso_enabled_date": pd.array([], dtype="string"),
            "portal_release_version": pd.array([], dtype="string"),
            "needs_assessment_score": pd.array([], dtype="Float64"),
            "snapshot_date": pd.array([], dtype="string"),
            "submitted_by": pd.array([], dtype="string"),
            "submitted_via_issue": pd.array([], dtype="Int64"),
            "submitted_at": pd.array([], dtype="string")
        }
    )
    try:
        theme06_nl_research_portal_data = pd.read_csv(_url, dtype="string")
    except Exception:
        theme06_nl_research_portal_data = _empty
    else:
        for _col, _dtype in {"needs_assessment_score": "Float64", "submitted_via_issue": "Int64"}.items():
            theme06_nl_research_portal_data[_col] = pd.to_numeric(
                theme06_nl_research_portal_data[_col], errors="coerce"
            ).astype(_dtype)
        theme06_nl_research_portal_data = theme06_nl_research_portal_data.reindex(columns=_empty.columns)
    return (theme06_nl_research_portal_data,)


@app.cell
def theme06_nl_research_portal_table(theme06_nl_research_portal_data, mo):
    theme06_nl_research_portal_table = mo.ui.table(theme06_nl_research_portal_data, label="Submitted data")
    theme06_nl_research_portal_table
    return (theme06_nl_research_portal_table,)


@app.cell
def theme06_nl_research_portal_chart(alt, theme06_nl_research_portal_data, theme06_nl_research_portal_table, mo):
    _shown = (
        theme06_nl_research_portal_table.value if len(theme06_nl_research_portal_table.value) else theme06_nl_research_portal_data
    )
    theme06_nl_research_portal_chart = (
        alt.Chart(_shown)
        .mark_bar()
        .encode(
            x=alt.X("institution:N", title=None),
            y=alt.Y("needs_assessment_score:Q"),
        )
        .properties(title="Needs-assessment score by institution")
    )
    mo.ui.altair_chart(theme06_nl_research_portal_chart)
    return


@app.cell
def outro(mo):
    mo.md("""
    ## Add or correct data

    Submit new data via the
    [06-nl-research-portal Issue Form](https://github.com/durf-project/dashboards/issues/new?template=06-nl-research-portal-data.yml).
    To fix a mistake in an existing row, edit `notebooks/06-nl-research-portal/data.csv`
    directly and open a PR -- see `AGENTS.md`.
    """)
    return


if __name__ == "__main__":
    app.run()
