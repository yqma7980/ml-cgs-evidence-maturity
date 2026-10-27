#!/usr/bin/env python3
"""Build an ESR-oriented literature seed matrix from Crossref metadata.

This script is intentionally conservative: it records Crossref metadata and
heuristic review classifications, but it does not claim that every returned item
has been content-reviewed. The resulting CSV is a screening artifact for the ESR
rewrite, not a final reference list.
"""

from __future__ import annotations

import csv
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "esr" / "literature" / "ESR_LITERATURE_MATRIX.csv"

QUERIES = [
    ("general_storage_review", "geological CO2 storage review trapping mechanisms monitoring"),
    ("general_storage_review", "CO2 sequestration subsurface geological formations trapping monitoring review"),
    ("general_storage_review", "comprehensive review CO2 geological storage principles mechanisms prospects"),
    ("competing_review", "machine learning driven CO2 geological storage comprehensive review outlook"),
    ("competing_review", "statistical computational perspective CO2 geological storage Earth-Science Reviews"),
    ("site_capacity", "CO2 geological storage site selection capacity assessment machine learning GIS"),
    ("site_capacity", "geologic carbon dioxide storage resource assessment machine learning"),
    ("characterization_inversion", "CO2 saturation seismic inversion machine learning geological storage"),
    ("characterization_inversion", "time-lapse seismic CO2 storage inversion saturation deep learning"),
    ("characterization_inversion", "multiphysics imaging CO2 saturation geological carbon storage uncertainty"),
    ("surrogate_dynamics", "geological carbon storage surrogate model pressure saturation machine learning"),
    ("surrogate_dynamics", "CO2 storage Fourier neural operator pressure saturation"),
    ("surrogate_dynamics", "geologic carbon storage neural operator surrogate model"),
    ("surrogate_dynamics", "CO2 plume migration machine learning heterogeneous formations"),
    ("surrogate_dynamics", "CO2 storage graph neural network faulted reservoirs"),
    ("surrogate_dynamics", "multi-fidelity Fourier neural operator geological carbon storage"),
    ("physics_guided", "physics-informed deep learning CO2 storage site response"),
    ("physics_guided", "physics-informed neural networks CO2 migration saline aquifers"),
    ("optimization_control", "geological CO2 storage injection optimization Bayesian optimization"),
    ("optimization_control", "geological CO2 storage reinforcement learning pressure management"),
    ("optimization_control", "CO2 storage geomechanical risk multiobjective optimization machine learning"),
    ("monitoring_history_mrv", "CO2 storage history matching data assimilation machine learning"),
    ("monitoring_history_mrv", "geological carbon storage monitoring history matching 4D seismic"),
    ("monitoring_history_mrv", "CO2 storage monitoring measurement verification MRV review"),
    ("monitoring_history_mrv", "CO2 storage InSAR surface deformation pressure forecasting data assimilation"),
    ("leakage_wellbore_risk", "CO2 storage leakage risk assessment review"),
    ("leakage_wellbore_risk", "CO2 leakage detection machine learning pressure monitoring geological storage"),
    ("leakage_wellbore_risk", "wellbore leakage risk geologic carbon sequestration deep learning"),
    ("leakage_wellbore_risk", "CO2 release field experiments leakage monitoring review"),
    ("geomechanics_seal", "geological CO2 storage geomechanics induced seismicity review"),
    ("geomechanics_seal", "CO2 storage caprock integrity breakthrough pressure review"),
    ("geochemistry_trapping", "CO2 mineral trapping sedimentary reservoirs review geological storage"),
    ("geochemistry_trapping", "reactive transport geologic carbon sequestration review"),
    ("geochemistry_trapping", "basalt CO2 mineralization geological storage review"),
    ("field_projects", "Sleipner CO2 storage monitoring seismic review"),
    ("field_projects", "In Salah CO2 storage surface deformation geomechanics"),
    ("field_projects", "Otway CO2 storage monitoring seismic plume"),
    ("field_projects", "Cranfield CO2 storage monitoring pressure leakage"),
    ("field_projects", "Illinois Basin Decatur CO2 storage monitoring"),
    ("field_projects", "Aquistore CO2 storage monitoring seismic"),
    ("field_projects", "Frio CO2 storage field experiment monitoring"),
    ("trustworthy_ml", "trustworthy machine learning uncertainty calibration out-of-distribution review"),
    ("trustworthy_ml", "machine learning model risk uncertainty calibration scientific applications"),
]

RELEVANCE_TERMS = [
    "co2",
    "carbon dioxide",
    "carbon storage",
    "carbon sequestration",
    "geological storage",
    "geologic storage",
    "saline aquifer",
    "sleipner",
    "in salah",
    "otway",
    "cranfield",
    "decatur",
    "aquistore",
    "frio",
    "machine learning",
    "neural operator",
    "uncertainty",
    "out-of-distribution",
    "trustworthy",
]


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").replace("\n", " ")).strip()


def first(value: object) -> str:
    if isinstance(value, list) and value:
        return clean_text(str(value[0]))
    if isinstance(value, str):
        return clean_text(value)
    return ""


def authors(item: dict) -> str:
    people = []
    for author in item.get("author", [])[:8]:
        given = author.get("given", "")
        family = author.get("family", "")
        name = clean_text(f"{given} {family}".strip())
        if name:
            people.append(name)
    if len(item.get("author", [])) > 8:
        people.append("et al.")
    return "; ".join(people)


def year(item: dict) -> str:
    for key in ["published-print", "published-online", "published", "issued"]:
        parts = item.get(key, {}).get("date-parts", [])
        if parts and parts[0]:
            return str(parts[0][0])
    return ""


def query_crossref(query: str, rows: int = 15) -> list[dict]:
    params = urllib.parse.urlencode(
        {
            "query.bibliographic": query,
            "rows": rows,
            "select": "DOI,title,author,issued,published-print,published-online,container-title,type,URL,is-referenced-by-count,abstract",
        }
    )
    url = f"https://api.crossref.org/works?{params}"
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.load(response)["message"]["items"]


def classify_data_type(title: str, seed_category: str) -> str:
    t = title.lower()
    if seed_category == "trustworthy_ml":
        return "methodological_review_or_general_ml"
    if any(term in t for term in ["sleipner", "otway", "cranfield", "decatur", "aquistore", "frio", "in salah"]):
        return "field_or_field_project"
    if any(term in t for term in ["review", "perspective", "outlook"]):
        return "review"
    if any(term in t for term in ["simulation", "model", "surrogate", "neural operator", "fno"]):
        return "simulation_or_model"
    if any(term in t for term in ["experiment", "laboratory", "core", "pore-scale", "release"]):
        return "laboratory_or_controlled_field"
    if any(term in t for term in ["seismic", "monitoring", "insar", "pressure"]):
        return "monitoring_or_geophysical"
    return "unclear"


def classify_stage(seed_category: str) -> str:
    mapping = {
        "general_storage_review": "storage_context",
        "competing_review": "review_positioning",
        "site_capacity": "pre_injection_decision",
        "characterization_inversion": "characterization",
        "surrogate_dynamics": "dynamic_prediction",
        "physics_guided": "physics_guided_learning",
        "optimization_control": "operation_control",
        "monitoring_history_mrv": "monitoring_mrv",
        "leakage_wellbore_risk": "risk_response",
        "geomechanics_seal": "seal_and_geomechanics",
        "geochemistry_trapping": "trapping_and_geochemistry",
        "field_projects": "field_evidence",
        "trustworthy_ml": "trustworthiness_methods",
    }
    return mapping.get(seed_category, seed_category)


def readiness(seed_category: str, data_type: str, title: str) -> str:
    t = title.lower()
    if seed_category == "trustworthy_ml":
        return "cross_domain_method_context"
    if data_type == "field_or_field_project":
        return "field_evidence_context"
    if "review" in t:
        return "review_context"
    if data_type == "simulation_or_model":
        return "simulation_only_or_model_based"
    if data_type == "laboratory_or_controlled_field":
        return "lab_or_controlled_field"
    return "screening_needed"


def is_relevant(title: str, seed_category: str) -> bool:
    lower = title.lower()
    if seed_category == "trustworthy_ml":
        return any(term in lower for term in ["uncertainty", "calibration", "out-of-distribution", "trustworthy", "model risk"])
    storage_anchor = any(
        term in lower
        for term in [
            "co2",
            "co<sub>2</sub>",
            "carbon dioxide",
            "carbon storage",
            "carbon sequestration",
            "geological storage",
            "geologic storage",
            "sleipner",
            "in salah",
            "otway",
            "cranfield",
            "decatur",
            "aquistore",
            "frio",
        ]
    )
    return storage_anchor and any(term in lower for term in RELEVANCE_TERMS)


def main() -> int:
    rows: list[dict[str, str]] = []
    seen: set[str] = set()

    for seed_category, query in QUERIES:
        try:
            items = query_crossref(query)
        except Exception as exc:  # pragma: no cover - network guard
            print(f"WARN: query failed: {query}: {exc}")
            continue
        time.sleep(0.2)
        for item in items:
            title = first(item.get("title"))
            doi = clean_text(item.get("DOI", ""))
            if not title:
                continue
            key = doi.lower() if doi else title.lower()
            if key in seen:
                continue
            if not is_relevant(title, seed_category):
                continue
            seen.add(key)
            data_type = classify_data_type(title, seed_category)
            pid_root = re.sub(r"[^A-Za-z0-9]+", "", (authors(item).split(";")[0].split()[-1] if authors(item) else "Ref"))[:18]
            y = year(item) or "YYYY"
            paper_id = f"ESR_{pid_root}{y}_{len(rows)+1:03d}"
            rows.append(
                {
                    "paper_id": paper_id,
                    "title": title,
                    "authors": authors(item),
                    "year": y,
                    "venue": first(item.get("container-title")),
                    "doi_or_url": f"https://doi.org/{doi}" if doi else clean_text(item.get("URL", "")),
                    "storage_stage": classify_stage(seed_category),
                    "geological_process": "",
                    "decision_supported": "",
                    "data_type": data_type,
                    "ml_method": "",
                    "physics_included": "",
                    "uncertainty_treatment": "",
                    "validation_type": data_type,
                    "field_case": "",
                    "main_contribution": "",
                    "limitation": "",
                    "evidence_maturity_level": readiness(seed_category, data_type, title),
                    "review_section": "",
                    "seed_query_category": seed_category,
                    "crossref_referenced_by": str(item.get("is-referenced-by-count", "")),
                    "metadata_source": "Crossref API",
                    "content_screening_status": "metadata_seed_needs_content_review",
                }
            )

    rows.sort(key=lambda row: (row["storage_stage"], -int(row["crossref_referenced_by"] or 0), row["year"]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
