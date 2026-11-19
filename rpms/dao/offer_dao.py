
from rpms.util.db_connection import get_connection


class OfferDAO:

    def find_all(self, search="", status=""):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)

            query = """
                SELECT o.*,
                       a.application_code,
                       a.application_status,
                       c.candidate_id,
                       c.full_name AS candidate_name,
                       c.email AS candidate_email,
                       j.job_title,
                       co.company_name
                FROM offers o
                JOIN applications a ON o.application_id = a.application_id
                JOIN candidates c ON a.candidate_id = c.candidate_id
                JOIN jobs j ON a.job_id = j.job_id
                JOIN companies co ON j.company_id = co.company_id
                WHERE 1=1
            """
            values = []

            if search:
                query += """
                    AND (
                        o.offer_code LIKE %s
                        OR c.full_name LIKE %s
                        OR co.company_name LIKE %s
                        OR j.job_title LIKE %s
                        OR o.designation LIKE %s
                    )
                """
                term = f"%{search}%"
                values.extend([term] * 5)

            if status:
                query += " AND o.offer_status = %s"
                values.append(status)

            query += " ORDER BY o.offer_id DESC"

            cur.execute(query, tuple(values))
            return cur.fetchall()

        finally:
            con.close()

    def find_by_id(self, offer_id):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute("""
                SELECT o.*,
                       a.application_code,
                       a.application_status,
                       c.candidate_id,
                       c.full_name AS candidate_name,
                       j.job_title,
                       j.company_id,
                       co.company_name
                FROM offers o
                JOIN applications a ON o.application_id = a.application_id
                JOIN candidates c ON a.candidate_id = c.candidate_id
                JOIN jobs j ON a.job_id = j.job_id
                JOIN companies co ON j.company_id = co.company_id
                WHERE o.offer_id = %s
            """, (offer_id,))
            return cur.fetchone()
        finally:
            con.close()

    def find_application(self, application_id):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute("""
                SELECT a.application_id,
                       a.application_code,
                       a.application_status,
                       a.candidate_id,
                       c.full_name AS candidate_name,
                       j.job_id,
                       j.job_title,
                       j.company_id,
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

    def find_by_application(self, application_id):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute("""
                SELECT offer_id, offer_code, offer_status
                FROM offers
                WHERE application_id = %s
            """, (application_id,))
            return cur.fetchone()
        finally:
            con.close()

    def save(self, offer):
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute("""
                INSERT INTO offers (
                    offer_code,
                    application_id,
                    designation,
                    offered_package_lpa,
                    offer_date,
                    expected_joining_date,
                    offer_status,
                    remarks
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                offer.offer_code,
                offer.application_id,
                offer.designation,
                offer.offered_package_lpa,
                offer.offer_date,
                offer.expected_joining_date,
                offer.offer_status,
                offer.remarks
            ))
            con.commit()
            return cur.lastrowid
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def update_status(self, offer_id, status):
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute("""
                UPDATE offers
                SET offer_status = %s
                WHERE offer_id = %s
            """, (status, offer_id))
            con.commit()
            return cur.rowcount
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def get_statistics(self):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute("""
                SELECT
                    COUNT(*) AS total_offers,
                    SUM(offer_status = 'ACCEPTED') AS accepted_offers,
                    SUM(offer_status = 'OFFERED') AS pending_offers,
                    SUM(offer_status = 'REJECTED') AS rejected_offers
                FROM offers
            """)
            return cur.fetchone()
        finally:
            con.close()
