import duckdb, pathlib, sys
here = pathlib.Path(__file__).parent
c = duckdb.connect(); c.execute((here / 'checks.sql').read_text())
cases = [
 ("orcid_ok('0000-0002-1825-0097')", True),            # ORCID's documented example
 ("orcid_ok('https://orcid.org/0000-0001-5109-3700')", True),
 ("orcid_ok('0000-0002-1694-233X')", True),
 ("orcid_ok('0000-0002-1825-0098')", False),           # wrong check digit
 ("orcid_ok('000000021825009 7')", False),
 ("orcid_ok('http://orcid.org/0000-0002-1825-0097')", False),
 ("isni_ok('0000 0001 2103 2683')", True),
 ("isni_ok('0000000121032684')", False),
 ("doi_ok('10.1038/s41586-021-03819-2')", True),
 ("doi_ok('https://doi.org/10.1038/s41586-021-03819-2')", False),
 ("doi_problem('https://doi.org/10.1038/x')", 'URL or doi: prefix'),
 ("doi_problem(' 10.1038/x')", 'whitespace'),
 ("doi_problem('')", 'missing'),
 ("doi_problem('10.1038/abc')", 'valid'),
 ("doi_ok('10.1002/(SICI)1099-1077(1998110)13:2+<S87::AID-HUP53>3.0.CO;2-8')", True),  # old SICI DOI
 ("doi_problem('10.1093/law/97801928824 86.001.0001')", 'whitespace'),
 ("doi_problem('https://doi.org/doi: 10.1007/164_2020_356')", 'URL or doi: prefix'),
 ("ror_ok('https://ror.org/027m9bs27')", True),
 ("ror_ok('https://ror.org/02e2c7k09')", True),
 ("ror_ok('ror.org/027m9bs27')", False),
 ("coar_access_ok('http://purl.org/coar/access_right/c_abf2')", True),
 ("coar_access_ok('open access')", False),
 ("funder_id_ok('https://doi.org/10.13039/501100003246')", True),
 ("raid_ok('https://raid.org/10.82841/5f1fd3a5')", True),
 ("raid_ok('raid.org/10.82841/5f1fd3a5')", False),
 ("iso_date_ok('2024-02-30')", False),
 ("iso_date_ok('2024-02')", True),
 ("handle_ok('https://hdl.handle.net/11245/1.433289')", True),
 ("handle_ok('https://hdl.handle.net/20.500.11755/9f63f17d-e522-40d5-8186-4779ed3c0edd')", True),
 ("handle_ok('1871.1/320f2df6')", True),
 ("handle_ok('https://hdl.handle.net/')", False),
 ("handle_ok('https://doi.org/10.1038/abc')", False),
 ("handle_prefix('https://hdl.handle.net/1871.1/320f2df6')", '1871.1'),
 ("handle_prefix('20.500.11755/abc')", '20.500.11755'),
 ("urn_nbn_ok('urn:nbn:nl:ui:29-1234567')", True),
 ("urn_nbn_ok('URN:NBN:NL:UI:10-1874-12345')", True),
 ("urn_nbn_ok('urn:nbn:nl:hs:18-abc')", True),
 ("urn_nbn_ok('urn:nbn:de:0001-12345')", False),
 ("urn_nbn_ok('urn:nbn:nl:ui:29')", False),
 ("urn_nbn_prefix('URN:NBN:NL:UI:29-1234567')", 'urn:nbn:nl:ui:29-'),
 ("abstract_ok(repeat('x', 120), 'Title')", True),
 ("abstract_ok('Title', 'Title')", False),
]
bad = 0
for expr, want in cases:
    got = c.execute('SELECT ' + expr).fetchone()[0]
    bad += got != want
    print('ok  ' if got == want else 'FAIL', expr, '->', got)
print('failures:', bad); sys.exit(1 if bad else 0)
