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

    **Status: placeholder.** The cells below produce an empty table with the
    columns this dashboard needs -- there is no harvesting or reporting
    pipeline from participating institutions yet. Once one exists, replace
    `theme06_nl_research_portal_placeholder_data` with a real query and the table/chart below
    will pick it up unchanged. See `AGENTS.md` for the convention this
    notebook follows.
    """)
    return


@app.cell
def theme06_nl_research_portal_placeholder_data(pd):
    # TODO: replace with a real query once institutions report this data.
    # Columns match "Datapoints needed from participating institutions" above.
    theme06_nl_research_portal_placeholder_data = pd.DataFrame(
        {
            "institution": pd.array([], dtype="string"),
            "surfconext_sso_enabled": pd.array([], dtype="boolean"),
            "portal_release_version": pd.array([], dtype="string"),
            "needs_assessment_score": pd.array([], dtype="Float64"),
            "snapshot_date": pd.array([], dtype="string")
        }
    )
    return (theme06_nl_research_portal_placeholder_data,)


@app.cell
def theme06_nl_research_portal_table(theme06_nl_research_portal_placeholder_data, mo):
    mo.ui.table(theme06_nl_research_portal_placeholder_data)
    return


@app.cell
def theme06_nl_research_portal_chart(alt, theme06_nl_research_portal_placeholder_data, mo):
    theme06_nl_research_portal_chart = (
        alt.Chart(theme06_nl_research_portal_placeholder_data)
        .mark_bar()
        .encode(
            x=alt.X("institution:N", title=None),
            y=alt.Y("needs_assessment_score:Q"),
        )
        .properties(title="Needs-assessment score by institution (placeholder -- no data yet)")
    )
    mo.ui.altair_chart(theme06_nl_research_portal_chart)
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
