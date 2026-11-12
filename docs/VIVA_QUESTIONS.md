# Viva Questions and Answers

## General Project Questions

**Q1. What is the objective of this project?**
A: The project aims to help job seekers identify whether a job posting is
genuine or fraudulent. It uses a Machine Learning model combined with
rule-based red flag detection to produce a scam probability score (0-100%)
and a plain-English explanation, helping users avoid job scams that often
ask for money or personal information.

**Q2. What problem does this project solve in the real world?**
A: Job scams are extremely common — fraudsters post fake "work from home"
or "data entry" jobs promising high pay with no experience, then ask
victims to pay registration/processing fees or share sensitive personal
data (Aadhar, bank details). This system gives job seekers an instant,
automated way to check a posting's legitimacy before they engage with it.

**Q3. What is the technology stack used?**
A: Frontend — HTML5, CSS3, JavaScript, Bootstrap 5. Backend — Python Flask.
Database — MySQL. Machine Learning — Scikit-learn (TF-IDF + Logistic
Regression), Pandas, NumPy.

**Q4. Why did you choose Flask over Django?**
A: Flask is lightweight and gives fine-grained control over routing,
database access, and ML model integration without imposing a rigid
project structure. For a project of this scope — a few pages plus an ML
inference pipeline — Flask's minimalism made it easier to integrate
`joblib`-loaded models directly into route handlers without extra
boilerplate.

## Machine Learning Questions

**Q5. How does the ML model classify a job as fake or genuine?**
A: All text fields (title, description, requirements, company profile,
salary, location) are concatenated into a single text string. This text
is converted into numerical features using **TF-IDF (Term
Frequency–Inverse Document Frequency)** vectorization with unigrams and
bigrams. The vectorized features are fed into a **Logistic Regression**
classifier, which outputs a probability that the posting belongs to the
"fake" class.

**Q6. What is TF-IDF and why did you use it?**
A: TF-IDF is a technique that converts text into numeric vectors by
weighing words based on how frequently they appear in a document (Term
Frequency) versus how common they are across all documents (Inverse
Document Frequency). Words that are common across many fake postings but
rare in genuine ones (e.g., "guaranteed", "registration fee") get
distinguishing weight. It's simple, fast, interpretable, and works well
for short-text classification tasks without needing GPU-based deep
learning.

**Q7. Why Logistic Regression and not a more complex model like a neural network?**
A: Logistic Regression is well-suited for high-dimensional, sparse text
features (like TF-IDF output), trains quickly, is interpretable
(coefficients show word importance), and performs competitively for
binary text classification on moderately sized datasets. A deep learning
model would require significantly more data and compute for marginal
gains in this context.

**Q8. How is the dataset structured?**
A: Each row represents a job posting with columns: `title`,
`company_profile`, `description`, `requirements`, `salary`,
`company_email_domain`, `location`, and a binary label `fraudulent`
(1 = fake, 0 = genuine). The sample dataset contains 800 synthetically
generated rows (400 genuine, 400 fake) modeled on common real-world
patterns.

**Q9. How did you evaluate the model?**
A: Using an 80/20 train-test split with stratification to preserve class
balance. Evaluation metrics include **accuracy, precision, recall, F1-score,
and a confusion matrix**, all printed by `train_model.py`.

**Q10. What is `class_weight='balanced'` and why is it used?**
A: It automatically adjusts the weight given to each class inversely
proportional to its frequency in the training data, which helps prevent
the model from being biased toward the majority class — important if the
dataset has more genuine postings than fake ones (as real-world data
often does).

**Q11. How is the final scam probability score calculated?**
A: It's a weighted combination:
`final_score = 0.7 × (ML model's fake probability) + 0.3 × (red_flag_count / 7 × 100)`.
This blends the model's learned language-pattern detection (70% weight)
with explicit, explainable rule-based red flags (30% weight). A score
≥ 50% results in a "FAKE" verdict.

**Q12. What are the 7 red flags your system checks?**
A: (1) Unrealistic Salary, (2) No Company Details, (3) Asking for Money,
(4) Suspicious Email Domain, (5) Grammar/Spelling Issues, (6) Urgency/
Pressure Tactics, and (7) Unrealistic Claims (e.g., "no experience needed,
guaranteed job").

**Q13. How does the system generate the AI explanation?**
A: A template-based natural language generator (`explanation_generator.py`)
constructs a human-readable explanation by combining the prediction label,
the scam probability score, and the specific red flags detected, listing
each triggered flag with its description and a tailored recommendation.

## Database Questions

**Q14. Describe your database schema.**
A: There are three tables: `users` (stores user accounts with hashed
passwords and roles), `job_analyses` (stores every analysis with the job
details, ML prediction, scam score, explanation, and red flags as JSON),
and `red_flag_master` (a reference table listing the 7 red flag types).
`job_analyses.user_id` is a foreign key referencing `users.user_id` with
`ON DELETE CASCADE`.

**Q15. Why did you store red flags as JSON instead of a separate table?**
A: The red flags for each analysis are a fixed set of 7 boolean checks
computed at analysis time — they're not independent entities with their
own lifecycle. Storing them as a JSON array within `job_analyses` avoids
an unnecessary join while keeping the structure flexible if more flag
types are added later. `red_flag_master` separately documents the
canonical flag names/descriptions for consistency.

**Q16. How do you prevent SQL injection?**
A: All SQL queries use parameterized placeholders (`%s`) via
`mysql-connector-python`, so user input is never directly concatenated
into SQL strings.

## Security Questions

**Q17. How are passwords stored securely?**
A: Passwords are hashed using Werkzeug's `generate_password_hash()`
(PBKDF2 with salt) before storage. Plaintext passwords are never stored
or logged. Login verifies via `check_password_hash()`.

**Q18. How does your application manage user sessions?**
A: Flask's built-in session mechanism stores `user_id`, `full_name`, and
`role` in a signed cookie (signed using `SECRET_KEY`). The
`login_required` and `admin_required` decorators check for `user_id` in
the session and the user's role before granting access to protected
routes.

**Q19. How do you ensure one user cannot view another user's reports?**
A: The `/report/<analysis_id>` route filters the database query with
`WHERE analysis_id = %s AND user_id = %s`, so a report only loads if it
belongs to the logged-in user; otherwise, "Report not found" is shown.

## Frontend Questions

**Q20. How is the UI made responsive?**
A: Using Bootstrap 5's grid system (`row`/`col-*`) and responsive utility
classes, combined with custom CSS media queries for the score gauge and
hero section at smaller breakpoints.

**Q21. How does the scam probability "gauge" work visually?**
A: It's a CSS `conic-gradient` on a circular `div`, where the gradient
angle is driven by a CSS variable (`--score-pct`) set inline from the
Jinja template based on the analysis's `scam_probability`. The color
changes (green/amber/red) based on score thresholds.

## Project Management / Conceptual Questions

**Q22. What were the main challenges you faced?**
A: Balancing ML model output with rule-based detection so neither
dominates unfairly; designing a dataset that captures realistic scam
language patterns; and ensuring the explanation generator produces
genuinely useful, non-repetitive text for different combinations of
flags and scores.

**Q23. How would you improve accuracy with real-world data?**
A: Train on the Kaggle "Real or Fake Job Posting Prediction" dataset
(~18,000 real postings), use cross-validation for hyperparameter tuning,
experiment with ensemble models (Random Forest, Gradient Boosting), and
potentially incorporate word embeddings (Word2Vec/BERT) for richer
semantic features.

**Q24. Is this system scalable for production use?**
A: The current architecture (Flask + MySQL + joblib model) handles
moderate traffic well since the model is loaded once at startup and
inference is fast. For higher scale, the application could be containerized,
deployed behind a load balancer with multiple Flask workers (Gunicorn),
and the database moved to a managed cloud MySQL instance with read
replicas.

**Q25. What is the difference between precision and recall in this context, and which matters more?**
A: Precision = of all postings flagged as fake, how many are actually
fake. Recall = of all actually fake postings, how many were correctly
flagged. In a scam detection system, **recall is often more critical** —
missing a fake posting (false negative) could lead a user to lose money
or share sensitive data, whereas a false positive (flagging a genuine job
as suspicious) merely causes extra caution. The `class_weight='balanced'`
setting and threshold tuning (50%) can be adjusted to favor recall if
needed.
