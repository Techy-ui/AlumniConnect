from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    flash,
    url_for
)

from werkzeug.security import (
    check_password_hash,
    generate_password_hash
)

from db import get_connection

settings_bp = Blueprint(
    "settings",
    __name__
)

@settings_bp.route("/settings", methods=["GET", "POST"])
def settings():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if request.method == "POST":

        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        conn = get_connection()
        cur = conn.cursor()

        if session["role"] == "student":

            cur.execute("""
                SELECT password
                FROM students
                WHERE student_id=%s
            """, (session["user_id"],))

            user = cur.fetchone()

            table = "students"
            id_column = "student_id"

        else:

            cur.execute("""
                SELECT password
                FROM alumni
                WHERE alumni_id=%s
            """, (session["user_id"],))

            user = cur.fetchone()

            table = "alumni"
            id_column = "alumni_id"

        if not check_password_hash(user["password"], current_password):

            flash("Current password is incorrect.", "danger")

            cur.close()
            conn.close()

            return redirect(url_for("settings.settings"))

        if new_password != confirm_password:

            flash("New passwords do not match.", "danger")

            cur.close()
            conn.close()

            return redirect(url_for("settings.settings"))

        if len(new_password) < 6:

            flash("Password must be at least 6 characters long.", "warning")

            cur.close()
            conn.close()

            return redirect(url_for("settings.settings"))

        hashed_password = generate_password_hash(new_password)

        cur.execute(
            f"""
            UPDATE {table}
            SET password=%s
            WHERE {id_column}=%s
            """,
            (
                hashed_password,
                session["user_id"]
            )
        )

        conn.commit()

        cur.close()
        conn.close()

        flash("Password updated successfully!", "success")

        session.clear()

        flash(
            "Password changed successfully. Please log in again.",
            "success"
        )

        return redirect(url_for("auth.login"))

    return render_template("settings/settings.html")