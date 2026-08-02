from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SUPP = ROOT / "supplementary" / "ijggc" / "wp9_8_r1"
SENSITIVITY = ROOT / "evidence" / "WP9_8_R1_SENSITIVITY_ANALYSIS_RESULTS.csv"
FIELD_REVIEW = ROOT / "evidence" / "WP9_8_R1_AUTHOR_VERIFIED_FIELD_OVERRIDES.csv"
METHOD_MAPPING = ROOT / "evidence" / "WP9_8_R1_METHOD_FAMILY_MAPPING.csv"
ANALYSIS_MANIFEST = ROOT / "validation" / "WP9_8_R1_ANALYSIS_MANIFEST.json"
FIG_S1_SOURCE = ROOT / "figures" / "ijggc" / "v2_wp8_r2" / "supplementary"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def build_journal_only_sensitivity() -> None:
    rows = [
        row
        for row in read_csv(SENSITIVITY)
        if row.get("scenario") == "peer_reviewed_journal_only"
        and row.get("metric") != "red_zone_recode_criticality"
    ]
    output: list[dict[str, str]] = []
    for row in rows:
        output.append(
            {
                "analysis_universe": "Peer-reviewed journal-only sensitivity set",
                "metric": row["metric"],
                "N": row["scenario_total_N"],
                "positive": row["numerator"],
                "available": row["denominator"],
                "missing_or_unavailable": row["missing_or_unavailable_n"],
                "observed_fraction_of_total": row["observed_fraction_of_scenario_total"],
                "positive_paper_ids": row["positive_paper_ids"],
                "interpretation": (
                    "Descriptive sensitivity count only; the corpus is not a random sample "
                    "and no population-prevalence inference is intended."
                ),
            }
        )
    if not output or {row["N"] for row in output} != {"36"}:
        raise RuntimeError("Journal-only sensitivity set is missing or is not N=36")
    write_csv(
        SUPP / "TableS09_journal_only_sensitivity.csv",
        output,
        [
            "analysis_universe",
            "metric",
            "N",
            "positive",
            "available",
            "missing_or_unavailable",
            "observed_fraction_of_total",
            "positive_paper_ids",
            "interpretation",
        ],
    )


def copy_review_ledgers() -> None:
    field_rows = read_csv(FIELD_REVIEW)
    method_rows = read_csv(METHOD_MAPPING)
    if len(field_rows) != 51:
        raise RuntimeError(f"Expected 51 signed field-review rows, found {len(field_rows)}")
    if len(method_rows) != 57:
        raise RuntimeError(f"Expected 57 method-mapping rows, found {len(method_rows)}")
    shutil.copy2(FIELD_REVIEW, SUPP / "TableS21_WP9_8_R1_author_verified_field_overrides.csv")
    shutil.copy2(METHOD_MAPPING, SUPP / "TableS22_WP9_8_R1_method_family_mapping.csv")
    shutil.copy2(ANALYSIS_MANIFEST, SUPP / "WP9_8_R1_ANALYSIS_MANIFEST.json")


def copy_screening_figure() -> None:
    for suffix in ("pdf", "png", "svg"):
        source = FIG_S1_SOURCE / f"FigS01_record_disposition.{suffix}"
        if not source.exists():
            raise FileNotFoundError(source)
        shutil.copy2(source, SUPP / source.name)


def validate_outputs() -> None:
    s9 = read_csv(SUPP / "TableS09_journal_only_sensitivity.csv")
    s21 = read_csv(SUPP / "TableS21_WP9_8_R1_author_verified_field_overrides.csv")
    s22 = read_csv(SUPP / "TableS22_WP9_8_R1_method_family_mapping.csv")
    author_reviewed = [row for row in s22 if row.get("wp9_8_r1_review_item_id", "").strip()]
    if {row["N"] for row in s9} != {"36"}:
        raise RuntimeError("Table S9 did not retain N=36")
    if len(s21) != 51 or len(author_reviewed) != 9:
        raise RuntimeError(
            f"Review-ledger mismatch: S21={len(s21)}, reviewed method mappings={len(author_reviewed)}"
        )
    manifest = json.loads((SUPP / "WP9_8_R1_ANALYSIS_MANIFEST.json").read_text(encoding="utf-8"))
    if manifest.get("main_N") != 57:
        raise RuntimeError("Analysis manifest does not report main N=57")


def main() -> None:
    SUPP.mkdir(parents=True, exist_ok=True)
    build_journal_only_sensitivity()
    copy_review_ledgers()
    copy_screening_figure()
    validate_outputs()
    print(SUPP)


if __name__ == "__main__":
    main()
