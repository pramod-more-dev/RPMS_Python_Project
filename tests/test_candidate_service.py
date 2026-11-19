
import unittest
from unittest.mock import Mock

from rpms.exception.exceptions import CandidateNotFoundError
from rpms.model.candidate import Candidate
from rpms.service.candidate_service import CandidateService


class TestCandidateService(unittest.TestCase):

    def setUp(self):
        self.dao = Mock()
        self.service = CandidateService(self.dao)

    def create_candidate(self, **overrides):
        data = {
            "candidate_code": "CAN-TEST-001",
            "full_name": "Test Candidate",
            "email": "candidate@example.com",
            "mobile": "9876543210",
            "qualification": "BCS",
            "passing_year": 2026,
            "percentage": 75.5,
            "backlog_count": 0,
            "primary_technology": "Python"
        }
        data.update(overrides)
        return Candidate(**data)

    def test_valid_candidate_add(self):
        candidate = self.create_candidate()
        self.dao.find_by_email.return_value = None
        self.dao.find_by_mobile.return_value = None
        self.dao.save.return_value = 101

        result = self.service.add_candidate(candidate)

        self.assertEqual(result, 101)
        self.dao.save.assert_called_once_with(candidate)

    def test_invalid_candidate_code(self):
        candidate = self.create_candidate(candidate_code=" ")

        with self.assertRaisesRegex(ValueError, "Candidate code is required"):
            self.service.add_candidate(candidate)

        self.dao.save.assert_not_called()

    def test_invalid_candidate_name(self):
        candidate = self.create_candidate(full_name=" ")

        with self.assertRaisesRegex(ValueError, "Candidate name is required"):
            self.service.add_candidate(candidate)

        self.dao.save.assert_not_called()

    def test_invalid_email(self):
        candidate = self.create_candidate(email="invalid-email")

        with self.assertRaisesRegex(ValueError, "Invalid email"):
            self.service.add_candidate(candidate)

        self.dao.save.assert_not_called()

    def test_invalid_mobile(self):
        candidate = self.create_candidate(mobile="12345")

        with self.assertRaisesRegex(ValueError, "Mobile must contain 10 digits"):
            self.service.add_candidate(candidate)

        self.dao.save.assert_not_called()

    def test_invalid_percentage(self):
        candidate = self.create_candidate(percentage=105)

        with self.assertRaisesRegex(ValueError, "Percentage must be between 0 and 100"):
            self.service.add_candidate(candidate)

        self.dao.save.assert_not_called()

    def test_negative_backlog_count(self):
        candidate = self.create_candidate(backlog_count=-1)

        with self.assertRaisesRegex(ValueError, "Backlog count cannot be negative"):
            self.service.add_candidate(candidate)

        self.dao.save.assert_not_called()

    def test_invalid_passing_year(self):
        candidate = self.create_candidate(passing_year=1999)

        with self.assertRaisesRegex(ValueError, "Invalid passing year"):
            self.service.add_candidate(candidate)

        self.dao.save.assert_not_called()

    def test_duplicate_email(self):
        candidate = self.create_candidate()
        self.dao.find_by_email.return_value = Candidate(candidate_id=10)

        with self.assertRaisesRegex(ValueError, "Duplicate email"):
            self.service.add_candidate(candidate)

        self.dao.save.assert_not_called()

    def test_duplicate_mobile(self):
        candidate = self.create_candidate()
        self.dao.find_by_email.return_value = None
        self.dao.find_by_mobile.return_value = Candidate(candidate_id=10)

        with self.assertRaisesRegex(ValueError, "Duplicate mobile"):
            self.service.add_candidate(candidate)

        self.dao.save.assert_not_called()

    def test_successful_candidate_update(self):
        candidate = self.create_candidate()
        existing = Candidate(
            candidate_id=7,
            profile_status="INACTIVE",
            placement_status="PLACED"
        )

        self.dao.find_by_id.return_value = existing
        self.dao.find_by_email.return_value = None
        self.dao.find_by_mobile.return_value = None
        self.dao.update.return_value = True

        result = self.service.update_candidate(7, candidate)

        self.assertEqual(result, 7)
        self.assertEqual(candidate.candidate_id, 7)
        self.assertEqual(candidate.profile_status, "INACTIVE")
        self.assertEqual(candidate.placement_status, "PLACED")
        self.dao.update.assert_called_once_with(candidate)

    def test_update_with_duplicate_email(self):
        candidate = self.create_candidate()
        existing = Candidate(candidate_id=7)
        another_candidate = Candidate(candidate_id=8)

        self.dao.find_by_id.return_value = existing
        self.dao.find_by_email.return_value = another_candidate

        with self.assertRaisesRegex(
            ValueError,
            "Email already belongs to another candidate"
        ):
            self.service.update_candidate(7, candidate)

        self.dao.update.assert_not_called()

    def test_update_with_duplicate_mobile(self):
        candidate = self.create_candidate()
        existing = Candidate(candidate_id=7)
        another_candidate = Candidate(candidate_id=8)

        self.dao.find_by_id.return_value = existing
        self.dao.find_by_email.return_value = None
        self.dao.find_by_mobile.return_value = another_candidate

        with self.assertRaisesRegex(
            ValueError,
            "Mobile already belongs to another candidate"
        ):
            self.service.update_candidate(7, candidate)

        self.dao.update.assert_not_called()

    def test_candidate_not_found(self):
        self.dao.find_by_id.return_value = None

        with self.assertRaises(CandidateNotFoundError):
            self.service.get_candidate(999)

    def test_get_all_candidates(self):
        expected = [
            Candidate(candidate_id=1),
            Candidate(candidate_id=2)
        ]
        self.dao.find_all.return_value = expected

        result = self.service.get_all_candidates()

        self.assertEqual(result, expected)
        self.dao.find_all.assert_called_once()


if __name__ == "__main__":
    unittest.main(verbosity=2)
