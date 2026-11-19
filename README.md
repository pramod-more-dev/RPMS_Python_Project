# Recruitment & Placement Management System (RPMS)

A Python-based Recruitment and Placement Management System built using Flask, MySQL, HTML, CSS, and JavaScript.

RPMS helps placement administrators manage candidates, companies, job openings, applications, interviews, offers, joining details, placements, and recruitment reports through an integrated web application.

## Project Overview

The Recruitment & Placement Management System (RPMS) is designed to simplify and organize the recruitment and campus placement process.

The application provides a centralized platform for maintaining candidate records, managing company and job information, tracking applications, conducting interview rounds, processing offers, and monitoring final placements.

The project follows a layered architecture using Python models, DAO classes, service classes, and a MySQL database.

## Key Features

- User authentication and session management.
- Dashboard with recruitment summary cards and analytics.
- Candidate registration, management, and profile details.
- Company management.
- Job creation, updating, and management.
- Candidate job applications and application status tracking.
- Candidate eligibility checking.
- Duplicate application prevention.
- Interview scheduling and interview feedback management.
- Offer management and joining details.
- Placement tracking.
- Recruitment reports and analytics.
- Report filtering and CSV export.
- Activity logging.
- MySQL database integration.

## Technology Stack

| Category | Technology |
|---|---|
| Programming Language | Python |
| Backend Framework | Flask |
| Database | MySQL |
| Database Connector | MySQL Connector/Python |
| Frontend | HTML5, CSS3, JavaScript |
| Development Environment | Visual Studio Code |
| Database Management | MySQL Workbench |
| Version Control | Git and GitHub |

## Application Architecture

The application follows a layered architecture.

```text
User / Web Browser
        |
        v
HTML, CSS and JavaScript UI
        |
        v
Flask Application (web_app.py)
        |
        v
Service Layer
(Business Logic and Validation)
        |
        v
DAO Layer
(Database Operations)
        |
        v
MySQL Connector
        |
        v
MySQL Database
```

### Main Layers

- **Model:** Represents application data and entities.
- **DAO:** Handles database operations.
- **Service:** Implements business rules and validation.
- **App:** Contains application entry-point and console application logic.
- **Util:** Provides database connection and validation utilities.
- **Exception:** Contains custom exception handling.
- **UI:** Provides the web application interface.

## Project Modules

1. Authentication and Login
2. Dashboard
3. Candidate Management
4. Company Management
5. Job Management
6. Application Management
7. Eligibility Checking
8. Interview Management and Feedback
9. Offer Management
10. Joining Management
11. Placement Management
12. Reports and Analytics
13. Activity Logging

## Project Structure

```text
RPMS_Python_VSCode/
|
|-- web_app.py
|-- main.py
|-- requirements.txt
|-- README.md
|-- reports.sql
|-- RPMS_Data_Dictionary.csv
|-- RPMS_ER_Diagram.png
|-- RPMS_ER_Diagram.mwb
|-- test_candidate_dao.py
|
|-- rpms/
|   |-- app/
|   |-- dao/
|   |-- exception/
|   |-- model/
|   |-- service/
|   |-- util/
|
|-- sql/
|   |-- rpms_schema.sql
|   |-- rpms_sample_data.sql
|   |-- rpms_full_setup.sql
|
|-- ui/
|   |-- login.html
|   |-- dashboard.html
|   |-- candidates.html
|   |-- candidate-form.html
|   |-- candidate-details.html
|   |-- companies.html
|   |-- company-form.html
|   |-- jobs.html
|   |-- job-form.html
|   |-- applications.html
|   |-- interviews.html
|   |-- placement-process.html
|   |-- reports.html
|   |
|   |-- css/
|       |-- style.css
|
|-- docs/
```

## Database Information

**Database Name:** `recruitment_portal`

The application uses MySQL with 17 database tables.

| No. | Table Name |
|---:|---|
| 1 | users |
| 2 | roles |
| 3 | candidates |
| 4 | candidate_skills |
| 5 | companies |
| 6 | jobs |
| 7 | job_skills |
| 8 | applications |
| 9 | application_history |
| 10 | interview_rounds |
| 11 | interview_feedback |
| 12 | offers |
| 13 | placements |
| 14 | skills |
| 15 | qualifications |
| 16 | locations |
| 17 | activity_logs |

Database documentation is available in:

- `RPMS_ER_Diagram.png`
- `RPMS_ER_Diagram.mwb`
- `RPMS_Data_Dictionary.csv`

## Installation and Setup

### Prerequisites

- Python 3.9 or newer
- MySQL Server
- MySQL Workbench (recommended)
- Git
- Visual Studio Code (recommended)

### 1. Clone the Repository

```bash
git clone https://github.com/pramod-more-dev/RPMS_Python_Project.git
```

### 2. Open the Project Directory

```bash
cd RPMS_Python_Project
```

### 3. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it using PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure the MySQL Database

Open MySQL Workbench.

1. Execute `sql/rpms_schema.sql` to create the database and tables.
2. Select the `recruitment_portal` database.
3. Execute `sql/rpms_sample_data.sql` to insert sample records.

**Important:** The `rpms_full_setup.sql` script contains `DROP DATABASE IF EXISTS`. It can delete an existing `recruitment_portal` database. Use it only when intentionally resetting a disposable development database.

The sample SQL file contains placeholder password hashes for demo users. Configure a valid password hash before attempting to log in with a seeded demo account.

### 6. Configure Environment Variables

The application reads database credentials and the Flask secret key from environment variables.

In PowerShell, configure:

```powershell
$env:RPMS_DB_HOST = "localhost"
$env:RPMS_DB_PORT = "3306"
$env:RPMS_DB_USER = "root"
$env:RPMS_DB_PASSWORD = "YOUR_MYSQL_PASSWORD"
$env:RPMS_DB_NAME = "recruitment_portal"
```

Generate a secure Flask secret key for the current terminal session:

```powershell
$env:RPMS_SECRET_KEY = (python -c "import secrets; print(secrets.token_hex(32))")
```

Replace `YOUR_MYSQL_PASSWORD` with your own local MySQL password.

Do not commit database passwords, secret keys, or other credentials to GitHub.

### 7. Run the Web Application

Start the Flask application:

```bash
python web_app.py
```

Open the following address in your browser:

```text
http://127.0.0.1:5000
```

The main web application entry point is `web_app.py`.

A separate console application entry point is also available through `main.py`.

## Application Workflow

```text
Login
  |
  v
Dashboard
  |
  v
Candidate Management
  |
  v
Company Management
  |
  v
Job Management
  |
  v
Application and Eligibility Checking
  |
  v
Interview Scheduling and Feedback
  |
  v
Offer Management
  |
  v
Joining Process
  |
  v
Placement Management
  |
  v
Reports and Analytics
```

## Security and Development Notes

- Database credentials are configured using environment variables.
- Flask session cookies use HTTP-only and SameSite settings.
- Authentication is required for protected application routes.
- Password verification uses password hashing.
- SQL operations are handled through the DAO layer.

This project is configured for local development and academic demonstration. The current Flask development configuration, including debug mode and local cookie settings, must be reviewed and hardened before any production deployment.

## Project Type

Internship Project - Recruitment & Placement Management System

## Repository

GitHub: https://github.com/pramod-more-dev/RPMS_Python_Project
