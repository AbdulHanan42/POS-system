import html
import os
import smtplib
import ssl
from email.message import EmailMessage

import resend

resend.api_key = os.getenv("RESEND_API_KEY")


def _deliver_customer_email(email: str, subject: str, text: str, html_content: str) -> bool:
    smtp_host = (os.getenv("SMTP_HOST") or "").strip()
    smtp_username = (os.getenv("SMTP_USERNAME") or "").strip()
    smtp_password = os.getenv("SMTP_PASSWORD") or ""
    if smtp_host.lower() == "smtp.gmail.com":
        smtp_password = "".join(smtp_password.split())
    smtp_sender = (os.getenv("SMTP_FROM_EMAIL") or smtp_username).strip()

    if smtp_host and smtp_sender and bool(smtp_username) == bool(smtp_password):
        try:
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            ssl_setting = os.getenv("SMTP_USE_SSL")
            use_ssl = (
                ssl_setting.lower() in {"1", "true", "yes"}
                if ssl_setting is not None
                else smtp_port == 465
            )
            message = EmailMessage()
            message["Subject"] = subject
            message["From"] = smtp_sender
            message["To"] = email
            message.set_content(text)
            message.add_alternative(html_content, subtype="html")
            context = ssl.create_default_context()

            if use_ssl:
                with smtplib.SMTP_SSL(
                    smtp_host,
                    smtp_port,
                    context=context,
                    timeout=10,
                ) as smtp:
                    if smtp_username:
                        smtp.login(smtp_username, smtp_password)
                    smtp.send_message(message)
            else:
                with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as smtp:
                    smtp.ehlo()
                    smtp.starttls(context=context)
                    smtp.ehlo()
                    if smtp_username:
                        smtp.login(smtp_username, smtp_password)
                    smtp.send_message(message)
            return True
        except Exception as error:
            print(f"SMTP customer email failed ({type(error).__name__}); trying Resend fallback.")
    elif smtp_host:
        print("SMTP is incomplete; trying Resend fallback.")

    resend_sender = (
        os.getenv("RESEND_FROM_EMAIL") or os.getenv("SMTP_FROM_EMAIL") or ""
    ).strip()
    if not resend.api_key or not resend_sender:
        print("Customer email could not be sent; configure SMTP or Resend with a valid sender.")
        return False

    try:
        resend.Emails.send({
            "from": resend_sender,
            "to": [email],
            "subject": subject,
            "text": text,
            "html": html_content,
        })
        return True
    except Exception as error:
        print(f"Resend customer email failed ({type(error).__name__}).")
        return False


def send_customer_registration_otp(email: str, name: str, otp: str) -> bool:
    """Send the email verification code using SMTP, with Resend fallback."""
    safe_name = html.escape(name)
    return _deliver_customer_email(
        email,
        "Verify your email to complete registration",
        f"Hi {name},\n\nYour verification code is {otp}. It expires in 10 minutes.",
        f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2>Verify your email</h2>
                <p>Hi {safe_name}, enter this code to finish creating your account:</p>
                <p style="font-size: 28px; font-weight: bold; letter-spacing: 6px;">{otp}</p>
                <p>This code expires in 10 minutes.</p>
            </div>
        """,
    )


def send_customer_registration_confirmation(email: str, name: str) -> bool:
    """Send registration confirmation after successful email verification."""
    site_url = (os.getenv("CUSTOMER_SITE_URL") or "http://localhost:5174").rstrip("/")
    safe_name = html.escape(name)
    safe_url = html.escape(site_url, quote=True)
    return _deliver_customer_email(
        email,
        "Your account is ready",
        (
            f"Hi {name},\n\nYour email has been verified and your account is ready. "
            f"Continue your order here: {site_url}"
        ),
        f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2>Your account is ready, {safe_name}!</h2>
                <p>Your email has been verified and your account is ready.</p>
                <p><a href="{safe_url}">Continue your order</a></p>
            </div>
        """,
    )


async def send_password_reset_email(email: str, otp: str) -> bool:
    """Send password reset OTP email using Resend"""
    if not resend.api_key:
        print(f"Resend API key not configured. OTP for {email}: {otp}")
        return False

    try:
        resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": [email],
            "subject": "Password Reset Code",
            "html": f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #333;">Password Reset Request</h2>
                    <p>You requested to reset your password. Use the following code to proceed:</p>
                    <div style="background: #f4f4f4; padding: 20px; text-align: center; font-size: 24px; font-weight: bold; letter-spacing: 5px; margin: 20px 0;">
                        {otp}
                    </div>
                    <p>This code will expire in 1 hour.</p>
                    <p>If you didn't request this, please ignore this email.</p>
                </div>
            """,
        })
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        print(f"OTP for {email}: {otp}")
        return False
