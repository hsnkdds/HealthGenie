from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime
import webbrowser
import threading
from report_generator import generate_report
from symptom_rules import check_symptoms
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "neon_healthgenie_secret"
DATABASE = "database.db"

# ================= DATABASE =================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    is_admin INTEGER DEFAULT 0
)
""")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        sender TEXT,
        message TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ================= AI RESPONSE ENGINE =================

def ai_response(message):
    message = message.lower()

    symptom_rules = {
        "burn": ("Burn detected. Cool with running water 10-20 minutes.", 1),
        "fever": ("Possible infection or flu. Stay hydrated.", 1),
        "cough": ("Cold or respiratory irritation.", 1),
        "headache": ("Stress, dehydration, or migraine.", 1),
        "chest pain": ("Chest pain is serious. Seek medical attention.", 3),
        "tight chest": ("Possible asthma or anxiety.", 2),
        "shortness of breath": ("Serious respiratory symptom. Seek care.", 3),
        "unconscious": ("Medical emergency. Immediate help required.", 5),
        "seizure": ("Emergency condition. Seek help now.", 5),
        "bleeding": ("Apply pressure. Seek care if severe.", 3),
        "stomach pain": ("Digestive issue possible.", 1),
        "dizziness": ("Possible dehydration or low BP.", 2),
        "fatigue": ("Rest and hydration recommended.", 1),
    }

    responses = []
    risk_score = 0

    for symptom in symptom_rules:
        if symptom in message:
            response, risk = symptom_rules[symptom]
            responses.append(response)
            risk_score += risk

    if not responses:
        return {
            "reply": "I'm not sure about that symptom. Please describe more clearly.",
            "risk": 0
        }
    
    

    if risk_score >= 6:
        risk_level = "HIGH RISK"
    elif risk_score >= 3:
        risk_level = "MODERATE RISK"
    else:
        risk_level = "LOW RISK"

    final_reply = " ".join(responses) + f"\n\nRisk Level: {risk_level}"

    return {
        "reply": final_reply,
        "risk": risk_score
    }

# ================= ROUTES =================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        age = request.form.get("age")
        gender = request.form.get("gender")

        conn = get_db()
        cursor = conn.cursor()

        is_admin = 0
        if username == "hsnkdds819" and password == "hsnkdds":
            is_admin = 1

        try:
            hashed = generate_password_hash(password)

            cursor.execute(
                "INSERT INTO users (username, password, age, gender, is_admin) VALUES (?, ?, ?, ?, ?)",
                (username, hashed, age, gender, is_admin),
            )

            conn.commit()

        except sqlite3.IntegrityError:
            conn.close()
            return "Username already exists. Try another one."

        conn.close()
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )

        user = cursor.fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["is_admin"] = user["is_admin"]

            return redirect(url_for("dashboard"))

        else:
            return "Invalid username or password"

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()

    # Total chats
    cursor.execute(
        "SELECT COUNT(*) FROM chat_messages WHERE user_id=?",
        (session["user_id"],)
    )
    total_chats = cursor.fetchone()[0]

    last_active_time = "Recently Active"

    # AI health score
    if total_chats > 20:
        ai_health = 100
    elif total_chats > 10:
        ai_health = 85
    elif total_chats > 5:
        ai_health = 70
    else:
        ai_health = 50

    # Weekly analytics
    cursor.execute("""
        SELECT strftime('%w', timestamp) as day, COUNT(*)
        FROM chat_messages
        WHERE user_id = ?
        GROUP BY day
    """, (session["user_id"],))

    rows = cursor.fetchall()

    chart_data = [0,0,0,0,0,0,0]

    for row in rows:
        day = int(row[0])
        count = row[1]

        # Convert Sun-Sat → Mon-Sun
        if day == 0:
            chart_data[6] = count
        else:
            chart_data[day-1] = count

    conditions = ["Flu", "Common Cold"]

    recommendation = "Stay hydrated, get enough rest, and monitor symptoms."

    conn.close()

    return render_template(
        "dashboard.html",
        username=session["username"],
        total_chats=total_chats,
        ai_health=ai_health,
        last_active_time=last_active_time,
        chart_data=chart_data,
        conditions=conditions,
        recommendation=recommendation
    )


@app.route("/chat", methods=["GET", "POST"])
def chat():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        message = request.form.get("message")
        msg = message.lower()

        # Save user message
        cursor.execute(
            "INSERT INTO chat_messages (user_id, sender, message) VALUES (?, ?, ?)",
            (session["user_id"], "User", message),
        )

        # Greeting responses
        if msg in ["hi", "hello", "hey","hy"]:
            reply = "Hello! 👋 I'm HealthGenie. Tell me your symptoms and I'll try to help."
            risk = 0

        elif "how are you" in msg:
            reply = "I'm doing great! 😊 How can I help with your health today?"
            risk = 0

        elif "thank" in msg:
            reply = "You're welcome! Stay healthy. 💙"
            risk = 0

        elif "bye" in msg:
            reply = "Goodbye! Take care of your health. 👋"
            risk = 0

        else:
            # AI symptom analysis
            ai_data = check_symptoms(message)
            reply = ai_data["reply"]
            risk = ai_data["risk"]
        # Calculate health score
        health_score = max(0, 100 - (risk * 10))

        reply_with_score = reply + f"\nHealth Score: {health_score}/100"

        # Save AI response
        cursor.execute(
            "INSERT INTO chat_messages (user_id, sender, message) VALUES (?, ?, ?)",
            (session["user_id"], "AI", reply_with_score),
        )

        conn.commit()

    # Load chat history
    cursor.execute(
        "SELECT * FROM chat_messages WHERE user_id=? ORDER BY id ASC",
        (session["user_id"],),
    )

    messages = cursor.fetchall()

    conn.close()

    return render_template("chat.html", messages=messages)

#report
@app.route("/report", methods=["GET", "POST"])
def report():

    if "user_id" not in session:
        return redirect(url_for("login"))

    report = None

    if request.method == "POST":
        symptoms = request.form["symptoms"]
        diseases = check_symptoms(symptoms)
        report = generate_report(session["username"], symptoms, diseases)

    return render_template("report.html", report=report)
#PROFILE

@app.route("/profile")
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT username, age, gender FROM users WHERE id = ?",
        (session["user_id"],)
    )

    user = cursor.fetchone()

    conn.close()

    return render_template("profile.html", user=user)

@app.route("/admin")
def admin_panel():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if session.get("is_admin") != 1:
        return "Access Denied"

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, username FROM users")
    users = cursor.fetchall()

    user_data = []

    for user in users:
        user_id = user["id"]

        cursor.execute(
            "SELECT COUNT(*) FROM chat_messages WHERE user_id=?",
            (user_id,)
        )
        total_chats = cursor.fetchone()[0]

        user_data.append({
            "id": user_id,
            "username": user["username"],
            "total_chats": total_chats
        })

    conn.close()

    return render_template("admin.html", users=user_data)


@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):
    if "user_id" not in session or session.get("is_admin") != 1:
        return "Access Denied"

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM chat_messages WHERE user_id=?", (user_id,))
    cursor.execute("DELETE FROM users WHERE id=?", (user_id,))

    conn.commit()
    conn.close()

    return redirect(url_for("admin_panel"))


@app.route("/emergency")
def emergency():
    return render_template("emergency.html")


@app.route("/articles")
def articles():
    return render_template("articles.html")


@app.route("/bmi", methods=["GET","POST"])
def bmi():

    bmi = None
    category = None

    if request.method == "POST":

        weight = float(request.form["weight"])
        height = float(request.form["height"]) / 100

        bmi = round(weight / (height * height), 2)

        if bmi < 18.5:
            category = "Underweight"
        elif bmi < 25:
            category = "Normal"
        elif bmi < 30:
            category = "Overweight"
        else:
            category = "Obese"

    return render_template("bmi.html", bmi=bmi, category=category)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# ================= AUTO OPEN BROWSER =================

def open_browser():
    webbrowser.open("http://127.0.0.1:5000")

# ================= RUN APP =================

if __name__ == "__main__":
    threading.Timer(1.5, open_browser).start()
    app.run(debug=True)
