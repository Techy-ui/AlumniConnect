
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    flash,
    session
)
from werkzeug.security import check_password_hash
from db import get_connection
from notification import create_notification

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    # If already logged in, redirect to the appropriate dashboard
    if "user_id" in session:
        if session.get("role") == "student":
            return redirect("/students/student_dashboard")
        elif session.get("role") == "alumni":
            return redirect("/alumni/alumni_dashboard")

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        conn = get_connection()
        cur = conn.cursor()

        if role == "student":

            cur.execute(
                "SELECT * FROM students WHERE email = %s",
                (email,)
            )

            user = cur.fetchone()

            if user:
                if check_password_hash(user["password"], password):

                    session["user_id"] = user["student_id"]
                    session["role"] = "student"

                    flash(f"Welcome back, {user['full_name']}!", "success")

                    cur.close()
                    conn.close()

                    session["show_notification_toast"] = True

                    return redirect("/students/student_dashboard")

        elif role == "alumni":

            cur.execute(
                "SELECT * FROM alumni WHERE email = %s",
                (email,)
            )

            user = cur.fetchone()

            if user:
                if check_password_hash(user["password"], password):

                    session["user_id"] = user["alumni_id"]
                    session["role"] = "alumni"

                    flash(f"Welcome back, {user['full_name']}!", "success")

                    cur.close()
                    conn.close()

                    session["show_notification_toast"] = True

                    return redirect("/alumni/alumni_dashboard")

        cur.close()
        conn.close()

        flash("Invalid email or password!", "danger")

    return render_template("auth/login.html")

from flask import session, redirect, url_for, flash

@auth_bp.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out successfully.", "success")

    return redirect(url_for("auth.login"))