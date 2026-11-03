-- ISO 7064 MOD 11-2 check character, used by ORCID and ISNI (16 characters, last one is the check)
CREATE OR REPLACE MACRO mod11_2_ok(id) AS (
  regexp_full_match(replace(id, '-', ''), '\d{15}[\dX]') AND
  replace(CAST((12 - list_reduce(
           list_transform(string_split(left(replace(id, '-', ''), 15), ''), lambda x: CAST(x AS INTEGER)),
           lambda acc, d: ((acc + d) * 2) % 11, 0) % 11) % 11 AS VARCHAR), '10', 'X')
    = right(replace(id, '-', ''), 1)
);
-- DOI: directory indicator 10. + registrant code + / + suffix without whitespace. The DOI handbook allows
-- almost any character in the suffix; Crossref's stricter pattern rejects valid old SICI DOIs (with + and <>).
CREATE OR REPLACE MACRO doi_ok(v) AS regexp_full_match(v, '10\.\d{4,9}(\.\d+)*/\S+');
CREATE OR REPLACE MACRO doi_problem(v) AS CASE
  WHEN v IS NULL OR trim(v) = '' THEN 'missing'
  WHEN doi_ok(v) THEN 'valid'
  WHEN regexp_matches(lower(v), '^(https?://(dx\.)?doi\.org/|doi:)') THEN 'URL or doi: prefix'
  WHEN v <> trim(v) OR regexp_matches(v, '\s') THEN 'whitespace'
  ELSE 'other format error' END;
CREATE OR REPLACE MACRO orcid_ok(v) AS
  regexp_full_match(v, '(https://orcid\.org/)?\d{4}-\d{4}-\d{4}-\d{3}[\dX]')
  AND mod11_2_ok(regexp_replace(v, '^https://orcid\.org/', ''));
CREATE OR REPLACE MACRO isni_ok(v) AS
  regexp_full_match(replace(v, ' ', ''), '\d{15}[\dX]') AND mod11_2_ok(replace(v, ' ', ''));
CREATE OR REPLACE MACRO ror_ok(v) AS regexp_full_match(v, '(https://ror\.org/)?0[a-hj-km-np-tv-z0-9]{6}\d{2}');
CREATE OR REPLACE MACRO coar_access_ok(v) AS regexp_full_match(v, 'http://purl\.org/coar/access_right/c_(abf2|f1cf|16ec|14cb)');
CREATE OR REPLACE MACRO funder_id_ok(v) AS regexp_full_match(v, '(https://doi\.org/)?10\.13039/\d+');
CREATE OR REPLACE MACRO raid_ok(v) AS regexp_full_match(v, 'https://raid\.org/10\.\d{4,9}/[^\s]+');
CREATE OR REPLACE MACRO iso_date_ok(v) AS regexp_full_match(v, '\d{4}(-\d{2}(-\d{2})?)?') AND TRY_CAST(rpad(v, 10, '-01-01')[1:10] AS DATE) IS NOT NULL;
CREATE OR REPLACE MACRO abstract_ok(abstract, title) AS
  length(trim(abstract)) >= 100 AND lower(trim(abstract)) <> lower(trim(coalesce(title, '')));
