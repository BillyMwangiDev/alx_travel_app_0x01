# API Testing Guide for ALX Travel App

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Seed the database (optional):**
   ```bash
   python manage.py seed --listings 5 --bookings-per-listing 2 --reviews-per-listing 2
   ```

4. **Start the development server:**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/api/`

## API Endpoints

### Base URL
- Development: `http://localhost:8000/api/`

### Listings Endpoints

#### 1. List All Listings
- **Method:** `GET`
- **URL:** `http://localhost:8000/api/listings/`
- **Description:** Retrieve a paginated list of all listings (10 per page)
- **Response:** JSON array of listing objects

#### 2. Create a Listing
- **Method:** `POST`
- **URL:** `http://localhost:8000/api/listings/`
- **Headers:** `Content-Type: application/json`
- **Body:**
  ```json
  {
    "title": "Cozy Apartment in Downtown",
    "description": "Beautiful 2-bedroom apartment with modern amenities",
    "location": "New York, NY",
    "price_per_night": "150.00",
    "max_guests": 4
  }
  ```

#### 3. Retrieve a Specific Listing
- **Method:** `GET`
- **URL:** `http://localhost:8000/api/listings/{id}/`
- **Example:** `http://localhost:8000/api/listings/1/`

#### 4. Update a Listing (Full Update)
- **Method:** `PUT`
- **URL:** `http://localhost:8000/api/listings/{id}/`
- **Headers:** `Content-Type: application/json`
- **Body:** Complete listing object with all fields

#### 5. Partially Update a Listing
- **Method:** `PATCH`
- **URL:** `http://localhost:8000/api/listings/{id}/`
- **Headers:** `Content-Type: application/json`
- **Body:** Partial listing object with only fields to update
  ```json
  {
    "price_per_night": "175.00"
  }
  ```

#### 6. Delete a Listing
- **Method:** `DELETE`
- **URL:** `http://localhost:8000/api/listings/{id}/`

#### 7. Get Bookings for a Listing
- **Method:** `GET`
- **URL:** `http://localhost:8000/api/listings/{id}/bookings/`
- **Example:** `http://localhost:8000/api/listings/1/bookings/`

### Bookings Endpoints

#### 1. List All Bookings
- **Method:** `GET`
- **URL:** `http://localhost:8000/api/bookings/`
- **Query Parameters:**
  - `listing_id` (optional): Filter bookings by listing ID
  - Example: `http://localhost:8000/api/bookings/?listing_id=1`

#### 2. Create a Booking
- **Method:** `POST`
- **URL:** `http://localhost:8000/api/bookings/`
- **Headers:** `Content-Type: application/json`
- **Body:**
  ```json
  {
    "listing": 1,
    "guest_name": "John Doe",
    "guest_email": "john@example.com",
    "start_date": "2024-06-01",
    "end_date": "2024-06-05",
    "total_price": "600.00",
    "status": "PENDING"
  }
  ```
- **Note:** `status` can be: `PENDING`, `CONFIRMED`, or `CANCELLED`

#### 3. Retrieve a Specific Booking
- **Method:** `GET`
- **URL:** `http://localhost:8000/api/bookings/{id}/`
- **Example:** `http://localhost:8000/api/bookings/1/`

#### 4. Update a Booking (Full Update)
- **Method:** `PUT`
- **URL:** `http://localhost:8000/api/bookings/{id}/`
- **Headers:** `Content-Type: application/json`
- **Body:** Complete booking object with all fields

#### 5. Partially Update a Booking
- **Method:** `PATCH`
- **URL:** `http://localhost:8000/api/bookings/{id}/`
- **Headers:** `Content-Type: application/json`
- **Body:** Partial booking object
  ```json
  {
    "status": "CONFIRMED"
  }
  ```

#### 6. Delete a Booking
- **Method:** `DELETE`
- **URL:** `http://localhost:8000/api/bookings/{id}/`

## Testing with Postman

### Postman Collection Setup

1. **Create a new Collection:** "ALX Travel App API"

2. **Set Collection Variables:**
   - `base_url`: `http://localhost:8000/api`

### Example Requests

#### Create a Listing
1. Create a new request in Postman
2. Set method to `POST`
3. URL: `{{base_url}}/listings/`
4. Headers: `Content-Type: application/json`
5. Body (raw JSON):
   ```json
   {
     "title": "Beachfront Villa",
     "description": "Luxurious villa with ocean view",
     "location": "Miami, FL",
     "price_per_night": "300.00",
     "max_guests": 6
   }
   ```
6. Click "Send"

#### Get All Listings
1. Method: `GET`
2. URL: `{{base_url}}/listings/`
3. Click "Send"

#### Create a Booking
1. Method: `POST`
2. URL: `{{base_url}}/bookings/`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
   ```json
   {
     "listing": 1,
     "guest_name": "Jane Smith",
     "guest_email": "jane@example.com",
     "start_date": "2024-07-01",
     "end_date": "2024-07-07",
     "total_price": "2100.00",
     "status": "PENDING"
   }
   ```

#### Update Booking Status
1. Method: `PATCH`
2. URL: `{{base_url}}/bookings/1/`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
   ```json
   {
     "status": "CONFIRMED"
   }
   ```

#### Delete a Listing
1. Method: `DELETE`
2. URL: `{{base_url}}/listings/1/`
3. Click "Send"

## Testing with cURL

### Create a Listing
```bash
curl -X POST http://localhost:8000/api/listings/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mountain Cabin",
    "description": "Cozy cabin in the mountains",
    "location": "Aspen, CO",
    "price_per_night": "200.00",
    "max_guests": 4
  }'
```

### Get All Listings
```bash
curl http://localhost:8000/api/listings/
```

### Get a Specific Listing
```bash
curl http://localhost:8000/api/listings/1/
```

### Create a Booking
```bash
curl -X POST http://localhost:8000/api/bookings/ \
  -H "Content-Type: application/json" \
  -d '{
    "listing": 1,
    "guest_name": "Bob Johnson",
    "guest_email": "bob@example.com",
    "start_date": "2024-08-01",
    "end_date": "2024-08-05",
    "total_price": "800.00",
    "status": "PENDING"
  }'
```

### Get Bookings for a Listing
```bash
curl http://localhost:8000/api/listings/1/bookings/
```

### Filter Bookings by Listing
```bash
curl http://localhost:8000/api/bookings/?listing_id=1
```

### Update a Listing
```bash
curl -X PATCH http://localhost:8000/api/listings/1/ \
  -H "Content-Type: application/json" \
  -d '{
    "price_per_night": "250.00"
  }'
```

### Delete a Booking
```bash
curl -X DELETE http://localhost:8000/api/bookings/1/
```

## API Documentation

### Swagger UI
Access interactive API documentation at:
- **URL:** `http://localhost:8000/swagger/`

### ReDoc
Access alternative API documentation at:
- **URL:** `http://localhost:8000/redoc/`

### OpenAPI Schema
- **JSON:** `http://localhost:8000/swagger.json`
- **YAML:** `http://localhost:8000/swagger.yaml`

## Expected Response Formats

### Listing Object
```json
{
  "id": 1,
  "title": "Cozy Apartment",
  "description": "Beautiful apartment",
  "location": "New York, NY",
  "price_per_night": "150.00",
  "max_guests": 4,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Booking Object
```json
{
  "id": 1,
  "listing": 1,
  "guest_name": "John Doe",
  "guest_email": "john@example.com",
  "start_date": "2024-06-01",
  "end_date": "2024-06-05",
  "total_price": "600.00",
  "status": "PENDING",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Paginated Response
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/listings/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Listing 1",
      ...
    },
    ...
  ]
}
```

## Error Responses

### Validation Error (400)
```json
{
  "field_name": [
    "Error message describing the validation issue."
  ]
}
```

### Not Found (404)
```json
{
  "detail": "Not found."
}
```

## Testing Checklist

- [ ] GET /api/listings/ - List all listings
- [ ] POST /api/listings/ - Create a new listing
- [ ] GET /api/listings/{id}/ - Retrieve a specific listing
- [ ] PUT /api/listings/{id}/ - Full update a listing
- [ ] PATCH /api/listings/{id}/ - Partial update a listing
- [ ] DELETE /api/listings/{id}/ - Delete a listing
- [ ] GET /api/listings/{id}/bookings/ - Get bookings for a listing
- [ ] GET /api/bookings/ - List all bookings
- [ ] GET /api/bookings/?listing_id=1 - Filter bookings by listing
- [ ] POST /api/bookings/ - Create a new booking
- [ ] GET /api/bookings/{id}/ - Retrieve a specific booking
- [ ] PUT /api/bookings/{id}/ - Full update a booking
- [ ] PATCH /api/bookings/{id}/ - Partial update a booking
- [ ] DELETE /api/bookings/{id}/ - Delete a booking
- [ ] Access Swagger documentation at /swagger/
- [ ] Access ReDoc documentation at /redoc/

