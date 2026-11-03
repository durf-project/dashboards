"""Shared DuckLake connection for probe.py and extract.py."""

import os
import pathlib
import urllib.parse

import duckdb

CATALOG = "ducklake:https://objectstore.surf.nl/cea01a7216d64348b7e51e5f3fc1901d:sprouts/catalog.ducklake"
CHECKS = pathlib.Path(__file__).parent / "checks.sql"


def connect(target: str | None = None) -> duckdb.DuckDBPyConnection:
    """Attach the ORI DuckLake as `lake` and load the validity macros.

    PROBE_ATTACH=/path/to/file.duckdb uses a local database instead (for testing).
    DUCKDB_EXTENSIONS=/dir installs ducklake/httpfs from <dir>/<name>.duckdb_extension,
    for networks where DuckDB can't download extensions itself (it fetches them over
    plain http, which some proxies refuse). HTTPS_PROXY is passed on to httpfs.
    """
    target = target or os.environ.get("PROBE_ATTACH", CATALOG)
    con = duckdb.connect()
    options = "READ_ONLY"
    if target.startswith("ducklake:"):
        ext_dir = os.environ.get("DUCKDB_EXTENSIONS")
        for ext in ("ducklake", "httpfs"):
            src = f"'{pathlib.Path(ext_dir) / (ext + '.duckdb_extension')}'" if ext_dir else ext
            con.execute(f"INSTALL {src}; LOAD {ext};")
        proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
        if proxy:
            con.execute(f"SET http_proxy = '{urllib.parse.urlparse(proxy).netloc}'")
        options += ", CREATE_IF_NOT_EXISTS false"
    con.execute(f"ATTACH '{target}' AS lake ({options})")
    con.execute(CHECKS.read_text())
    return con
