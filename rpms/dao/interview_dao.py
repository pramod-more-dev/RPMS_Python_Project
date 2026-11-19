
from rpms.util.db_connection import get_connection


class InterviewDAO:

    def serialize_time(self, record):
        if record and record.get("scheduled_time") is not None:
            value = record["scheduled_time"]

            if hasattr(value, "total_seconds"):
                total_seconds = int(value.total_seconds())
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60

                record["scheduled_time"] = (
                    f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                )
            else:
                record["scheduled_time"] = str(value)

        return record

    def get_all(self, search="", status="", round_type=""):
        connection = get_connection()

        try:
            cursor = connection.cursor(dictionary=True)

            query = """
                SELECT
                    i.interview_id,
                    i.application_id,
                    i.round_number,
                    i.round_type,
                    i.scheduled_date,
                    i.scheduled_time,
                    i.mode,
                    i.interviewer_name,
                    i.meeting_or_location,
                    i.status,
                    i.created_at,
                    a.application_code,
                    c.full_name AS candidate_name,
                    c.email AS candidate_email,
                    j.job_title,
                    co.company_name,
                    f.feedback_id,
                    f.technical_rating,
                    f.communication_rating,
                    f.problem_solving_rating,
                    f.overall_rating,
                    f.recommendation,
                    f.remarks
                FROM interview_rounds i
                INNER JOIN applications a
                    ON i.application_id = a.application_id
                INNER JOIN candidates c
                    ON a.candidate_id = c.candidate_id
                INNER JOIN jobs j
                    ON a.job_id = j.job_id
                INNER JOIN companies co
                    ON j.company_id = co.company_id
                LEFT JOIN interview_feedback f
                    ON i.interview_id = f.interview_id
                WHERE 1 = 1
            """

            values = []

            if search:
                query += """
                    AND (
                        c.full_name LIKE %s
                        OR j.job_title LIKE %s
                        OR co.company_name LIKE %s
                        OR a.application_code LIKE %s
                    )
                """
                term = f"%{search}%"
                values.extend([term, term, term, term])

            if status:
                query += " AND i.status = %s"
                values.append(status)

            if round_type:
                query += " AND i.round_type = %s"
                values.append(round_type)

            query += """
                ORDER BY i.scheduled_date DESC,
                         i.scheduled_time DESC,
                         i.interview_id DESC
            """

            cursor.execute(query, tuple(values))
            records = cursor.fetchall()

            return [
                self.serialize_time(record)
                for record in records
            ]

        finally:
            cursor.close()
            connection.close()

    def get_by_id(self, interview_id):
        connection = get_connection()

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute("""
                SELECT
                    i.*,
                    a.application_code,
                    c.full_name AS candidate_name,
                    c.email AS candidate_email,
                    j.job_title,
                    co.company_name,
                    f.feedback_id,
                    f.technical_rating,
                    f.communication_rating,
                    f.problem_solving_rating,
                    f.overall_rating,
                    f.recommendation,
                    f.remarks,
                    f.submitted_by,
                    f.submitted_at
                FROM interview_rounds i
                INNER JOIN applications a
                    ON i.application_id = a.application_id
                INNER JOIN candidates c
                    ON a.candidate_id = c.candidate_id
                INNER JOIN jobs j
                    ON a.job_id = j.job_id
                INNER JOIN companies co
                    ON j.company_id = co.company_id
                LEFT JOIN interview_feedback f
                    ON i.interview_id = f.interview_id
                WHERE i.interview_id = %s
            """, (interview_id,))

            record = cursor.fetchone()
            return self.serialize_time(record)

        finally:
            cursor.close()
            connection.close()

    def create(self, interview):
        connection = get_connection()

        try:
            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO interview_rounds (
                    application_id,
                    round_number,
                    round_type,
                    scheduled_date,
                    scheduled_time,
                    mode,
                    interviewer_name,
                    meeting_or_location,
                    status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                interview.application_id,
                interview.round_number,
                interview.round_type,
                interview.scheduled_date,
                interview.scheduled_time,
                interview.mode,
                interview.interviewer_name,
                interview.meeting_or_location,
                interview.status
            ))

            connection.commit()
            return cursor.lastrowid

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def update_status(self, interview_id, status):
        connection = get_connection()

        try:
            cursor = connection.cursor()

            cursor.execute("""
                UPDATE interview_rounds
                SET status = %s
                WHERE interview_id = %s
            """, (status, interview_id))

            connection.commit()
            return cursor.rowcount

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()

    def get_feedback(self, interview_id):
        connection = get_connection()

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute("""
                SELECT *
                FROM interview_feedback
                WHERE interview_id = %s
                ORDER BY feedback_id DESC
                LIMIT 1
            """, (interview_id,))

            return cursor.fetchone()

        finally:
            cursor.close()
            connection.close()

    def save_feedback(self, feedback):
        connection = get_connection()

        try:
            cursor = connection.cursor(dictionary=True)

            cursor.execute("""
                SELECT feedback_id
                FROM interview_feedback
                WHERE interview_id = %s
                ORDER BY feedback_id DESC
                LIMIT 1
            """, (feedback.interview_id,))

            existing = cursor.fetchone()

            values = (
                feedback.technical_rating,
                feedback.communication_rating,
                feedback.problem_solving_rating,
                feedback.overall_rating,
                feedback.recommendation,
                feedback.remarks,
                feedback.submitted_by
            )

            if existing:
                cursor.execute("""
                    UPDATE interview_feedback
                    SET technical_rating = %s,
                        communication_rating = %s,
                        problem_solving_rating = %s,
                        overall_rating = %s,
                        recommendation = %s,
                        remarks = %s,
                        submitted_by = %s
                    WHERE feedback_id = %s
                """, values + (existing["feedback_id"],))

                feedback_id = existing["feedback_id"]

            else:
                cursor.execute("""
                    INSERT INTO interview_feedback (
                        interview_id,
                        technical_rating,
                        communication_rating,
                        problem_solving_rating,
                        overall_rating,
                        recommendation,
                        remarks,
                        submitted_by
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    feedback.interview_id,
                    feedback.technical_rating,
                    feedback.communication_rating,
                    feedback.problem_solving_rating,
                    feedback.overall_rating,
                    feedback.recommendation,
                    feedback.remarks,
                    feedback.submitted_by
                ))

                feedback_id = cursor.lastrowid

            connection.commit()
            return feedback_id

        except Exception:
            connection.rollback()
            raise

        finally:
            cursor.close()
            connection.close()
