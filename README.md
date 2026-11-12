# fake_job_scam_detection_using_ml

## JobShield AI — Fake Job Scam Detection System

A full-stack web application that helps job seekers identify whether a job
posting is **genuine** or **fraudulent** using Machine Learning and rule-based
red flag detection.

**Final Year B.Tech Computer Science Engineering Project**

---

## Table of Contents

1. [Tech Stack](#tech-stack)
2. [Folder Structure](#folder-structure)
3. [Features](#features)
4. [Setup Instructions](#setup-instructions)
5. [Training the ML Model](#training-the-ml-model)
6. [Running the Application](#running-the-application)
7. [Admin Login](#admin-login)
8. [API Endpoints](#api-endpoints)
9. [Project Documentation](#project-documentation)

---

## Tech Stack

| Layer          | Technology                                |
|-----------------|--------------------------------------------|
| Frontend        | HTML5, CSS3, JavaScript, Bootstrap 5        |
| Backend         | Python, Flask                               |
| Database        | MySQL                                       |
| Machine Learning| Scikit-learn (Logistic Regression + TF-IDF), Pandas, NumPy |

---

## Folder Structure

```
fake-job-detector/
│
├── app/                            # Flask application
│   ├── app.py                      # Main Flask app (routes, logic)
│   ├── config.py                   # Configuration (DB credentials, paths)
│   ├── db.py                       # MySQL connection helper
│   ├── seed_admin.py                # Script to create default admin user
│   │
│   ├── models/                     # Trained ML model files (.pkl)
│   │   ├── fake_job_model.pkl
│   │   └── tfidf_vectorizer.pkl
│   │
│   ├── utils/                      # Helper modules
│   │   ├── red_flags.py            # Rule-based red flag detection
│   │   └── explanation_generator.py # AI-style explanation generator
│   │
│   ├── templates/                  # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── register.html
│   │   ├── login.html
│   │   ├── analyze.html
│   │   ├── report.html
│   │   ├── dashboard.html
│   │   ├── reports.html
│   │   ├── admin.html
│   │   ├── 404.html
│   │   └── 500.html
│   │
│   └── static/
│       ├── css/style.css
│       ├── js/main.js
│       └── images/
│
├── ml/                              # Machine Learning pipeline
│   ├── train_model.py               # Model training script
│   ├── dataset/
│   │   ├── generate_dataset.py      # Generates sample dataset
│   │   └── fake_job_postings.csv    # Sample training dataset (800 rows)
│   └── model/                       # Output of training (copied to app/models)
│       ├── fake_job_model.pkl
│       └── tfidf_vectorizer.pkl
│
├── database/
│   └── schema.sql                   # MySQL database schema
│
├── docs/                            # Project documentation
│   ├── ER_DIAGRAM.md
│   ├── ARCHITECTURE.md
│   ├── FLOWCHART.md
│   ├── API_ENDPOINTS.md
│   ├── TESTING_STRATEGY.md
│   ├── FUTURE_ENHANCEMENTS.md
│   ├── RESUME_DESCRIPTION.md
│   └── VIVA_QUESTIONS.md
│
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

---

## Features

1. **User Registration & Login** — Secure session-based authentication with password hashing.
2. **Job Posting Analysis** — Submit job details via a form.
3. **Fake Job Detection using ML** — TF-IDF + Logistic Regression model trained on labeled data.
4. **Scam Probability Score (0–100%)** — Combined ML + red-flag weighted score.
5. **Red Flag Detection** — Unrealistic salary, missing company details, money requests, suspicious email domains, grammar/spelling issues, urgency tactics, unrealistic claims.
6. **AI-Generated Explanation** — Plain-English reasoning for the verdict.
7. **Dashboard** — Total analyzed, fake count, genuine count, recent analyses.
8. **Search & Filter Reports** — By job title and verdict.
9. **Admin Panel** — User management and system-wide statistics.
10. **Responsive Modern UI** — Built with Bootstrap 5, custom theme.

---

## Setup Instructions

### Prerequisites
- Python 3.10+
- MySQL Server 8.0+
- pip

### 1. Clone / Extract Project

```bash
cd fake-job-detector
```

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up MySQL Database

Log into MySQL and run the schema file:

```bash
mysql -u root -p < database/schema.sql
```

This creates the `fake_job_detection` database with all required tables
and seeds the `red_flag_master` reference table.

### 5. Configure Environment Variables

Set your local MySQL credentials and a session secret in the terminal where
you will run the app. In PowerShell:

```powershell
$env:MYSQL_HOST = "localhost"
$env:MYSQL_USER = "root"
$env:MYSQL_PASSWORD = "your-local-mysql-password"
$env:MYSQL_DB = "fake_job_detection"
$env:MYSQL_PORT = "3306"
$env:SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
```

In Bash:

```bash
export MYSQL_HOST=localhost
export MYSQL_USER=root
export MYSQL_PASSWORD=your-local-mysql-password
export MYSQL_DB=fake_job_detection
export MYSQL_PORT=3306
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
```

Do not commit passwords or production secrets. The app generates a temporary
session secret if `SECRET_KEY` is not set; configure a stable secret through
the environment for deployments.

### 6. Create an Admin User

Set a strong admin password in the same terminal before running the seeder.
In PowerShell:

```powershell
$env:ADMIN_PASSWORD = "your-strong-admin-password"
$env:ADMIN_EMAIL = "admin@jobshield.com"
Set-Location app
python seed_admin.py
```

The admin email can be changed with `ADMIN_EMAIL`. The seeder does not use or
print a default password.

---

## Training the ML Model

The pre-trained model is already included in `app/models/`. To retrain
(or train on a different dataset):

```bash
cd ml
python dataset/generate_dataset.py     # Generates fake_job_postings.csv (optional, sample already included)
python train_model.py                  # Trains and saves model + vectorizer
```

After training, copy the new model files into the app:

```bash
cp ml/model/*.pkl app/models/
```

> **Note:** For better real-world accuracy, replace/augment the sample
> dataset with the Kaggle "Real or Fake Job Posting Prediction" dataset
> (~18,000 real-world labeled postings).

---

## Running the Application

```bash
cd app
python app.py
```

The app will start on **http://localhost:5000**

Open your browser and navigate to that URL.

---

## Admin Login

Use the email and password supplied when creating the admin account.

---

## API Endpoints

See [`docs/API_ENDPOINTS.md`](docs/API_ENDPOINTS.md) for the full list of
routes and the JSON API endpoint for programmatic job analysis.

---

## Project Documentation

| Document | Description |
|----------|--------------|
| [ER Diagram](docs/ER_DIAGRAM.md) | Entity-Relationship diagram and database design |
| [Architecture](docs/ARCHITECTURE.md) | System architecture overview |
| [Flowchart](docs/FLOWCHART.md) | Application flow and ML pipeline flowchart |
| [API Endpoints](docs/API_ENDPOINTS.md) | List of all routes and JSON API |
| [Testing Strategy](docs/TESTING_STRATEGY.md) | Unit, integration, and ML model testing approach |
| [Future Enhancements](docs/FUTURE_ENHANCEMENTS.md) | Planned improvements |
| [Resume Description](docs/RESUME_DESCRIPTION.md) | Ready-to-use resume bullet points |
| [Viva Questions](docs/VIVA_QUESTIONS.md) | Common viva/interview questions and answers |

---

## License

This project was built for educational purposes as a final-year academic
project. Free to use and modify.
