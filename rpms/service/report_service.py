
from datetime import datetime

from rpms.util.db_connection import get_connection


class ReportService:

    def _fetch_all(self, query, params=None):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute(query, params or ())
            return cur.fetchall()
        finally:
            con.close()

    def _fetch_one(self, query, params=None):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute(query, params or ())
            return cur.fetchone()
        finally:
            con.close()

    # -------------------------------------------------
    # FILTER VALIDATION
    # -------------------------------------------------

    def _normalise_filters(self, filters=None):
        filters = filters or {}

        result = {
            "date_from": str(filters.get("date_from") or "").strip(),
            "date_to": str(filters.get("date_to") or "").strip(),
            "technology": str(filters.get("technology") or "").strip(),
            "company_id": str(filters.get("company_id") or "").strip(),
            "recruiter_id": str(filters.get("recruiter_id") or "").strip(),
            "passing_year": str(filters.get("passing_year") or "").strip()
        }

        for key in ("date_from", "date_to"):
            if result[key]:
                try:
                    datetime.strptime(result[key], "%Y-%m-%d")
                except ValueError:
                    raise ValueError(
                        f"Invalid {key.replace('_', ' ')}. Use YYYY-MM-DD."
                    )

        if result["date_from"] and result["date_to"]:
            if result["date_from"] > result["date_to"]:
                raise ValueError("From date cannot be after To date.")

        for key in ("company_id", "recruiter_id", "passing_year"):
            if result[key]:
                try:
                    value = int(result[key])
                    if value <= 0:
                        raise ValueError
                    result[key] = value
                except ValueError:
                    raise ValueError(
                        f"Invalid {key.replace('_', ' ')}."
                    )

        return result

    def _conditions(
        self,
        filters,
        date_column=None,
        candidate_alias="c",
        job_alias="j",
        application_alias="a"
    ):
        conditions = []
        params = []

        if filters.get("date_from") and date_column:
            conditions.append(f"{date_column} >= %s")
            params.append(filters["date_from"])

        if filters.get("date_to") and date_column:
            conditions.append(
                f"{date_column} < DATE_ADD(%s, INTERVAL 1 DAY)"
            )
            params.append(filters["date_to"])

        if filters.get("technology") and candidate_alias:
            conditions.append(
                f"{candidate_alias}.primary_technology = %s"
            )
            params.append(filters["technology"])

        if filters.get("company_id") and job_alias:
            conditions.append(
                f"{job_alias}.company_id = %s"
            )
            params.append(filters["company_id"])

        if filters.get("recruiter_id") and application_alias:
            conditions.append(
                f"{application_alias}.assigned_recruiter_id = %s"
            )
            params.append(filters["recruiter_id"])

        if filters.get("passing_year") and candidate_alias:
            conditions.append(
                f"{candidate_alias}.passing_year = %s"
            )
            params.append(filters["passing_year"])

        return conditions, params

    def _where_clause(self, conditions):
        if not conditions:
            return ""
        return " WHERE " + " AND ".join(conditions)

    # -------------------------------------------------
    # FILTER OPTIONS
    # -------------------------------------------------

    def get_filter_options(self):

        technologies = self._fetch_all("""
            SELECT DISTINCT primary_technology AS value
            FROM candidates
            WHERE primary_technology IS NOT NULL
              AND TRIM(primary_technology) <> ''
            ORDER BY primary_technology
        """)

        companies = self._fetch_all("""
            SELECT company_id, company_name
            FROM companies
            ORDER BY company_name
        """)

        recruiters = self._fetch_all("""
            SELECT u.user_id, u.full_name
            FROM users u
            INNER JOIN roles r
                ON r.role_id = u.role_id
            WHERE LOWER(r.role_name) = 'recruiter'
              AND u.status = 'ACTIVE'
            ORDER BY u.full_name
        """)

        passing_years = self._fetch_all("""
            SELECT DISTINCT passing_year AS value
            FROM candidates
            ORDER BY passing_year DESC
        """)

        return {
            "technologies": technologies,
            "companies": companies,
            "recruiters": recruiters,
            "passing_years": passing_years
        }

    # -------------------------------------------------
    # OVERVIEW
    # -------------------------------------------------

    def get_overview(self, filters=None):
        filters = self._normalise_filters(filters)

        candidate_conditions, candidate_params = self._conditions(
            filters,
            date_column="c.created_at",
            candidate_alias="c",
            job_alias=None,
            application_alias=None
        )

        job_conditions, job_params = self._conditions(
            filters,
            date_column="j.posted_date",
            candidate_alias=None,
            job_alias="j",
            application_alias=None
        )
        job_conditions.append("j.status = 'OPEN'")

        application_conditions, application_params = self._conditions(
            filters,
            date_column="a.applied_at"
        )

        placement_conditions, placement_params = self._conditions(
            filters,
            date_column="p.created_at",
            candidate_alias="c",
            job_alias="j",
            application_alias="a"
        )
        placement_conditions.append("p.placement_status = 'ACTIVE'")

        candidate_query = """
            SELECT COUNT(*) AS total
            FROM candidates c
        """ + self._where_clause(candidate_conditions)

        job_query = """
            SELECT COUNT(*) AS total
            FROM jobs j
        """ + self._where_clause(job_conditions)

        application_query = """
            SELECT COUNT(DISTINCT a.application_id) AS total
            FROM applications a
            INNER JOIN candidates c
                ON c.candidate_id = a.candidate_id
            INNER JOIN jobs j
                ON j.job_id = a.job_id
        """ + self._where_clause(application_conditions)

        placement_query = """
            SELECT COUNT(DISTINCT p.placement_id) AS total
            FROM placements p
            INNER JOIN candidates c
                ON c.candidate_id = p.candidate_id
            INNER JOIN jobs j
                ON j.job_id = p.job_id
            LEFT JOIN applications a
                ON a.candidate_id = p.candidate_id
               AND a.job_id = p.job_id
        """ + self._where_clause(placement_conditions)

        return {
            "total_candidates": self._fetch_one(
                candidate_query, candidate_params
            )["total"],

            "open_jobs": self._fetch_one(
                job_query, job_params
            )["total"],

            "total_applications": self._fetch_one(
                application_query, application_params
            )["total"],

            "total_placements": self._fetch_one(
                placement_query, placement_params
            )["total"]
        }

    # -------------------------------------------------
    # CANDIDATES BY TECHNOLOGY
    # -------------------------------------------------

    def candidate_count_by_technology(self, filters=None):
        filters = self._normalise_filters(filters)

        conditions, params = self._conditions(
            filters,
            date_column="c.created_at",
            candidate_alias="c",
            job_alias=None,
            application_alias=None
        )

        query = """
            SELECT
                COALESCE(
                    NULLIF(c.primary_technology, ''),
                    'Not Specified'
                ) AS technology,
                COUNT(*) AS total
            FROM candidates c
        """ + self._where_clause(conditions) + """
            GROUP BY c.primary_technology
            ORDER BY total DESC
        """

        return self._fetch_all(query, params)

    # -------------------------------------------------
    # APPLICATIONS BY STATUS
    # -------------------------------------------------

    def application_count_by_status(self, filters=None):
        filters = self._normalise_filters(filters)

        conditions, params = self._conditions(
            filters,
            date_column="a.applied_at"
        )

        query = """
            SELECT
                a.application_status,
                COUNT(DISTINCT a.application_id) AS total
            FROM applications a
            INNER JOIN candidates c
                ON c.candidate_id = a.candidate_id
            INNER JOIN jobs j
                ON j.job_id = a.job_id
        """ + self._where_clause(conditions) + """
            GROUP BY a.application_status
            ORDER BY total DESC
        """

        return self._fetch_all(query, params)

    # -------------------------------------------------
    # OPEN JOBS BY COMPANY
    # -------------------------------------------------

    def open_jobs_by_company(self, filters=None):
        filters = self._normalise_filters(filters)

        join_conditions = ["j.status = 'OPEN'"]
        params = []

        if filters.get("date_from"):
            join_conditions.append("j.posted_date >= %s")
            params.append(filters["date_from"])

        if filters.get("date_to"):
            join_conditions.append(
                "j.posted_date < DATE_ADD(%s, INTERVAL 1 DAY)"
            )
            params.append(filters["date_to"])

        if filters.get("company_id"):
            join_conditions.append("j.company_id = %s")
            params.append(filters["company_id"])

        query = """
            SELECT
                co.company_id,
                co.company_name,
                COUNT(j.job_id) AS open_job_positions,
                COALESCE(SUM(j.openings), 0) AS total_openings
            FROM companies co
            LEFT JOIN jobs j
                ON co.company_id = j.company_id
                AND """ + " AND ".join(join_conditions) + """
            GROUP BY co.company_id, co.company_name
            ORDER BY open_job_positions DESC, co.company_name
        """

        return self._fetch_all(query, params)

    # -------------------------------------------------
    # PLACEMENT SUMMARY BY COMPANY
    # -------------------------------------------------

    def placement_summary_by_company(self, filters=None):
        filters = self._normalise_filters(filters)

        conditions, params = self._conditions(
            filters,
            date_column="p.created_at",
            candidate_alias="ca",
            job_alias="j",
            application_alias="a"
        )

        conditions.append("p.placement_status = 'ACTIVE'")

        query = """
            SELECT
                co.company_name,
                COUNT(DISTINCT p.placement_id) AS placed_candidates,
                ROUND(AVG(p.final_package_lpa), 2)
                    AS average_package_lpa,
                MAX(p.final_package_lpa) AS highest_package_lpa
            FROM placements p
            INNER JOIN companies co
                ON co.company_id = p.company_id
            INNER JOIN candidates ca
                ON ca.candidate_id = p.candidate_id
            INNER JOIN jobs j
                ON j.job_id = p.job_id
            LEFT JOIN applications a
                ON a.candidate_id = p.candidate_id
               AND a.job_id = p.job_id
        """ + self._where_clause(conditions) + """
            GROUP BY co.company_id, co.company_name
            ORDER BY placed_candidates DESC, co.company_name
        """

        return self._fetch_all(query, params)

    # -------------------------------------------------
    # OFFER TO JOINING CONVERSION
    # -------------------------------------------------

    def offer_to_joining_conversion(self, filters=None):
        filters = self._normalise_filters(filters)

        conditions, params = self._conditions(
            filters,
            date_column="o.offer_date"
        )

        query = """
            SELECT
                o.offer_status,
                COUNT(DISTINCT o.offer_id) AS total_offers,
                COUNT(DISTINCT CASE
                    WHEN p.joining_status = 'JOINED'
                    THEN p.placement_id
                END) AS joined_candidates
            FROM offers o
            INNER JOIN applications a
                ON a.application_id = o.application_id
            INNER JOIN candidates c
                ON c.candidate_id = a.candidate_id
            INNER JOIN jobs j
                ON j.job_id = a.job_id
            LEFT JOIN placements p
                ON p.offer_id = o.offer_id
        """ + self._where_clause(conditions) + """
            GROUP BY o.offer_status
            ORDER BY total_offers DESC
        """

        return self._fetch_all(query, params)

    # -------------------------------------------------
    # RECRUITMENT FUNNEL
    # -------------------------------------------------

    def recruitment_funnel(self, filters=None):
        filters = self._normalise_filters(filters)

        conditions, params = self._conditions(
            filters,
            date_column="a.applied_at"
        )

        query = """
            SELECT
                COUNT(DISTINCT a.application_id) AS applied,

                COUNT(DISTINCT CASE
                    WHEN a.eligibility_status = 'ELIGIBLE'
                    THEN a.application_id
                END) AS eligible,

                COUNT(DISTINCT CASE
                    WHEN a.application_status = 'SHORTLISTED'
                    THEN a.application_id
                END) AS shortlisted,

                COUNT(DISTINCT CASE
                    WHEN a.application_status IN (
                        'INTERVIEW_SCHEDULED',
                        'INTERVIEWED'
                    )
                    THEN a.application_id
                END) AS interviewed,

                COUNT(DISTINCT CASE
                    WHEN a.application_status IN (
                        'SELECTED',
                        'OFFERED',
                        'JOINED'
                    )
                    THEN a.application_id
                END) AS selected,

                COUNT(DISTINCT o.offer_id) AS offered,

                COUNT(DISTINCT CASE
                    WHEN p.joining_status = 'JOINED'
                    THEN p.placement_id
                END) AS joined

            FROM applications a

            INNER JOIN candidates c
                ON c.candidate_id = a.candidate_id

            INNER JOIN jobs j
                ON j.job_id = a.job_id

            LEFT JOIN offers o
                ON o.application_id = a.application_id

            LEFT JOIN placements p
                ON p.offer_id = o.offer_id
        """ + self._where_clause(conditions)

        row = self._fetch_one(query, params) or {}

        stages = [
            ("Applied", "applied"),
            ("Eligible", "eligible"),
            ("Shortlisted", "shortlisted"),
            ("Interviewed", "interviewed"),
            ("Selected", "selected"),
            ("Offered", "offered"),
            ("Joined", "joined")
        ]

        return [
            {
                "stage": label,
                "total": int(row.get(key) or 0)
            }
            for label, key in stages
        ]

    # -------------------------------------------------
    # TECHNOLOGY-WISE PLACEMENT
    # -------------------------------------------------

    def technology_wise_placement(self, filters=None):
        filters = self._normalise_filters(filters)

        conditions, params = self._conditions(
            filters,
            date_column="p.created_at",
            candidate_alias="c",
            job_alias="j",
            application_alias="a"
        )

        conditions.append("p.placement_status = 'ACTIVE'")

        query = """
            SELECT
                COALESCE(
                    NULLIF(c.primary_technology, ''),
                    'Not Specified'
                ) AS technology,

                COUNT(DISTINCT p.placement_id) AS total_placements,

                ROUND(AVG(p.final_package_lpa), 2)
                    AS average_package_lpa,

                MAX(p.final_package_lpa) AS highest_package_lpa

            FROM placements p

            INNER JOIN candidates c
                ON c.candidate_id = p.candidate_id

            INNER JOIN jobs j
                ON j.job_id = p.job_id

            LEFT JOIN applications a
                ON a.candidate_id = p.candidate_id
               AND a.job_id = p.job_id
        """ + self._where_clause(conditions) + """
            GROUP BY c.primary_technology
            ORDER BY total_placements DESC
        """

        return self._fetch_all(query, params)

    # -------------------------------------------------
    # RECRUITER PERFORMANCE
    # -------------------------------------------------

    def recruiter_performance(self, filters=None):
        filters = self._normalise_filters(filters)

        conditions, params = self._conditions(
            filters,
            date_column="a.applied_at",
            candidate_alias="c",
            job_alias="j",
            application_alias="a"
        )

        conditions.extend([
            "u.status = 'ACTIVE'",
            "LOWER(r.role_name) = 'recruiter'"
        ])

        query = """
            SELECT
                u.user_id AS recruiter_id,
                u.full_name AS recruiter_name,

                COUNT(DISTINCT a.application_id)
                    AS assigned_applications,

                COUNT(DISTINCT CASE
                    WHEN a.application_status = 'SHORTLISTED'
                    THEN a.application_id
                END) AS shortlisted,

                COUNT(DISTINCT CASE
                    WHEN a.application_status IN (
                        'INTERVIEW_SCHEDULED',
                        'INTERVIEWED'
                    )
                    THEN a.application_id
                END) AS interviewed,

                COUNT(DISTINCT CASE
                    WHEN a.application_status IN (
                        'SELECTED',
                        'OFFERED',
                        'JOINED'
                    )
                    THEN a.application_id
                END) AS selected,

                COUNT(DISTINCT o.offer_id) AS total_offers,

                COUNT(DISTINCT CASE
                    WHEN p.joining_status = 'JOINED'
                    THEN p.placement_id
                END) AS joined_candidates

            FROM users u

            INNER JOIN roles r
                ON r.role_id = u.role_id

            LEFT JOIN applications a
                ON a.assigned_recruiter_id = u.user_id

            LEFT JOIN candidates c
                ON c.candidate_id = a.candidate_id

            LEFT JOIN jobs j
                ON j.job_id = a.job_id

            LEFT JOIN offers o
                ON o.application_id = a.application_id

            LEFT JOIN placements p
                ON p.offer_id = o.offer_id
        """ + self._where_clause(conditions) + """
            GROUP BY u.user_id, u.full_name
            ORDER BY assigned_applications DESC, u.full_name
        """

        return self._fetch_all(query, params)

    # -------------------------------------------------
    # PENDING INTERVIEWS
    # -------------------------------------------------

    def pending_interviews(self, filters=None):
        filters = self._normalise_filters(filters)

        conditions, params = self._conditions(
            filters,
            date_column="ir.scheduled_date"
        )

        conditions.extend([
            "ir.status IN ('SCHEDULED', 'RESCHEDULED')",
            "ir.scheduled_date >= CURDATE()"
        ])

        query = """
            SELECT
                ir.interview_id,
                ir.round_number,
                ir.round_type,
                ir.scheduled_date,
                CAST(ir.scheduled_time AS CHAR) AS scheduled_time,
                ir.mode,
                ir.interviewer_name,
                ir.meeting_or_location,
                ir.status,

                a.application_code,

                c.candidate_id,
                c.full_name AS candidate_name,
                c.primary_technology,

                j.job_title,
                co.company_name

            FROM interview_rounds ir

            INNER JOIN applications a
                ON a.application_id = ir.application_id

            INNER JOIN candidates c
                ON c.candidate_id = a.candidate_id

            INNER JOIN jobs j
                ON j.job_id = a.job_id

            INNER JOIN companies co
                ON co.company_id = j.company_id
        """ + self._where_clause(conditions) + """
            ORDER BY ir.scheduled_date, ir.scheduled_time
        """

        return self._fetch_all(query, params)

    # -------------------------------------------------
    # OPEN JOB AGING
    # -------------------------------------------------

    def open_job_aging(self, filters=None):
        filters = self._normalise_filters(filters)

        conditions, params = self._conditions(
            filters,
            date_column="j.posted_date",
            candidate_alias=None,
            job_alias="j",
            application_alias=None
        )

        conditions.append("j.status = 'OPEN'")

        query = """
            SELECT
                j.job_id,
                j.job_code,
                j.job_title,
                co.company_name,
                j.location,
                j.openings,
                j.posted_date,
                j.application_deadline,

                DATEDIFF(
                    CURDATE(),
                    j.posted_date
                ) AS age_in_days,

                CASE
                    WHEN DATEDIFF(CURDATE(), j.posted_date) <= 7
                        THEN '0-7 Days'

                    WHEN DATEDIFF(CURDATE(), j.posted_date) <= 15
                        THEN '8-15 Days'

                    WHEN DATEDIFF(CURDATE(), j.posted_date) <= 30
                        THEN '16-30 Days'

                    ELSE 'Above 30 Days'
                END AS aging_bucket

            FROM jobs j

            INNER JOIN companies co
                ON co.company_id = j.company_id
        """ + self._where_clause(conditions) + """
            ORDER BY age_in_days DESC, j.job_title
        """

        return self._fetch_all(query, params)

    # -------------------------------------------------
    # ALL REPORTS
    # -------------------------------------------------

    def get_all_reports(self, filters=None):
        filters = self._normalise_filters(filters)

        return {
            "overview": self.get_overview(filters),

            "candidates_by_technology":
                self.candidate_count_by_technology(filters),

            "applications_by_status":
                self.application_count_by_status(filters),

            "open_jobs_by_company":
                self.open_jobs_by_company(filters),

            "placement_summary_by_company":
                self.placement_summary_by_company(filters),

            "offer_to_joining_conversion":
                self.offer_to_joining_conversion(filters),

            "recruitment_funnel":
                self.recruitment_funnel(filters),

            "technology_wise_placement":
                self.technology_wise_placement(filters),

            "recruiter_performance":
                self.recruiter_performance(filters),

            "pending_interviews":
                self.pending_interviews(filters),

            "open_job_aging":
                self.open_job_aging(filters)
        }
