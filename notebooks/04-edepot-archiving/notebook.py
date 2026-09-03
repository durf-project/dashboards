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

    **Status: placeholder.** The cells below produce an empty table with the
    columns this dashboard needs -- there is no harvesting or reporting
    pipeline from participating institutions yet. Once one exists, replace
    `theme04_edepot_archiving_placeholder_data` with a real query and the table/chart below
    will pick it up unchanged. See `AGENTS.md` for the convention this
    notebook follows.
    """)
    return


@app.cell
def theme04_edepot_archiving_placeholder_data(pd):
    # TODO: replace with a real query once institutions report this data.
    # Columns match "Datapoints needed from participating institutions" above.
    theme04_edepot_archiving_placeholder_data = pd.DataFrame(
        {
            "repo": pd.array([], dtype="string"),
            "pdfs_in_repo": pd.array([], dtype="Int64"),
            "pdfs_in_edepot": pd.array([], dtype="Int64"),
            "urn_nbn_resolution_pct": pd.array([], dtype="Float64"),
            "snapshot_date": pd.array([], dtype="string")
        }
    )
    return (theme04_edepot_archiving_placeholder_data,)


@app.cell
def theme04_edepot_archiving_table(theme04_edepot_archiving_placeholder_data, mo):
    mo.ui.table(theme04_edepot_archiving_placeholder_data)
    return


@app.cell
def theme04_edepot_archiving_chart(alt, theme04_edepot_archiving_placeholder_data, mo):
    theme04_edepot_archiving_chart = (
        alt.Chart(theme04_edepot_archiving_placeholder_data)
        .mark_bar()
        .encode(
            x=alt.X("repo:N", title=None),
            y=alt.Y("pdfs_in_edepot:Q"),
        )
        .properties(title="PDFs archived in the e-Depot, by repo (placeholder -- no data yet)")
    )
    mo.ui.altair_chart(theme04_edepot_archiving_chart)
    return


@app.cell
def outro(mo):
    mo.md("""
    ## Next step

    Wire up the real data source for this theme (see `AGENTS.md` ->
    "Data access" for what's already available versus what has to come
    from participating institutions), then swap it into the placeholder
    query cell above.
    """)
    return


if __name__ == "__main__":
    app.run()
