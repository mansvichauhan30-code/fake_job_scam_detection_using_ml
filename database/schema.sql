-- ============================================================
-- Fake Job Scam Detection System - Database Schema
-- Database: MySQL
-- ============================================================

CREATE DATABASE IF NOT EXISTS fake_job_detection;
USE fake_job_detection;

-- ------------------------------------------------------------
-- Table: users
-- Stores registered users (job seekers) and admins
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin') DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ------------------------------------------------------------
-- Table: job_analyses
-- Stores every job posting analyzed by users along with results
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS job_analyses (
    analysis_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    job_title VARCHAR(200) NOT NULL,
    company_profile TEXT,
    job_description TEXT NOT NULL,
    requirements TEXT,
    salary VARCHAR(100),
    company_email_domain VARCHAR(100),
    location VARCHAR(150),

    -- ML Prediction results
    prediction ENUM('FAKE', 'GENUINE') NOT NULL,
    scam_probability DECIMAL(5,2) NOT NULL,  -- 0.00 to 100.00

    -- AI generated explanation
    ai_explanation TEXT,

    -- Red flags stored as JSON for flexibility
    red_flags JSON,
    red_flag_count INT DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_job_analyses_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- Table: red_flag_master (optional reference table)
-- Master list of red flag types for consistent reporting
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS red_flag_master (
    flag_id INT AUTO_INCREMENT PRIMARY KEY,
    flag_name VARCHAR(100) NOT NULL UNIQUE,
    flag_description TEXT
);

INSERT INTO red_flag_master (flag_name, flag_description) VALUES
('Unrealistic Salary', 'Salary offered seems unrealistically high or vague for the role described.'),
('No Company Details', 'Company profile is missing, too short, or not specified.'),
('Asking for Money', 'Posting asks the candidate to pay a fee, deposit, or other charges.'),
('Suspicious Email Domain', 'Recruiter email domain is associated with temporary/suspicious mail services.'),
('Grammar / Spelling Issues', 'Posting contains spelling mistakes, excessive punctuation, or unusual formatting.'),
('Urgency / Pressure Tactics', 'Posting uses urgency phrases to pressure quick action.'),
('Unrealistic Claims', 'Posting makes unrealistic promises such as guaranteed jobs with no experience.');

-- ------------------------------------------------------------
-- Indexes for performance
-- ------------------------------------------------------------
CREATE INDEX idx_job_analyses_user ON job_analyses(user_id);
CREATE INDEX idx_job_analyses_prediction ON job_analyses(prediction);
CREATE INDEX idx_job_analyses_created ON job_analyses(created_at);

-- ------------------------------------------------------------
-- Create the admin account with app/seed_admin.py after configuring its environment variables.
-- Actual hash should be generated via the app's registration/seed script
-- ------------------------------------------------------------
-- INSERT INTO users (full_name, email, password_hash, role)
-- VALUES ('System Admin', 'admin@fakejobdetector.com', '<bcrypt_hash_here>', 'admin');
