# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb>=1.5.2"]
# ///
"""
Extract the publication snapshot behind the DURF Metadata Monitor and embed it
in ../static.html (the <script id="dashboard-data"> element), the same static
snapshot approach as the Full Text Monitor.

    uv run notebooks/02-metadata-quality/probe/extract.py

Aggregates lake.cris.publications (publication years 1995-2025) by institution x
year x publication type, with presence and validity counts per field from
checks.sql, plus one real example value per kind of format error.
"""

import datetime
import json
import pathlib
import re

from lake import connect

PAGE = pathlib.Path(__file__).parent.parent / "static.html"
PUBTYPES = {  # same mapping as the Full Text Monitor
    "http://purl.org/coar/resource_type/c_6501": "Journal article",
    "http://purl.org/coar/resource_type/c_0640": "Journal",
    "http://purl.org/coar/resource_type/c_3248": "Book part",
    "http://purl.org/coar/resource_type/c_5794": "Conference paper",
    "http://purl.org/coar/resource_type/c_db06": "Doctoral thesis",
    "http://purl.org/coar/resource_type/c_2f33": "Book",
    "http://purl.org/coar/resource_type/c_93fc": "Report",
    "http://purl.org/coar/resource_type/c_dcae04bc": "Review article",
    "http://purl.org/coar/resource_type/c_efa0": "Review",
    "http://purl.org/coar/resource_type/c_8042": "Working paper",
}
BASE = """
  SELECT repository_info.institution AS inst,
         TRY_CAST(LEFT("cerif:PublicationDate", 4) AS INTEGER) AS yr,
         "pubt:Type"."#text" AS pubtype,
         doi_problem("cerif:DOI") AS doi,
         list_filter("cerif:Abstract", lambda a: nullif(trim(a."#text"), '') IS NOT NULL)[1]."#text" AS abstract,
         "cerif:Title"[1]."#text" AS title,
         "ar:Access" AS access,
         "cerif:Handle" AS handle,
         "cerif:URL" AS url,
         len(list_filter("cerif:OriginatesFrom", lambda x: x."cerif:Project"."@id" IS NOT NULL)) > 0 AS has_project
  FROM lake.cris.publications
"""
# the Handle prefix family each institution uses most. A family is the first segment
# of the prefix (11245.1 and 11245 are both UvA, 1871.1 and 1871 both VU), except
# for 20.500.* prefixes, which are separate prefixes each.
FAMILY = "CASE WHEN handle_prefix(handle) LIKE '20.500.%' THEN handle_prefix(handle) ELSE split_part(handle_prefix(handle), '.', 1) END"
MAIN_PREFIX = f"SELECT inst, mode({FAMILY}) AS main_prefix FROM p WHERE handle_ok(handle) GROUP BY inst"
MEASURES = {
    "n": "COUNT(*)",
    "doi_present": "COUNT(*) FILTER (WHERE doi <> 'missing')",
    "doi_valid": "COUNT(*) FILTER (WHERE doi = 'valid')",
    "doi_prefix": "COUNT(*) FILTER (WHERE doi = 'URL or doi: prefix')",
    "doi_ws": "COUNT(*) FILTER (WHERE doi = 'whitespace')",
    "abs_present": "COUNT(*) FILTER (WHERE abstract IS NOT NULL)",
    "abs_valid": "COUNT(*) FILTER (WHERE abstract_ok(abstract, title))",
    "abs_short": "COUNT(*) FILTER (WHERE abstract IS NOT NULL AND length(trim(abstract)) < 100)",
    "abs_eqtitle": "COUNT(*) FILTER (WHERE abstract IS NOT NULL AND length(trim(abstract)) >= 100 AND lower(trim(abstract)) = lower(trim(coalesce(title, ''))))",
    "oa_present": "COUNT(*) FILTER (WHERE nullif(trim(access), '') IS NOT NULL)",
    "oa_valid": "COUNT(*) FILTER (WHERE coar_access_ok(access))",
    "proj_present": "COUNT(*) FILTER (WHERE has_project)",
    "handle_present": "COUNT(*) FILTER (WHERE nullif(trim(handle), '') IS NOT NULL)",
    "handle_valid": "COUNT(*) FILTER (WHERE handle_ok(handle))",
    # valid, and with the prefix family the institution uses most
    "handle_mainprefix": f"COUNT(*) FILTER (WHERE handle_ok(handle) AND {FAMILY} = main_prefix)",
    # a URN:NBN anywhere in the Handle or URL field (the harvest has no URN column)
    "urn_found": "COUNT(*) FILTER (WHERE regexp_matches(lower(coalesce(handle, '') || ' ' || coalesce(url, '')), 'urn:nbn:'))",
}


def main() -> None:
    con = connect()
    rows = con.execute(
        f"WITH p AS ({BASE}), main AS ({MAIN_PREFIX}) SELECT inst, yr, pubtype, {', '.join(f'{v} AS {k}' for k, v in MEASURES.items())} "
        "FROM p LEFT JOIN main USING (inst) WHERE yr BETWEEN 1995 AND 2025 GROUP BY ALL"
    ).fetchall()
    # collapse publication types to the labelled ones + "Other"
    agg: dict = {}
    for inst, yr, pt, *counts in rows:
        key = (inst, yr, PUBTYPES.get(pt, "Other"))
        agg[key] = [a + b for a, b in zip(agg.get(key, [0] * len(counts)), counts)]
    insts = sorted({k[0] for k in agg})
    pubtypes = sorted({k[2] for k in agg})
    examples = dict(con.execute(
        # a typical example per kind of error: the most common length-15-to-60 value
        'SELECT r, mode(doi) FROM (SELECT doi_problem("cerif:DOI") AS r, "cerif:DOI" AS doi FROM lake.cris.publications) '
        "WHERE r NOT IN ('valid', 'missing') AND length(doi) BETWEEN 15 AND 60 GROUP BY 1"
    ).fetchall())
    # Handle prefixes per institution (top 5), and each institution's ROR (to look up its URN:NBN prefix)
    prefixes: dict = {}
    for inst, pref, n in con.execute(
        f"WITH p AS ({BASE}) SELECT inst, handle_prefix(handle), COUNT(*) FROM p "
        "WHERE yr BETWEEN 1995 AND 2025 AND handle_ok(handle) GROUP BY ALL ORDER BY 1, 3 DESC"
    ).fetchall():
        if len(prefixes.setdefault(inst, [])) < 5:
            prefixes[inst].append([pref, n])
    rors = dict(con.execute("SELECT repository_info.institution, any_value(repository_info.ror) FROM lake.cris.publications GROUP BY 1").fetchall())
    snapshot = con.execute("SELECT CAST(max(snapshot_time) AS VARCHAR) FROM ducklake_snapshots('lake')").fetchone()[0]
    newest = con.execute("SELECT CAST(max(header.datestamp) AS VARCHAR) FROM lake.cris.publications").fetchone()[0]
    data = {
        "extracted": datetime.date.today().isoformat(),
        "catalog_snapshot": str(snapshot)[:10],
        "newest_datestamp": str(newest)[:10],
        "dims": {"institution": insts, "pubtype": pubtypes},
        "measures": list(MEASURES),
        "rows": [[insts.index(i), y, pubtypes.index(p), *c] for (i, y, p), c in sorted(agg.items())],
        "handle_prefixes": prefixes,
        "inst_ror": rors,
        "examples": {"doi_prefix": examples.get("URL or doi: prefix"), "doi_ws": examples.get("whitespace"), "doi_other": examples.get("other format error")},
    }
    payload = json.dumps(data, separators=(",", ":"))
    html = PAGE.read_text(encoding="utf-8")
    html, n = re.subn(r'(<script id="dashboard-data" type="application/json">).*?(</script>)',
                      lambda m: m.group(1) + payload + m.group(2), html, count=1, flags=re.S)
    if n != 1:
        raise SystemExit('static.html has no <script id="dashboard-data"> element')
    PAGE.write_text(html, encoding="utf-8")
    print(f"embedded {len(data['rows'])} rows ({len(payload) // 1024} KB) into {PAGE}")


if __name__ == "__main__":
    main()
