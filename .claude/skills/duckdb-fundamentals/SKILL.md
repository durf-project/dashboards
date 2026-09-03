---
name: duckdb-fundamentals
description: >
  Use this skill for general DuckDB and DuckLake mechanics that aren't
  specific to the SURF ORI catalog -- installing/loading extensions inside
  a Python connection, ATTACHing a DuckLake catalog, reading DuckDB's
  Binder Error messages, quoting identifiers, and other SQL dialect
  gotchas. Trigger on phrases like "install a DuckDB extension", "how does
  ATTACH work", "what does ducklake: mean", "column not found" /
  "Binder Error", or any DuckDB SQL error message. For questions about
  the SURF ORI catalog's actual schemas, tables, or columns (OpenAlex,
  OpenAIRE, CRIS, OpenAPC), use the `ori-ducklake` skill instead -- this
  one is the general-purpose complement to it.
---

# DuckDB & DuckLake fundamentals

**This repo never uses a standalone `duckdb` CLI binary.** Every notebook
reaches DuckDB through the `duckdb` Python package, installed ephemerally
by `uv`/`uvx` from the notebook's PEP 723 header (see `AGENTS.md`). Don't
suggest `brew install duckdb`, `curl -fsSL https://install.duckdb.org | sh`,
or any other system-level install -- there's nothing to install, and
nothing on `PATH` to find.

## Extensions: INSTALL vs LOAD

Every fresh `duckdb.connect()` starts with no extensions loaded --
extensions aren't bundled into the pip package and aren't persisted across
processes. `INSTALL` downloads and caches the extension binary (a no-op if
already cached); `LOAD` makes it usable in *this* connection. You need both,
every time, in a script:

```python
con = duckdb.connect()
con.execute("INSTALL ducklake; LOAD ducklake;")
con.execute("INSTALL httpfs; LOAD httpfs;")   # needed for any https:// or s3:// path
```

Community extensions (not in DuckDB core) need `FROM community`:

```sql
INSTALL h3 FROM community;
LOAD h3;
```

## ATTACH and DuckLake

`ducklake:<catalog-url>` is the URI scheme for attaching a DuckLake catalog
-- DuckLake stores table metadata (schemas, snapshots, file manifests)
separately from the actual Parquet data files, which is what makes
time-travel and cheap schema evolution possible.

```sql
ATTACH 'ducklake:https://objectstore.surf.nl/<bucket-path>/catalog.ducklake'
    AS lake (READ_ONLY, CREATE_IF_NOT_EXISTS false);
```

- `READ_ONLY` -- always set this for notebook work. There's no reason a
  participant notebook should write back to the shared catalog.
- `CREATE_IF_NOT_EXISTS false` -- fail loudly if the catalog path is wrong,
  instead of silently creating an empty one.
- Once attached, refer to tables as `lake.<schema>.<table>` -- see
  `ori-ducklake` for the actual schema/table names in the SURF ORI catalog.

## Reading DuckDB's error messages

DuckDB's `Binder Error` is almost always a column or table name problem,
and the message usually tells you what it *did* find:

```
Binder Error: Referenced column "instituton_name" not found in FROM clause!
Candidate bindings: "institution_name"
```

Before guessing at a fix, run `DESCRIBE lake.<schema>.<table>;` or
`SELECT * FROM lake.<schema>.<table> LIMIT 1;` to see the real column
names and types rather than assuming.

## Quoting identifiers

Unquoted identifiers in DuckDB are case-insensitive and must be a plain
run of letters/digits/underscores. Anything else -- hyphens, spaces,
leading digits -- needs double quotes:

```sql
-- schema name has a hyphen: must be quoted
SELECT * FROM lake."nl-orgs".baseline;

-- fine unquoted: plain identifier
SELECT * FROM lake.openalex.institutions;
```

Don't confuse SQL double-quotes (identifiers) with single-quotes (string
literals) -- `"nl-orgs"` and `'nl-orgs'` mean different things to DuckDB.

## Sizing a query before you run it

Object-store-backed tables can be large even when they look small in a
schema listing. Before running an aggregate over an unfamiliar table:

- Check row count / file size first if a tool for that is available (the
  `ori-ducklake` MCP server's `catalog_stats` is free and instant for the
  SURF catalog).
- Prefer `USING SAMPLE n ROWS` over `LIMIT n` when exploring without a
  selective `WHERE` -- `LIMIT` still has to produce rows in scan order,
  which can mean scanning much more than `n` rows on a filtered-out
  dataset; `USING SAMPLE` doesn't.
- Filter before you `UNNEST` a struct/array column, not after -- unnesting
  first and filtering second means building the full exploded row set in
  memory before throwing most of it away.

## Where to look things up

There's no bundled offline doc index in this repo. For anything not
covered above or in `ori-ducklake`, check:

- DuckDB SQL reference and function docs: https://duckdb.org/docs/
- DuckLake format docs: https://ducklake.select/docs/stable/
