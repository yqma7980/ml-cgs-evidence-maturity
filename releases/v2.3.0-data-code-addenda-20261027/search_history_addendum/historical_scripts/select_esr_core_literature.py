#!/usr/bin/env python3
"""Select a balanced ESR core literature matrix from the metadata seed."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "esr" / "literature" / "ESR_LITERATURE_MATRIX.csv"
OUT = ROOT / "esr" / "literature" / "ESR_CORE_LITERATURE_MATRIX.csv"

TARGETS = {
    "storage_context": 18,
    "review_positioning": 10,
    "pre_injection_decision": 10,
    "characterization": 14,
    "dynamic_prediction": 22,
    "physics_guided_learning": 8,
    "operation_control": 10,
    "monitoring_mrv": 14,
    "risk_response": 16,
    "seal_and_geomechanics": 12,
    "trapping_and_geochemistry": 12,
    "field_evidence": 20,
    "trustworthiness_methods": 10,
}

EXCLUDE_TITLE_PARTS = [
    "capture, transportation and geological storage",
    "aqueous formate solution",
    "enhanced oil recovery, geologic sequestration",
]


def score(row: dict[str, str]) -> tuple[int, int, str]:
    title = row["title"].lower()
    cited = int(row["crossref_referenced_by"] or 0)
    penalty = 0
    if any(part in title for part in EXCLUDE_TITLE_PARTS):
        penalty += 100000
    if not row["doi_or_url"]:
        penalty += 1000
    if row["year"] in {"", "None", "YYYY"}:
        penalty += 500
    # Prefer reviews, field evidence, and high cited items.
    boost = 0
    if "review" in title:
        boost += 150
    if row["data_type"] == "field_or_field_project":
        boost += 100
    if "machine learning" in title or "neural" in title:
        boost += 80
    return (penalty, -cited - boost, row["title"])


def main() -> int:
    rows = list(csv.DictReader(SEED.open(encoding="utf-8")))
    selected: list[dict[str, str]] = []
    seen_titles: set[str] = set()

    for stage, target in TARGETS.items():
        candidates = [row for row in rows if row["storage_stage"] == stage]
        candidates.sort(key=score)
        count = 0
        for row in candidates:
            normalized = row["title"].lower()
            if normalized in seen_titles:
                continue
            if score(row)[0] >= 100000:
                continue
            seen_titles.add(normalized)
            row = dict(row)
            row["content_screening_status"] = "core_metadata_screened_needs_full_text_check"
            selected.append(row)
            count += 1
            if count >= target:
                break

    selected.sort(key=lambda row: (row["storage_stage"], -int(row["crossref_referenced_by"] or 0), row["title"]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(selected[0].keys()))
        writer.writeheader()
        writer.writerows(selected)
    print(f"Wrote {len(selected)} rows to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

