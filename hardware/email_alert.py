
# sends email alerts when a threat is detected

import smtplib
from email.message import EmailMessage
import time

sender = "coopdetection@gmail.com"
app_password = "YOUR_APP_PASSWORD"


def send_email_alert(recipient="joshua.deree@icloud.com"):
    msg = EmailMessage()
    msg["Subject"] = "Chicken Coop Alert"
    msg["From"] = sender
    msg["To"] = recipient

    msg.set_content(
        "Potential predator detected\n"
        f"Time: {time.strftime('%H:%M:%S')}"
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender, app_password)
        smtp.send_message(msg)
