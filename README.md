ALX Travel App - 0. Database Modeling and Data Seeding

Overview
- Implements core models (`Listing`, `Booking`, `Review`), DRF serializers, and a `seed` management command for sample data.

Setup (Windows PowerShell / cmd)
1) Create & activate virtualenv (Python 3.12)

```
py -3.12 -m venv .venv
.venv\Scripts\activate
```

2) Install dependencies

```
pip install -r requirements.txt
```

3) Environment files

Create `.env` at either `alx_travel_app/alx_travel_app/` or repo root with:

```
SECRET_KEY=django-insecure-change-me
DEBUG=True
DB_NAME=alx_travel_app_db
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306
```

Use `.env.example` as a template.

4) Database setup

```
python manage.py makemigrations
python manage.py migrate
```

5) Run seeder

```
python manage.py seed --listings 5 --bookings-per-listing 2 --reviews-per-listing 2 --flush
```

6) Run tests

```
pytest -q
```

Models
- `Listing`: title, description, location, price_per_night, max_guests, timestamps.
- `Booking`: FK to Listing, guest details, date range, total_price, status, constraint end_date ≥ start_date.
- `Review`: FK to Listing, reviewer_name, rating (1–5), comment, timestamp.

Serializers
- `ListingSerializer`, `BookingSerializer` with validation (date range, non-negative total_price).

Management Command
- `python manage.py seed` creates sample listings with associated bookings and reviews. Options: `--listings`, `--bookings-per-listing`, `--reviews-per-listing`, `--flush`.

Git

```
git init
git checkout -b main
git checkout -b feat/models-and-seed
git add .
git commit -m "Initialize models, serializers, and seed command"
```

Example commit series
- chore(project): add config files (.flake8, CI, docs)
- feat(models): add Listing, Booking, Review with constraints
- feat(api): add serializers for listing and booking
- feat(seed): add management command to seed database
- test(listings): add unit and integration tests

Project Tree (key parts)

```
alx_travel_app/
  manage.py
  requirements.txt
  README.md
  .flake8
  .github/workflows/ci.yml
  Dockerfile
  docker-compose.yml
  docs/ADRs/0001-seeding.md
  alx_travel_app/
    alx_travel_app/
      settings.py
      urls.py
      listings/
        models.py
        serializers.py
        tests.py
        management/commands/seed.py
```

CI
- GitHub Actions workflow runs lint, tests, and security audit.

Docker (dev)

```
docker build -t alx-travel-app:dev .
docker compose up -d
```

Notes
- This project currently uses `django-environ` for settings. Populate `.env` and keep secrets out of source control.


