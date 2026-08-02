from __future__ import annotations

import csv
import hashlib
import json
import shutil
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "manuscript" / "international-journal-of-greenhouse-gas-control-wp9-8-r1"
OUTPUTS = ROOT / "outputs"
PACKAGE = (
    ROOT
    / "submission"
    / "international-journal-of-greenhouse-gas-control"
    / "2026-08-01_wp9_8_r1_author_review_candidate"
)
PUBLIC = ROOT / "release" / "ijggc_wp9_8_r1_public_archive_candidate_2026-08-01_r1"
SUPP = ROOT / "supplementary" / "ijggc" / "wp9_8_r1"
FIGS = ROOT / "figures" / "ijggc" / "wp9_8_r1"
WP9_FIGS = ROOT / "figures" / "wp9_7"

PDF_OUT = OUTPUTS / "international_journal_of_greenhouse_gas_control_WP9_8_R1_AUTHOR_REVIEW.pdf"
TEX_OUT = OUTPUTS / "international_journal_of_greenhouse_gas_control_WP9_8_R1_AUTHOR_REVIEW.tex"
ZIP_OUT = OUTPUTS / "international_journal_of_greenhouse_gas_control_WP9_8_R1_AUTHOR_REVIEW_PACKAGE.zip"


def copy_file(source: Path, target: Path) -> None:
    if not source.exists():
        raise FileNotFoundError(source)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manifest(folder: Path) -> Path:
    output = folder / "FILE_MANIFEST_SHA256.csv"
    rows: list[dict[str, str | int]] = []
    for path in sorted(folder.rglob("*")):
        if not path.is_file() or path == output:
            continue
        rows.append(
            {
                "relative_path": path.relative_to(folder).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["relative_path", "size_bytes", "sha256"])
        writer.writeheader()
        writer.writerows(rows)
    return output


def copy_main_outputs() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    copy_file(SOURCE / "main.pdf", PDF_OUT)
    copy_file(SOURCE / "main.tex", TEX_OUT)


def copy_main_figures(target: Path) -> None:
    for path in sorted(FIGS.rglob("*")):
        if path.is_file():
            copy_file(path, target / path.relative_to(FIGS))
    for stem in (
        "FigWP9_02_method_family_evidence_obligations_qualitative",
        "FigWP9_03_geological_context_validation_gaps_qualitative",
        "FigWP9_04_actionable_deployment_roadmap",
    ):
        for fmt in ("pdf", "svg", "png", "tiff"):
            source = WP9_FIGS / fmt / f"{stem}.{fmt}"
            if source.exists():
                copy_file(source, target / fmt / source.name)


def build_author_review_package() -> None:
    if PACKAGE.exists():
        shutil.rmtree(PACKAGE)

    manuscript = PACKAGE / "01_manuscript"
    supplement = PACKAGE / "02_supplementary"
    figures = PACKAGE / "03_figures"
    review = PACKAGE / "04_author_review"

    for name in (
        "main.pdf",
        "main.tex",
        "references_submission_cleaned_v3.bib",
        "elsarticle.cls",
        "elsarticle-harv.bst",
        "Table01_review_positioning.tex",
        "Table02_core_evidence_summary.tex",
        "Table03_minimum_validation_packages.tex",
        "Table04_field_anchor_implications.tex",
    ):
        copy_file(SOURCE / name, manuscript / name)
    for name in (
        "Fig01_decision_chain_evidence_framework.pdf",
        "Fig02_evidence_regimes_by_application.pdf",
        "Fig03_missingness_aware_maturity_dimensions.pdf",
        "Fig04_validation_outcomes_by_application.pdf",
        "Fig05_field_anchor_evidence_roles.pdf",
        "FigWP9_02_method_family_evidence_obligations.pdf",
        "FigWP9_03_geological_context_validation_gaps.pdf",
        "FigWP9_04_actionable_deployment_roadmap.pdf",
    ):
        copy_file(SOURCE / name, manuscript / name)

    for path in sorted(SUPP.iterdir()):
        if path.is_file():
            copy_file(path, supplement / path.name)
    copy_file(ROOT / "evidence" / "JOURNAL_NEUTRAL_CODEBOOK_V2_WP9_3.md", supplement / "methods" / "JOURNAL_NEUTRAL_CODEBOOK_V2_WP9_3.md")
    copy_file(ROOT / "evidence" / "scoring_rubric.md", supplement / "methods" / "scoring_rubric.md")
    copy_main_figures(figures)

    for name in (
        "WP9_8_R1_INTEGRATION_REPORT.md",
        "WP9_8_R1_FIGURE_TABLE_DESIGN_REPORT.md",
        "WP9_8_R1_SYNC_REBUILD_REPORT.md",
        "WP9_8_R1_VISUAL_QA.md",
        "WP9_8_R1_GO_NO_GO.md",
        "WP9_8_R1_WORK_PACKAGE_STATUS.md",
    ):
        source = ROOT / "validation" / name
        if source.exists():
            copy_file(source, review / name)

    readme = """# WP9.8-R1 author-review candidate

This is an author-review package, not a direct journal-upload bundle.

- `01_manuscript` contains the synchronized PDF and editable LaTeX source.
- `02_supplementary` contains Supplementary Tables S1-S22, supplementary figures, and coding rules.
- `03_figures` contains the editable and review-resolution figure exports.
- `04_author_review` contains validation reports and is not a journal attachment.

The locked core contains 70 full-text-verified primary records. The main quantitative universe is N=57. WP9.8-R1 applies 51 signed field decisions across 37 papers and nine signed method-family mappings. No literature PDF or internal author workbook is included.
"""
    (PACKAGE / "README.md").write_text(readme, encoding="utf-8")
    write_manifest(PACKAGE)


def build_public_archive_candidate() -> None:
    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    data = PUBLIC / "data"
    methods = PUBLIC / "methods"
    figures = PUBLIC / "figures"
    scripts = PUBLIC / "scripts"
    reports = PUBLIC / "reports"

    for path in sorted(SUPP.iterdir()):
        if path.is_file():
            copy_file(path, data / path.name)
    for name in (
        "WP9_8_R1_AUTHOR_VERIFIED_FIELD_OVERRIDES.csv",
        "WP9_8_R1_AUTHOR_VERIFIED_METHOD_MAPPINGS.csv",
        "WP9_8_R1_AUTHOR_VERIFIED_ANALYSIS_CORE.csv",
        "WP9_8_R1_METHOD_FAMILY_MAPPING.csv",
        "WP9_8_R1_DECISION_EVIDENCE_PROFILES.csv",
        "WP9_8_R1_EVIDENCE_REGIME_PROFILES.csv",
        "WP9_8_R1_VALIDATION_OUTCOME_PROFILES.csv",
        "WP9_8_R1_SENSITIVITY_ANALYSIS_RESULTS.csv",
    ):
        copy_file(ROOT / "evidence" / name, data / "analysis" / name)
    copy_file(ROOT / "evidence" / "JOURNAL_NEUTRAL_CODEBOOK_V2_WP9_3.md", methods / "JOURNAL_NEUTRAL_CODEBOOK_V2_WP9_3.md")
    copy_file(ROOT / "evidence" / "scoring_rubric.md", methods / "scoring_rubric.md")
    copy_main_figures(figures)
    for name in (
        "integrate_wp9_8_r1_author_review.py",
        "extract_wp9_8_author_review.mjs",
        "finalize_wp9_8_r1_supplement.py",
        "validate_wp9_8_r1.py",
        "build_wp8_ijggc_figures_tables.py",
        "build_wp9_8_r1_package.py",
        "validate_wp9_8_r1_package.py",
    ):
        copy_file(ROOT / "scripts" / "journal_neutral" / name, scripts / name)
    for name in (
        "WP9_8_R1_INTEGRATION_REPORT.md",
        "WP9_8_R1_FIGURE_TABLE_DESIGN_REPORT.md",
        "WP9_8_R1_SYNC_REBUILD_REPORT.md",
        "WP9_8_R1_VISUAL_QA.md",
    ):
        source = ROOT / "validation" / name
        if source.exists():
            copy_file(source, reports / name)

    metadata = {
        "release_status": "local_public_archive_candidate_not_deposited",
        "analysis_version": "WP9.8-R1-AUTHOR-VERIFIED-2026-08-01",
        "locked_core_N": 70,
        "main_quantitative_N": 57,
        "signed_field_decisions": 51,
        "papers_with_signed_field_decisions": 37,
        "signed_method_family_mappings": 9,
        "rights_note": "No copyrighted full-text PDFs are included.",
    }
    (PUBLIC / "RELEASE_METADATA.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    (PUBLIC / "README.md").write_text(
        "# WP9.8-R1 local public-archive candidate\n\n"
        "This candidate contains the author-verified analysis tables, supplementary files, coding rules, figure data, figures, and deterministic generation scripts. It has not been uploaded and has no new DOI. No copyrighted article PDF or internal signed workbook is included.\n",
        encoding="utf-8",
    )
    write_manifest(PUBLIC)


def build_zip() -> None:
    if ZIP_OUT.exists():
        ZIP_OUT.unlink()
    with zipfile.ZipFile(ZIP_OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(PACKAGE.rglob("*")):
            if path.is_file():
                archive.write(path, arcname=(Path(PACKAGE.name) / path.relative_to(PACKAGE)).as_posix())


def main() -> None:
    copy_main_outputs()
    build_author_review_package()
    build_public_archive_candidate()
    build_zip()
    for path in (PDF_OUT, TEX_OUT, PACKAGE, PUBLIC, ZIP_OUT):
        print(path)


if __name__ == "__main__":
    main()
