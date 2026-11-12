# API Endpoints

All routes are defined in `app/app.py`. Routes marked **Auth Required**
need an active session (`login_required`). Routes marked **Admin Only**
need `role = 'admin'` (`admin_required`).

## Page Routes (HTML, Server-Rendered)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/` | Public | Landing page with feature overview |
| GET, POST | `/register` | Public | User registration form & submission |
| GET, POST | `/login` | Public | User login form & submission |
| GET | `/logout` | Auth Required | Clears session and logs out |
| GET, POST | `/analyze` | Auth Required | Job posting analysis form & processing |
| GET | `/report/<int:analysis_id>` | Auth Required | View a single analysis report |
| GET | `/dashboard` | Auth Required | User dashboard with stats and recent analyses |
| GET | `/reports` | Auth Required | Search & filter past reports |
| GET | `/admin` | Admin Only | Admin dashboard with system stats |
| POST | `/admin/delete_user/<int:user_id>` | Admin Only | Delete a user and their reports (cascade) |

## JSON API Endpoint

### `POST /api/analyze`

**Auth Required.** Accepts a JSON payload describing a job posting and
returns the ML prediction, scam probability, red flags, and AI explanation
without persisting to the database. Useful for AJAX-based front-end widgets
or external integrations (e.g., browser extension).

**Request Body:**
```json
{
  "title": "Software Engineer - Backend",
  "company_profile": "Infosys is a leading IT services company.",
  "description": "We are looking for a skilled Software Engineer...",
  "requirements": "Bachelor's degree in CS, 1-3 years experience",
  "salary": "30000-50000",
  "company_email_domain": "company.com",
  "location": "Pune, India"
}
```

**Response Body:**
```json
{
  "prediction": "GENUINE",
  "scam_probability": 3.72,
  "red_flags": [
    {
      "name": "Unrealistic Salary",
      "detected": false,
      "description": "The salary offered seems unrealistically high or vague for the role described."
    },
    {
      "name": "No Company Details",
      "detected": false,
      "description": "The company profile is missing, too short, or not specified."
    }
    // ... 5 more flags
  ],
  "explanation": "Based on our analysis, the job posting \"Software Engineer - Backend\" appears to be a GENUINE job posting..."
}
```

**Example cURL:**
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -b "session=<your_session_cookie>" \
  -d '{
        "title": "Online Data Entry Job",
        "company_profile": "",
        "description": "Earn Rs 50000 weekly! No experience needed! Pay Rs 500 registration fee.",
        "requirements": "Anyone can apply",
        "salary": "50000 weekly",
        "company_email_domain": "tempmail.com",
        "location": "Work From Home"
      }'
```

## Form Fields Reference (`/analyze`)

| Field Name | Required | Description |
|---|---|---|
| `title` | Yes | Job title |
| `company_profile` | No | Company description from posting |
| `description` | Yes | Full job description |
| `requirements` | No | Skills/qualifications |
| `salary` | No | Salary/pay as written in posting |
| `company_email_domain` | No | Recruiter email domain (e.g., gmail.com) |
| `location` | No | Job location |

## Query Parameters (`/reports`)

| Parameter | Values | Description |
|---|---|---|
| `q` | string | Search term matched against `job_title` (LIKE %term%) |
| `filter` | `all`, `FAKE`, `GENUINE` | Filter results by verdict |

Example: `/reports?q=data+entry&filter=FAKE`

## HTTP Status Codes

| Code | Meaning |
|---|---|
| 200 | Success |
| 302 | Redirect (e.g., after login/logout/form submission) |
| 404 | Page/resource not found (custom `404.html`) |
| 500 | Internal server error (custom `500.html`) |
