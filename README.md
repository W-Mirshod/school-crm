# School CRM

A minimal Django-based CRM for school user management with registration, login, password reset, and admin panel.

## Features
- User registration and SMS verification
- JWT login and token refresh
- Password reset via SMS
- Admin panel with filters and search
- API docs at `/swagger/`

## Quick Start

### Docker
```bash
docker compose up --build
```

### Manual
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Admin: `/admin/`

---
