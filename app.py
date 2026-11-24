
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

DATABASE = os.path.join("database", "leads.db")

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs("database", exist_ok=True)

    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            designation TEXT NOT NULL,
            industry TEXT NOT NULL,
            status TEXT DEFAULT 'New'
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def home():
    conn = get_db_connection()
    leads = conn.execute(
        "SELECT * FROM leads ORDER BY id DESC"
    ).fetchall()

    total = len(leads)
    connected = sum(1 for lead in leads if lead["status"] == "Connected")

    conn.close()

    return render_template(
        "index.html",
        leads=leads,
        total=total,
        connected=connected
    )

@app.route("/add-lead", methods=["POST"])
def add_lead():
    name = request.form.get("name", "").strip()
    designation = request.form.get("designation", "").strip()
    industry = request.form.get("industry", "").strip()

    if name and designation and industry:
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO leads (name, designation, industry) VALUES (?, ?, ?)",
            (name, designation, industry)
        )
        conn.commit()
        conn.close()

    return redirect(url_for("home"))


@app.route("/edit-lead/<int:lead_id>", methods=["GET", "POST"])
def edit_lead(lead_id):
    conn = get_db_connection()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        designation = request.form.get("designation", "").strip()
        industry = request.form.get("industry", "").strip()

        if name and designation and industry:
            conn.execute(
                "UPDATE leads SET name=?, designation=?, industry=? WHERE id=?",
                (name, designation, industry, lead_id)
            )
            conn.commit()

        conn.close()
        return redirect(url_for("home"))

    lead = conn.execute(
        "SELECT * FROM leads WHERE id=?", (lead_id,)
    ).fetchone()

    conn.close()

    if lead is None:
        return "Lead not found", 404

    return render_template("edit.html", lead=lead)


@app.route("/delete-lead/<int:lead_id>", methods=["POST"])
def delete_lead(lead_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM leads WHERE id=?", (lead_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("home"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
