
from rpms.util.db_connection import get_connection


class PlacementDAO:

    def find_all(self, search="", joining_status=""):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)

            query = """
                SELECT p.*,
                       o.offer_code,
                       c.full_name AS candidate_name,
                       co.company_name,
                       j.job_title
                FROM placements p
                JOIN offers o ON p.offer_id = o.offer_id
                JOIN candidates c ON p.candidate_id = c.candidate_id
                JOIN companies co ON p.company_id = co.company_id
                JOIN jobs j ON p.job_id = j.job_id
                WHERE 1=1
            """
            values = []

            if search:
                query += """
                    AND (
                        c.full_name LIKE %s
                        OR co.company_name LIKE %s
                        OR j.job_title LIKE %s
                        OR o.offer_code LIKE %s
                    )
                """
                term = f"%{search}%"
                values.extend([term] * 4)

            if joining_status:
                query += " AND p.joining_status = %s"
                values.append(joining_status)

            query += " ORDER BY p.placement_id DESC"

            cur.execute(query, tuple(values))
            return cur.fetchall()

        finally:
            con.close()

    def find_by_id(self, placement_id):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute("""
                SELECT p.*,
                       o.offer_code,
                       c.full_name AS candidate_name,
                       co.company_name,
                       j.job_title
                FROM placements p
                JOIN offers o ON p.offer_id = o.offer_id
                JOIN candidates c ON p.candidate_id = c.candidate_id
                JOIN companies co ON p.company_id = co.company_id
                JOIN jobs j ON p.job_id = j.job_id
                WHERE p.placement_id = %s
            """, (placement_id,))
            return cur.fetchone()
        finally:
            con.close()

    def find_by_offer(self, offer_id):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)
            cur.execute("""
                SELECT placement_id
                FROM placements
                WHERE offer_id = %s
            """, (offer_id,))
            return cur.fetchone()
        finally:
            con.close()

    def create_from_offer(self, offer_id):
        con = get_connection()
        try:
            cur = con.cursor(dictionary=True)

            cur.execute("""
                SELECT o.offer_id,
                       o.application_id,
                       o.designation,
                       o.offered_package_lpa,
                       o.expected_joining_date,
                       o.offer_status,
                       a.candidate_id,
                       j.company_id,
                       j.job_id
                FROM offers o
                JOIN applications a ON o.application_id = a.application_id
                JOIN jobs j ON a.job_id = j.job_id
                WHERE o.offer_id = %s
                FOR UPDATE
            """, (offer_id,))

            offer = cur.fetchone()

            if not offer:
                raise ValueError("Offer not found")

            if offer["offer_status"] != "ACCEPTED":
                raise ValueError("Only accepted offers can create placements")

            cur.execute("""
                SELECT placement_id
                FROM placements
                WHERE offer_id = %s
            """, (offer_id,))

            if cur.fetchone():
                raise ValueError("Placement already exists for this offer")

            cur.execute("""
                INSERT INTO placements (
                    candidate_id,
                    company_id,
                    job_id,
                    offer_id,
                    designation,
                    final_package_lpa,
                    expected_joining_date,
                    joining_status,
                    placement_status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'PENDING', 'ACTIVE')
            """, (
                offer["candidate_id"],
                offer["company_id"],
                offer["job_id"],
                offer["offer_id"],
                offer["designation"],
                offer["offered_package_lpa"],
                offer["expected_joining_date"]
            ))

            placement_id = cur.lastrowid
            con.commit()
            return placement_id

        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def update_joining(self, placement_id, joining_status, actual_joining_date):
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute("""
                UPDATE placements
                SET joining_status = %s,
                    actual_joining_date = %s
                WHERE placement_id = %s
            """, (joining_status, actual_joining_date, placement_id))
            con.commit()
            return cur.rowcount
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def update_placement_status(self, placement_id, status):
        con = get_connection()
        try:
            cur = con.cursor()
            cur.execute("""
                UPDATE placements
                SET placement_status = %s
                WHERE placement_id = %s
            """, (status, placement_id))
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
                    COUNT(*) AS total_placements,
                    SUM(joining_status = 'JOINED') AS joined_count,
                    SUM(joining_status = 'PENDING') AS pending_count,
                    SUM(placement_status = 'ACTIVE') AS active_count
                FROM placements
            """)
            return cur.fetchone()
        finally:
            con.close()
