
from datetime import date
from math import isfinite

from rpms.dao.offer_dao import OfferDAO
from rpms.model.offer import Offer


class OfferService:

    VALID_STATUSES = {
        "OFFERED", "ACCEPTED", "REJECTED", "EXPIRED", "WITHDRAWN"
    }

    def __init__(self, offer_dao=None):
        self.offer_dao = offer_dao or OfferDAO()

    def get_all_offers(self, search="", status=""):
        status = str(status or "").strip().upper()

        if status and status not in self.VALID_STATUSES:
            raise ValueError("Invalid offer status")

        return self.offer_dao.find_all(search.strip(), status)

    def get_offer(self, offer_id):
        offer = self.offer_dao.find_by_id(offer_id)
        if not offer:
            raise ValueError("Offer not found")
        return offer

    def get_statistics(self):
        return self.offer_dao.get_statistics()

    def create_offer(self, data):
        try:
            application_id = int(data.get("application_id") or 0)
            package = float(data.get("offered_package_lpa"))
            offer_date = date.fromisoformat(str(data.get("offer_date") or ""))
            expected_date = data.get("expected_joining_date") or None

            if expected_date:
                expected_date = date.fromisoformat(str(expected_date))

        except (TypeError, ValueError):
            raise ValueError("Enter valid application, package and dates")

        if application_id <= 0:
            raise ValueError("Valid Application ID is required")

        if not isfinite(package) or package < 0:
            raise ValueError("Package must be zero or greater")

        offer_code = str(data.get("offer_code") or "").strip()
        designation = str(data.get("designation") or "").strip()
        remarks = str(data.get("remarks") or "").strip() or None

        if not offer_code or len(offer_code) > 40:
            raise ValueError("Offer code is required (maximum 40 characters)")

        if not designation or len(designation) > 120:
            raise ValueError("Designation is required (maximum 120 characters)")

        if remarks and len(remarks) > 500:
            raise ValueError("Remarks cannot exceed 500 characters")

        application = self.offer_dao.find_application(application_id)

        if not application:
            raise ValueError("Application not found")

        if application["application_status"] != "SELECTED":
            raise ValueError("An offer can only be created for a SELECTED application")

        if self.offer_dao.find_by_application(application_id):
            raise ValueError("An offer already exists for this application")

        offer = Offer(
            offer_code=offer_code,
            application_id=application_id,
            designation=designation,
            offered_package_lpa=package,
            offer_date=offer_date,
            expected_joining_date=expected_date,
            offer_status="OFFERED",
            remarks=remarks
        )

        return self.offer_dao.save(offer)

    def update_status(self, offer_id, status):
        status = str(status or "").strip().upper()

        if status not in self.VALID_STATUSES:
            raise ValueError("Invalid offer status")

        offer = self.get_offer(offer_id)

        if offer["offer_status"] in {"REJECTED", "EXPIRED", "WITHDRAWN"}:
            raise ValueError("This offer is already closed")

        self.offer_dao.update_status(offer_id, status)
        return offer_id
