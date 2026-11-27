# model_engine.py
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

OBJECTIVE_COLS = [
    "q19_otp_scam_action",
    "q20_before_confirming_transfer",
    "q21_why_check_dfs_fees",
    "q22_safest_online_access",
    "q23_phishing_link_action",
    "q24_before_online_loan_bnpl",
    "q25_why_review_tx_history",
]

PERCEIVED_COLS = [
    "q11_understand_how_dfs_work",
    "q12_know_check_tx_and_balance",
    "q13_understand_dfs_fees",
    "q14_know_protect_info",
    "q15_recognize_suspicious_scams",
    "q16_understand_online_loan_risks",
    "q17_can_compare_dfs",
    "q18_understand_check_tx_details",
]

HABIT_COLS = [
    "q26_prepare_budget",
    "q27_monitor_expenses",
    "q28_save_before_spending",
    "q29_compare_prices",
    "q30_consider_affordability",
    "q31_avoid_unnecessary_purchases",
    "q32_review_tx_history",
    "q33_check_tx_details",
    "q34_check_available_balance",
    "q35_keep_credentials_private",
    "q36_verify_suspicious_requests",
    "q37_check_loan_repayment_terms",
    "q38_pay_loans_on_time",
    "q39_adjust_spending",
    "q40_save_for_emergencies",
    "q41_track_dfs_money_flow",
    "q42_decisions_based_on_needs",
]

DEFAULT_PERSONAS = {
    0: {
        "name": "Active Transactors",
        "summary": "Frequent digital financial service users who actively transact across platforms.",
    },
    1: {
        "name": "At-Risk Novices",
        "summary": "Lower DFS confidence and literacy scores; primary target for campus financial literacy support.",
    },
    2: {
        "name": "Disciplined Savers",
        "summary": "Consistent saving habits, planned money allocation, and strong financial literacy.",
    },
}


def load_artifacts() -> dict[str, Any]:
    """Load both exported .joblib artifacts and cohort medians (for optional quick-mode defaults)."""
    clf_artifact = joblib.load(MODELS_DIR / "dfl_classifier_pipeline.joblib")
    km_artifact = joblib.load(MODELS_DIR / "persona_kmeans_pipeline.joblib")

    medians = {}
    encoded_csv = PROCESSED_DIR / "psu_financial_literacy_encoded.csv"
    if encoded_csv.exists():
        df_ref = pd.read_csv(encoded_csv)
        medians = df_ref.drop(columns=["dfl_score", "dfl_class"], errors="ignore").median().to_dict()

    return {
        "clf_pipe": clf_artifact.get("pipeline") or clf_artifact.get("model"),
        "clf_features": list(clf_artifact["feature_columns"]),
        "clf_threshold": float(clf_artifact.get("threshold", 0.19)),
        "clf_name": clf_artifact.get("model_name", "RF - In-Fold SMOTE"),
        "km_pipe": km_artifact.get("pipeline") or km_artifact.get("model"),
        "km_features": list(km_artifact["feature_columns"]),
        "persona_mapping": km_artifact.get("persona_mapping", DEFAULT_PERSONAS),
        "medians": medians,
    }


def compute_oecd_score(row: dict[str, Any]) -> dict[str, float] | None:
    """Compute the equal-weighted OECD/INFE 0-100 composite score if q11-q42 are present."""
    required = OBJECTIVE_COLS + PERCEIVED_COLS + HABIT_COLS
    if not all(col in row for col in required):
        return None

    obj_score = (sum(float(row[c]) for c in OBJECTIVE_COLS) / len(OBJECTIVE_COLS)) * 100.0
    perc_mean = np.mean([float(row[c]) for c in PERCEIVED_COLS])
    perc_score = ((perc_mean - 1.0) / 4.0) * 100.0
    habit_mean = np.mean([float(row[c]) for c in HABIT_COLS])
    habit_score = ((habit_mean - 1.0) / 4.0) * 100.0

    composite = round((obj_score + perc_score + habit_score) / 3.0, 2)
    return {
        "dfl_score": composite,
        "objective_score": round(obj_score, 1),
        "perceived_score": round(perc_score, 1),
        "habit_score": round(habit_score, 1),
    }


def match_apriori_patterns(row: dict[str, Any], cluster_id: int) -> list[str]:
    """Return human-readable Apriori behavioral patterns triggered by the student's responses."""
    matched: list[str] = []

    if row.get("q07_ewallets") == 1 and row.get("q07_mobile_banking") == 1:
        matched.append("Multi-Platform DFS User (E-Wallets + Mobile Banking bundle)")
    if row.get("q09_send_receive") == 1 and row.get("q09_buy_goods") == 1:
        matched.append("Active Digital Spender (Peer transfers + online purchases)")
    if row.get("q45_divide_planned") == 1 and row.get("q09_save_money") == 1:
        matched.append("Structured Planner (Divides funds by plan + digital saving)")
    if row.get("q46_online_ads") == 1 or row.get("q47_impulse_buying") == 1:
        matched.append("Ad/Impulse Spending Trigger (Elevated below-70 risk indicator)")
    if row.get("q43_likelihood_use_bnpl", 0) >= 4 or row.get("q44_likelihood_use_loan", 0) >= 4:
        matched.append("High Credit/BNPL Openness (Requires interest & fee awareness)")
    if row.get("q47_diff_saving") == 1 and row.get("q47_limited_allowance") == 1:
        matched.append("Budget-Constrained Saver (Limited allowance + difficulty saving)")

    if not matched:
        persona_fallback = {
            0: "Consistent with Active Transactor DFS usage patterns",
            1: "Consistent with At-Risk Novice support profile",
            2: "Consistent with Disciplined Saver budgeting profile",
        }
        matched.append(persona_fallback.get(cluster_id, "General campus financial behavior profile"))

    return matched


def build_data_driven_recommendations(
    row: dict[str, Any],
    is_at_risk: bool,
    cluster_id: int,
    oecd_scores: dict[str, float] | None,
) -> list[str]:
    """Generate targeted recommendations anchored to Notebook 05 top predictors and persona."""
    tips: list[str] = []

    if is_at_risk or (oecd_scores and oecd_scores["dfl_score"] < 70):
        tips.append(
            "Priority: Join a campus financial literacy workshop—your profile falls near or below the OECD 70/100 benchmark."
        )

    if row.get("q45_divide_planned", 0) == 0:
        tips.append(
            "Adopt planned money division: as soon as your allowance arrives, split it into fixed buckets (essentials, savings, wants)."
        )
    if row.get("q48_confidence_managing_dfs", 3) <= 3:
        tips.append(
            "Build digital finance confidence by practicing transaction history checks, fee reviews, and account security settings."
        )
    if row.get("q43_likelihood_use_bnpl", 0) >= 4 or row.get("q44_likelihood_use_loan", 0) >= 4:
        tips.append(
            "Review total repayment costs, interest rates, and late penalties before using BNPL or online lending apps."
        )
    if row.get("q46_online_ads", 0) == 1 or row.get("q47_impulse_buying", 0) == 1:
        tips.append(
            "Counter online ad triggers with a 24-hour cooling-off rule before checking out non-essential items."
        )
    if row.get("q47_diff_saving", 0) == 1 or row.get("q09_save_money", 0) == 0:
        tips.append(
            "Automate a small 'pay yourself first' transfer into a dedicated savings wallet before daily spending."
        )
    if row.get("q49_scam_not_sure", 0) == 1 or row.get("q49_scam_yes", 0) == 1:
        tips.append(
            "Strengthen scam defense: never share OTPs, verify sender domains, and enable two-factor authentication on all e-wallets."
        )

    if not tips:
        if cluster_id == 2:
            tips.append("Your Disciplined Saver habits are strong—consider setting a 3-month post-graduation emergency fund target.")
        else:
            tips.append("Maintain your current budgeting routine and do a monthly audit of digital subscriptions and transfer fees.")

    return tips


def predict_student_profile(raw_inputs: dict[str, Any], artifacts: dict[str, Any]) -> dict[str, Any]:
    """Run both exported pipelines on a single student's encoded survey dictionary."""
    km_features = artifacts["km_features"]
    clf_features = artifacts["clf_features"]
    medians = artifacts["medians"]

    # Build a full 108-column row using student answers + cohort medians as safe fallback
    full_row = {col: raw_inputs.get(col, medians.get(col, 0)) for col in km_features}
    df_full = pd.DataFrame([full_row])

    # 1. Supervised Risk Classifier (RF - In-Fold SMOTE, 76 leakage-free features)
    X_clf = df_full[clf_features]
    risk_prob = float(artifacts["clf_pipe"].predict_proba(X_clf)[0, 0])
    threshold = artifacts["clf_threshold"]
    is_at_risk = risk_prob >= threshold

    # 2. Unsupervised Behavioral Persona (K-Means k=3, 108 features)
    X_km = df_full[km_features]
    cluster_id = int(artifacts["km_pipe"].predict(X_km)[0])
    persona_info = artifacts["persona_mapping"].get(cluster_id, DEFAULT_PERSONAS[cluster_id])

    # 3. Exact OECD/INFE Score (if q11-q42 were answered in Full Assessment mode)
    oecd_scores = compute_oecd_score(raw_inputs)

    # 4. Apriori Pattern Matches & Recommendations
    patterns = match_apriori_patterns(full_row, cluster_id)
    recommendations = build_data_driven_recommendations(full_row, is_at_risk, cluster_id, oecd_scores)

    return {
        "model_name": artifacts["clf_name"],
        "risk_probability": round(risk_prob * 100, 1),
        "threshold_pct": round(threshold * 100, 1),
        "is_at_risk": is_at_risk,
        "literacy_status": "Below Target (< 70)" if is_at_risk else "Meets Target (>= 70)",
        "cluster_id": cluster_id,
        "persona_name": persona_info["name"],
        "persona_summary": persona_info["summary"],
        "oecd_scores": oecd_scores,
        "patterns": patterns,
        "recommendations": recommendations,
    }