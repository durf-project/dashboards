# /// script
# requires-python = ">=3.11"
# ///
"""
Do the publication records at the source carry a Handle and a URN:NBN?

For every endpoint that oai_check.py could reach, fetch the first page of
ListRecords (100 records at most, deleted records left out):
- CRIS systems: the OpenAIRE CERIF format, set openaire_cris_publications
  (the profile has optional cerif:Handle and cerif:URN elements);
- repositories: oai_openaire when offered, else oai_dc, without a set.
Counts the records with a DOI, a Handle and a URN:NBN, and which URN:NBN
prefixes (urn:nbn:nl:ui:NN-) occur, to compare with the prefix the KB assigned
to the institution (surf-ori/nl-research-organisations, nbn_prefixes.csv).

    uv run identifier_sample.py oai-results.json > identifier-sample.json
"""

import collections
import concurrent.futures as cf
import json
import re
import sys
import time
import xml.etree.ElementTree as ET

from oai_check import NS, oai

DOI = re.compile(r"\b10\.\d{4,9}(?:\.\d+)*/[^\s<\"]+")
HANDLE = re.compile(r"hdl\.handle\.net/\d+(?:\.\d+)*/[^\s<\"]+|<(?:\w+:)?Handle>\s*[^<\s]+", re.I)
URN_NBN = re.compile(r"urn:nbn:nl:(?:ui|hs|in):\d{2}-[^\s<\"]+", re.I)


def sample(res: dict) -> dict:
    base = res.get("checked_url") or res["baseurl"]
    cris = res["cris"].get("prefix")
    if cris:
        prefix, set_spec = cris, "openaire_cris_publications"
    else:
        prefix, set_spec = ("oai_openaire" if res["literature"]["oai_openaire"] else "oai_dc"), None
    out = {"baseurl": res["baseurl"], "metadataPrefix": prefix, "set": set_spec, "checked": time.strftime("%Y-%m-%d")}
    try:
        params = {"verb": "ListRecords", "metadataPrefix": prefix}
        if set_spec:
            params["set"] = set_spec
        root = oai(base, **params)
        n = doi = handle = urn = 0
        prefixes: collections.Counter = collections.Counter()
        examples = {}
        for rec in root.findall(".//o:record", NS):
            header = rec.find("o:header", NS)
            if header is not None and header.get("status") == "deleted":
                continue
            text = ET.tostring(rec, encoding="unicode")
            n += 1
            doi += bool(DOI.search(text))
            h = HANDLE.search(text)
            handle += bool(h)
            urns = URN_NBN.findall(text)
            urn += bool(urns)
            for u in set(x.lower() for x in urns):
                prefixes[re.match(r"urn:nbn:nl:\w{2}:\d{2}-", u).group(0)] += 1
                examples.setdefault("urn", u)
            if h:
                examples.setdefault("handle", re.sub(r"<[^>]+>\s*", "", h.group(0)))
        out.update(ok=True, records=n, with_doi=doi, with_handle=handle, with_urn=urn,
                   urn_prefixes=dict(prefixes), examples=examples)
    except Exception as e:
        out.update(ok=False, error=f"{type(e).__name__}: {str(e)[:160]}")
    return out


def main() -> None:
    results = [r for r in json.load(open(sys.argv[1])) if r.get("ok")]
    with cf.ThreadPoolExecutor(6) as ex:
        print(json.dumps(list(ex.map(sample, results)), indent=1))


if __name__ == "__main__":
    main()
