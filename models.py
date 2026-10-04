from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class UserProfile:
    name: str = ""
    age: int = 0
    country: str = ""
    nationality: str = ""
    education: str = ""
    field: str = ""
    gpa: str = ""
    experience: str = ""
    skills: str = ""
    deadline: str = ""


@dataclass
class ResearchItem:
    title: str
    summary: str
    category: str = ""
    source_url: str = ""
    source_type: str = "Unknown"


@dataclass
class ActionTask:
    title: str
    description: str
    priority: int = 5
    why_it_matters: str = ""
    deadline: str = ""
    completed: bool = False


@dataclass
class CaseState:

    goal: str = ""

    goal_type: str = ""
    location: str = ""
    deadline: str = ""

    # IMPORTANT:
    # This remains the internal AI field-name list.
    # The UI converts these into human-readable questions.
    missing_information: List[str] = field(
        default_factory=list
    )

    # User answers to the missing-information questions.
    # This is separate from missing_information so the
    # original agent schema is not broken.
    missing_information_answers: Dict[str, Any] = field(
        default_factory=dict
    )

    research: List[ResearchItem] = field(
        default_factory=list
    )

    eligibility_status: str = ""

    eligibility_summary: str = ""

    eligibility_requirements: List[str] = field(
        default_factory=list
    )

    document_requirements: List[dict] = field(
        default_factory=list
    )

    uploaded_documents: List[str] = field(
        default_factory=list
    )

    verifications: List[dict] = field(
        default_factory=list
    )

    action_plan: List[ActionTask] = field(
        default_factory=list
    )

    next_step: str = ""

    progress: int = 0

    warnings: List[str] = field(
        default_factory=list
    )

    def update_progress(self):

        if not self.action_plan:

            self.progress = 0

            self.next_step = (
                "Generate your personalized action plan."
            )

            return

        completed = sum(
            task.completed
            for task in self.action_plan
        )

        self.progress = int(
            completed / len(self.action_plan) * 100
        )

        pending = [
            task
            for task in self.action_plan
            if not task.completed
        ]

        pending.sort(
            key=lambda x: x.priority
        )

        if pending:

            self.next_step = pending[0].title

        else:

            self.next_step = (
                "🎉 All current tasks are complete. "
                "Review your case for any remaining requirements."
            )
