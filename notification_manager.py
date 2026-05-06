import smtplib
import os
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


class NotificationManager:
    """Sends email alerts via Gmail SMTP."""

    def __init__(self):
        self.sender = os.getenv("GMAIL_SENDER", "")
        self.password = os.getenv("GMAIL_APP_PASSWORD", "")
        self.recipient = os.getenv("ALERT_EMAIL_TO", self.sender)

        if not self.sender or not self.password:
            raise EnvironmentError(
                "GMAIL_SENDER and GMAIL_APP_PASSWORD must be set in .env.\n"
                "Use a Gmail App Password: https://support.google.com/accounts/answer/185833"
            )

    def send_deal_alert(self, flight):
        """Send an HTML + plain-text deal alert email for a FlightData object."""
        subject = (
            f"Flight Deal: {flight.origin_airport}→{flight.destination_airport} "
            f"for {flight.currency}{flight.price:.0f}!"
        )
        plain = _build_plain(flight)
        html = _build_html(flight)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.sender
        msg["To"] = self.recipient
        msg.attach(MIMEText(plain, "plain", "utf-8"))
        msg.attach(MIMEText(html, "html", "utf-8"))

        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as conn:
                conn.ehlo()
                conn.starttls()
                conn.login(self.sender, self.password)
                conn.sendmail(self.sender, self.recipient, msg.as_string())
            logger.info("Alert sent to %s for %s→%s", self.recipient,
                        flight.origin_airport, flight.destination_airport)
        except smtplib.SMTPException as e:
            logger.error("Failed to send email for %s→%s: %s",
                         flight.origin_airport, flight.destination_airport, e)
            raise


def _build_plain(f):
    lines = [
        "FLIGHT DEAL ALERT",
        "=" * 40,
        f"Route:     {f.origin_city} ({f.origin_airport}) → {f.destination_city} ({f.destination_airport})",
        f"Price:     {f.currency}{f.price:.2f}",
        f"Departs:   {f.out_date}",
        f"Returns:   {f.return_date}",
    ]
    if f.deep_link:
        lines += ["", f"Book now: {f.deep_link}"]
    return "\n".join(lines)


def _build_html(f):
    book_link = f'<p><a href="{f.deep_link}" style="color:#1a73e8">Book this deal →</a></p>' if f.deep_link else ""
    return f"""<!DOCTYPE html>
<html>
<body style="font-family:Arial,sans-serif;max-width:480px;margin:auto;padding:24px">
  <h2 style="color:#d93025">✈ Flight Deal Alert!</h2>
  <table style="border-collapse:collapse;width:100%">
    <tr>
      <td style="padding:8px;font-weight:bold;color:#555">Route</td>
      <td style="padding:8px">{f.origin_city} ({f.origin_airport}) → {f.destination_city} ({f.destination_airport})</td>
    </tr>
    <tr style="background:#f8f9fa">
      <td style="padding:8px;font-weight:bold;color:#555">Price</td>
      <td style="padding:8px;font-size:1.4em;color:#188038"><strong>{f.currency}{f.price:.2f}</strong></td>
    </tr>
    <tr>
      <td style="padding:8px;font-weight:bold;color:#555">Departs</td>
      <td style="padding:8px">{f.out_date}</td>
    </tr>
    <tr style="background:#f8f9fa">
      <td style="padding:8px;font-weight:bold;color:#555">Returns</td>
      <td style="padding:8px">{f.return_date}</td>
    </tr>
  </table>
  {book_link}
  <p style="font-size:0.8em;color:#999;margin-top:24px">
    Sent by flight-deal-scraper
  </p>
</body>
</html>"""
