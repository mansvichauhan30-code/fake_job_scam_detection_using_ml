# Flowcharts

## 1. Overall Application Flow

```
                        ┌─────────────┐
                        │    Start     │
                        └──────┬───────┘
                                ▼
                        ┌──────────────┐
                        │ Landing Page  │
                        └──────┬───────┘
                                ▼
                    ┌────────────────────┐
                    │ Logged in already?  │
                    └─────┬──────────┬────┘
                       No │          │ Yes
                          ▼          ▼
                ┌──────────────┐  ┌──────────────┐
                │ Register/Login│  │  Dashboard    │
                └──────┬────────┘  └──────┬───────┘
                       │                   │
                       └─────────┬─────────┘
                                  ▼
                         ┌──────────────────┐
                         │  Analyze Job Page  │
                         └─────────┬─────────┘
                                    ▼
                         ┌──────────────────────┐
                         │ Submit job posting form │
                         └─────────┬─────────────┘
                                    ▼
                         ┌──────────────────────┐
                         │  Backend Processing     │
                         │  (see ML Pipeline below) │
                         └─────────┬─────────────┘
                                    ▼
                         ┌──────────────────────┐
                         │  Save result to DB      │
                         └─────────┬─────────────┘
                                    ▼
                         ┌──────────────────────┐
                         │  Show Report Page       │
                         │  (Score, Verdict,        │
                         │   Red Flags, Explanation)│
                         └─────────┬─────────────┘
                                    ▼
                  ┌─────────────────────────────────┐
                  │ User can: View Dashboard,         │
                  │ Search Reports, Analyze Another    │
                  └─────────┬─────────────────────────┘
                              ▼
                        ┌──────────┐
                        │   End     │
                        └──────────┘
```

## 2. ML Detection Pipeline (Per Analysis Request)

```
                ┌─────────────────────────┐
                │ Job posting data received │
                │ (title, description,       │
                │  salary, email, etc.)      │
                └────────────┬──────────────┘
                              ▼
        ┌──────────────────────────────────────────┐
        │   STEP 1: Rule-Based Red Flag Detection     │
        │   Check 7 categories:                       │
        │   - Unrealistic Salary                      │
        │   - No Company Details                      │
        │   - Asking for Money                        │
        │   - Suspicious Email Domain                 │
        │   - Grammar/Spelling Issues                 │
        │   - Urgency/Pressure Tactics                │
        │   - Unrealistic Claims                      │
        │   → red_flag_count (0-7)                    │
        └────────────────────┬─────────────────────┘
                               ▼
        ┌──────────────────────────────────────────┐
        │   STEP 2: ML Model Prediction                │
        │   - Combine all text fields                  │
        │   - TF-IDF Vectorize                          │
        │   - Logistic Regression predict_proba()       │
        │   → ml_probability (0-100%)                   │
        └────────────────────┬─────────────────────┘
                               ▼
        ┌──────────────────────────────────────────┐
        │   STEP 3: Combine Scores                     │
        │   red_flag_score = (count/7) × 100           │
        │   final_score = 0.7×ml_probability            │
        │                + 0.3×red_flag_score           │
        └────────────────────┬─────────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │ final_score >= 50?    │
                    └────┬────────────┬────┘
                      Yes│            │No
                         ▼            ▼
                  ┌────────────┐ ┌────────────┐
                  │ Label: FAKE │ │ Label:GENUINE│
                  └──────┬─────┘ └──────┬───────┘
                          └──────┬───────┘
                                  ▼
        ┌──────────────────────────────────────────┐
        │   STEP 4: Generate AI Explanation            │
        │   - Based on label + red flags + score        │
        │   - Returns natural language text             │
        └────────────────────┬─────────────────────┘
                               ▼
        ┌──────────────────────────────────────────┐
        │   STEP 5: Persist to job_analyses table       │
        └────────────────────┬─────────────────────┘
                               ▼
                       ┌─────────────┐
                       │ Return Report │
                       └─────────────┘
```

## 3. ML Model Training Flow (Offline, Run Once)

```
        ┌────────────────────────────┐
        │ generate_dataset.py          │
        │ → fake_job_postings.csv       │
        │   (800 labeled samples)        │
        └─────────────┬──────────────┘
                       ▼
        ┌────────────────────────────┐
        │ train_model.py                │
        │ 1. Load CSV                    │
        │ 2. Combine text columns        │
        │ 3. Train/Test split (80/20)    │
        │ 4. TF-IDF vectorize (3000 feat,│
        │    1-2 grams, stopwords removed)│
        │ 5. Train Logistic Regression   │
        │    (class_weight='balanced')   │
        │ 6. Evaluate (accuracy, F1,     │
        │    precision, recall)          │
        │ 7. Save .pkl files via joblib  │
        └─────────────┬──────────────┘
                       ▼
        ┌────────────────────────────┐
        │ fake_job_model.pkl            │
        │ tfidf_vectorizer.pkl          │
        │ → copied to app/models/        │
        └─────────────┬──────────────┘
                       ▼
        ┌────────────────────────────┐
        │ Loaded by Flask app at        │
        │ startup for real-time          │
        │ inference                      │
        └────────────────────────────┘
```

## 4. Authentication Flow

```
            ┌──────────────┐
            │ User visits    │
            │ /login or       │
            │ /register       │
            └──────┬─────────┘
                    ▼
        ┌──────────────────────┐
        │ /register: collect      │
        │ name, email, password    │
        │ → hash password (PBKDF2) │
        │ → check email uniqueness  │
        │ → INSERT into users       │
        └──────┬───────────────────┘
                ▼
        ┌──────────────────────┐
        │ /login: verify email     │
        │ + check_password_hash()  │
        └──────┬───────────────────┘
                ▼
       ┌──────────────────────────┐
       │ Set session (user_id,       │
       │ full_name, role)             │
       └──────┬───────────────────────┘
               ▼
      ┌────────────────────┐
      │ role == 'admin'?     │
      └────┬───────────┬────┘
        Yes│           │No
           ▼           ▼
   ┌──────────────┐ ┌──────────────┐
   │ Admin Panel    │ │ User Dashboard │
   └──────────────┘ └──────────────┘
```
