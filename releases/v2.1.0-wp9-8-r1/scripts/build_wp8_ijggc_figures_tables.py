from __future__ import annotations

import csv
import json
import math
import os
import textwrap
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[2]
CORE = Path(os.environ.get("IJGGC_CORE_PATH", ROOT / "evidence" / "WP4_CONSERVATIVE_ANALYSIS_CORE.csv"))
DIMENSIONS = Path(os.environ.get("IJGGC_DIMENSIONS_PATH", ROOT / "evidence" / "DECISION_EVIDENCE_PROFILES.csv"))
OUTCOMES = Path(os.environ.get("IJGGC_OUTCOMES_PATH", ROOT / "evidence" / "WP4_VALIDATION_OUTCOME_PROFILES.csv"))
PACKAGES = ROOT / "evidence" / "WP5_MINIMUM_VALIDATION_PACKAGES.csv"
FIELD_SUMMARY = ROOT / "evidence" / "FIELD_PROJECT_VALIDATION_SUMMARY.csv"
POSITIONING = ROOT / "tables" / "journal_neutral" / "Table01_competing_review_positioning.csv"
PUBLICATION_METADATA = ROOT / "evidence" / "IJGGC_V2_PUBLICATION_METADATA.csv"
REFERENCE_METADATA_OVERRIDES = ROOT / "config" / "ijggc_v2_reference_metadata_overrides.json"

VERSION = os.environ.get("IJGGC_VERSION", "v1")

FIG_ROOT = ROOT / "figures" / "ijggc" / VERSION
FIG_SVG = FIG_ROOT / "svg"
FIG_PDF = FIG_ROOT / "pdf"
FIG_PNG = FIG_ROOT / "png"
FIG_DATA = FIG_ROOT / "data"
TABLE_ROOT = ROOT / "tables" / "ijggc" / VERSION
SUPP_ROOT = ROOT / "supplementary" / "ijggc" / VERSION
VALIDATION = ROOT / "validation"

MAIN_N = 57

GROUP_ORDER = [
    "Storage dynamics and surrogates",
    "Monitoring, inversion and updating",
    "Leakage, wellbore and containment risk",
    "Operation and control",
    "Screening and characterization",
    "Other / cross-cutting",
]

GROUP_SHORT = {
    "Storage dynamics and surrogates": "Storage dynamics\nand surrogates",
    "Monitoring, inversion and updating": "Monitoring, inversion\nand updating",
    "Leakage, wellbore and containment risk": "Leakage, wellbore\nand containment risk",
    "Operation and control": "Operation and control",
    "Screening and characterization": "Screening and\ncharacterization",
    "Other / cross-cutting": "Other / cross-cutting",
}

COLORS = {
    "navy": "#23415F",
    "blue": "#4C78A8",
    "teal": "#2A9D8F",
    "green": "#7DBE6C",
    "gold": "#E9C46A",
    "coral": "#E76F51",
    "pink": "#D979B3",
    "gray": "#B8BDC5",
    "light_gray": "#E9ECEF",
    "dark": "#24292F",
}


def configure_matplotlib() -> None:
    mpl.rcParams.update(
        {
            "font.family": "Times New Roman",
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "figure.titlesize": 13,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "axes.linewidth": 0.8,
            "axes.edgecolor": "#4B5563",
            "text.color": COLORS["dark"],
            "axes.labelcolor": COLORS["dark"],
            "xtick.color": COLORS["dark"],
            "ytick.color": COLORS["dark"],
        }
    )


def ensure_dirs() -> None:
    for path in [FIG_SVG, FIG_PDF, FIG_PNG, FIG_DATA, TABLE_ROOT, SUPP_ROOT, VALIDATION]:
        path.mkdir(parents=True, exist_ok=True)


def export_figure(fig: plt.Figure, stem: str) -> None:
    fig.savefig(FIG_SVG / f"{stem}.svg", bbox_inches="tight")
    fig.savefig(FIG_PDF / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(FIG_PNG / f"{stem}.png", dpi=600, bbox_inches="tight")
    plt.close(fig)


def display_group(value: str) -> str:
    if value in {"Unmapped applications", "Cross-cutting and other"}:
        return "Other / cross-cutting"
    return value


def regime_group(value: str) -> str:
    value = str(value).strip().lower()
    if value in {"synthetic simulation", "reduced-physics simulation / analytical regimes"}:
        return "Simulator-generated"
    if value in {"synthetic monitoring", "field-facing monitoring or synthetic monitoring"}:
        return "Synthetic monitoring"
    if value == "field-inspired simulation":
        return "Field-inspired simulation"
    if value == "single field case":
        return "Single field case"
    if value in {
        "field-derived database",
        "field-derived case study",
        "field-derived geospatial database",
        "field-derived reservoir database",
        "gis layers and geological screening criteria",
        "experimental/literature database",
    }:
        return "Field-/experiment-derived"
    return "Not reported"


def latex_escape(value: object) -> str:
    text = str(value)
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    core = pd.read_csv(CORE, dtype=str).fillna("")
    core = core[core["wp4_main_claim_eligible"].str.lower().eq("yes")].copy()
    if len(core) != MAIN_N:
        raise ValueError(f"Expected N={MAIN_N} claim-eligible rows, found {len(core)}")
    core["display_group"] = core["application_group"].map(display_group)
    core["display_regime"] = core["data_regime"].map(regime_group)
    # Correct bibliographic presentation fields without changing the locked
    # evidence coding or quantitative universe.
    if PUBLICATION_METADATA.exists():
        metadata = pd.read_csv(PUBLICATION_METADATA, dtype=str).fillna("")
        metadata = metadata[metadata["crossref_status"].str.lower().eq("resolved")].set_index("paper_id")
        for index, row in core.iterrows():
            paper_id = row["paper_id"]
            if paper_id not in metadata.index:
                continue
            resolved = metadata.loc[paper_id]
            replacements = {
                "title": resolved.get("corrected_title", ""),
                "authors": resolved.get("corrected_authors", ""),
                "year": resolved.get("corrected_year", ""),
                "venue": resolved.get("corrected_venue", ""),
                "doi_or_url": (
                    f"https://doi.org/{resolved.get('corrected_doi', '')}"
                    if resolved.get("corrected_doi", "")
                    else ""
                ),
                "peer_review_status": resolved.get("normalized_publication_status", ""),
            }
            for column, value in replacements.items():
                if value:
                    core.at[index, column] = value
    # Apply author-verified identity corrections after the legacy normalization
    # table so an earlier erroneous DOI match cannot overwrite them.
    overrides = json.loads(REFERENCE_METADATA_OVERRIDES.read_text(encoding="utf-8"))
    for index, row in core.iterrows():
        metadata = overrides.get(row["paper_id"])
        if not metadata:
            continue
        for column in (
            "title", "authors", "year", "venue", "doi_or_url", "peer_review_status"
        ):
            value = metadata.get(column, "")
            if value:
                core.at[index, column] = value
    # Full-text-verified correction: the legacy normalization table associated
    # this key with an unrelated Engineering article.
    lu_mask = core["paper_id"].eq("Lu2022_BayesianOptimization")
    if lu_mask.any():
        core.loc[lu_mask, "title"] = "Bayesian Optimization for Field-Scale Geological Carbon Storage"
        core.loc[lu_mask, "authors"] = (
            "Xueying Lu; Kirk E. Jordan; Mary F. Wheeler; "
            "Edward O. Pyzer-Knapp; Matthew Benatan"
        )
        core.loc[lu_mask, "year"] = "2022"
        core.loc[lu_mask, "venue"] = "Engineering"
        core.loc[lu_mask, "doi_or_url"] = "https://doi.org/10.1016/j.eng.2022.06.011"
        core.loc[lu_mask, "peer_review_status"] = "peer_reviewed_journal"
    dimensions = pd.read_csv(DIMENSIONS, dtype=str).fillna("")
    outcomes = pd.read_csv(OUTCOMES, dtype=str).fillna("")
    packages = pd.read_csv(PACKAGES, dtype=str).fillna("")
    field = pd.read_csv(FIELD_SUMMARY, dtype=str).fillna("")
    return core, dimensions, outcomes, packages, field


def figure_1_framework(packages: pd.DataFrame, trace: list[dict[str, object]]) -> None:
    stages = [
        ("Screen", "site and capacity"),
        ("Characterize", "properties and\nconnectivity"),
        ("Forecast", "pressure and plume"),
        ("Control", "rates and wells"),
        ("Monitor", "state and MRV"),
        ("Respond", "leakage and integrity"),
        ("Steward", "long term assurance"),
    ]
    layers = [
        "Provenance",
        "Geological\ncoverage",
        "Physical\ndiagnostics",
        "Uncertainty",
        "Transfer",
        "Field or\nexperiment",
        "Decision\nmetric",
        "Audit record",
    ]
    fig, ax = plt.subplots(figsize=(14.2, 7.2))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.03, 0.96, "Decision chain and evidence required for trustworthy ML-CGS", fontsize=15, weight="bold", va="top")
    ax.text(
        0.03,
        0.90,
        "The validation target changes with the storage decision; no single benchmark score establishes readiness across the chain.",
        fontsize=10.5,
        va="top",
    )
    stage_colors = ["#D9EEF4", "#DDEDD8", "#FFF1B8", "#F9D8B4", "#DDE3EA", "#F4CCCC", "#DCEAF2"]
    x0, width, gap = 0.030, 0.120, 0.018
    for idx, ((title, detail), color) in enumerate(zip(stages, stage_colors)):
        x = x0 + idx * (width + gap)
        box = FancyBboxPatch((x, 0.64), width, 0.18, boxstyle="round,pad=0.006,rounding_size=0.008", fc=color, ec="#6B7280", lw=0.9)
        ax.add_patch(box)
        ax.text(x + width / 2, 0.755, title, ha="center", va="center", fontsize=10.4, weight="bold")
        ax.text(x + width / 2, 0.690, detail, ha="center", va="center", fontsize=8.8, linespacing=1.05)
        if idx < len(stages) - 1:
            ax.add_patch(FancyArrowPatch((x + width + 0.002, 0.73), (x + width + gap - 0.002, 0.73), arrowstyle="-|>", mutation_scale=10, lw=0.9, color="#5B6570"))
    ax.text(0.03, 0.56, "Minimum evidence chain", fontsize=11.2, weight="bold", va="center")
    ax.text(0.03, 0.455, "Evidence foundation", fontsize=9.6, weight="bold", color="#374151", va="center")
    ax.text(0.03, 0.255, "Decision qualification", fontsize=9.6, weight="bold", color="#374151", va="center")
    lx0, lwidth, lgap = 0.185, 0.168, 0.030
    layer_colors = [COLORS["blue"], COLORS["teal"], COLORS["gold"], COLORS["pink"], COLORS["green"], COLORS["coral"], "#7A6FAC", COLORS["navy"]]
    for idx, (label, color) in enumerate(zip(layers, layer_colors)):
        row = idx // 4
        col = idx % 4
        x = lx0 + col * (lwidth + lgap)
        y = 0.390 if row == 0 else 0.190
        box = FancyBboxPatch((x, y), lwidth, 0.13, boxstyle="round,pad=0.005,rounding_size=0.008", fc=color, ec="white", lw=0.8)
        ax.add_patch(box)
        ax.text(x + lwidth / 2, y + 0.065, label, ha="center", va="center", color="white" if idx != 2 else COLORS["dark"], fontsize=9.1, weight="bold")
        if col < 3:
            ax.add_patch(FancyArrowPatch((x + lwidth + 0.003, y + 0.065), (x + lwidth + lgap - 0.003, y + 0.065), arrowstyle="-|>", mutation_scale=9, lw=0.8, color="#7C838A"))
    export_figure(fig, "Fig01_decision_chain_evidence_framework")
    pd.DataFrame(
        [
            {"element_type": "decision_stage", "order": i + 1, "label": title, "description": detail.replace("\n", " ")}
            for i, (title, detail) in enumerate(stages)
        ]
        + [
            {"element_type": "evidence_layer", "order": i + 1, "label": label.replace("\n", " "), "description": "Author synthesis from WP5 packages"}
            for i, label in enumerate(layers)
        ]
    ).to_csv(FIG_DATA / "Fig01_plot_data.csv", index=False)
    trace.append(
        {
            "figure_id": "Fig01",
            "visual_element": "decision chain and eight evidence layers",
            "aggregation_rule": "author synthesis from seven WP5 packages",
            "source_file": PACKAGES.relative_to(ROOT).as_posix(),
            "source_paper_ids": ";".join(sorted(set(";".join(packages["primary_support_ids"]).split(";")))),
            "source_paper_count": len(set(";".join(packages["primary_support_ids"]).split(";"))),
            "unknown_count": "NA",
            "notes": "Conceptual synthesis; not a quantitative maturity score.",
        }
    )


def figure_2_regimes(core: pd.DataFrame, trace: list[dict[str, object]]) -> pd.DataFrame:
    regimes = [
        "Simulator-generated",
        "Synthetic monitoring",
        "Field-inspired simulation",
        "Single field case",
        "Field-/experiment-derived",
        "Not reported",
    ]
    colors = [COLORS["blue"], COLORS["teal"], COLORS["coral"], COLORS["green"], COLORS["gold"], COLORS["gray"]]
    rows = []
    trace_rows = []
    for group in GROUP_ORDER:
        subset = core[core["display_group"].eq(group)]
        for regime in regimes:
            ids = sorted(subset.loc[subset["display_regime"].eq(regime), "paper_id"].tolist())
            rows.append({"application_group": group, "data_regime": regime, "N": len(ids)})
            trace_rows.append(
                {
                    "figure_id": "Fig02",
                    "visual_element": f"{group} | {regime}",
                    "aggregation_rule": "count of N=57 claim-eligible records after documented regime grouping",
                    "source_file": CORE.relative_to(ROOT).as_posix(),
                    "source_paper_ids": ";".join(ids),
                    "source_paper_count": len(ids),
                    "unknown_count": len(ids) if regime == "Not reported" else 0,
                    "notes": "Other/cross-cutting combines two one-record groups; no record is removed.",
                }
            )
    plot = pd.DataFrame(rows)
    plot.to_csv(FIG_DATA / "Fig02_plot_data.csv", index=False)
    trace.extend(trace_rows)
    pivot = plot.pivot(index="application_group", columns="data_regime", values="N").reindex(GROUP_ORDER).fillna(0)
    fig, ax = plt.subplots(figsize=(11.5, 6.5))
    left = np.zeros(len(GROUP_ORDER))
    y = np.arange(len(GROUP_ORDER))
    for regime, color in zip(regimes, colors):
        vals = pivot[regime].to_numpy(dtype=float)
        ax.barh(y, vals, left=left, color=color, edgecolor="white", linewidth=0.7, height=0.67, label=regime)
        for i, value in enumerate(vals):
            if value >= 2:
                ax.text(left[i] + value / 2, i, f"{int(value)}", ha="center", va="center", fontsize=8.5, color="white" if regime not in {"Field-/experiment-derived", "Not reported"} else COLORS["dark"], weight="bold")
        left += vals
    for i, total in enumerate(left):
        ax.text(total + 0.35, i, f"N={int(total)}", va="center", fontsize=9.5, weight="bold")
    ax.set_yticks(y, [GROUP_SHORT[g] for g in GROUP_ORDER])
    ax.invert_yaxis()
    ax.set_xlabel("Full-text verified, main-claim-eligible primary ML-CGS records")
    ax.set_xlim(0, max(left) + 3.2)
    ax.grid(axis="x", color="#D8DDE3", linewidth=0.6)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.legend(ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.01), frameon=False)
    ax.set_title("Simulator-generated evidence dominates the largest ML-CGS application groups", loc="left", pad=48, weight="bold")
    ax.text(0, -0.12, "Grouped display retains all 57 records. Gray denotes a regime that was not reported, not a zero score.", transform=ax.transAxes, fontsize=9, style="italic")
    export_figure(fig, "Fig02_evidence_regimes_by_application")
    return plot


def figure_3_dimensions(dimensions: pd.DataFrame, trace: list[dict[str, object]], core: pd.DataFrame) -> pd.DataFrame:
    dimension_order = [
        "field_evidence_score",
        "physical_consistency_score",
        "uncertainty_score",
        "transferability_score",
        "decision_readiness_score",
    ]
    labels = ["Field evidence", "Physical consistency", "Uncertainty", "Transferability", "Decision readiness"]
    all_rows = dimensions[(dimensions["application_group"].eq("ALL")) & dimensions["dimension"].isin(dimension_order)].copy()
    all_rows = all_rows.set_index("dimension").reindex(dimension_order).reset_index()
    records = []
    for _, row in all_rows.iterrows():
        for score in range(5):
            records.append({"dimension": row["dimension"], "category": f"Score {score}", "N": int(row[f"score_{score}_n"] or 0)})
        records.append({"dimension": row["dimension"], "category": "Unknown / not reported", "N": int(row["unscored_n"] or 0)})
        ids = sorted(core["paper_id"].tolist())
        trace.append(
            {
                "figure_id": "Fig03",
                "visual_element": row["dimension"],
                "aggregation_rule": "score distribution across N=57; unscored retained separately",
                "source_file": DIMENSIONS.relative_to(ROOT).as_posix(),
                "source_paper_ids": ";".join(ids),
                "source_paper_count": len(ids),
                "unknown_count": int(row["unscored_n"] or 0),
                "notes": "Unknown/not reported values are not included in any score bin.",
            }
        )
    plot = pd.DataFrame(records)
    plot.to_csv(FIG_DATA / "Fig03_plot_data.csv", index=False)
    categories = [f"Score {i}" for i in range(5)] + ["Unknown / not reported"]
    colors = ["#C8D6E5", COLORS["blue"], COLORS["teal"], COLORS["green"], COLORS["gold"], COLORS["light_gray"]]
    pivot = plot.pivot(index="dimension", columns="category", values="N").reindex(dimension_order).fillna(0)
    fig, ax = plt.subplots(figsize=(11.5, 5.8))
    left = np.zeros(len(dimension_order))
    y = np.arange(len(dimension_order))
    for category, color in zip(categories, colors):
        vals = pivot[category].to_numpy(dtype=float)
        ax.barh(y, vals, left=left, color=color, edgecolor="white", linewidth=0.7, height=0.62, label=category)
        for i, value in enumerate(vals):
            if value >= 4:
                ax.text(left[i] + value / 2, i, str(int(value)), ha="center", va="center", fontsize=8.5, color=COLORS["dark"], weight="bold")
        left += vals
    for i, (_, row) in enumerate(all_rows.iterrows()):
        high = int(row["score_ge3_n"] or 0)
        available = int(row["available_n"] or 0)
        ax.text(MAIN_N + 0.7, i, f"reported {available}/{MAIN_N}; score >=3: {high}", va="center", fontsize=9)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(0, MAIN_N + 18)
    ax.set_xlabel("Number of records")
    ax.axvline(MAIN_N, color="#5F6770", lw=0.8)
    ax.grid(axis="x", color="#D8DDE3", linewidth=0.6)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.legend(ncol=6, loc="lower center", bbox_to_anchor=(0.5, 1.02), frameon=False, columnspacing=1.2)
    ax.set_title("High-grade evidence is uncommon and missingness differs by maturity dimension", loc="left", pad=46, weight="bold")
    ax.text(0, -0.15, "Bars use the full N=57 denominator. The light-gray segment is unscored evidence, not score 0.", transform=ax.transAxes, fontsize=9, style="italic")
    export_figure(fig, "Fig03_missingness_aware_maturity_dimensions")
    return plot


OUTCOME_SPECS = [
    ("direct_field_validation", "Direct field\nevaluation"),
    ("controlled_release_ml_validation", "Controlled-event\nevaluation"),
    ("explicit_ood_testing", "Explicit OOD\ntesting"),
    ("explicit_cross_site_testing", "Cross-site / setting\ntesting"),
    ("uncertainty_calibration_or_posterior_check", "Calibrated UQ /\nposterior check"),
    ("surrogate_error_propagation", "Surrogate-error\npropagation"),
    ("any_physical_diagnostic_checked", "Any physical\ndiagnostic"),
]


def positive_ids(core: pd.DataFrame, outcome: str) -> list[str]:
    if outcome == "direct_field_validation":
        mask = core["field_validation_category"].isin(
            [
                "field_observation_comparison",
                "field_workflow_evaluation",
                "operating_storage_site_evaluation",
            ]
        )
    elif outcome == "controlled_release_ml_validation":
        mask = core["controlled_release_validation_state"].eq("ml_evaluated_on_controlled_release")
    elif outcome == "explicit_ood_testing":
        mask = core["ood_test_category"].isin(
            [
                "legacy_explicit_ood_test",
                "cross_site_heldout",
                "unseen_parameter_range",
                "unseen_geology_or_faults",
                "unseen_schedule_or_boundary",
            ]
        )
    elif outcome == "explicit_cross_site_testing":
        mask = core["cross_site_test_state"].isin(
            ["explicit_heldout_cross_site_test", "cross_site_validated"]
        )
    elif outcome == "uncertainty_calibration_or_posterior_check":
        mask = core["uncertainty_calibration_category"].isin(
            [
                "legacy_uncertainty_calibration_or_posterior_check",
                "calibrated_or_posterior_checked",
                "posterior_predictive_check",
                "calibration_or_interval_reliability_test",
            ]
        )
    elif outcome == "surrogate_error_propagation":
        mask = core["surrogate_error_propagation_category"].isin(
            ["legacy_surrogate_error_propagation", "propagated_into_inference_or_decision"]
        )
    elif outcome == "any_physical_diagnostic_checked":
        diagnostic_cols = [
            "mass_conservation_diagnostic",
            "pressure_threshold_diagnostic",
            "plume_volume_diagnostic",
            "geomechanics_diagnostic",
            "geochemistry_diagnostic",
            "rock_physics_diagnostic",
            "sensor_physics_diagnostic",
        ]
        mask = core[diagnostic_cols].eq("diagnostic_checked").any(axis=1)
    else:
        raise KeyError(outcome)
    return sorted(core.loc[mask, "paper_id"].tolist())


def synchronize_package_status(packages: pd.DataFrame, core: pd.DataFrame) -> pd.DataFrame:
    """Recompute the seven WP5 package summaries from the current reviewed core."""
    synchronized = packages.copy()
    known_ids = set(core["paper_id"])
    assigned_ids: list[str] = []
    statuses: list[str] = []

    for _, row in synchronized.iterrows():
        support_ids = [item for item in str(row["primary_support_ids"]).split(";") if item]
        missing = sorted(set(support_ids) - known_ids)
        if missing:
            raise ValueError(
                f"Package {row['package_id']} contains IDs absent from the N={len(core)} core: {missing}"
            )
        assigned_ids.extend(support_ids)
        subset = core[core["paper_id"].isin(support_ids)].copy()
        status = (
            f"N={len(subset)}; "
            f"field={len(positive_ids(subset, 'direct_field_validation'))}; "
            f"controlled={len(positive_ids(subset, 'controlled_release_ml_validation'))}; "
            f"OOD={len(positive_ids(subset, 'explicit_ood_testing'))}; "
            f"cross-site={len(positive_ids(subset, 'explicit_cross_site_testing'))}; "
            f"UQ/posterior={len(positive_ids(subset, 'uncertainty_calibration_or_posterior_check'))}; "
            f"surrogate-error={len(positive_ids(subset, 'surrogate_error_propagation'))}; "
            f"physical-diagnostic={len(positive_ids(subset, 'any_physical_diagnostic_checked'))}"
        )
        statuses.append(status)

    if len(assigned_ids) != len(core) or set(assigned_ids) != known_ids:
        duplicates = sorted({paper_id for paper_id in assigned_ids if assigned_ids.count(paper_id) > 1})
        unassigned = sorted(known_ids - set(assigned_ids))
        raise ValueError(
            "WP5 package membership must partition the reviewed core exactly; "
            f"assignments={len(assigned_ids)}, unique={len(set(assigned_ids))}, "
            f"duplicates={duplicates}, unassigned={unassigned}"
        )

    synchronized["current_verified_status"] = statuses
    return synchronized


def figure_4_outcomes(core: pd.DataFrame, outcomes: pd.DataFrame, trace: list[dict[str, object]]) -> pd.DataFrame:
    source = outcomes[outcomes["outcome"].isin([x[0] for x in OUTCOME_SPECS]) & ~outcomes["application_group"].eq("ALL")].copy()
    source["display_group"] = source["application_group"].map(display_group)
    numeric_cols = ["total_N", "positive_n", "not_reported_n", "unclear_n"]
    for col in numeric_cols:
        source[col] = pd.to_numeric(source[col], errors="coerce").fillna(0).astype(int)
    grouped = source.groupby(["display_group", "outcome"], as_index=False)[numeric_cols].sum()
    rows = []
    for group in GROUP_ORDER:
        group_core = core[core["display_group"].eq(group)]
        for outcome, label in OUTCOME_SPECS:
            entry = grouped[(grouped["display_group"].eq(group)) & (grouped["outcome"].eq(outcome))]
            if entry.empty:
                total = len(group_core)
                positive = 0
                not_reported = total
                unclear = 0
            else:
                total = int(entry.iloc[0]["total_N"])
                positive = int(entry.iloc[0]["positive_n"])
                not_reported = int(entry.iloc[0]["not_reported_n"])
                unclear = int(entry.iloc[0]["unclear_n"])
            outcome_positive = set(positive_ids(group_core, outcome))
            rows.append(
                {
                    "application_group": group,
                    "outcome": outcome,
                    "outcome_label": label.replace("\n", " "),
                    "total_N": total,
                    "positive_n": positive,
                    "positive_fraction_total": positive / total if total else math.nan,
                    "not_reported_n": not_reported,
                    "unclear_n": unclear,
                }
            )
            trace.append(
                {
                    "figure_id": "Fig04",
                    "visual_element": f"{group} | {outcome}",
                    "aggregation_rule": "positive count divided by full application-group denominator; missing retained",
                    "source_file": OUTCOMES.relative_to(ROOT).as_posix(),
                    "source_paper_ids": ";".join(sorted(outcome_positive)),
                    "source_paper_count": len(outcome_positive),
                    "unknown_count": not_reported + unclear,
                    "notes": "Cell annotation is positive/total; NR reports not-reported count.",
                }
            )
    plot = pd.DataFrame(rows)
    plot.to_csv(FIG_DATA / "Fig04_plot_data.csv", index=False)
    matrix = np.zeros((len(GROUP_ORDER), len(OUTCOME_SPECS)))
    fig, ax = plt.subplots(figsize=(12.2, 6.7))
    for i, group in enumerate(GROUP_ORDER):
        for j, (outcome, _) in enumerate(OUTCOME_SPECS):
            row = plot[(plot["application_group"].eq(group)) & plot["outcome"].eq(outcome)].iloc[0]
            matrix[i, j] = row["positive_fraction_total"]
    cmap = mpl.colors.LinearSegmentedColormap.from_list("evidence", ["#F3F4F6", "#B7DFD8", "#2A9D8F", "#1F5D58"])
    image = ax.imshow(matrix, cmap=cmap, vmin=0, vmax=max(0.5, float(np.nanmax(matrix))), aspect="auto")
    for i, group in enumerate(GROUP_ORDER):
        for j, (outcome, _) in enumerate(OUTCOME_SPECS):
            row = plot[(plot["application_group"].eq(group)) & plot["outcome"].eq(outcome)].iloc[0]
            ax.text(j, i - 0.08, f"{int(row['positive_n'])}/{int(row['total_N'])}", ha="center", va="center", fontsize=9, weight="bold")
            ax.text(j, i + 0.22, f"NR {int(row['not_reported_n'])}", ha="center", va="center", fontsize=7.6, color="#4B5563")
    ax.set_xticks(np.arange(len(OUTCOME_SPECS)), [x[1] for x in OUTCOME_SPECS])
    ax.set_yticks(np.arange(len(GROUP_ORDER)), [GROUP_SHORT[g] for g in GROUP_ORDER])
    ax.tick_params(axis="x", top=True, bottom=False, labeltop=True, labelbottom=False, pad=8)
    ax.set_xticks(np.arange(-0.5, len(OUTCOME_SPECS), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(GROUP_ORDER), 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=2)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.spines[:].set_visible(False)
    cbar = fig.colorbar(image, ax=ax, fraction=0.025, pad=0.03)
    cbar.set_label("Positive records / full group N", rotation=90)
    ax.set_title("Decision-relevant validation outcomes remain uneven and frequently unreported", loc="left", pad=58, weight="bold")
    ax.text(0, -0.15, "Each cell shows positive/total and the number not reported (NR). Missingness is not interpreted as failure.", transform=ax.transAxes, fontsize=9, style="italic")
    export_figure(fig, "Fig04_validation_outcomes_by_application")
    return plot


def figure_5_field_anchors(field: pd.DataFrame, trace: list[dict[str, object]]) -> pd.DataFrame:
    plot = field[[
        "project_group",
        "primary_ml_validation_count",
        "field_or_mechanism_background_count",
        "benchmark_design_anchor_count",
        "source_paper_ids",
    ]].copy()
    count_cols = ["primary_ml_validation_count", "field_or_mechanism_background_count", "benchmark_design_anchor_count"]
    for col in count_cols:
        plot[col] = pd.to_numeric(plot[col], errors="coerce").fillna(0).astype(int)
    plot["total_relations"] = plot[count_cols].sum(axis=1)
    plot = plot.sort_values(["total_relations", "project_group"], ascending=[True, True]).reset_index(drop=True)
    plot.to_csv(FIG_DATA / "Fig05_plot_data.csv", index=False)
    fig, ax = plt.subplots(figsize=(11.5, 8.2))
    y = np.arange(len(plot))
    left = np.zeros(len(plot))
    labels = ["Direct primary ML evaluation", "Field / mechanism context", "Benchmark-design anchor"]
    colors = [COLORS["coral"], COLORS["teal"], COLORS["gold"]]
    for col, label, color in zip(count_cols, labels, colors):
        vals = plot[col].to_numpy(dtype=float)
        ax.barh(y, vals, left=left, height=0.65, color=color, edgecolor="white", linewidth=0.7, label=label)
        for i, value in enumerate(vals):
            if value >= 1:
                ax.text(left[i] + value / 2, i, str(int(value)), ha="center", va="center", fontsize=8.5, weight="bold", color=COLORS["dark"])
        left += vals
    ax.set_yticks(y, plot["project_group"])
    ax.set_xlabel("Source-site relations in the field-anchor synthesis")
    ax.set_xlim(0, max(left) + 1)
    ax.grid(axis="x", color="#D8DDE3", linewidth=0.6)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.legend(ncol=3, loc="lower center", bbox_to_anchor=(0.5, 1.01), frameon=False)
    ax.set_title("Field projects contribute different kinds of evidence to ML validation", loc="left", pad=44, weight="bold")
    ax.text(0, -0.10, "A named field project is not automatically direct ML field validation; evidence roles are counted separately.", transform=ax.transAxes, fontsize=9, style="italic")
    export_figure(fig, "Fig05_field_anchor_evidence_roles")
    for _, row in plot.iterrows():
        ids = [x for x in str(row["source_paper_ids"]).split(";") if x]
        trace.append(
            {
                "figure_id": "Fig05",
                "visual_element": row["project_group"],
                "aggregation_rule": "count of source-site relations by evidence role",
                "source_file": FIELD_SUMMARY.relative_to(ROOT).as_posix(),
                "source_paper_ids": ";".join(ids),
                "source_paper_count": len(ids),
                "unknown_count": 0,
                "notes": "Direct ML, context, and benchmark-design roles are mutually classified at relation level.",
            }
        )
    return plot


def write_table_01() -> None:
    src = pd.read_csv(POSITIONING, dtype=str).fillna("")
    src.to_csv(TABLE_ROOT / "Table01_review_positioning.csv", index=False)
    selected = src.head(6)
    existing_contribution = {
        "Yan et al. (2021)": "Surveys machine-learning applications across the wider CCUS chain.",
        "Li et al. (2023)": "Integrates storage mechanisms, project experience, and emerging ML applications.",
        "Mao and Jahanbani Ghahfarokhi (2024)": "Reviews intelligent decision-making across geological storage workflows.",
        "Li et al. (2024)": "Synthesizes statistical and computational methods, including uncertainty treatment.",
        "Marvin et al. (2025)": "Connects ML progress to monitoring, uncertainty, anomaly detection, and application needs.",
        "Lin et al. (2025)": "Provides broad coverage of ML methods and geological-storage applications.",
    }
    present_review_distinction = {
        "Yan et al. (2021)": "Restricts the evidence synthesis to storage decisions and their validation requirements.",
        "Li et al. (2023)": "Separates primary ML evidence from mechanism, project-context, and benchmark-design anchors.",
        "Mao and Jahanbani Ghahfarokhi (2024)": "Uses a verified, missingness-aware corpus to qualify decision claims.",
        "Li et al. (2024)": "Links evidence maturity to seven decision-specific minimum validation packages.",
        "Marvin et al. (2025)": "Traces every quantitative element to verified records while retaining missing evidence explicitly.",
        "Lin et al. (2025)": "Uses non-compensatory packages to distinguish demonstrations from broader decision support.",
    }
    lines = [
        r"\begin{table}[!htbp]",
        r"\centering",
        r"\caption{Positioning of the present review relative to recent geological CO$_2$ storage and ML reviews.}",
        r"\label{tab:positioning}",
        r"\small",
        r"\setlength{\tabcolsep}{4pt}",
        r"\begin{tabularx}{\textwidth}{>{\RaggedRight\arraybackslash}p{0.16\textwidth} >{\RaggedRight\arraybackslash}p{0.18\textwidth} >{\RaggedRight\arraybackslash}p{0.25\textwidth} >{\RaggedRight\arraybackslash}X}",
        r"\toprule",
        r"Review & Principal scope & Existing contribution & Distinction of the present review \\",
        r"\midrule",
    ]
    for _, row in selected.iterrows():
        review = row["review"]
        distinction = present_review_distinction.get(
            review,
            "Decision-centered evidence maturity with explicit treatment of missing verification evidence.",
        )
        lines.append(
            "{} & {} & {} & {} \\\\".format(
                latex_escape(review),
                latex_escape(row["scope"]),
                latex_escape(existing_contribution.get(review, row["positioning_implication"])),
                latex_escape(distinction),
            )
        )
    lines += [r"\bottomrule", r"\end{tabularx}", r"\end{table}"]
    (TABLE_ROOT / "Table01_review_positioning.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")


def application_gap(group: str) -> str:
    return {
        "Storage dynamics and surrogates": "Field comparison, calibrated uncertainty, and downstream error propagation remain sparse.",
        "Monitoring, inversion and updating": "Field-facing examples exist, but cross-setting validation and audit-ready updates remain limited.",
        "Leakage, wellbore and containment risk": "Rare-event, pathway, and representative field evidence remain insufficient for deployment claims.",
        "Operation and control": "Evidence is mainly simulation based; operational field anchoring is absent in the coded subset.",
        "Screening and characterization": "Small heterogeneous evidence base; triage has not been shown to certify dynamic capacity.",
        "Other / cross-cutting": "Too few records for a stable application-level maturity interpretation.",
    }[group]


def write_table_02(core: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for group in GROUP_ORDER:
        subset = core[core["display_group"].eq(group)]
        regime = subset["display_regime"].value_counts().idxmax() if len(subset) else "NA"
        rows.append(
            {
                "application_group": group,
                "N": len(subset),
                "dominant_evidence_regime": regime,
                "field_evaluation": len(positive_ids(subset, "direct_field_validation")),
                "controlled_event": len(positive_ids(subset, "controlled_release_ml_validation")),
                "OOD": len(positive_ids(subset, "explicit_ood_testing")),
                "cross_site_or_setting": len(positive_ids(subset, "explicit_cross_site_testing")),
                "calibrated_UQ_or_posterior": len(positive_ids(subset, "uncertainty_calibration_or_posterior_check")),
                "physical_diagnostic": len(positive_ids(subset, "any_physical_diagnostic_checked")),
                "surrogate_error_propagation": len(positive_ids(subset, "surrogate_error_propagation")),
                "main_evidence_gap": application_gap(group),
            }
        )
    table = pd.DataFrame(rows)
    table.to_csv(TABLE_ROOT / "Table02_core_evidence_summary.csv", index=False)
    lines = [
        r"\begin{table}[!htbp]",
        r"\centering",
        r"\caption{Evidence summary for the N=57 main-claim-eligible primary ML-CGS records. Counts report positively identified evidence; unreported fields are not treated as absence.}",
        r"\label{tab:core-summary}",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{3.5pt}",
        r"\begin{tabularx}{\textwidth}{>{\RaggedRight\arraybackslash}p{0.16\textwidth} c >{\RaggedRight\arraybackslash}p{0.13\textwidth} c c c c c c c >{\RaggedRight\arraybackslash}X}",
        r"\toprule",
        r"Application group & N & Dominant regime & Field & Controlled & OOD & Cross & UQ & Physics & Error prop. & Main evidence gap \\",
        r"\midrule",
    ]
    for _, row in table.iterrows():
        lines.append(
            "{} & {} & {} & {} & {} & {} & {} & {} & {} & {} & {} \\\\".format(
                latex_escape(row["application_group"]),
                row["N"],
                latex_escape(row["dominant_evidence_regime"]),
                row["field_evaluation"],
                row["controlled_event"],
                row["OOD"],
                row["cross_site_or_setting"],
                row["calibrated_UQ_or_posterior"],
                row["physical_diagnostic"],
                row["surrogate_error_propagation"],
                latex_escape(row["main_evidence_gap"]),
            )
        )
    lines += [r"\bottomrule", r"\end{tabularx}", r"\end{table}"]
    (TABLE_ROOT / "Table02_core_evidence_summary.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return table


def compact_requirement(row: pd.Series) -> str:
    summaries = {
        "P1_screening_capacity": (
            "Represent basin geology and reservoir-caprock variability; distinguish static resource proxies from "
            "dynamic injectivity, pressure, and containment; test ranking uncertainty and withheld basins."
        ),
        "P2_pressure_control": (
            "Represent connectivity, boundaries, faults, injectivity, and pressure-sensitive geomechanics; check mass "
            "balance, pressure thresholds, constraints, and schedule stress tests; propagate uncertainty to decision loss."
        ),
        "P3_plume_trapping": (
            "Cover claimed geology, fluids, grids, schedules, and boundaries; diagnose mass balance, plume edge and "
            "volume, pressure, saturation, trapping, and temporal error; propagate surrogate discrepancy."
        ),
        "P4_monitoring_mrv": (
            "Represent reservoir, overburden, rock-physics, survey, and detectability variability; check forward and "
            "posterior predictive consistency across modalities; test changed surveys, noise, geology, and sites."
        ),
        "P5_leakage_response": (
            "Represent pathways, rates, backgrounds, noise, and non-leak alternatives; check signal-pathway physics and "
            "detectability; evaluate alarm reliability, base-rate effects, transfer, and response consequences."
        ),
        "P6_wellbore_integrity": (
            "Represent well classes, materials, completion histories, fluids, pressures, and degradation; link risk to "
            "flow-path, cement, casing, and geochemical mechanisms; test population transfer with integrity evidence."
        ),
        "P7_geomechanics_seal": (
            "Represent faults, stresses, caprock properties, pressure paths, and heterogeneity; diagnose coupled "
            "pressure-stress, slip, deformation, breakthrough, seismicity, and containment under propagated uncertainty."
        ),
    }
    return summaries[str(row["package_id"])]


def write_table_03(packages: pd.DataFrame) -> pd.DataFrame:
    table = packages[["package_id", "storage_decision", "hidden_variable_or_risk", "current_verified_status", "current_evidence_gap", "claim_boundary"]].copy()
    table["minimum_validation_logic"] = packages.apply(compact_requirement, axis=1)
    table.to_csv(TABLE_ROOT / "Table03_minimum_validation_packages.csv", index=False)
    lines = [
        r"\begingroup",
        r"\footnotesize",
        r"\setlength{\tabcolsep}{3pt}",
        r"\begin{longtable}{>{\RaggedRight\arraybackslash}p{0.15\textwidth} >{\RaggedRight\arraybackslash}p{0.17\textwidth} >{\RaggedRight\arraybackslash}p{0.29\textwidth} >{\RaggedRight\arraybackslash}p{0.15\textwidth} >{\RaggedRight\arraybackslash}p{0.17\textwidth}}",
        r"\caption{Decision-specific minimum validation packages proposed by this review. The packages are qualification frameworks, not regulatory thresholds; complete package specifications are provided in Supplementary Table S4.}\label{tab:minimum-packages}\\",
        r"\toprule",
        r"Storage decision & Hidden variable or risk & Minimum validation logic & Verified-core status & Main evidence gap \\",
        r"\midrule",
        r"\endfirsthead",
        r"\multicolumn{5}{c}{\tablename\ \thetable{} -- continued}\\",
        r"\toprule",
        r"Storage decision & Hidden variable or risk & Minimum validation logic & Verified-core status & Main evidence gap \\",
        r"\midrule",
        r"\endhead",
        r"\bottomrule",
        r"\endfoot",
    ]
    for idx, row in packages.iterrows():
        requirement = compact_requirement(row)
        status = (
            row["current_verified_status"]
            .replace("UQ/posterior", "UQ or posterior")
            .replace("surrogate-error", "surrogate error")
            .replace("physical-diagnostic", "physical diagnostic")
        )
        lines.append(
            "{} & {} & {} & {} & {} \\\\".format(
                latex_escape(row["storage_decision"]),
                latex_escape(row["hidden_variable_or_risk"]),
                latex_escape(requirement),
                latex_escape(status),
                latex_escape(row["current_evidence_gap"]),
            )
        )
    lines.extend([r"\end{longtable}", r"\endgroup"])
    (TABLE_ROOT / "Table03_minimum_validation_packages.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return table


def write_table_04(field: pd.DataFrame) -> pd.DataFrame:
    selected_groups = ["Cranfield", "Frio pilots", "Sleipner", "CO2CRC Otway", "In Salah", "Illinois Basin / IBDP", "Aquistore", "ZERT"]
    selected = field[field["project_group"].isin(selected_groups)].copy()
    selected["evidence_roles"] = selected.apply(
        lambda r: f"direct ML={r['primary_ml_validation_count']}; context={r['field_or_mechanism_background_count']}; benchmark={r['benchmark_design_anchor_count']}",
        axis=1,
    )
    table = selected[["project_group", "project_or_experiment_names", "evidence_roles", "validation_implication", "main_limitation", "source_paper_ids"]]
    table.to_csv(TABLE_ROOT / "Table04_field_anchor_implications.csv", index=False)
    lines = [
        r"\begingroup",
        r"\small",
        r"\setlength{\tabcolsep}{3pt}",
        r"\begin{longtable}{>{\RaggedRight\arraybackslash}p{0.12\textwidth} >{\RaggedRight\arraybackslash}p{0.17\textwidth} >{\RaggedRight\arraybackslash}p{0.13\textwidth} >{\RaggedRight\arraybackslash}p{0.27\textwidth} >{\RaggedRight\arraybackslash}p{0.23\textwidth}}",
        r"\caption{Selected field projects and controlled experiments as validation anchors. Role counts distinguish direct primary ML evaluation from geoscience context and benchmark design.}\label{tab:field-anchors}\\",
        r"\toprule",
        r"Project group & Project or experiment & Evidence roles & Validation implication & Boundary or limitation \\",
        r"\midrule",
        r"\endfirsthead",
        r"\multicolumn{5}{c}{\tablename\ \thetable{} -- continued}\\",
        r"\toprule",
        r"Project group & Project or experiment & Evidence roles & Validation implication & Boundary or limitation \\",
        r"\midrule",
        r"\endhead",
        r"\bottomrule",
        r"\endfoot",
    ]
    for _, row in selected.iterrows():
        lines.append(
            "{} & {} & {} & {} & {} \\\\".format(
                latex_escape(row["project_group"]),
                latex_escape(row["project_or_experiment_names"]),
                latex_escape(row["evidence_roles"]),
                latex_escape(row["validation_implication"]),
                latex_escape(row["main_limitation"]),
            )
        )
    lines.extend([r"\end{longtable}", r"\endgroup"])
    (TABLE_ROOT / "Table04_field_anchor_implications.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return table


def write_supplement(core: pd.DataFrame, dimensions: pd.DataFrame, outcomes: pd.DataFrame, packages: pd.DataFrame, field: pd.DataFrame, trace: pd.DataFrame) -> None:
    core_public_cols = [
        "paper_id", "title", "authors", "year", "venue", "doi_or_url", "peer_review_status",
        "storage_stage", "application_area", "application_group", "decision_supported", "data_regime",
        "field_case", "ml_method_family", "target_outputs", "validation_type", "field_validation_category",
        "controlled_release_validation_state", "ood_test_category", "cross_site_test_state",
        "uncertainty_calibration_category", "surrogate_error_propagation_category",
        "mass_conservation_diagnostic", "pressure_threshold_diagnostic", "plume_volume_diagnostic",
        "geomechanics_diagnostic", "geochemistry_diagnostic", "rock_physics_diagnostic",
        "sensor_physics_diagnostic", "field_evidence_score_state", "physical_consistency_score_state",
        "uncertainty_score_state", "transferability_score_state", "decision_readiness_score_state",
        "wp4_main_claim_eligible",
    ]
    core[core_public_cols].to_csv(SUPP_ROOT / "TableS01_main_claim_eligible_core.csv", index=False)
    dimension_drop = [
        column for column in dimensions.columns
        if "proportion" in column.lower() or "wilson" in column.lower()
    ]
    outcome_drop = [
        column for column in outcomes.columns
        if "proportion" in column.lower() or "fraction" in column.lower() or "wilson" in column.lower()
    ]
    dimensions.drop(columns=dimension_drop, errors="ignore").to_csv(
        SUPP_ROOT / "TableS02_decision_evidence_profiles.csv", index=False
    )
    outcomes.drop(columns=outcome_drop, errors="ignore").to_csv(
        SUPP_ROOT / "TableS03_validation_outcome_profiles.csv", index=False
    )
    packages.to_csv(SUPP_ROOT / "TableS04_minimum_validation_packages_full.csv", index=False)
    field.to_csv(SUPP_ROOT / "TableS05_field_anchor_summary.csv", index=False)
    trace.to_csv(SUPP_ROOT / "TableS06_figure_traceability.csv", index=False)


def write_captions() -> None:
    captions = """# IJGGC main-figure captions

**Figure 1. Decision chain and evidence required for trustworthy machine learning in geological CO2 storage.** The figure links seven storage-decision stages to eight minimum evidence layers. Its message is that validation is decision specific and non-compensatory: strong performance in one layer cannot substitute for missing geological coverage, physical diagnostics, uncertainty, transfer, field or experimental evidence, decision metrics, or an audit record. This is an author synthesis derived from the seven validation packages, not a quantitative maturity score.

**Figure 2. Evidence regimes by ML-CGS application group in the N=57 main-claim-eligible corpus.** Simulator-generated evidence dominates storage dynamics, monitoring/inversion, operation/control, and containment-risk applications. All 57 records are retained; two one-record categories are grouped as other/cross-cutting for readability. Gray indicates that the evidence regime was not reported and is not interpreted as score zero.

**Figure 3. Missingness-aware evidence-maturity dimensions for the N=57 quantitative universe.** Field evidence, physical consistency, uncertainty, transferability, and decision readiness are shown as full-denominator score distributions, with unscored records retained separately. High-grade evidence (score at least 3) is uncommon in every dimension, while the amount of unreported evidence differs markedly across dimensions. The plot therefore supports a missingness-aware interpretation rather than a single compensatory readiness average.

**Figure 4. Decision-relevant validation outcomes by application group.** Each cell reports the number of positively identified records over the full group denominator and separately reports the number not reported (NR). Explicit OOD testing is more common than direct field evaluation, cross-site or cross-setting testing, calibrated uncertainty or posterior checks, and surrogate-error propagation. Missing fields are evidence gaps and are not interpreted as failures of individual studies.

**Figure 5. Evidence roles of field projects and controlled experiments in the field-anchor synthesis.** Source-site relations are separated into direct primary ML evaluation, field or mechanism context, and benchmark-design roles. The figure shows why citing a field project does not by itself constitute ML field validation: most projects currently define mechanisms, monitoring realism, or benchmark requirements, while direct evaluation of an ML workflow is concentrated in a small number of relations.
"""
    (FIG_ROOT / "Figure_Captions_IJGGC.md").write_text(captions, encoding="utf-8")


def main() -> None:
    configure_matplotlib()
    ensure_dirs()
    core, dimensions, outcomes, packages, field = load_data()
    packages = synchronize_package_status(packages, core)
    trace: list[dict[str, object]] = []
    figure_1_framework(packages, trace)
    fig2 = figure_2_regimes(core, trace)
    fig3 = figure_3_dimensions(dimensions, trace, core)
    fig4 = figure_4_outcomes(core, outcomes, trace)
    fig5 = figure_5_field_anchors(field, trace)
    trace_df = pd.DataFrame(trace)
    trace_df.to_csv(FIG_DATA / "FIGURE_TRACEABILITY.csv", index=False)
    write_table_01()
    table2 = write_table_02(core)
    table3 = write_table_03(packages)
    table4 = write_table_04(field)
    table_trace = pd.DataFrame(
        [
            {"table_id": "Table01", "source_file": POSITIONING.relative_to(ROOT).as_posix(), "source_paper_ids": "competing reviews", "source_count": len(pd.read_csv(POSITIONING))},
            {"table_id": "Table02", "source_file": CORE.relative_to(ROOT).as_posix(), "source_paper_ids": ";".join(sorted(core.paper_id)), "source_count": len(core)},
            {"table_id": "Table03", "source_file": PACKAGES.relative_to(ROOT).as_posix(), "source_paper_ids": ";".join(sorted(set(";".join(packages.primary_support_ids).split(";")))), "source_count": len(set(";".join(packages.primary_support_ids).split(";")))},
            {"table_id": "Table04", "source_file": FIELD_SUMMARY.relative_to(ROOT).as_posix(), "source_paper_ids": ";".join(sorted(set(";".join(table4.source_paper_ids).split(";")))), "source_count": len(set(";".join(table4.source_paper_ids).split(";")))},
        ]
    )
    table_trace.to_csv(TABLE_ROOT / "TABLE_TRACEABILITY.csv", index=False)
    write_supplement(core, dimensions, outcomes, packages, field, trace_df)
    write_captions()
    report = f"""# WP8 Figure and Table Build Report

Status: BUILD COMPLETE

## Locked inputs

- Full verified primary corpus: 70 records (not modified)
- Main quantitative universe: {len(core)} records
- WP5 packages: {len(packages)}
- Field project/experiment groups: {len(field)}

## Outputs

- Main figures: 5, each exported as SVG, PDF, and 600 dpi PNG
- Main tables: 4, each with CSV and LaTeX source
- Supplementary tables: 6
- Figure traceability rows: {len(trace_df)}
- Table traceability rows: {len(table_trace)}

## Evidence boundaries

- Unknown, unclear, and not reported values remain distinct from score zero.
- Figure 2 retains all N=57 records after a documented display grouping.
- Figure 4 uses the full application-group denominator and reports missingness.
- Field anchors are separated into direct ML, geoscience context, and benchmark-design roles.
- No copyrighted full text or local PDF path is included in the supplementary outputs.
"""
    (VALIDATION / "WP8_FIGURE_TABLE_BUILD_REPORT.md").write_text(report, encoding="utf-8")
    print(f"WP8 build complete: {FIG_ROOT}")


if __name__ == "__main__":
    main()
