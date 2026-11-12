"""
red_flags.py
-------------
Rule-based Red Flag Detection module.

This module analyzes the raw text of a job posting and detects
common scam indicators ("red flags"). These rules complement the
ML model's prediction and are used to:
    1. Generate the list of red flags shown to the user
    2. Help build the AI-generated explanation
    3. Contribute to the final scam probability score
"""

import re

# ---------------------------------------------------------
# Keyword lists used for rule-based detection
# ---------------------------------------------------------

MONEY_REQUEST_KEYWORDS = [
    "registration fee", "processing fee", "security deposit", "deposit amount",
    "pay a fee", "kit fee", "training fee", "refundable amount",
    "send money", "pay rs", "pay $", "activation fee", "joining fee"
]

URGENCY_KEYWORDS = [
    "limited seats", "apply immediately", "hurry up", "urgent hiring",
    "offer ends soon", "act now", "immediate joining", "only few vacancies"
]

UNREALISTIC_PHRASES = [
    "no experience needed", "no qualification required", "anyone can apply",
    "guaranteed job", "100% job placement", "easy money", "earn daily cash",
    "huge income", "unlimited earning", "guarenteed", "no investment needed"
]

SUSPICIOUS_EMAIL_DOMAINS = [
    "tempmail.com", "yahoo.in", "rediffmail.com", "outlook.in",
    "mailinator.com", "guerrillamail.com"
]

FREE_EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]

COMMON_MISSPELLINGS = [
    "recieve", "guarenteed", "eligibel", "carrer", "oppertunity",
    "responsibilty", "experiance", "untill", "garunteed", "managment"
]


def check_unrealistic_salary(salary_text):
    """
    Detect unrealistic / suspicious salary patterns.
    Flags very high daily/weekly pay or vague unlimited-earning claims.
    """
    if not salary_text:
        return False
    salary_text = salary_text.lower()

    if "unlimited" in salary_text or "guarenteed" in salary_text or "guaranteed" in salary_text:
        return True

    # Detect very high numeric values combined with daily/weekly terms
    if re.search(r"(daily|per day|weekly|per week)", salary_text):
        numbers = re.findall(r"\d+", salary_text.replace(",", ""))
        for num in numbers:
            if int(num) >= 2000:  # e.g. Rs 2000+/day is unrealistic for most entry jobs
                return True

    # Detect amounts above 1,00,000/month type entries with vague context
    if re.search(r"1,?00,?000", salary_text) and "month" in salary_text:
        return True

    return False


def check_no_company_details(company_profile):
    """Detect missing or vague company information."""
    if not company_profile:
        return True
    company_profile = company_profile.strip().lower()
    if company_profile in ["", "n/a", "na", "not specified", "private limited", "none"]:
        return True
    if len(company_profile) < 15:
        return True
    return False


def check_money_request(full_text):
    """Detect language asking the candidate to pay money."""
    text = full_text.lower()
    return any(keyword in text for keyword in MONEY_REQUEST_KEYWORDS)


def check_suspicious_email(email_domain):
    """Detect suspicious or temporary email domains."""
    if not email_domain:
        return False
    domain = email_domain.strip().lower()
    return domain in SUSPICIOUS_EMAIL_DOMAINS


def check_grammar_issues(full_text):
    """
    Simple heuristic grammar/spelling check.
    Looks for common misspellings and excessive punctuation/caps.
    """
    text = full_text.lower()
    issues = 0

    for word in COMMON_MISSPELLINGS:
        if word in text:
            issues += 1

    # Excessive exclamation marks
    if full_text.count("!") >= 2:
        issues += 1

    # ALL CAPS words (shouting) - count words fully in caps with length > 3
    caps_words = re.findall(r"\b[A-Z]{4,}\b", full_text)
    if len(caps_words) >= 1:
        issues += 1

    return issues > 0


def check_urgency_language(full_text):
    """Detect urgency/pressure tactics commonly used in scams."""
    text = full_text.lower()
    return any(keyword in text for keyword in URGENCY_KEYWORDS)


def check_unrealistic_claims(full_text):
    """Detect unrealistic promises (no experience, guaranteed job, etc.)."""
    text = full_text.lower()
    return any(phrase in text for phrase in UNREALISTIC_PHRASES)


def analyze_red_flags(job_data):
    """
    Run all red flag checks on the given job posting data.

    Parameters
    ----------
    job_data : dict
        Dictionary containing keys:
        title, company_profile, description, requirements,
        salary, company_email_domain, location

    Returns
    -------
    dict with:
        - flags: list of dicts {name, detected, description}
        - flag_count: number of flags triggered
    """
    full_text = " ".join([
        job_data.get("title", ""),
        job_data.get("description", ""),
        job_data.get("requirements", ""),
        job_data.get("company_profile", "")
    ])

    flags = [
        {
            "name": "Unrealistic Salary",
            "detected": check_unrealistic_salary(job_data.get("salary", "")),
            "description": "The salary offered seems unrealistically high or vague for the role described."
        },
        {
            "name": "No Company Details",
            "detected": check_no_company_details(job_data.get("company_profile", "")),
            "description": "The company profile is missing, too short, or not specified."
        },
        {
            "name": "Asking for Money",
            "detected": check_money_request(full_text),
            "description": "The posting asks the candidate to pay a fee, deposit, or other charges."
        },
        {
            "name": "Suspicious Email Domain",
            "detected": check_suspicious_email(job_data.get("company_email_domain", "")),
            "description": "The recruiter's email domain is associated with temporary or suspicious mail services."
        },
        {
            "name": "Grammar / Spelling Issues",
            "detected": check_grammar_issues(full_text),
            "description": "The posting contains spelling mistakes, excessive punctuation, or unusual formatting."
        },
        {
            "name": "Urgency / Pressure Tactics",
            "detected": check_urgency_language(full_text),
            "description": "The posting uses urgency phrases to pressure quick action without due diligence."
        },
        {
            "name": "Unrealistic Claims",
            "detected": check_unrealistic_claims(full_text),
            "description": "The posting makes unrealistic promises such as guaranteed jobs with no experience."
        }
    ]

    flag_count = sum(1 for f in flags if f["detected"])

    return {
        "flags": flags,
        "flag_count": flag_count
    }
