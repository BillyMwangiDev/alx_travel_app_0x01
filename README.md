ALX Travel App - 0x02. Chapa Payment Integration

Overview
- Implements core models (`Listing`, `Booking`, `Review`, `Payment`), DRF serializers, ViewSets with CRUD operations, and a `seed` management command for sample data.
- Provides RESTful API endpoints for managing listings and bookings with Swagger documentation.
- Integrates Chapa API for secure payment processing with booking workflow.
- Uses Celery for background email tasks (confirmation emails on successful payment).

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

# Chapa API Configuration
CHAPA_SECRET_KEY=your-chapa-secret-key-here
CHAPA_API_URL=https://api.chapa.co/v1
CHAPA_WEBHOOK_CALLBACK_URL=http://localhost:8000/api/payments/verify/

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@alxtravelapp.local

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

**Important:** 
- Get your Chapa API secret key from https://developer.chapa.co/
- For testing, use Chapa's sandbox environment
- For production, use your production API keys
- The `.env` file is in `.gitignore` - your API keys will NOT be committed to git

4) Install Redis (required for Celery)

**Windows:**
- Download and install Redis from https://redis.io/download
- Or use WSL/Docker: `docker run -d -p 6379:6379 redis:alpine`

**Linux/Mac:**
```bash
sudo apt-get install redis-server  # Ubuntu/Debian
brew install redis  # Mac
```

5) Database setup

```
python manage.py makemigrations
python manage.py migrate
```

6) Start Celery worker (in a separate terminal)

```bash
celery -A alx_travel_app.alx_travel_app worker --loglevel=info
```

7) Run seeder

```
python manage.py seed --listings 5 --bookings-per-listing 2 --reviews-per-listing 2 --flush
```

8) Run tests

```
pytest -q
```

Models
- `Listing`: title, description, location, price_per_night, max_guests, timestamps.
- `Booking`: FK to Listing, guest details, date range, total_price, status, constraint end_date ≥ start_date.
- `Review`: FK to Listing, reviewer_name, rating (1–5), comment, timestamp.
- `Payment`: OneToOne with Booking, stores booking_reference, transaction_id, amount, status (PENDING/COMPLETED/FAILED).

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
- `POST /api/bookings/` - Create a new booking (automatically initiates payment)
- `GET /api/bookings/{id}/` - Retrieve a specific booking
- `PUT /api/bookings/{id}/` - Update a booking (full update)
- `PATCH /api/bookings/{id}/` - Partially update a booking
- `DELETE /api/bookings/{id}/` - Delete a booking

Payment API (`/api/payments/`)
- `POST /api/bookings/{booking_id}/initiate-payment/` - Manually initiate payment for an existing booking
- `GET /api/payments/verify/?tx_ref=<transaction_reference>` - Verify payment status with Chapa API
- `POST /api/payments/verify/` - Verify payment (webhook callback from Chapa)

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

Create a Booking (automatically initiates payment):
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

Response includes payment details and checkout URL:
```json
{
  "booking": {...},
  "payment": {
    "status": "PENDING",
    "booking_reference": "BK-1-ABC12345",
    "amount": "600.00",
    "checkout_url": "https://checkout.chapa.co/..."
  }
}
```

Verify Payment:
```bash
curl -X GET "http://localhost:8000/api/payments/verify/?tx_ref=BK-1-ABC12345"
```

Initiate Payment for Existing Booking:
```bash
curl -X POST http://localhost:8000/api/bookings/1/initiate-payment/
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
- feat(models): add Payment model for Chapa integration
- feat(api): add serializers for listing and booking
- feat(api): add ViewSets for listings and bookings with CRUD operations
- feat(api): configure RESTful API routes with DRF router
- feat(api): add Swagger documentation for API endpoints
- feat(payment): integrate Chapa API for payment processing
- feat(payment): add payment initiation and verification endpoints
- feat(booking): integrate payment workflow with booking creation
- feat(celery): set up Celery for background email tasks
- feat(email): add booking confirmation email task
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

Payment Workflow

1. **Booking Creation**: When a user creates a booking via `POST /api/bookings/`, the system:
   - Creates the booking record
   - Creates a Payment record with status PENDING
   - Initiates payment with Chapa API
   - Returns booking details along with payment checkout URL

2. **Payment Completion**: User completes payment on Chapa's checkout page

3. **Payment Verification**: After payment, Chapa redirects to `/api/payments/verify/`:
   - System verifies payment status with Chapa API
   - Updates Payment status to COMPLETED or FAILED
   - Updates Booking status to CONFIRMED if payment successful
   - Sends confirmation email asynchronously via Celery

4. **Manual Verification**: You can manually verify payment status:
   ```
   GET /api/payments/verify/?tx_ref=<booking_reference>
   ```

Testing Payment Integration

1. **Use Chapa Sandbox**: Get test API keys from https://developer.chapa.co/
2. **Test Payment Flow**:
   - Create a booking (payment is initiated automatically)
   - Use the returned checkout_url to complete payment
   - Payment will be verified automatically via callback
   - Check email for confirmation (if email is configured)

3. **Monitor Logs**: Check Django logs and Celery worker logs for payment status updates

Celery Setup

Start Redis server:
```bash
redis-server
```

Start Celery worker:
```bash
celery -A alx_travel_app.alx_travel_app worker --loglevel=info
```

Start Celery beat (optional, for scheduled tasks):
```bash
celery -A alx_travel_app.alx_travel_app beat --loglevel=info
```

Notes
- This project uses `django-environ` for settings. Populate `.env` and keep secrets out of source control.
- Chapa API keys should be stored securely in environment variables.
- For production, configure proper email backend (SMTP, SendGrid, etc.).
- Ensure Redis is running for Celery to work.
- Test payments using Chapa's sandbox environment before going live.


