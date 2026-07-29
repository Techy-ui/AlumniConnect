from flask import Flask, render_template, request, redirect, flash, session
from db import get_connection
from werkzeug.security import generate_password_hash, check_password_hash
from notification import (
    create_notification,
    get_notifications,
    get_unread_count,
    mark_as_read,
    mark_all_as_read,
    delete_notification
)
import os
from routes.auth import auth_bp
from routes.student import student_bp
from routes.alumni import alumni_bp
from routes.mentorship import mentorship_bp
from routes.jobs import jobs_bp
from routes.notifications import notifications_bp
from routes.settings import settings_bp

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static")
)

@app.context_processor
def inject_notification_count():

    if "user_id" not in session:
        return {"unread_count": 0}

    return {
        "unread_count": get_unread_count(
            session["role"],
            session["user_id"]
        )
    }

app.config["UPLOAD_FOLDER"] = "static/uploads/resumes"
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024   # 10 MB

app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(alumni_bp)
app.register_blueprint(mentorship_bp)
app.register_blueprint(jobs_bp)
app.register_blueprint(notifications_bp)
app.register_blueprint(settings_bp)


app.secret_key = "alumniconnect_secret_key"

@app.route("/")
def home():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) AS total FROM alumni")
    alumni_count = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS total FROM students")
    student_count = cur.fetchone()["total"]

    cur.execute("""
    SELECT alumni_id,
        full_name,
        company,
        designation
    FROM alumni
    ORDER BY alumni_id DESC
    """)

    alumni = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "pages/home.html",
        alumni=alumni,
        alumni_count=alumni_count,
        student_count=student_count
    )





@app.route("/search")
def search():

    query = request.args.get("query", "")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""

        SELECT
            alumni_id,
            full_name,
            company,
            designation,
            department,
            skills

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

    results = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "pages/search.html",
        query=query,
        results=results
    )


@app.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out successfully.", "success")

    return redirect("/login")




@app.route("/notifications")
def notifications():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""

        SELECT *

        FROM notifications

        WHERE user_role=%s

        AND user_id=%s

        ORDER BY created_at DESC

    """,
    (
        session["role"],
        session["user_id"]
    ))

    notifications = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        "notifications.html",
        notifications=notifications
    )

if __name__ == "__main__":
    app.run(debug=True)

