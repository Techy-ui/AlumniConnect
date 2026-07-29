from flask import Blueprint, render_template, session, redirect, url_for

from notification import (
    get_notifications,
    mark_as_read,
    mark_all_as_read,
    delete_notification
)

notifications_bp = Blueprint(
    "notifications",
    __name__
)


@notifications_bp.route("/notifications")
def notifications():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    notifications = get_notifications(
        session["role"],
        session["user_id"]
    )

    return render_template(
        "notifications/notifications.html",
        notifications=notifications
    )


@notifications_bp.route("/notifications/read/<int:notification_id>")
def read_notification(notification_id):

    mark_as_read(notification_id)

    return redirect(url_for("notifications.notifications"))


@notifications_bp.route("/notifications/read_all")
def read_all_notifications():

    mark_all_as_read(
        session["role"],
        session["user_id"]
    )

    return redirect(url_for("notifications.notifications"))


@notifications_bp.route("/notifications/delete/<int:notification_id>")
def remove_notification(notification_id):

    delete_notification(notification_id)

    return redirect(url_for("notifications.notifications"))