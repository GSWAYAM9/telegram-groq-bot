import sqlite3
from flask import Flask, render_template, request, redirect, session, url_for
from functools import wraps
from config import DB_PATH, DASHBOARD_USER, DASHBOARD_PASS, FLASK_SECRET, PORT
from bot.logger import LOG

app = Flask(__name__, static_folder="static", template_folder="templates")
app.secret_key = FLASK_SECRET


# ---------------- LOGIN PROTECTION -----------------
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


def query(q, params=(), commit=False):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(q, params)
    if commit:
        con.commit()
        con.close()
        return
    data = cur.fetchall()
    con.close()
    return data


# ---------------- AUTH -----------------
@app.route("/dash/login", methods=["GET", "POST"])
def login():
    msg = ""
    if request.method == "POST":
        if request.form["username"] == DASHBOARD_USER and request.form["password"] == DASHBOARD_PASS:
            session["admin"] = True
            return redirect("/dash")
        msg = "Invalid credentials"
    return render_template("login.html", message=msg)


@app.route("/dash/logout")
def logout():
    session.clear()
    return redirect("/dash/login")


# ---------------- HOME -----------------
@app.route("/dash")
@login_required
def dashboard_home():
    events = query("SELECT ts, user_id, username, action, detail FROM events ORDER BY id DESC LIMIT 50")

    stats = query("""
    SELECT 
        (SELECT COUNT(*) FROM events),
        (SELECT COUNT(*) FROM convs),
        (SELECT COUNT(*) FROM users)
    """)[0]

    return render_template("index.html",
                           total_events=stats[0],
                           total_messages=stats[1],
                           total_users=stats[2],
                           events=events)


# ---------------- USERS -----------------
@app.route("/dash/users")
@login_required
def users():
    rows = query("""
        SELECT user_id, username, first_name, last_name, persona, ts 
        FROM users ORDER BY ts DESC
    """)
    return render_template("users.html", users=rows)


# ---------------- CONVERSATIONS -----------------
@app.route("/dash/conversations/<uid>")
@login_required
def conversations(uid):
    conv = query("""
        SELECT role, content, ts
        FROM convs WHERE user_id=?
        ORDER BY id DESC LIMIT 60
    """, (uid,))
    return render_template("conversations.html", uid=uid, conversations=conv)


# ---------------- PERSONA -----------------
@app.route("/dash/persona/<uid>", methods=["GET", "POST"])
@login_required
def persona(uid):
    if request.method == "POST":
        p = request.form.get("persona")
        query("UPDATE users SET persona=? WHERE user_id=?", (p, uid), commit=True)
        return redirect("/dash/users")

    persona = query("SELECT persona FROM users WHERE user_id=?", (uid,))[0][0]
    return render_template("personas.html", uid=uid, persona=persona)


# ---------------- BROADCAST -----------------
@app.route("/dash/broadcast", methods=["POST"])
@login_required
def broadcast():
    from telegram import Bot
    from config import TELEGRAM_BOT_TOKEN

    msg = request.form.get("message")
    users = query("SELECT user_id FROM users LIMIT 50")

    bot = Bot(TELEGRAM_BOT_TOKEN)
    sent = 0

    for u in users:
        try:
            bot.send_message(chat_id=int(u[0]), text="📢 Broadcast:\n" + msg)
            sent += 1
        except:
            pass

    return f"Message sent to {sent} users!"


# ---------------- RUN -----------------
def start_dashboard():
    LOG.info("Dashboard running on port %s", PORT)
    app.run(host="0.0.0.0", port=PORT, use_reloader=False)

