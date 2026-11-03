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

## OpenAIRE tab

| File | What it does |
| --- | --- |
| `openaire.py` | The RPOs from `"nl-orgs".baseline`, matched on ROR to `openaire.organizations`, their datasources (`openaire.datasources`), harvesting interfaces (OpenAIRE Datasource Manager API) and counts of research products per datasource and projects per organisation per 5-year period (OpenAIRE Graph API, ~4,300 requests, within its 7,200/hour limit). Embeds the result in `../static.html`: `uv run openaire.py [oai-results.json]` |
| `oai_check.py` | Identify, ListMetadataFormats and ListSets on each OAI-PMH base URL, and which formats and sets of the OpenAIRE CRIS / literature guidelines are offered: `uv run oai_check.py oai-urls.json > oai-results.json`, then pass `oai-results.json` to `openaire.py`. |
| `oai-urls.json` | The 82 base URLs of the RPOs' CRIS systems and literature repositories (written by `openaire.py`). |

The OpenAIRE result tables in the DuckLake (`openaire.publications`, `datasets`,
`software`, `otherresearchproducts`) have empty `collectedfrom`, `organizations`
and `projects` columns (checked 3 November 2026), so they can't be counted per
datasource or organisation; the Graph API is used for that instead.
`oai_check.py` needs network access to the institutions' own servers (74 hosts).

What the endpoint check of 3 November 2026 found (`oai-results.json`):

- 38 of the 82 base URLs answered. For an `http://` URL the check tries
  `https://` first; 35 endpoints only answer over plain http, which the
  check environment's proxy does not pass, so they are "not checked" rather
  than broken. The rest failed with 403, 500, resets or TLS errors.
- The OpenAIRE Guidelines for CRIS Managers 1.1/1.2 ("Use of OAI-PMH") require
  a metadata prefix starting with `oai_cerif_openaire` and make all nine
  `openaire_cris_*` sets mandatory, "even if not all of them are populated".
  16 of the 18 reachable CRIS endpoints recognise all nine (Radboud's Metis
  misses funding, patents, events and equipments). Many sets are empty:
  equipments everywhere but Twente, funding and projects at most, and
  Leiden's endpoint has no records in any set. OpenAIRE harvests only
  publications (13), products (10) and patents (10) from these endpoints;
  persons and orgunits at one, projects and funding at none.
- Literature repositories: guidelines 4 recommend `oai_openaire` and no longer
  require a set (the `openaire` set is commented out of the 4.x text);
  the 3.0 profile requires `oai_dc` with set `openaire`.
- In the CERIF publication records of UvA, UU and RUG an author is only a
  reference (`<cerif:Person id="…">`); the ORCIDs are in the separate Person
  records (`openaire_cris_persons`: 29 of the first 100 at UvA, 7 at UU).
  That explains why `lake.cris.publications` has no ORCID: the DuckLake only
  harvests the publications set.
