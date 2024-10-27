from email.message import EmailMessage
import smtplib
import os
from email.message import EmailMessage

from dotenv import load_dotenv
load_dotenv()

SENDER_USER_EMAIL = os.getenv("USER_EMAIL", "default@gmail.com")
SENDER_USER_PASSWORD = os.getenv("SENDER_USER_PASSWORD", "test password")


def send_verification_email(email: str, verification_url: str):
    msg = EmailMessage()
    msg["From"] = SENDER_USER_EMAIL
    msg["To"] = email
    msg["Subject"] = "Email Verification"
    msg.set_content(f"Please verify your email by clicking on this link: {verification_url}")

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(SENDER_USER_EMAIL,SENDER_USER_PASSWORD)
        smtp.send_message(msg)
        
    return "Mail sent successfully!"