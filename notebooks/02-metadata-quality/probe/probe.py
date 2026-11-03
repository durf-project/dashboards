# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb>=1.5.2"]
# ///
"""
Feasibility probe for the DURF Metadata Monitor (theme 2).

Step 1 of the plan on the dashboard's "Plan & feasibility" tab:

1. lists every table in the ORI DuckLake `cris` schema (are there persons,
   orgunits or projects next to publications?);
2. for each table, prints the columns whose (nested) type mentions DOI, ORCID,
   ROR, abstract, funding/project, access or corresponding author, so the
   "To verify" rows can be settled;
3. for lake.cris.publications, counts presence and validity per institution for
   the fields whose column is documented (DOI, abstract, open access status),
   using the checks in checks.sql.

Usage (needs network access to objectstore.surf.nl):

    uv run notebooks/02-metadata-quality/probe/probe.py > probe-output.json
"""

import json
import os
import pathlib
import re

import duckdb

CATALOG = "ducklake:https://objectstore.surf.nl/cea01a7216d64348b7e51e5f3fc1901d:sprouts/catalog.ducklake"
# PROBE_ATTACH=/path/to/file.duckdb runs the same probe against a local database (used for testing)
ATTACH_TARGET = os.environ.get("PROBE_ATTACH", CATALOG)
KEYWORDS = re.compile(r"doi|orcid|ror|isni|scopus|abstract|funding|fundref|funder|project|originatesfrom|access|corresponding|identifier", re.I)


def main() -> None:
    con = duckdb.connect()
    options = "READ_ONLY"
    if ATTACH_TARGET.startswith("ducklake:"):
        for ext in ("ducklake", "httpfs"):
            con.execute(f"INSTALL {ext}; LOAD {ext};")
        options += ", CREATE_IF_NOT_EXISTS false"
    con.execute(f"ATTACH '{ATTACH_TARGET}' AS lake ({options})")
    con.execute((pathlib.Path(__file__).parent / "checks.sql").read_text())

    out: dict = {"tables": {}}
    tables = [r[0] for r in con.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_catalog = 'lake' AND table_schema = 'cris' ORDER BY 1"
    ).fetchall()]
    for t in tables:
        cols = con.execute(
            "SELECT column_name, data_type FROM information_schema.columns "
            "WHERE table_catalog = 'lake' AND table_schema = 'cris' AND table_name = ? ORDER BY ordinal_position", [t]
        ).fetchall()
        out["tables"][t] = {
            "columns": [c[0] for c in cols],
            # nested STRUCT types are one long string; keep the matching keywords per column
            "candidate_fields": {c[0]: sorted(set(m.lower() for m in KEYWORDS.findall(c[0] + " " + c[1]))) for c in cols if KEYWORDS.search(c[0] + " " + c[1])},
        }

    if "publications" in tables:
        rows = con.execute("""
            SELECT repository_info.institution AS institution,
                   COUNT(*) AS n,
                   COUNT(*) FILTER (WHERE nullif(trim("cerif:DOI"), '') IS NOT NULL) AS doi_present,
                   COUNT(*) FILTER (WHERE doi_ok("cerif:DOI")) AS doi_valid,
                   COUNT(*) FILTER (WHERE len("cerif:Abstract") > 0) AS abstract_present,
                   COUNT(*) FILTER (WHERE abstract_ok("cerif:Abstract"[1]."#text", "cerif:Title"[1]."#text")) AS abstract_valid,
                   COUNT(*) FILTER (WHERE nullif(trim("ar:Access"), '') IS NOT NULL) AS oa_present,
                   COUNT(*) FILTER (WHERE coar_access_ok("ar:Access")) AS oa_valid
            FROM lake.cris.publications
            GROUP BY ALL ORDER BY n DESC
        """)
        names = [d[0] for d in rows.description]
        out["publications_by_institution"] = [dict(zip(names, r)) for r in rows.fetchall()]
        out["doi_problems"] = dict(con.execute(
            'SELECT doi_problem("cerif:DOI"), COUNT(*) FROM lake.cris.publications GROUP BY 1 ORDER BY 2 DESC'
        ).fetchall())

    print(json.dumps(out, indent=2, default=str))


if __name__ == "__main__":
    main()
