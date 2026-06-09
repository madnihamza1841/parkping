# ParkPing Backend

Django REST Framework backend with Django Channels WebSocket support.

## Local Setup

### Prerequisites
- Python 3.11+
- Redis (optional for local dev — in-memory channel layer used by default)

### Steps

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env with your values

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

ASGI server (for WebSocket support):
```bash
daphne parkping_backend.asgi:application
```

### Settings

| Module | Purpose |
|--------|---------|
| `parkping_backend/settings/base.py` | Shared settings |
| `parkping_backend/settings/local.py` | SQLite + in-memory channels |
| `parkping_backend/settings/production.py` | PostgreSQL + Redis + HTTPS |

Set `DJANGO_SETTINGS_MODULE` to switch, e.g.:
```bash
export DJANGO_SETTINGS_MODULE=parkping_backend.settings.production
```

### API Docs

Swagger UI available at `/api/docs/` once the server is running.

### Running Tests

```bash
pytest
```
