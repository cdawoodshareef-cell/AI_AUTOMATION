import requests
import smtplib
from email.mime.text import MIMEText


# ================= AI FUNCTION =================
def ai_lead(name, message):
    prompt = f"""
You are a professional business assistant for DS AI Solutions.

Customer Name: {name}
Customer Message: {message}

Your task:
- Write a high-converting professional email reply
- No subject line
- No placeholders
- Keep it short, clear, and persuasive

Business context:
- DS AI Solutions provides AI automation services
- Services include dashboards, automation tools, integrations
- Pricing starts from ₹5,000

Important:
- Encourage the customer to take next step (call / reply / discussion)
- Make it feel personalized and helpful

Signature (use exactly):
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

        print("RAW RESPONSE:", response.text)

        data = response.json()

        return data["choices"][0]["message"]["content"]

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

        print("✅ Email sent successfully!")

    except Exception as e:
        print("❌ Email Error:", str(e))


# ================= MAIN =================
if __name__ == "__main__":
    name = "Rahul"
    email = "receiver_email@gmail.com"
    message = "I want pricing details for your service"

    # Generate AI response
    ai_output = ai_lead(name, message)

    print("\n===== AI OUTPUT =====\n")
    print(ai_output)

    # Send email
    send_email(email, ai_output)