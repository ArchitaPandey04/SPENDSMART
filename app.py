#  app.py - main Flask app for SpendSmart backend. it sets up flask server and render the homepage

from flask import Flask, render_template, request,redirect,url_for,flash
import sqlite3
from app_db import get_db
from werkzeug.security import generate_password_hash,check_password_hash
from flask import session
import json
from flask import jsonify
from typing import List
from flask import jsonify
from ml.model_utils import prepare_df_for_user, aggregate_monthly_expenses
from ml.predictor import predict_next_month





app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# Home page route
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        print(f"POST received: name={name}, email={email}")  # debug

        if not name or not email or not password:
            print("Validation failed: missing fields")
            flash("All fields are required.")
            return redirect(url_for("signup"))

        hashed_password = generate_password_hash(password)
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, hashed_password)
            )
            conn.commit()
            conn.close()
            print("User inserted successfully")  # debug
            
            flash("Signup successful! Please login.")
            print("Redirecting to login")  # debug
            return redirect(url_for("login"))
        
        except sqlite3.IntegrityError:
            print("IntegrityError: Email exists")  # debug
            flash("Email already exists. Try another.")
            return redirect(url_for("signup"))

    print("GET request: rendering signup.html")  # debug
    return render_template("signup.html")


    
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        print(f"POST login: email={email}, password={password}")  # debug

        if not email or not password:
            print("Validation failed: missing fields")
            flash("Email and password are required.")
            return redirect(url_for("login"))

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        print(f"User fetched: {user}")  # debug

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            flash(f"Welcome back, {user['name']}!")
            print("Redirecting to dashboard")  # debug
            return redirect(url_for("dashboard"))
        else:
            print("Invalid login credentials")
            flash("Invalid email or password.")
            return redirect(url_for("login"))

    print("GET login page")  # debug
    return render_template("login.html")

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    if "user_id" not in session:
        flash("Please log in first.")
        return redirect(url_for("login"))
    
    conn = get_db()
    cursor = conn.cursor()
    
    predicted_amount = None
    monthly_df = None

    # -----------------------------
    # Add expense only on POST
    # -----------------------------
    if request.method == "POST":

        date = request.form.get("date")
        description = request.form.get("description")
        amount = request.form.get("amount")
        category = request.form.get("category")

        if not date or not amount:
            flash("Date and amount are required")

        else:
            cursor.execute(
                (
                    "INSERT INTO expenses (user_id, date, description, amount, category) "
                    "VALUES (?,?,?,?,?)"
                ),
                (session["user_id"], date, description, amount, category)
            )
            conn.commit()
            flash("Expense added successfully.")

            # --------------------------------------
            # Run ML ONLY when expense successfully added
            # --------------------------------------
            from ml.model_utils import prepare_df_for_user, aggregate_monthly_expenses
            from ml.predictor import predict_next_month

            df = prepare_df_for_user(conn, session["user_id"])
            monthly_df = aggregate_monthly_expenses(df)

            if not monthly_df.empty:
                predicted_amount = predict_next_month(monthly_df)

    # -----------------------------
    # Fetch all expenses ALWAYS
    # -----------------------------
    cursor.execute(
        "SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC",
        (session["user_id"],)
    )
    expenses = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        name=session["user_name"],
        expenses=expenses,
        predicted_amount=predicted_amount,
        monthly_df=monthly_df.to_dict(orient="records") if monthly_df is not None else None
    )





@app.route("/logout")
def logout():
    # remove all session data
    session.clear()
    flash("you have been logged out successfully.")
    return redirect(url_for("login"))


@app.route('/update_expense/<int:expense_id>', methods=['POST'])
def update_expense(expense_id):
    if "user_id" not in session:
        return {"error": "Not logged in"}, 403

    data = request.get_json()
    if not data:
        return {"error": "No data received"}, 400

    date = data.get("date")
    description = data.get("desc")
    amount = data.get("amt")
    category = data.get("cat")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE expenses SET date=?, description=?, amount=?, category=? WHERE id=? AND user_id=?",
        (date, description, amount, category, expense_id, session["user_id"])
    )
    conn.commit()
    conn.close()

    return {"success": True}

    
@app.route("/add_expense", methods=["POST"])
def add_expense():
        date = request.form["date"]
        description = request.form["description"]
        amount = request.form["amount"]
        category = request.form["category"]

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO expenses (user_id, date, description, amount, category)
            VALUES (1, ?, ?, ?, ?)
        """, (date, description, amount, category))
        conn.commit()
        conn.close()

        return redirect(url_for("dashboard"))

@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    if "user_id" not in session:
        return jsonify({"success": False, "error": "not_logged_in"}), 401
    
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM expenses WHERE id = ? AND user_id = ?",
        (expense_id, session["user_id"])
    )
    
    conn.commit()
    conn.close()

    return jsonify({"success": True})
        

@app.route('/expense_summary')
def expense_summary():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401

    conn = get_db()
    cursor = conn.cursor()

    # --- Category-wise totals ---
    cursor.execute("""
        SELECT category, SUM(amount) as total
        FROM expenses
        WHERE user_id = ?
        GROUP BY category
    """, (session["user_id"],))
    category_data = cursor.fetchall()

    # --- Monthly totals ---
    cursor.execute("""
        SELECT strftime('%Y-%m', date) as month, SUM(amount) as total
        FROM expenses
        WHERE user_id = ?
        GROUP BY month
        ORDER BY month
    """, (session["user_id"],))
    monthly_data = cursor.fetchall()

    conn.close()

    # --- Convert rows to JSON-friendly dicts ---
    data = {
        "category_totals": [
            {"category": row["category"], "total": row["total"]} for row in category_data
        ],
        "monthly_totals": [
            {"month": row["month"], "total": row["total"]} for row in monthly_data
        ]
    }

    return jsonify(data)






    

        


# Run the app
if __name__ == "__main__":
    
    app.run(debug=True)