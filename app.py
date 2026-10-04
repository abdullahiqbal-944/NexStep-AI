import streamlit as st

from agents import NexStepAI
from models import UserProfile


st.set_page_config(
    page_title="NexStep AI",
    page_icon="🧭",
    layout="wide",
)


# -----------------------------
# Session State
# -----------------------------

if "case" not in st.session_state:
    st.session_state.case = None

if "profile" not in st.session_state:
    st.session_state.profile = UserProfile()

if "ai" not in st.session_state:
    st.session_state.ai = None


def get_ai():
    """Create the AI service only when it is actually needed."""
    if st.session_state.ai is None:
        st.session_state.ai = NexStepAI()
    return st.session_state.ai


# -----------------------------
# Styling
# -----------------------------

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


# -----------------------------
# Sidebar
# -----------------------------

st.sidebar.title("🧭 NexStep AI")
st.sidebar.caption("Your intelligent case manager")

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
    "NexStep AI converts complicated goals into "
    "research-backed, personalized next steps."
)


# ============================================================
# Dashboard
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
            "No case created yet. Go to **Define Goal** and describe "
            "what you want to accomplish."
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("AI Agents", "7")

        with col2:
            st.metric("Research", "Web Grounded")

        with col3:
            st.metric("Planning", "Personalized")

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

        st.subheader("🎯 Current Goal")

        st.write(case.goal)

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

            st.subheader("⚠️ Important")

            for warning in case.warnings:
                st.warning(warning)


# ============================================================
# Define Goal
# ============================================================

elif page == "🎯 Define Goal":

    st.title("🎯 Define Your Goal")

    st.write(
        "Describe your goal naturally. NexStep AI will analyze it "
        "and determine what information is required."
    )

    goal = st.text_area(
        "What do you want to accomplish?",
        placeholder=(
            "Example: I want to apply for a fully funded master's "
            "scholarship in Germany."
        ),
        height=160,
    )

    if st.button(
        "🚀 Analyze Goal",
        type="primary",
        use_container_width=True,
    ):

        if not goal.strip():
            st.error("Please enter a goal first.")
        else:

            with st.spinner("Understanding your goal..."):

                try:

                    ai = get_ai()

                    case = ai.understand_goal(
                        goal,
                        st.session_state.profile,
                    )

                    st.session_state.case = case

                    st.success("Goal successfully analyzed!")

                except Exception as e:

                    st.error(f"Error: {e}")

    if st.session_state.case:

        case = st.session_state.case

        st.divider()

        st.subheader("🧠 AI Understanding")

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

        if case.missing_information:

            st.subheader("❓ Missing Information")

            for item in case.missing_information:

                st.write(f"• {item}")


# ============================================================
# Profile
# ============================================================

elif page == "👤 Profile":

    st.title("👤 Your Profile")

    st.write(
        "Your profile helps NexStep AI personalize eligibility "
        "and action plans."
    )

    profile = st.session_state.profile

    col1, col2 = st.columns(2)

    with col1:

        profile.name = st.text_input(
            "Name",
            value=profile.name,
        )

        profile.age = st.number_input(
            "Age",
            min_value=0,
            max_value=100,
            value=profile.age,
        )

        profile.country = st.text_input(
            "Country",
            value=profile.country,
        )

        profile.nationality = st.text_input(
            "Nationality",
            value=profile.nationality,
        )

        profile.education = st.text_input(
            "Education",
            value=profile.education,
        )

    with col2:

        profile.field = st.text_input(
            "Field / Major",
            value=profile.field,
        )

        profile.gpa = st.text_input(
            "GPA / Percentage",
            value=profile.gpa,
        )

        profile.experience = st.text_area(
            "Experience",
            value=profile.experience,
        )

        profile.skills = st.text_area(
            "Skills",
            value=profile.skills,
        )

        profile.deadline = st.text_input(
            "Important Deadline",
            value=profile.deadline,
        )

    if st.button(
        "💾 Save Profile",
        type="primary",
    ):

        st.session_state.profile = profile

        st.success("Profile saved successfully!")


# ============================================================
# Research
# ============================================================

elif page == "🔎 Research":

    st.title("🔎 Research")

    if not st.session_state.case:

        st.warning("Create a goal first.")

    else:

        case = st.session_state.case

        st.write(
            "AI will research requirements, deadlines, documents, "
            "fees and official sources."
        )

        if st.button(
            "🔎 Start Research",
            type="primary",
            use_container_width=True,
        ):

            with st.spinner(
                "Researching official and reliable sources..."
            ):

                try:

                    ai = get_ai()

                    case = ai.research_case(case)

                    st.session_state.case = case

                    st.success("Research completed!")

                except Exception as e:

                    st.error(f"Research error: {e}")

        if case.research:

            st.subheader("📚 Research Findings")

            for item in case.research:

                with st.expander(
                    item.title
                ):

                    st.write(
                        item.summary
                    )

                    if item.category:

                        st.caption(
                            f"Category: {item.category}"
                        )

                    if item.source_url:

                        st.markdown(
                            f"[🔗 Open Source]({item.source_url})"
                        )


# ============================================================
# Eligibility
# ============================================================

elif page == "✅ Eligibility":

    st.title("✅ Eligibility")

    if not st.session_state.case:

        st.warning("Create a goal first.")

    else:

        case = st.session_state.case

        if st.button(
            "✅ Check Eligibility",
            type="primary",
            use_container_width=True,
        ):

            with st.spinner(
                "Checking eligibility..."
            ):

                try:

                    ai = get_ai()

                    case = ai.check_eligibility(
                        case,
                        st.session_state.profile,
                    )

                    st.session_state.case = case

                except Exception as e:

                    st.error(
                        f"Eligibility error: {e}"
                    )

        if case.eligibility_status:

            status = case.eligibility_status

            if status == "ELIGIBLE":

                st.success("🟢 ELIGIBLE")

            elif status == "NOT ELIGIBLE":

                st.error("🔴 NOT ELIGIBLE")

            elif status == "UNCERTAIN":

                st.warning("🟡 UNCERTAIN")

            else:

                st.info(
                    f"Status: {status}"
                )

        if case.eligibility_summary:

            st.subheader("Summary")

            st.write(
                case.eligibility_summary
            )

        if case.eligibility_requirements:

            st.subheader(
                "Requirements"
            )

            for req in case.eligibility_requirements:

                st.write(
                    f"• {req}"
                )


# ============================================================
# Documents
# ============================================================

elif page == "📄 Documents":

    st.title("📄 Documents")

    if not st.session_state.case:

        st.warning("Create a goal first.")

    else:

        case = st.session_state.case

        uploaded_files = st.file_uploader(
            "Upload your documents",
            type=[
                "pdf",
                "docx",
                "txt",
                "png",
                "jpg",
                "jpeg",
            ],
            accept_multiple_files=True,
        )

        if uploaded_files:

            case.uploaded_documents = [
                file.name
                for file in uploaded_files
            ]

            st.success(
                f"{len(uploaded_files)} document(s) uploaded."
            )

        if st.button(
            "📋 Analyze Required Documents",
            type="primary",
            use_container_width=True,
        ):

            with st.spinner(
                "Identifying required documents..."
            ):

                try:

                    ai = get_ai()

                    case = ai.analyze_documents(
                        case
                    )

                    st.session_state.case = case

                except Exception as e:

                    st.error(
                        f"Document error: {e}"
                    )

        if case.document_requirements:

            st.subheader(
                "📋 Document Checklist"
            )

            for doc in case.document_requirements:

                if doc.status == "Available":

                    st.success(
                        f"🟢 {doc.name} — Available"
                    )

                elif doc.status == "Missing":

                    st.error(
                        f"🔴 {doc.name} — Missing"
                    )

                else:

                    st.warning(
                        f"🟡 {doc.name} — "
                        f"{doc.status}"
                    )


# ============================================================
# Verification
# ============================================================

elif page == "🛡️ Verification":

    st.title("🛡️ Verification")

    if not st.session_state.case:

        st.warning("Create a goal first.")

    else:

        case = st.session_state.case

        if st.button(
            "🛡️ Verify Research",
            type="primary",
            use_container_width=True,
        ):

            with st.spinner(
                "Checking important claims..."
            ):

                try:

                    ai = get_ai()

                    case = ai.verify_case(
                        case
                    )

                    st.session_state.case = case

                except Exception as e:

                    st.error(
                        f"Verification error: {e}"
                    )

        if case.verifications:

            for verification in case.verifications:

                with st.expander(
                    verification.claim
                ):

                    st.write(
                        f"**Status:** "
                        f"{verification.status}"
                    )

                    st.write(
                        f"**Confidence:** "
                        f"{verification.confidence}"
                    )

                    st.write(
                        verification.explanation
                    )

                    if verification.source_url:

                        st.markdown(
                            f"[🔗 Source]"
                            f"({verification.source_url})"
                        )


# ============================================================
# Action Plan
# ============================================================

elif page == "🗺️ Action Plan":

    st.title("🗺️ Personalized Action Plan")

    if not st.session_state.case:

        st.warning("Create a goal first.")

    else:

        case = st.session_state.case

        if st.button(
            "🧠 Generate Action Plan",
            type="primary",
            use_container_width=True,
        ):

            with st.spinner(
                "Building your personalized plan..."
            ):

                try:

                    ai = get_ai()

                    case = ai.create_action_plan(
                        case,
                        st.session_state.profile,
                    )

                    st.session_state.case = case

                    st.success(
                        "Action plan created!"
                    )

                except Exception as e:

                    st.error(
                        f"Planning error: {e}"
                    )

        if case.next_step:

            st.markdown(
                f"""
                <div class="next-step">
                    <h2>🚀 YOUR NEXT STEP</h2>
                    <p>{case.next_step}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if case.action_plan:

            st.subheader(
                "📋 Tasks"
            )

            for i, task in enumerate(
                case.action_plan
            ):

                completed = st.checkbox(
                    task.title,
                    value=task.completed,
                    key=f"task_{i}",
                )

                task.completed = completed

                st.caption(
                    f"Priority: {task.priority} | "
                    f"{task.description}"
                )

                if task.why_it_matters:

                    st.caption(
                        f"Why: {task.why_it_matters}"
                    )

                st.divider()

            case.update_progress()

            st.progress(
                case.progress / 100
            )

            st.caption(
                f"Overall progress: "
                f"{case.progress}%"
    )

