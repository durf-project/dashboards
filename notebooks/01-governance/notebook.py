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

    **Status: placeholder.** The cells below produce an empty table with the
    columns this dashboard needs -- there is no harvesting or reporting
    pipeline from participating institutions yet. Once one exists, replace
    `theme01_governance_placeholder_data` with a real query and the table/chart below
    will pick it up unchanged. See `AGENTS.md` for the convention this
    notebook follows.
    """)
    return


@app.cell
def theme01_governance_placeholder_data(pd):
    # TODO: replace with a real query once institutions report this data.
    # Columns match "Datapoints needed from participating institutions" above.
    theme01_governance_placeholder_data = pd.DataFrame(
        {
            "institution": pd.array([], dtype="string"),
            "nameco_status": pd.array([], dtype="string"),
            "rule_book_signed": pd.array([], dtype="boolean"),
            "symposium_attendance_2026": pd.array([], dtype="Int64"),
            "last_governance_review": pd.array([], dtype="string")
        }
    )
    return (theme01_governance_placeholder_data,)


@app.cell
def theme01_governance_table(theme01_governance_placeholder_data, mo):
    mo.ui.table(theme01_governance_placeholder_data)
    return


@app.cell
def theme01_governance_chart(alt, theme01_governance_placeholder_data, mo):
    theme01_governance_chart = (
        alt.Chart(theme01_governance_placeholder_data)
        .mark_bar()
        .encode(
            x=alt.X("institution:N", title=None),
            y=alt.Y("symposium_attendance_2026:Q"),
        )
        .properties(title="Symposium attendance by institution (placeholder -- no data yet)")
    )
    mo.ui.altair_chart(theme01_governance_chart)
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
