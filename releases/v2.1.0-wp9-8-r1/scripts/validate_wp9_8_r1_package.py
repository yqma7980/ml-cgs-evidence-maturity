from __future__ import annotations

import csv
import hashlib
import re
import zipfile
from pathlib import Path

import pypdfium2 as pdfium


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "submission" / "international-journal-of-greenhouse-gas-control" / "2026-08-01_wp9_8_r1_author_review_candidate"
PUBLIC = ROOT / "release" / "ijggc_wp9_8_r1_public_archive_candidate_2026-08-01_r1"
PDF = ROOT / "outputs" / "international_journal_of_greenhouse_gas_control_WP9_8_R1_AUTHOR_REVIEW.pdf"
TEX = ROOT / "outputs" / "international_journal_of_greenhouse_gas_control_WP9_8_R1_AUTHOR_REVIEW.tex"
ZIP = ROOT / "outputs" / "international_journal_of_greenhouse_gas_control_WP9_8_R1_AUTHOR_REVIEW_PACKAGE.zip"
REPORT = ROOT / "validation" / "WP9_8_R1_PACKAGE_VALIDATION.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def verify_manifest(folder: Path) -> tuple[bool, str]:
    manifest = folder / "FILE_MANIFEST_SHA256.csv"
    if not manifest.exists():
        return False, "manifest missing"
    rows = read_csv(manifest)
    bad = []
    for row in rows:
        path = folder / row["relative_path"]
        if not path.exists() or sha256(path) != row["sha256"]:
            bad.append(row["relative_path"])
    return not bad, f"{len(rows)} entries; bad={len(bad)}"


def main() -> int:
    checks: list[tuple[str, bool, str]] = []
    for path in (PACKAGE, PUBLIC, PDF, TEX, ZIP):
        checks.append((f"exists:{path.name}", path.exists(), str(path)))
    if not all(ok for _, ok, _ in checks):
        return finish(checks)

    document = pdfium.PdfDocument(str(PDF))
    page_count = len(document)
    extracted = []
    for index in range(page_count):
        page = document[index]
        text_page = page.get_textpage()
        extracted.append(text_page.get_text_range())
        text_page.close()
        page.close()
    document.close()
    text = "\n".join(extracted)
    checks.append(("pdf_pages", page_count == 42, str(page_count)))
    checks.append(("pdf_matches_package", sha256(PDF) == sha256(PACKAGE / "01_manuscript" / "main.pdf"), sha256(PDF)))

    normalized = re.sub(r"\s+", " ", text)
    tex_text = re.sub(r"\s+", " ", TEX.read_text(encoding="utf-8", errors="ignore"))
    current_phrases = (
        "70 full-text-verified primary ML-CGS records",
        "A claim-eligible subset of 57 primary records forms the quantitative synthesis",
    )
    for phrase in current_phrases:
        checks.append((f"current_source:{phrase}", phrase.lower() in tex_text.lower(), phrase))
    stale = (
        "3 / 3 / 26",
        "3/3/26",
        "11 full-text verified",
        "145 records still pending",
        "N=49",
        "N = 49",
        "RefNone",
        "information to verify",
        "Unknown authors",
        "TODO",
        "TBD",
    )
    for phrase in stale:
        checks.append((f"stale_absent:{phrase}", phrase.lower() not in normalized.lower(), phrase))

    table2 = read_csv(ROOT / "tables" / "ijggc" / "wp9_8_r1" / "Table02_core_evidence_summary.csv")
    sums = {
        "N": sum(int(row["N"]) for row in table2),
        "field": sum(int(row["field_evaluation"]) for row in table2),
        "controlled": sum(int(row["controlled_event"]) for row in table2),
        "ood": sum(int(row["OOD"]) for row in table2),
        "cross": sum(int(row["cross_site_or_setting"]) for row in table2),
        "uq": sum(int(row["calibrated_UQ_or_posterior"]) for row in table2),
        "physics": sum(int(row["physical_diagnostic"]) for row in table2),
        "surrogate": sum(int(row["surrogate_error_propagation"]) for row in table2),
    }
    expected = {"N": 57, "field": 5, "controlled": 5, "ood": 13, "cross": 1, "uq": 13, "physics": 23, "surrogate": 4}
    checks.append(("table2_vector", sums == expected, str(sums)))

    checks.append(("supplement_S1_rows", len(read_csv(PACKAGE / "02_supplementary" / "TableS01_main_claim_eligible_core.csv")) == 57, "expected 57"))
    checks.append(("supplement_S21_rows", len(read_csv(PACKAGE / "02_supplementary" / "TableS21_WP9_8_R1_author_verified_field_overrides.csv")) == 51, "expected 51"))
    checks.append(("supplement_S22_rows", len(read_csv(PACKAGE / "02_supplementary" / "TableS22_WP9_8_R1_method_family_mapping.csv")) == 57, "expected 57"))
    checks.append(("figure_S1_exists", (PACKAGE / "02_supplementary" / "FigS01_record_disposition.pdf").exists(), "screening flow"))
    checks.append(("codebook_exists", (PACKAGE / "02_supplementary" / "methods" / "JOURNAL_NEUTRAL_CODEBOOK_V2_WP9_3.md").exists(), "WP9.3 codebook"))

    forbidden_extensions = {".xlsx"}
    forbidden_names = []
    for folder in (PACKAGE, PUBLIC):
        for path in folder.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(folder).as_posix()
            if path.suffix.lower() in forbidden_extensions or "full_text" in relative.lower() or "literature/" in relative.lower():
                forbidden_names.append(f"{folder.name}/{relative}")
    checks.append(("no_internal_workbook_or_fulltext", not forbidden_names, ";".join(forbidden_names) or "clean"))

    local_path_hits = []
    for folder in (PACKAGE, PUBLIC):
        for path in folder.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".md", ".txt", ".csv", ".json", ".tex", ".bib", ".py"}:
                continue
            content = path.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"C:[\\/]Users[\\/]win11base|Desktop[\\/]machine learning", content, flags=re.I):
                local_path_hits.append(path.relative_to(folder).as_posix())
    checks.append(("no_local_absolute_paths", not local_path_hits, ";".join(local_path_hits) or "clean"))

    package_ok, package_detail = verify_manifest(PACKAGE)
    public_ok, public_detail = verify_manifest(PUBLIC)
    checks.append(("package_manifest", package_ok, package_detail))
    checks.append(("public_manifest", public_ok, public_detail))
    with zipfile.ZipFile(ZIP) as archive:
        names = archive.namelist()
    checks.append(("zip_nonempty", len(names) > 20, f"{len(names)} entries"))

    return finish(checks)


def finish(checks: list[tuple[str, bool, str]]) -> int:
    failed = [(name, detail) for name, ok, detail in checks if not ok]
    passed = len(checks) - len(failed)
    lines = [
        "# WP9.8-R1 package validation",
        "",
        f"- Result: {'PASS' if not failed else 'FAIL'}",
        f"- Checks passed: {passed}/{len(checks)}",
        f"- Checks failed: {len(failed)}",
        "",
        "## Checks",
        "",
        *[f"- {'PASS' if ok else 'FAIL'}: `{name}` ({detail})" for name, ok, detail in checks],
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"WP9.8-R1 package {'PASS' if not failed else 'FAIL'}: {passed}/{len(checks)}")
    for name, detail in failed:
        print(f"FAIL {name}: {detail}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
