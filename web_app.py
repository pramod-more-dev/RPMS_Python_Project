
import os
from dataclasses import asdict
from datetime import date, timedelta
from pathlib import Path

from flask import (
    Flask,
    jsonify,
    request,
    send_from_directory,
    session,
    redirect
)

from rpms.dao.candidate_dao import CandidateDAO
from rpms.model.candidate import Candidate
from rpms.service.candidate_service import CandidateService
from rpms.exception.exceptions import CandidateNotFoundError

from rpms.dao.company_dao import CompanyDAO
from rpms.model.company import Company
from rpms.service.company_service import CompanyService

from rpms.dao.job_dao import JobDAO
from rpms.model.job import Job
from rpms.service.job_service import JobService

from rpms.model.application import Application
from rpms.service.application_service import ApplicationService

from rpms.service.interview_service import InterviewService
from rpms.service.offer_service import OfferService
from rpms.service.placement_service import PlacementService
from rpms.service.report_service import ReportService
from rpms.service.auth_service import AuthService


BASE_DIR = Path(__file__).resolve().parent
UI_DIR = BASE_DIR / "ui"

app = Flask(__name__)

app.secret_key = os.environ.get("RPMS_SECRET_KEY")
if not app.secret_key:
    raise RuntimeError("RPMS_SECRET_KEY environment variable is required.")

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False,
    PERMANENT_SESSION_LIFETIME=timedelta(days=7)
)


candidate_dao = CandidateDAO()
candidate_service = CandidateService(candidate_dao)

company_dao = CompanyDAO()
company_service = CompanyService(company_dao)

job_dao = JobDAO()
job_service = JobService(job_dao)

application_service = ApplicationService()
interview_service = InterviewService()

offer_service = OfferService()
placement_service = PlacementService()
report_service = ReportService()

auth_service = AuthService()


# =====================================================
# AUTHENTICATION AND SESSION PROTECTION
# =====================================================

@app.before_request
def protect_routes():

    path = request.path

    public_api_routes = {
        "/api/auth/login",
        "/api/auth/logout"
    }

    if path.startswith("/api/"):

        if path in public_api_routes:
            return None

        if "user" not in session:
            return jsonify({
                "error": "Authentication required. Please sign in."
            }), 401

        return None

    if path.endswith(".html") and path != "/login.html":

        if "user" not in session:
            return redirect("/")

    return None


# =====================================================
# AUTHENTICATION API
# =====================================================

@app.route("/api/auth/login", methods=["POST"])
def login():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Valid login data is required."
        }), 400

    identifier = str(
        data.get("identifier")
        or data.get("email")
        or data.get("username")
        or ""
    ).strip()

    password = data.get("password", "")

    if not identifier or not isinstance(password, str) or not password:
        return jsonify({
            "error": "Username/email and password are required."
        }), 400

    try:
        user = auth_service.authenticate(identifier, password)

        if not user:
            return jsonify({
                "error": "Invalid username/email or password."
            }), 401

        session.clear()

        session["user"] = user
        session.permanent = bool(data.get("remember", False))

        return jsonify({
            "message": "Login successful.",
            "user": user,
            "redirect": "/dashboard.html"
        }), 200

    except Exception:
        app.logger.exception("Login failed")

        return jsonify({
            "error": "Unable to process login. Please try again."
        }), 500


@app.route("/api/auth/logout", methods=["POST"])
def logout_api():

    session.clear()

    return jsonify({
        "message": "Logout successful."
    }), 200


@app.route("/api/auth/me", methods=["GET"])
def get_logged_in_user():

    return jsonify({
        "user": session.get("user")
    }), 200


@app.route("/logout", methods=["GET"])
def logout_page():

    session.clear()

    return redirect("/")


# =====================================================
# PAGE ROUTES
# =====================================================

@app.route("/")
def home():

    if "user" in session:
        return redirect("/dashboard.html")

    return send_from_directory(UI_DIR, "login.html")


@app.route("/<path:filename>")
def serve_ui(filename):

    if filename == "login.html":
        session.clear()

    return send_from_directory(UI_DIR, filename)


# =====================================================
# COMMON HELPERS
# =====================================================

def serialize_job(job):

    data = asdict(job)

    for key, value in data.items():
        if isinstance(value, date):
            data[key] = value.isoformat()

    return data


def parse_optional_float(value):

    if value is None or value == "":
        return None

    return float(value)


def parse_optional_int(value):

    if value is None or value == "":
        return None

    return int(value)


def parse_date(value):

    if not value:
        return None

    return date.fromisoformat(value)


def create_candidate(data):

    return Candidate(
        candidate_code=str(data.get("candidate_code", "")).strip(),
        full_name=str(data.get("full_name", "")).strip(),
        email=str(data.get("email", "")).strip(),
        mobile=str(data.get("mobile", "")).strip(),
        qualification=str(data.get("qualification", "")).strip(),
        passing_year=int(data.get("passing_year")),
        percentage=float(data.get("percentage")),
        backlog_count=int(data.get("backlog_count")),
        primary_technology=str(data.get("primary_technology", "")).strip()
    )


def create_company(data):

    return Company(
        company_code=str(data.get("company_code", "")).strip(),
        company_name=str(data.get("company_name", "")).strip(),
        industry=str(data.get("industry") or "").strip(),
        website=str(data.get("website") or "").strip(),
        location=str(data.get("location") or "").strip(),
        company_type=str(data.get("company_type") or "").strip(),
        hr_name=str(data.get("hr_name") or "").strip(),
        hr_email=str(data.get("hr_email") or "").strip(),
        hr_mobile=str(data.get("hr_mobile") or "").strip(),
        status=str(data.get("status") or "ACTIVE").strip().upper()
    )


def create_job(data):

    return Job(
        job_code=str(data.get("job_code", "")).strip(),
        company_id=int(data.get("company_id") or 0),
        job_title=str(data.get("job_title", "")).strip(),
        employment_type=str(data.get("employment_type") or "FULL_TIME").strip().upper(),
        location=str(data.get("location", "")).strip(),
        openings=int(data.get("openings") or 0),
        min_package_lpa=parse_optional_float(data.get("min_package_lpa")),
        max_package_lpa=parse_optional_float(data.get("max_package_lpa")),
        min_percentage=parse_optional_float(data.get("min_percentage")),
        min_passing_year=parse_optional_int(data.get("min_passing_year")),
        max_passing_year=parse_optional_int(data.get("max_passing_year")),
        max_backlogs=int(data.get("max_backlogs") or 0),
        experience_min_years=float(data.get("experience_min_years") or 0),
        qualification_rule=str(data.get("qualification_rule") or "").strip() or None,
        posted_date=parse_date(data.get("posted_date")),
        application_deadline=parse_date(data.get("application_deadline")),
        status=str(data.get("status") or "OPEN").strip().upper(),
        created_by=int(data.get("created_by") or 0)
    )


def create_application(data):

    return Application(
        candidate_id=int(data.get("candidate_id") or 0),
        job_id=int(data.get("job_id") or 0),
        source=str(data.get("source") or "PORTAL").strip(),
        assigned_recruiter_id=parse_optional_int(
            data.get("assigned_recruiter_id")
        )
    )


def get_report_filters():

    return {
        "date_from": request.args.get("date_from", "").strip(),
        "date_to": request.args.get("date_to", "").strip(),
        "technology": request.args.get("technology", "").strip(),
        "company_id": request.args.get("company_id", "").strip(),
        "recruiter_id": request.args.get("recruiter_id", "").strip(),
        "passing_year": request.args.get("passing_year", "").strip()
    }


# =====================================================
# CANDIDATE API
# =====================================================

@app.route("/api/candidates", methods=["GET"])
def get_candidates():

    try:
        candidates = candidate_service.get_all_candidates()
        return jsonify([asdict(candidate) for candidate in candidates]), 200

    except Exception:
        app.logger.exception("Unable to fetch candidates")
        return jsonify({"error": "Unable to fetch candidates"}), 500


@app.route("/api/candidates/<int:candidate_id>", methods=["GET"])
def get_candidate(candidate_id):

    try:
        candidate = candidate_service.get_candidate(candidate_id)
        return jsonify(asdict(candidate)), 200

    except CandidateNotFoundError as error:
        return jsonify({"error": str(error)}), 404

    except Exception:
        app.logger.exception("Unable to fetch candidate")
        return jsonify({"error": "Unable to fetch candidate"}), 500


@app.route("/api/candidates", methods=["POST"])
def add_candidate():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON data is required"}), 400

    try:
        candidate = create_candidate(data)
        candidate_id = candidate_service.add_candidate(candidate)

        return jsonify({
            "message": "Candidate added successfully",
            "candidate_id": candidate_id
        }), 201

    except (ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Unable to add candidate")
        return jsonify({
            "error": "Unable to add candidate. Check duplicate values and database connection."
        }), 400


@app.route("/api/candidates/<int:candidate_id>", methods=["PUT"])
def update_candidate(candidate_id):

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON data is required"}), 400

    try:
        candidate = create_candidate(data)
        updated_id = candidate_service.update_candidate(candidate_id, candidate)

        return jsonify({
            "message": "Candidate updated successfully",
            "candidate_id": updated_id
        }), 200

    except CandidateNotFoundError as error:
        return jsonify({"error": str(error)}), 404

    except (ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Unable to update candidate")
        return jsonify({
            "error": "Unable to update candidate. Check duplicate values and database connection."
        }), 500


# =====================================================
# COMPANY API
# =====================================================

@app.route("/api/companies", methods=["GET"])
def get_companies():

    try:
        companies = company_service.get_all_companies()
        return jsonify([asdict(company) for company in companies]), 200

    except Exception:
        app.logger.exception("Unable to fetch companies")
        return jsonify({"error": "Unable to fetch companies"}), 500


@app.route("/api/companies/<int:company_id>", methods=["GET"])
def get_company(company_id):

    try:
        company = company_service.get_company(company_id)
        return jsonify(asdict(company)), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 404

    except Exception:
        app.logger.exception("Unable to fetch company")
        return jsonify({"error": "Unable to fetch company"}), 500


@app.route("/api/companies", methods=["POST"])
def add_company():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON data is required"}), 400

    try:
        company = create_company(data)
        company_id = company_service.add_company(company)

        return jsonify({
            "message": "Company added successfully",
            "company_id": company_id
        }), 201

    except (ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Unable to add company")
        return jsonify({
            "error": "Unable to add company. Check duplicate company code and database connection."
        }), 500


@app.route("/api/companies/<int:company_id>", methods=["PUT"])
def update_company(company_id):

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON data is required"}), 400

    try:
        company = create_company(data)
        updated_id = company_service.update_company(company_id, company)

        return jsonify({
            "message": "Company updated successfully",
            "company_id": updated_id
        }), 200

    except ValueError as error:
        status_code = 404 if "not found" in str(error).lower() else 400
        return jsonify({"error": str(error)}), status_code

    except Exception:
        app.logger.exception("Unable to update company")
        return jsonify({
            "error": "Unable to update company. Check duplicate company code and database connection."
        }), 500


# =====================================================
# JOB API
# =====================================================

@app.route("/api/jobs", methods=["GET"])
def get_jobs():

    try:
        search = request.args.get("search", "").strip()
        status = request.args.get("status", "").strip().upper()

        jobs = job_service.get_all_jobs(search, status)

        return jsonify([serialize_job(job) for job in jobs]), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Unable to fetch jobs")
        return jsonify({"error": "Unable to fetch jobs"}), 500


@app.route("/api/jobs/<int:job_id>", methods=["GET"])
def get_job(job_id):

    try:
        job = job_service.get_job(job_id)
        return jsonify(serialize_job(job)), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 404

    except Exception:
        app.logger.exception("Unable to fetch job")
        return jsonify({"error": "Unable to fetch job"}), 500


@app.route("/api/jobs", methods=["POST"])
def add_job():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON data is required"}), 400

    try:
        job = create_job(data)
        job_id = job_service.add_job(job)

        return jsonify({
            "message": "Job created successfully",
            "job_id": job_id
        }), 201

    except (ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Unable to create job")
        return jsonify({
            "error": "Unable to create job. Check job code, company, creator user and database constraints."
        }), 400


@app.route("/api/jobs/<int:job_id>", methods=["PUT"])
def update_job(job_id):

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON data is required"}), 400

    try:
        job = create_job(data)
        updated_id = job_service.update_job(job_id, job)

        return jsonify({
            "message": "Job updated successfully",
            "job_id": updated_id
        }), 200

    except ValueError as error:
        status_code = 404 if "not found" in str(error).lower() else 400
        return jsonify({"error": str(error)}), status_code

    except TypeError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Unable to update job")
        return jsonify({
            "error": "Unable to update job. Check database constraints."
        }), 500


# =====================================================
# APPLICATION API
# =====================================================

@app.route("/api/applications", methods=["GET"])
def get_applications():

    try:
        search = request.args.get("search", "").strip()
        status = request.args.get("status", "").strip().upper()

        applications = application_service.get_all_applications(
            search,
            status
        )

        return jsonify(applications), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Unable to fetch applications")
        return jsonify({"error": "Unable to fetch applications"}), 500


@app.route("/api/applications/<int:application_id>", methods=["GET"])
def get_application(application_id):

    try:
        application = application_service.get_application(application_id)
        return jsonify(application), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 404

    except Exception:
        app.logger.exception("Unable to fetch application")
        return jsonify({"error": "Unable to fetch application"}), 500


@app.route("/api/applications", methods=["POST"])
def add_application():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON data is required"}), 400

    try:
        application = create_application(data)
        application_id = application_service.add_application(application)

        return jsonify({
            "message": "Application created successfully",
            "application_id": application_id,
            "eligibility_status": application.eligibility_status,
            "eligibility_reason": application.eligibility_reason
        }), 201

    except (ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Unable to create application")
        return jsonify({
            "error": "Unable to create application. Check candidate, job and database constraints."
        }), 500


@app.route("/api/applications/<int:application_id>/status", methods=["PUT"])
def update_application_status(application_id):

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON data is required"}), 400

    try:
        status = str(data.get("application_status") or "").strip().upper()

        updated_id = application_service.update_status(
            application_id,
            status
        )

        return jsonify({
            "message": "Application status updated successfully",
            "application_id": updated_id,
            "application_status": status
        }), 200

    except ValueError as error:
        status_code = 404 if "not found" in str(error).lower() else 400
        return jsonify({"error": str(error)}), status_code

    except Exception:
        app.logger.exception("Unable to update application status")
        return jsonify({
            "error": "Unable to update application status"
        }), 500


# =====================================================
# INTERVIEW API
# =====================================================

@app.route("/api/interviews", methods=["GET"])
def get_interviews():

    try:
        search = request.args.get("search", "").strip()
        status = request.args.get("status", "").strip().upper()
        round_type = request.args.get("round_type", "").strip()

        interviews = interview_service.get_all_interviews(
            search,
            status,
            round_type
        )

        return jsonify(interviews), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Unable to fetch interviews")
        return jsonify({"error": "Unable to fetch interviews"}), 500


@app.route("/api/interviews/<int:interview_id>", methods=["GET"])
def get_interview(interview_id):

    try:
        interview = interview_service.get_interview(interview_id)
        return jsonify(interview), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 404

    except Exception:
        app.logger.exception("Unable to fetch interview")
        return jsonify({"error": "Unable to fetch interview"}), 500


@app.route("/api/interviews", methods=["POST"])
def schedule_interview():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON data is required"}), 400

    try:
        interview_id = interview_service.schedule_interview(data)

        return jsonify({
            "message": "Interview scheduled successfully",
            "interview_id": interview_id
        }), 201

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Unable to schedule interview")
        return jsonify({
            "error": "Unable to schedule interview. Check Application ID, duplicate round number and database constraints."
        }), 400


@app.route("/api/interviews/<int:interview_id>/status", methods=["PUT"])
def update_interview_status(interview_id):

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON data is required"}), 400

    try:
        status = data.get("status")
        interview_service.update_status(interview_id, status)

        return jsonify({
            "message": "Interview status updated successfully",
            "interview_id": interview_id,
            "status": str(status).upper()
        }), 200

    except ValueError as error:
        status_code = 404 if "not found" in str(error).lower() else 400
        return jsonify({"error": str(error)}), status_code

    except Exception:
        app.logger.exception("Unable to update interview status")
        return jsonify({"error": "Unable to update interview status"}), 500


# =====================================================
# INTERVIEW FEEDBACK API
# =====================================================

@app.route("/api/interviews/<int:interview_id>/feedback", methods=["GET"])
def get_interview_feedback(interview_id):

    try:
        feedback = interview_service.get_feedback(interview_id)
        return jsonify(feedback or {}), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 404

    except Exception:
        app.logger.exception("Unable to fetch interview feedback")
        return jsonify({"error": "Unable to fetch interview feedback"}), 500


@app.route("/api/interviews/<int:interview_id>/feedback", methods=["POST"])
def save_interview_feedback(interview_id):

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON data is required"}), 400

    try:
        feedback_id = interview_service.save_feedback(interview_id, data)

        return jsonify({
            "message": "Interview feedback saved successfully",
            "feedback_id": feedback_id,
            "interview_id": interview_id
        }), 201

    except ValueError as error:
        status_code = 404 if "not found" in str(error).lower() else 400
        return jsonify({"error": str(error)}), status_code

    except Exception:
        app.logger.exception("Unable to save interview feedback")
        return jsonify({
            "error": "Unable to save feedback. Check submitted-by user ID and database constraints."
        }), 500


# =====================================================
# OFFER API
# =====================================================

@app.route("/api/offers", methods=["GET"])
def get_offers():

    try:
        search = request.args.get("search", "").strip()
        status = request.args.get("status", "").strip().upper()

        offers = offer_service.get_all_offers(search, status)

        return jsonify(offers), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Unable to fetch offers")
        return jsonify({"error": "Unable to fetch offers"}), 500


@app.route("/api/offers/<int:offer_id>", methods=["GET"])
def get_offer(offer_id):

    try:
        return jsonify(offer_service.get_offer(offer_id)), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 404

    except Exception:
        app.logger.exception("Unable to fetch offer")
        return jsonify({"error": "Unable to fetch offer"}), 500


@app.route("/api/offers/statistics", methods=["GET"])
def get_offer_statistics():

    try:
        return jsonify(offer_service.get_statistics()), 200

    except Exception:
        app.logger.exception("Unable to fetch offer statistics")
        return jsonify({"error": "Unable to fetch offer statistics"}), 500


@app.route("/api/offers", methods=["POST"])
def add_offer():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON data is required"}), 400

    try:
        offer_id = offer_service.create_offer(data)

        return jsonify({
            "message": "Offer created successfully",
            "offer_id": offer_id
        }), 201

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Unable to create offer")
        return jsonify({
            "error": "Unable to create offer. Check offer code, application and database constraints."
        }), 500


@app.route("/api/offers/<int:offer_id>/status", methods=["PUT"])
def update_offer_status(offer_id):

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON data is required"}), 400

    try:
        status = data.get("offer_status")
        offer_service.update_status(offer_id, status)

        return jsonify({
            "message": "Offer status updated successfully",
            "offer_id": offer_id,
            "offer_status": str(status).upper()
        }), 200

    except ValueError as error:
        status_code = 404 if "not found" in str(error).lower() else 400
        return jsonify({"error": str(error)}), status_code

    except Exception:
        app.logger.exception("Unable to update offer status")
        return jsonify({"error": "Unable to update offer status"}), 500


# =====================================================
# PLACEMENT API
# =====================================================

@app.route("/api/placements", methods=["GET"])
def get_placements():

    try:
        search = request.args.get("search", "").strip()
        joining_status = request.args.get("joining_status", "").strip().upper()

        placements = placement_service.get_all_placements(
            search,
            joining_status
        )

        return jsonify(placements), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Unable to fetch placements")
        return jsonify({"error": "Unable to fetch placements"}), 500


@app.route("/api/placements/<int:placement_id>", methods=["GET"])
def get_placement(placement_id):

    try:
        return jsonify(placement_service.get_placement(placement_id)), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 404

    except Exception:
        app.logger.exception("Unable to fetch placement")
        return jsonify({"error": "Unable to fetch placement"}), 500


@app.route("/api/placements/statistics", methods=["GET"])
def get_placement_statistics():

    try:
        return jsonify(placement_service.get_statistics()), 200

    except Exception:
        app.logger.exception("Unable to fetch placement statistics")
        return jsonify({"error": "Unable to fetch placement statistics"}), 500


@app.route("/api/placements", methods=["POST"])
def add_placement():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON data is required"}), 400

    try:
        placement_id = placement_service.create_placement(
            data.get("offer_id")
        )

        return jsonify({
            "message": "Placement created successfully",
            "placement_id": placement_id
        }), 201

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Unable to create placement")
        return jsonify({
            "error": "Unable to create placement. Check accepted offer and database constraints."
        }), 500


@app.route("/api/placements/<int:placement_id>/joining", methods=["PUT"])
def update_placement_joining(placement_id):

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON data is required"}), 400

    try:
        placement_service.update_joining(placement_id, data)

        return jsonify({
            "message": "Joining details updated successfully",
            "placement_id": placement_id,
            "joining_status": str(data.get("joining_status") or "").upper()
        }), 200

    except ValueError as error:
        status_code = 404 if "not found" in str(error).lower() else 400
        return jsonify({"error": str(error)}), status_code

    except Exception:
        app.logger.exception("Unable to update joining details")
        return jsonify({"error": "Unable to update joining details"}), 500


@app.route("/api/placements/<int:placement_id>/status", methods=["PUT"])
def update_placement_status(placement_id):

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON data is required"}), 400

    try:
        status = data.get("placement_status")
        placement_service.update_placement_status(placement_id, status)

        return jsonify({
            "message": "Placement status updated successfully",
            "placement_id": placement_id,
            "placement_status": str(status).upper()
        }), 200

    except ValueError as error:
        status_code = 404 if "not found" in str(error).lower() else 400
        return jsonify({"error": str(error)}), status_code

    except Exception:
        app.logger.exception("Unable to update placement status")
        return jsonify({"error": "Unable to update placement status"}), 500


# =====================================================
# REPORTS API
# =====================================================

@app.route("/api/reports/filters", methods=["GET"])
def get_report_filter_options():

    try:
        return jsonify(report_service.get_filter_options()), 200

    except Exception:
        app.logger.exception("Unable to fetch report filter options")
        return jsonify({"error": "Unable to fetch report filter options"}), 500


@app.route("/api/reports", methods=["GET"])
def get_all_reports():

    try:
        filters = get_report_filters()
        reports = report_service.get_all_reports(filters)

        return jsonify(reports), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Unable to fetch reports")
        return jsonify({"error": "Unable to fetch reports"}), 500


@app.route("/api/reports/overview", methods=["GET"])
def get_report_overview():

    try:
        return jsonify(
            report_service.get_overview(get_report_filters())
        ), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Unable to fetch report overview")
        return jsonify({"error": "Unable to fetch report overview"}), 500


@app.route("/api/reports/candidates-by-technology", methods=["GET"])
def get_candidates_by_technology_report():

    try:
        return jsonify(
            report_service.candidate_count_by_technology(
                get_report_filters()
            )
        ), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Unable to fetch candidate technology report")
        return jsonify({"error": "Unable to fetch candidate technology report"}), 500


@app.route("/api/reports/applications-by-status", methods=["GET"])
def get_applications_by_status_report():

    try:
        return jsonify(
            report_service.application_count_by_status(
                get_report_filters()
            )
        ), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Unable to fetch application status report")
        return jsonify({"error": "Unable to fetch application status report"}), 500


@app.route("/api/reports/open-jobs-by-company", methods=["GET"])
def get_open_jobs_by_company_report():

    try:
        return jsonify(
            report_service.open_jobs_by_company(
                get_report_filters()
            )
        ), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Unable to fetch open jobs report")
        return jsonify({"error": "Unable to fetch open jobs report"}), 500


@app.route("/api/reports/placement-summary-by-company", methods=["GET"])
def get_placement_summary_report():

    try:
        return jsonify(
            report_service.placement_summary_by_company(
                get_report_filters()
            )
        ), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Unable to fetch placement summary")
        return jsonify({"error": "Unable to fetch placement summary"}), 500


@app.route("/api/reports/offer-to-joining", methods=["GET"])
def get_offer_to_joining_report():

    try:
        return jsonify(
            report_service.offer_to_joining_conversion(
                get_report_filters()
            )
        ), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Unable to fetch offer conversion report")
        return jsonify({"error": "Unable to fetch offer conversion report"}), 500


@app.route("/api/reports/recruitment-funnel", methods=["GET"])
def get_recruitment_funnel_report():

    try:
        return jsonify(
            report_service.recruitment_funnel(get_report_filters())
        ), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Unable to fetch recruitment funnel")
        return jsonify({"error": "Unable to fetch recruitment funnel"}), 500


@app.route("/api/reports/technology-wise-placement", methods=["GET"])
def get_technology_wise_placement_report():

    try:
        return jsonify(
            report_service.technology_wise_placement(get_report_filters())
        ), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Unable to fetch technology-wise placement")
        return jsonify({"error": "Unable to fetch technology-wise placement"}), 500


@app.route("/api/reports/recruiter-performance", methods=["GET"])
def get_recruiter_performance_report():

    try:
        return jsonify(
            report_service.recruiter_performance(get_report_filters())
        ), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Unable to fetch recruiter performance")
        return jsonify({"error": "Unable to fetch recruiter performance"}), 500


@app.route("/api/reports/pending-interviews", methods=["GET"])
def get_pending_interviews_report():

    try:
        return jsonify(
            report_service.pending_interviews(get_report_filters())
        ), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Unable to fetch pending interviews")
        return jsonify({"error": "Unable to fetch pending interviews"}), 500


@app.route("/api/reports/open-job-aging", methods=["GET"])
def get_open_job_aging_report():

    try:
        return jsonify(
            report_service.open_job_aging(get_report_filters())
        ), 200

    except ValueError as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Unable to fetch open job aging")
        return jsonify({"error": "Unable to fetch open job aging"}), 500


# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
