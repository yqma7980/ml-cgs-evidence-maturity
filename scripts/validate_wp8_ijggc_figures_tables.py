from __future__ import annotations

import csv
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "evidence" / "WP4_CONSERVATIVE_ANALYSIS_CORE.csv"
FULL_CORE = ROOT / "evidence" / "FULL_TEXT_VERIFIED_CORE_CORPUS.csv"
BACKGROUND = ROOT / "evidence" / "BACKGROUND_NON_PRIMARY_ANCHORS.csv"
FIELD_MATRIX = ROOT / "evidence" / "FIELD_PROJECT_VALIDATION_MATRIX.csv"
FIG_ROOT = ROOT / "figures" / "ijggc" / "v1"
TABLE_ROOT = ROOT / "tables" / "ijggc" / "v1"
SUPP_ROOT = ROOT / "supplementary" / "ijggc" / "v1"
REPORT = ROOT / "validation" / "WP8_IJGGC_FIGURE_TABLE_VALIDATION.md"

FIGURES = {
    "Fig01": "Fig01_decision_chain_evidence_framework",
    "Fig02": "Fig02_evidence_regimes_by_application",
    "Fig03": "Fig03_missingness_aware_maturity_dimensions",
    "Fig04": "Fig04_validation_outcomes_by_application",
    "Fig05": "Fig05_field_anchor_evidence_roles",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def as_int(value: str) -> int:
    return int(float(value or 0))


def main() -> int:
    checks: list[tuple[str, bool, str]] = []

    def check(name: str, condition: bool, detail: str) -> None:
        checks.append((name, bool(condition), detail))

    analysis_core = read_csv(CORE)
    core = [row for row in analysis_core if row.get("wp4_main_claim_eligible", "").strip().lower() == "yes"]
    full_core = read_csv(FULL_CORE)
    background = read_csv(BACKGROUND)
    field_matrix = read_csv(FIELD_MATRIX)
    locked_ids = {row["paper_id"].strip() for row in full_core if row.get("paper_id", "").strip()}
    background_ids = {row["paper_id"].strip() for row in background if row.get("paper_id", "").strip()}
    field_anchor_ids = {row["source_paper_id"].strip() for row in field_matrix if row.get("source_paper_id", "").strip()}
    traceable_ids = locked_ids | background_ids | field_anchor_ids
    main_ids = {row["paper_id"].strip() for row in core if row.get("paper_id", "").strip()}
    check("main quantitative universe is N=57", len(core) == 57, f"N={len(core)}")
    check("locked full-text core remains available", len(full_core) >= 70, f"N={len(full_core)}")
    check("main IDs are a subset of the locked core", main_ids <= locked_ids, f"outside={sorted(main_ids - locked_ids)}")

    for figure_id, stem in FIGURES.items():
        for folder, extension in (("svg", "svg"), ("pdf", "pdf"), ("png", "png")):
            path = FIG_ROOT / folder / f"{stem}.{extension}"
            check(f"{figure_id} {extension} exists", path.exists() and path.stat().st_size > 1000, str(path.relative_to(ROOT)))
        data_path = FIG_ROOT / "data" / f"{figure_id}_plot_data.csv"
        check(f"{figure_id} plot data exists", data_path.exists() and data_path.stat().st_size > 20, str(data_path.relative_to(ROOT)))

    trace_path = FIG_ROOT / "data" / "FIGURE_TRACEABILITY.csv"
    trace = read_csv(trace_path)
    invalid_trace_ids: set[str] = set()
    for row in trace:
        for paper_id in row.get("source_paper_ids", "").split(";"):
            paper_id = paper_id.strip()
            if paper_id and paper_id not in traceable_ids:
                invalid_trace_ids.add(paper_id)
    check("all figure traceability IDs exist in locked primary or background evidence", not invalid_trace_ids, f"invalid={sorted(invalid_trace_ids)}")
    check("all five figures have traceability rows", set(FIGURES) <= {row["figure_id"] for row in trace}, f"figures={sorted({row['figure_id'] for row in trace})}")

    fig2 = read_csv(FIG_ROOT / "data" / "Fig02_plot_data.csv")
    fig2_total = sum(as_int(row["N"]) for row in fig2)
    check("Figure 2 retains all N=57 records", fig2_total == 57, f"sum={fig2_total}")

    fig3 = read_csv(FIG_ROOT / "data" / "Fig03_plot_data.csv")
    fig3_totals: dict[str, int] = {}
    for row in fig3:
        fig3_totals[row["dimension"]] = fig3_totals.get(row["dimension"], 0) + as_int(row["N"])
    check("Figure 3 uses N=57 for every dimension", len(fig3_totals) == 5 and all(value == 57 for value in fig3_totals.values()), str(fig3_totals))
    check("Figure 3 retains unknown/unreported separately", any(row["category"] == "Unknown / not reported" and as_int(row["N"]) > 0 for row in fig3), "unknown category present")

    fig4 = read_csv(FIG_ROOT / "data" / "Fig04_plot_data.csv")
    group_sizes: dict[str, int] = {}
    for row in fig4:
        group = row["application_group"]
        total = as_int(row["total_N"])
        group_sizes.setdefault(group, total)
        check(f"Figure 4 denominator stable for {group}", group_sizes[group] == total, f"N={total}")
        check(f"Figure 4 positive count bounded for {group}/{row['outcome']}", 0 <= as_int(row["positive_n"]) <= total, f"positive={row['positive_n']}; N={total}")
        check(f"Figure 4 missing count bounded for {group}/{row['outcome']}", 0 <= as_int(row["not_reported_n"]) <= total, f"NR={row['not_reported_n']}; N={total}")
    check("Figure 4 group denominators sum to N=57", sum(group_sizes.values()) == 57, str(group_sizes))

    for number in range(1, 5):
        matches = list(TABLE_ROOT.glob(f"Table{number:02d}_*.csv"))
        tex_matches = list(TABLE_ROOT.glob(f"Table{number:02d}_*.tex"))
        check(f"Table {number} CSV exists", len(matches) == 1 and matches[0].stat().st_size > 20, str([p.name for p in matches]))
        check(f"Table {number} LaTeX exists", len(tex_matches) == 1 and tex_matches[0].stat().st_size > 20, str([p.name for p in tex_matches]))

    table_trace_path = TABLE_ROOT / "TABLE_TRACEABILITY.csv"
    table_trace = read_csv(table_trace_path)
    check("four main tables have traceability", {"Table01", "Table02", "Table03", "Table04"} <= {row["table_id"] for row in table_trace}, f"rows={len(table_trace)}")

    supplement = sorted(SUPP_ROOT.glob("TableS*.csv"))
    check("six supplementary tables exist", len(supplement) == 6, f"count={len(supplement)}")
    forbidden_patterns = [
        re.compile(r"[A-Za-z]:\\"),
        re.compile(r"literature[/\\]full_text", re.I),
        re.compile(r"representative_quote_or_page_note", re.I),
        re.compile(r"pdf_path", re.I),
    ]
    leaks: list[str] = []
    for path in supplement:
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        if any(pattern.search(text) for pattern in forbidden_patterns):
            leaks.append(path.name)
    check("supplement contains no local PDF paths or quote-note fields", not leaks, f"flagged={leaks}")

    captions = FIG_ROOT / "Figure_Captions_IJGGC.md"
    caption_text = captions.read_text(encoding="utf-8") if captions.exists() else ""
    check("standalone captions cover Figures 1-5", all(f"**Figure {number}." in caption_text for number in range(1, 6)), str(captions.relative_to(ROOT)))
    check("captions define missingness conservatively", "not interpreted as score zero" in caption_text and "not interpreted as failures" in caption_text, "missingness language present")

    failed = [item for item in checks if not item[1]]
    lines = [
        "# WP8 IJGGC Figure and Table Validation",
        "",
        f"Status: {'PASS' if not failed else 'FAIL'}",
        "",
        f"Checks passed: {len(checks) - len(failed)}/{len(checks)}",
        "",
        "## Checks",
        "",
    ]
    for name, passed, detail in checks:
        lines.append(f"- [{'x' if passed else ' '}] {name}: {detail}")
    lines.extend(
        [
            "",
            "## Evidence boundary",
            "",
            "The locked 70-paper corpus was not modified. Main quantitative graphics use N=57. Unknown, unclear and not reported values remain distinct from score zero.",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"WP8 validation: {'PASS' if not failed else 'FAIL'} ({len(checks) - len(failed)}/{len(checks)})")
    print(REPORT)
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
