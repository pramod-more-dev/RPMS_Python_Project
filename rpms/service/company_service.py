
from rpms.model.company import Company


class CompanyService:

    def __init__(self, company_dao):
        self.company_dao = company_dao

    def _validate(self, company):
        if not company.company_code:
            raise ValueError("Company code is required")

        if not company.company_name:
            raise ValueError("Company name is required")

        if len(company.company_code) > 30:
            raise ValueError("Company code cannot exceed 30 characters")

        if len(company.company_name) > 180:
            raise ValueError("Company name cannot exceed 180 characters")

        if company.status not in ("ACTIVE", "INACTIVE"):
            raise ValueError("Status must be ACTIVE or INACTIVE")

        if company.hr_email:
            if "@" not in company.hr_email or "." not in company.hr_email:
                raise ValueError("Invalid HR email address")

        if company.hr_mobile:
            if not company.hr_mobile.isdigit() or not 7 <= len(company.hr_mobile) <= 15:
                raise ValueError("Enter a valid HR mobile number")

    def add_company(self, company):
        self._validate(company)

        if self.company_dao.find_by_code(company.company_code):
            raise ValueError("Company code already exists")

        return self.company_dao.save(company)

    def update_company(self, company_id, company):
        existing = self.get_company(company_id)
        self._validate(company)

        duplicate = self.company_dao.find_by_code(company.company_code)

        if duplicate and duplicate.company_id != company_id:
            raise ValueError("Company code already exists")

        company.company_id = company_id

        if not self.company_dao.update(company):
            raise ValueError("Company update failed")

        return company_id

    def get_company(self, company_id):
        company = self.company_dao.find_by_id(company_id)

        if not company:
            raise ValueError(f"Company ID {company_id} not found")

        return company

    def get_all_companies(self):
        return self.company_dao.find_all()
