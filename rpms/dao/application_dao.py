
from rpms.util.db_connection import get_connection


class ApplicationDAO:

    def find_all(self, search="", status=""):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)

            query = """
                SELECT a.*,
                       c.full_name AS candidate_name,
                       j.job_title,
                       co.company_name
                FROM applications a
                JOIN candidates c ON a.candidate_id = c.candidate_id
                JOIN jobs j ON a.job_id = j.job_id
                JOIN companies co ON j.company_id = co.company_id
                WHERE 1=1
            """
            values = []

            if search:
                query += """
                    AND (
                        a.application_code LIKE %s
                        OR c.full_name LIKE %s
                        OR j.job_title LIKE %s
                        OR co.company_name LIKE %s
                    )
                """
                term = f"%{search}%"
                values.extend([term, term, term, term])

            if status:
                query += " AND a.application_status = %s"
                values.append(status)

            query += " ORDER BY a.application_id DESC"

            cur.execute(query, tuple(values))
            return cur.fetchall()

        finally:
            con.close()

    def find_by_id(self, application_id):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute("""
                SELECT a.*,
                       c.full_name AS candidate_name,
                       j.job_title,
                       co.company_name
                FROM applications a
                JOIN candidates c ON a.candidate_id = c.candidate_id
                JOIN jobs j ON a.job_id = j.job_id
                JOIN companies co ON j.company_id = co.company_id
                WHERE a.application_id = %s
            """, (application_id,))
            return cur.fetchone()
        finally:
            con.close()

    def find_duplicate(self, candidate_id, job_id):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute("""
                SELECT application_id
                FROM applications
                WHERE candidate_id = %s AND job_id = %s
                LIMIT 1
            """, (candidate_id, job_id))
            return cur.fetchone()
        finally:
            con.close()

    def save(self, application):
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute("""
                INSERT INTO applications (
                    application_code,
                    candidate_id,
                    job_id,
                    eligibility_status,
                    eligibility_reason,
                    application_status,
                    source,
                    assigned_recruiter_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                application.application_code,
                application.candidate_id,
                application.job_id,
                application.eligibility_status,
                application.eligibility_reason,
                application.application_status,
                application.source,
                application.assigned_recruiter_id
            ))
            con.commit()
            return cur.lastrowid
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def update_status(self, application_id, status):
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute("""
                UPDATE applications
                SET application_status = %s
                WHERE application_id = %s
            """, (status, application_id))
            con.commit()
            return cur.rowcount
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()
