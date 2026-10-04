import streamlit as st

from agents import NexStepAI
from models import UserProfile


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="NexStep AI",
    page_icon="🧭",
    layout="wide",
)


# ============================================================
# SESSION STATE
# ============================================================

if "case" not in st.session_state:
    st.session_state.case = None

if "profile" not in st.session_state:
    st.session_state.profile = UserProfile()

if "ai" not in st.session_state:
    st.session_state.ai = None

# Important:
# User answers survive Streamlit reruns.
if "missing_information_answers" not in st.session_state:
    st.session_state.missing_information_answers = {}

if "missing_information_submitted" not in st.session_state:
    st.session_state.missing_information_submitted = False


# ============================================================
# AI INITIALIZATION
# ============================================================

def get_ai():

    if st.session_state.ai is None:

        st.session_state.ai = NexStepAI()

    return st.session_state.ai


# ============================================================
# MISSING INFORMATION FORMATTER
# ============================================================

# Explicit professional questions for important fields.
MISSING_INFO_QUESTIONS = {

    "country_of_citizenship_or_residence":
        "What is your country of citizenship or current residence?",

    "target_intake_or_academic_year":
        "Which intake or academic year are you targeting?",

    "grading_scale_maximum":
        "What is the maximum value of your grading scale? "
        "(e.g., 4.0, 5.0, 10.0 or 100)",

    "work_or_research_experience":
        "Do you have any relevant work or research experience?",

    "german_language_proficiency":
        "What is your German language proficiency?",

    "planned_ielts_test_date":
        "When do you plan to take the IELTS test?",

    "target_degree_level":
        "What degree level are you targeting?",

    "previous_education":
        "What is your previous education?",

    "available_budget":
        "What is your available budget?",

    "financial_proof_available":
        "Do you have financial proof available?",

    "english_language_proficiency":
        "What is your English language proficiency?",

    "ielts_score":
        "What is your IELTS score?",

    "toefl_score":
        "What is your TOEFL score?",

    "years_of_experience":
        "How many years of relevant experience do you have?",

    "current_occupation":
        "What is your current occupation?",

    "target_country":
        "Which country are you targeting?",

    "target_university":
        "Which university are you targeting?",

    "target_program":
        "Which program or course are you targeting?",

    "preferred_start_date":
        "When would you like to start?",

    "travel_purpose":
        "What is the main purpose of your travel?",

    "visa_type":
        "Which type of visa are you planning to apply for?",

    "employment_status":
        "What is your current employment status?",

    "relevant_certification":
        "Do you currently hold any relevant certifications?",
}


def format_missing_field(field_name):
    """
    Convert an internal schema key into a professional
    human-readable question.

    The internal key is NEVER shown directly.
    """

    # Normalize accidental whitespace.
    key = str(field_name).strip()

    # Use an explicit professional question when available.
    if key in MISSING_INFO_QUESTIONS:

        return MISSING_INFO_QUESTIONS[key]

    # --------------------------------------------------------
    # Generic fallback
    # --------------------------------------------------------

    # Convert snake_case / kebab-case to words.
    words = key.replace(
        "_",
        " "
    ).replace(
        "-",
        " "
    )

    # Remove excessive whitespace.
    words = " ".join(
        words.split()
    )

    # Professional title case fallback.
    words = words.strip().title()

    if not words:

        return "Please provide the required information."

    return words


def get_field_type(field_name):
    """
    Determine the most appropriate Streamlit widget.
    This is only presentation logic and does not affect
    the agent schema.
    """

    key = str(field_name).lower()

    if (
        "date" in key
        or "deadline" in key
    ):

        return "date"

    if (
        "proficiency" in key
        or key in {
            "german_language_proficiency",
            "english_language_proficiency",
        }
    ):

        return "select_proficiency"

    if (
        "available" in key
        or key.endswith("_required")
        or key.startswith("has_")
        or key.startswith("have_")
    ):

        return "yes_no"

    if (
        "experience" in key
        or "description" in key
        or "background" in key
        or "statement" in key
    ):

        return "textarea"

    return "text"


def render_missing_information_form(case):
    """
    Render a professional interactive form for missing information.

    Raw internal schema names are never rendered.
    """

    missing_fields = case.missing_information

    # --------------------------------------------------------
    # No missing information
    # --------------------------------------------------------

    if not missing_fields:

        st.success(
            "✅ No additional information required.\n\n"
            "Your goal is ready for research and planning."
        )

        return False

    st.markdown(
        "### ❓ A Few Details Needed"
    )

    st.write(
        "To create a more accurate eligibility assessment, "
        "research result, and personalized action plan, "
        "please provide the following information:"
    )

    # --------------------------------------------------------
    # Existing answers
    # --------------------------------------------------------

    answers = st.session_state.missing_information_answers

    # --------------------------------------------------------
    # Form
    # --------------------------------------------------------

    with st.form(
        "missing_information_form",
        clear_on_submit=False,
    ):

        for index, field_name in enumerate(
            missing_fields,
            start=1,
        ):

            question = format_missing_field(
                field_name
            )

            field_type = get_field_type(
                field_name
            )

            # Stable Streamlit key.
            # The internal field name is used internally
            # as a widget key but NEVER displayed.
            widget_key = (
                f"missing_info_{field_name}"
            )

            existing_value = answers.get(
                field_name,
                ""
            )

            st.markdown(
                f"**{index}. {question}**"
            )

            # ------------------------------------------------
            # Date
            # ------------------------------------------------

            if field_type == "date":

                value = st.date_input(
                    question,
                    value=None,
                    key=widget_key,
                    label_visibility="collapsed",
                )

                if value is not None:

                    answers[field_name] = (
                        value.isoformat()
                    )

            # ------------------------------------------------
            # Proficiency
            # ------------------------------------------------

            elif field_type == "select_proficiency":

                options = [
                    "Not applicable",
                    "Beginner",
                    "Elementary",
                    "Intermediate",
                    "Upper-intermediate",
                    "Advanced",
                    "Fluent",
                    "Native",
                    "Not sure",
                ]

                default_index = 0

                if existing_value in options:

                    default_index = options.index(
                        existing_value
                    )

                value = st.selectbox(
                    question,
                    options,
                    index=default_index,
                    key=widget_key,
                    label_visibility="collapsed",
                )

                answers[field_name] = value

            # ------------------------------------------------
            # Yes / No
            # ------------------------------------------------

            elif field_type == "yes_no":

                options = [
                    "Please select",
                    "Yes",
                    "No",
                    "Not sure",
                ]

                default_index = 0

                if existing_value in options:

                    default_index = options.index(
                        existing_value
                    )

                value = st.selectbox(
                    question,
                    options,
                    index=default_index,
                    key=widget_key,
                    label_visibility="collapsed",
                )

                if value != "Please select":

                    answers[field_name] = value

            # ------------------------------------------------
            # Text area
            # ------------------------------------------------

            elif field_type == "textarea":

                value = st.text_area(
                    question,
                    value=str(
                        existing_value
                    ),
                    key=widget_key,
                    label_visibility="collapsed",
                )

                answers[field_name] = value

            # ------------------------------------------------
            # Default text input
            # ------------------------------------------------

            else:

                value = st.text_input(
                    question,
                    value=str(
                        existing_value
                    ),
                    key=widget_key,
                    label_visibility="collapsed",
                )

                answers[field_name] = value

            st.write("")

        submitted = st.form_submit_button(
            "➡️ Continue",
            type="primary",
            use_container_width=True,
        )

    # --------------------------------------------------------
    # Continue button
    # --------------------------------------------------------

    if submitted:

        # Store a clean copy in session state.
        st.session_state.missing_information_answers = {
            key: value
            for key, value in answers.items()
            if value is not None
            and str(value).strip() != ""
        }

        st.session_state.missing_information_submitted = True

        # Save answers in case state too.
        case.missing_information_answers = (
            st.session_state.missing_information_answers
        )

        st.session_state.case = case

        return True

    return False


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 18px;
        color: #9aa4b2;
        margin-bottom: 25px;
    }

    .next-step {
        padding: 20px;
        border-radius: 14px;
        border: 1px solid #4f46e5;
        background: rgba(79, 70, 229, 0.12);
        margin: 15px 0;
    }

    .status-box {
        padding: 15px;
        border-radius: 12px;
        background: rgba(100, 100, 100, 0.12);
        margin: 10px 0;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🧭 NexStep AI")

st.sidebar.caption(
    "Your intelligent case manager"
)

page = st.sidebar.radio(
    "Navigate",
    [
        "🏠 Dashboard",
        "🎯 Define Goal",
        "👤 Profile",
        "🔎 Research",
        "✅ Eligibility",
        "📄 Documents",
        "🛡️ Verification",
        "🗺️ Action Plan",
    ],
)

st.sidebar.divider()

st.sidebar.info(
    "NexStep AI converts complicated real-world goals "
    "into research-backed personalized next steps."
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    st.markdown(
        '<div class="main-title">🧭 NexStep AI</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="subtitle">'
        "Turn a real-world goal into a clear action plan."
        "</div>",
        unsafe_allow_html=True,
    )

    if not st.session_state.case:

        st.info(
            "No case created yet. Go to **Define Goal** "
            "and describe what you want to accomplish."
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "AI Agents",
                "7"
            )

        with col2:
            st.metric(
                "Research",
                "Web Grounded"
            )

        with col3:
            st.metric(
                "Planning",
                "Personalized"
            )

    else:

        case = st.session_state.case

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Progress",
                f"{case.progress}%"
            )

        with col2:

            st.metric(
                "Tasks",
                len(case.action_plan)
            )

        with col3:

            st.metric(
                "Warnings",
                len(case.warnings)
            )

        st.subheader(
            "🎯 Current Goal"
        )

        st.write(
            case.goal
        )

        if case.next_step:

            st.markdown(
                f"""
                <div class="next-step">
                    <h3>🚀 NEXT STEP</h3>
                    <strong>{case.next_step}</strong>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if case.warnings:

            st.subheader(
                "⚠️ Important"
            )

            for warning in case.warnings:

                st.warning(
                    warning
                )


# ============================================================
# DEFINE GOAL
# ============================================================

elif page == "🎯 Define Goal":

    st.title(
        "🎯 Define Your Goal"
    )

    st.write(
        "Describe your goal naturally. NexStep AI will "
        "understand it and identify any information needed "
        "before research begins."
    )

    goal = st.text_area(
        "What do you want to accomplish?",
        placeholder=(
            "Example: I want to apply for a fully funded "
            "master's scholarship in Germany."
        ),
        height=160,
    )

    if st.button(
        "🚀 Analyze Goal",
        type="primary",
        use_container_width=True,
    ):

        if not goal.strip():

            st.error(
                "Please enter a goal first."
            )

        else:

            with st.spinner(
                "Understanding your goal..."
            ):

                try:

                    ai = get_ai()

                    case = ai.understand_goal(
                        goal,
                        st.session_state.profile,
                    )

                    st.session_state.case = case

                    # Reset answers for a new goal.
                    st.session_state.missing_information_answers = {}

                    st.session_state.missing_information_submitted = False

                    st.success(
                        "Goal successfully analyzed!"
                    )

                except Exception as e:

                    st.error(
                        f"Error: {e}"
                    )

    # --------------------------------------------------------
    # AI Understanding
    # --------------------------------------------------------

    if st.session_state.case:

        case = st.session_state.case

        st.divider()

        st.subheader(
            "🧠 AI Understanding"
        )

        if case.goal_type:

            st.write(
                f"**Goal Type:** {case.goal_type}"
            )

        if case.location:

            st.write(
                f"**Location:** {case.location}"
            )

        if case.deadline:

            st.write(
                f"**Deadline:** {case.deadline}"
            )

        # ----------------------------------------------------
        # Missing Information
        # ----------------------------------------------------

        st.divider()

        answers_submitted = (
            st.session_state.missing_information_submitted
        )

        if not answers_submitted:

            form_submitted = (
                render_missing_information_form(
                    case
                )
            )

            # ------------------------------------------------
            # Immediately continue the workflow
            # after user submits answers.
            # ------------------------------------------------

            if form_submitted:

                with st.spinner(
                    "Updating your case with the information you provided..."
                ):

                    try:

                        ai = get_ai()

                        additional_info = (
                            st.session_state
                            .missing_information_answers
                        )

                        # Research now receives the completed
                        # information.
                        case = ai.research_case(
                            case,
                            additional_info,
                        )

                        # Eligibility also receives it.
                        case = ai.check_eligibility(
                            case,
                            st.session_state.profile,
                            additional_info,
                        )

                        case.missing_information_answers = (
                            additional_info
                        )

                        st.session_state.case = case

                        st.session_state.missing_information_submitted = True

                        st.success(
                            "✅ Information saved. "
                            "Research and eligibility analysis "
                            "have been updated."
                        )

                    except Exception as e:

                        st.error(
                            f"Unable to continue processing: {e}"
                        )

        else:

            st.success(
                "✅ Additional information saved."
            )

            st.info(
                "Your answers have been passed to the "
                "research and eligibility agents."
            )

            if case.research:

                st.write(
                    "You can now continue from the "
                    "**Research** or **Eligibility** se
