#  app.py - main Flask app for SpendSmart backend. it sets up flask server and render the homepage

from flask import Flask, render_template, request,redirect,url_for,flash
import sqlite3
from app_db import get_db
from werkzeug.security import generate_password_hash,check_password_hash
from flask import session
import json
from flask import jsonify
from typing import List



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
        # checking if user is logged in
    if "user_id" not in session:
        flash("Please log in first.")
        return redirect(url_for("login"))
    
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == "POST":
        # Get form data for new expense
        date = request.form.get("date")
        description = request.form.get("description")
        amount = request.form.get("amount")
        category = request.form.get("category")
        
        # Validation: check required fields
        if not date or not amount:
            flash("Date and amount are required")
        else:
            cursor.execute(
                "INSERT INTO expenses (user_id, date, description, amount, category) VALUES (?,?,?,?,?)",
                (session["user_id"], date,description,amount,category)
            )
            conn.commit()
            flash("Expense added successfully.")
            
            # Fetch all expenses for the logged- in user
    cursor.execute(
        "SELECT * FROM expenses WHERE user_id = ? ORDER BY date DESC",
        (session["user_id"],)
    )
    expenses = cursor.fetchall()
    conn.close()
    
    return render_template("dashboard.html", name=session["user_name"], expenses=expenses)


@app.route("/logout")
def logout():
    # remove all session data
    session.clear()
    flash("you have been logged out successfully.")
    return redirect(url_for("login"))


@app.route('/update_expense/<int:expense_id>', methods=['GET', 'POST'])
def update_expense(expense_id):
    conn = get_db()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        description = request.form['description']
        amount = request.form['amount']
        category = request.form['category']
        date = request.form['date']
        
        cursor.execute(
            """
            UPDATE expenses
            SET description = ?, amount = ?, category = ?, date = ?
            WHERE id = ?
            """,
            (description, amount, category, date, expense_id)
        )
        
        conn.commit()
        conn.close()
        
        # after updating, go back to the dashboard
        return redirect(url_for('dashboard'))
    
    else:
        cursor.execute("SELECT * FROM expenses WHERE id = ?" ,(expense_id,))
        expense = cursor.fetchone()
        conn.close()
        
        print(dict(expense) if expense else "Expense not found")
        
        return "Expense data fetched successfully()"
    
@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    if "user_id" not in session:
        flash("Please log in first.")
        return redirect(url_for("login"))
    
    conn = get_db()
    cursor = conn.cursor()
    
    # deleting only if the expenses belongs to the logged-in user
    cursor.execute(
        "DELETE FROM expenses WHERE id = ? AND user_id = ?",
        (expense_id, session["user_id"])
    )
    
    conn.commit()
    conn.close()
    
    flash("Expense deletd successfully.")
    return redirect(url_for('dashboard'))
        

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