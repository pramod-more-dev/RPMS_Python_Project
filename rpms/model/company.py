
from dataclasses import dataclass


@dataclass
class Company:
    company_id: int | None = None
    company_code: str = ""
    company_name: str = ""
    industry: str = ""
    website: str = ""
    location: str = ""
    company_type: str = ""
    hr_name: str = ""
    hr_email: str = ""
    hr_mobile: str = ""
    status: str = "ACTIVE"
    created_at: object = None
