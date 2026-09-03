# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "marimo",
#     "duckdb>=1.5.2",
#     "altair",
#     "pandas",
#     "pyarrow",
# ]
# ///

import marimo

__generated_with = "0.20.4"
app = marimo.App(width="full", app_title="{{TITLE}}")


@app.cell
async def wasm_dependencies():
    # WASM export (uvx marimo export html-wasm) runs inside Pyodide in the
    # browser. duckdb and its extensions aren't bundled by default there,
    # so install them at runtime via micropip. On a normal desktop run
    # this cell is a no-op -- the PEP 723 header above already handles it.
    import sys

    if "pyodide" in sys.modules:
        import micropip

        _ = await micropip.install(["duckdb"])
    return


@app.cell
def imports():
    import altair as alt
    import duckdb
    import marimo as mo

    return alt, duckdb, mo


@app.cell
def intro(mo):
    mo.md("""
    # {{TITLE}}

    Your work starts here. The query below already produces a chart --
    run this notebook and you should see one within a few seconds,
    no edits needed.
    """)
    return


@app.cell
def duckdb_connection(duckdb):
    # Connects read-only to the SURF ORI DuckLake catalog. No credentials
    # needed -- this bucket is public for reads.
    con = duckdb.connect()
    con.execute("INSTALL ducklake; LOAD ducklake;")
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute("""
        ATTACH 'ducklake:https://objectstore.surf.nl/cea01a7216d64348b7e51e5f3fc1901d:sprouts/catalog.ducklake'
        AS lake (READ_ONLY, CREATE_IF_NOT_EXISTS false)
    """)
    return (con,)


@app.cell
def dutch_institutions_query(con, mo):
    # A native marimo SQL cell: it's still `mo.sql()` under the hood, but
    # keep it to *only* the query -- no Python branching or string-building
    # in here. That's what makes it show up as a SQL cell when you open this
    # in `marimo edit`, and it's what keeps `marimo check` happy.
    #
    # Small and fast: a count of Dutch institutions in OpenAlex, by type.
    # Filtered and aggregated on a 120K-row table -- never scan
    # openalex.works unfiltered, it's 364M rows and will hang.
    dutch_institutions = mo.sql(
        f"""
        SELECT type, COUNT(*) AS institution_count
        FROM lake.openalex.institutions
        WHERE country_code = 'NL'
        GROUP BY type
        ORDER BY institution_count DESC
        """,
        engine=con,
        output=False,
    )
    return (dutch_institutions,)


@app.cell
def dutch_institutions_table(dutch_institutions, mo):
    # The Python side of the same result: a separate cell, so the SQL cell
    # above stays pure SQL and this stays pure Python.
    mo.ui.table(dutch_institutions)
    return


@app.cell
def dutch_institutions_chart(alt, dutch_institutions, mo):
    chart = (
        alt.Chart(dutch_institutions)
        .mark_bar()
        .encode(
            x=alt.X("institution_count:Q", title="Institutions"),
            y=alt.Y("type:N", sort="-x", title=None),
        )
        .properties(title="Dutch institutions in OpenAlex, by type")
    )
    mo.ui.altair_chart(chart)
    return


@app.cell
def outro(mo):
    mo.md("""
    ## Try it yourself

    Change the query above, or ask your agent something like:
    *"Show me the same chart but for Germany instead of the Netherlands."*
    """)
    return


# --- Stated proxy example (commented out) ----------------------------------
# Strategic questions rarely have a direct column to query. This shows the
# pattern for using a proxy honestly: name it, and say what it misses.
# Uncomment and adapt if your question needs one.
#
# @app.cell
# def sdg_proxy_query(con, mo):
#     # PROXY: topic classification stands in for "SDG-related research".
#     # There is no ground-truth SDG field in OpenAlex. This undercounts
#     # projects whose SDG relevance isn't visible in the abstract, and
#     # may overcount generic environmental topics that aren't really
#     # SDG-aligned. Say this in your own notebook wherever you use a
#     # proxy -- naming it is a stronger result than hiding it.
#     sdg_proxy = mo.sql(
#         f"""
#         SELECT sdg.display_name, COUNT(*) AS work_count
#         FROM lake.openalex.works w,
#              UNNEST(w.sustainable_development_goals) AS sdg
#         WHERE w.publication_year >= 2020
#         GROUP BY sdg.display_name
#         ORDER BY work_count DESC
#         LIMIT 10
#         """,
#         engine=con,
#         output=False,
#     )
#     return (sdg_proxy,)
#
#
# @app.cell
# def sdg_proxy_table(mo, sdg_proxy):
#     mo.ui.table(sdg_proxy)
#     return


if __name__ == "__main__":
    app.run()
