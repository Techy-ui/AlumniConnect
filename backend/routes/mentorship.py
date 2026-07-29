from flask import Blueprint, render_template, request, redirect, session, flash, url_for
from db import get_connection
from notification import create_notification

mentorship_bp = Blueprint("mentorship", __name__)

# ------------------------------
# Browse Mentors (Students)
# ------------------------------

@mentorship_bp.route("/mentors")
def browse_mentors():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            alumni_id,
            full_name,
            company,
            designation,
            experience,
            location,
            skills
        FROM alumni
        ORDER BY full_name
    """)

    mentors = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "mentorship/browse_mentors.html",
        mentors=mentors
    )

@mentorship_bp.route("/mentor/<int:alumni_id>")
def mentor_profile(alumni_id):

    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM alumni
        WHERE alumni_id=%s
    """, (alumni_id,))

    mentor = cur.fetchone()

    cur.close()
    conn.close()

    return render_template(
        "mentorship/mentor_profile.html",
        mentor=mentor
    )


@mentorship_bp.route(
    "/request_mentorship/<int:alumni_id>",
    methods=["GET", "POST"]
)
def request_mentorship(alumni_id):

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "student":
        flash("Only students can request mentorship.", "danger")
        return redirect("/login")

    if request.method == "POST":

        subject = request.form["subject"]
        message = request.form["message"]

        conn = get_connection()
        cur = conn.cursor()

        # Prevent duplicate pending requests
        cur.execute("""
            SELECT *
            FROM mentorship_requests
            WHERE student_id=%s
            AND alumni_id=%s
            AND status='Pending'
        """,
        (
            session["user_id"],
            alumni_id
        ))

        existing = cur.fetchone()

        if existing:

            flash(
                "You already have a pending request.",
                "warning"
            )

            cur.close()
            conn.close()

            return redirect(url_for(
                "mentorship.mentor_profile",
                alumni_id=alumni_id
            ))

        cur.execute("""
            INSERT INTO mentorship_requests
            (
                student_id,
                alumni_id,
                subject,
                message
            )
            VALUES
            (%s,%s,%s,%s)
        """,
        (
            session["user_id"],
            alumni_id,
            subject,
            message
        ))

        conn.commit()

        create_notification(
            "alumni",
            alumni_id,
            "New Mentorship Request",
            "A student has requested mentorship."
        )

        cur.close()
        conn.close()

        flash(
            "Mentorship request sent successfully!",
            "success"
        )

        return redirect(url_for("mentorship.browse_mentors"))

    return render_template(
        "mentorship/request_mentorship.html",
        alumni_id=alumni_id
    )

# ------------------------------
# My Mentorship Requests (Student)
# ------------------------------

@mentorship_bp.route("/my_mentorships")
def my_mentorships():

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "student":
        return redirect("/login")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            mr.*,
            a.full_name,
            a.company,
            a.designation
        FROM mentorship_requests mr
        JOIN alumni a
        ON mr.alumni_id = a.alumni_id
        WHERE mr.student_id=%s
        ORDER BY mr.request_date DESC
    """, (session["user_id"],))

    requests = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "mentorship/my_mentorships.html",
        requests=requests
    )


# ------------------------------
# Manage Requests (Alumni)
# ------------------------------

@mentorship_bp.route("/manage_requests")
def manage_requests():

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "alumni":
        return redirect("/login")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            mr.*,
            s.full_name,
            s.department,
            s.current_year,
            s.skills,
            s.profile_photo
        FROM mentorship_requests mr
        JOIN students s
        ON mr.student_id = s.student_id
        WHERE mr.alumni_id=%s
        ORDER BY mr.request_date DESC
    """, (session["user_id"],))

    requests = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "mentorship/manage_requests.html",
        requests=requests
    )


@mentorship_bp.route(
    "/respond_request/<int:request_id>",
    methods=["GET", "POST"]
)
def respond_request(request_id):

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "alumni":
        return redirect("/login")

    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":

        response_message = request.form["response_message"]
        meeting_date = request.form["meeting_date"]
        meeting_time = request.form["meeting_time"]
        meeting_link = request.form["meeting_link"]

        cur.execute("""
            UPDATE mentorship_requests
            SET
                status='Accepted',
                response_message=%s,
                meeting_date=%s,
                meeting_time=%s,
                meeting_link=%s
            WHERE request_id=%s
            AND alumni_id=%s
        """,
        (
            response_message,
            meeting_date,
            meeting_time,
            meeting_link,
            request_id,
            session["user_id"]
        ))

        conn.commit()

        cur.execute("""
            SELECT student_id
            FROM mentorship_requests
            WHERE request_id=%s
        """,(request_id,))

        student = cur.fetchone()

        if student:

            create_notification(
                "student",
                student["student_id"],
                "Mentorship Accepted",
                "Your mentorship request has been accepted."
            )

        cur.close()
        conn.close()

        flash(
            "Mentorship request accepted successfully.",
            "success"
        )

        return redirect(url_for("mentorship.manage_requests"))

    cur.execute("""
        SELECT
            mr.*,
            s.full_name
        FROM mentorship_requests mr
        JOIN students s
        ON mr.student_id=s.student_id
        WHERE mr.request_id=%s
        AND mr.alumni_id=%s
    """,
    (
        request_id,
        session["user_id"]
    ))

    mentorship = cur.fetchone()

    cur.close()
    conn.close()

    return render_template(
        "mentorship/respond_request.html",
        mentorship=mentorship
    )
# ------------------------------
# Accept Request
# ------------------------------

@mentorship_bp.route("/accept_request/<int:request_id>")
def accept_request(request_id):

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "alumni":
        return redirect("/login")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE mentorship_requests
    SET status='Accepted'
    WHERE request_id=%s
    AND alumni_id=%s
""", (
    request_id,
    session["user_id"]
))

    conn.commit()

    cur.execute("""
        SELECT student_id
        FROM mentorship_requests
        WHERE request_id=%s
    """, (request_id,))

    student = cur.fetchone()

    if student:
        create_notification(
            "student",
            student["student_id"],
            "Mentorship Accepted",
            "Your mentorship request has been accepted."
        )

    cur.close()
    conn.close()

    flash(
        "Request accepted successfully.",
        "success"
    )

    return redirect(url_for("mentorship.manage_requests"))



# ------------------------------
# Reject Request
# ------------------------------

@mentorship_bp.route("/reject_request/<int:request_id>")
def reject_request(request_id):

    if "user_id" not in session:
        return redirect("/login")

    if session["role"] != "alumni":
        return redirect("/login")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    UPDATE mentorship_requests
    SET status='Rejected'
    WHERE request_id=%s
    AND alumni_id=%s
""", (
    request_id,
    session["user_id"]
))
    conn.commit()

    cur.execute("""
        SELECT student_id
        FROM mentorship_requests
        WHERE request_id=%s
    """, (request_id,))

    student = cur.fetchone()

    if student:
        create_notification(
            "student",
            student["student_id"],
            "Mentorship Rejected",
            "Your mentorship request has been rejected."
        )

    cur.close()
    conn.close()

    flash(
        "Request rejected.",
        "success"
    )

    return redirect(url_for("mentorship.manage_requests"))



