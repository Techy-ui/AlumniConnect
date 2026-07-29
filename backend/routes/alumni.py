from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    flash,
    session,
    url_for
)
from werkzeug.security import generate_password_hash
from db import get_connection
alumni_bp = Blueprint("alumni", __name__)

@alumni_bp.route("/alumni/add_alumni", methods=["GET","POST"])
def add_alumni():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = generate_password_hash(
            request.form["password"]
        )
        year = request.form["year"]
        department = request.form["department"]
        company = request.form["company"]
        designation = request.form["designation"]
        experience = request.form["experience"]
        location = request.form["location"]
        bio = request.form["bio"]
        linkedin = request.form["linkedin"]
        github = request.form["github"]
        skills = request.form["skills"]

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO alumni
            (
                full_name,
                email,
                password,
                graduation_year,
                department,
                company,
                designation,
                experience,
                location,
                skills,
                bio,
                linkedin,
                github
            )
            VALUES
            (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                name,
                email,
                password,
                year,
                department,
                company,
                designation,
                experience,
                location,
                skills,
                bio,
                linkedin,
                github
            ))

        conn.commit()

        cur.close()
        conn.close()

        return redirect("/")

    return render_template("alumni/add_alumni.html")

@alumni_bp.route("/alumni/explore_alumni")
def explore_alumni():

    query = request.args.get("query", "")

    conn = get_connection()
    cur = conn.cursor()

    if query:

        cur.execute("""

        SELECT *

        FROM alumni

        WHERE

            LOWER(full_name) LIKE LOWER(%s)

            OR LOWER(company) LIKE LOWER(%s)

            OR LOWER(department) LIKE LOWER(%s)

            OR LOWER(skills) LIKE LOWER(%s)

        ORDER BY full_name

        """,

        (
            f"%{query}%",
            f"%{query}%",
            f"%{query}%",
            f"%{query}%"
        ))

    else:

        cur.execute("""

        SELECT *

        FROM alumni

        ORDER BY full_name

        """)

    alumni = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "alumni/explore_alumni.html",
        alumni=alumni,
        query=query
    )

@alumni_bp.route("/alumni/alumni_profile")
def alumni_profile():

    if session.get("role") != "alumni":
        return redirect(url_for("auth.login"))

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM alumni
        WHERE alumni_id = %s
    """, (session["user_id"],))

    person = cur.fetchone()

    cur.close()
    conn.close()

    return render_template(
        "alumni/alumni_profile.html",
        person=person
    )



@alumni_bp.route("/alumni/alumni_dashboard")
def alumni_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    cur = conn.cursor()

    alumni_id = session["user_id"]

    # Alumni details
    cur.execute("""
        SELECT *
        FROM alumni
        WHERE alumni_id=%s
    """, (alumni_id,))
    alumni = cur.fetchone()

    # Total jobs
    cur.execute("""
        SELECT COUNT(*) AS count
        FROM jobs
        WHERE alumni_id=%s
    """, (alumni_id,))
    total_jobs = cur.fetchone()["count"]

    # Total mentorship requests
    cur.execute("""
        SELECT COUNT(*) AS count
        FROM mentorship_requests
        WHERE alumni_id=%s
    """, (alumni_id,))
    total_requests = cur.fetchone()["count"]

    # Total applications
    cur.execute("""
        SELECT COUNT(*) AS count
        FROM job_applications ja
        JOIN jobs j
        ON ja.job_id = j.job_id
        WHERE j.alumni_id=%s
    """, (alumni_id,))
    total_applications = cur.fetchone()["count"]

    # Recent jobs
    cur.execute("""
        SELECT *
        FROM jobs
        WHERE alumni_id=%s
        ORDER BY created_at DESC
    """, (alumni_id,))
    jobs = cur.fetchall()

    # Recent mentorship requests
    cur.execute("""
        SELECT
            mr.*,
            s.full_name AS student_name,
            s.department
        FROM mentorship_requests mr
        JOIN students s
        ON mr.student_id = s.student_id
        WHERE mr.alumni_id = %s
        ORDER BY mr.request_date DESC
    """, (alumni_id,))
    mentorship_requests = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "alumni/alumni_dashboard.html",
        alumni=alumni,
        total_jobs=total_jobs,
        total_requests=total_requests,
        total_applications=total_applications,
        jobs=jobs,
        mentorship_requests=mentorship_requests
    )

@alumni_bp.route("/alumni/explore_students")
def explore_students():

    if "user_id" not in session:
        return redirect("/login")

    search = request.args.get("search", "").strip()
    department = request.args.get("department", "").strip()
    batch = request.args.get("batch", "").strip()

    conn = get_connection()
    cur = conn.cursor()

    query = """
        SELECT *
        FROM students
        WHERE 1=1
    """

    params = []

    if search:
        query += """
            AND (
                LOWER(full_name) LIKE LOWER(%s)
                OR LOWER(department) LIKE LOWER(%s)
                OR LOWER(skills) LIKE LOWER(%s)
            )
        """
        params.extend([
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        ])

    if department:
        query += " AND department = %s"
        params.append(department)

    if batch:
        query += " AND graduation_year = %s"
        params.append(batch)

    query += " ORDER BY full_name"

    cur.execute(query, params)

    students = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "alumni/explore_students.html",
        students=students
    )


@alumni_bp.route("/alumni/analytics")
def analytics():

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "alumni":
        return redirect("/login")

    conn = get_connection()
    cur = conn.cursor()

    alumni_id = session["user_id"]

    # Total jobs
    cur.execute("""
        SELECT COUNT(*)
        FROM jobs
        WHERE alumni_id=%s
    """, (alumni_id,))
    total_jobs = cur.fetchone()["count"]

    # Total mentorship requests
    cur.execute("""
        SELECT COUNT(*)
        FROM mentorship_requests
        WHERE alumni_id=%s
    """, (alumni_id,))
    total_requests = cur.fetchone()["count"]

    # Total applications
    cur.execute("""
        SELECT COUNT(*)
        FROM job_applications ja
        JOIN jobs j
        ON ja.job_id=j.job_id
        WHERE j.alumni_id=%s
    """, (alumni_id,))
    total_applications = cur.fetchone()["count"]

    # Accepted applications
    cur.execute("""
        SELECT COUNT(*)
        FROM job_applications ja
        JOIN jobs j
        ON ja.job_id=j.job_id
        WHERE j.alumni_id=%s
        AND ja.status='Accepted'
    """, (alumni_id,))
    accepted = cur.fetchone()["count"]

    # Applications per Job
    cur.execute("""
        SELECT
            j.job_title,
            COUNT(ja.application_id) AS applicants
        FROM jobs j
        LEFT JOIN job_applications ja
        ON j.job_id=ja.job_id
        WHERE j.alumni_id=%s
        GROUP BY j.job_title
        ORDER BY applicants DESC
    """, (alumni_id,))

    applications_chart = cur.fetchall()

    # Mentorship status
    cur.execute("""
        SELECT
            status,
            COUNT(*) AS total
        FROM mentorship_requests
        WHERE alumni_id=%s
        GROUP BY status
    """, (alumni_id,))

    mentorship_chart = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "alumni/analytics.html",
        total_jobs=total_jobs,
        total_requests=total_requests,
        total_applications=total_applications,
        accepted=accepted,
        applications_chart=applications_chart,
        mentorship_chart=mentorship_chart
    )