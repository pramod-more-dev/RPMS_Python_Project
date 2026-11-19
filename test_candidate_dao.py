
from rpms.dao.candidate_dao import CandidateDAO

dao = CandidateDAO()

candidates = dao.find_all()

print("\n===== CANDIDATE LIST =====")

for candidate in candidates:
    print(candidate.candidate_id, candidate.full_name, candidate.email, candidate.primary_technology)

print("\nTotal Candidates:", len(candidates))
