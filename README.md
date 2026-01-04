# Hospital Management System (DBMS)
A Django-based Hospital Management System backed by PostgreSQL. This project contains a Django project named guardiandb with an app named hospital.

## Tech Stack
Backend: Django (5.x)

Database: PostgreSQL

Language: Python 3.10+

## Repository Structure
Hospital-Management-System-DBMS/guardiandb/

manage.py — Django management script

guardiandb/ — Django project settings and URLs

hospital/ — Core application (models, views, templates, static)

requirements.txt — Python dependencies

Note: The project root is this folder; manage.py lives under Hospital-Management-System-DBMS/guardiandb/.

## Prerequisites
Python 3.10+

PostgreSQL 13+

Git

## Quick Start (Windows PowerShell)

### Create and activate a virtual environment
 py -m venv .venv

 .venv\Scripts\Activate.ps1

### Install dependencies
 pip install --upgrade pip

 pip install -r .\Hospital-Management-System-DBMS\guardiandb\requirements.txt

### Configure PostgreSQL

 Create a database and user, or adjust credentials in guardiandb/settings.py.

 Default local settings (edit as needed):

 NAME: guardiandb

 USER: postgres

 PASSWORD: *****

 HOST: localhost

 PORT: 5432

### Apply migrations and create a superuser
 from the folder that contains manage.py

 cd .\Hospital-Management-System-DBMS\guardiandb

 python manage.py migrate

 python manage.py createsuperuser

## Run the development server
 python manage.py runserver

 App will be available at: http://127.0.0.1:8000/

## Useful URLs
Admin: /admin/

Login: /login/

Dashboard (post-login): /dashboard/

## Configuration Notes
DEBUG is enabled by default. Do not use this configuration in production.

ALLOWED_HOSTS is empty; add your hostnames for deployment.

Time zone is set to Asia/Kolkata in settings.

Consider externalizing secrets (like SECRET_KEY and DB credentials) via environment variables for production. You may create a .env file and update settings.py accordingly.

## Static Files

Run python manage.py collectstatic before deploying to gather static files into the static root (configure in settings as needed).

## Troubleshooting
If pip install -r requirements.txt fails due to platform-specific wheels, upgrade pip and setuptools, then retry.

If you cannot connect to PostgreSQL, verify service is running, credentials are correct, and the database exists.

If python maps to Python 2 on your system, use py or python3 accordingly.
