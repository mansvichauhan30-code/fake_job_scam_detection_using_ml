# Testing Strategy

## 1. Unit Testing

### Red Flag Detection (`utils/red_flags.py`)
Test each detection function in isolation with known inputs:

| Test Case | Input | Expected Output |
|---|---|---|
| Unrealistic salary - daily pay | `"50000-100000 (Daily)"` | `True` |
| Unrealistic salary - normal | `"30000-50000"` | `False` |
| No company details - empty | `""` | `True` |
| No company details - valid | `"Infosys is a leading IT company."` | `False` |
| Money request detected | `"...pay registration fee..."` | `True` |
| Suspicious email | `"tempmail.com"` | `True` |
| Valid email | `"gmail.com"` | `False` |
| Grammar issues | Text containing "guarenteed" | `True` |
| Urgency language | `"...limited seats, apply immediately!!!"` | `True` |
| Unrealistic claims | `"no experience needed, guaranteed job"` | `True` |

**Tooling:** `pytest` with test functions calling `analyze_red_flags()` and
asserting `flag['detected']` values for each of the 7 categories.

### Explanation Generator (`utils/explanation_generator.py`)
- Test that `generate_explanation()` returns a non-empty string for both
  `prediction=0` and `prediction=1`.
- Test that detected flag names appear in the explanation text when
  `flag_count > 0`.
- Test that the "Recommendation" section changes appropriately based on
  prediction.

### ML Model
- Load `fake_job_model.pkl` and `tfidf_vectorizer.pkl`.
- Run `predict_proba()` on a known fake sample → assert probability > 0.5.
- Run `predict_proba()` on a known genuine sample → assert probability < 0.5.
- Verify model output shape and class labels (`model.classes_ == [0, 1]`).

## 2. Integration Testing

### Authentication Flow
- Register a new user → verify row inserted in `users` table with hashed password.
- Attempt registration with duplicate email → expect flash error, no duplicate row.
- Login with correct credentials → verify session contains `user_id`, `full_name`, `role`.
- Login with incorrect password → expect flash error, no session created.
- Access `/dashboard` without login → expect redirect to `/login`.
- Access `/admin` as a non-admin user → expect redirect with permission error.

### Job Analysis Flow
- Submit `/analyze` form with valid fake-job-like data → expect:
  - New row in `job_analyses` with `prediction = 'FAKE'`
  - `scam_probability >= 50`
  - `red_flag_count > 0`
  - Redirect to `/report/<analysis_id>`
- Submit `/analyze` form with valid genuine-job-like data → expect:
  - `prediction = 'GENUINE'`
  - `scam_probability < 50`
- Submit `/analyze` with missing required fields (title/description) →
  expect flash error and redirect back to form.

### Dashboard & Reports
- After multiple analyses, verify `/dashboard` stat counts
  (`total_jobs`, `fake_jobs`, `genuine_jobs`) match database counts.
- Test `/reports?q=<term>` returns only rows where `job_title LIKE %term%`.
- Test `/reports?filter=FAKE` returns only rows with `prediction = 'FAKE'`.
- Test that one user cannot view another user's report via `/report/<id>`
  (should return "Report not found" since query filters by `user_id`).

### Admin Panel
- Verify `/admin` displays correct `total_users`, `total_analyses`,
  `total_fake`, `total_genuine`.
- Test `/admin/delete_user/<id>` removes the user and cascades to delete
  their `job_analyses` rows (via `ON DELETE CASCADE`).
- Verify admin cannot delete their own account.

## 3. ML Model Evaluation Testing

Run after every retraining (`train_model.py`):

| Metric | Target (sample dataset) |
|---|---|
| Accuracy | ≥ 0.85 |
| Precision (fake class) | ≥ 0.85 |
| Recall (fake class) | ≥ 0.85 |
| F1-score (fake class) | ≥ 0.85 |

> On the included synthetic 800-row dataset, the model achieves ~100%
> on these metrics because synthetic fake/genuine patterns are highly
> distinct. **When using a real-world dataset (e.g., Kaggle's 18,000-row
> dataset), expect more realistic metrics in the 85-95% range** and
> evaluate using the confusion matrix and classification report printed
> by `train_model.py`.

## 4. Frontend / UI Testing

- **Responsiveness:** Test all pages at breakpoints (mobile ≤576px, tablet
  768px, desktop ≥1200px) using browser dev tools.
- **Form validation:** Confirm required fields (`title`, `description`)
  block submission when empty; password confirmation mismatch is caught
  client-side.
- **Navigation:** Verify navbar links change based on auth state
  (logged out vs. user vs. admin).
- **Score gauge rendering:** Verify gauge color changes correctly at
  thresholds (<25% green, 25-50% amber, ≥50% red).
- **Cross-browser:** Test on Chrome, Firefox, and Edge.

## 5. Security Testing

- **SQL Injection:** Attempt injection via login/registration fields
  (e.g., `' OR '1'='1`) — should fail since all queries are parameterized.
- **Session security:** Confirm protected routes redirect when session
  cookie is cleared/tampered.
- **Password storage:** Confirm `password_hash` column never stores
  plaintext (verify via direct DB inspection).
- **Authorization:** Confirm a regular user cannot access `/admin` or
  `/admin/delete_user/<id>` routes (should redirect with "permission" flash).

## 6. Manual End-to-End Test Scenarios

| # | Scenario | Steps | Expected Result |
|---|---|---|---|
| 1 | Register → Login → Analyze fake job | Register new user, login, paste a "work from home, pay registration fee" posting | Verdict = FAKE, score ≥ 50%, multiple red flags shown |
| 2 | Analyze genuine job | Paste a real-looking IT job posting with company details and normal salary | Verdict = GENUINE, score < 50%, 0-1 red flags |
| 3 | Dashboard updates | Analyze 3 jobs (mix of fake/genuine) | Dashboard stat cards reflect correct totals |
| 4 | Search reports | Search for a keyword from a previously analyzed job title | Only matching reports shown |
| 5 | Filter reports | Filter by "Fake Only" | Only FAKE-labeled reports shown |
| 6 | Admin login | Login with seeded admin account | Redirected to `/admin`, stats and user list visible |
| 7 | Admin delete user | Delete a non-admin user | User removed from list, their reports cascade-deleted |

## Recommended Testing Tools

- **pytest** — unit and integration tests for Flask routes (using `app.test_client()`)
- **pytest-flask** — Flask-specific test fixtures
- **coverage.py** — measure test coverage
- **Selenium / Playwright** — automated UI/E2E testing (optional, advanced)
