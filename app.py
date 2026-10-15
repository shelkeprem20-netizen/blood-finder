from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# Secret key for admin login session
app.secret_key = "blood-finder-secret-key-2026"


# =====================================================
# DATABASE
# =====================================================

def get_database():

    connection = sqlite3.connect("blood_finder.db")

    connection.row_factory = sqlite3.Row

    return connection


# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():

    return render_template("index.html")


# =====================================================
# FIND BLOOD
# =====================================================

@app.route("/find-blood", methods=["GET", "POST"])
def find_blood():

    donors = []

    if request.method == "POST":

        blood_group = request.form["blood_group"]
        location = request.form["location"]

        connection = get_database()

        donors_data = connection.execute(
            """
            SELECT *
            FROM donors
            WHERE blood_group = ?
            AND location LIKE ?
            AND availability = 'Available'
            AND verification_status = 'Verified'
            """,
            (
                blood_group,
                "%" + location + "%"
            )
        ).fetchall()

        connection.close()

        # Calculate next eligible donation date
        for donor in donors_data:

            donor_data = dict(donor)

            try:

                last_donation = datetime.strptime(
                    donor_data["last_donation"],
                    "%Y-%m-%d"
                )

                next_donation = last_donation + timedelta(days=90)

                donor_data["next_donation"] = next_donation.strftime(
                    "%Y-%m-%d"
                )

            except (ValueError, TypeError):

                donor_data["next_donation"] = "Not available"

            donors.append(donor_data)

    return render_template(
        "find_blood.html",
        donors=donors
    )


# =====================================================
# REGISTER DONOR
# =====================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        phone = request.form["phone"]
        blood_group = request.form["blood_group"]
        location = request.form["location"]
        last_donation = request.form["last_donation"]
        availability = request.form["availability"]

        connection = get_database()

        connection.execute(
            """
            INSERT INTO donors
            (
                name,
                phone,
                blood_group,
                location,
                last_donation,
                availability,
                verification_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                phone,
                blood_group,
                location,
                last_donation,
                availability,
                "Pending"
            )
        )

        connection.commit()

        connection.close()

        return redirect("/register?success=1")

    return render_template("register.html")


# =====================================================
# BLOOD INFORMATION
# =====================================================

@app.route("/blood-info")
def blood_info():

    return render_template("blood_info.html")


# =====================================================
# ABOUT PROJECT
# =====================================================

@app.route("/about")
def about():

    return render_template("about.html")


# =====================================================
# ADMIN LOGIN
# =====================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    error = None

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        # College project admin credentials
        if username == "admin" and password == "bloodfinder123":

            session["admin_logged_in"] = True

            return redirect("/admin")

        else:

            error = "Invalid username or password"

    return render_template(
        "admin_login.html",
        error=error
    )


# =====================================================
# ADMIN PANEL
# =====================================================

@app.route("/admin")
def admin():

    # Check login
    if not session.get("admin_logged_in"):

        return redirect("/admin/login")

    connection = get_database()

    donors = connection.execute(
        """
        SELECT *
        FROM donors
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return render_template(
        "admin.html",
        donors=donors
    )


# =====================================================
# UPDATE DONOR VERIFICATION
# =====================================================

@app.route("/admin/verify/<int:donor_id>/<status>")
def verify_donor(donor_id, status):

    # Check login
    if not session.get("admin_logged_in"):

        return redirect("/admin/login")

    allowed_statuses = [
        "Pending",
        "Verified",
        "Rejected"
    ]

    if status not in allowed_statuses:

        return "Invalid verification status", 400

    connection = get_database()

    connection.execute(
        """
        UPDATE donors
        SET verification_status = ?
        WHERE id = ?
        """,
        (
            status,
            donor_id
        )
    )

    connection.commit()

    connection.close()

    return redirect("/admin")


# =====================================================
# ADMIN LOGOUT
# =====================================================

@app.route("/admin/logout")
def admin_logout():

    session.pop("admin_logged_in", None)

    return redirect("/admin/login")


# =====================================================
# START SERVER
# =====================================================

if __name__ == "__main__":

    app.run(debug=True)