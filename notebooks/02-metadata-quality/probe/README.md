# Metadata Monitor probe

Feasibility work behind the theme 2 **DURF Metadata Monitor** (`../static.html`,
published as `02-metadata-quality.html`). That page is a proof of concept with
**mock data**; these files are what turns it into a real one.

| File | What it does |
| --- | --- |
| `checks.sql` | DuckDB macros for the validity checks: DOI (Crossref pattern, with a reason for failures), ORCID and ISNI (pattern + ISO 7064 MOD 11-2 check digit), ROR, COAR access rights, Crossref Funder ID, RAiD, ISO dates, abstract length. |
| `test_checks.py` | 26 test cases for those macros: `uv run --with duckdb python -I test_checks.py` |
| `probe.py` | Lists the tables in the ORI DuckLake `cris` schema, the columns that look like DOI/ORCID/ROR/abstract/funding/access fields, and counts presence + validity per institution for the documented publication fields: `uv run probe.py > probe-output.json` |

`probe.py` needs network access to `objectstore.surf.nl` (and to
`extensions.duckdb.org` for the `ducklake`/`httpfs` extensions). To try it
without that, point it at a local DuckDB file with a `cris.publications`
table: `PROBE_ATTACH=/path/to/file.duckdb uv run probe.py`.

Next steps are on the dashboard's **Plan & feasibility** tab.
