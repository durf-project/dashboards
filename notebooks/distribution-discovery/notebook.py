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
app = marimo.App(width="full", app_title="Metadata Distribution & Discovery Optimization")


@app.cell
def imports():
    import altair as alt
    import pandas as pd
    import marimo as mo

    return alt, mo, pd


@app.cell
def intro(mo):
    mo.md("""
    # Metadata Distribution & Discovery Optimization

    **DURF theme 5.**

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

    **Status: placeholder.** The cells below produce an empty table with the
    columns this dashboard needs -- there is no harvesting or reporting
    pipeline from participating institutions yet. Once one exists, replace
    `distribution-discovery_placeholder_data` with a real query and the table/chart below
    will pick it up unchanged. See `AGENTS.md` for the convention this
    notebook follows.
    """)
    return


@app.cell
def distribution_discovery_placeholder_data(pd):
    # TODO: replace with a real query once institutions report this data.
    # Columns match "Datapoints needed from participating institutions" above.
    distribution_discovery_placeholder_data = pd.DataFrame(
        {
            "repo": pd.array([], dtype="string"),
            "scholar_guideline_compliance_pct": pd.array([], dtype="Float64"),
            "grey_lit_without_doi": pd.array([], dtype="Int64"),
            "grey_lit_doi_minted": pd.array([], dtype="Int64"),
            "snapshot_date": pd.array([], dtype="string")
        }
    )
    return (distribution_discovery_placeholder_data,)


@app.cell
def distribution_discovery_table(distribution_discovery_placeholder_data, mo):
    mo.ui.table(distribution_discovery_placeholder_data)
    return


@app.cell
def distribution_discovery_chart(alt, distribution_discovery_placeholder_data, mo):
    distribution_discovery_chart = (
        alt.Chart(distribution_discovery_placeholder_data)
        .mark_bar()
        .encode(
            x=alt.X("repo:N", title=None),
            y=alt.Y("scholar_guideline_compliance_pct:Q"),
        )
        .properties(title="Google Scholar guideline compliance, by repo (placeholder -- no data yet)")
    )
    mo.ui.altair_chart(distribution_discovery_chart)
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
