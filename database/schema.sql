alumniconnect=# CREATE TABLE alumni (

    alumni_id SERIAL PRIMARY KEY,

    full_name VARCHAR(100) NOT NULL,

    email VARCHAR(100) UNIQUE NOT NULL,

    graduation_year INT,

    department VARCHAR(50),

    company VARCHAR(100),

    designation VARCHAR(100),

    skills TEXT,

    linkedin_url VARCHAR(255)

);

CREATE TABLE

alumniconnect=# CREATE TABLE students (

    student_id SERIAL PRIMARY KEY,

    full_name VARCHAR(100) NOT NULL,

    email VARCHAR(100) UNIQUE NOT NULL,

    department VARCHAR(50),

    current_year INT,

    interests TEXT

);

CREATE TABLE

alumniconnect=# CREATE TABLE mentorship_requests (

    request_id SERIAL PRIMARY KEY,

    student_id INT REFERENCES students(student_id),

    alumni_id INT REFERENCES alumni(alumni_id),

    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    status VARCHAR(20) DEFAULT 'Pending'

);

CREATE TABLE

alumniconnect=# CREATE TABLE opportunities (

    opportunity_id SERIAL PRIMARY KEY,

    alumni_id INT REFERENCES alumni(alumni_id),

    title VARCHAR(200),

    company VARCHAR(100),

    description TEXT,

    posted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

CREATE TABLE

alumniconnect=# \dt

                List of relations

 Schema |        Name         | Type  |  Owner

--------+---------------------+-------+----------

 public | alumni              | table | postgres

 public | mentorship_requests | table | postgres

 public | opportunities       | table | postgres

 public | students            | table | postgres

(4 rows)
