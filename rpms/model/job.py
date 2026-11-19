
from dataclasses import dataclass
from datetime import date


@dataclass
class Job:
    job_id: int | None = None
    job_code: str = ""
    company_id: int = 0
    job_title: str = ""
    employment_type: str = "FULL_TIME"
    location: str = ""
    openings: int = 1
    min_package_lpa: float | None = None
    max_package_lpa: float | None = None
    min_percentage: float | None = None
    min_passing_year: int | None = None
    max_passing_year: int | None = None
    max_backlogs: int = 0
    experience_min_years: float = 0.0
    qualification_rule: str | None = None
    posted_date: date | None = None
    application_deadline: date | None = None
    status: str = "OPEN"
    created_by: int = 0
    created_at: object | None = None
