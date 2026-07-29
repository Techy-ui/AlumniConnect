from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    flash,
    session
)

from db import get_connection

from notification import create_notification

jobs_bp = Blueprint("jobs", __name__)

@jobs_bp.route("/post_job", methods=["GET","POST"])
def post_job():

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "alumni":
        return redirect("/login")

    if request.method == "POST":

        company = request.form["company"]
        job_title = request.form["job_title"]
        location = request.form["location"]
        job_type = request.form["job_type"]
        salary = request.form["salary"]
        description = request.form["description"]
        skills_required = request.form["skills_required"]
        deadline = request.form["deadline"]

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO jobs
        (
            alumni_id,
            company,
            job_title,
            location,
            job_type,
            salary,
            description,
            skills_required,
            deadline
        )
        VALUES
        (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            session["user_id"],
            company,
            job_title,
            location,
            job_type,
            salary,
            description,
            skills_required,
            deadline
        ))

        conn.commit()

        cur.close()
        conn.close()

        flash("Job posted successfully!", "success")

        return redirect("/alumni/alumni_dashboard")

    return render_template("jobs/post_job.html")

@jobs_bp.route("/jobs")
def browse_jobs():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            j.*,
            a.full_name
        FROM jobs j
        JOIN alumni a
        ON j.alumni_id = a.alumni_id
        ORDER BY created_at DESC
    """)

    jobs = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "jobs/browse_jobs.html",
        jobs=jobs
    )

@jobs_bp.route("/job/<int:job_id>")
def job_details(job_id):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            j.*,
            a.full_name
        FROM jobs j
        JOIN alumni a
        ON j.alumni_id=a.alumni_id
        WHERE job_id=%s
    """,(job_id,))

    job = cur.fetchone()

    cur.close()
    conn.close()

    return render_template(
        "jobs/job_details.html",
        job=job
    )

@jobs_bp.route("/apply/<int:job_id>")
def apply_job(job_id):

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "student":
        flash("Only students can apply.", "danger")
        return redirect("/login")

    conn = get_connection()
    cur = conn.cursor()

    # Check duplicate application
    cur.execute("""
        SELECT *
        FROM job_applications
        WHERE job_id=%s
        AND student_id=%s
    """,
    (
        job_id,
        session["user_id"]
    ))

    existing = cur.fetchone()

    if existing:

        flash(
            "You have already applied for this job.",
            "warning"
        )

        cur.close()
        conn.close()

        return redirect(f"/job/{job_id}")

    cur.execute("""
        INSERT INTO job_applications
        (
            job_id,
            student_id
        )
        VALUES
        (%s,%s)
    """,
    (
        job_id,
        session["user_id"]
    ))

    conn.commit()

    # Find alumni who posted the job
    cur.execute("""
        SELECT alumni_id
        FROM jobs
        WHERE job_id=%s
    """, (job_id,))

    job = cur.fetchone()

    if job:
        create_notification(
            "alumni",
            job["alumni_id"],
            "New Job Application",
            "A student has applied for your job posting."
        )

    cur.close()
    conn.close()

    flash(
        "Application submitted successfully!",
        "success"
    )

    return redirect("/jobs")

@jobs_bp.route("/my_jobs")
def my_jobs():

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "alumni":
        return redirect("/login")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            j.job_id,
            j.company,
            j.job_title,
            j.location,
            j.job_type,
            j.deadline,
            COUNT(ja.application_id) AS applicants

        FROM jobs j

        LEFT JOIN job_applications ja
        ON j.job_id = ja.job_id

        WHERE j.alumni_id=%s

        GROUP BY
            j.job_id,
            j.company,
            j.job_title,
            j.location,
            j.job_type,
            j.deadline

        ORDER BY j.created_at DESC
    """, (session["user_id"],))

    jobs = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "jobs/my_jobs.html",
        jobs=jobs
    )

@jobs_bp.route("/view_applicants/<int:job_id>")
def view_applicants(job_id):

    if session.get("role") != "alumni":
        return redirect("/login")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT

            ja.application_id,

            ja.status,

            s.student_id,

            s.full_name,

            s.department,

            s.current_year,

            s.skills,

            s.github,

            s.linkedin

        FROM job_applications ja

        JOIN students s

        ON ja.student_id=s.student_id

        WHERE ja.job_id=%s

        ORDER BY ja.applied_at DESC
    """,(job_id,))

    applicants = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "jobs/applicants.html",
        applicants=applicants
    )

@jobs_bp.route(
    "/respond_application/<int:application_id>",
    methods=["GET", "POST"]
)
def respond_application(application_id):

    if session.get("role") != "alumni":
        return redirect("/login")

    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":

        response_message = request.form["response_message"]
        interview_date = request.form["interview_date"]
        interview_time = request.form["interview_time"]
        interview_link = request.form["interview_link"]

        cur.execute("""
            UPDATE job_applications
            SET
                status='Accepted',
                response_message=%s,
                interview_date=%s,
                interview_time=%s,
                interview_link=%s
            WHERE application_id=%s
        """,
        (
            response_message,
            interview_date,
            interview_time,
            interview_link,
            application_id
        ))

        conn.commit()

        cur.execute("""
            SELECT student_id
            FROM job_applications
            WHERE application_id=%s
        """,(application_id,))

        student = cur.fetchone()

        if student:

            create_notification(
                "student",
                student["student_id"],
                "Application Accepted",
                "Congratulations! Your application has been accepted."
            )

        cur.close()
        conn.close()

        flash(
            "Applicant accepted successfully.",
            "success"
        )

        return redirect("/my_jobs")

    cur.execute("""
        SELECT
            ja.*,
            s.full_name
        FROM job_applications ja
        JOIN students s
        ON ja.student_id=s.student_id
        WHERE ja.application_id=%s
    """,(application_id,))

    applicant = cur.fetchone()

    cur.close()
    conn.close()

    return render_template(
        "jobs/respond_application.html",
        applicant=applicant
    )

@jobs_bp.route("/accept_application/<int:application_id>")
def accept_application(application_id):

    if session.get("role") != "alumni":
        return redirect("/login")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT student_id
        FROM job_applications
        WHERE application_id=%s
    """, (application_id,))

    student = cur.fetchone()

    cur.execute("""
        UPDATE job_applications
        SET status='Accepted'
        WHERE application_id=%s
    """, (application_id,))

    conn.commit()

    if student:
        create_notification(
            "student",
            student["student_id"],
            "Application Accepted",
            "Congratulations! Your job application has been accepted."
        )

    cur.close()
    conn.close()

    flash("Application Accepted.", "success")

    return redirect(request.referrer)

@jobs_bp.route("/reject_application/<int:application_id>")
def reject_application(application_id):

    if session.get("role") != "alumni":
        return redirect("/login")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT student_id
        FROM job_applications
        WHERE application_id=%s
    """, (application_id,))

    student = cur.fetchone()

    cur.execute("""
        UPDATE job_applications
        SET status='Rejected'
        WHERE application_id=%s
    """, (application_id,))

    conn.commit()

    if student:
        create_notification(
            "student",
            student["student_id"],
            "Application Rejected",
            "Your application was not selected this time."
        )

    cur.close()
    conn.close()

    flash("Application Rejected.", "warning")

    return redirect(request.referrer)

@jobs_bp.route("/my_applications")
def my_applications():

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "student":
        return redirect("/login")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT

            ja.*,

            j.company,

            j.job_title,

            j.location,

            j.job_type

        FROM job_applications ja

        JOIN jobs j
        ON ja.job_id=j.job_id

        WHERE ja.student_id=%s

        ORDER BY ja.applied_at DESC
    """,(session["user_id"],))

    applications = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "jobs/my_applications.html",
        applications=applications
    )