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
    <!DOCTYPE html>
    <html>
    <head>
        <title>Add Alumni</title>

        <style>

            body{
                font-family: Arial, sans-serif;
                background: #f4f6f9;
                display:flex;
                justify-content:center;
                align-items:center;
                min-height:100vh;
            }

            .container{
                background:white;
                width:500px;
                padding:30px;
                border-radius:15px;
                box-shadow:0 5px 15px rgba(0,0,0,0.2);
            }

            h1{
                text-align:center;
                color:#2c3e50;
                margin-bottom:20px;
            }

            label{
                font-weight:bold;
                color:#333;
            }

            input{
                width:100%;
                padding:10px;
                margin-top:5px;
                margin-bottom:15px;
                border:1px solid #ccc;
                border-radius:8px;
                box-sizing:border-box;
            }

            .btn{
                width:100%;
                background:#007bff;
                color:white;
                border:none;
                padding:12px;
                border-radius:8px;
                font-size:16px;
                cursor:pointer;
            }

            .btn:hover{
                background:#0056b3;
            }

            .back{
                display:block;
                text-align:center;
                margin-top:15px;
                text-decoration:none;
                color:#007bff;
            }

        </style>

    </head>

    <body>

    <div class="container">

    <h1>🎓 Add Alumni</h1>

    <form method="POST">

    <label>Full Name</label>
    <input type="text" name="name" required>

    <label>Email</label>
    <input type="email" name="email" required>

    <label>Graduation Year</label>
    <input type="number" name="year" required>

    <label>Department</label>
    <input type="text" name="department" required>

    <label>Company</label>
    <input type="text" name="company">

    <label>Designation</label>
    <input type="text" name="designation">

    <label>Skills</label>
    <input type="text" name="skills">

    <button class="btn" type="submit">
    Add Alumni
    </button>

    </form>

    <a class="back" href="/">
    ← Back to Dashboard
    </a>

    </div>

    </body>
    </html>
    """


if __name__ == "__main__":
    app.run(debug=True)
