
from datetime import date, datetime

from rpms.dao.application_dao import ApplicationDAO
from rpms.dao.candidate_dao import CandidateDAO
from rpms.dao.job_dao import JobDAO
from rpms.model.application import Application


class ApplicationService:

    VALID_STATUSES = {
        "APPLIED",
        "UNDER_REVIEW",
        "ELIGIBILITY_VERIFIED",
        "SHORTLISTED",
        "INTERVIEW_SCHEDULED",
        "INTERVIEWED",
        "SELECTED",
        "REJECTED",
        "OFFERED",
        "JOINED",
        "WITHDRAWN"
    }

    def __init__(self):
        self.application_dao = ApplicationDAO()
        self.candidate_dao = CandidateDAO()
        self.job_dao = JobDAO()

    def get_all_applications(self, search="", status=""):
        status = (status or "").strip().upper()

        if status and status not in self.VALID_STATUSES:
            raise ValueError("Invalid application status")

        return self.application_dao.find_all(search, status)

    def get_application(self, application_id):
        application = self.application_dao.find_by_id(application_id)

        if not application:
            raise ValueError("Application not found")

        return application

    def add_application(self, application):
        if application.candidate_id <= 0:
            raise ValueError("Select a valid candidate")

        if application.job_id <= 0:
            raise ValueError("Select a valid job")

        candidate = self.candidate_dao.find_by_id(
            application.candidate_id
        )

        if not candidate:
            raise ValueError("Candidate not found")

        job = self.job_dao.find_by_id(application.job_id)

        if not job:
            raise ValueError("Job not found")

        if job.status != "OPEN":
            raise ValueError(
                "Applications can only be submitted for OPEN jobs"
            )

        if (
            job.application_deadline
            and job.application_deadline < date.today()
        ):
            raise ValueError("Application deadline has passed")

        if self.application_dao.find_duplicate(
            application.candidate_id,
            application.job_id
        ):
            raise ValueError(
                "This candidate has already applied for this job"
            )

        reasons = []

        if job.min_percentage is not None:
            if (
                candidate.percentage is None
                or float(candidate.percentage) < float(job.min_percentage)
            ):
                reasons.append(
                    f"Minimum percentage required: {job.min_percentage}%"
                )

        if job.min_passing_year is not None:
            if candidate.passing_year < job.min_passing_year:
                reasons.append(
                    f"Passing year must be {job.min_passing_year} or later"
                )

        if job.max_passing_year is not None:
            if candidate.passing_year > job.max_passing_year:
                reasons.append(
                    f"Passing year must be {job.max_passing_year} or earlier"
                )

        if candidate.backlog_count > job.max_backlogs:
            reasons.append(
                f"Maximum allowed backlogs: {job.max_backlogs}"
            )

        if job.qualification_rule:
            allowed = [
                item.strip().lower()
                for item in job.qualification_rule.replace(",", "/").split("/")
                if item.strip()
            ]

            qualification = (
                candidate.qualification or ""
            ).strip().lower()

            if allowed and not any(
                item in qualification for item in allowed
            ):
                reasons.append(
                    "Qualification does not match job requirements"
                )

        application.eligibility_status = (
            "NOT_ELIGIBLE" if reasons else "ELIGIBLE"
        )

        application.eligibility_reason = (
            "; ".join(reasons)
            if reasons
            else "Candidate meets the configured eligibility criteria"
        )

        application.application_code = (
            f"APP-{datetime.now().strftime('%y%m%d%H%M%S')}-"
            f"{application.candidate_id}-{application.job_id}"
        )

        application.application_status = "APPLIED"

        return self.application_dao.save(application)

    def update_status(self, application_id, status):
        status = (status or "").strip().upper()

        if status not in self.VALID_STATUSES:
            raise ValueError("Invalid application status")

        self.get_application(application_id)

        updated = self.application_dao.update_status(
            application_id,
            status
        )

        if not updated:
            raise ValueError("Application status was not updated")

        return application_id
