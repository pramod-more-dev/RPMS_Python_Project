
# Recruitment & Placement Management System (RPMS)

## Project Overview
The Recruitment and Placement Management System (RPMS) is a Python and MySQL based application designed to manage candidate information, company details, job opportunities, applications, interviews, offers and placements.

It helps placement administrators organize recruitment activities and maintain candidate records efficiently.

## Technologies Used
- Python
- MySQL
- MySQL Connector
- HTML5
- CSS3
- Visual Studio Code
- MySQL Workbench

## Project Modules

1. Candidate Management
2. Company Management
3. Job Management
4. Application Management
5. Eligibility Checking
6. Interview Management
7. Offer Management
8. Placement Management
9. Reports
10. Activity Logging

## Project Structure

```text
RPMS_Python_VSCode/
│
├── main.py
├── requirements.txt
├── README.md
│
├── rpms/
│   ├── app/
│   ├── dao/
│   ├── exception/
│   ├── model/
│   ├── service/
│   └── util/
│
└── ui/
    ├── login.html
    ├── dashboard.html
    ├── candidates.html
    ├── candidate-form.html
    ├── candidate-details.html
    ├── companies.html
    ├── jobs.html
    ├── job-form.html
    ├── applications.html
    ├── interviews.html
    ├── placement-process.html
    ├── reports.html
    └── css/
        └── style.css
```

## Database
Database Name: `recruitment_portal`

The MySQL database contains tables for:
- Candidates
- Companies
- Jobs
- Applications
- Interview Rounds
- Interview Feedback
- Offers
- Placements
- Users and Roles
- Skills
- Application History
- Activity Logs

## Setup Instructions

1. Install Python and MySQL Server.
2. Create the MySQL database using the provided schema SQL file.
3. Import the sample data SQL file.
4. Install the required Python package:

```bash
pip install mysql-connector-python
```

5. Configure the MySQL connection details in:

```text
rpms/util/db_connection.py
```

6. Run the application:

```bash
python main.py
```

## Running the UI Prototype

Open the `ui` folder and launch `login.html` in a web browser.

The HTML/CSS pages are a separate static UI prototype. They are not connected to the Python backend.

## Main Features

- Add and view candidate records.
- Validate candidate information.
- Prevent duplicate candidate email and mobile numbers.
- View available job openings.
- Check candidate eligibility for jobs.
- Prevent duplicate applications.
- Generate recruitment reports.
- Maintain activity logs.
- Display recruitment and placement information.

## Project Type
Internship Project – Recruitment & Placement Management System
