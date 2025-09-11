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
