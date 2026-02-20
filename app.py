
from flask import Flask, render_template, request, redirect, url_for, session, send_file
import sqlite3
import uuid
from datetime import datetime
import csv
from io import StringIO

app = Flask(__name__)
app.secret_key = "super-secure-admin-key"

DATABASE = "database.db"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "miracle123"

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS registrations (
        id TEXT PRIMARY KEY,
        full_name TEXT,
        dob TEXT,
        age TEXT,
        gender TEXT,
        school TEXT,
        grade TEXT,
        address TEXT,
        parent_name TEXT,
        relationship TEXT,
        phone TEXT,
        alt_phone TEXT,
        email TEXT,
        occupation TEXT,
        medical TEXT,
        allergies TEXT,
        emergency_name TEXT,
        emergency_phone TEXT,
        created_at TEXT
    )''')
    conn.commit()
    conn.close()
init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        reg_id = str(uuid.uuid4())[:8]
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("INSERT INTO registrations VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            reg_id,
            request.form["full_name"],
            request.form["dob"],
            request.form["age"],
            request.form["gender"],
            request.form["school"],
            request.form["grade"],
            request.form["address"],
            request.form["parent_name"],
            request.form["relationship"],
            request.form["phone"],
            request.form["alt_phone"],
            request.form["email"],
            request.form["occupation"],
            request.form["medical"],
            request.form["allergies"],
            request.form["emergency_name"],
            request.form["emergency_phone"],
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        conn.close()
        return redirect(url_for("receipt", reg_id=reg_id))
    return render_template("register.html")

@app.route("/receipt/<reg_id>")
def receipt(reg_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM registrations WHERE id=?", (reg_id,))
    data = c.fetchone()
    conn.close()
    return render_template("receipt.html", data=data)

# ================= ADMIN =================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form["username"] == ADMIN_USERNAME and request.form["password"] == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM registrations ORDER BY created_at DESC")
    data = c.fetchall()
    conn.close()
    return render_template("admin_dashboard.html", data=data, total=len(data))

@app.route("/admin/export")
def export_csv():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM registrations")
    rows = c.fetchall()
    conn.close()
    si = StringIO()
    cw = csv.writer(si)
    cw.writerows(rows)
    output = si.getvalue()
    return send_file(
        StringIO(output),
        mimetype="text/csv",
        as_attachment=True,
        download_name="registrations.csv"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

