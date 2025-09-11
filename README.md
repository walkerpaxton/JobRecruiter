## JobRecruiter

A web app that provides a job recruiting service.

### Tech Stack
- **Backend**: Django (Python)
- **Database**: SQL (e.g., MySQL/PostgreSQL)
- **Frontend**: HTML + Bootstrap
- **Hosting**: PythonAnywhere

### Project Structure
```text
JobRecruiter/
├─ manage.py
├─ requirements.txt
├─ runtime.txt                  # e.g., python-3.11.x for PythonAnywhere
├─ .env.example                 # environment variable names (no secrets)
├─ README.md
├─ config/                      # Django project settings and URLs
│  ├─ __init__.py
│  ├─ settings/
│  │  ├─ __init__.py
│  │  ├─ base.py               # common settings
│  │  ├─ local.py              # dev overrides
│  │  └─ production.py         # PythonAnywhere overrides
│  ├─ urls.py
│  ├─ wsgi.py                  # PythonAnywhere uses WSGI
│  └─ asgi.py
├─ apps/
│  ├─ core/
│  ├─ accounts/
│  ├─ jobs/
│  └─ applications/
├─ templates/
├─ static/
├─ media/
├─ scripts/
└─ deploy/
```

### Local Development
1. Create and activate a virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables in `.env`
4. Run migrations and start the server

### Deploy (PythonAnywhere)
- Create a virtualenv and install requirements
- Point WSGI to the Django project
- Set environment variables and static/media settings
