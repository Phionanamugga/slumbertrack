# SlumberTrack — Django Sleep Tracking App

A clean, extensible sleep tracking web app built with Django and Django REST Framework.
Includes:
- Log sleep sessions with quality, awakenings, and notes
- Set personal sleep goals (target hours/bedtime/wake time)
- Dashboard with charts (Chart.js)
- CSV import/export
- Session-based auth + API endpoints

## Quickstart

```bash
python -m venv .venv && source venv/bin/activate  # Mac virtual environment activation
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/
- Sign up (or login with the superuser)
- Log your first sleep session
- Set your sleep goal

## API
- `/api/sessions/` (GET/POST, authenticated)
- `/api/goals/` (GET/POST, authenticated)

## CSV Format
Headers: `start,end,quality,latency_minutes,awakenings,tags,notes`
Example row:
`2025-08-10T22:45:00+03:00,2025-08-11T06:15:00+03:00,4,10,1,"coffee","slept well"`

## Tests
```bash
python manage.py test
```

## Notes
- Default timezone is **Africa/Kampala**.
- This project is intentionally lightweight; tailor models as you integrate wearable data.
