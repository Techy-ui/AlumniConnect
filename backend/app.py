from flask import Flask, request, redirect
from db import get_connection

app = Flask(__name__)

@app.route("/")
def home():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT full_name, company, designation
        FROM alumni
        ORDER BY alumni_id
    """)

    alumni = cur.fetchall()

    cur.close()
    conn.close()

    html = """
    <html>
    <head>
        <title>AlumniConnect</title>
        <style>
            body{
                font-family: Arial;
                margin:40px;
                background:#f4f4f4;
            }
            .card{
                background:white;
                padding:15px;
                margin:10px;
                border-radius:10px;
            }
            a{
                text-decoration:none;
                background:#007bff;
                color:white;
                padding:10px;
                border-radius:5px;
            }
        </style>
    </head>
    <body>

    <h1>🎓 AlumniConnect</h1>

    <a href="/add_alumni">Add Alumni</a>

    <hr>
    """

    for name, company, designation in alumni:
        html += f"""
        <div class='card'>
            <h3>{name}</h3>
            <p>Company: {company}</p>
            <p>Role: {designation}</p>
        </div>
        """

    html += "</body></html>"

    return html


@app.route("/add_alumni", methods=["GET", "POST"])
def add_alumni():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        year = request.form["year"]
        department = request.form["department"]
        company = request.form["company"]
        designation = request.form["designation"]
        skills = request.form["skills"]

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO alumni
            (full_name,email,graduation_year,department,company,designation,skills)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """,
        (name,email,year,department,company,designation,skills))

        conn.commit()

        cur.close()
        conn.close()

        return redirect("/")

    return """
    <h1>Add Alumni</h1>

    <form method="POST">

        Name:<br>
        <input type="text" name="name"><br><br>

        Email:<br>
        <input type="email" name="email"><br><br>

        Graduation Year:<br>
        <input type="number" name="year"><br><br>

        Department:<br>
        <input type="text" name="department"><br><br>

        Company:<br>
        <input type="text" name="company"><br><br>

        Designation:<br>
        <input type="text" name="designation"><br><br>

        Skills:<br>
        <input type="text" name="skills"><br><br>

        <input type="submit" value="Add Alumni">

    </form>
    """


if __name__ == "__main__":
    app.run(debug=True)
