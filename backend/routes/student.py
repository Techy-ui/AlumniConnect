import os

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    flash,
    session,
    current_app
)

from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from db import get_connection
student_bp = Blueprint("student", __name__)

@student_bp.route("/students/student_register", methods=["GET","POST"])
def student_register():

    if request.method == "POST":

        full_name = request.form["full_name"]
        email = request.form["email"]

        password = generate_password_hash(
            request.form["password"]
        )

        department = request.form["department"]
        current_year = request.form["current_year"]
        skills = request.form["skills"]
        interests = request.form["interests"]
        linkedin = request.form["linkedin"]
        github = request.form["github"]

        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT student_id FROM students WHERE email = %s",
            (email,)
        )

        existing_student = cur.fetchone()

        if existing_student:
            cur.close()
            conn.close()

            flash("⚠ This email is already registered. Please login instead.", "warning")

            return redirect("/students/student_register")

        cur.execute("""
            INSERT INTO students
            (
                full_name,
                email,
                password,
                department,
                current_year,
                skills,
                interests,
                linkedin,
                github
            )
            VALUES
            (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING student_id
            """,
            (
                full_name,
                email,
                password,
                department,
                current_year,
                skills,
                interests,
                linkedin,
                github
            ))

        student = cur.fetchone()
        student_id = student["student_id"]

        conn.commit()

        cur.close()
        conn.close()

        return redirect("/students/student_dashboard")

    return render_template("students/student_register.html")

@student_bp.route("/students/student_dashboard")
def student_dashboard():

    if "user_id" not in session:
        flash("Please login first.", "warning")
        return redirect("/login")

    if session.get("role") != "student":
        flash("Access denied.", "danger")
        return redirect("/login")

    conn = get_connection()
    cur = conn.cursor()

    student_id = session["user_id"]

    cur.execute("""
        SELECT *
        FROM students
        WHERE student_id = %s
    """, (student_id,))

    student = cur.fetchone()

    cur.execute("""
        SELECT *
        FROM alumni
        WHERE department = %s
        LIMIT 5
    """, (student["department"],))

    recommendations = cur.fetchall()


    
    cur.close()
    conn.close()

    return render_template(
        "students/student_dashboard.html",
        student=student,
        recommendations=recommendations
    )

@student_bp.route("/students/profile", methods=["GET", "POST"])
def student_profile():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":

        # -------------------------
        # Upload Profile Photo
        # -------------------------

        profile_photo = request.files.get("profile_photo")
        photo_filename = None

        if profile_photo and profile_photo.filename != "":

            photo_filename = secure_filename(profile_photo.filename)

            photo_path = os.path.join(
                current_app.static_folder,
                "uploads",
                "profile_photos",
                photo_filename
            )

            os.makedirs(os.path.dirname(photo_path), exist_ok=True)

            profile_photo.save(photo_path)

        # -------------------------
        # Upload Resume
        # -------------------------

        resume = request.files.get("resume")
        resume_filename = None

        if resume and resume.filename != "":

            resume_filename = secure_filename(resume.filename)

            resume_path = os.path.join(
                current_app.static_folder,
                "uploads",
                "resumes",
                resume_filename
            )

            os.makedirs(os.path.dirname(resume_path), exist_ok=True)

            resume.save(resume_path)

        # -------------------------
        # Update Database
        # -------------------------

        cur.execute("""
        UPDATE students
        SET
            full_name=%s,
            email=%s,
            department=%s,
            current_year=%s,
            skills=%s,
            bio=%s,
            github=%s,
            linkedin=%s,
            profile_photo=COALESCE(%s, profile_photo),
            resume=COALESCE(%s, resume)
        WHERE student_id=%s
        """,
        (
            request.form["full_name"],
            request.form["email"],
            request.form["department"],
            request.form["current_year"],
            request.form["skills"],
            request.form["bio"],
            request.form["github"],
            request.form["linkedin"],
            photo_filename,
            resume_filename,
            session["user_id"]
        ))

        conn.commit()

        flash(
            "Profile Updated Successfully!",
            "success"
        )

    cur.execute("""
        SELECT *
        FROM students
        WHERE student_id=%s
    """, (session["user_id"],))

    student = cur.fetchone()

    cur.close()
    conn.close()

    return render_template(
        "students/profile.html",
        student=student
    )

@student_bp.route("/student/analytics")
def student_analytics():

    if session.get("role") != "student":
        return redirect(url_for("auth.login"))

    conn = get_connection()
    cur = conn.cursor()

    student_id = session["user_id"]

    # Applications
    cur.execute("""
        SELECT COUNT(*) AS total
        FROM job_applications
        WHERE student_id=%s
    """,(student_id,))
    applications = cur.fetchone()["total"]

    # Mentorship Requests
    cur.execute("""
        SELECT COUNT(*) AS total
        FROM mentorship_requests
        WHERE student_id=%s
    """,(student_id,))
    mentorships = cur.fetchone()["total"]

    # Notifications
    cur.execute("""
        SELECT COUNT(*) AS total
        FROM notifications
        WHERE user_role='student'
        AND user_id=%s
    """,(student_id,))
    notifications = cur.fetchone()["total"]

    # Jobs Available
    cur.execute("""
        SELECT COUNT(*) AS total
        FROM jobs
    """)
    jobs = cur.fetchone()["total"]

    cur.close()
    conn.close()

    return render_template(
        "students/analytics.html",
        applications=applications,
        mentorships=mentorships,
        notifications=notifications,
        jobs=jobs
    )

@student_bp.route("/students/delete_profile_photo", methods=["POST"])
def delete_profile_photo():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT profile_photo FROM students WHERE student_id=%s",
        (session["user_id"],)
    )

    student = cur.fetchone()

    if student and student["profile_photo"]:

        photo_path = os.path.join(
            current_app.static_folder,
            "uploads",
            "profile_photos",
            student["profile_photo"]
        )

        if os.path.exists(photo_path):
            os.remove(photo_path)

        cur.execute("""
            UPDATE students
            SET profile_photo=NULL
            WHERE student_id=%s
        """, (session["user_id"],))

        session["profile_photo"] = None

        conn.commit()

        flash("Profile photo deleted successfully.","success")

    cur.close()
    conn.close()

    return redirect("/students/profile")

@student_bp.route("/students/delete_resume", methods=["POST"])
def delete_resume():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT resume FROM students WHERE student_id=%s",
        (session["user_id"],)
    )

    student = cur.fetchone()

    if student and student["resume"]:

        resume_path = os.path.join(
            current_app.static_folder,
            "uploads",
            "resumes",
            student["resume"]
        )

        if os.path.exists(resume_path):
            os.remove(resume_path)

        cur.execute("""
            UPDATE students
            SET resume=NULL
            WHERE student_id=%s
        """, (session["user_id"],))

        conn.commit()

        flash("Resume deleted successfully.","success")

    cur.close()
    conn.close()

    return redirect("/students/profile")