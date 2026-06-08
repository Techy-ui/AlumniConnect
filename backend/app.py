from flask import Flask
from db import get_connection

app = Flask(__name__)

@app.route("/")
def home():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT full_name, company, designation FROM alumni")
    alumni = cur.fetchall()

    cur.close()
    conn.close()

    html = """
    <html>
    <head>
        <title>AlumniConnect</title>
        <style>
            body{
                font-family: Arial, sans-serif;
                margin:40px;
                background:#f4f4f4;
            }
            h1{
                color:#2c3e50;
            }
            .card{
                background:white;
                padding:15px;
                margin:10px;
                border-radius:10px;
                box-shadow:0px 2px 5px rgba(0,0,0,0.2);
            }
        </style>
    </head>
    <body>
        <h1>🎓 AlumniConnect</h1>
        <h3>Registered Alumni</h3>
    """

    for name, company, designation in alumni:
        html += f"""
        <div class='card'>
            <h3>{name}</h3>
            <p><b>Company:</b> {company}</p>
            <p><b>Role:</b> {designation}</p>
        </div>
        """

    html += "</body></html>"
    return html

if __name__ == "__main__":
    app.run(debug=True)
