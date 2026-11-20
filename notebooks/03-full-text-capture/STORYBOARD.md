# Theme 3 dashboard storyboard

Updated 18 November 2026. The existing dashboard implements `theme3-publications-v8`. The publisher section below is a proposed addition for review; this document update does not implement it. Other sections describe the current agreed design and supersede older appended decisions.

## Audience and purpose

Theme 3 leads and repository teams need a baseline for institutional full-text capture, supporting digital resilience, Taverne and future TDM/AI use. Pascal's Activity 1 calls for coverage by repository over time; the current view compares publication cohorts from 2021–2025 at one observation date.

The story is **institutional PDF coverage → source-reported access → organisation differences → publisher-specific gaps within organisations → redundancy → reported Taverne contribution**. Publisher comparisons help identify where repository teams can focus follow-up. They describe the PDF evidence in the source; they do not assign responsibility for a gap to a publisher or institution.

Use Storytelling with Data principles throughout: one clear reader question per view, consistent axes and encodings, direct labels, counts alongside rates, and progressive disclosure for detail. References already used in the project: https://www.storytellingwithdata.com/blog/2021/8/16/exploring-data-is-different-than-explaining-data and https://www.storytellingwithdata.com/blog/2022/2/1/swdchallenge-declutter-and-focus.

## Shared counting and interaction rules

- Default to publication years 2021–2025 and the currently included publication types. All mapped type labels starting with COAR and doctoral theses are excluded before matching and every statistic. Keep the exclusion explanation in methods/audit material rather than dashboard narrative.
- Count distinct publication keys. DOI is primary; DOI-less matching requires title, year and the full supplied sorted author-surname list. Incomplete signatures retain separately counted and flagged repository-record identities. See `theme-3-deduplication.md` for normalisation and limitations.
- Institutional attachment URLs with PDF format evidence are the agreed repository-copy proxy. Publisher links, DOI resolvers and other external links do not count as institutional PDFs. A missing observed PDF does not establish that no local file exists.
- Organisation-level PDF status uses evidence from that organisation's selected repository records. A PDF in another organisation does not fill its local gap. Where one organisation has several repository endpoints, deduplicate publication keys across those endpoints before computing organisation measures; retain endpoint detail in the audit.
- Keep source access labels and count distinct publications within each label. Labels may overlap across matched records; never replace them with a synthetic exclusive classification. Source-record counts remain available for reconciliation.
- Persistent left-sidebar checkbox filters cover organisations/repositories, publication types and years, with Select all, Clear and Reset. Active scope is visible. Selecting an organisation opens its detail; All organisations restores the overview while retaining year/type filters.
- Preserve source projections, mapping tables, matching links, file evidence, every metric SQL definition, intermediate calculations, hashes and run versions. SQL panels default to complete source queries against DuckLake, with local prepared-table queries separately labelled.
- Source data quality is being addressed separately. Continue using the existing evidence boundary and audit trail; this storytelling update does not redesign the source-quality work.

## 1. Overall institutional PDF coverage

**Reader question:** What share of the covered publication population has an institutional PDF recorded?

Use one horizontal proportion bar with the observed PDF percentage prominent and distinct publication counts beside it. The complementary segment is No institutional PDF observed. Show the selected publication period, covered repositories and observation date.

Denominator: distinct selected publication keys. Numerator: selected keys with institutional PDF evidence in the selected repository scope. A recorded URL is a custody proxy, not verification of retrieval or permanent preservation.

## 2. PDF coverage by source-reported publication access

**Reader question:** How does institutional PDF coverage differ across the access labels supplied by repositories?

Use aligned horizontal coverage bars with source-record counts, distinct publication counts and distinct PDF-bearing publication counts. Retain Open access, Restricted, Embargoed, Metadata only and Unknown. A publication can contribute to several source-label rows; publication row totals are not additive. The source-record column reconciles separately.

For each label, count the distinct selected keys with that label. Its PDF numerator uses records carrying that same label. Missing labels stay Unknown even where another record for the same publication has a known label. Publication access and attachment access remain separate fields.

## 3. Organisation comparison and existing drill-downs

**Reader question:** Where does institutional PDF coverage differ, and how large are the populations behind the percentages?

Keep the organisation comparison with PDF coverage, distinct publication volume and the count without observed institutional PDFs. Show counts alongside rates and avoid performance-league-table wording.

Selecting an organisation opens its publication-type and publication-year detail. Year is Publication year: these are cohorts at a single observation, rather than changes in deposit performance. Existing year/type filters also scope the planned publisher section.

Organisation totals overlap for jointly authored publications and must not be added into a national unique total.

## 4. Publisher-specific PDF gaps — proposed addition

### Decisions from the discussion

- Two linked charts: an overview covering all organisations, followed by all-publisher detail for one selected organisation.
- Each organisation has its **own** top three publisher groups, chosen by total distinct publication volume within that organisation and the active year/type filters.
- Plot missing-PDF percentages, not publisher market share. Each publisher has its own denominator.
- Combine imprints and spelling variants into parent publishing groups through an explicit, inspectable mapping.
- A source record listing multiple publishers is a metadata error. Do not choose the first publisher or assign the record to every publisher.
- Keep the initial drill-down focused on publishers. An additional timeline is not part of the proposed first implementation.

### Chart A: all organisations and their most important publishers

**Reader question:** For each organisation, how large is the PDF gap for its highest-volume publishers and its remaining publishers?

**Form:** A grouped horizontal bar chart. Each organisation forms a clearly separated block containing up to four bars: its top publisher, second publisher, third publisher, and Others. Publisher names are directly labelled within each block because the top three can differ between organisations.

All bars use a common 0–100% horizontal axis labelled **Publications without an institutional PDF (%)**. Use one consistent gap colour. Do not colour bars by volume rank: rank 1 can mean a different publisher in another organisation. Use organisation labels, spacing and direct values for grouping rather than a large colour legend.

Order publishers within an organisation by total publication volume; keep Others last. Do not select or reorder the top three by missing-PDF rate or missing-PDF count. Use a stable publisher-name tie-break when publication volumes are equal. Fewer than three eligible publishers means fewer named bars, without empty placeholders. Show an Others bar only when a remaining publisher population exists.

For each bar show **missing percentage** and supporting **missing / total publications**, for example `20% · 20 / 100`. Display names such as Elsevier, Springer Nature and Wiley rather than positional labels such as Publisher 1. A zero denominator is not a 0% rate.

Organisation blocks follow the organisation overview's ordering; publisher ranks are local to each block. Keep the plot vertically scrollable/readable rather than compressing all organisation labels and bars into one viewport.

**Title:** “Where are institutional PDFs missing among each organisation's largest publishers?” A finding-led subtitle can be added only when supported by the calculated matrix described below.

**Illustrative example — invented values, not source results:**

| Organisation | Local publisher group | Publication-volume rank | Missing PDF rate |
| --- | --- | --- | ---: |
| University A | Elsevier | 1 | 20% |
| University A | Springer Nature | 2 | 40% |
| University A | Wiley | 3 | 5% |
| University A | Others: remaining 20 publisher groups | — | 60% |
| University B | Its own three highest-volume groups + Others | Local ranking | Independently calculated |

The percentages are separate rates with separate denominators. **Do not stack the four percentages or force them to sum to 100%.**

### Exact calculations

For organisation `o` and normalised parent publisher `p`, within the active filters:

- `N(o,p)` = distinct publication keys assigned unambiguously to `p` for `o`, including publications both with and without a local PDF.
- `M(o,p)` = those distinct keys with no institutional PDF observed in organisation `o`.
- Displayed rate = `100 × M(o,p) / N(o,p)`.
- Top three = the three publisher groups with the largest `N(o,p)`, **not** the largest `M(o,p)` or `M(o,p)/N(o,p)`.

Others pools all eligible publisher groups outside that organisation's top three. Its numerator and denominator are calculated over the distinct publication-key union of those groups:

`Others rate = 100 × missing keys in the remaining groups / all keys in the remaining groups`.

This is a pooled rate, **not an unweighted mean of publisher percentages**, the percentage of publishers with missing PDFs, or the share of all missing PDFs attributable to other publishers. The number of publisher groups pooled into Others can appear as supporting context.

Changing years or types recalculates local publisher volumes, the top three and all rates. Selecting an organisation changes the detail view, not its PDF evidence scope or publisher-attribution rule. Never use a national publisher denominator for an organisation-specific rate.

### Chart B: all publishers for the selected organisation

**Reader question:** Which publisher groups account for the selected organisation's observed PDF gaps, considering publication volume as well as the percentage missing?

Selecting an organisation block or its label opens a linked detail chart below the overview. Show **all eligible publisher groups for that organisation**, including those previously pooled into Others. The title identifies the organisation and active years. Use horizontal bars on the same 0–100% scale, ordered by total publication volume, with missing / total counts and the missing percentage directly labelled.

Keep this as one publisher-comparison chart. The existing year/type filters allow focused comparisons without adding more simultaneous plots. Provide an obvious All organisations / Close detail action. A direct selection in the existing organisation comparison should select the same publisher detail.

When no organisation is selected, show a short “Select an organisation to inspect all its publishers” prompt in the detail area. Do not substitute a national publisher chart, which would change the question and denominator. Organisation filtering and chart selection must stay in sync; multiple selected organisations can remain in Chart A, while Chart B requires one explicit organisation.

### Cross-organisation storytelling

The intended insight is whether PDF gaps recur for the same publisher across organisations. Calculate this from the **full organisation × publisher matrix**, including publishers outside each organisation's displayed top three. A publisher hidden in Others is not absent from the analysis.

Any summary must state its coverage: how many organisations have publications from that publisher, their publication volumes, and the range of missing-PDF rates. For example: “Publisher X: missing-PDF rates range from A% to B% across K organisations with publications in this selection.” Values must be calculated, not inserted as a generic claim.

Use “all organisations” only if every organisation in the current comparison has a nonzero eligible denominator for that publisher. A publisher with no publications at an organisation has no rate there; it is not 0% missing. Do not describe gaps as consistently high without an agreed benchmark. A transparent range and organisation count support an initial observation without inventing a high/low threshold.

Keep the cross-organisation annotation brief. The overview and the drill-down provide the detailed evidence; a separate ranking, heatmap or timeline is not needed for this first addition.

### Publisher attribution and errors

Inspect the full source publisher array, `cerif:Publishers.cerif:Publisher`, rather than the original dashboard's first-publisher shortcut. Different language names for one publisher entry are not multiple publisher entries.

If a source record contains multiple publisher entries, flag **Publisher metadata error** before parent-group mapping. Do not silently resolve it by first entry, largest publisher or mapping every entry to a common parent. Conflicting parent-publisher assignments across matched records for the same organisation/publication must also be flagged rather than chosen arbitrarily.

Publications with unresolved publisher attribution remain in the overall organisation publication/PDF statistics, but are excluded from named-publisher ranking and rate calculations until attribution is resolved. Show their distinct count in publisher-section supporting context and make the source records inspectable. Missing publisher information is separately flagged as **Publisher not supplied**. Neither errors nor missing publisher information belongs in Others. This makes publisher-attributable coverage visible without silently losing publications from organisation totals.

Retain raw publisher entries, normalised names, parent-group assignments and mapping version. Reviewable alias/imprint mappings must precede ranking, so publisher spelling variants cannot occupy multiple top-three positions. Ambiguous mappings remain unresolved; they must not be guessed from loose substring matches.

The current retained baseline projection omitted publisher arrays. Before implementation, retain them from the same DuckLake snapshot and verify joins to existing record identities, as was done for author surnames. Preserve the old dashboard and metric runs for comparison.

### Timeline decision

**Recommendation:** use the all-publisher breakdown as the initial drill-down and the existing year filter for temporal focus. This keeps the detail focused on the stated question.

If temporal detail is requested later, offer a separate optional view for **publication-year cohort coverage** for one publisher. A genuine uptake timeline requires repeated comparable observation snapshots or deposit-history evidence. A single source snapshot cannot support a historical deposit-progress line.

### Acceptance checks for the later dashboard implementation

1. Different organisations can have different top-three publishers. A publisher with fewer missing PDFs still appears if its total publication volume places it in the top three.
2. The local top three uses publications both with and without PDFs; it is not ranked from the missing-PDF subset.
3. A test organisation with 20 missing PDFs out of 100 publications for Elsevier displays 20%, independent of other organisations or publishers.
4. If two remaining publishers have 1/10 and 90/100 missing, Others displays `91/110 = 82.7%`, not `(10% + 90%)/2 = 50%`.
5. Every rate numerator is a distinct-key subset of its own denominator. Shared institutional publications do not create duplicate counts within an organisation/publisher group.
6. One organisation's PDF cannot fill another organisation's local gap.
7. Clicking an organisation opens every eligible publisher group for that organisation, without an Others truncation. Clearing the selection restores the overview and keeps year/type filters.
8. Multiple publisher entries and conflicting assignments are inspectable errors; missing publisher information is separate. Neither enters Others or the top-three ranking.
9. Cross-organisation statements use the full matrix and show the number of organisations represented. Zero-volume cells do not enter rate summaries as zeroes.
10. Both charts retain exact source SQL, parent-group mapping, ranking, Others membership, numerators, denominators and results in the audit trail. Embeds preserve organisation/year/type scope and identify the selected organisation.

## 5. Redundancy across the available federation

**Reader question:** Is the institutional PDF observed in zero, one or at least two Dutch repositories?

Keep the 0 / 1 / 2+ distribution over selected distinct publication keys. A repository selection chooses the publication population; redundancy checks all available repositories for that population. It counts observed repository locations, not identical file versions or independent preservation systems.

The existing audit identifies a scope distinction between selected-record PDF coverage and federation-wide redundancy. Retain its explicit definition until a separate decision aligns those views; the publisher extension must use organisation-local PDF evidence.

## 6. Reported Taverne contribution

**Reader question:** What share of observed institutional PDF coverage carries the reported Taverne label?

Keep the primary percentage among institutional-PDF publication groups, with the percentage among all selected groups as supporting context. Follow the original exact first-file/first-licence `#text = 'taverne'` rule, deduplicated by publication key. A missing label is not proof of non-use. Retain discrepancies where a Taverne label appears without observed institutional PDF evidence.

## Supporting evidence and presentation

Non-PDF counts remain supporting detail: count distinct keys with institutional other formats and no matched PDF. Keep format and hosting evidence inspectable. Retain DURF typography, Theme 3 accent, shared navigation, light/dark behaviour and per-chart SQL/embed controls.

Existing source and matching limitations stay in the methods/audit material. Preserve the normal page-scrolling layout and the left filter sidebar; every story section remains reachable. The publisher proposal does not alter the existing dashboard until this storyboard is agreed and implementation is requested.
