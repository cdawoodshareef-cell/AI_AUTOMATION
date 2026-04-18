import os
import smtplib
from email.mime.text import MIMEText
from openai import OpenAI

# ================= OPENAI SETUP =================
client = OpenAI(api_key=os.getenv("ae91f5bad8c4e3e031e7b11e41c55941"))

# ================= EMAIL CONFIG =================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# ⚠️ Replace with your sender email
SENDER_EMAIL = "cdawoodshareef@gmail.com"
SENDER_PASSWORD = "arxgknlecosbkwtl"  # Use Gmail App Password (NOT normal password)

# ================= AI FUNCTION =================
def ai_lead(name, message):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional sales assistant. Write clear, persuasive, and polite replies to customers."
                },
                {
                    "role": "user",
                    "content": f"Customer Name: {name}\nCustomer Message: {message}\nWrite a professional response email."
                }
            ]
        )

        ai_text = response.choices[0].message.content
        return ai_text

    except Exception as e:
        return f"AI Error: {str(e)}"

# ================= EMAIL FUNCTION =================
def send_email(receiver_email, message):
    try:
        msg = MIMEText(message)
        msg["Subject"] = "Response from DS AI Solutions"
        msg["From"] = SENDER_EMAIL
        msg["To"] = receiver_email

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()

        return "Email sent successfully"

    except Exception as e:
        return f"Email Error: {str(e)}"

# ================= MAIN (TESTING ONLY) =================
if __name__ == "__main__":
    name = "Rahul"
    email = "receiver_email@gmail.com"
    message = "I want pricing details for your service"

    # Generate AI response
    ai_output = ai_lead(name, message)

    print("\n===== AI OUTPUT =====\n")
    print(ai_output)

    # Send email
    result = send_email(email, ai_output)
    print("\n===== EMAIL STATUS =====\n")
    print(result)