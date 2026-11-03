# /// script
# requires-python = ">=3.11"
# ///
"""
Check OAI-PMH endpoints against the OpenAIRE guidelines.

For every base URL: Identify, ListMetadataFormats and ListSets (following
resumption tokens), then which of the formats and sets the OpenAIRE guidelines
ask for are offered:

- CRIS systems (OpenAIRE Guidelines for CRIS Managers 1.1/1.2, "Use of
  OAI-PMH"): a metadataPrefix starting with oai_cerif_openaire, and all nine
  sets openaire_cris_publications, _products, _patents, _persons, _orgunits,
  _projects, _funding, _events and _equipments are mandatory ("shall be
  recognized by the CRIS, even if not all of them are populated"); Identify
  carries one CERIF Service record. For each of the nine sets the check also
  asks ListIdentifiers whether it is populated;
- literature repositories (OpenAIRE Guidelines for Literature Repositories
  4.x): recommended metadataPrefix oai_openaire, no mandatory set (the
  "openaire" set is commented out of the 4.x text); the older 3.0 profile
  uses oai_dc with the mandatory set openaire. Its population is checked too.

    uv run oai_check.py urls.json > oai-results.json

urls.json is a JSON list of base URLs. Only the standard library is used.
"""

import concurrent.futures as cf
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

NS = {"o": "http://www.openarchives.org/OAI/2.0/"}
CRIS_SETS = ["openaire_cris_publications", "openaire_cris_persons", "openaire_cris_orgunits", "openaire_cris_projects",
             "openaire_cris_funding", "openaire_cris_products", "openaire_cris_patents", "openaire_cris_equipments", "openaire_cris_events"]
HEADERS = {"User-Agent": "DURF-metadata-monitor/0.1 (OAI-PMH guidelines check)"}
# behind a proxy that only sets HTTPS_PROXY, send plain-http endpoints through it too
_proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
OPENER = urllib.request.build_opener(urllib.request.ProxyHandler(
    {"http": os.environ.get("HTTP_PROXY") or os.environ.get("http_proxy") or _proxy, "https": _proxy} if _proxy else {}))


def oai(base: str, **params) -> ET.Element:
    url = base + ("&" if "?" in base else "?") + urllib.parse.urlencode(params)
    for attempt in range(2):  # one retry for transient errors (resets, 5xx, timeouts)
        try:
            with OPENER.open(urllib.request.Request(url, headers=HEADERS), timeout=60) as r:
                root = ET.fromstring(r.read())
            break
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if attempt or isinstance(e, urllib.error.HTTPError) and e.code < 500:
                raise
            time.sleep(5)
    err = root.find("o:error", NS)
    # an empty set list is reported as noSetHierarchy, by some servers as noRecordsMatch
    if err is not None and not (params.get("verb") == "ListSets" and err.get("code") in ("noSetHierarchy", "noRecordsMatch")):
        raise RuntimeError(f"{err.get('code')}: {(err.text or '').strip()[:120]}")
    return root


def first_page_count(base: str, prefix: str, set_spec: str):
    """Records in a set: completeListSize when the server gives it, else the size
    of the first page as a lower bound ("100+"); 0 when the set is empty."""
    try:
        root = oai(base, verb="ListIdentifiers", metadataPrefix=prefix, set=set_spec)
    except RuntimeError as e:
        return 0 if str(e).startswith("noRecordsMatch") else f"error: {str(e)[:80]}"
    except Exception as e:
        return f"error: {type(e).__name__}"
    n = len(root.findall(".//o:header", NS))
    token = root.find(".//o:resumptionToken", NS)
    if token is not None and token.get("completeListSize"):
        return int(token.get("completeListSize"))
    return f"{n}+" if token is not None and (token.text or "").strip() else n


def check(base: str) -> dict:
    """Check one endpoint. For an http:// URL, try https:// first: many endpoints
    have moved, and some networks (proxies) don't pass plain http at all."""
    if base.startswith("http://"):
        res = check_one("https://" + base[len("http://"):], base)
        if res["ok"]:
            return res
        res_http = check_one(base, base)
        if not res_http["ok"]:
            res_http["error"] += f" (https:// variant: {res['error']})"
        return res_http
    return check_one(base, base)


def check_one(url: str, base: str) -> dict:
    out: dict = {"baseurl": base, "checked_url": url, "checked": time.strftime("%Y-%m-%d")}
    base = url
    try:
        ident = oai(base, verb="Identify").find("o:Identify", NS)
        out["identify"] = {k: (ident.findtext(f"o:{k}", default="", namespaces=NS) or "").strip()
                           for k in ("repositoryName", "protocolVersion", "earliestDatestamp", "deletedRecord", "granularity")}
        fmts = oai(base, verb="ListMetadataFormats").findall(".//o:metadataPrefix", NS)
        out["formats"] = sorted({f.text.strip() for f in fmts if f.text})
        sets, params, pages = [], {"verb": "ListSets"}, 0
        while pages < 25:
            root = oai(base, **params)
            sets += [s.text.strip() for s in root.findall(".//o:setSpec", NS) if s.text]
            token = root.findtext(".//o:resumptionToken", default="", namespaces=NS).strip()
            pages += 1
            if not token:
                break
            params = {"verb": "ListSets", "resumptionToken": token}
        out["set_count"] = len(sets)
        out["sets_truncated"] = pages >= 25
        # keep only the sets the guidelines care about, plus a sample of the rest
        wanted = set(CRIS_SETS) | {"openaire", "openaire_data", "ec_fundedresources", "driver"}
        out["guideline_sets"] = sorted(s for s in sets if s in wanted)
        out["sets_sample"] = sets[:15]
        f, s = set(out["formats"]), set(sets)
        cris_prefix = next((x for x in out["formats"] if x.startswith("oai_cerif_openaire")), None)
        out["cris"] = {"oai_cerif_openaire": bool(cris_prefix), "prefix": cris_prefix,
                       "sets": {x: x in s for x in CRIS_SETS},
                       "service_in_identify": any("Service" in el.tag for d in ident.findall("o:description", NS) for el in d.iter())}
        if cris_prefix:
            out["cris"]["records"] = {x: first_page_count(base, cris_prefix, x) for x in CRIS_SETS if x in s}
        out["literature"] = {"oai_openaire": "oai_openaire" in f, "set_openaire": "openaire" in s,
                             "oai_dc": "oai_dc" in f, "set_ec_fundedresources": "ec_fundedresources" in s, "set_driver": "driver" in s}
        if "openaire" in s:
            out["literature"]["records_openaire"] = first_page_count(base, "oai_openaire" if "oai_openaire" in f else "oai_dc", "openaire")
        out["ok"] = True
    except Exception as e:  # unreachable, not OAI-PMH, bad XML, ...
        out["ok"] = False
        out["error"] = f"{type(e).__name__}: {str(e)[:200]}"
    return out


def main() -> None:
    urls = json.load(open(sys.argv[1]))
    with cf.ThreadPoolExecutor(8) as ex:
        results = list(ex.map(check, urls))
    print(json.dumps(results, indent=1))


if __name__ == "__main__":
    main()
