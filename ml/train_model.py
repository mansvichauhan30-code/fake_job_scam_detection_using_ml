"""
train_model.py
----------------
Trains and COMPARES multiple ML algorithms:
    1. Logistic Regression
    2. Random Forest
    3. Naive Bayes
    4. Decision Tree
    5. Support Vector Machine (SVM)

Best model automatically save hota hai.
"""

import pandas as pd
import numpy as np
import joblib
import os

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)

# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------
DATA_PATH = os.path.join(os.path.dirname(__file__), "dataset", "fake_job_postings.csv")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")
os.makedirs(MODEL_DIR, exist_ok=True)

MODEL_PATH = os.path.join(MODEL_DIR, "fake_job_model.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")
RESULTS_PATH = os.path.join(MODEL_DIR, "comparison_results.csv")


def load_and_prepare_data():
    """Load dataset and combine text columns."""
    import os
    csv_path = DATA_PATH
    xlsx_path = DATA_PATH.replace(".csv", ".xlsx")

    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        print("Loaded CSV file")
    elif os.path.exists(xlsx_path):
        df = pd.read_excel(xlsx_path)
        print("Loaded Excel file")
    else:
        raise FileNotFoundError("Dataset file not found!")

    print("Columns found:", list(df.columns))
    print("Total rows:", len(df))

    # Fill missing values
    text_cols = ["title", "company_profile", "description",
                 "requirements", "location"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].fillna("")
        else:
            df[col] = ""

    # Handle salary column
    if "salary_range" in df.columns:
        df["salary"] = df["salary_range"].fillna("")
    elif "salary" in df.columns:
        df["salary"] = df["salary"].fillna("")
    else:
        df["salary"] = ""

    # Combine all text
    df["text"] = (
        df["title"] + " " +
        df["company_profile"] + " " +
        df["description"] + " " +
        df["requirements"] + " " +
        df["salary"] + " " +
        df["location"]
    )

    X = df["text"]
    y = df["fraudulent"]

    print(f"Fake jobs   : {sum(y == 1)}")
    print(f"Genuine jobs: {sum(y == 0)}")
    return X, y


def train():
    print("\n" + "="*60)
    print("   FAKE JOB DETECTION - ALGORITHM COMPARISON")
    print("="*60)

    print("\nLoading dataset...")
    X, y = load_and_prepare_data()

    # Train/Test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # TF-IDF Vectorization
    print("\nVectorizing text using TF-IDF...")
    vectorizer = TfidfVectorizer(
        max_features=5000,
        stop_words="english",
        ngram_range=(1, 2)
    )
    X_train_tfidf = vectorizer.fit_transform(X_train)
    X_test_tfidf = vectorizer.transform(X_test)

    # ---------------------------------------------------------
    # Define all algorithms
    # ---------------------------------------------------------
    algorithms = {
        "Logistic Regression": LogisticRegression(
            max_iter=1000,
            class_weight="balanced"
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=100,
            class_weight="balanced",
            random_state=42
        ),
        "Naive Bayes": MultinomialNB(),
        "Decision Tree": DecisionTreeClassifier(
            class_weight="balanced",
            random_state=42
        ),
        "SVM (Linear)": CalibratedClassifierCV(
            LinearSVC(
                class_weight="balanced",
                max_iter=1000
            )
        )
    }

    # ---------------------------------------------------------
    # Train and evaluate each algorithm
    # ---------------------------------------------------------
    results = []
    best_f1 = 0
    best_model = None
    best_name = ""

    print("\n" + "="*60)
    print("   TRAINING & EVALUATING ALL ALGORITHMS")
    print("="*60)

    for name, model in algorithms.items():
        print(f"\n--- {name} ---")

        # Train
        model.fit(X_train_tfidf, y_train)

        # Predict
        y_pred = model.predict(X_test_tfidf)

        # Metrics
        acc  = round(accuracy_score(y_test, y_pred) * 100, 2)
        prec = round(precision_score(y_test, y_pred,
                     zero_division=0) * 100, 2)
        rec  = round(recall_score(y_test, y_pred,
                     zero_division=0) * 100, 2)
        f1   = round(f1_score(y_test, y_pred,
                     zero_division=0) * 100, 2)

        print(f"  Accuracy  : {acc}%")
        print(f"  Precision : {prec}%")
        print(f"  Recall    : {rec}%")
        print(f"  F1 Score  : {f1}%")

        results.append({
            "Algorithm": name,
            "Accuracy (%)": acc,
            "Precision (%)": prec,
            "Recall (%)": rec,
            "F1 Score (%)": f1
        })

        # Track best model by F1 Score
        if f1 > best_f1:
            best_f1 = f1
            best_model = model
            best_name = name

    # ---------------------------------------------------------
    # Print Comparison Table
    # ---------------------------------------------------------
    print("\n" + "="*60)
    print("   ALGORITHM COMPARISON TABLE")
    print("="*60)
    print(f"{'Algorithm':<25} {'Accuracy':>10} {'Precision':>10} {'Recall':>10} {'F1 Score':>10}")
    print("-"*60)
    for r in results:
        print(f"{r['Algorithm']:<25} {r['Accuracy (%)']:>9}% {r['Precision (%)']:>9}% {r['Recall (%)']:>9}% {r['F1 Score (%)']:>9}%")
    print("-"*60)
    print(f"\n🏆 BEST MODEL: {best_name} (F1 Score: {best_f1}%)")

    # ---------------------------------------------------------
    # Save comparison results to CSV
    # ---------------------------------------------------------
    results_df = pd.DataFrame(results)
    results_df.to_csv(RESULTS_PATH, index=False)
    print(f"\nComparison results saved to: {RESULTS_PATH}")

    # ---------------------------------------------------------
    # Save best model and vectorizer
    # ---------------------------------------------------------
    joblib.dump(best_model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)
    print(f"Best model ({best_name}) saved to: {MODEL_PATH}")
    print(f"Vectorizer saved to: {VECTORIZER_PATH}")
    print("\n" + "="*60)


if __name__ == "__main__":
    train()