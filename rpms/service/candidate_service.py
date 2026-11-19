
from rpms.exception.exceptions import CandidateNotFoundError
from rpms.util.validation import (
    is_valid_email,
    is_valid_mobile,
    is_valid_percentage,
    is_valid_backlog_count,
    is_valid_passing_year
)


class CandidateService:

    def __init__(self, candidate_dao):
        self.candidate_dao = candidate_dao

    def _validate_candidate(self, candidate):
        if not candidate.candidate_code.strip():
            raise ValueError("Candidate code is required")

        if not candidate.full_name.strip():
            raise ValueError("Candidate name is required")

        if not is_valid_email(candidate.email):
            raise ValueError("Invalid email")

        if not is_valid_mobile(candidate.mobile):
            raise ValueError("Mobile must contain 10 digits")

        if not is_valid_percentage(candidate.percentage):
            raise ValueError("Percentage must be between 0 and 100")

        if not is_valid_backlog_count(candidate.backlog_count):
            raise ValueError("Backlog count cannot be negative")

        if not is_valid_passing_year(candidate.passing_year):
            raise ValueError("Invalid passing year")

    def add_candidate(self, candidate):
        self._validate_candidate(candidate)

        if self.candidate_dao.find_by_email(candidate.email):
            raise ValueError("Duplicate email")

        if self.candidate_dao.find_by_mobile(candidate.mobile):
            raise ValueError("Duplicate mobile")

        return self.candidate_dao.save(candidate)

    def update_candidate(self, candidate_id, candidate):
        existing = self.get_candidate(candidate_id)

        self._validate_candidate(candidate)

        email_candidate = self.candidate_dao.find_by_email(candidate.email)
        if email_candidate and email_candidate.candidate_id != candidate_id:
            raise ValueError("Email already belongs to another candidate")

        mobile_candidate = self.candidate_dao.find_by_mobile(candidate.mobile)
        if mobile_candidate and mobile_candidate.candidate_id != candidate_id:
            raise ValueError("Mobile already belongs to another candidate")

        candidate.candidate_id = candidate_id
        candidate.profile_status = existing.profile_status
        candidate.placement_status = existing.placement_status

        if not self.candidate_dao.update(candidate):
            raise CandidateNotFoundError(
                f"Candidate ID {candidate_id} not found"
            )

        return candidate_id

    def get_candidate(self, candidate_id):
        candidate = self.candidate_dao.find_by_id(candidate_id)

        if not candidate:
            raise CandidateNotFoundError(
                f"Candidate ID {candidate_id} not found"
            )

        return candidate

    def get_all_candidates(self):
        return self.candidate_dao.find_all()
