# /// script
# requires-python = ">=3.11"
# ///
"""
Check OAI-PMH endpoints against the OpenAIRE guidelines.

For every base URL: Identify, ListMetadataFormats and ListSets (following
resumption tokens), then which of the formats and sets the OpenAIRE guidelines
ask for are offered:

- CRIS systems (OpenAIRE Guidelines for CRIS Managers 1.1/1.2):
  metadataPrefix oai_cerif_openaire, sets openaire_cris_publications,
  _persons, _orgunits, _projects, _funding, _products, _patents, _equipments, _events;
- literature repositories (OpenAIRE Guidelines for Literature Repositories 4):
  metadataPrefix oai_openaire, set openaire; the older 3.0 profile uses oai_dc
  with sets openaire / ec_fundedresources (and DRIVER: driver).

    uv run oai_check.py urls.json > oai-results.json

urls.json is a JSON list of base URLs. Only the standard library is used.
"""

import concurrent.futures as cf
import json
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

NS = {"o": "http://www.openarchives.org/OAI/2.0/"}
CRIS_SETS = ["openaire_cris_publications", "openaire_cris_persons", "openaire_cris_orgunits", "openaire_cris_projects",
             "openaire_cris_funding", "openaire_cris_products", "openaire_cris_patents", "openaire_cris_equipments", "openaire_cris_events"]
HEADERS = {"User-Agent": "DURF-metadata-monitor/0.1 (OAI-PMH guidelines check)"}


def oai(base: str, **params) -> ET.Element:
    url = base + ("&" if "?" in base else "?") + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=60) as r:
        root = ET.fromstring(r.read())
    err = root.find("o:error", NS)
    if err is not None and err.get("code") != "noSetHierarchy":
        raise RuntimeError(f"{err.get('code')}: {(err.text or '').strip()[:120]}")
    return root


def check(base: str) -> dict:
    out: dict = {"baseurl": base, "checked": time.strftime("%Y-%m-%d")}
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
        out["cris"] = {"oai_cerif_openaire": "oai_cerif_openaire" in f, "sets": {x: x in s for x in CRIS_SETS}}
        out["literature"] = {"oai_openaire": "oai_openaire" in f, "set_openaire": "openaire" in s,
                             "oai_dc": "oai_dc" in f, "set_ec_fundedresources": "ec_fundedresources" in s, "set_driver": "driver" in s}
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
