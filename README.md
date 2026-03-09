# Gharpayy CRM

A complete Lead Management CRM system for the **Gharpayy** PG accommodation platform.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2 (Python) |
| Database | MongoDB (via mongoengine) |
| Frontend | Django Templates + Bootstrap 5 |
| Auth | Django built-in auth (SQLite) |
| Deployment | Render + Gunicorn |

---

## Features

- **Lead Capture** — Public-facing form; auto-assigns an agent via round-robin
- **Lead Pipeline** — 8-stage Kanban board (New Lead → Booked / Lost)
- **Visit Scheduling** — Book property visits, record outcomes
- **Follow-up Reminders** — Auto-generated when a lead stagnates >24 h in a stage
- **Agent Management** — Add/edit agents; round-robin auto assignment
- **Dashboard** — KPI cards, pipeline overview, source distribution chart
- **Analytics** — Bar/pie/line charts for stage, source, agent performance, monthly trend

---

## Local Setup

### 1. Clone & create virtualenv

```bash
git clone <repo-url>
cd gharpayy
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and set your MONGODB_URI and a strong SECRET_KEY
```

### 3. Run migrations (SQLite for Django auth)

```bash
python manage.py migrate
```

### 4. Seed sample data

```bash
python manage.py seed_data
```

This creates:
- Superuser: `admin` / `admin123`
- 3 agents (Rahul, Priya, Amit)
- 10 sample leads

### 5. Start the dev server

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` — you'll be redirected to `/login/`.

---

## URL Reference

| URL | Description |
|-----|-------------|
| `/` | Dashboard |
| `/login/` | Login page |
| `/leads/` | Lead list |
| `/leads/capture/` | Public lead capture form |
| `/leads/pipeline/` | Kanban pipeline view |
| `/leads/followups/` | Pending follow-up reminders |
| `/leads/<id>/` | Lead detail / edit |
| `/visits/` | Visit list |
| `/visits/schedule/` | Schedule a visit |
| `/agents/` | Agent list |
| `/analytics/` | Analytics page |

---

## Running Follow-up Reminders

Run this command manually or set it up as a cron job / Render cron:

```bash
python manage.py create_followups
```

This creates reminders for any lead that has been in the same stage for more than 24 hours.

---

## MongoDB Models

```
Collection: agents       — Agent documents
Collection: leads        — Lead documents
Collection: visits       — Visit documents
Collection: followups    — FollowUp reminder documents
Collection: stage_history — Lead stage change history
Collection: round_robin_state — Tracks round-robin assignment index
```

---

## Project Structure

```
gharpayy/
├── gharpayy/            # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── leads/               # Lead management app
│   ├── models.py        # Lead, StageHistory, FollowUp
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── management/commands/
│       ├── create_followups.py
│       └── seed_data.py
├── agents/              # Agent management app
│   ├── models.py        # Agent, RoundRobinState
│   ├── views.py
│   ├── urls.py
│   └── utils.py         # Round-robin logic
├── visits/              # Visit scheduling app
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   └── urls.py
├── dashboard/           # Dashboard & analytics app
│   ├── views.py
│   └── urls.py
├── templates/           # All HTML templates
│   ├── base.html
│   ├── auth/login.html
│   ├── dashboard/
│   ├── leads/
│   ├── agents/
│   └── visits/
├── static/              # CSS, JS, images
├── requirements.txt
├── Procfile
├── .env.example
└── manage.py
```

---

## Deployment on Render

1. Push code to GitHub
2. Create a **new Web Service** on Render, connect the repo
3. Set **Build Command**: `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput`
4. Set **Start Command**: `gunicorn gharpayy.wsgi:application`
5. Add **Environment Variables**:
   - `SECRET_KEY` — a long random string
   - `DEBUG` — `False`
   - `ALLOWED_HOSTS` — `your-app.onrender.com`
   - `MONGODB_URI` — your MongoDB Atlas connection string
   - `MONGODB_DB` — `gharpayy`
6. (Optional) Add a **Cron Job** on Render:
   - Command: `python manage.py create_followups`
   - Schedule: `0 * * * *` (every hour)

---

## Creating a Django Superuser Manually

```bash
python manage.py createsuperuser
```
