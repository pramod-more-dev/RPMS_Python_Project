RPMS PYTHON PROJECT - PYCHARM SETUP
==================================

1. Clone or download the RPMS_Python_Project repository.
2. Open PyCharm.
3. Select File > Open.
4. Select the RPMS project folder.
5. Configure the Python interpreter if PyCharm asks.

FIRST TIME SETUP
----------------

Open the PyCharm Terminal and run:

    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt

DATABASE CONFIGURATION
---------------------

Database name:
    recruitment_portal

Database:
    MySQL

Check database configuration:
    rpms/util/db_connection.py

Configure the following environment variables
before starting the application:

    RPMS_DB_HOST
    RPMS_DB_PORT
    RPMS_DB_USER
    RPMS_DB_PASSWORD
    RPMS_DB_NAME
    RPMS_SECRET_KEY

Never store database passwords or secret keys
directly in project source files.

DATABASE SETUP
--------------

Execute the SQL scripts in this order:

1. sql/rpms_schema.sql
2. sql/rpms_sample_data.sql

WARNING:
    rpms_full_setup.sql contains DROP DATABASE IF EXISTS.
    Use it only when intentionally resetting a disposable
    development database.

RUN THE WEB APPLICATION
-----------------------

    python web_app.py

Open the browser:

    http://127.0.0.1:5000

CONSOLE APPLICATION
-------------------

The separate console application can be started using:

    python main.py

IMPORTANT
---------

The web application entry point is web_app.py.
The console application entry point is main.py.

Configure valid demo user password hashes before attempting
to log in with seeded demo accounts.