"""
Ingest one data-submission Issue Form into its theme's data.csv.

Reads the opened issue (body, author, labels) from environment variables set
by .github/workflows/ingest-submission.yml, maps the issue-form fields back
to column ids by their exact label text, appends one row -- plus who
submitted it, which issue it came from, and when -- to
notebooks/<slug>/data.csv, and writes the resolved slug (or nothing, if no
theme label matched) to $GITHUB_OUTPUT for the workflow to branch on.

No numeric parsing or validation here on purpose: whatever the submitter
typed is stored as plain text, so a maintainer can read and hand-edit the
CSV directly. The notebook that reads this file is responsible for coercing
specific columns to numeric dtypes (with errors="coerce", not a crash) when
it loads them -- see AGENTS.md.
"""

import csv
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

LABEL_TO_SLUG = {
    "theme-1-governance": "01-governance",
    "theme-2-metadata-quality": "02-metadata-quality",
    "theme-3-full-text-capture": "03-full-text-capture",
    "theme-4-edepot-archiving": "04-edepot-archiving",
    "theme-5-distribution-discovery": "05-distribution-discovery",
    "theme-6-nl-research-portal": "06-nl-research-portal",
}

# slug -> ordered [(issue-form label text, column id), ...]
THEME_FIELDS = {
    "01-governance": [
        ("Institution name", "institution"),
        ("NaMeCo membership status", "nameco_status"),
        ("Federation Rule Book agreement signed?", "rule_book_signed"),
        ("Signature date (if signed)", "rule_book_signed_date"),
        ("National Symposium / General Assembly attendance", "symposium_attendance"),
        (
            "Date of the most recent governance framework review affecting your institution",
            "last_governance_review",
        ),
    ],
    "02-metadata-quality": [
        ("Repository / CRIS name", "repo"),
        ("Share of records passing OAI application-profile validation", "compliance_pct"),
        ("Share of records with a ROR-identified institution", "ror_pct"),
        ("Share of records with an ORCID for at least one author", "orcid_pct"),
        ("Share of records with a DOI", "doi_pct"),
        ("Snapshot date", "snapshot_date"),
    ],
    "03-full-text-capture": [
        ("Repository / CRIS name", "repo"),
        ("Total metadata records", "total_records"),
        (
            "Records with a full-text PDF link hosted on your own institutional domain",
            "records_with_local_pdf",
        ),
        ("Snapshot date", "snapshot_date"),
    ],
    "04-edepot-archiving": [
        ("Repository / CRIS name", "repo"),
        ("PDFs present in the source repository", "pdfs_in_repo"),
        ("PDFs confirmed archived in the KB e-Depot", "pdfs_in_edepot"),
        (
            "URN:NBN resolution success rate for your institution's identifiers",
            "urn_nbn_resolution_pct",
        ),
        ("Snapshot date", "snapshot_date"),
    ],
    "05-distribution-discovery": [
        ("Repository / CRIS name", "repo"),
        ("Google Scholar inclusion-guideline compliance", "scholar_guideline_compliance_pct"),
        ("Grey-literature records with a local PDF but no DOI", "grey_lit_without_doi"),
        ("Of those, records that have since had a DOI minted", "grey_lit_doi_minted"),
        ("Snapshot date", "snapshot_date"),
    ],
    "06-nl-research-portal": [
        ("Institution name", "institution"),
        ("SURFconext SSO enabled?", "surfconext_sso_enabled"),
        ("SSO enablement date (if enabled)", "surfconext_sso_enabled_date"),
        (
            "Portal release version your institution is integrated with",
            "portal_release_version",
        ),
        ("Customer value / needs-assessment score", "needs_assessment_score"),
        ("Snapshot date", "snapshot_date"),
    ],
}

META_COLUMNS = ["submitted_by", "submitted_via_issue", "submitted_at"]

HEADER_RE = re.compile(r"^### (.+)$", re.MULTILINE)


def parse_issue_form_body(body: str) -> dict[str, str]:
    """Split a GitHub issue-form body into {label: value}, GitHub's own
    rendering: each field is a "### <label>" header followed by the
    response (or the literal "_No response_" if left blank)."""
    matches = list(HEADER_RE.finditer(body))
    fields = {}
    for i, m in enumerate(matches):
        label = m.group(1).strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        value = body[start:end].strip()
        if value == "_No response_":
            value = ""
        fields[label] = value
    return fields


def resolve_slug(labels: list[str]) -> str | None:
    for label in labels:
        if label in LABEL_TO_SLUG:
            return LABEL_TO_SLUG[label]
    return None


def append_row(slug: str, row: dict[str, str]) -> None:
    fieldnames = [col for _, col in THEME_FIELDS[slug]] + META_COLUMNS
    csv_path = REPO_ROOT / "notebooks" / slug / "data.csv"
    is_new = not csv_path.exists()
    with open(csv_path, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if is_new:
            writer.writeheader()
        writer.writerow({col: row.get(col, "") for col in fieldnames})


def main() -> None:
    labels = json.loads(os.environ["ISSUE_LABELS_JSON"])
    slug = resolve_slug(labels)

    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with open(output_path, "a") as f:
            f.write(f"slug={slug or ''}\n")

    if slug is None:
        print("No matching theme label found; leaving issue for manual handling.")
        return

    body_fields = parse_issue_form_body(os.environ["ISSUE_BODY"])
    row = {col: body_fields.get(label, "") for label, col in THEME_FIELDS[slug]}
    row["submitted_by"] = os.environ["ISSUE_AUTHOR"]
    row["submitted_via_issue"] = os.environ["ISSUE_NUMBER"]
    row["submitted_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    append_row(slug, row)
    print(f"Appended submission from @{row['submitted_by']} to notebooks/{slug}/data.csv")


if __name__ == "__main__":
    main()
