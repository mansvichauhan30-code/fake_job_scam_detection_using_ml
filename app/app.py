"""
app.py
-------
Main Flask application for the Fake Job Scam Detection System.

Features:
    - User registration & login (session-based auth)
    - Job posting analysis using ML model
    - Red flag detection
    - AI-generated explanation
    - Dashboard with statistics
    - Search & filter previous reports
    - Admin panel
"""

import os
import json
from datetime import datetime

from flask import (
    Flask, render_template, request, redirect, url_for, session, flash, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash
import joblib

from config import Config
from db import execute_query
from utils.red_flags import analyze_red_flags
from utils.explanation_generator import generate_explanation

# ---------------------------------------------------------
# App Initialization
# ---------------------------------------------------------
app = Flask(__name__)
app.config.from_object(Config)

# ---------------------------------------------------------
# Load trained ML model and TF-IDF vectorizer at startup
# ---------------------------------------------------------
try:
    model = joblib.load(Config.MODEL_PATH)
    vectorizer = joblib.load(Config.VECTORIZER_PATH)
    print("ML model and vectorizer loaded successfully.")
except Exception as e:
    model = None
    vectorizer = None
    print(f"Warning: Could not load ML model/vectorizer: {e}")


# ===========================================================
# AUTH HELPERS
# ===========================================================

def login_required(f):
    """Decorator to require login for protected routes."""
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin role for protected routes."""
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login"))
        if session.get("role") != "admin":
            flash("You do not have permission to access this page.", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated_function


# ===========================================================
# ROUTES: PUBLIC PAGES
# ===========================================================

@app.route("/")
def index():
    """Landing page."""
    return render_template("index.html")


# ===========================================================
# ROUTES: AUTHENTICATION
# ===========================================================

@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration page."""
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Basic validation
        if not full_name or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return redirect(url_for("register"))

        # Check if email already exists
        existing = execute_query(
            "SELECT user_id FROM users WHERE email = %s", (email,), fetchone=True
        )
        if existing:
            flash("Email already registered. Please log in.", "danger")
            return redirect(url_for("login"))

        # Hash password and insert new user
        password_hash = generate_password_hash(password)
        execute_query(
            "INSERT INTO users (full_name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
            (full_name, email, password_hash, "user"),
            commit=True
        )

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login page."""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = execute_query(
            "SELECT * FROM users WHERE email = %s", (email,), fetchone=True
        )

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["user_id"]
            session["full_name"] = user["full_name"]
            session["role"] = user["role"]
            flash(f"Welcome back, {user['full_name']}!", "success")

            if user["role"] == "admin":
                return redirect(url_for("admin_panel"))
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log out the current user."""
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

@app.route("/extract-url", methods=["POST"])
@login_required
def extract_url():
    """
    URL se job details extract karke
    analyze form mein fill karta hai.
    """
    from utils.url_extractor import extract_from_url

    url = request.form.get("job_url", "").strip()

    if not url:
        flash("Please enter a valid URL.", "danger")
        return redirect(url_for("analyze"))

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    # URL se details extract karo
    extracted = extract_from_url(url)

    if extracted["error"]:
        flash(f"Could not extract details: {extracted['error']}", "warning")

    return render_template("analyze.html", extracted=extracted, url=url)


# ===========================================================
# ROUTES: JOB ANALYSIS
# ===========================================================

@app.route("/analyze", methods=["GET", "POST"])
@login_required
def analyze():
    """Job posting analysis page."""
    if request.method == "POST":
        # Collect form data
        job_data = {
            "title": request.form.get("title", "").strip(),
            "company_profile": request.form.get("company_profile", "").strip(),
            "description": request.form.get("description", "").strip(),
            "requirements": request.form.get("requirements", "").strip(),
            "salary": request.form.get("salary", "").strip(),
            "company_email_domain": request.form.get("company_email_domain", "").strip(),
            "location": request.form.get("location", "").strip(),
        }

        if not job_data["title"] or not job_data["description"]:
            flash("Job Title and Description are required.", "danger")
            return redirect(url_for("analyze"))

        # ---------------------------------------------------
        # 1. Red Flag Detection
        # ---------------------------------------------------
        red_flag_result = analyze_red_flags(job_data)

        # ---------------------------------------------------
        # 2. ML Model Prediction
        # ---------------------------------------------------
        combined_text = " ".join([
            job_data["title"], job_data["company_profile"],
            job_data["description"], job_data["requirements"],
            job_data["salary"], job_data["location"]
        ])

        ml_probability = 0.0
        if model is not None and vectorizer is not None:
            text_vector = vectorizer.transform([combined_text])
            # probability of class 1 (fake)
            ml_probability = model.predict_proba(text_vector)[0][1] * 100
        else:
            # Fallback if model not loaded: base score on red flags only
            ml_probability = (red_flag_result["flag_count"] / 7) * 100

        # ---------------------------------------------------
        # 3. Combine ML probability with red flag score
        #    Final score = 70% ML model + 30% red flag ratio
        # ---------------------------------------------------
        red_flag_score = (red_flag_result["flag_count"] / 7) * 100
        final_score = (0.7 * ml_probability) + (0.3 * red_flag_score)
        final_score = round(min(max(final_score, 0), 100), 2)

        prediction_label = "FAKE" if final_score >= 50 else "GENUINE"
        prediction_int = 1 if prediction_label == "FAKE" else 0

        # ---------------------------------------------------
        # 4. AI-generated explanation
        # ---------------------------------------------------
        explanation = generate_explanation(
            prediction_int, final_score, red_flag_result, job_data["title"]
        )

        # ---------------------------------------------------
        # 5. Save analysis to database
        # ---------------------------------------------------
        flags_json = json.dumps(red_flag_result["flags"])

        analysis_id = execute_query(
            """
            INSERT INTO job_analyses
            (user_id, job_title, company_profile, job_description, requirements,
             salary, company_email_domain, location, prediction, scam_probability,
             ai_explanation, red_flags, red_flag_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                session["user_id"], job_data["title"], job_data["company_profile"],
                job_data["description"], job_data["requirements"], job_data["salary"],
                job_data["company_email_domain"], job_data["location"],
                prediction_label, final_score, explanation, flags_json,
                red_flag_result["flag_count"]
            ),
            commit=True
        )

        return redirect(url_for("report", analysis_id=analysis_id))

    return render_template("analyze.html")


@app.route("/report/<int:analysis_id>")
@login_required
def report(analysis_id):
    """Display the analysis report/result page."""
    analysis = execute_query(
        "SELECT * FROM job_analyses WHERE analysis_id = %s AND user_id = %s",
        (analysis_id, session["user_id"]), fetchone=True
    )

    if not analysis:
        flash("Report not found.", "danger")
        return redirect(url_for("dashboard"))

    # Parse JSON red flags
    analysis["red_flags_parsed"] = json.loads(analysis["red_flags"]) if analysis["red_flags"] else []

    return render_template("report.html", analysis=analysis)


# ===========================================================
# ROUTES: DASHBOARD
# ===========================================================

@app.route("/dashboard")
@login_required
def dashboard():
    """User dashboard showing statistics, charts and recent analyses."""
    user_id = session["user_id"]

    # Total counts
    total_jobs = execute_query(
        "SELECT COUNT(*) AS count FROM job_analyses WHERE user_id = %s",
        (user_id,), fetchone=True
    )["count"]

    fake_jobs = execute_query(
        "SELECT COUNT(*) AS count FROM job_analyses WHERE user_id = %s AND prediction = 'FAKE'",
        (user_id,), fetchone=True
    )["count"]

    genuine_jobs = execute_query(
        "SELECT COUNT(*) AS count FROM job_analyses WHERE user_id = %s AND prediction = 'GENUINE'",
        (user_id,), fetchone=True
    )["count"]

    # Recent analyses (last 5)
    recent_analyses = execute_query(
        """
        SELECT analysis_id, job_title, prediction, scam_probability, created_at
        FROM job_analyses
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT 5
        """,
        (user_id,), fetch=True
    )

    # Last 7 days bar chart data
    from datetime import datetime, timedelta
    bar_labels = []
    bar_fake = []
    bar_genuine = []

    for i in range(6, -1, -1):
        day = datetime.now() - timedelta(days=i)
        day_str = day.strftime('%d %b')
        bar_labels.append(day_str)

        fake_count = execute_query(
            """SELECT COUNT(*) AS count FROM job_analyses
               WHERE user_id = %s AND prediction = 'FAKE'
               AND DATE(created_at) = %s""",
            (user_id, day.strftime('%Y-%m-%d')), fetchone=True
        )["count"]

        genuine_count = execute_query(
            """SELECT COUNT(*) AS count FROM job_analyses
               WHERE user_id = %s AND prediction = 'GENUINE'
               AND DATE(created_at) = %s""",
            (user_id, day.strftime('%Y-%m-%d')), fetchone=True
        )["count"]

        bar_fake.append(fake_count)
        bar_genuine.append(genuine_count)

    return render_template(
        "dashboard.html",
        total_jobs=total_jobs,
        fake_jobs=fake_jobs,
        genuine_jobs=genuine_jobs,
        recent_analyses=recent_analyses,
        bar_labels=bar_labels,
        bar_fake=bar_fake,
        bar_genuine=bar_genuine
    )

# ===========================================================
# ROUTES: REPORTS - SEARCH & FILTER
# ===========================================================

@app.route("/reports")
@login_required
def reports():
    """List all past reports with search and filter options."""
    user_id = session["user_id"]

    search_query = request.args.get("q", "").strip()
    filter_type = request.args.get("filter", "all")  # all, FAKE, GENUINE

    query = "SELECT * FROM job_analyses WHERE user_id = %s"
    params = [user_id]

    if search_query:
        query += " AND job_title LIKE %s"
        params.append(f"%{search_query}%")

    if filter_type in ("FAKE", "GENUINE"):
        query += " AND prediction = %s"
        params.append(filter_type)

    query += " ORDER BY created_at DESC"

    results = execute_query(query, tuple(params), fetch=True)

    return render_template(
        "reports.html", results=results, search_query=search_query, filter_type=filter_type
    )


# ===========================================================
# ROUTES: ADMIN PANEL
# ===========================================================

@app.route("/admin")
@admin_required
def admin_panel():
    """Admin dashboard showing overall system statistics."""
    total_users = execute_query("SELECT COUNT(*) AS count FROM users", fetchone=True)["count"]
    total_analyses = execute_query("SELECT COUNT(*) AS count FROM job_analyses", fetchone=True)["count"]
    total_fake = execute_query(
        "SELECT COUNT(*) AS count FROM job_analyses WHERE prediction = 'FAKE'", fetchone=True
    )["count"]
    total_genuine = execute_query(
        "SELECT COUNT(*) AS count FROM job_analyses WHERE prediction = 'GENUINE'", fetchone=True
    )["count"]

    # All users list
    users = execute_query(
        "SELECT user_id, full_name, email, role, created_at FROM users ORDER BY created_at DESC",
        fetch=True
    )

    # All analyses (recent 20)
    all_analyses = execute_query(
        """
        SELECT a.analysis_id, a.job_title, a.prediction, a.scam_probability,
               a.created_at, u.full_name, u.email
        FROM job_analyses a
        JOIN users u ON a.user_id = u.user_id
        ORDER BY a.created_at DESC
        LIMIT 20
        """,
        fetch=True
    )

    return render_template(
        "admin.html",
        total_users=total_users,
        total_analyses=total_analyses,
        total_fake=total_fake,
        total_genuine=total_genuine,
        users=users,
        all_analyses=all_analyses
    )


@app.route("/admin/delete_user/<int:user_id>", methods=["POST"])
@admin_required
def admin_delete_user(user_id):
    """Admin: delete a user account."""
    if user_id == session["user_id"]:
        flash("You cannot delete your own admin account.", "danger")
        return redirect(url_for("admin_panel"))

    execute_query("DELETE FROM users WHERE user_id = %s", (user_id,), commit=True)
    flash("User deleted successfully.", "success")
    return redirect(url_for("admin_panel"))


# ===========================================================
# API ENDPOINTS (JSON) - for AJAX / external integration
# ===========================================================

@app.route("/api/analyze", methods=["POST"])
@login_required
def api_analyze():
    """
    JSON API endpoint for job analysis.
    Accepts JSON payload and returns prediction result as JSON.
    """
    data = request.get_json()

    job_data = {
        "title": data.get("title", ""),
        "company_profile": data.get("company_profile", ""),
        "description": data.get("description", ""),
        "requirements": data.get("requirements", ""),
        "salary": data.get("salary", ""),
        "company_email_domain": data.get("company_email_domain", ""),
        "location": data.get("location", ""),
    }

    red_flag_result = analyze_red_flags(job_data)

    combined_text = " ".join(job_data.values())
    if model is not None and vectorizer is not None:
        text_vector = vectorizer.transform([combined_text])
        ml_probability = model.predict_proba(text_vector)[0][1] * 100
    else:
        ml_probability = (red_flag_result["flag_count"] / 7) * 100

    red_flag_score = (red_flag_result["flag_count"] / 7) * 100
    final_score = round((0.7 * ml_probability) + (0.3 * red_flag_score), 2)
    prediction_label = "FAKE" if final_score >= 50 else "GENUINE"

    explanation = generate_explanation(
        1 if prediction_label == "FAKE" else 0, final_score, red_flag_result, job_data["title"]
    )

    return jsonify({
        "prediction": prediction_label,
        "scam_probability": final_score,
        "red_flags": red_flag_result["flags"],
        "explanation": explanation
    })


# ===========================================================
# ERROR HANDLERS
# ===========================================================

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """User profile page — edit name and change password."""
    user_id = session["user_id"]

    # Get current user data
    user = execute_query(
        "SELECT * FROM users WHERE user_id = %s", (user_id,), fetchone=True
    )

    # Get user stats
    total_jobs = execute_query(
        "SELECT COUNT(*) AS count FROM job_analyses WHERE user_id = %s",
        (user_id,), fetchone=True
    )["count"]

    fake_jobs = execute_query(
        "SELECT COUNT(*) AS count FROM job_analyses WHERE user_id = %s AND prediction = 'FAKE'",
        (user_id,), fetchone=True
    )["count"]

    genuine_jobs = execute_query(
        "SELECT COUNT(*) AS count FROM job_analyses WHERE user_id = %s AND prediction = 'GENUINE'",
        (user_id,), fetchone=True
    )["count"]

    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_name":
            new_name = request.form.get("full_name", "").strip()
            if not new_name:
                flash("Name cannot be empty.", "danger")
            else:
                execute_query(
                    "UPDATE users SET full_name = %s WHERE user_id = %s",
                    (new_name, user_id), commit=True
                )
                session["full_name"] = new_name
                flash("Name updated successfully!", "success")

        elif action == "change_password":
            current_password = request.form.get("current_password", "")
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")

            if not check_password_hash(user["password_hash"], current_password):
                flash("Current password is incorrect.", "danger")
            elif len(new_password) < 6:
                flash("New password must be at least 6 characters.", "danger")
            elif new_password != confirm_password:
                flash("New passwords do not match.", "danger")
            else:
                new_hash = generate_password_hash(new_password)
                execute_query(
                    "UPDATE users SET password_hash = %s WHERE user_id = %s",
                    (new_hash, user_id), commit=True
                )
                flash("Password changed successfully!", "success")

        return redirect(url_for("profile"))

    return render_template(
        "profile.html",
        user=user,
        total_jobs=total_jobs,
        fake_jobs=fake_jobs,
        genuine_jobs=genuine_jobs
    )


# ─── Yahan se error handlers shuru hote hain ───
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


# ===========================================================
# MAIN
# ===========================================================

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
