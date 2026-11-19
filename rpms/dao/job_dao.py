
from rpms.model.job import Job
from rpms.util.db_connection import get_connection


class JobDAO:

    def find_all(self, search="", status=""):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)

            sql = """
                SELECT j.*, c.company_name
                FROM jobs j
                INNER JOIN companies c ON j.company_id = c.company_id
                WHERE 1=1
            """
            params = []

            if search:
                sql += """
                    AND (
                        j.job_title LIKE %s
                        OR j.job_code LIKE %s
                        OR j.location LIKE %s
                        OR c.company_name LIKE %s
                    )
                """
                value = f"%{search}%"
                params.extend([value, value, value, value])

            if status:
                sql += " AND j.status = %s"
                params.append(status)

            sql += " ORDER BY j.job_id DESC"

            cur.execute(sql, tuple(params))
            return [self._map(row) for row in cur.fetchall()]
        finally:
            con.close()

    def find_by_id(self, job_id):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute("""
                SELECT j.*, c.company_name
                FROM jobs j
                INNER JOIN companies c ON j.company_id = c.company_id
                WHERE j.job_id = %s
            """, (job_id,))
            row = cur.fetchone()
            return self._map(row) if row else None
        finally:
            con.close()

    def find_open_jobs(self):
        return self.find_all(status="OPEN")

    def save(self, job):
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute("""
                INSERT INTO jobs (
                    job_code, company_id, job_title, employment_type,
                    location, openings, min_package_lpa, max_package_lpa,
                    min_percentage, min_passing_year, max_passing_year,
                    max_backlogs, experience_min_years, qualification_rule,
                    posted_date, application_deadline, status, created_by
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                job.job_code, job.company_id, job.job_title,
                job.employment_type, job.location, job.openings,
                job.min_package_lpa, job.max_package_lpa,
                job.min_percentage, job.min_passing_year,
                job.max_passing_year, job.max_backlogs,
                job.experience_min_years, job.qualification_rule,
                job.posted_date, job.application_deadline,
                job.status, job.created_by
            ))
            con.commit()
            return cur.lastrowid
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def update(self, job_id, job):
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute("""
                UPDATE jobs SET
                    job_code = %s,
                    company_id = %s,
                    job_title = %s,
                    employment_type = %s,
                    location = %s,
                    openings = %s,
                    min_package_lpa = %s,
                    max_package_lpa = %s,
                    min_percentage = %s,
                    min_passing_year = %s,
                    max_passing_year = %s,
                    max_backlogs = %s,
                    experience_min_years = %s,
                    qualification_rule = %s,
                    posted_date = %s,
                    application_deadline = %s,
                    status = %s
                WHERE job_id = %s
            """, (
                job.job_code, job.company_id, job.job_title,
                job.employment_type, job.location, job.openings,
                job.min_package_lpa, job.max_package_lpa,
                job.min_percentage, job.min_passing_year,
                job.max_passing_year, job.max_backlogs,
                job.experience_min_years, job.qualification_rule,
                job.posted_date, job.application_deadline,
                job.status, job_id
            ))
            con.commit()
            return cur.rowcount > 0
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    @staticmethod
    def _map(row):
        return Job(
            job_id=row["job_id"],
            job_code=row["job_code"],
            company_id=row["company_id"],
            job_title=row["job_title"],
            employment_type=row["employment_type"],
            location=row["location"],
            openings=row["openings"],
            min_package_lpa=float(row["min_package_lpa"]) if row["min_package_lpa"] is not None else None,
            max_package_lpa=float(row["max_package_lpa"]) if row["max_package_lpa"] is not None else None,
            min_percentage=float(row["min_percentage"]) if row["min_percentage"] is not None else None,
            min_passing_year=row["min_passing_year"],
            max_passing_year=row["max_passing_year"],
            max_backlogs=row["max_backlogs"],
            experience_min_years=float(row["experience_min_years"]),
            qualification_rule=row["qualification_rule"],
            posted_date=row["posted_date"],
            application_deadline=row["application_deadline"],
            status=row["status"],
            created_by=row["created_by"],
            created_at=row["created_at"]
        )
