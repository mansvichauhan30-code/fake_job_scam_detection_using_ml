"""
seed_admin.py
--------------
Run this script once after creating the database schema to create
an admin account.

Usage:
    cd app
    ADMIN_PASSWORD="choose-a-strong-password" python seed_admin.py
"""

import os

from werkzeug.security import generate_password_hash
from db import execute_query

ADMIN_NAME = "System Admin"
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@jobshield.com")


def seed_admin():
    admin_password = os.environ.get("ADMIN_PASSWORD")
    if not admin_password:
        raise SystemExit("Set ADMIN_PASSWORD before running this script.")

    existing = execute_query(
        "SELECT user_id FROM users WHERE email = %s", (ADMIN_EMAIL,), fetchone=True
    )

    if existing:
        print("Admin user already exists. Skipping.")
        return

    password_hash = generate_password_hash(admin_password)

    execute_query(
        "INSERT INTO users (full_name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
        (ADMIN_NAME, ADMIN_EMAIL, password_hash, "admin"),
        commit=True
    )

    print("Admin user created successfully!")
    print(f"   Email   : {ADMIN_EMAIL}")


if __name__ == "__main__":
    seed_admin()
