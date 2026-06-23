
from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
import requests
from datetime import datetime
from reportlab.pdfgen import canvas
import os

app = Flask(__name__)
app.secret_key = "cosmic_destiny_secret"


# ==========================
# DATABASE
# ==========================

def init_db():
    conn = sqlite3.connect("database.db")

    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        dob TEXT,
        zodiac TEXT,
        horoscope TEXT,
        report_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

init_db()


# ==========================
# PDF GENERATOR
# ==========================

def create_pdf(name, zodiac, horoscope):

    if not os.path.exists("reports"):
        os.makedirs("reports")

    filename = f"reports/{name}.pdf"

    pdf = canvas.Canvas(filename)

    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(180, 800, "Cosmic Destiny Report")

    pdf.setFont("Helvetica", 14)

    pdf.drawString(50, 750, f"Name: {name}")
    pdf.drawString(50, 720, f"Zodiac Sign: {zodiac}")

    pdf.drawString(50, 680, "Horoscope:")

    text = pdf.beginText(50, 650)
    text.textLines(horoscope)

    pdf.drawText(text)

    pdf.save()


# ==========================
# ZODIAC CALCULATOR
# ==========================

def zodiac_sign(month, day):

    zodiac_dates = [
        ((1, 20), "Aquarius"),
        ((2, 19), "Pisces"),
        ((3, 21), "Aries"),
        ((4, 20), "Taurus"),
        ((5, 21), "Gemini"),
        ((6, 21), "Cancer"),
        ((7, 23), "Leo"),
        ((8, 23), "Virgo"),
        ((9, 23), "Libra"),
        ((10, 23), "Scorpio"),
        ((11, 22), "Sagittarius"),
        ((12, 22), "Capricorn")
    ]

    for (m, d), sign in zodiac_dates:
        if (month, day) < (m, d):
            break
        zodiac = sign

    return zodiac if month != 1 or day >= 20 else "Capricorn"


# ==========================
# ZODIAC INFORMATION
# ==========================

zodiac_info = {

    "Aries": {
        "element": "Fire",
        "planet": "Mars",
        "strength": "Confident, Energetic",
        "weakness": "Impulsive"
    },

    "Taurus": {
        "element": "Earth",
        "planet": "Venus",
        "strength": "Reliable, Patient",
        "weakness": "Stubborn"
    },

    "Gemini": {
        "element": "Air",
        "planet": "Mercury",
        "strength": "Smart, Adaptable",
        "weakness": "Indecisive"
    },

    "Cancer": {
        "element": "Water",
        "planet": "Moon",
        "strength": "Loyal, Caring",
        "weakness": "Emotional"
    },

    "Leo": {
        "element": "Fire",
        "planet": "Sun",
        "strength": "Creative, Leader",
        "weakness": "Egoistic"
    },

    "Virgo": {
        "element": "Earth",
        "planet": "Mercury",
        "strength": "Practical",
        "weakness": "Overthinking"
    },

    "Libra": {
        "element": "Air",
        "planet": "Venus",
        "strength": "Balanced",
        "weakness": "Avoids Decisions"
    },

    "Scorpio": {
        "element": "Water",
        "planet": "Pluto",
        "strength": "Passionate",
        "weakness": "Jealous"
    },

    "Sagittarius": {
        "element": "Fire",
        "planet": "Jupiter",
        "strength": "Adventurous",
        "weakness": "Restless"
    },

    "Capricorn": {
        "element": "Earth",
        "planet": "Saturn",
        "strength": "Disciplined",
        "weakness": "Serious"
    },

    "Aquarius": {
        "element": "Air",
        "planet": "Uranus",
        "strength": "Innovative",
        "weakness": "Detached"
    },

    "Pisces": {
        "element": "Water",
        "planet": "Neptune",
        "strength": "Compassionate",
        "weakness": "Dreamy"
    }
}


# ==========================
# HOME PAGE
# ==========================

@app.route("/")
def home():
    return render_template("index.html")


# ==========================
# USER DETAILS PAGE
# ==========================

@app.route("/details", methods=["GET", "POST"])
def details():

    if request.method == "POST":

        name = request.form["name"]
        dob = request.form["dob"]

        session["name"] = name
        session["dob"] = dob

        date_obj = datetime.strptime(dob, "%Y-%m-%d")

        sign = zodiac_sign(
            date_obj.month,
            date_obj.day
        )

        session["sign"] = sign

        conn = sqlite3.connect("database.db")
        cur = conn.cursor()

        cur.execute(
            """
            INSERT INTO users
            (name,dob,zodiac)
            VALUES(?,?,?)
            """,
            (name, dob, sign)
        )

        conn.commit()
        conn.close()

        return redirect("/zodiac")

    return render_template("details.html")


# ==========================
# ZODIAC PAGE
# ==========================

@app.route("/zodiac")
def zodiac():

    sign = session["sign"]

    return render_template(
        "zodiac.html",
        sign=sign,
        data=zodiac_info[sign]
    )


# ==========================
# FORECAST PAGE
# ==========================

@app.route("/forecast")
def forecast():

    sign = session["sign"]
    name = session["name"]

    try:

        url = f"https://ohmanda.com/api/horoscope/{sign.lower()}"

        response = requests.get(url)

        horoscope = response.json()["horoscope"]

    except:

        horoscope = "Today's forecast is unavailable."

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE users
        SET horoscope=?
        WHERE name=?
        """,
        (horoscope, name)
    )

    conn.commit()
    conn.close()

    create_pdf(name, sign, horoscope)

    return render_template(
        "forecast.html",
        horoscope=horoscope
    )


# ==========================
# FUTURE INSIGHTS PAGE
# ==========================

@app.route("/future")
def future():
    return render_template("future.html")


# ==========================
# DASHBOARD PAGE
# ==========================

@app.route("/dashboard")
def dashboard():

    lucky = {
        "number": 7,
        "color": "Royal Blue",
        "day": "Thursday",
        "gemstone": "Sapphire"
    }

    return render_template(
        "dashboard.html",
        lucky=lucky
    )


# ==========================
# DOWNLOAD PDF
# ==========================

@app.route("/download")
def download():

    name = session["name"]

    return send_file(
        f"reports/{name}.pdf",
        as_attachment=True
    )


# ==========================
# HISTORY PAGE
# ==========================

@app.route("/history")
def history():

    conn = sqlite3.connect("database.db")

    cur = conn.cursor()

    cur.execute("""
    SELECT
    name,
    dob,
    zodiac,
    report_date
    FROM users
    ORDER BY id DESC
    """)

    data = cur.fetchall()

    conn.close()

    return render_template(
        "history.html",
        data=data
    )


# ==========================
# RUN APP
# ==========================

if __name__ == "__main__":
    app.run(debug=True)
