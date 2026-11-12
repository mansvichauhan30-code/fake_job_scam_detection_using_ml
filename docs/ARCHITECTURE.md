# Project Architecture

## High-Level Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                          CLIENT (Browser)                          │
│  HTML5 + CSS3 + Bootstrap 5 + Vanilla JS                            │
│  Pages: Landing, Register, Login, Analyze, Report, Dashboard,      │
│         Reports, Admin                                              │
└───────────────────────────┬──────────────────────────────────────┘
                              │ HTTP (GET/POST forms, AJAX/JSON)
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                     APPLICATION LAYER (Flask)                       │
│                                                                       │
│  ┌───────────────┐   ┌───────────────────┐   ┌───────────────────┐│
│  │ Auth Module    │   │ Job Analysis Module │   │ Admin Module      ││
│  │ - Register     │   │ - Form handling     │   │ - User mgmt       ││
│  │ - Login        │   │ - Orchestrates ML    │   │ - Stats           ││
│  │ - Session mgmt │   │   + Red Flags        │   │                   ││
│  └───────────────┘   └─────────┬─────────────┘   └───────────────────┘│
│                                  │                                       │
│         ┌────────────────────────┼────────────────────────┐          │
│         ▼                        ▼                          ▼          │
│  ┌─────────────┐        ┌─────────────────┐       ┌──────────────────┐│
│  │ red_flags.py │        │ ML Model         │       │ explanation_     ││
│  │ (rule-based  │        │ (TF-IDF +        │       │ generator.py     ││
│  │  detection)  │        │  Logistic Reg.)  │       │ (AI explanation) ││
│  └─────────────┘        └─────────────────┘       └──────────────────┘│
└───────────────────────────┬──────────────────────────────────────┘
                              │ SQL (mysql-connector-python)
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│                       DATA LAYER (MySQL)                            │
│  Tables: users | job_analyses | red_flag_master                     │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                  ML TRAINING PIPELINE (Offline)                      │
│  dataset/generate_dataset.py → fake_job_postings.csv                │
│           → train_model.py → TF-IDF Vectorizer + Logistic Regression│
│           → fake_job_model.pkl + tfidf_vectorizer.pkl               │
│           → loaded by Flask app at runtime                          │
└──────────────────────────────────────────────────────────────────┘
```

## Layer Responsibilities

### 1. Presentation Layer (Frontend)
- **Technology:** HTML5, CSS3 (custom theme), Bootstrap 5, vanilla JavaScript
- **Responsibility:** Rendering forms, dashboards, reports; client-side validation; responsive layout across devices.
- **Rendering:** Server-side rendering via Jinja2 templates (`app/templates/`).

### 2. Application Layer (Backend — Flask)
- **`app.py`** — central Flask app containing all route handlers (controllers).
- **`config.py`** — centralized configuration (DB credentials, model paths).
- **`db.py`** — database access layer abstracting MySQL connections and query execution.
- **`utils/red_flags.py`** — rule-based detection engine for the 7 red flag categories.
- **`utils/explanation_generator.py`** — template-based natural language explanation generator.

### 3. Machine Learning Layer
- **Feature extraction:** TF-IDF vectorization of combined job text (title, description, requirements, company profile, salary, location).
- **Model:** Logistic Regression classifier (`class_weight='balanced'`) trained on labeled fake/genuine postings.
- **Output:** Probability of the "fake" class (0–1), scaled to 0–100%.
- **Persistence:** Model and vectorizer serialized with `joblib` and loaded once at Flask app startup for low-latency inference.

### 4. Scoring & Decision Layer
The final **Scam Probability Score** is a weighted combination:

```
final_score = (0.7 × ML_model_probability) + (0.3 × red_flag_ratio × 100)
```

- ML model contributes 70% (captures language patterns, semantics).
- Rule-based red flags contribute 30% (captures explicit, explainable scam indicators).
- Threshold: score ≥ 50% → classified as **FAKE**, else **GENUINE**.

### 5. Data Layer (MySQL)
- **`users`** — authentication and role management.
- **`job_analyses`** — stores every submission with full results (denormalized red flags as JSON for flexibility).
- **`red_flag_master`** — lookup table for flag metadata.

## Request Flow Example: Analyzing a Job Posting

```
User submits form (POST /analyze)
        │
        ▼
Flask route `analyze()`
        │
        ├──► red_flags.analyze_red_flags(job_data)
        │         → returns list of 7 flags + count
        │
        ├──► vectorizer.transform(combined_text)
        │         → model.predict_proba(...)
        │         → ML scam probability
        │
        ├──► Combine scores → final_score, prediction label
        │
        ├──► explanation_generator.generate_explanation(...)
        │         → natural language explanation
        │
        ├──► db.execute_query(INSERT INTO job_analyses ...)
        │         → analysis_id
        │
        ▼
Redirect to /report/<analysis_id>
        │
        ▼
Render report.html with score gauge, verdict, flags, explanation
```

## Security Considerations
- Passwords hashed using Werkzeug's `generate_password_hash` (PBKDF2).
- Session-based authentication with Flask's signed session cookies (`SECRET_KEY`).
- SQL queries use parameterized statements (`%s` placeholders) to prevent SQL injection.
- Role-based access control (`login_required`, `admin_required` decorators) for protected routes.
- Each user can only view their own reports (`WHERE user_id = %s` filter).
