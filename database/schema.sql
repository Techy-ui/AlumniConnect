-- Drop existing tables (optional)
DROP TABLE IF EXISTS job_applications CASCADE;
DROP TABLE IF EXISTS jobs CASCADE;
DROP TABLE IF EXISTS mentorship_requests CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS opportunities CASCADE;
DROP TABLE IF EXISTS students CASCADE;
DROP TABLE IF EXISTS alumni CASCADE;

--------------------------------------------------
-- Alumni
--------------------------------------------------

CREATE TABLE alumni (
    alumni_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255),
    graduation_year INT,
    department VARCHAR(100),
    company VARCHAR(150),
    designation VARCHAR(150),
    skills TEXT,
    linkedin_url VARCHAR(255),
    profile_photo VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------
-- Students
--------------------------------------------------

CREATE TABLE students (
    student_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255),
    department VARCHAR(100),
    current_year INT,
    interests TEXT,
    resume VARCHAR(255),
    profile_photo VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------
-- Jobs
--------------------------------------------------

CREATE TABLE jobs (
    job_id SERIAL PRIMARY KEY,
    alumni_id INT REFERENCES alumni(alumni_id) ON DELETE CASCADE,
    company VARCHAR(150) NOT NULL,
    job_title VARCHAR(150) NOT NULL,
    location VARCHAR(150),
    job_type VARCHAR(100),
    description TEXT,
    skills_required TEXT,
    deadline DATE,
    salary VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------
-- Job Applications
--------------------------------------------------

CREATE TABLE job_applications (
    application_id SERIAL PRIMARY KEY,
    job_id INT REFERENCES jobs(job_id) ON DELETE CASCADE,
    student_id INT REFERENCES students(student_id) ON DELETE CASCADE,
    status VARCHAR(30) DEFAULT 'Pending',
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_message TEXT,
    interview_date DATE,
    interview_time TIME,
    interview_link TEXT
);

--------------------------------------------------
-- Mentorship Requests
--------------------------------------------------

CREATE TABLE mentorship_requests (
    request_id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(student_id) ON DELETE CASCADE,
    alumni_id INT REFERENCES alumni(alumni_id) ON DELETE CASCADE,
    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(30) DEFAULT 'Pending',
    subject VARCHAR(255),
    message TEXT,
    response_message TEXT,
    meeting_link TEXT,
    meeting_date DATE,
    meeting_time TIME
);

--------------------------------------------------
-- Opportunities
--------------------------------------------------

CREATE TABLE opportunities (
    opportunity_id SERIAL PRIMARY KEY,
    alumni_id INT REFERENCES alumni(alumni_id) ON DELETE CASCADE,
    title VARCHAR(200),
    company VARCHAR(150),
    description TEXT,
    posted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

--------------------------------------------------
-- Notifications
--------------------------------------------------

CREATE TABLE notifications (
    notification_id SERIAL PRIMARY KEY,
    user_role VARCHAR(20) NOT NULL,
    user_id INT NOT NULL,
    title VARCHAR(255),
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);