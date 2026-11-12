"""
url_extractor.py
-----------------
Job posting URL se automatically details extract karta hai.
"""

import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def extract_from_url(url):
    """URL se job posting details extract karo."""
    result = {
        "title": "",
        "company_profile": "",
        "description": "",
        "requirements": "",
        "salary": "",
        "location": "",
        "company_email_domain": "",
        "error": None
    }

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        if "indeed.com" in url:
            result = extract_indeed(soup, result)
        elif "naukri.com" in url:
            result = extract_naukri(soup, result)
        elif "linkedin.com" in url:
            result = extract_linkedin(soup, result)
        else:
            result = extract_general(soup, result)

        if not result["title"]:
            page_title = soup.find("title")
            if page_title:
                result["title"] = clean_text(page_title.text)

    except requests.exceptions.Timeout:
        result["error"] = "Website response timeout. Please try again."
    except requests.exceptions.ConnectionError:
        result["error"] = "Could not connect to the URL."
    except requests.exceptions.HTTPError as e:
        result["error"] = f"Website returned error: {e}"
    except Exception as e:
        result["error"] = f"Could not extract details: {str(e)}"

    return result


def extract_indeed(soup, result):
    """Indeed.com se details extract karo."""
    title = soup.find("h1", class_=re.compile("jobsearch-JobInfoHeader-title|title"))
    if title:
        result["title"] = clean_text(title.text)

    company = soup.find("div", class_=re.compile("jobsearch-InlineCompanyRating|company"))
    if company:
        result["company_profile"] = clean_text(company.text)

    location = soup.find("div", class_=re.compile("jobsearch-JobInfoHeader-subtitle"))
    if location:
        result["location"] = clean_text(location.text)

    desc = soup.find("div", id="jobDescriptionText")
    if desc:
        result["description"] = clean_text(desc.text)

    salary = soup.find("div", class_=re.compile("salary|compensation"))
    if salary:
        result["salary"] = clean_text(salary.text)

    return result


def extract_naukri(soup, result):
    """Naukri.com se details extract karo."""
    title = soup.find("h1")
    if title:
        result["title"] = clean_text(title.text)

    company = soup.find("a", class_=re.compile("comp-name|company"))
    if company:
        result["company_profile"] = clean_text(company.text)

    location = soup.find("a", class_=re.compile("loc|location"))
    if location:
        result["location"] = clean_text(location.text)

    salary = soup.find("li", class_=re.compile("salary"))
    if salary:
        result["salary"] = clean_text(salary.text)

    desc = soup.find("div", class_=re.compile("job-desc|description|dang-inner-html"))
    if desc:
        result["description"] = clean_text(desc.text)

    return result


def extract_linkedin(soup, result):
    """LinkedIn se details extract karo."""
    title = soup.find("h1")
    if title:
        result["title"] = clean_text(title.text)

    company = soup.find("a", class_=re.compile("topcard__org-name|company"))
    if company:
        result["company_profile"] = clean_text(company.text)

    location = soup.find("span", class_=re.compile("topcard__flavor--bullet|location"))
    if location:
        result["location"] = clean_text(location.text)

    desc = soup.find("div", class_=re.compile("description__text|show-more-less-html"))
    if desc:
        result["description"] = clean_text(desc.text)

    return result


def extract_general(soup, result):
    """General websites ke liye extraction."""
    h1 = soup.find("h1")
    if h1:
        result["title"] = clean_text(h1.text)

    full_text = soup.get_text(separator=" ", strip=True)

    salary_match = re.search(
        r'(?:salary|pay|ctc|package|stipend)[:\s]*'
        r'([₹$]?[\d,]+\s*(?:-\s*[₹$]?[\d,]+)?\s*'
        r'(?:per|/|p\.?a\.?|lpa|lakh)?[\s\w]*)',
        full_text, re.IGNORECASE
    )
    if salary_match:
        result["salary"] = salary_match.group(1).strip()

    location_match = re.search(
        r'(?:location|city|place)[:\s]*'
        r'([A-Za-z\s,]+(?:India|Mumbai|Delhi|Bangalore|Pune|Hyderabad|Chennai)?)',
        full_text, re.IGNORECASE
    )
    if location_match:
        result["location"] = location_match.group(1).strip()[:100]

    paragraphs = soup.find_all("p")
    if paragraphs:
        longest = max(paragraphs, key=lambda p: len(p.text))
        if len(longest.text) > 100:
            result["description"] = clean_text(longest.text)

    for tag in soup.find_all(["div", "section", "ul"]):
        text = tag.get_text().lower()
        if any(word in text for word in
               ["requirement", "qualification", "skill", "experience"]):
            if len(tag.get_text()) > 50:
                result["requirements"] = clean_text(tag.get_text())[:1000]
                break

    return result


def clean_text(text):
    """Text clean karo."""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()[:2000]