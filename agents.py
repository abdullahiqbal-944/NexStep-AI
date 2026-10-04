from models import (
    ActionTask,
    CaseState,
    ResearchItem,
    UserProfile,
)

from gemini_service import GeminiService


class NexStepAI:

    def __init__(self):

        self.llm = GeminiService()

    # =========================================================
    # Helper
    # =========================================================

    @staticmethod
    def _format_additional_information(
        additional_information
    ):

        if not additional_information:
            return "No additional information provided."

        lines = []

        for key, value in additional_information.items():

            if value is None:
                continue

            if isinstance(value, str) and not value.strip():
                continue

            lines.append(
                f"{key}: {value}"
            )

        if not lines:
            return "No additional information provided."

        return "\n".join(lines)

    # =========================================================
    # 1. GOAL UNDERSTANDING AGENT
    # =========================================================

    def understand_goal(
        self,
        goal,
        profile,
    ):

        prompt = f"""
Analyze this user's real-world goal.

USER GOAL:
{goal}

USER PROFILE:
Name: {profile.name}
Age: {profile.age}
Country: {profile.country}
Nationality: {profile.nationality}
Education: {profile.education}
Field: {profile.field}
GPA: {profile.gpa}
Experience: {profile.experience}
Skills: {profile.skills}
Deadline: {profile.deadline}

Return JSON:

{{
    "goal_type": "",
    "location": "",
    "deadline": "",
    "missing_information": [],
    "warnings": []
}}

IMPORTANT:

The "missing_information" array is an INTERNAL
machine-readable field list.

Use stable snake_case identifiers such as:

country_of_citizenship_or_residence
target_intake_or_academic_year
grading_scale_maximum
work_or_research_experience
german_language_proficiency
planned_ielts_test_date

Do NOT put full natural-language questions in this field.

Rules:

- Do not invent user information.
- Identify information that is genuinely necessary.
- Only request information that could affect eligibility,
  research or planning.
- Keep the system generic enough for scholarships,
  admissions, visas, jobs, internships, certifications,
  government services, travel and other real-world goals.
"""

        data = self.llm.generate_json(
            prompt
        )

        case = CaseState(
            goal=goal,
            goal_type=data.get(
                "goal_type",
                ""
            ),
            location=data.get(
                "location",
                ""
            ),
            deadline=data.get(
                "deadline",
                ""
            ),
            missing_information=data.get(
                "missing_information",
                []
            ),
            warnings=data.get(
                "warnings",
                []
            ),
        )

        case.next_step = (
            "Review the additional information needed "
            "to make your case more accurate."
        )

        return case

    # =========================================================
    # 2. RESEARCH AGENT
    # =========================================================

    def research_case(
        self,
        case,
        additional_information=None,
    ):

        additional_information_text = (
            self._format_additional_information(
                additional_information
            )
        )

        prompt = f"""
Research the following real-world case.

GOAL:
{case.goal}

GOAL TYPE:
{case.goal_type}

LOCATION:
{case.location}

DEADLINE:
{case.deadline}

USER'S ADDITIONAL INFORMATION:
{additional_information_text}

Find:

- Eligibility requirements
- Application requirements
- Important deadlines
- Required documents
- Fees
- Application procedure
- Official application link
- Important restrictions
- Important warnings

Return JSON:

{{
    "items": [
        {{
            "title": "",
            "summary": "",
            "category": "",
            "source_url": "",
            "source_type": ""
        }}
    ]
}}

Every important factual item should have a source URL
when possible.

Prioritize official sources.

Do not invent requirements.
"""

        data = self.llm.generate_json(
            prompt,
            use_search=True,
        )

        items = []

        for item in data.get(
            "items",
            []
        ):

            items.append(
                ResearchItem(
                    title=item.get(
                        "title",
                        "Research Finding"
                    ),
                    summary=item.get(
                        "summary",
                        ""
                    ),
                    category=item.get(
                        "category",
                        ""
                    ),
                    source_url=item.get(
                        "source_url",
                        ""
                    ),
                    source_type=item.get(
                        "source_type",
                        "Unknown"
                    ),
                )
            )

        case.research = items

        case.next_step = (
            "Check whether you meet the researched "
            "eligibility requirements."
        )

        return case

    # =========================================================
    # 3. ELIGIBILITY AGENT
    # =========================================================

    def check_eligibility(
        self,
        case,
        profile,
        additional_information=None,
    ):

        research_text = "\n".join(
            [
                f"{item.title}: {item.summary}"
                for item in case.research
            ]
        )

        additional_information_text = (
            self._format_additional_information(
                additional_information
            )
        )

        prompt = f"""
Determine the user's eligibility.

USER PROFILE:
Name: {profile.name}
Age: {profile.age}
Country: {profile.country}
Nationality: {profile.nationality}
Education: {profile.education}
Field: {profile.field}
GPA: {profile.gpa}
Experience: {profile.experience}
Skills: {profile.skills}

ADDITIONAL USER INFORMATION:
{additional_information_text}

CASE:
{case.goal}

RESEARCH:
{research_text}

Return JSON:

{{
    "status": "ELIGIBLE",
    "summary": "",
    "requirements": []
}}

Allowed status values:

ELIGIBLE
NOT ELIGIBLE
UNCERTAIN
NEEDS VERIFICATION

Rules:

- Never assume missing information.
- Use the additional user information when relevant.
- If an important fact is unknown, use UNCERTAIN
  or NEEDS VERIFICATION.
- Explain the reasoning clearly.
"""

        data = self.llm.generate_json(
            prompt
        )

        case.eligibility_status = data.get(
            "status",
            "UNCERTAIN"
        )

        case.eligibility_summary = data.get(
            "summary",
            ""
        )

        case.eligibility_requirements = data.get(
            "requirements",
            []
        )

        case.next_step = (
            "Identify and prepare the documents required "
            "for the application."
        )

        return case

    # =========================================================
    # 4. DOCUMENT AGENT
    # =========================================================

    def analyze_documents(
        self,
        case,
    ):

        research_text = "\n".join(
            [
                f"{item.title}: {item.summary}"
                for item in case.research
            ]
        )

        uploaded = ", ".join(
            case.uploaded_documents
        )

        prompt = f"""
Identify the documents required for this case.

GOAL:
{case.goal}

RESEARCH:
{research_text}

DOCUMENTS THE USER UPLOADED:
{uploaded}

Return JSON:

{{
    "documents": [
        {{
            "name": "",
            "status": "",
            "reason": ""
        }}
    ]
}}

Allowed statuses:

Available
Missing
Optional
Conditionally Required
Needs Verification

Important:

A filename does NOT prove that a document is valid,
complete or authentic.
"""

        data = self.llm.generate_json(
            prompt
        )

        case.document_requirements = (
            data.get(
                "documents",
                []
            )
        )

        case.next_step = (
            "Verify the important requirements and sources."
        )

        return case

    # =========================================================
    # 5. VERIFICATION AGENT
    # =========================================================

    def verify_case(
        self,
        case,
    ):

        research_text = "\n".join(
            [
                f"TITLE: {item.title}\n"
                f"SUMMARY: {item.summary}\n"
                f"SOURCE: {item.source_url}"
                for item in case.research
            ]
        )

        prompt = f"""
Verify the important claims in this research.

CASE:
{case.goal}

RESEARCH:
{research_text}

Return JSON:

{{
    "verifications": [
        {{
            "claim": "",
            "status": "",
            "confidence": 0,
            "explanation": "",
            "source_url": ""
        }}
    ]
}}

Allowed status:

VERIFIED
NOT VERIFIED
UNCERTAIN
CONFLICTING

Confidence must be between 0 and 100.

Prefer official sources.
"""

        data = self.llm.generate_json(
            prompt,
            use_search=True,
        )

        case.verifications = data.get(
            "verifications",
            []
        )

        case.next_step = (
            "Generate a personalized action plan."
        )

        return case

    # =========================================================
    # 6. PLANNING AGENT
    # =========================================================

    def create_action_plan(
        self,
        case,
        profile,
        additional_information=None,
    ):

        research_text = "\n".join(
            [
                f"{item.title}: {item.summary}"
                for item in case.research
            ]
        )

        documents = "\n".join(
            [
                f"{doc.get('name', '')}: "
                f"{doc.get('status', '')}"
                for doc in case.document_requirements
            ]
        )

        additional_information_text = (
            self._format_additional_information(
                additional_information
            )
        )

        prompt = f"""
Create a practical personalized action plan.

GOAL:
{case.goal}

USER PROFILE:
Country: {profile.country}
Education: {profile.education}
Field: {profile.field}
GPA: {profile.gpa}
Experience: {profile.experience}
Skills: {profile.skills}
Deadline: {profile.deadline}

ADDITIONAL USER INFORMATION:
{additional_information_text}

RESEARCH:
{research_text}

DOCUMENTS:
{documents}

ELIGIBILITY:
{case.eligibility_summary}

Return JSON:

{{
    "tasks": [
        {{
            "title": "",
            "description": "",
            "priority": 1,
            "why_it_matters": "",
            "deadline": ""
        }}
    ]
}}

Rules:

- Priority 1 is the most urgent/important.
- Break complicated processes into practical tasks.
- Put prerequisites before dependent tasks.
- Include document preparation.
- Include application submission.
- Include final review.
- Do not create impossible or invented requirements.
"""

        data = self.llm.generate_json(
            prompt
        )

        tasks = []

        for item in data.get(
            "tasks",
            []
        ):

            tasks.append(
                ActionTask(
                    title=item.get(
                        "title",
                        "Complete task"
                    ),
                    description=item.get(
                        "description",
                        ""
                    ),
                    priority=int(
                        item.get(
                            "priority",
                            5
                        )
                    ),
                    why_it_matters=item.get(
                        "why_it_matters",
                        ""
                    ),
                    deadline=item.get(
                        "deadline",
                        ""
                    ),
                )
            )

        tasks.sort(
            key=lambda x: x.priority
        )

        case.action_plan = tasks

        case.update_progress()

        return case
