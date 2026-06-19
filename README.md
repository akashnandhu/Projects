# Mental Health Care & Safety Intervention Platform

A complete, production-ready Django web application whose core mission is to provide a supportive, real-time chat environment with intelligent background analysis to detect crisis situations (suicide/self-harm ideation) or public safety threats.

## Prerequisites

- Python 3.11+
- Redis Server (for production channel layer)
- PostgreSQL (for production database)

## Setup Instructions

### 1. Create and Activate Virtual Environment

**Windows:**
```shell
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```shell
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```shell
pip install -r requirements.txt
```

### 3. Setup Environment Variables
Copy the `.env.example` file to create your local `.env`:
```shell
cp .env.example .env
```
Update the `.env` settings as needed for your environment.

### 4. Database Migrations
Make sure you are in the project root containing `manage.py`.
```shell
python manage.py makemigrations accounts chat alerts
python manage.py migrate
```

### 5. Create Superuser (For Staff Dashboard Access)
```shell
python manage.py createsuperuser
```

### 6. Collect Static Files
```shell
python manage.py collectstatic
```

### 7. Run the Application with Daphne
You must use an ASGI server like Daphne to handle WebSockets properly.
```shell
daphne -b 127.0.0.1 -p 8000 config.asgi:application
```
Alternatively, for pure local development, you can still run `python manage.py runserver`, as Django 5 + channels handles ASGI correctly if Daphne is in `INSTALLED_APPS`.
```shell
python manage.py runserver
```

## Production Enhancements Notes
Always search for `# TODO:` in the codebase to see where production readiness changes apply. Key components:
1. **Database:** Switch to PostgreSQL.
2. **Channel Layer:** Configure Redis.
3. **Content Moderation:** Replace intent classifier heuristics with an NLP model.
4. **Security:** Implement `django-encrypted-model-fields` for PII protection.
