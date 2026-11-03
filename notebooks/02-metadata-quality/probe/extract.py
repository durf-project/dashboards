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
         len(list_filter("cerif:OriginatesFrom", lambda x: x."cerif:Project"."@id" IS NOT NULL)) > 0 AS has_project
  FROM lake.cris.publications
"""
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
}


def main() -> None:
    con = connect()
    rows = con.execute(
        f"WITH p AS ({BASE}) SELECT inst, yr, pubtype, {', '.join(f'{v} AS {k}' for k, v in MEASURES.items())} "
        "FROM p WHERE yr BETWEEN 1995 AND 2025 GROUP BY ALL"
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
    snapshot = con.execute("SELECT CAST(max(snapshot_time) AS VARCHAR) FROM ducklake_snapshots('lake')").fetchone()[0]
    newest = con.execute("SELECT CAST(max(header.datestamp) AS VARCHAR) FROM lake.cris.publications").fetchone()[0]
    data = {
        "extracted": datetime.date.today().isoformat(),
        "catalog_snapshot": str(snapshot)[:10],
        "newest_datestamp": str(newest)[:10],
        "dims": {"institution": insts, "pubtype": pubtypes},
        "measures": list(MEASURES),
        "rows": [[insts.index(i), y, pubtypes.index(p), *c] for (i, y, p), c in sorted(agg.items())],
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
