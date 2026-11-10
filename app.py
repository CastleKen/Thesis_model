import base64
from pathlib import Path

import streamlit as st


st.set_page_config(
    page_title="Digital Financial Literacy Kiosk",
    layout="centered",
    initial_sidebar_state="collapsed",
)


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

.main-card {
    background: var(--card);
    border: 1px solid rgba(42, 26, 14, 0.12);
    border-radius: 18px;
    padding: 1.4rem 1.2rem;
    box-shadow: 0 10px 30px rgba(42, 26, 14, 0.12);
    animation: fadeUp 500ms ease;
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

/* Secondary buttons are intentionally pale/low-emphasis */
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

    div.stButton > button:hover,
    div.stButton > button:active,
    div.stButton > button:focus,
    div.stButton > button:focus-visible,
    div.stFormSubmitButton > button:hover,
    div.stFormSubmitButton > button:active,
    div.stFormSubmitButton > button:focus,
    div.stFormSubmitButton > button:focus-visible {
        transform: none !important;
    }
}

/* Ensure dark text on white/light controls */
[data-testid="stWidgetLabel"] p,
.stCheckbox label span,
.stRadio label span {
    color: var(--ink) !important;
}

.stTextInput input,
.stNumberInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] > div {
    background: #ffffff !important;
    color: var(--ink) !important;
    border: 1px solid rgba(42, 26, 14, 0.25) !important;
}

.stTextInput input::placeholder,
.stNumberInput input::placeholder,
.stTextArea textarea::placeholder {
    color: var(--muted) !important;
    opacity: 1 !important;
}

.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus,
.stSelectbox div[data-baseweb="select"] > div:focus-within {
    color: var(--ink) !important;
    border: 1px solid rgba(212, 98, 26, 0.55) !important;
    box-shadow: 0 0 0 1px rgba(212, 98, 26, 0.3) !important;
}

[data-testid="stAlert"] {
    background: rgba(244, 174, 82, 0.2);
    border: 1px solid rgba(212, 98, 26, 0.35);
    color: var(--ink);
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
    padding: 0.7rem;
}

.apriori-card {
    grid-column: 1 / -1;
    justify-self: center;
    width: min(420px, 100%);
}

.kpi-label {
    font-size: 0.82rem;
    color: var(--muted);
}

.kpi-value {
    font-size: 1.1rem;
    font-weight: 700;
    margin-top: 0.2rem;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 640px) {
    .main-card {
        padding: 1rem 0.8rem;
    }

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


if "screen" not in st.session_state:
    st.session_state.screen = "welcome"

if "profile" not in st.session_state:
    st.session_state.profile = {}

if "answers" not in st.session_state:
    st.session_state.answers = {}

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


def build_recommendations(score: int, answers: dict) -> list[str]:
    tips: list[str] = []

    if score < 55:
        tips.append("Start with a weekly budget plan using the 50/30/20 rule.")
        tips.append("List all debts and begin with either the highest-interest debt or the smallest balance first.")
        tips.append("Set up automatic savings, even a small fixed amount each week.")
    elif score < 75:
        tips.append("Improve consistency: review your budget every Sunday and track your spending categories.")
        tips.append("Build your emergency fund toward at least 3 months of basic expenses.")
        tips.append("Create one SMART financial goal for the next 90 days.")
    else:
        tips.append("Keep your current habits and add a monthly financial review checkpoint.")
        tips.append("Diversify savings into separate buckets: emergency, tuition/career, and long-term goals.")
        tips.append("Mentor peers or family on basic budgeting and responsible spending.")

    if answers.get("expense_tracking") is False:
        tips.append("Track expenses daily using a notebook, spreadsheet, or budgeting app.")

    if answers.get("impulse_buying_frequency", 1) >= 4:
        tips.append("Use a 24-hour waiting rule before non-essential purchases.")

    if answers.get("emergency_fund_months", 0.0) < 3:
        tips.append("Prioritize growing your emergency fund until it covers at least 3 months.")

    if answers.get("debt_amount", 0) > answers.get("monthly_income", 0):
        tips.append("Your debt is higher than your monthly income; pause non-essential spending and create a debt reduction plan.")

    return tips


@st.dialog("How Does It Work?")
def show_how_it_works() -> None:
     st.write("This kiosk follows a simple step-by-step assessment flow:")
     st.markdown(
          """
1. **Welcome Screen**
    You start the assessment and review what it is for.

2. **Participant Information**
    You provide basic details (ID, age, and program).

3. **Financial Behavior Questionnaire**
    You answer questions about budgeting, debt, saving, and spending habits.

4. **Scoring & Interpretation**
    The app computes a **digital financial literacy score** and assigns a literacy band.

5. **Result & Next Action**
    You can assess another participant or reset the kiosk for a new session.
          """
     )
     st.caption("Current version uses UI-side demo scoring and can be connected to your ML models later.")


with st.container():

    st.markdown(
        """
<div class="logo-header">
    <img src="data:image/png;base64,{psu_logo_b64}" alt="PSU Logo"/>
    <img src="data:image/png;base64,{cs_logo_b64}" alt="CS Logo"/>
</div>
        """.format(
            psu_logo_b64=st.session_state.get("psu_logo_b64", ""),
            cs_logo_b64=st.session_state.get("cs_logo_b64", ""),
        ),
        unsafe_allow_html=True,
    )

    if st.session_state.screen == "welcome":
        st.title("Digital Financial Literacy Assessment")
        st.write(
            "A simple kiosk interface for student financial behavior assessment. "
            "Use this as your front-end shell before connecting your model pipeline."
        )

        if st.button("Start Assessment", use_container_width=True, type="primary"):
            st.session_state.screen = "profile"
            st.rerun()

        if st.button("How Does it Work?", use_container_width=True, key="how_it_works_btn", type="secondary"):
            show_how_it_works()

    elif st.session_state.screen == "profile":
        st.header("Basic Information")
        with st.form("profile_form"):
            age = st.number_input("Age", min_value=16, max_value=70, value=21)
            program = st.text_input("Program / Course", placeholder="Ex: BS Information Technology")

            left, right = st.columns(2)
            with left:
                go_back = st.form_submit_button("Back", use_container_width=True)
            with right:
                go_next = st.form_submit_button("Continue", use_container_width=True)

            if go_back:
                st.session_state.screen = "welcome"
                st.rerun()

            if go_next:
                st.session_state.profile = {
                    "age": int(age),
                    "program": program.strip() or "N/A",
                }
                st.session_state.screen = "questionnaire"
                st.rerun()

    elif st.session_state.screen == "questionnaire":
        st.header("Lets Identify Your Finacial Persona!")
        with st.form("questionnaire_form"):
            monthly_income = st.number_input("Monthly allowance or income (PHP)", min_value=0, value=15000, step=500)
            
            budgeting_habit = st.slider("How consistent are you with budgeting?", min_value=1, max_value=5, value=3)
            impulse_buying_frequency = st.slider("How often do you buy things impulsively?", min_value=1, max_value=5, value=3)

            left, right = st.columns(2)
            with left:
                go_back = st.form_submit_button("Back", use_container_width=True)
            with right:
                submit = st.form_submit_button("Generate Result", use_container_width=True)

            if go_back:
                st.session_state.screen = "profile"
                st.rerun()

            if submit:
                # UI-only placeholder output. Replace with real model calls later.
                base_score = 50
                base_score += (budgeting_habit - 3) * 6
                base_score -= (impulse_buying_frequency - 3) * 5

                score = max(0, min(100, base_score))
                if score >= 75:
                    band = "High"
                    segment = "Stable"
                elif score >= 55:
                    band = "Moderate"
                    segment = "Developing"
                else:
                    band = "Needs Support"
                    segment = "At-Risk"

                st.session_state.answers = {
                    "monthly_income": monthly_income,
                    "budgeting_habit": budgeting_habit,
                    "impulse_buying_frequency": impulse_buying_frequency,
                }

                st.session_state.result = {
                    "score": score,
                    "band": band,
                    "segment": segment,
                    "logistic_prob": min(99, max(1, int(score))),
                    "rules_triggered": "2 patterns matched" if score >= 60 else "1 pattern matched",
                }
                st.session_state.screen = "result"
                st.rerun()

    elif st.session_state.screen == "result":
        profile = st.session_state.profile
        result = st.session_state.result
        literacy_level = "High" if result["score"] >= 75 else "Low"

        st.header("Assessment Result")
        st.subheader(f"Digital Financial Literacy: {literacy_level}")

        st.markdown(
            f"""
<div class="kpi-row">
  <div class="kpi-card"><div class="kpi-label">Digital Financial Literacy Score</div><div class="kpi-value">{result['score']}/100</div></div>
  <div class="kpi-card"><div class="kpi-label">Financial Behavior Cluster</div><div class="kpi-value">{result['segment']}</div></div>
    <div class="kpi-card apriori-card"><div class="kpi-label">Apriori Analysis</div><div class="kpi-value">{result['rules_triggered']}</div></div>
</div>
""",
            unsafe_allow_html=True,
        )

        st.write("### Explanation:")
        st.write(
            "The digital financial literacy level is determined from your current score and financial behavior inputs. "
            "A higher score indicates stronger budgeting and saving habits, while a lower score indicates areas that need support."
        )
        st.write(
            "The Financial Behavior Cluster and Apriori Analysis summarize your spending and planning patterns, "
            "which are used to identify practical next steps in the recommendations page."
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("View Suggestions", use_container_width=True, type="secondary"):
                st.session_state.screen = "recommendations"
                st.rerun()
        with col2:
            if st.button("Assess Another", use_container_width=True, type="primary"):
                st.session_state.answers = {}
                st.session_state.result = None
                st.session_state.screen = "profile"
                st.rerun()

    elif st.session_state.screen == "recommendations":
        result = st.session_state.result
        answers = st.session_state.answers

        st.header("Recommendations & Next Steps")
        st.write(f"Based on your score (**{result['score']}/100**), here are practical suggestions:")

        recommendations = build_recommendations(result["score"], answers)
        for i, tip in enumerate(recommendations, start=1):
            st.write(f"{i}. {tip}")

        st.write("### Quick Habit Plan")
        st.write("- Daily: Record every expense.")
        st.write("- Weekly: Review budget and identify one spending cut.")
        st.write("- Monthly: Check debt, savings, and progress on your financial goal.")

        left, right = st.columns(2)
        with left:
            if st.button("Back to Results", use_container_width=True, type="secondary"):
                st.session_state.screen = "result"
                st.rerun()
        with right:
            if st.button("Assess Another", use_container_width=True, type="primary", key="rec_assess_another"):
                st.session_state.answers = {}
                st.session_state.result = None
                st.session_state.screen = "profile"
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
