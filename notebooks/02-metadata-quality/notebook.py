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

    **Status: placeholder.** The cells below produce an empty table with the
    columns this dashboard needs -- there is no harvesting or reporting
    pipeline from participating institutions yet. Once one exists, replace
    `theme02_metadata_quality_placeholder_data` with a real query and the table/chart below
    will pick it up unchanged. See `AGENTS.md` for the convention this
    notebook follows.
    """)
    return


@app.cell
def theme02_metadata_quality_placeholder_data(pd):
    # TODO: replace with a real query once institutions report this data.
    # Columns match "Datapoints needed from participating institutions" above.
    theme02_metadata_quality_placeholder_data = pd.DataFrame(
        {
            "repo": pd.array([], dtype="string"),
            "compliance_pct": pd.array([], dtype="Float64"),
            "ror_pct": pd.array([], dtype="Float64"),
            "orcid_pct": pd.array([], dtype="Float64"),
            "doi_pct": pd.array([], dtype="Float64"),
            "snapshot_date": pd.array([], dtype="string")
        }
    )
    return (theme02_metadata_quality_placeholder_data,)


@app.cell
def theme02_metadata_quality_table(theme02_metadata_quality_placeholder_data, mo):
    mo.ui.table(theme02_metadata_quality_placeholder_data)
    return


@app.cell
def theme02_metadata_quality_chart(alt, theme02_metadata_quality_placeholder_data, mo):
    theme02_metadata_quality_chart = (
        alt.Chart(theme02_metadata_quality_placeholder_data)
        .mark_bar()
        .encode(
            x=alt.X("repo:N", title=None),
            y=alt.Y("compliance_pct:Q"),
        )
        .properties(title="OAI application-profile compliance by repo (placeholder -- no data yet)")
    )
    mo.ui.altair_chart(theme02_metadata_quality_chart)
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
