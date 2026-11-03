# /// script
# requires-python = ">=3.11"
# dependencies = ["duckdb>=1.5.2"]
# ///
"""
Build the OpenAIRE tab of the DURF Metadata Monitor: how the research
performing organisations (RPOs) and their CRIS systems and repositories show up
in OpenAIRE. Embeds the result in ../static.html (<script id="openaire-data">).

    uv run openaire.py [oai-results.json]

It also writes oai-urls.json, the OAI-PMH base URLs of the CRIS systems and
literature repositories, for: uv run oai_check.py oai-urls.json > oai-results.json

Sources:
- ORI DuckLake: "nl-orgs".baseline (the RPOs and their ROR), joined on ROR to
  openaire.organizations (OpenAIRE ids, names, other identifiers), and
  openaire.datasources (type, compatibility, validation date, ...);
- OpenAIRE Graph API (api.openaire.eu/graph/v1): which datasources belong to an
  organisation, and the number of research products per datasource and of
  projects per organisation, per 5-year period. The DuckLake's openaire result
  tables can't be used for this: their collectedfrom, organizations and
  projects columns are empty;
- OpenAIRE Datasource Manager API (services.openaire.eu/openaire/ds/api):
  per datasource its harvesting interfaces (OAI-PMH base URL, format, sets,
  compatibility, last collection/aggregation date and record count);
- optionally the output of oai_check.py (formats and sets each endpoint offers).
"""

import concurrent.futures as cf
import datetime
import json
import os
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request

from lake import connect

PAGE = pathlib.Path(os.environ.get("MONITOR_PAGE", pathlib.Path(__file__).parent.parent / "static.html"))
GRAPH = "https://api.openaire.eu/graph/v1/"
DSM = "https://services.openaire.eu/openaire/ds/api/"
PERIODS = [(1995, 1999), (2000, 2004), (2005, 2009), (2010, 2014), (2015, 2019), (2020, 2025)]
PRODUCT_TYPES = ["publication", "dataset", "software", "other"]
# result counts only for datasources that hold research output of the institution itself
COUNTED_TYPES = re.compile(r"CRIS|Repository", re.I)
SKIP_GROUPS = {"NWO", "UN"}  # the funder and umbrella organisations are not RPOs


def get_json(url: str) -> dict:
    err = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "DURF-metadata-monitor/0.1"}), timeout=90) as r:
                used, limit = int(r.headers.get("x-ratelimit-used", 0)), int(r.headers.get("x-ratelimit-limit", 0) or 1e9)
                if limit and used > limit - 50:
                    time.sleep(60)
                return json.load(r)
        except Exception as e:  # retry transient errors
            err = e
            time.sleep(3 * (attempt + 1))
    raise err


def graph(endpoint: str, **params) -> dict:
    return get_json(GRAPH + endpoint + "?" + urllib.parse.urlencode(params))


API_DS: dict = {}  # datasource records from the Graph API, a fallback for ones not (yet) in the DuckLake


def datasources_of(org_id: str) -> list:
    out, page = [], 1
    while True:
        d = graph("dataSources", relOrganizationId=org_id, pageSize=100, page=page)
        out += d["results"]
        if len(out) >= d["header"]["numFound"] or not d["results"]:
            API_DS.update((x["id"], x) for x in out)
            return [x["id"] for x in out]
        page += 1


def interfaces_of(original_ids: list) -> tuple:
    """The DSM API knows a datasource by one of its originalIds."""
    for oid in original_ids or []:
        try:
            d = get_json(DSM + urllib.parse.quote(oid, safe=":"))
        except Exception:
            continue
        if d.get("api"):
            return oid, [{
                "baseurl": (a.get("baseurl") or "").strip(),
                "protocol": a.get("protocol"),
                "compatibility": a.get("compatibilityOverride") or a.get("compatibility"),
                "lastCollectionDate": a.get("lastCollectionDate"), "lastCollectionTotal": a.get("lastCollectionTotal"),
                "lastAggregationDate": a.get("lastAggregationDate"), "lastAggregationTotal": a.get("lastAggregationTotal"),
                "params": {p["param"]: p["value"] for p in a.get("apiParams") or []},
            } for a in d["api"]]
    return None, []


def count(endpoint: str, **params) -> int:
    return graph(endpoint, pageSize=1, **params)["header"]["numFound"]


def main() -> None:
    con = connect()
    rpos = con.execute("""
        SELECT b.acronym_EN, b.full_name_in_English, b.main_grouping, b.ROR_LINK,
               list(DISTINCT o.id ORDER BY o.id) FILTER (WHERE o.id IS NOT NULL) AS ids,
               any_value(o.legalName), any_value(o.websiteUrl),
               list(DISTINCT p.scheme) FILTER (WHERE p.scheme IS NOT NULL) AS pid_schemes
        FROM lake."nl-orgs".baseline b
        LEFT JOIN (SELECT o.*, r.value AS ror FROM lake.openaire.organizations o, UNNEST(o.pids) AS u(r) WHERE r.scheme = 'ROR') o
               ON o.ror = b.ROR_LINK
        LEFT JOIN (SELECT o.id, p.scheme FROM lake.openaire.organizations o, UNNEST(o.pids) AS u(p)) p ON p.id = o.id
        GROUP BY ALL ORDER BY 3, 1
    """).fetchall()
    orgs = [{"acronym": a, "name": n, "group": g, "ror": r, "openaire_ids": ids or [], "legalName": ln, "website": w,
             "pid_schemes": sorted(ps or [])} for a, n, g, r, ids, ln, w, ps in rpos if g not in SKIP_GROUPS]
    print(f"{len(orgs)} RPOs, {sum(1 for o in orgs if o['openaire_ids'])} found in OpenAIRE", file=sys.stderr)

    with cf.ThreadPoolExecutor(8) as ex:
        for o, ds in zip(orgs, ex.map(lambda o: sorted({d for i in o["openaire_ids"] for d in datasources_of(i)}), orgs)):
            o["datasources"] = ds
    ds_ids = sorted({d for o in orgs for d in o["datasources"]})
    con.execute("CREATE TEMP TABLE want AS SELECT unnest(?::VARCHAR[]) AS id", [ds_ids])
    rows = con.execute("""
        SELECT d.id, d.officialName, d.englishName, d.type.value, d.openaireCompatibility, d.websiteUrl,
               CAST(d.dateOfValidation AS VARCHAR), d.originalIds, list_transform(d.pids, lambda p: p.scheme || ':' || p.value),
               d.accessRights, d.uploadRights
        FROM lake.openaire.datasources d JOIN want USING (id)
    """).fetchall()
    datasources = {r[0]: {"name": r[1] or r[2], "type": r[3], "compatibility": r[4], "website": r[5], "validated": r[6],
                          "originalIds": r[7] or [], "pids": r[8] or [], "accessRights": r[9], "uploadRights": r[10]} for r in rows}
    print(f"{len(ds_ids)} datasources, {len(datasources)} in the DuckLake", file=sys.stderr)
    for i in ds_ids:
        if i not in datasources:
            x = API_DS[i]
            datasources[i] = {"name": x.get("officialName") or x.get("englishName"), "type": (x.get("type") or {}).get("value"),
                              "compatibility": x.get("openaireCompatibility"), "website": x.get("websiteUrl"),
                              "validated": x.get("dateOfValidation"), "originalIds": x.get("originalIds") or [],
                              "pids": [p["scheme"] + ":" + p["value"] for p in x.get("pids") or []],
                              "accessRights": x.get("accessRights"), "uploadRights": x.get("uploadRights"), "from_api": True}

    with cf.ThreadPoolExecutor(8) as ex:
        for d, (dsm_id, ifaces) in zip(datasources.values(), ex.map(lambda d: interfaces_of(d["originalIds"]), datasources.values())):
            d["dsm_id"], d["interfaces"] = dsm_id, ifaces

    jobs = [("ds", i, t, p) for i, d in datasources.items() if COUNTED_TYPES.search(d["type"] or "") for t in PRODUCT_TYPES for p in PERIODS]
    jobs += [("org", oid, "project", p) for o in orgs for oid in o["openaire_ids"] for p in PERIODS]
    print(f"{len(jobs)} count queries", file=sys.stderr)

    def run(job):
        kind, i, t, (y0, y1) = job
        if kind == "ds":
            return count("researchProducts", relCollectedFromDatasourceId=i, type=t,
                         fromPublicationDate=f"{y0}-01-01", toPublicationDate=f"{y1}-12-31")
        return count("projects", relOrganizationId=i, fromStartDate=f"{y0}-01-01", toStartDate=f"{y1}-12-31")

    with cf.ThreadPoolExecutor(8) as ex:
        results = list(ex.map(run, jobs))
    for (kind, i, t, p), n in zip(jobs, results):
        target = datasources[i] if kind == "ds" else next(o for o in orgs if i in o["openaire_ids"])
        target.setdefault("counts", {}).setdefault(t, [0] * len(PERIODS))[PERIODS.index(p)] += n

    # base URLs of the CRIS systems and literature repositories, for oai_check.py
    urls = sorted({(a["baseurl"] or "").strip().split("?")[0] for d in datasources.values()
                   if re.search(r"CRIS|Institutional|Thematic", d["type"] or "") for a in d["interfaces"]} - {""})
    (pathlib.Path(__file__).parent / "oai-urls.json").write_text(json.dumps(urls, indent=1) + "\n")

    oai = {}
    if len(sys.argv) > 1:
        for r in json.load(open(sys.argv[1])):
            oai[r["baseurl"]] = r

    data = {"extracted": datetime.date.today().isoformat(), "periods": PERIODS, "orgs": orgs,
            "datasources": datasources, "oai": oai}
    payload = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    html = PAGE.read_text(encoding="utf-8")
    html, n = re.subn(r'(<script id="openaire-data" type="application/json">).*?(</script>)',
                      lambda m: m.group(1) + payload + m.group(2), html, count=1, flags=re.S)
    if n != 1:
        raise SystemExit('static.html has no <script id="openaire-data"> element')
    PAGE.write_text(html, encoding="utf-8")
    print(f"embedded {len(orgs)} RPOs, {len(datasources)} datasources ({len(payload) // 1024} KB) into {PAGE}", file=sys.stderr)


if __name__ == "__main__":
    main()
