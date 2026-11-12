"""
generate_dataset.py
--------------------
Generates a sample synthetic dataset of job postings (fake & genuine)
for training the Fake Job Detection ML model.

In a real-world project, you would replace/augment this with the
Kaggle "Real or Fake Job Posting Prediction" dataset
(https://www.kaggle.com/datasets/shivamb/real-or-fake-fake-jobposting-prediction).

Output: fake_job_postings.csv
Columns:
    title, company_profile, description, requirements, salary,
    company_email_domain, location, fraudulent
"""

import pandas as pd
import random

# ---------------------------------------------------------
# Genuine job templates
# ---------------------------------------------------------
genuine_titles = [
    "Software Engineer", "Data Analyst", "HR Executive", "Backend Developer",
    "Frontend Developer", "Marketing Manager", "Business Analyst",
    "QA Engineer", "DevOps Engineer", "Product Manager", "UI/UX Designer",
    "Network Administrator", "Sales Executive", "Content Writer",
    "Customer Support Associate"
]

genuine_descriptions = [
    "We are looking for a skilled {title} to join our growing team. "
    "The candidate will work closely with cross-functional teams to deliver "
    "high quality solutions and meet project deadlines.",
    "Our company is hiring a {title} with strong communication skills and "
    "relevant experience. You will be responsible for daily operational "
    "tasks and collaborating with senior management.",
    "Join our team as a {title}. We offer a competitive salary, health "
    "insurance, and growth opportunities within the organization.",
    "We need an experienced {title} to support our expanding operations. "
    "The role requires good problem solving skills and a degree in a "
    "relevant field."
]

genuine_requirements = [
    "Bachelor's degree in relevant field, 1-3 years experience, good communication skills.",
    "Strong analytical skills, proficiency in MS Office, ability to work in a team.",
    "Relevant certification preferred, excellent written and verbal communication.",
    "Prior internship or work experience in a related domain is a plus."
]

genuine_companies = [
    "TCS", "Infosys", "Wipro", "Accenture", "Capgemini", "Cognizant",
    "HCL Technologies", "Tech Mahindra", "Zoho Corporation", "Freshworks"
]

genuine_domains = ["gmail.com", "company.com", "outlook.com", "yahoo.com"]

genuine_salaries = ["15000-25000", "25000-40000", "30000-50000", "40000-70000", "8-12 LPA"]

genuine_locations = ["Bangalore, India", "Pune, India", "Hyderabad, India",
                      "Chennai, India", "Mumbai, India", "Remote, India"]

# ---------------------------------------------------------
# Fake job templates (common scam patterns)
# ---------------------------------------------------------
fake_titles = [
    "Work From Home - Earn Daily Cash", "Urgent Hiring - Data Entry (No Skills Needed)",
    "Online Typing Job - Huge Income", "Part Time Job - Easy Money",
    "Immediate Joining - Copy Paste Work", "Earn $5000 Weekly From Home",
    "Govt Job Guarantee - Apply Now", "WhatsApp Job - Instant Payment",
    "Online Survey Job - No Investment Needed*", "Form Filling Job - Limited Vacancy"
]

fake_descriptions = [
    "Earn upto Rs. 50,000 per week working only 2 hours a day from home!! "
    "No experience needed, no qualifications required. Limited seats available, "
    "apply immediately!!!",
    "Congratulations!! You have been shortlisted for this job. To confirm your "
    "selection, please pay a small registration fee of Rs.500 to our company "
    "account. Hurry up offer ends soon.",
    "We guarantee 100% job placement with high salary packages. Just deposit "
    "a refundable security amount and start earning from day 1. No interview required.",
    "This is a golden opportunity to earn money sitting at home. Send your "
    "Aadhar card, bank details and processing fee to start your job today.",
    "We are urgently hiring candidates for online work. Salary is very very "
    "high, upto 1 lakh per month guarenteed. Contact us on whatsapp only."
]

fake_requirements = [
    "No qualification required, no experience required, just a smartphone and internet.",
    "Anyone can apply, students, housewives, retired person all are eligibel.",
    "Must be ready to pay registration amount for kit and training material.",
    "Send copy of ID proof and bank passbook for verification before joining."
]

fake_companies = [
    "Global Earn Solutions", "Quick Cash Pvt Ltd", "Online Job Hub",
    "Easy Income Network", "WorkFromHome Experts", "", "N/A", "Private Limited"
]

fake_domains = ["gmail.com", "rediffmail.com", "yahoo.in", "outlook.in", "tempmail.com"]

fake_salaries = ["50000-100000 (Daily)", "5000$ per week", "1,00,000/month Guaranteed",
                  "Unlimited Earning", "No Fixed Salary - Commission Based"]

fake_locations = ["Work From Home", "Anywhere", "Online", "Not Specified"]


def make_genuine_row():
    title = random.choice(genuine_titles)
    desc = random.choice(genuine_descriptions).format(title=title)
    return {
        "title": title,
        "company_profile": random.choice(genuine_companies) + " is a leading IT services company.",
        "description": desc,
        "requirements": random.choice(genuine_requirements),
        "salary": random.choice(genuine_salaries),
        "company_email_domain": random.choice(genuine_domains),
        "location": random.choice(genuine_locations),
        "fraudulent": 0
    }


def make_fake_row():
    title = random.choice(fake_titles)
    desc = random.choice(fake_descriptions)
    return {
        "title": title,
        "company_profile": random.choice(fake_companies),
        "description": desc,
        "requirements": random.choice(fake_requirements),
        "salary": random.choice(fake_salaries),
        "company_email_domain": random.choice(fake_domains),
        "location": random.choice(fake_locations),
        "fraudulent": 1
    }


def main(num_genuine=400, num_fake=400, seed=42):
    random.seed(seed)
    rows = [make_genuine_row() for _ in range(num_genuine)]
    rows += [make_fake_row() for _ in range(num_fake)]
    random.shuffle(rows)

    df = pd.DataFrame(rows)
    df.to_csv("fake_job_postings.csv", index=False)
    print(f"Dataset generated: {len(df)} rows")
    print(df['fraudulent'].value_counts())


if __name__ == "__main__":
    main()
