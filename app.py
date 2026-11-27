import base64
from pathlib import Path

import streamlit as st

from model_engine import load_artifacts, predict_student_profile

import pandas as pd  # Add this with your other imports at the top of app.py


st.set_page_config(
    page_title="Digital Financial Literacy Kiosk",
    layout="centered",
    initial_sidebar_state="collapsed",
)


@st.cache_resource(show_spinner="Loading ML models...")
def get_model_artifacts() -> dict:
    return load_artifacts()

@st.cache_resource(show_spinner=False)
def get_demo_profiles(_artifacts: dict) -> dict[int, dict]:
    """Find one real anonymized profile per K-Means cluster (0, 1, 2) under Quick Screening."""
    csv_path = Path(__file__).resolve().parent / "data" / "processed" / "psu_financial_literacy_encoded.csv"
    clf_cols = _artifacts["clf_features"]
    km_cols = _artifacts["km_features"]
    medians = _artifacts["medians"]

    if csv_path.exists():
        df = pd.read_csv(csv_path)
        buckets: dict[int, list[tuple[float, dict]]] = {0: [], 1: [], 2: []}
        all_rows = []
        km_pipe = _artifacts["km_pipe"]

        for i in range(len(df)):
            sample = df.loc[i, clf_cols].to_dict()
            res = predict_student_profile(sample, _artifacts)
            buckets[res["cluster_id"]].append((res["risk_probability"], sample))

            full_row = {col: sample.get(col, medians.get(col, 0)) for col in km_cols}
            dists = km_pipe.transform(pd.DataFrame([full_row]))[0]
            all_rows.append((dists, sample))

        selected: dict[int, dict] = {}
        # Cluster 0 (Active Transactors): representative mid-risk respondent
        if buckets[0]:
            buckets[0].sort(key=lambda x: x[0])
            selected[0] = buckets[0][len(buckets[0]) // 2][1]
        else:
            selected[0] = min(all_rows, key=lambda x: x[0][0])[1]

        # Cluster 1 (At-Risk Novices): highest-risk respondent
        if buckets[1]:
            buckets[1].sort(key=lambda x: x[0])
            selected[1] = buckets[1][-1][1]
        else:
            selected[1] = min(all_rows, key=lambda x: x[0][1])[1]

        # Cluster 2 (Disciplined Savers): lowest-risk (passing) respondent
        if buckets[2]:
            buckets[2].sort(key=lambda x: x[0])
            selected[2] = buckets[2][0][1]
        else:
            selected[2] = min(all_rows, key=lambda x: x[0][2])[1]

        return selected

    return {0: {}, 1: {}, 2: {}}

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Fraunces:opsz,wght@9..144,600&display=swap');

:root {
    --bg-1: #fef3e2;
    --bg-2: #f4ae52;
    --card: #fef3e2;
    --ink: #2a1a0e;
    --accent: #d4621a;
    --muted: #8f5c34;
}

[data-testid="stAppViewContainer"] {
    background: var(--bg-1);
    color: var(--ink);
}

/* Kiosk mode: remove Streamlit top bar and menu chrome */
[data-testid="stHeader"],
[data-testid="stToolbar"],
#MainMenu,
footer {
    display: none !important;
}

[data-testid="stAppViewContainer"] > .main {
    padding-top: 0.5rem;
}

.logo-header {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.8rem;
}

.logo-header img {
    display: block;
    height: 84px;
    width: auto;
}

h1, h2, h3 {
    font-family: "Fraunces", serif !important;
    letter-spacing: -0.01em;
}

p, label, div, span, button, input {
    font-family: "Space Grotesk", sans-serif !important;
}

div.stButton > button,
div.stFormSubmitButton > button {
    background: var(--accent);
    color: #fef3e2;
    border: 0;
    border-radius: 12px;
    font-weight: 700;
    padding: 0.5rem 1rem;
    transform: translateY(0);
    box-shadow: 0 2px 0 rgba(42, 26, 14, 0.18);
    transition: transform 150ms ease, box-shadow 150ms ease !important;
}

div.stButton > button[data-testid="stBaseButton-secondary"] {
    background: #f7d9b8 !important;
    color: var(--ink) !important;
    border: 1px solid rgba(42, 26, 14, 0.22) !important;
    box-shadow: 0 1px 0 rgba(42, 26, 14, 0.12);
}

div.stButton > button:hover,
div.stButton > button:active,
div.stButton > button:focus,
div.stButton > button:focus-visible,
div.stFormSubmitButton > button:hover,
div.stFormSubmitButton > button:active,
div.stFormSubmitButton > button:focus,
div.stFormSubmitButton > button:focus-visible {
    background: var(--accent) !important;
    color: #fef3e2 !important;
    border: 0 !important;
    box-shadow: 0 8px 18px rgba(42, 26, 14, 0.22) !important;
    transform: translateY(-1px) scale(1.01) !important;
    opacity: 1 !important;
}

div.stButton > button[data-testid="stBaseButton-secondary"]:hover,
div.stButton > button[data-testid="stBaseButton-secondary"]:active,
div.stButton > button[data-testid="stBaseButton-secondary"]:focus,
div.stButton > button[data-testid="stBaseButton-secondary"]:focus-visible {
    background: #f7d9b8 !important;
    color: var(--ink) !important;
    border: 1px solid rgba(42, 26, 14, 0.22) !important;
    box-shadow: 0 6px 14px rgba(42, 26, 14, 0.16) !important;
    transform: translateY(-1px) scale(1.01) !important;
}

@media (prefers-reduced-motion: reduce) {
    div.stButton > button,
    div.stFormSubmitButton > button {
        transition: none !important;
        transform: none !important;
    }
}

/* Ensure dark text on light background across all widget labels */
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label,
[data-testid="stRadio"] label,
[data-testid="stRadio"] label p,
[data-testid="stRadio"] label span,
div[role="radiogroup"] p,
div[role="radiogroup"] span,
.stCheckbox label,
.stCheckbox label p,
.stCheckbox label span,
[data-testid="stCaptionContainer"] p {
    color: var(--ink) !important;
}

.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div {
    background: #ffffff !important;
    color: var(--ink) !important;
    border: 1px solid rgba(42, 26, 14, 0.25) !important;
}

.stSelectbox div[data-baseweb="select"] > div:focus-within,
.stMultiSelect div[data-baseweb="select"] > div:focus-within {
    color: var(--ink) !important;
    border: 1px solid rgba(212, 98, 26, 0.55) !important;
    box-shadow: 0 0 0 1px rgba(212, 98, 26, 0.3) !important;
}

[data-testid="stAlert"] {
    background: rgba(244, 174, 82, 0.2);
    border: 1px solid rgba(212, 98, 26, 0.35);
    color: var(--ink);
}

[data-testid="stDialog"] [role="dialog"] {
    background: #FEF3E2 !important;
    border: 1px solid #c9cbd1 !important;
    color: #2f3138 !important;
}

[data-testid="stDialog"] [role="dialog"] h1,
[data-testid="stDialog"] [role="dialog"] h2,
[data-testid="stDialog"] [role="dialog"] h3,
[data-testid="stDialog"] [role="dialog"] p,
[data-testid="stDialog"] [role="dialog"] li,
[data-testid="stDialog"] [role="dialog"] span,
[data-testid="stDialog"] [role="dialog"] div {
    color: #2f3138 !important;
}

.kpi-row {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 0.6rem;
    margin-top: 0.8rem;
}

.kpi-card {
    background: rgba(254, 243, 226, 0.9);
    border: 1px solid rgba(212, 98, 26, 0.35);
    border-radius: 12px;
    padding: 0.75rem;
}

.apriori-card {
    grid-column: 1 / -1;
    justify-self: center;
    width: min(460px, 100%);
}

.kpi-label {
    font-size: 0.82rem;
    color: var(--muted);
}

.kpi-value {
    font-size: 1.15rem;
    font-weight: 700;
    margin-top: 0.2rem;
}

.kpi-sub {
    font-size: 0.78rem;
    color: var(--muted);
    margin-top: 0.2rem;
}

@media (max-width: 640px) {
    .logo-header img {
        height: 68px;
    }

    .kpi-row {
        grid-template-columns: 1fr;
    }

    .apriori-card {
        width: 100%;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


# --- Exact Option-to-Column Maps (Aligned with Notebook 02 Encoding) ---
AGE_GROUP_MAP = {
    "18–20 years old": 0,
    "21–22 years old": 1,
    "23–24 years old": 2,
    "25 years old and above": 3,
}

SEX_MAP = {
    "Male": "q02_male",
    "Female": "q02_female",
    "Prefer not to say": "q02_prefer_not",
}

PROGRAM_MAP = {
    "BS Computer Science (BSCS)": "q03_bscs",
    "BS Information Technology (BSIT)": "q03_bsit",
    "BS Marine Biology (BSMB)": "q03_bsmb",
    "BS Biology – Medical Biology (BSBio-Med)": "q03_bsbio_med",
    "BS Environmental Science (BSES)": "q03_bses",
}

FUND_SOURCE_MAP = {
    "Family / Parental Allowance": "q04_allowance",
    "Scholarship / Grant": "q04_scholarship",
    "Part-time / Full-time Employment": "q04_employment",
    "Personal Savings": "q04_personal_savings",
    "Small Business / Freelancing": "q04_business",
    "Other": "q04_other",
}

ALLOWANCE_MAP = {
    "Below ₱2,000": 0,
    "₱2,000 – ₱3,999": 1,
    "₱4,000 – ₱5,999": 2,
    "₱6,000 – ₱9,999": 3,
    "₱10,000 – ₱14,999": 4,
    "₱15,000 and above": 5,
}

DFS_PLATFORM_MAP = {
    "E-Wallets (GCash, Maya, etc.)": "q07_ewallets",
    "Mobile Banking Apps": "q07_mobile_banking",
    "Online Banking (Web Browser)": "q07_online_banking_web",
    "Online Payment Gateways / Checkout": "q07_online_payment",
    "Digital Savings / Investment Apps": "q07_digital_savings_inv",
    "Buy Now, Pay Later (SPayLater, BillEase, etc.)": "q07_bnpl",
    "Online Lending Apps": "q07_online_lending",
    "None": "q07_none",
    "Other": "q07_other",
}

DFS_FREQ_MAP = {
    "1 – Never / Rarely": 1,
    "2 – A few times a month": 2,
    "3 – Once a week": 3,
    "4 – Several times a week": 4,
    "5 – Daily": 5,
}

DFS_ACTIVITY_MAP = {
    "Send or receive money": "q09_send_receive",
    "Pay bills / utilities / load": "q09_pay_bills",
    "Buy goods or services online": "q09_buy_goods",
    "Receive allowance or scholarship": "q09_receive_allowance",
    "Save money digitally": "q09_save_money",
    "Transfer between accounts": "q09_transfer_accounts",
    "Borrow money / pay installments": "q09_borrow_installment",
    "Check account balance / history": "q09_check_balance",
    "Other": "q09_other",
}

DFS_DURATION_MAP = {
    "Not using / Less than 6 months": 0,
    "6 months to 1 year": 1,
    "1 to 2 years": 2,
    "2 to 3 years": 3,
    "More than 3 years": 4,
}

LIKELIHOOD_MAP = {
    "0 – Not Applicable / Unsure": 0,
    "1 – Very Unlikely": 1,
    "2 – Unlikely": 2,
    "3 – Neutral": 3,
    "4 – Likely": 4,
    "5 – Very Likely": 5,
}

MONEY_APPROACH_MAP = {
    "Save a portion first": "q45_save",
    "Spend on essentials first": "q45_essentials",
    "Spend on wants first": "q45_wants",
    "Divide into planned categories / budget": "q45_divide_planned",
    "No specific approach": "q45_no_approach",
    "Other": "q45_other",
}

SPENDING_INFLUENCE_MAP = {
    "Personal needs": "q46_personal_needs",
    "Available budget": "q46_available_budget",
    "Family needs": "q46_family_needs",
    "Friends / social circle": "q46_friends_social",
    "Online ads / social media": "q46_online_ads",
    "Discounts / promos / flash sales": "q46_discounts_promos",
    "Convenience of digital payments": "q46_digital_convenience",
    "Other": "q46_other",
}

CHALLENGE_MAP = {
    "Limited allowance / income": "q47_limited_allowance",
    "Difficulty saving consistently": "q47_diff_saving",
    "Difficulty budgeting": "q47_diff_budgeting",
    "Unexpected expenses": "q47_unexpected_expenses",
    "Impulse buying": "q47_impulse_buying",
    "Limited knowledge of digital financial tools": "q47_limited_dfs_knowledge",
    "Concern about online scams": "q47_scam_concern",
    "Difficulty understanding fees / interest / terms": "q47_diff_fees_terms",
    "None": "q47_none",
    "Other": "q47_other",
}

SCAM_MAP = {
    "Yes": "q49_scam_yes",
    "No": "q49_scam_no",
    "Not sure": "q49_scam_not_sure",
    "Prefer not to say": "q49_scam_prefer_not",
}

TOPIC_INTEREST_MAP = {
    "Budgeting": "q50_budgeting",
    "Saving strategies": "q50_saving",
    "Digital payments & e-wallets": "q50_digital_payments",
    "Account & data protection": "q50_account_protection",
    "Recognizing online scams": "q50_recognizing_scams",
    "Loans, interest rates & fees": "q50_loans_interest_fees",
    "Future financial planning": "q50_future_planning",
    "Other": "q50_other",
}


def encode_multi(selected_labels: list[str], mapping: dict[str, str]) -> dict[str, int]:
    selected_cols = {mapping[label] for label in selected_labels if label in mapping}
    return {col: (1 if col in selected_cols else 0) for col in mapping.values()}


def encode_single(selected_label: str, mapping: dict[str, str]) -> dict[str, int]:
    chosen_col = mapping.get(selected_label)
    return {col: (1 if col == chosen_col else 0) for col in mapping.values()}

def decode_ordinal(val: int, mapping: dict[str, int], fallback_idx: int = 0) -> int:
    keys = list(mapping.keys())
    for idx, label in enumerate(keys):
        if mapping[label] == int(round(val)):
            return idx
    return fallback_idx


def decode_single(row: dict, mapping: dict[str, str], fallback_idx: int = 0) -> int:
    keys = list(mapping.keys())
    for idx, label in enumerate(keys):
        if row.get(mapping[label], 0) == 1:
            return idx
    return fallback_idx


def decode_multi(row: dict, mapping: dict[str, str]) -> list[str]:
    return [label for label, col in mapping.items() if row.get(col, 0) == 1]


def decode_profile_to_ui(row: dict) -> dict:
    """Convert an encoded 76-feature dictionary back into Streamlit widget defaults."""
    return {
        "age_idx": decode_ordinal(row.get("q01_age_group", 1), AGE_GROUP_MAP, 1),
        "sex_idx": decode_single(row, SEX_MAP, 0),
        "program_idx": decode_single(row, PROGRAM_MAP, 0),
        "allowance_idx": decode_ordinal(row.get("q05_monthly_allowance", 2), ALLOWANCE_MAP, 2),
        "fund_sources": decode_multi(row, FUND_SOURCE_MAP),
        "uses_dfs_idx": 0 if row.get("q06_currently_uses_dfs", 1) == 1 else 1,
        "dfs_platforms": decode_multi(row, DFS_PLATFORM_MAP),
        "dfs_freq_idx": decode_ordinal(row.get("q08_dfs_usage_frequency", 4), DFS_FREQ_MAP, 3),
        "dfs_duration_idx": decode_ordinal(row.get("q10_dfs_usage_duration", 2), DFS_DURATION_MAP, 2),
        "dfs_activities": decode_multi(row, DFS_ACTIVITY_MAP),
        "bnpl_idx": decode_ordinal(row.get("q43_likelihood_use_bnpl", 2), LIKELIHOOD_MAP, 2),
        "loan_idx": decode_ordinal(row.get("q44_likelihood_use_loan", 1), LIKELIHOOD_MAP, 1),
        "money_approach": decode_multi(row, MONEY_APPROACH_MAP),
        "spending_influences": decode_multi(row, SPENDING_INFLUENCE_MAP),
        "challenges": decode_multi(row, CHALLENGE_MAP),
        "dfs_confidence": max(1, min(5, int(round(row.get("q48_confidence_managing_dfs", 3))))),
        "scam_idx": decode_single(row, SCAM_MAP, 1),
        "topics_interest": decode_multi(row, TOPIC_INTEREST_MAP),
    }


def reset_session(target_screen: str = "profile") -> None:
    st.session_state.step1_encoded = {}
    st.session_state.step2_encoded = {}
    st.session_state.form_defaults = None
    st.session_state.submitted_labels = {}
    st.session_state.result = None
    st.session_state.screen = target_screen


# --- Session State Initialization ---
if "screen" not in st.session_state:
    st.session_state.screen = "welcome"
if "step1_encoded" not in st.session_state:
    st.session_state.step1_encoded = {}
if "step2_encoded" not in st.session_state:
    st.session_state.step2_encoded = {}
if "result" not in st.session_state:
    st.session_state.result = None

if "psu_logo_b64" not in st.session_state:
    psu_path = Path(__file__).resolve().parent / "logos" / "PSU Logo.png"
    st.session_state.psu_logo_b64 = (
        base64.b64encode(psu_path.read_bytes()).decode("utf-8") if psu_path.exists() else ""
    )

if "cs_logo_b64" not in st.session_state:
    cs_path = Path(__file__).resolve().parent / "logos" / "CS Logo.png"
    st.session_state.cs_logo_b64 = (
        base64.b64encode(cs_path.read_bytes()).decode("utf-8") if cs_path.exists() else ""
    )
if "form_defaults" not in st.session_state:
    st.session_state.form_defaults = None
if "submitted_labels" not in st.session_state:
    st.session_state.submitted_labels = {}


@st.dialog("How Does It Work?")
def show_how_it_works() -> None:
    st.write("This offline campus kiosk screens digital financial literacy in two quick steps:")
    st.markdown(
        """
1. **Student & DFS Profile (Q1–Q10)**
   Share basic demographics, allowance tier, and digital financial service (DFS) usage habits.

2. **Financial Behavior & Challenges (Q43–Q50)**
   Answer brief questions on budgeting approach, BNPL/loan openness, DFS confidence, and financial challenges.

3. **Machine Learning Screening**
   Your responses are evaluated by our trained **Random Forest** early-warning classifier (benchmarked against Logistic Regression under the **OECD/INFE 70/100** target), **K-Means** behavioral persona clustering, and **Apriori** pattern matching.

4. **Actionable Recommendations**
   Receive tailored suggestions based on your specific behavioral risk drivers and persona.
        """
    )
    st.caption("No personal names or student IDs are stored—responses are processed locally on this kiosk.")

# --- Load ML Pipelines Once ---
artifacts = get_model_artifacts()

with st.container():
    st.markdown(
        f"""
<div class="logo-header">
    <img src="data:image/png;base64,{st.session_state.get('psu_logo_b64', '')}" alt="PSU Logo"/>
    <img src="data:image/png;base64,{st.session_state.get('cs_logo_b64', '')}" alt="CS Logo"/>
</div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.screen == "welcome":
        st.title("Digital Financial Literacy Assessment")
        st.write(
            "An offline campus kiosk for screening graduating students' digital financial literacy "
            "against the OECD/INFE 70/100 benchmark—powered by our top-performing **Random Forest** "
            "classifier (benchmarked against Logistic Regression), **K-Means Clustering**, and "
            "**Apriori Association Rule Learning**."
        )

        if st.button("Start Quick Screening", use_container_width=True, type="primary"):
            reset_session("profile")
            st.rerun()

        if st.button("How Does It Work?", use_container_width=True, key="how_it_works_btn", type="secondary"):
            show_how_it_works()
       # Hidden defense presets: only visible at http://localhost:8501/?demo=true
        if st.query_params.get("demo") == "true":
            st.divider()
            st.caption("Defense Demo Mode (1 Anonymized Respondent per K-Means Persona)")
            demo_profiles = get_demo_profiles(artifacts)

            d_col0, d_col1, d_col2 = st.columns(3)
            with d_col0:
                if st.button("Cluster 0: Active Transactors", use_container_width=True, type="secondary"):
                    reset_session("profile")
                    st.session_state.form_defaults = decode_profile_to_ui(demo_profiles[0])
                    st.rerun()
            with d_col1:
                if st.button("Cluster 1: At-Risk Novices", use_container_width=True, type="secondary"):
                    reset_session("profile")
                    st.session_state.form_defaults = decode_profile_to_ui(demo_profiles[1])
                    st.rerun()
            with d_col2:
                if st.button("Cluster 2: Disciplined Savers", use_container_width=True, type="secondary"):
                    reset_session("profile")
                    st.session_state.form_defaults = decode_profile_to_ui(demo_profiles[2])
                    st.rerun()

    elif st.session_state.screen == "profile":
        st.header("Step 1 of 2: Student & DFS Profile")
        st.caption("Quick Screening — Questions 1 to 10")

        d = st.session_state.form_defaults or {}
        if st.session_state.form_defaults:
            st.info("Demo preset loaded — review the pre-selected answers below, then click Continue.")
        with st.form("profile_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                age_label = st.selectbox("1. Age Group", list(AGE_GROUP_MAP.keys()), index=d.get("age_idx", 1))
                sex_label = st.radio("2. Sex", list(SEX_MAP.keys()), index=d.get("sex_idx", 0), horizontal=True)
            with col_b:
                program_label = st.selectbox("3. Degree Program", list(PROGRAM_MAP.keys()), index=d.get("program_idx", 0))
                allowance_label = st.selectbox("5. Monthly Allowance / Income", list(ALLOWANCE_MAP.keys()), index=d.get("allowance_idx", 2))

            fund_sources = st.multiselect(
                "4. Primary Sources of Funds (select all that apply)",
                list(FUND_SOURCE_MAP.keys()),
                default=d.get("fund_sources", ["Family / Parental Allowance"]),
            )

            uses_dfs = st.radio(
                "6. Do you currently use any Digital Financial Services (e-wallets, mobile banking, etc.)?",
                ["Yes", "No"],
                index=d.get("uses_dfs_idx", 0),
                horizontal=True,
            )

            dfs_platforms = st.multiselect(
                "7. Which Digital Financial Services do you use?",
                list(DFS_PLATFORM_MAP.keys()),
                default=d.get("dfs_platforms", ["E-Wallets (GCash, Maya, etc.)"]),
            )

            col_c, col_d = st.columns(2)
            with col_c:
                dfs_freq_label = st.selectbox("8. How often do you use DFS?", list(DFS_FREQ_MAP.keys()), index=d.get("dfs_freq_idx", 3))
            with col_d:
                dfs_duration_label = st.selectbox("10. How long have you been using DFS?", list(DFS_DURATION_MAP.keys()), index=d.get("dfs_duration_idx", 2))

            dfs_activities = st.multiselect(
                "9. What do you usually use DFS for?",
                list(DFS_ACTIVITY_MAP.keys()),
                default=d.get("dfs_activities", ["Send or receive money", "Buy goods or services online"]),
            )

            left, right = st.columns(2)
            with left:
                go_back = st.form_submit_button("Back", use_container_width=True)
            with right:
                go_next = st.form_submit_button("Continue to Step 2", use_container_width=True)

            if go_back:
                st.session_state.screen = "welcome"
                st.rerun()

            if go_next:
                encoded_step1 = {
                    "q01_age_group": AGE_GROUP_MAP[age_label],
                    "q05_monthly_allowance": ALLOWANCE_MAP[allowance_label],
                    "q06_currently_uses_dfs": 1 if uses_dfs == "Yes" else 0,
                    "q08_dfs_usage_frequency": DFS_FREQ_MAP[dfs_freq_label],
                    "q10_dfs_usage_duration": DFS_DURATION_MAP[dfs_duration_label],
                }
                encoded_step1.update(encode_single(sex_label, SEX_MAP))
                encoded_step1.update(encode_single(program_label, PROGRAM_MAP))
                encoded_step1.update(encode_multi(fund_sources, FUND_SOURCE_MAP))
                encoded_step1.update(encode_multi(dfs_platforms, DFS_PLATFORM_MAP))
                encoded_step1.update(encode_multi(dfs_activities, DFS_ACTIVITY_MAP))

                st.session_state.step1_encoded = encoded_step1
                st.session_state.screen = "questionnaire"
                st.rerun()

    elif st.session_state.screen == "questionnaire":
        st.header("Step 2 of 2: Financial Behavior & Habits")
        st.caption("Quick Screening — Questions 43 to 50")

        d = st.session_state.form_defaults or {}
        if st.session_state.form_defaults:
            st.info("Demo preset loaded — review the pre-selected answers below, then click Generate Result.")

        with st.form("questionnaire_form"):
            col_1, col_2 = st.columns(2)
            with col_1:
                bnpl_label = st.selectbox(
                    "43. Likelihood of using Buy Now, Pay Later (BNPL)",
                    list(LIKELIHOOD_MAP.keys()),
                    index=d.get("bnpl_idx", 2),
                )
            with col_2:
                loan_label = st.selectbox(
                    "44. Likelihood of using Online Lending Apps",
                    list(LIKELIHOOD_MAP.keys()),
                    index=d.get("loan_idx", 1),
                )

            money_approach = st.multiselect(
                "45. When you receive money/allowance, how do you usually manage it?",
                list(MONEY_APPROACH_MAP.keys()),
                default=d.get("money_approach", ["Divide into planned categories / budget"]),
            )

            spending_influences = st.multiselect(
                "46. What factors most influence your spending decisions?",
                list(SPENDING_INFLUENCE_MAP.keys()),
                default=d.get("spending_influences", ["Personal needs", "Available budget"]),
            )

            challenges = st.multiselect(
                "47. What financial challenges do you currently experience?",
                list(CHALLENGE_MAP.keys()),
                default=d.get("challenges", ["Limited allowance / income"]),
            )

            dfs_confidence = st.slider(
                "48. How confident are you in managing your finances using DFS? (1 = Not confident, 5 = Very confident)",
                min_value=1,
                max_value=5,
                value=d.get("dfs_confidence", 3),
            )

            scam_label = st.radio(
                "49. Have you ever experienced or encountered a digital financial scam?",
                list(SCAM_MAP.keys()),
                index=d.get("scam_idx", 1),
                horizontal=True,
            )

            topics_interest = st.multiselect(
                "50. Which financial literacy topics would you like to learn more about?",
                list(TOPIC_INTEREST_MAP.keys()),
                default=d.get("topics_interest", ["Budgeting", "Saving strategies"]),
            )

            left, right = st.columns(2)
            with left:
                go_back = st.form_submit_button("Back to Step 1", use_container_width=True)
            with right:
                submit = st.form_submit_button("Generate Result", use_container_width=True)

            if go_back:
                st.session_state.screen = "profile"
                st.rerun()

            if submit:
                encoded_step2 = {
                    "q43_likelihood_use_bnpl": LIKELIHOOD_MAP[bnpl_label],
                    "q44_likelihood_use_loan": LIKELIHOOD_MAP[loan_label],
                    "q48_confidence_managing_dfs": int(dfs_confidence),
                }
                encoded_step2.update(encode_multi(money_approach, MONEY_APPROACH_MAP))
                encoded_step2.update(encode_multi(spending_influences, SPENDING_INFLUENCE_MAP))
                encoded_step2.update(encode_multi(challenges, CHALLENGE_MAP))
                encoded_step2.update(encode_single(scam_label, SCAM_MAP))
                encoded_step2.update(encode_multi(topics_interest, TOPIC_INTEREST_MAP))

                st.session_state.step2_encoded = encoded_step2
                combined_inputs = {**st.session_state.step1_encoded, **encoded_step2}

                st.session_state.result = predict_student_profile(combined_inputs, artifacts)
                st.session_state.screen = "result"
                st.rerun()

    elif st.session_state.screen == "result":
        result = st.session_state.result
        if result is None:
            st.session_state.screen = "welcome"
            st.rerun()

        st.header("Assessment Result")
        st.subheader(f"OECD/INFE Screening: {result['literacy_status']}")

        pattern_count = len(result["patterns"])
        pattern_label = f"{pattern_count} pattern{'s' if pattern_count != 1 else ''} matched"

        st.markdown(
            f"""
<div class="kpi-row">
  <div class="kpi-card">
    <div class="kpi-label">At-Risk Probability ({result['model_name']})</div>
    <div class="kpi-value">{result['risk_probability']}%</div>
    <div class="kpi-sub">Early-warning cutoff: &ge; {result['threshold_pct']}%</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Financial Behavior Persona (K-Means)</div>
    <div class="kpi-value">{result['persona_name']}</div>
    <div class="kpi-sub">Cluster {result['cluster_id']}</div>
  </div>
  <div class="kpi-card apriori-card">
    <div class="kpi-label">Apriori Behavioral Patterns</div>
    <div class="kpi-value">{pattern_label}</div>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        st.write("### What This Means")
        if result["is_at_risk"]:
            st.warning(
                f"Your behavioral risk probability (**{result['risk_probability']}%**) reached or exceeded "
                f"the **{result['threshold_pct']}%** early-warning threshold for falling below the "
                "OECD/INFE 70/100 target. Check the Suggestions page for targeted habits to strengthen."
            )
        else:
            st.success(
                f"Your behavioral risk probability (**{result['risk_probability']}%**) is below the "
                f"**{result['threshold_pct']}%** early-warning threshold, indicating habits aligned with "
                "meeting the OECD/INFE 70/100 target."
            )

        st.write(f"**Persona Summary ({result['persona_name']}):** {result['persona_summary']}")

        st.write("**Detected Apriori Patterns:**")
        for pat in result["patterns"]:
            st.write(f"- {pat}")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("View Suggestions", use_container_width=True, type="secondary"):
                st.session_state.screen = "recommendations"
                st.rerun()
        with col2:
            if st.button("Assess Another", use_container_width=True, type="primary"):
                reset_session("profile")
                st.rerun()

    elif st.session_state.screen == "recommendations":
        result = st.session_state.result
        if result is None:
            st.session_state.screen = "welcome"
            st.rerun()

        st.header("Recommendations & Next Steps")
        st.write(
            f"Tailored for your **{result['persona_name']}** profile "
            f"(**{result['literacy_status']}**, risk signal: **{result['risk_probability']}%**):"
        )

        for i, tip in enumerate(result["recommendations"], start=1):
            st.write(f"{i}. {tip}")

        st.write("### Quick Habit Plan")
        st.write("- **Daily:** Record expenses and check e-wallet balances before spending.")
        st.write("- **Weekly:** Divide allowance into essentials, savings, and wants; audit impulse buys.")
        st.write("- **Monthly:** Review transaction history, transfer fees, and progress on your savings goal.")

        left, right = st.columns(2)
        with left:
            if st.button("Back to Results", use_container_width=True, type="secondary"):
                st.session_state.screen = "result"
                st.rerun()
        with right:
            if st.button("Assess Another", use_container_width=True, type="primary", key="rec_assess_another"):
                reset_session("profile")
                st.rerun()