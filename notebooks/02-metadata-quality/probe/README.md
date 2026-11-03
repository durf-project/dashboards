# Metadata Monitor probe

The data work behind the theme 2 **DURF Metadata Monitor** (`../static.html`,
published as `02-metadata-quality.html`). Its Publications tab is a real
snapshot of `lake.cris.publications`; the Persons, Organisations and Projects
tabs are mock-ups, because those datasets are not in the ORI DuckLake.

| File | What it does |
| --- | --- |
| `checks.sql` | DuckDB macros for the validity checks: DOI (with a reason for failures), ORCID and ISNI (pattern + ISO 7064 MOD 11-2 check digit), ROR, COAR access rights, Crossref Funder ID, RAiD, ISO dates, abstract length. |
| `test_checks.py` | 29 test cases for those macros: `uv run --with duckdb python -I test_checks.py` |
| `probe.py` | Lists the tables in the `cris` schema and the columns that look like DOI/ORCID/ROR/abstract/funding/access fields, and counts presence + validity per institution: `uv run probe.py > probe-output.json` |
| `extract.py` | Builds the publication snapshot (institution x year x publication type, 1995-2025) and embeds it in `../static.html`: `uv run extract.py` |
| `lake.py` | Shared connection to the DuckLake for `probe.py` and `extract.py`. |

Refreshing the dashboard is `uv run extract.py`, then commit `static.html`.

Both scripts need network access to `objectstore.surf.nl`, and DuckDB needs to
fetch its `ducklake` and `httpfs` extensions. DuckDB downloads extensions over
plain http, which some proxies refuse; in that case download
`https://extensions.duckdb.org/v<duckdb version>/<platform>/<name>.duckdb_extension.gz`,
unzip them into a folder and set `DUCKDB_EXTENSIONS=/that/folder`. `HTTPS_PROXY`
is passed on to DuckDB. `PROBE_ATTACH=/path/to/file.duckdb` runs either script
against a local database instead (for testing).

What the schema check of 3 November 2026 found:

- the `cris` schema has a single table, `publications`: no CERIF Persons, OrgUnits or Projects;
- authors (`cerif:Person`) carry only an internal `@id` and a name, affiliations
  (`cerif:OrgUnit`) only `@id`, acronym and name: no ORCID, no ROR;
- linked projects (`cerif:OriginatesFrom/cerif:Project`) carry only `@id` and a
  title: no grant number, no funder;
- there is no corresponding-author element.
