from __future__ import annotations

import csv
import html
import math
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "esr/LITERATURE_MATRIX.csv"
EVIDENCE_DIR = ROOT / "evidence"
FIG_DIR = ROOT / "figures/esr"
TABLE_DIR = ROOT / "tables/esr"
BOX_DIR = ROOT / "boxes"
VALIDATION_DIR = ROOT / "validation/esr"


FIELD_CASES = [
    "Sleipner",
    "In Salah",
    "Otway",
    "Frio",
    "Cranfield",
    "Decatur",
    "Aquistore",
    "Ketzin",
    "Weyburn",
    "Quest",
    "Illinois Basin",
]

APPLICATION_ORDER = [
    "site screening",
    "capacity estimation",
    "seismic inversion",
    "multiphysics inversion",
    "pressure surrogate",
    "plume/saturation surrogate",
    "neural operator surrogate",
    "GNN/faulted reservoir",
    "PINN/physics-guided migration",
    "Bayesian history matching",
    "monitoring design/MRV",
    "injection optimization",
    "RL control",
    "leakage detection",
    "wellbore leakage risk",
    "geomechanics/seal risk",
    "geochemistry/trapping",
    "field project context",
    "competing review",
    "trustworthy ML method",
    "other storage ML",
]

CONSTRAINTS = [
    "mass conservation",
    "pressure constraint",
    "relative permeability",
    "capillarity",
    "hysteresis",
    "buoyancy/gravity",
    "fault transmissibility",
    "geomechanics",
    "geochemistry/reactive transport",
    "rock physics",
    "sensor physics",
]


def ensure_dirs() -> None:
    for folder in [EVIDENCE_DIR, FIG_DIR, TABLE_DIR, BOX_DIR, VALIDATION_DIR]:
        folder.mkdir(parents=True, exist_ok=True)


def clean(text: str | None) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text).replace("\u2010", "-").replace("\u2011", "-").replace("\u2013", "-").replace("\u2014", "-").strip()


def norm(text: str | None) -> str:
    return clean(text).lower()


def contains(text: str, *words: str) -> bool:
    return any(word.lower() in text for word in words)


def detect_field_case(title: str, existing: str = "") -> str:
    found = []
    haystack = f"{title} {existing}"
    for case in FIELD_CASES:
        if case.lower() in haystack.lower():
            found.append(case)
    return "; ".join(found) if found else "none identified"


def infer_application(row: dict[str, str]) -> str:
    title = norm(row.get("title"))
    stage = norm(row.get("storage_stage"))

    if contains(title, "review") and not contains(title, "machine learning", "deep learning", "neural"):
        return "competing review"
    if contains(title, "machine learning for co2 geological storage", "machine-learning-driven"):
        return "competing review"
    if contains(stage, "trustworthiness"):
        return "trustworthy ML method"
    if contains(title, "leak", "leakage", "anomaly"):
        return "leakage detection"
    if contains(title, "geomech", "seismicity", "caprock", "seal", "fault", "breakthrough pressure", "surface deformation", "insar"):
        return "geomechanics/seal risk"
    if contains(title, "history matching", "data assimilation", "mcmc", "ensemble kalman", "posterior"):
        return "Bayesian history matching"
    if contains(title, "monitoring", "mrv", "verification", "time-lapse", "4d", "insar", "conformance"):
        if contains(title, "seismic inversion", "full waveform", "seismic full waveform", "saturation"):
            return "seismic inversion"
        return "monitoring design/MRV"
    if contains(title, "site", "suitability", "screening") and contains(title, "storage"):
        return "site screening"
    if contains(title, "capacity", "resource", "potential"):
        return "capacity estimation"
    if contains(title, "wellbore", "well leakage", "abandoned well"):
        return "wellbore leakage risk"
    if contains(title, "reinforcement learning"):
        return "RL control"
    if contains(title, "optimization", "pressure management", "control"):
        return "injection optimization"
    if contains(title, "multiphysics", "gravity and seismic", "electromagnetic"):
        return "multiphysics inversion"
    if contains(title, "seismic", "full-waveform", "seisco2net", "saturation estimation"):
        return "seismic inversion"
    if contains(title, "fourier neural operator", "neural operator", "operator learning", "u-fno", "fno", "wavelet neural operator"):
        return "neural operator surrogate"
    if contains(title, "graph neural", "gnn", "faulted"):
        return "GNN/faulted reservoir"
    if contains(title, "physics-informed", "physics informed", "pinn", "physics-constrained"):
        return "PINN/physics-guided migration"
    if contains(title, "physics coupled", "physics-informed", "physics inspired"):
        return "PINN/physics-guided migration"
    if contains(title, "pressure"):
        return "pressure surrogate"
    if contains(title, "plume", "saturation", "migration"):
        return "plume/saturation surrogate"
    if contains(title, "mineral", "reactive", "geochemical", "trapping", "basalt", "dissolution", "wettability"):
        return "geochemistry/trapping"
    if contains(title, "analog", "experience", "barendrecht"):
        return "field project context"
    if contains(stage, "field"):
        return "field project context"
    if contains(stage, "storage_context"):
        return "capacity estimation"
    if contains(stage, "trapping"):
        return "geochemistry/trapping"
    return "other storage ML"


def scope_status(row: dict[str, str]) -> tuple[str, str]:
    title = norm(row.get("title"))
    if contains(title, "supercritical co2 cycles"):
        return "exclude", "supercritical CO2 cycle control is outside geological storage scope"
    if contains(title, "co2 eor", "enhanced oil recovery", "co2 flooding", "flooding prediction", "flooding attribute"):
        if contains(title, "storage", "geological storage", "geologic storage", "geological carbon storage", "geologic carbon storage"):
            return "include_with_scope_note", "includes EOR/flooding language but also storage; use only for storage-relevant evidence"
        return "exclude", "CO2-EOR/flooding without clear geological-storage decision scope"
    if contains(title, "capture, transport") and not contains(title, "geologic storage", "geological storage"):
        return "include_with_scope_note", "broad CCUS context; use only for storage background"
    return "include", ""


def infer_stage(application: str, existing: str) -> str:
    if existing:
        return existing
    mapping = {
        "site screening": "pre_injection_decision",
        "capacity estimation": "pre_injection_decision",
        "seismic inversion": "characterization",
        "multiphysics inversion": "characterization",
        "pressure surrogate": "dynamic_prediction",
        "plume/saturation surrogate": "dynamic_prediction",
        "neural operator surrogate": "dynamic_prediction",
        "GNN/faulted reservoir": "dynamic_prediction",
        "PINN/physics-guided migration": "physics_guided_learning",
        "Bayesian history matching": "monitoring_mrv",
        "monitoring design/MRV": "monitoring_mrv",
        "injection optimization": "operation_control",
        "RL control": "operation_control",
        "leakage detection": "risk_response",
        "wellbore leakage risk": "risk_response",
        "geomechanics/seal risk": "seal_and_geomechanics",
        "geochemistry/trapping": "trapping_and_geochemistry",
        "competing review": "review_positioning",
        "trustworthy ML method": "trustworthiness_methods",
    }
    return mapping.get(application, "other")


def infer_data_regime(row: dict[str, str], application: str) -> str:
    title = norm(row.get("title"))
    data_type = norm(row.get("data_type"))
    field_case = detect_field_case(row.get("title", ""), row.get("field_case", ""))
    if application in {"competing review", "trustworthy ML method"}:
        return "review/synthesis"
    if field_case != "none identified":
        return "single field case"
    if contains(title, "controlled release", "release field experiment", "field release"):
        return "controlled release"
    if contains(title, "laboratory", "core", "pore-scale", "experimental"):
        return "laboratory"
    if contains(data_type, "field"):
        return "single field case"
    if contains(data_type, "monitoring", "geophysical"):
        return "field-facing monitoring or synthetic monitoring"
    if contains(data_type, "simulation", "model") or contains(title, "simulation", "surrogate", "operator", "modeling", "forecast"):
        return "synthetic simulation"
    return "unknown"


def infer_data_source(title: str, data_regime: str) -> str:
    text = norm(title)
    sources = []
    for key, label in [
        ("seismic", "seismic/time-lapse seismic"),
        ("pressure", "pressure"),
        ("gravity", "gravity"),
        ("electromagnetic", "electromagnetic"),
        ("em ", "electromagnetic"),
        ("insar", "surface deformation/InSAR"),
        ("deformation", "surface deformation"),
        ("geochem", "geochemistry"),
        ("groundwater", "groundwater"),
        ("well", "well/wellbore"),
        ("core", "core/lab"),
        ("gis", "GIS/geospatial"),
    ]:
        if key in text:
            sources.append(label)
    if not sources and data_regime == "synthetic simulation":
        sources.append("simulator ensemble")
    if not sources and data_regime == "review/synthesis":
        sources.append("literature review")
    return "; ".join(dict.fromkeys(sources)) if sources else "unknown"


def infer_scale(title: str) -> str:
    text = norm(title)
    if contains(text, "pore-scale", "pore scale"):
        return "pore scale"
    if contains(text, "core", "laboratory"):
        return "core/laboratory"
    if contains(text, "basin", "regional", "gis"):
        return "regional/basin"
    if contains(text, "field", "site", "sleipner", "otway", "frio", "cranfield", "decatur", "aquistore", "in salah"):
        return "field/site"
    if contains(text, "large-scale", "3d"):
        return "reservoir scale"
    return "unknown"


def infer_dimensionality(title: str) -> str:
    text = norm(title)
    if "3d" in text or "three-dimensional" in text:
        return "3D"
    if "2d" in text or "two-dimensional" in text:
        return "2D"
    if contains(text, "radial"):
        return "radial"
    return "unknown"


def infer_method_family(title: str, existing: str) -> tuple[str, str]:
    text = norm(f"{title} {existing}")
    if contains(text, "random forest"):
        return "tree ensemble", "random forest"
    if contains(text, "xgboost", "gradient boost", "boosting"):
        return "tree ensemble", "boosting/XGBoost"
    if contains(text, "support vector", "svm"):
        return "kernel method", "SVM"
    if contains(text, "graph neural", "gnn"):
        return "graph neural network", "GNN"
    if contains(text, "fourier neural operator", "u-fno", "fno"):
        return "neural operator", "FNO/U-FNO"
    if contains(text, "wavelet neural operator"):
        return "neural operator", "WNO"
    if contains(text, "physics-informed", "pinn", "physics-constrained"):
        return "physics-guided deep learning", "PINN/physics-constrained network"
    if contains(text, "reinforcement learning"):
        return "reinforcement learning", "RL"
    if contains(text, "bayesian", "mcmc", "kalman", "ensemble smoother"):
        return "Bayesian/data assimilation", "Bayesian/MCMC/EnKF"
    if contains(text, "convolution", "cnn", "u-net", "unet"):
        return "convolutional deep learning", "CNN/U-Net"
    if contains(text, "transformer", "videomae"):
        return "transformer", "Transformer/VideoMAE"
    if contains(text, "deep learning", "neural network"):
        return "deep learning", "DNN"
    if contains(text, "machine learning"):
        return "classical/unspecified ML", "machine learning"
    if contains(text, "review"):
        return "review/synthesis", "not applicable"
    return "not specified", "unknown"


def infer_outputs(application: str, title: str) -> str:
    text = norm(title)
    outputs = []
    for key, label in [
        ("pressure", "pressure field/pressure risk"),
        ("saturation", "CO2 saturation"),
        ("plume", "plume extent/migration"),
        ("capacity", "storage capacity/resource"),
        ("suitability", "site suitability/ranking"),
        ("leak", "leakage probability/anomaly"),
        ("wellbore", "wellbore leakage risk"),
        ("uncertainty", "uncertainty/posterior"),
        ("seismic", "seismic-derived state"),
    ]:
        if key in text:
            outputs.append(label)
    defaults = {
        "site screening": "site suitability/ranking",
        "capacity estimation": "storage capacity/resource",
        "seismic inversion": "CO2 saturation or property image",
        "multiphysics inversion": "CO2 saturation/uncertainty image",
        "pressure surrogate": "pressure field",
        "plume/saturation surrogate": "CO2 saturation/plume field",
        "neural operator surrogate": "pressure/saturation fields",
        "Bayesian history matching": "posterior parameters/states",
        "monitoring design/MRV": "monitoring evidence/uncertainty reduction",
        "injection optimization": "injection policy/rate schedule",
        "RL control": "pressure-management policy",
        "leakage detection": "leakage anomaly/risk score",
        "wellbore leakage risk": "wellbore leakage risk",
    }
    if not outputs:
        outputs.append(defaults.get(application, "storage-relevant output unknown"))
    return "; ".join(dict.fromkeys(outputs))


def infer_decision(application: str) -> str:
    mapping = {
        "site screening": "select sites for further characterization",
        "capacity estimation": "estimate storage resource/dynamic capacity",
        "seismic inversion": "update plume/saturation interpretation",
        "multiphysics inversion": "update plume/saturation uncertainty",
        "pressure surrogate": "forecast pressure limits and area of review",
        "plume/saturation surrogate": "forecast plume footprint and trapping",
        "neural operator surrogate": "accelerate ensemble forecasts for pressure/plume decisions",
        "GNN/faulted reservoir": "assess migration through complex connectivity",
        "PINN/physics-guided migration": "constrain reduced migration prediction",
        "Bayesian history matching": "update model and posterior forecasts",
        "monitoring design/MRV": "design and interpret MRV evidence",
        "injection optimization": "choose injection rates/wells under constraints",
        "RL control": "control pressure-management policy",
        "leakage detection": "trigger anomaly investigation or response",
        "wellbore leakage risk": "rank wellbore leakage pathways",
        "geomechanics/seal risk": "assess seal, fault, or induced-seismicity risk",
        "geochemistry/trapping": "assess long-term trapping and reaction uncertainty",
        "competing review": "position the review contribution",
        "trustworthy ML method": "inform validation and governance design",
    }
    return mapping.get(application, "unknown storage decision")


def infer_physics(title: str, application: str) -> tuple[str, str, dict[str, int]]:
    text = norm(title)
    coverage = {c: 0 for c in CONSTRAINTS}
    encoded = []
    if application in {"pressure surrogate", "plume/saturation surrogate", "neural operator surrogate", "GNN/faulted reservoir"}:
        encoded.append("flow physics inherited from simulator labels")
        coverage["pressure constraint"] = max(coverage["pressure constraint"], 1 if "pressure" in text else 0)
        coverage["mass conservation"] = max(coverage["mass conservation"], 1)
        coverage["relative permeability"] = max(coverage["relative permeability"], 1)
        coverage["capillarity"] = max(coverage["capillarity"], 1)
        coverage["buoyancy/gravity"] = max(coverage["buoyancy/gravity"], 1)
    if contains(text, "physics-informed", "physics-constrained", "pinn"):
        encoded.append("explicit physics constraint or residual indicated by title")
        coverage["mass conservation"] = max(coverage["mass conservation"], 2)
        coverage["pressure constraint"] = max(coverage["pressure constraint"], 2)
    if contains(text, "mass", "conservation", "balance"):
        coverage["mass conservation"] = 3
    if contains(text, "pressure"):
        coverage["pressure constraint"] = max(coverage["pressure constraint"], 1)
    if contains(text, "relative permeability"):
        coverage["relative permeability"] = 2
    if contains(text, "capillary", "capillarity", "breakthrough pressure"):
        coverage["capillarity"] = 2
    if contains(text, "hysteresis"):
        coverage["hysteresis"] = 2
    if contains(text, "buoyancy", "gravity"):
        coverage["buoyancy/gravity"] = 2
    if contains(text, "fault"):
        coverage["fault transmissibility"] = 2
    if contains(text, "geomech", "seismicity", "deformation", "caprock", "seal"):
        coverage["geomechanics"] = 2
    if contains(text, "mineral", "reactive", "geochemical", "dissolution", "basalt", "trapping"):
        coverage["geochemistry/reactive transport"] = 2
    if contains(text, "seismic", "waveform", "rock physics", "acoustic"):
        coverage["rock physics"] = 2
        coverage["sensor physics"] = max(coverage["sensor physics"], 1)
    if contains(text, "gravity", "electromagnetic", "monitoring", "sensor"):
        coverage["sensor physics"] = max(coverage["sensor physics"], 2)

    if not encoded:
        encoded.append("unknown or not explicit from metadata")
    missing = [name for name, value in coverage.items() if value == 0]
    return "; ".join(encoded), "; ".join(missing[:6]) + ("; ..." if len(missing) > 6 else ""), coverage


def infer_validation(title: str, data_regime: str) -> str:
    text = norm(title)
    if contains(text, "cross-site", "cross site", "leave-one-site"):
        return "cross-site test"
    if contains(text, "unseen", "out-of-distribution", "ood", "transfer"):
        return "OOD or transfer test"
    if data_regime == "single field case":
        return "field case comparison"
    if data_regime == "controlled release":
        return "controlled-release validation"
    if data_regime == "laboratory":
        return "laboratory validation"
    if data_regime == "synthetic simulation":
        return "held-out simulation or benchmark"
    if data_regime == "field-facing monitoring or synthetic monitoring":
        return "monitoring/synthetic-monitoring validation"
    if data_regime == "review/synthesis":
        return "review synthesis"
    return "unknown"


def infer_metrics(title: str, application: str) -> str:
    text = norm(title)
    metrics = []
    if contains(text, "uncertainty"):
        metrics.append("uncertainty estimate")
    if application in {"pressure surrogate", "neural operator surrogate", "injection optimization", "RL control"}:
        metrics.append("pressure error/constraint metric needed")
    if application in {"plume/saturation surrogate", "seismic inversion", "multiphysics inversion"}:
        metrics.append("saturation/plume error metric needed")
    if application in {"leakage detection", "wellbore leakage risk"}:
        metrics.append("detection probability/false alarm metric needed")
    if application in {"Bayesian history matching", "monitoring design/MRV"}:
        metrics.append("posterior predictive or uncertainty reduction metric needed")
    return "; ".join(metrics) if metrics else "reported metric unknown from metadata"


def infer_uncertainty(title: str) -> tuple[str, str]:
    text = norm(title)
    if contains(text, "calibrated", "calibration"):
        return "calibrated uncertainty", "yes"
    if contains(text, "bayesian", "mcmc", "posterior", "ensemble kalman", "uncertainty", "probabilistic"):
        return "probabilistic/posterior or ensemble uncertainty", "unknown"
    if contains(text, "sensitivity"):
        return "sensitivity analysis", "no"
    return "none identified from metadata", "no"


def yes_no_from_title(title: str, *keywords: str) -> str:
    text = norm(title)
    return "yes" if contains(text, *keywords) else "no"


def score_field_evidence(data_regime: str, validation_type: str) -> int | None:
    if data_regime == "review/synthesis":
        return None
    if data_regime == "synthetic simulation":
        return 0
    if data_regime == "field-facing monitoring or synthetic monitoring":
        return 1
    if data_regime in {"laboratory", "controlled release"}:
        return 2
    if data_regime == "single field case":
        return 3
    if "cross-site" in validation_type:
        return 4
    return 0


def score_physical(coverage: dict[str, int], application: str) -> int | None:
    if application in {"competing review", "trustworthy ML method"}:
        return None
    max_cov = max(coverage.values()) if coverage else 0
    active = sum(1 for value in coverage.values() if value > 0)
    if max_cov >= 3:
        return 3
    if max_cov >= 2:
        return 2
    if active >= 3:
        return 1
    return 0


def score_uncertainty(uncertainty_method: str, application: str) -> int | None:
    if application in {"competing review", "trustworthy ML method"}:
        return None
    text = norm(uncertainty_method)
    if "calibrated" in text:
        return 3
    if contains(text, "posterior", "probabilistic", "ensemble"):
        return 2
    if "sensitivity" in text:
        return 1
    return 0


def score_transfer(title: str, data_regime: str, validation_type: str, application: str) -> int | None:
    if application in {"competing review", "trustworthy ML method"}:
        return None
    text = norm(f"{title} {validation_type}")
    if contains(text, "cross-site", "cross site", "multiple field"):
        return 4
    if contains(text, "unseen geology", "fault architecture", "boundary", "ood", "out-of-distribution"):
        return 3
    if contains(text, "transfer", "unseen", "generaliz"):
        return 2
    if data_regime == "single field case":
        return 1
    return 0


def decision_criticality(application: str) -> int | None:
    if application in {"competing review", "trustworthy ML method"}:
        return None
    if application in {"leakage detection", "wellbore leakage risk", "RL control", "injection optimization", "geomechanics/seal risk"}:
        return 4
    if application in {"pressure surrogate", "plume/saturation surrogate", "neural operator surrogate", "Bayesian history matching", "monitoring design/MRV", "GNN/faulted reservoir"}:
        return 3
    if application in {"seismic inversion", "multiphysics inversion", "capacity estimation", "geochemistry/trapping"}:
        return 2
    if application in {"site screening", "field project context", "PINN/physics-guided migration"}:
        return 2
    return 1


def score_decision_readiness(application: str, field_score: int | None, physical_score: int | None, uncertainty_score: int | None, validation_type: str) -> int | None:
    if application in {"competing review", "trustworthy ML method"}:
        return None
    base = 1
    if application in {"site screening", "capacity estimation", "pressure surrogate", "plume/saturation surrogate", "neural operator surrogate", "seismic inversion", "multiphysics inversion"}:
        base = 2
    if application in {"Bayesian history matching", "monitoring design/MRV", "injection optimization", "leakage detection", "wellbore leakage risk", "geomechanics/seal risk"}:
        base = 2
    if application == "RL control":
        base = 1
    if (field_score or 0) >= 3 and (uncertainty_score or 0) >= 2:
        base = max(base, 3)
    if "cross-site" in validation_type and (uncertainty_score or 0) >= 3:
        base = 4
    return min(base, 4)


def weighted_score(values: dict[str, int | None]) -> str:
    weights = {
        "field": 0.25,
        "physical": 0.20,
        "uncertainty": 0.20,
        "transfer": 0.20,
        "decision": 0.15,
    }
    if any(values[key] is None for key in weights):
        return "NA"
    score = sum((values[key] or 0) * weight for key, weight in weights.items())
    return f"{score:.2f}"


def trustworthiness_score(overall: str, uncertainty: int | None, transfer: int | None) -> str:
    if overall == "NA" or uncertainty is None or transfer is None:
        return "NA"
    score = 0.7 * float(overall) + 0.15 * uncertainty + 0.15 * transfer
    return f"{score:.2f}"


def build_evidence_matrix() -> list[dict[str, str]]:
    with SOURCE.open(encoding="utf-8-sig", newline="") as handle:
        source_rows = list(csv.DictReader(handle))

    evidence_rows: list[dict[str, str]] = []
    excluded_rows: list[dict[str, str]] = []
    for row in source_rows:
        status, note = scope_status(row)
        if status == "exclude":
            excluded_rows.append(
                {
                    "paper_id": clean(row.get("paper_id")),
                    "title": clean(row.get("title")),
                    "doi_or_url": clean(row.get("doi_or_url")),
                    "exclusion_reason": note,
                }
            )
            continue
        title = clean(row.get("title"))
        application = infer_application(row)
        stage = infer_stage(application, clean(row.get("storage_stage")))
        data_regime = infer_data_regime(row, application)
        field_case = detect_field_case(title, row.get("field_case", ""))
        method_family, specific_model = infer_method_family(title, row.get("ml_method", ""))
        uncertainty_method, uncertainty_calibrated = infer_uncertainty(title)
        physics_encoded, physics_missing, coverage = infer_physics(title, application)
        validation_type = infer_validation(title, data_regime)
        field_score = score_field_evidence(data_regime, validation_type)
        physical_score = score_physical(coverage, application)
        uncertainty_score = score_uncertainty(uncertainty_method, application)
        transfer_score = score_transfer(title, data_regime, validation_type, application)
        decision_score = score_decision_readiness(application, field_score, physical_score, uncertainty_score, validation_type)
        criticality = decision_criticality(application)
        overall = weighted_score(
            {
                "field": field_score,
                "physical": physical_score,
                "uncertainty": uncertainty_score,
                "transfer": transfer_score,
                "decision": decision_score,
            }
        )

        evidence_rows.append(
            {
                "paper_id": clean(row.get("paper_id")),
                "title": title,
                "authors": clean(row.get("authors")),
                "year": clean(row.get("year")),
                "journal": clean(row.get("venue")),
                "doi_or_url": clean(row.get("doi_or_url")),
                "storage_stage": stage,
                "application_area": application,
                "geological_process": clean(row.get("geological_process")) or application,
                "decision_supported": clean(row.get("decision_supported")) or infer_decision(application),
                "data_regime": data_regime,
                "data_source": infer_data_source(title, data_regime),
                "field_case": field_case,
                "scale": infer_scale(title),
                "dimensionality": infer_dimensionality(title),
                "ml_method_family": method_family,
                "specific_model": specific_model,
                "baseline": clean(row.get("baseline_method")) or "unknown",
                "input_variables": clean(row.get("input_variables")) or infer_data_source(title, data_regime),
                "target_outputs": clean(row.get("target_output")) or infer_outputs(application, title),
                "physics_encoded": physics_encoded,
                "physics_missing": physics_missing or "unknown",
                "geomechanics_included": "yes" if coverage["geomechanics"] >= 2 else ("discussed/implicit" if coverage["geomechanics"] == 1 else "no"),
                "geochemistry_included": "yes" if coverage["geochemistry/reactive transport"] >= 2 else ("discussed/implicit" if coverage["geochemistry/reactive transport"] == 1 else "no"),
                "rock_physics_included": "yes" if coverage["rock physics"] >= 2 else ("discussed/implicit" if coverage["rock physics"] == 1 else "no"),
                "mass_conservation_checked": "yes" if coverage["mass conservation"] >= 3 else ("discussed/implicit" if coverage["mass conservation"] > 0 else "no"),
                "pressure_constraint_checked": "yes" if coverage["pressure constraint"] >= 3 else ("discussed/implicit" if coverage["pressure constraint"] > 0 else "no"),
                "uncertainty_method": uncertainty_method,
                "uncertainty_calibrated": uncertainty_calibrated,
                "ood_tested": yes_no_from_title(title, "ood", "out-of-distribution", "unseen geology", "unseen"),
                "cross_site_tested": yes_no_from_title(title, "cross-site", "cross site", "leave-one-site"),
                "field_validated": "yes" if field_score == 3 else "no",
                "controlled_release_validated": "yes" if data_regime == "controlled release" else "no",
                "validation_type": validation_type,
                "metrics_used": infer_metrics(title, application),
                "decision_metric_used": "explicit decision metric unknown from metadata",
                "main_result": clean(row.get("main_contribution")) or "metadata seed; full-text extraction needed",
                "main_limitation": clean(row.get("limitation")) or "full-text limitation coding needed; avoid detailed claims until screened",
                "field_evidence_score": "" if field_score is None else str(field_score),
                "physical_consistency_score": "" if physical_score is None else str(physical_score),
                "uncertainty_score": "" if uncertainty_score is None else str(uncertainty_score),
                "transferability_score": "" if transfer_score is None else str(transfer_score),
                "decision_readiness_score": "" if decision_score is None else str(decision_score),
                "decision_criticality_score": "" if criticality is None else str(criticality),
                "overall_readiness_score": overall,
                "trustworthiness_score": trustworthiness_score(overall, uncertainty_score, transfer_score),
                "review_section": clean(row.get("review_section")) or stage,
                "claim_supported": clean(row.get("claim_ids")) or "claim linkage needed after full-text screening",
                "scope_status": status,
                "scope_note": note,
                "notes": f"coding_basis=metadata/title/rubric; source_status={clean(row.get('content_screening_status')) or 'unknown'}",
            }
        )
        evidence_rows[-1].update({f"constraint_{slug(c)}": str(coverage[c]) for c in CONSTRAINTS})

    if excluded_rows:
        write_csv(VALIDATION_DIR / "OUT_OF_SCOPE_EXCLUDED_ROWS.csv", excluded_rows)
    return evidence_rows


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str] | None = None) -> None:
    if not rows:
        return
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def csv_to_markdown(csv_path: Path) -> None:
    with csv_path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        return
    fields = list(rows[0].keys())
    lines = [
        "| " + " | ".join(fields) + " |",
        "| " + " | ".join("---" for _ in fields) + " |",
    ]
    for row in rows:
        values = [str(row.get(field, "")).replace("|", "\\|") for field in fields]
        lines.append("| " + " | ".join(values) + " |")
    csv_path.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_scoring_rubric() -> None:
    text = """# Evidence Maturity Scoring Rubric

This rubric converts the literature matrix into a reproducible, semi-quantitative evidence backbone. Scores are conservative and should be upgraded only after abstract or full-text screening. Empty scores mean the item is a review, general context source, or not applicable.

## Field Evidence Score

| Score | Definition |
|---:|---|
| 0 | Purely synthetic simulation or benchmark evidence. |
| 1 | Simulation with realistic geology, field-facing monitoring geometry, or synthetic monitoring. |
| 2 | Laboratory, experimental, controlled-release, or semi-field evidence. |
| 3 | Single field case application or comparison. |
| 4 | Multiple field cases or cross-site validation. |

## Physical Consistency Score

| Score | Definition |
|---:|---|
| 0 | No physics check identified from metadata. |
| 1 | Physics inherited from simulator labels or discussed qualitatively. |
| 2 | Partial physics loss, simplified physical constraint, or explicit process coverage. |
| 3 | Diagnostic check such as mass balance, pressure residuals, plume volume, or comparable physical validation. |
| 4 | Coupled physical validation across flow, monitoring, and risk variables. |

## Uncertainty Score

| Score | Definition |
|---:|---|
| 0 | Deterministic point prediction only, or no uncertainty identified. |
| 1 | Sensitivity or ensemble analysis without probabilistic calibration. |
| 2 | Probabilistic, Bayesian, posterior, or ensemble uncertainty reported. |
| 3 | Calibrated uncertainty or posterior predictive checking. |
| 4 | Uncertainty propagated into decision, optimization, MRV, or corrective-action workflow. |

## Transferability Score

| Score | Definition |
|---:|---|
| 0 | Same distribution train/test split or no transfer test identified. |
| 1 | Single field case or field-facing evaluation without transfer. |
| 2 | Unseen parameter range or transfer-learning test. |
| 3 | Unseen geology, wells, faults, boundary conditions, or OOD test. |
| 4 | Cross-site or multiple-field transfer validation. |

## Decision Readiness Score

| Score | Definition |
|---:|---|
| 0 | Technical demonstration with no storage decision linkage. |
| 1 | Predicts a storage-relevant variable. |
| 2 | Linked to a storage decision variable. |
| 3 | Tested near a decision threshold or with field uncertainty. |
| 4 | Auditable operational/MRV workflow with documented human or regulatory use path. |

## Overall Readiness

Overall readiness is calculated as:

```text
0.25 * field evidence
+ 0.20 * physical consistency
+ 0.20 * uncertainty
+ 0.20 * transferability
+ 0.15 * decision readiness
```

This weighting deliberately gives most weight to evidence and transfer because the manuscript's thesis is that the bottleneck for ML in geological CO2 storage is evidence maturity, not algorithm availability.
"""
    (EVIDENCE_DIR / "scoring_rubric.md").write_text(text, encoding="utf-8")


def numeric(value: str) -> float | None:
    try:
        if value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def group_stats(rows: list[dict[str, str]], key: str) -> dict[str, dict[str, float]]:
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[row[key]].append(row)
    stats: dict[str, dict[str, float]] = {}
    for group, group_rows in groups.items():
        stats[group] = {"N": len(group_rows)}
        for column in [
            "field_evidence_score",
            "physical_consistency_score",
            "uncertainty_score",
            "transferability_score",
            "decision_readiness_score",
            "decision_criticality_score",
            "overall_readiness_score",
            "trustworthiness_score",
        ]:
            values = [numeric(row[column]) for row in group_rows]
            values = [value for value in values if value is not None]
            stats[group][column] = sum(values) / len(values) if values else float("nan")
    return stats


def color_scale(value: float, low: str = "#d73027", mid: str = "#fee08b", high: str = "#1a9850") -> str:
    if math.isnan(value):
        return "#d9d9d9"
    value = max(0.0, min(4.0, value)) / 4.0
    def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
        return "#" + "".join(f"{v:02x}" for v in rgb)
    a, b, t = (low, mid, value * 2) if value < 0.5 else (mid, high, (value - 0.5) * 2)
    ar, ag, ab = hex_to_rgb(a)
    br, bg, bb = hex_to_rgb(b)
    return rgb_to_hex((round(ar + (br - ar) * t), round(ag + (bg - ag) * t), round(ab + (bb - ab) * t)))


def svg_header(width: int, height: int) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#222} .small{font-size:11px}.label{font-size:12px}.title{font-size:18px;font-weight:700}.axis{stroke:#333;stroke-width:1}.grid{stroke:#ddd;stroke-width:1}.note{font-size:10px;fill:#555}</style>',
        '<rect width="100%" height="100%" fill="white"/>',
    ]


def write_svg(path: Path, parts: list[str]) -> None:
    path.write_text("\n".join(parts + ["</svg>\n"]), encoding="utf-8")


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def text_wrap(text: str, max_chars: int) -> list[str]:
    words = str(text).split()
    lines: list[str] = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 > max_chars:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        lines.append(current)
    return lines or [""]


def draw_wrapped(parts: list[str], text: str, x: float, y: float, width_chars: int, klass: str = "small", line_height: int = 13, anchor: str = "middle") -> None:
    for i, line in enumerate(text_wrap(text, width_chars)):
        parts.append(f'<text class="{klass}" x="{x:.1f}" y="{y + i * line_height:.1f}" text-anchor="{anchor}">{esc(line)}</text>')


def figure1(rows: list[dict[str, str]]) -> None:
    stats = group_stats(rows, "storage_stage")
    decisions = [
        ("screening", "pre_injection_decision"),
        ("characterization", "characterization"),
        ("dynamic forecasting", "dynamic_prediction"),
        ("operation/control", "operation_control"),
        ("monitoring/MRV", "monitoring_mrv"),
        ("risk response", "risk_response"),
        ("stewardship/context", "field_evidence"),
    ]
    layers = [
        ("data source", "field_evidence_score"),
        ("geological process", "physical_consistency_score"),
        ("ML task", "overall_readiness_score"),
        ("decision variable", "decision_readiness_score"),
        ("validation target", "transferability_score"),
        ("readiness level", "overall_readiness_score"),
    ]
    width, height = 1320, 760
    parts = svg_header(width, height)
    parts.append('<text class="title" x="40" y="36">Figure 1. CO2 storage decision chain x ML evidence map</text>')
    parts.append('<text class="note" x="40" y="56">Cell color = average score (0-4); circle size = paper count; black border = at least one field-validated row; diagonal hatch = simulation-only dominates.</text>')
    left, top, cw, ch = 190, 105, 145, 82
    for j, (label, stage) in enumerate(decisions):
        x = left + j * cw
        draw_wrapped(parts, label, x + cw / 2, 82, 17, "label")
    for i, (layer, metric) in enumerate(layers):
        y = top + i * ch
        draw_wrapped(parts, layer, 34, y + 34, 18, "label", anchor="start")
        for j, (_label, stage) in enumerate(decisions):
            x = left + j * cw
            stage_rows = [r for r in rows if r["storage_stage"] == stage]
            if not stage_rows and stage == "field_evidence":
                stage_rows = [r for r in rows if r["application_area"] == "field project context"]
            values = [numeric(r[metric]) for r in stage_rows]
            values = [v for v in values if v is not None]
            avg = sum(values) / len(values) if values else float("nan")
            n = len(stage_rows)
            field_any = any(r["field_validated"] == "yes" for r in stage_rows)
            synthetic_count = sum(1 for r in stage_rows if r["data_regime"] == "synthetic simulation")
            fill = color_scale(avg)
            stroke = "#111" if field_any else "#999"
            sw = 2.5 if field_any else 1
            parts.append(f'<rect x="{x}" y="{y}" width="{cw-6}" height="{ch-7}" rx="4" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
            if n and synthetic_count / n > 0.55:
                for k in range(-60, 150, 18):
                    parts.append(f'<line x1="{x+k}" y1="{y+ch-7}" x2="{x+k+70}" y2="{y}" stroke="#777" stroke-width="0.6" opacity="0.35"/>')
            radius = 6 + min(22, math.sqrt(n) * 4)
            parts.append(f'<circle cx="{x+cw/2}" cy="{y+ch/2-3}" r="{radius:.1f}" fill="white" opacity="0.62" stroke="#333"/>')
            label = "NA" if math.isnan(avg) else f"{avg:.1f}"
            parts.append(f'<text class="label" x="{x+cw/2}" y="{y+ch/2+1}" text-anchor="middle">{label}</text>')
            parts.append(f'<text class="note" x="{x+cw/2}" y="{y+ch-14}" text-anchor="middle">N={n}</text>')
    legend_y = height - 70
    parts.append(f'<text class="label" x="40" y="{legend_y}">Score color:</text>')
    for idx, val in enumerate([0, 1, 2, 3, 4]):
        x = 135 + idx * 58
        parts.append(f'<rect x="{x}" y="{legend_y-16}" width="44" height="18" fill="{color_scale(val)}" stroke="#999"/>')
        parts.append(f'<text class="note" x="{x+22}" y="{legend_y+17}" text-anchor="middle">{val}</text>')
    parts.append(f'<text class="note" x="520" y="{legend_y}">This is a reproducible evidence map generated from evidence/evidence_matrix.csv; metadata-coded rows require full-text verification before submission.</text>')
    write_svg(FIG_DIR / "Figure1_decision_chain_evidence_map.svg", parts)


def figure2(rows: list[dict[str, str]]) -> None:
    width, height = 1280, 780
    parts = svg_header(width, height)
    parts.append('<text class="title" x="40" y="36">Figure 2. Simulation-to-field gap: evidence flow from data regime to validation type</text>')
    parts.append('<text class="note" x="40" y="56">Line width = paper count; color = average uncertainty score. Grey flows are low-field-evidence routes.</text>')
    cols = [
        ("Data regime", "data_regime", 90),
        ("ML task/application", "application_area", 520),
        ("Validation type", "validation_type", 970),
    ]
    for title, _key, x in cols:
        parts.append(f'<text class="label" x="{x}" y="92">{esc(title)}</text>')

    top, gap = 125, 9
    col_nodes: list[dict[str, tuple[float, float, float]]] = []
    for _title, key, x in cols:
        counts = Counter(r[key] for r in rows if r[key])
        common = counts.most_common(8)
        total = sum(c for _, c in common) or 1
        nodes: dict[str, tuple[float, float, float]] = {}
        y = top
        for name, count in common:
            h = max(24, count / total * 520)
            nodes[name] = (x, y, h)
            fill = "#f4f4f4"
            parts.append(f'<rect x="{x}" y="{y:.1f}" width="220" height="{h:.1f}" rx="4" fill="{fill}" stroke="#777"/>')
            draw_wrapped(parts, f"{name} (N={count})", x + 8, y + 16, 28, "small", anchor="start")
            y += h + gap
        col_nodes.append(nodes)

    def flow_key(a: str, b: str, key1: str, key2: str) -> tuple[int, float]:
        flow_rows = [r for r in rows if r[key1] == a and r[key2] == b]
        us = [numeric(r["uncertainty_score"]) for r in flow_rows]
        us = [u for u in us if u is not None]
        return len(flow_rows), (sum(us) / len(us) if us else 0)

    def draw_flow(nodes_a, nodes_b, key_a, key_b, xoff_a=220, xoff_b=0) -> None:
        flows = []
        for a in nodes_a:
            for b in nodes_b:
                count, uavg = flow_key(a, b, key_a, key_b)
                if count:
                    flows.append((count, uavg, a, b))
        flows = sorted(flows, reverse=True)[:26]
        for count, uavg, a, b in flows:
            x1, y1, h1 = nodes_a[a]
            x2, y2, h2 = nodes_b[b]
            stroke = color_scale(uavg, "#bdbdbd", "#74add1", "#4575b4")
            width_line = max(1.5, min(18, count * 0.95))
            y_start = y1 + h1 / 2
            y_end = y2 + h2 / 2
            parts.append(
                f'<path d="M {x1+xoff_a} {y_start:.1f} C {(x1+xoff_a+x2+xoff_b)/2:.1f} {y_start:.1f}, {(x1+xoff_a+x2+xoff_b)/2:.1f} {y_end:.1f}, {x2+xoff_b} {y_end:.1f}" '
                f'fill="none" stroke="{stroke}" stroke-width="{width_line:.1f}" opacity="0.50"/>'
            )

    draw_flow(col_nodes[0], col_nodes[1], "data_regime", "application_area")
    draw_flow(col_nodes[1], col_nodes[2], "application_area", "validation_type")
    parts.append('<text class="note" x="40" y="735">Interpretation: if the thickest flows remain synthetic simulation -> surrogate/dynamic tasks -> held-out simulation, the evidence bottleneck is validation regime rather than algorithm availability.</text>')
    write_svg(FIG_DIR / "Figure2_simulation_to_field_gap_alluvial.svg", parts)


def figure3(rows: list[dict[str, str]]) -> None:
    stats = group_stats([r for r in rows if r["application_area"] not in {"competing review", "trustworthy ML method"}], "application_area")
    width, height = 1120, 820
    parts = svg_header(width, height)
    parts.append('<text class="title" x="40" y="36">Figure 3. Evidence maturity map: field evidence vs decision criticality</text>')
    parts.append('<text class="note" x="40" y="56">Bubble size = number of papers; color = average uncertainty score. Red zone = high decision criticality but low field evidence.</text>')
    left, top, plot_w, plot_h = 120, 105, 820, 590
    parts.append(f'<rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" fill="#fff7f7" stroke="#ddd"/>')
    parts.append(f'<rect x="{left}" y="{top}" width="{plot_w*0.42}" height="{plot_h*0.42}" fill="#fff" opacity="0.65"/>')
    parts.append(f'<text class="note" x="{left+12}" y="{top+22}">high criticality / low field evidence red zone</text>')
    for i in range(5):
        x = left + i / 4 * plot_w
        y = top + plot_h - i / 4 * plot_h
        parts.append(f'<line class="grid" x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{top+plot_h}"/>')
        parts.append(f'<line class="grid" x1="{left}" y1="{y:.1f}" x2="{left+plot_w}" y2="{y:.1f}"/>')
        parts.append(f'<text class="small" x="{x:.1f}" y="{top+plot_h+25}" text-anchor="middle">{i}</text>')
        parts.append(f'<text class="small" x="{left-18}" y="{y+4:.1f}" text-anchor="end">{i}</text>')
    parts.append(f'<line class="axis" x1="{left}" y1="{top+plot_h}" x2="{left+plot_w}" y2="{top+plot_h}"/>')
    parts.append(f'<line class="axis" x1="{left}" y1="{top}" x2="{left}" y2="{top+plot_h}"/>')
    parts.append(f'<text class="label" x="{left+plot_w/2}" y="{top+plot_h+55}" text-anchor="middle">Field evidence score (0-4)</text>')
    parts.append(f'<text class="label" transform="translate({left-72},{top+plot_h/2}) rotate(-90)" text-anchor="middle">Decision criticality score (0-4)</text>')

    for app, values in stats.items():
        x_val = values["field_evidence_score"]
        y_val = values["decision_criticality_score"]
        if math.isnan(x_val) or math.isnan(y_val):
            continue
        x = left + x_val / 4 * plot_w
        y = top + plot_h - y_val / 4 * plot_h
        n = values["N"]
        r = 6 + min(30, math.sqrt(n) * 4.5)
        fill = color_scale(values["uncertainty_score"], "#f7f7f7", "#abd9e9", "#2c7bb6")
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}" stroke="#333" opacity="0.82"/>')
        draw_wrapped(parts, app, x, y + r + 13, 18, "note")
    parts.append('<text class="note" x="980" y="130">Color: uncertainty score</text>')
    for idx, val in enumerate([0, 1, 2, 3, 4]):
        y = 160 + idx * 32
        parts.append(f'<rect x="980" y="{y}" width="34" height="18" fill="{color_scale(val, "#f7f7f7", "#abd9e9", "#2c7bb6")}" stroke="#999"/>')
        parts.append(f'<text class="note" x="1025" y="{y+13}">{val}</text>')
    write_svg(FIG_DIR / "Figure3_evidence_maturity_map.svg", parts)


def figure4(rows: list[dict[str, str]]) -> None:
    apps = [app for app in APPLICATION_ORDER if app not in {"competing review", "trustworthy ML method", "other storage ML"}]
    width, height = 1420, 850
    parts = svg_header(width, height)
    parts.append('<text class="title" x="40" y="36">Figure 4. Physics constraint coverage heatmap</text>')
    parts.append('<text class="note" x="40" y="56">Cell score: 0 not identified, 1 inherited/discussed, 2 simplified/explicit process, 3 diagnostic check, 4 coupled validation.</text>')
    left, top, cw, ch = 285, 130, 92, 36
    for j, constraint in enumerate(CONSTRAINTS):
        x = left + j * cw + 42
        parts.append(f'<text class="small" transform="translate({x},{top-12}) rotate(-55)" text-anchor="start">{esc(constraint)}</text>')
    for i, app in enumerate(apps):
        y = top + i * ch
        draw_wrapped(parts, app, 35, y + 22, 32, "small", anchor="start")
        app_rows = [r for r in rows if r["application_area"] == app]
        for j, constraint in enumerate(CONSTRAINTS):
            key = f"constraint_{slug(constraint)}"
            vals = [numeric(r.get(key, "")) for r in app_rows]
            vals = [v for v in vals if v is not None]
            avg = sum(vals) / len(vals) if vals else float("nan")
            x = left + j * cw
            parts.append(f'<rect x="{x}" y="{y}" width="{cw-4}" height="{ch-3}" fill="{color_scale(avg)}" stroke="#eee"/>')
            label = "" if math.isnan(avg) else f"{avg:.1f}"
            parts.append(f'<text class="note" x="{x+cw/2-2}" y="{y+22}" text-anchor="middle">{label}</text>')
    parts.append(f'<text class="note" x="40" y="{height-34}">Interpretation: sparse high scores identify where ML studies rarely verify storage physics beyond simulator-inherited labels.</text>')
    write_svg(FIG_DIR / "Figure4_physics_constraint_coverage_heatmap.svg", parts)


def figure5() -> None:
    rows = [
        ("Data provenance", "Simulation, lab, controlled release, or field?", "Dataset card; source trace", "False confidence"),
        ("Physical consistency", "Mass, pressure, plume and process plausibility?", "Conservation and process diagnostics", "Nonphysical plume"),
        ("Uncertainty calibration", "Are intervals reliable for decisions?", "Posterior predictive checks", "False precision"),
        ("Transferability", "Works on unseen geology or sites?", "OOD/cross-site test", "Deployment failure"),
        ("Monitoring consistency", "Matches independent observations?", "Multi-sensor validation", "Wrong MRV inference"),
        ("Decision auditability", "Can an action be traced and justified?", "Decision log and model card", "Regulatory distrust"),
        ("Regulatory readiness", "Can evidence be reviewed?", "MRV documentation package", "Non-adoption"),
    ]
    width, height = 1120, 720
    parts = svg_header(width, height)
    parts.append('<text class="title" x="40" y="36">Figure 5. Trustworthiness audit ladder for ML-assisted CO2 storage</text>')
    parts.append('<text class="note" x="40" y="56">Each layer is an audit question, not a decorative maturity slogan.</text>')
    headers = ["Layer", "Audit question", "Evidence required", "Failure if absent"]
    xs = [60, 310, 590, 850]
    ws = [220, 250, 230, 210]
    y = 95
    for x, w, header in zip(xs, ws, headers):
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="34" fill="#23395b" stroke="#23395b"/>')
        parts.append(f'<text class="label" x="{x+10}" y="{y+22}" fill="white">{esc(header)}</text>')
    for i, row in enumerate(rows):
        y = 135 + i * 76
        fill = "#f7fbff" if i % 2 == 0 else "#eef5f9"
        for x, w, cell in zip(xs, ws, row):
            parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="68" fill="{fill}" stroke="#c7d5df"/>')
            draw_wrapped(parts, cell, x + 10, y + 19, max(18, int(w / 8)), "small", anchor="start")
        parts.append(f'<circle cx="35" cy="{y+34}" r="15" fill="{color_scale(i/6*4)}" stroke="#333"/>')
        parts.append(f'<text class="note" x="35" y="{y+38}" text-anchor="middle">{i+1}</text>')
    write_svg(FIG_DIR / "Figure5_trustworthiness_audit_ladder.svg", parts)


def figure6(rows: list[dict[str, str]]) -> None:
    cases = FIELD_CASES[:-1] + ["Illinois Basin"]
    cols = [
        ("4D/seismic", ["seismic", "4d", "time-lapse", "waveform"]),
        ("pressure", ["pressure"]),
        ("deformation", ["insar", "deformation"]),
        ("geochemistry", ["geochem", "groundwater"]),
        ("controlled release", ["controlled release", "release field"]),
        ("ML paper in corpus", ["machine learning", "deep learning", "neural", "seisco2net"]),
        ("validation use", ["validation", "inversion", "monitoring", "history matching"]),
    ]
    width, height = 1180, 700
    parts = svg_header(width, height)
    parts.append('<text class="title" x="40" y="36">Figure 6. Case-study evidence map in the current corpus</text>')
    parts.append('<text class="note" x="40" y="56">Dots mark evidence types identified from titles/metadata in the current corpus, not a complete site inventory.</text>')
    left, top, cw, ch = 235, 110, 115, 44
    for j, (col, _keys) in enumerate(cols):
        draw_wrapped(parts, col, left + j * cw + cw / 2, 88, 14, "small")
    for i, case in enumerate(cases):
        y = top + i * ch
        parts.append(f'<text class="label" x="40" y="{y+27}" text-anchor="start">{esc(case)}</text>')
        case_rows = [r for r in rows if case.lower() in f"{r['title']} {r['field_case']}".lower()]
        for j, (_col, keys) in enumerate(cols):
            x = left + j * cw
            hit = any(any(key in norm(r["title"]) for key in keys) for r in case_rows)
            fill = "#2c7bb6" if hit else "#f0f0f0"
            stroke = "#1b4f72" if hit else "#bbb"
            parts.append(f'<rect x="{x}" y="{y}" width="{cw-8}" height="{ch-6}" fill="#fff" stroke="#eee"/>')
            parts.append(f'<circle cx="{x+cw/2-4}" cy="{y+ch/2-3}" r="{12 if hit else 7}" fill="{fill}" stroke="{stroke}"/>')
        parts.append(f'<text class="note" x="{left + len(cols)*cw + 10}" y="{y+27}">N={len(case_rows)}</text>')
    parts.append(f'<text class="note" x="40" y="{height-35}">This map is intentionally corpus-based: it shows where the review evidence currently has field anchors and where full-text/manual case coding is still needed.</text>')
    write_svg(FIG_DIR / "Figure6_case_study_evidence_map.svg", parts)


def write_tables(rows: list[dict[str, str]]) -> None:
    stats = group_stats(rows, "application_area")
    table1 = []
    for app in APPLICATION_ORDER:
        if app not in stats:
            continue
        app_rows = [r for r in rows if r["application_area"] == app]
        if app in {"competing review", "trustworthy ML method"}:
            continue
        regimes = Counter(r["data_regime"] for r in app_rows)
        table1.append(
            {
                "Application": app,
                "N papers": str(len(app_rows)),
                "Dominant data regime": regimes.most_common(1)[0][0] if regimes else "unknown",
                "Field evidence avg": f"{stats[app]['field_evidence_score']:.2f}" if not math.isnan(stats[app]["field_evidence_score"]) else "NA",
                "UQ avg": f"{stats[app]['uncertainty_score']:.2f}" if not math.isnan(stats[app]["uncertainty_score"]) else "NA",
                "Physics avg": f"{stats[app]['physical_consistency_score']:.2f}" if not math.isnan(stats[app]["physical_consistency_score"]) else "NA",
                "Transfer/OOD avg": f"{stats[app]['transferability_score']:.2f}" if not math.isnan(stats[app]["transferability_score"]) else "NA",
                "Readiness avg": f"{stats[app]['overall_readiness_score']:.2f}" if not math.isnan(stats[app]["overall_readiness_score"]) else "NA",
            }
        )
    write_csv(TABLE_DIR / "Table1_literature_corpus_summary.csv", table1)
    csv_to_markdown(TABLE_DIR / "Table1_literature_corpus_summary.csv")

    table3 = [
        {"ML family": "CNN/U-Net", "Typical use": "gridded pressure/saturation or seismic inversion", "Geological assumptions inherited": "training geomodel distribution and rock-physics labels", "Physical process missing most often": "OOD geology, boundary-condition shift, long-term trapping", "Required validation": "mass/plume volume, pressure-threshold error, OOD geology"},
        {"ML family": "FNO/U-FNO/neural operators", "Typical use": "operator surrogate for pressure/saturation fields", "Geological assumptions inherited": "simulator physics, grid family, well schedules", "Physical process missing most often": "faults, capillarity/hysteresis, geochemistry, geomechanics", "Required validation": "cross-geology tests, conservation diagnostics, threshold-conditioned error"},
        {"ML family": "GNN", "Typical use": "faulted reservoirs and irregular connectivity", "Geological assumptions inherited": "graph topology and connectivity definition", "Physical process missing most often": "uncertain fault transmissibility and coupled flow-geomechanics", "Required validation": "unseen fault architectures and connectivity perturbations"},
        {"ML family": "PINN/physics-guided DL", "Typical use": "reduced migration physics and constrained prediction", "Geological assumptions inherited": "chosen governing equation simplification", "Physical process missing most often": "full 3D heterogeneous multiphase coupling", "Required validation": "residual, simulator, and field/monitoring consistency"},
        {"ML family": "Bayesian surrogate/data assimilation", "Typical use": "history matching and posterior forecasts", "Geological assumptions inherited": "prior ensemble and likelihood design", "Physical process missing most often": "prior misspecification and surrogate discrepancy", "Required validation": "posterior predictive checks and surrogate-error propagation"},
    ]
    write_csv(TABLE_DIR / "Table3_method_family_assumptions_validation.csv", table3)
    csv_to_markdown(TABLE_DIR / "Table3_method_family_assumptions_validation.csv")

    table4 = [
        {"Failure mode": "Mass nonconservation", "Where it appears": "plume/saturation surrogate", "Why dangerous": "wrong storage amount or plume volume", "Diagnostic": "injected vs predicted CO2 volume", "Mitigation": "conservative architecture or simulator correction"},
        {"Failure mode": "Pressure bias near threshold", "Where it appears": "pressure surrogate and optimization", "Why dangerous": "unsafe injection or caprock/fault risk", "Diagnostic": "error conditioned on pressure limit", "Mitigation": "threshold-weighted loss and safety-margin validation"},
        {"Failure mode": "Overconfident posterior", "Where it appears": "history matching/data assimilation", "Why dangerous": "false certainty in operating or MRV decisions", "Diagnostic": "posterior predictive check", "Mitigation": "surrogate-error propagation and prior sensitivity"},
        {"Failure mode": "Synthetic leakage bias", "Where it appears": "leakage anomaly detection", "Why dangerous": "false alarms or missed rare events", "Diagnostic": "controlled-release or field-analogue test", "Mitigation": "rare-event calibration and decision-threshold analysis"},
        {"Failure mode": "Rock-physics mismatch", "Where it appears": "seismic inversion", "Why dangerous": "wrong saturation or plume interpretation", "Diagnostic": "multi-sensor comparison", "Mitigation": "rock-physics uncertainty and independent data validation"},
        {"Failure mode": "Cross-site failure", "Where it appears": "deployment/transfer", "Why dangerous": "model appears general but is site-family specific", "Diagnostic": "leave-one-site-out or unseen-geology test", "Mitigation": "domain adaptation and explicit transfer limits"},
    ]
    write_csv(TABLE_DIR / "Table4_failure_modes_and_mitigation.csv", table4)
    csv_to_markdown(TABLE_DIR / "Table4_failure_modes_and_mitigation.csv")

    table5 = [
        {"Existing review": "Broad ESR GCS reviews", "Scope": "storage mechanisms, trapping, monitoring, prospects", "What it covers well": "storage science and field context", "Gap left": "little ML audit/readiness framework", "This review contribution": "evidence maturity and decision-readiness synthesis"},
        {"Existing review": "ESR statistical/computational storage review", "Scope": "statistical and computational perspective", "What it covers well": "modeling and uncertainty context", "Gap left": "not a storage-specific trustworthy-ML deployment audit", "This review contribution": "ML trust, MRV auditability, and evidence mismatch"},
        {"Existing review": "Energy & Fuels ML-driven GCS review", "Scope": "ML applications across CGS", "What it covers well": "method coverage and application survey", "Gap left": "risk of application catalogue", "This review contribution": "field evidence, physics coverage, and decision readiness scoring"},
        {"Existing review": "Results in Engineering ML storage/EOR review", "Scope": "ML for storage/EOR, sim-to-real, deployment roadmap", "What it covers well": "direct ML deployment framing", "Gap left": "includes CO2-EOR and not ESR MRV/evidence-audit focused", "This review contribution": "geological-storage-only MRV and stewardship evidence system"},
        {"Existing review": "Monitoring/MRV and leakage reviews", "Scope": "monitoring, release experiments, risk pathways", "What it covers well": "field realism and detection constraints", "Gap left": "limited ML synthesis", "This review contribution": "ML-enabled auditable MRV and rare-event validation framework"},
    ]
    write_csv(TABLE_DIR / "Table5_competing_review_differentiation.csv", table5)
    csv_to_markdown(TABLE_DIR / "Table5_competing_review_differentiation.csv")

    # Table 2 is the rubric; create a CSV companion.
    rubric = [
        {"Dimension": "Field evidence", "0": "pure synthetic", "1": "realistic/synthetic monitoring", "2": "lab/controlled release", "3": "single field case", "4": "multiple field/cross-site"},
        {"Dimension": "Physical consistency", "0": "none", "1": "qualitative/inherited", "2": "partial constraint", "3": "diagnostic check", "4": "coupled validation"},
        {"Dimension": "Uncertainty", "0": "deterministic", "1": "sensitivity", "2": "probabilistic/posterior", "3": "calibrated", "4": "decision propagated"},
        {"Dimension": "Transferability", "0": "same distribution", "1": "single field/no transfer", "2": "unseen parameter", "3": "unseen geology/OOD", "4": "cross-site"},
        {"Dimension": "Decision readiness", "0": "technical demo", "1": "predicts variable", "2": "linked to decision", "3": "near threshold/field uncertainty", "4": "auditable MRV/operation"},
    ]
    write_csv(TABLE_DIR / "Table2_readiness_scoring_rubric.csv", rubric)
    csv_to_markdown(TABLE_DIR / "Table2_readiness_scoring_rubric.csv")


def write_boxes() -> None:
    boxes = {
        "Box1_what_counts_as_field_validation.md": """# Box 1. What Counts As Field Validation?

Held-out simulation is not field validation. A realistic geomodel is not field validation. A single field monitoring dataset is stronger evidence, but it is not cross-site generalization. For this review, field validation means that the ML workflow is evaluated against observations or interpretations from an operating or experimental storage site. Stronger evidence comes from multiple fields, leave-one-site-out tests, or controlled-release experiments tied to monitoring decisions.
""",
        "Box2_accuracy_is_insufficient_for_plume_prediction.md": """# Box 2. Why Accuracy Is Insufficient For CO2 Plume Prediction

Low global error can hide decision-relevant failure. A model can have low MSE while placing the plume edge incorrectly, biasing pressure near an injection limit, violating injected-volume balance, predicting the wrong migration direction, or producing a plume that is undetectable by the proposed monitoring system. Storage ML should report mass/plume-volume diagnostics, pressure-threshold errors, plume-edge uncertainty, and monitoring detectability, not only global test-set accuracy.
""",
        "Box3_field_projects_as_ml_validation_anchors.md": """# Box 3. Field Projects As ML Validation Anchors

Field projects such as Sleipner, In Salah, Otway, Frio, Cranfield, Decatur, Aquistore, Ketzin, Weyburn-Midale, Quest, and Illinois Basin projects are not interchangeable labels. Each can anchor different evidence types: time-lapse seismic, pressure response, deformation, geochemistry, controlled release, plume history, or operational constraints. The review should use field projects as validation anchors, while distinguishing single-case demonstration from generalizable field transfer.
""",
        "Box4_leakage_detection_as_rare_event_decision.md": """# Box 4. Leakage Detection As A Rare-Event Decision Problem

Leakage detection is not a normal balanced classification problem. True leakage should be rare, labels are sparse, monitoring noise is site-specific, and false positives and false negatives have asymmetric consequences. Evaluation should include probability of detection, false-alarm cost, missed-leakage consequence, monitoring-noise robustness, base-rate sensitivity, and the operational response pathway after an alarm.
""",
        "Box5_minimum_reporting_checklist.md": """# Box 5. Minimum Reporting Checklist For ML-CGS Papers

Minimum reporting items: training data provenance; site/geology represented; simulator, lab, or field source; physics included; physics omitted; input variables; target outputs; baseline; metrics; uncertainty method; OOD or transfer test; field or controlled validation; decision supported; known failure modes; code/data availability; and intended MRV or operational use. A paper that omits these items may be useful technically but is difficult to assess as storage decision evidence.
""",
        "Box6_model_card_for_mrv_facing_ml.md": """# Box 6. Model Card For MRV-Facing ML

An MRV-facing model card should document intended use, excluded use, training data provenance, field cases represented, monitoring modalities, physical constraints, known missing physics, uncertainty calibration, OOD tests, failure modes, human review steps, decision thresholds, version history, and audit logs. The goal is not bureaucratic overhead; it is to make ML outputs reviewable by operators, regulators, and independent technical experts.
""",
    }
    for name, text in boxes.items():
        (BOX_DIR / name).write_text(text, encoding="utf-8")


def write_reports(rows: list[dict[str, str]]) -> None:
    stats = group_stats(rows, "application_area")
    regime_counts = Counter(r["data_regime"] for r in rows)
    validation_counts = Counter(r["validation_type"] for r in rows)
    app_counts = Counter(r["application_area"] for r in rows)
    unknown_lim = sum(1 for r in rows if "full-text" in r["main_limitation"])
    report = [
        "# Evidence Coverage Report",
        "",
        f"Evidence matrix rows: {len(rows)}",
        f"Rows requiring full-text limitation coding: {unknown_lim}",
        "",
        "## Application Coverage",
        "",
        "| Application | N | Avg field evidence | Avg physical consistency | Avg uncertainty | Avg transferability | Avg readiness |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for app, count in app_counts.most_common():
        s = stats[app]
        def fmt(key: str) -> str:
            return "NA" if math.isnan(s[key]) else f"{s[key]:.2f}"
        report.append(f"| {app} | {count} | {fmt('field_evidence_score')} | {fmt('physical_consistency_score')} | {fmt('uncertainty_score')} | {fmt('transferability_score')} | {fmt('overall_readiness_score')} |")
    report += ["", "## Data Regime Counts", ""]
    for regime, count in regime_counts.most_common():
        report.append(f"- {regime}: {count}")
    report += ["", "## Validation Type Counts", ""]
    for val, count in validation_counts.most_common():
        report.append(f"- {val}: {count}")
    report += ["", "## Interpretation", "", "The current corpus is broad enough to support evidence mapping, but many rows remain metadata-coded. The strongest immediate synthesis is the mismatch between decision-critical applications and limited field/cross-site validation, not a claim that each row is fully extracted."]
    (VALIDATION_DIR / "EVIDENCE_COVERAGE_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    figure_files = sorted(FIG_DIR.glob("Figure*.svg"))
    table_files = sorted(TABLE_DIR.glob("Table*.csv"))
    ft_report = [
        "# Figure And Table Readiness Report",
        "",
        "## Vector Figures",
        "",
    ]
    for path in figure_files:
        ft_report.append(f"- PASS: `{path.as_posix()}`")
    ft_report += ["", "## Manuscript-Ready Tables", ""]
    for path in table_files:
        ft_report.append(f"- PASS: `{path.as_posix()}`")
    ft_report += ["", "## Caveat", "", "Figures and tables are reproducible and vector/editable, but their coding basis is currently metadata/title/rubric. Final ESR submission requires full-text confirmation and manual correction of coded fields."]
    (VALIDATION_DIR / "FIGURE_TABLE_READINESS_REPORT.md").write_text("\n".join(ft_report) + "\n", encoding="utf-8")

    risky = []
    for r in rows:
        field = numeric(r["field_evidence_score"])
        critical = numeric(r["decision_criticality_score"])
        if field is not None and critical is not None and field <= 1 and critical >= 3:
            risky.append(r)
    low_report = [
        "# Low-Evidence / High-Criticality Report",
        "",
        f"Rows in low-field-evidence/high-decision-criticality zone: {len(risky)}",
        "",
        "| paper_id | application | title | field score | criticality | validation |",
        "|---|---|---|---:|---:|---|",
    ]
    for r in risky[:80]:
        low_report.append(f"| {r['paper_id']} | {r['application_area']} | {r['title'][:90]} | {r['field_evidence_score']} | {r['decision_criticality_score']} | {r['validation_type']} |")
    low_report += ["", "## Interpretation", "", "These rows drive the manuscript's core thesis: the bottleneck is evidence maturity mismatch, especially where ML supports pressure, injection, monitoring, leakage, wellbore, or geomechanical decisions without field or transfer validation."]
    (VALIDATION_DIR / "LOW_EVIDENCE_HIGH_CRITICALITY_REPORT.md").write_text("\n".join(low_report) + "\n", encoding="utf-8")

    unsupported = [
        "# Unsupported Synthesis Claims",
        "",
        "No manuscript expansion was performed in this task. The evidence products support future claims but do not yet clear a full sentence-level manuscript audit.",
        "",
        "## Claims now supported as synthesis from the matrix",
        "",
        "- ML-CGS evidence is uneven across application areas.",
        "- Simulation-only evidence dominates several dynamic-prediction and optimization categories.",
        "- High-decision-criticality applications should not claim field readiness without field/cross-site evidence.",
        "- Physics coverage is sparse or simulator-inherited for many ML application areas.",
        "",
        "## Claims still requiring full-text support",
        "",
        "- Any paper-specific numerical speed-up, accuracy, F1, RMSE, or uncertainty calibration claim.",
        "- Any claim that a model is operationally or regulator-ready.",
        "- Any claim that a specific field project validates a model beyond what is coded in the matrix.",
    ]
    (VALIDATION_DIR / "UNSUPPORTED_SYNTHESIS_CLAIMS.md").write_text("\n".join(unsupported) + "\n", encoding="utf-8")


def generate_all() -> None:
    ensure_dirs()
    rows = build_evidence_matrix()
    write_csv(EVIDENCE_DIR / "evidence_matrix.csv", rows)
    write_scoring_rubric()
    write_tables(rows)
    figure1(rows)
    figure2(rows)
    figure3(rows)
    figure4(rows)
    figure5()
    figure6(rows)
    write_boxes()
    write_reports(rows)
    figure_readme = """# ESR Vector Figures

All files in this folder are SVG vector graphics generated from `evidence/evidence_matrix.csv` unless otherwise noted. They are intended as editable synthesis figures, not bitmap placeholders.

- Figure 1: decision chain x evidence map.
- Figure 2: simulation-to-field gap alluvial flow.
- Figure 3: evidence maturity map.
- Figure 4: physics constraint coverage heatmap.
- Figure 5: trustworthiness audit ladder.
- Figure 6: case-study evidence map.
"""
    (FIG_DIR / "README.md").write_text(figure_readme, encoding="utf-8")
    table_readme = """# ESR Tables

Tables are generated from the evidence matrix and saved in both CSV and Markdown format where appropriate. CSV files are the data source; Markdown files are quick manuscript-readable renderings.
"""
    (TABLE_DIR / "README.md").write_text(table_readme, encoding="utf-8")
    readme = """# Evidence Backbone

This folder contains the structured evidence matrix and scoring rubric for the ESR rebuild. The matrix is generated from `esr/LITERATURE_MATRIX.csv` using conservative metadata/title coding. It is suitable for building synthesis figures and identifying evidence gaps, but it is not a substitute for full-text extraction.

Main files:

- `evidence_matrix.csv`: one row per paper, with decision, data, physics, validation, and readiness fields.
- `scoring_rubric.md`: reproducible 0-4 scoring rules and overall-readiness formula.
"""
    (EVIDENCE_DIR / "README.md").write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    generate_all()
    print(f"Wrote evidence backbone to {EVIDENCE_DIR}")
    print(f"Wrote vector figures to {FIG_DIR}")
    print(f"Wrote manuscript-ready tables to {TABLE_DIR}")
