import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from models_config import MODELS, TERM_RULES  # noqa: E402


def sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def evaluate_term(term: str, values: dict) -> float:
    rule = TERM_RULES[term]
    if rule["type"] == "direct":
        return float(values[rule["input"]])
    if rule["type"] == "bool":
        return 1.0 if bool(values[rule["input"]]) else 0.0
    if rule["type"] == "equals":
        return 1.0 if values[rule["input"]] == rule["value"] else 0.0
    if rule["type"] == "log1p":
        return math.log1p(float(values[rule["input"]]))
    raise ValueError(term)


def predict(model_key: str, values: dict) -> float:
    model = MODELS[model_key]
    lp = float(model["intercept"])
    for term in model["active_terms"]:
        lp += float(model["coefficients"][term]) * evaluate_term(term, values)
    return sigmoid(lp)


def main():
    sample = {
        "demo_age_years": 50,
        "clin_pain_duration_hours": 24,
        "clin_anorexia": True,
        "clin_nausea": True,
        "clin_guarding_rebound_status": "guarding",
        "clin_heart_rate": 98,
        "lab_wbc": 13.5,
        "lab_lymphocyte_abs": 1.0,
        "lab_crp": 55,
        "ct_appendix_max_diameter_mm": 11,
        "ct_appendix_wall_thickening": True,
        "ct_fat_stranding_grade": "Nhiều",
        "ct_periappendiceal_free_fluid": True,
        "ct_fecalith_present": True,
        "ct_wall_non_enhancement": False,
        "ct_luminal_fluid": True,
        "ct_ileus_or_sbo": False,
    }

    probs = {key: predict(key, sample) for key in MODELS}
    assert all(0.0 < p < 1.0 for p in probs.values())
    print("Smoke test passed.")
    for key, value in probs.items():
        print(key, round(value, 6))


if __name__ == "__main__":
    main()
