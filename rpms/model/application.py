
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Application:
    application_id: int | None = None
    application_code: str = ""
    candidate_id: int = 0
    job_id: int = 0
    applied_at: datetime | None = None
    eligibility_status: str = "PENDING"
    eligibility_reason: str = ""
    application_status: str = "APPLIED"
    source: str = "PORTAL"
    assigned_recruiter_id: int | None = None
    updated_at: datetime | None = None
    candidate_name: str = ""
    job_title: str = ""
    company_name: str = ""
