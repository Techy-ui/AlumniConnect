from db import get_connection


def create_notification(user_role, user_id, title, message):
    """
    Create a new notification for a user.

    Parameters:
        user_role (str): "student" or "alumni"
        user_id (int): ID of the user
        title (str): Notification title
        message (str): Notification message
    """

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO notifications
            (
                user_role,
                user_id,
                title,
                message
            )
            VALUES
            (%s, %s, %s, %s)
        """, (
            user_role,
            user_id,
            title,
            message
        ))

        conn.commit()

    except Exception as e:
        conn.rollback()
        print("Notification Error:", e)

    finally:
        cur.close()
        conn.close()


def get_notifications(user_role, user_id):
    """
    Fetch all notifications for a user.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT *
        FROM notifications
        WHERE user_role = %s
        AND user_id = %s
        ORDER BY created_at DESC
    """, (
        user_role,
        user_id
    ))

    notifications = cur.fetchall()

    cur.close()
    conn.close()

    return notifications


def get_unread_count(user_role, user_id):
    """
    Return number of unread notifications.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*) AS total
        FROM notifications
        WHERE user_role = %s
        AND user_id = %s
        AND is_read = FALSE
    """, (
        user_role,
        user_id
    ))

    count = cur.fetchone()["total"]

    cur.close()
    conn.close()

    return count


def mark_as_read(notification_id):
    """
    Mark one notification as read.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE notifications
        SET is_read = TRUE
        WHERE notification_id = %s
    """, (notification_id,))

    conn.commit()

    cur.close()
    conn.close()


def mark_all_as_read(user_role, user_id):
    """
    Mark all notifications for a user as read.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE notifications
        SET is_read = TRUE
        WHERE user_role = %s
        AND user_id = %s
    """, (
        user_role,
        user_id
    ))

    conn.commit()

    cur.close()
    conn.close()


def delete_notification(notification_id):
    """
    Delete a notification.
    """

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        DELETE FROM notifications
        WHERE notification_id = %s
    """, (notification_id,))

    conn.commit()

    cur.close()
    conn.close()