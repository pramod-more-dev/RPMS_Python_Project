
from rpms.model.job import Job


class JobService:

    VALID_STATUSES = {"DRAFT", "OPEN", "CLOSED", "CANCELLED"}
    VALID_EMPLOYMENT_TYPES = {
        "FULL_TIME", "PART_TIME", "CONTRACT", "INTERNSHIP"
    }

    def __init__(self, job_dao):
        self.job_dao = job_dao

    def get_all_jobs(self, search="", status=""):
        if status and status not in self.VALID_STATUSES:
            raise ValueError("Invalid job status")

        return self.job_dao.find_all(search, status)

    def get_job(self, job_id):
        job = self.job_dao.find_by_id(job_id)

        if not job:
            raise ValueError("Job not found")

        return job

    def add_job(self, job):
        self._validate(job)

        if not job.created_by:
            raise ValueError("Created by user ID is required")

        return self.job_dao.save(job)

    def update_job(self, job_id, job):
        existing_job = self.get_job(job_id)

        # Preserve the original creator during job editing.
        job.created_by = existing_job.created_by

        self._validate(job)

        if not self.job_dao.update(job_id, job):
            raise ValueError("Job update failed")

        return job_id

    def _validate(self, job):
        if not job.job_code:
            raise ValueError("Job code is required")

        if len(job.job_code) > 40:
            raise ValueError("Job code cannot exceed 40 characters")

        if not job.company_id or job.company_id < 1:
            raise ValueError("Valid company is required")

        if not job.job_title:
            raise ValueError("Job title is required")

        if len(job.job_title) > 150:
            raise ValueError("Job title cannot exceed 150 characters")

        if not job.location:
            raise ValueError("Job location is required")

        if len(job.location) > 120:
            raise ValueError("Location cannot exceed 120 characters")

        if job.employment_type not in self.VALID_EMPLOYMENT_TYPES:
            raise ValueError("Invalid employment type")

        if job.status not in self.VALID_STATUSES:
            raise ValueError("Invalid job status")

        if job.openings <= 0:
            raise ValueError("Openings must be greater than zero")

        if job.max_backlogs < 0:
            raise ValueError("Maximum backlogs cannot be negative")

        if job.experience_min_years < 0:
            raise ValueError("Experience cannot be negative")

        if job.min_percentage is not None:
            if not 0 <= job.min_percentage <= 100:
                raise ValueError(
                    "Minimum percentage must be between 0 and 100"
                )

        if (
            job.min_package_lpa is not None
            and job.max_package_lpa is not None
            and job.min_package_lpa > job.max_package_lpa
        ):
            raise ValueError(
                "Minimum package cannot exceed maximum package"
            )

        if (
            job.min_passing_year is not None
            and job.max_passing_year is not None
            and job.min_passing_year > job.max_passing_year
        ):
            raise ValueError(
                "Minimum passing year cannot exceed maximum passing year"
            )

        if not job.posted_date or not job.application_deadline:
            raise ValueError(
                "Posted date and application deadline are required"
            )

        if job.application_deadline < job.posted_date:
            raise ValueError(
                "Application deadline cannot be before posted date"
            )

        if not job.created_by or job.created_by < 1:
            raise ValueError("Valid creator user ID is required")
