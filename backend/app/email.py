import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY")


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
