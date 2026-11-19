
from rpms.util.db_connection import get_connection
from rpms.model.company import Company


class CompanyDAO:

    def find_all(self):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute("""
                SELECT company_id, company_code, company_name, industry,
                       website, location, company_type, hr_name, hr_email,
                       hr_mobile, status, created_at
                FROM companies
                ORDER BY company_id DESC
            """)
            rows = cur.fetchall()
            return [Company(**row) for row in rows]
        finally:
            con.close()

    def find_by_id(self, company_id):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute(
                "SELECT * FROM companies WHERE company_id = %s",
                (company_id,)
            )
            row = cur.fetchone()
            return Company(**row) if row else None
        finally:
            con.close()

    def find_by_code(self, company_code):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute(
                "SELECT * FROM companies WHERE company_code = %s",
                (company_code,)
            )
            row = cur.fetchone()
            return Company(**row) if row else None
        finally:
            con.close()

    def save(self, company):
        sql = """
            INSERT INTO companies (
                company_code, company_name, industry, website, location,
                company_type, hr_name, hr_email, hr_mobile, status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            company.company_code,
            company.company_name,
            company.industry or None,
            company.website or None,
            company.location or None,
            company.company_type or None,
            company.hr_name or None,
            company.hr_email or None,
            company.hr_mobile or None,
            company.status
        )

        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute(sql, values)
            con.commit()
            return cur.lastrowid
        finally:
            con.close()

    def update(self, company):
        sql = """
            UPDATE companies
            SET company_code = %s,
                company_name = %s,
                industry = %s,
                website = %s,
                location = %s,
                company_type = %s,
                hr_name = %s,
                hr_email = %s,
                hr_mobile = %s,
                status = %s
            WHERE company_id = %s
        """

        values = (
            company.company_code,
            company.company_name,
            company.industry or None,
            company.website or None,
            company.location or None,
            company.company_type or None,
            company.hr_name or None,
            company.hr_email or None,
            company.hr_mobile or None,
            company.status,
            company.company_id
        )

        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute(sql, values)
            con.commit()
            return cur.rowcount > 0
        finally:
            con.close()
