from dataclasses import dataclass


@dataclass
class Interview:
    interview_id: int | None = None
    application_id: int = 0
    round_number: int = 1
    round_type: str = ""
    scheduled_date: str = ""
    scheduled_time: str | None = None
    mode: str = "ONLINE"
    interviewer_name: str | None = None
    meeting_or_location: str | None = None
    status: str = "SCHEDULED"


@dataclass
class InterviewFeedback:
    feedback_id: int | None = None
    interview_id: int = 0
    technical_rating: float = 0
    communication_rating: float = 0
    problem_solving_rating: float = 0
    overall_rating: float = 0
    recommendation: str = ""
    remarks: str = ""
    submitted_by: int = 1