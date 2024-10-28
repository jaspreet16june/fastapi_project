import os
import base64
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv
load_dotenv()

SENDER_USER_EMAIL = os.getenv("SENDER_USER_EMAIL", "test@gmail.com")
SENDER_USER_PASSWORD = os.getenv("SENDER_USER_PASSWORD", "umjn bzqs zggd nzrm")


def send_verification_email(email: str, verification_url: str):
    """
    Send a verification email to the user.

    This function sends an email containing a verification link to the user's email address.
    It uses SMTP over SSL to securely send the email.

    Parameters:
        email (str): The recipient's email address.
        verification_url (str): The URL that the user should click to verify their email.

    Returns:
        str: A success message indicating that the email has been sent.

    Raises:
        SMTPException: If there is an issue with the SMTP connection or sending the email.
    """
    
    msg = EmailMessage()
    msg["From"] = SENDER_USER_EMAIL
    msg["To"] = email
    msg["Subject"] = "Email Verification"
    msg.set_content(f"Please verify your email by clicking on this link: {verification_url}")

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(SENDER_USER_EMAIL,SENDER_USER_PASSWORD)
        smtp.send_message(msg)
        
    return "Mail sent successfully!"

def generate_encrypted_url(filename: str) -> str:
    # Basic encoding of the filename for the URL
    """
    Generate an encrypted URL for accessing a file.

    This function encodes the filename using base64 encoding to create a URL-safe
    version of the filename, allowing secure download links.

    Parameters:
        filename (str): The name of the file to encode.

    Returns:
        str: A URL-safe encoded down
        load path for the file.
    """
    encoded_filename = base64.urlsafe_b64encode(filename.encode()).decode()
    download_url = f"tmp/path/to/your/files/{encoded_filename}"
    
    return download_url