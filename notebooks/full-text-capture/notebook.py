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
app = marimo.App(width="full", app_title="Full Text Capture")


@app.cell
def imports():
    import altair as alt
    import pandas as pd
    import marimo as mo

    return alt, mo, pd


@app.cell
def intro(mo):
    mo.md("""
    # Full Text Capture

    **DURF theme 3.**

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

    **Status: placeholder.** The cells below produce an empty table with the
    columns this dashboard needs -- there is no harvesting or reporting
    pipeline from participating institutions yet. Once one exists, replace
    `full-text-capture_placeholder_data` with a real query and the table/chart below
    will pick it up unchanged. See `AGENTS.md` for the convention this
    notebook follows.
    """)
    return


@app.cell
def full_text_capture_placeholder_data(pd):
    # TODO: replace with a real query once institutions report this data.
    # Columns match "Datapoints needed from participating institutions" above.
    full_text_capture_placeholder_data = pd.DataFrame(
        {
            "repo": pd.array([], dtype="string"),
            "total_records": pd.array([], dtype="Int64"),
            "records_with_local_pdf": pd.array([], dtype="Int64"),
            "snapshot_date": pd.array([], dtype="string")
        }
    )
    return (full_text_capture_placeholder_data,)


@app.cell
def full_text_capture_table(full_text_capture_placeholder_data, mo):
    mo.ui.table(full_text_capture_placeholder_data)
    return


@app.cell
def full_text_capture_chart(alt, full_text_capture_placeholder_data, mo):
    full_text_capture_chart = (
        alt.Chart(full_text_capture_placeholder_data)
        .mark_bar()
        .encode(
            x=alt.X("repo:N", title=None),
            y=alt.Y("records_with_local_pdf:Q"),
        )
        .properties(title="Records with a locally-hosted full text, by repo (placeholder -- no data yet)")
    )
    mo.ui.altair_chart(full_text_capture_chart)
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
