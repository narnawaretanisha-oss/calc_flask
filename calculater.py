from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps

app = Flask(__name__)

app.secret_key = "anshu_calculator_secret_key"

DATABASE = "calculator.db"


# =========================
# DATABASE CONNECTION
# =========================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# =========================
# CREATE TABLES
# =========================

def init_db():

    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            expression TEXT NOT NULL,
            result TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


# =========================
# LOGIN REQUIRED
# =========================

def login_required(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("login"))

        return func(*args, **kwargs)

    return wrapper


# =========================
# HOME
# =========================

@app.route("/")
def home():

    if "user_id" in session:
        return redirect(url_for("calculator"))

    return redirect(url_for("login"))


# =========================
# SIGNUP
# =========================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if username == "" or password == "":
            flash("Please fill all fields.")
            return redirect(url_for("signup"))

        if password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for("signup"))

        if len(password) < 4:
            flash("Password must contain at least 4 characters.")
            return redirect(url_for("signup"))

        conn = get_db()

        existing_user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        if existing_user:

            conn.close()

            flash("Username already exists.")
            return redirect(url_for("signup"))

        hashed_password = generate_password_hash(password)

        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hashed_password)
        )

        conn.commit()
        conn.close()

        flash("Account created successfully. Please login.")

        return redirect(url_for("login"))

    return render_template("signup.html")


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["username"] = user["username"]

            return redirect(url_for("calculator"))

        flash("Invalid username or password.")

    return render_template("login.html")


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))


# =========================
# CALCULATOR
# =========================

@app.route("/calculator")
@login_required
def calculator():

    return render_template(
        "calculater1.html",
        username=session["username"]
    )


# =========================
# SAVE CALCULATION
# =========================

@app.route("/save-calculation", methods=["POST"])
@login_required
def save_calculation():

    data = request.get_json()

    expression = data.get("expression")
    result = data.get("result")

    if not expression or result is None:

        return jsonify({
            "success": False
        })

    current_time = datetime.now().strftime(
        "%d-%m-%Y %I:%M:%S %p"
    )

    conn = get_db()

    conn.execute("""
        INSERT INTO calculations
        (user_id, expression, result, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        session["user_id"],
        expression,
        str(result),
        current_time
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "success": True
    })


# =========================
# HISTORY
# =========================

@app.route("/history")
@login_required
def history():

    conn = get_db()

    calculations = conn.execute("""
        SELECT *
        FROM calculations
        WHERE user_id = ?
        ORDER BY id DESC
    """, (
        session["user_id"],
    )).fetchall()

    conn.close()

    return render_template(
        "history.html",
        calculations=calculations,
        username=session["username"]
    )


# =========================
# CLEAR HISTORY
# =========================

@app.route("/clear-history", methods=["POST"])
@login_required
def clear_history():

    conn = get_db()

    conn.execute(
        "DELETE FROM calculations WHERE user_id = ?",
        (session["user_id"],)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("history"))


# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
@login_required
def dashboard():

    conn = get_db()

    total = conn.execute("""
        SELECT COUNT(*) AS count
        FROM calculations
        WHERE user_id = ?
    """, (
        session["user_id"],
    )).fetchone()["count"]

    addition = conn.execute("""
        SELECT COUNT(*) AS count
        FROM calculations
        WHERE user_id = ?
        AND expression LIKE '%+%'
    """, (
        session["user_id"],
    )).fetchone()["count"]

    subtraction = conn.execute("""
        SELECT COUNT(*) AS count
        FROM calculations
        WHERE user_id = ?
        AND expression LIKE '%-%'
    """, (
        session["user_id"],
    )).fetchone()["count"]

    multiplication = conn.execute("""
        SELECT COUNT(*) AS count
        FROM calculations
        WHERE user_id = ?
        AND expression LIKE '%*%'
    """, (
        session["user_id"],
    )).fetchone()["count"]

    division = conn.execute("""
        SELECT COUNT(*) AS count
        FROM calculations
        WHERE user_id = ?
        AND expression LIKE '%/%'
    """, (
        session["user_id"],
    )).fetchone()["count"]

    recent = conn.execute("""
        SELECT *
        FROM calculations
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 5
    """, (
        session["user_id"],
    )).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        username=session["username"],
        total=total,
        addition=addition,
        subtraction=subtraction,
        multiplication=multiplication,
        division=division,
        recent=recent
    )


# =========================
# RUN
# =========================

if __name__ == "__main__":

    init_db()

    app.run(debug=True)