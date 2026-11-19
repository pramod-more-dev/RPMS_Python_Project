
from datetime import date

from rpms.dao.placement_dao import PlacementDAO


class PlacementService:

    VALID_JOINING_STATUSES = {
        "PENDING", "JOINED", "NOT_JOINED", "DEFERRED", "NO_SHOW"
    }

    VALID_PLACEMENT_STATUSES = {"ACTIVE", "CANCELLED"}

    def __init__(self, placement_dao=None):
        self.placement_dao = placement_dao or PlacementDAO()

    def get_all_placements(self, search="", joining_status=""):
        joining_status = str(joining_status or "").strip().upper()

        if joining_status and joining_status not in self.VALID_JOINING_STATUSES:
            raise ValueError("Invalid joining status")

        return self.placement_dao.find_all(search.strip(), joining_status)

    def get_placement(self, placement_id):
        placement = self.placement_dao.find_by_id(placement_id)

        if not placement:
            raise ValueError("Placement not found")

        return placement

    def get_statistics(self):
        return self.placement_dao.get_statistics()

    def create_placement(self, offer_id):
        try:
            offer_id = int(offer_id)
        except (TypeError, ValueError):
            raise ValueError("Valid Offer ID is required")

        if offer_id <= 0:
            raise ValueError("Valid Offer ID is required")

        if self.placement_dao.find_by_offer(offer_id):
            raise ValueError("Placement already exists for this offer")

        return self.placement_dao.create_from_offer(offer_id)

    def update_joining(self, placement_id, data):
        status = str(data.get("joining_status") or "").strip().upper()

        if status not in self.VALID_JOINING_STATUSES:
            raise ValueError("Invalid joining status")

        actual_date_value = data.get("actual_joining_date") or None

        try:
            actual_date = (
                date.fromisoformat(str(actual_date_value))
                if actual_date_value else None
            )
        except ValueError:
            raise ValueError("Enter a valid actual joining date")

        if status == "JOINED" and not actual_date:
            raise ValueError("Actual joining date is required when status is JOINED")

        if status != "JOINED":
            actual_date = None

        self.get_placement(placement_id)

        self.placement_dao.update_joining(
            placement_id,
            status,
            actual_date
        )

        return placement_id

    def update_placement_status(self, placement_id, status):
        status = str(status or "").strip().upper()

        if status not in self.VALID_PLACEMENT_STATUSES:
            raise ValueError("Invalid placement status")

        self.get_placement(placement_id)
        self.placement_dao.update_placement_status(placement_id, status)

        return placement_id
