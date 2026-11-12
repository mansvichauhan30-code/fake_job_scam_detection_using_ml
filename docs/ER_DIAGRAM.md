# ER Diagram & Database Design

## Entity-Relationship Diagram (Text Representation)

```
┌────────────────────────────┐
│           USERS             │
├──────────────────────────────┤
│ PK  user_id        INT       │
│     full_name      VARCHAR   │
│     email          VARCHAR(U)│
│     password_hash  VARCHAR   │
│     role           ENUM      │
│     created_at     TIMESTAMP │
└──────────────┬───────────────┘
               │ 1
               │
               │ has many
               │
               │ M
┌──────────────▼────────────────────────┐
│            JOB_ANALYSES                │
├──────────────────────────────────────────┤
│ PK  analysis_id        INT               │
│ FK  user_id            INT  → users.user_id │
│     job_title          VARCHAR(200)      │
│     company_profile    TEXT              │
│     job_description    TEXT              │
│     requirements       TEXT              │
│     salary             VARCHAR(100)      │
│     company_email_domain VARCHAR(100)    │
│     location           VARCHAR(150)      │
│     prediction          ENUM(FAKE/GENUINE)│
│     scam_probability    DECIMAL(5,2)     │
│     ai_explanation      TEXT             │
│     red_flags            JSON            │
│     red_flag_count       INT             │
│     created_at           TIMESTAMP       │
└──────────────────────────────────────────┘


┌──────────────────────────────────┐
│         RED_FLAG_MASTER           │
├──────────────────────────────────┤
│ PK  flag_id          INT          │
│     flag_name        VARCHAR(100) │
│     flag_description TEXT         │
└──────────────────────────────────┘
(Reference table — not directly FK-linked;
 used for consistent flag naming/reporting)
```

## Relationship Summary

| Relationship | Type | Description |
|---|---|---|
| `users` → `job_analyses` | One-to-Many | One user can submit many job analyses. Each analysis belongs to exactly one user. |
| `red_flag_master` | Standalone reference | Provides canonical names/descriptions for the 7 red flag types used across the system. |

## Table Descriptions

### `users`
Stores registered job seekers and admin accounts.

| Column | Type | Constraints | Description |
|---|---|---|---|
| user_id | INT | PK, AUTO_INCREMENT | Unique user identifier |
| full_name | VARCHAR(100) | NOT NULL | User's display name |
| email | VARCHAR(150) | UNIQUE, NOT NULL | Login email |
| password_hash | VARCHAR(255) | NOT NULL | Werkzeug-hashed password |
| role | ENUM('user','admin') | DEFAULT 'user' | Access control role |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Account creation time |

### `job_analyses`
Stores every job posting submitted for analysis along with the ML/red-flag results.

| Column | Type | Constraints | Description |
|---|---|---|---|
| analysis_id | INT | PK, AUTO_INCREMENT | Unique report identifier |
| user_id | INT | FK → users.user_id | Owner of the analysis |
| job_title | VARCHAR(200) | NOT NULL | Title of the job posting |
| company_profile | TEXT | | Company description provided |
| job_description | TEXT | NOT NULL | Full job description text |
| requirements | TEXT | | Skills/qualifications text |
| salary | VARCHAR(100) | | Salary/pay range as entered |
| company_email_domain | VARCHAR(100) | | Recruiter email domain |
| location | VARCHAR(150) | | Job location |
| prediction | ENUM('FAKE','GENUINE') | NOT NULL | Final classification |
| scam_probability | DECIMAL(5,2) | NOT NULL | 0.00–100.00 score |
| ai_explanation | TEXT | | Generated explanation text |
| red_flags | JSON | | Array of {name, detected, description} |
| red_flag_count | INT | DEFAULT 0 | Number of flags triggered (0-7) |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Analysis timestamp |

### `red_flag_master`
Reference table listing the 7 canonical red flag types.

| Column | Type | Description |
|---|---|---|
| flag_id | INT (PK) | Identifier |
| flag_name | VARCHAR(100) | e.g. "Unrealistic Salary" |
| flag_description | TEXT | Human-readable description |

## Indexes

- `idx_job_analyses_user` on `job_analyses(user_id)` — speeds up dashboard/report queries per user.
- `idx_job_analyses_prediction` on `job_analyses(prediction)` — speeds up fake/genuine count aggregation.
- `idx_job_analyses_created` on `job_analyses(created_at)` — speeds up recent-analyses ordering.

## Normalization Notes

The schema is in **3NF**:
- No repeating groups (red flags stored as JSON array for flexibility, since they represent a fixed set of 7 boolean checks computed per analysis — not an independent entity requiring its own table).
- All non-key attributes depend only on the primary key of their table.
- `red_flag_master` is kept separate as a lookup/reference table to avoid hardcoding flag descriptions across the codebase.
