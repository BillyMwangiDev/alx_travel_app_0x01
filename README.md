ALX Travel App - 0x01. API Development for Listings and Bookings

Overview
- Implements core models (`Listing`, `Booking`, `Review`), DRF serializers, ViewSets with CRUD operations, and a `seed` management command for sample data.
- Provides RESTful API endpoints for managing listings and bookings with Swagger documentation.

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

API Endpoints

All API endpoints are available under `/api/` and follow RESTful conventions.

Listings API (`/api/listings/`)
- `GET /api/listings/` - List all listings (paginated, 10 per page)
- `POST /api/listings/` - Create a new listing
- `GET /api/listings/{id}/` - Retrieve a specific listing
- `PUT /api/listings/{id}/` - Update a listing (full update)
- `PATCH /api/listings/{id}/` - Partially update a listing
- `DELETE /api/listings/{id}/` - Delete a listing
- `GET /api/listings/{id}/bookings/` - Get all bookings for a specific listing

Bookings API (`/api/bookings/`)
- `GET /api/bookings/` - List all bookings (paginated, 10 per page)
  - Query parameter: `?listing_id=1` - Filter bookings by listing ID
- `POST /api/bookings/` - Create a new booking
- `GET /api/bookings/{id}/` - Retrieve a specific booking
- `PUT /api/bookings/{id}/` - Update a booking (full update)
- `PATCH /api/bookings/{id}/` - Partially update a booking
- `DELETE /api/bookings/{id}/` - Delete a booking

API Documentation
- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`
- OpenAPI Schema (JSON): `http://localhost:8000/swagger.json`
- OpenAPI Schema (YAML): `http://localhost:8000/swagger.yaml`

Example API Requests

Create a Listing:
```bash
curl -X POST http://localhost:8000/api/listings/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Cozy Apartment in Downtown",
    "description": "Beautiful 2-bedroom apartment",
    "location": "New York, NY",
    "price_per_night": "150.00",
    "max_guests": 4
  }'
```

Create a Booking:
```bash
curl -X POST http://localhost:8000/api/bookings/ \
  -H "Content-Type: application/json" \
  -d '{
    "listing": 1,
    "guest_name": "John Doe",
    "guest_email": "john@example.com",
    "start_date": "2024-06-01",
    "end_date": "2024-06-05",
    "total_price": "600.00",
    "status": "PENDING"
  }'
```

Get Listings:
```bash
curl http://localhost:8000/api/listings/
```

Get Bookings for a Listing:
```bash
curl http://localhost:8000/api/listings/1/bookings/
```

Filter Bookings by Listing:
```bash
curl http://localhost:8000/api/bookings/?listing_id=1
```

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
- feat(api): add ViewSets for listings and bookings with CRUD operations
- feat(api): configure RESTful API routes with DRF router
- feat(api): add Swagger documentation for API endpoints
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
        views.py
        urls.py
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


