from flask import Flask, render_template, request, redirect, session
import requests
import smtplib
from email.mime.text import MIMEText
import csv
from datetime import datetime
import os
import re

app = Flask(__name__)
app.secret_key = "secret123"


# ================= FORMAT NAME =================
def format_name(name):
    return name.strip().title()


# ================= SAVE USER =================
def save_user(username, email, password):
    file_exists = os.path.isfile("users.csv")

    with open("users.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["Username", "Email", "Password"])

        writer.writerow([username, email, password])


# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if os.path.exists("users.csv"):
            with open("users.csv", "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                next(reader)

                for row in reader:
                    if row[0] == username and row[2] == password:
                        session["user"] = username
                        return redirect("/")

        return "❌ Invalid Login"

    return render_template("login.html")


# ================= SIGNUP =================
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        save_user(username, email, password)
        return redirect("/login")

    return render_template("signup.html")


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# ================= AI FUNCTION =================
def ai_lead(name, message):
    prompt = f"""
You are a professional business assistant for DS AI Solutions.

Customer Name: {name}
Customer Message: {message}

- Start with: Dear {name},
- Mention pricing starts from ₹5,000
- Keep it short and persuasive

End with:

Warm regards,
Dawood Shareef
Founder, DS AI Solutions
India
"""

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": "Bearer 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",
                "Content-Type": "application/json"
            },
            json={
                "model": "openai/gpt-3.5-turbo",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }
        )

        data = response.json()
        output = data["choices"][0]["message"]["content"]

        if not output.lower().startswith("dear"):
            output = f"Dear {name},\n\n" + output

        output = re.sub(r"^Dear\s+.*?,", f"Dear {name},\n\n", output, flags=re.IGNORECASE)
        output = re.sub(r"\.\s+", ".\n\n", output)

        return output.strip()

    except Exception as e:
        return f"AI Error: {str(e)}"


# ================= EMAIL FUNCTION =================
def send_email(to_email, content):
    from_email = "cdawoodshareef@gmail.com"
    app_password = "arxgknlecosbkwtl"

    try:
        msg = MIMEText(content, "plain", "utf-8")
        msg["Subject"] = "Response to your inquiry"
        msg["From"] = from_email
        msg["To"] = to_email

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, app_password)

        server.send_message(msg)
        server.quit()

        return "✅ Email sent successfully"

    except Exception as e:
        return f"❌ Email error: {str(e)}"


# ================= SAVE LEAD =================
def save_lead(username, name, email, message):
    file_exists = os.path.isfile("leads.csv")

    with open("leads.csv", "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["User", "Date", "Name", "Email", "Message", "Status", "FollowUp"])

        writer.writerow([
            username,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            name,
            email,
            message,
            "New",
            "0"
        ])


# ================= FOLLOW-UP EMAIL =================
def send_followup_email(name, email, step):
    messages = [
        f"""Dear {name},

Just following up on my previous message.

Would love to understand your requirement.

Warm regards,
Dawood Shareef
Founder, DS AI Solutions
India
""",
        f"""Dear {name},

Checking again. Our services start from ₹5,000.

Would you like a quick call?

Warm regards,
Dawood Shareef
Founder, DS AI Solutions
India
""",
        f"""Dear {name},

Final follow-up. Happy to assist anytime.

Warm regards,
Dawood Shareef
Founder, DS AI Solutions
India
"""
    ]

    send_email(email, messages[step - 1])


# ================= FOLLOW-UP ENGINE =================
def run_followups():
    if not os.path.exists("leads.csv"):
        return

    with open("leads.csv", "r", encoding="utf-8") as file:
        rows = list(csv.reader(file))

    if len(rows) <= 1:
        return

    header = rows[0]
    data = rows[1:]
    updated = False

    for row in data:
        try:
            lead_time = datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
        except:
            continue

        days = (datetime.now() - lead_time).days

        try:
            followup = int(row[6])
        except:
            followup = 0

        if followup == 0 and days >= 1:
            send_followup_email(row[2], row[3], 1)
            row[6] = "1"
            updated = True

        elif followup == 1 and days >= 3:
            send_followup_email(row[2], row[3], 2)
            row[6] = "2"
            updated = True

        elif followup == 2 and days >= 7:
            send_followup_email(row[2], row[3], 3)
            row[6] = "3"
            updated = True

    if updated:
        with open("leads.csv", "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(data)


# ================= UPDATE STATUS =================
@app.route("/update_status/<int:index>/<status>")
def update_status(index, status):
    if "user" not in session:
        return redirect("/login")

    with open("leads.csv", "r", encoding="utf-8") as file:
        rows = list(csv.reader(file))

    header = rows[0]
    data = rows[1:]

    if 0 <= index < len(data):
        data[index][5] = status

    with open("leads.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)

    return redirect("/leads")


# ================= VIEW LEADS =================
@app.route("/leads")
def view_leads():
    if "user" not in session:
        return redirect("/login")

    rows = []

    if os.path.exists("leads.csv"):
        with open("leads.csv", "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)

            for i, row in enumerate(reader):
                if row[0] == session["user"]:
                    rows.append((i, row))

    return render_template("leads.html", rows=rows)


# ================= HOME =================
@app.route("/", methods=["GET", "POST"])
def index():
    if "user" not in session:
        return redirect("/login")

    run_followups()

    output = ""
    status = ""

    if request.method == "POST":
        name = format_name(request.form["name"])
        email = request.form["email"]
        message = request.form["message"]

        output = ai_lead(name, message)
        status = send_email(email, output)

        save_lead(session["user"], name, email, message)

    return render_template("index.html", output=output, status=status)


# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)