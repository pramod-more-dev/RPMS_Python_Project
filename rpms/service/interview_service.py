from datetime import date, time

from rpms.dao.interview_dao import InterviewDAO
from rpms.model.interview import Interview, InterviewFeedback


class InterviewService:

    VALID_MODES = {"ONLINE", "OFFLINE", "TELEPHONIC"}

    VALID_STATUSES = {
        "SCHEDULED",
        "COMPLETED",
        "RESCHEDULED",
        "CANCELLED",
        "NO_SHOW"
    }

    def __init__(self, interview_dao=None):
        self.interview_dao = interview_dao or InterviewDAO()

    def get_all_interviews(self, search="", status="", round_type=""):
        if status and status not in self.VALID_STATUSES:
            raise ValueError("Invalid interview status")

        return self.interview_dao.get_all(
            search.strip(),
            status,
            round_type.strip()
        )

    def get_interview(self, interview_id):
        interview = self.interview_dao.get_by_id(interview_id)

        if not interview:
            raise ValueError("Interview not found")

        return interview

    def schedule_interview(self, data):
        try:
            application_id = int(data.get("application_id") or 0)
            round_number = int(data.get("round_number") or 0)
            round_type = str(data.get("round_type") or "").strip()
            scheduled_date = date.fromisoformat(
                str(data.get("scheduled_date") or "")
            )

            scheduled_time = data.get("scheduled_time") or None
            if scheduled_time:
                time.fromisoformat(str(scheduled_time))

            mode = str(data.get("mode") or "").strip().upper()
            status = str(data.get("status") or "SCHEDULED").strip().upper()

        except (TypeError, ValueError):
            raise ValueError("Please enter valid interview details")

        if application_id <= 0:
            raise ValueError("Valid Application ID is required")

        if round_number <= 0:
            raise ValueError("Round number must be greater than zero")

        if not round_type or len(round_type) > 50:
            raise ValueError("Valid round type is required (maximum 50 characters)")

        if mode not in self.VALID_MODES:
            raise ValueError("Mode must be ONLINE, OFFLINE or TELEPHONIC")

        if status not in self.VALID_STATUSES:
            raise ValueError("Invalid interview status")

        interviewer_name = str(
            data.get("interviewer_name") or ""
        ).strip() or None

        meeting_or_location = str(
            data.get("meeting_or_location") or ""
        ).strip() or None

        if interviewer_name and len(interviewer_name) > 120:
            raise ValueError("Interviewer name cannot exceed 120 characters")

        if meeting_or_location and len(meeting_or_location) > 255:
            raise ValueError("Meeting details cannot exceed 255 characters")

        interview = Interview(
            application_id=application_id,
            round_number=round_number,
            round_type=round_type,
            scheduled_date=scheduled_date.isoformat(),
            scheduled_time=str(scheduled_time) if scheduled_time else None,
            mode=mode,
            interviewer_name=interviewer_name,
            meeting_or_location=meeting_or_location,
            status=status
        )

        return self.interview_dao.create(interview)

    def update_status(self, interview_id, status):
        status = str(status or "").strip().upper()

        if status not in self.VALID_STATUSES:
            raise ValueError("Invalid interview status")

        if not self.interview_dao.get_by_id(interview_id):
            raise ValueError("Interview not found")

        self.interview_dao.update_status(interview_id, status)
        return interview_id

    def get_feedback(self, interview_id):
        if not self.interview_dao.get_by_id(interview_id):
            raise ValueError("Interview not found")

        return self.interview_dao.get_feedback(interview_id)

    def save_feedback(self, interview_id, data):
        if not self.interview_dao.get_by_id(interview_id):
            raise ValueError("Interview not found")

        try:
            technical = float(data.get("technical_rating"))
            communication = float(data.get("communication_rating"))
            problem_solving = float(data.get("problem_solving_rating"))
            overall = float(data.get("overall_rating"))
            submitted_by = int(data.get("submitted_by") or 1)
        except (TypeError, ValueError):
            raise ValueError("Enter valid ratings and submitted-by user ID")

        ratings = [technical, communication, problem_solving, overall]

        if any(rating < 0 or rating > 10 for rating in ratings):
            raise ValueError("All ratings must be between 0 and 10")

        if submitted_by <= 0:
            raise ValueError("Valid submitted-by user ID is required")

        recommendation = str(
            data.get("recommendation") or ""
        ).strip().upper()

        if not recommendation:
            raise ValueError("Recommendation is required")

        if len(recommendation) > 30:
            raise ValueError("Recommendation cannot exceed 30 characters")

        remarks = str(data.get("remarks") or "").strip()

        feedback = InterviewFeedback(
            interview_id=interview_id,
            technical_rating=technical,
            communication_rating=communication,
            problem_solving_rating=problem_solving,
            overall_rating=overall,
            recommendation=recommendation,
            remarks=remarks,
            submitted_by=submitted_by
        )

        return self.interview_dao.save_feedback(feedback)