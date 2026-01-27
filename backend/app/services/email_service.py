import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlmodel import Session, select
from app.models.database import engine
from app.models.settings import SystemSetting
import json
import logging

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def get_smtp_config():
        with Session(engine) as session:
            setting = session.get(SystemSetting, "smtp_config")
            if setting:
                return json.loads(setting.value)
            return None

    @staticmethod
    def send_email(subject: str, body: str, recipients: list[str] = None):
        config = EmailService.get_smtp_config()
        if not config:
            logger.warning("SMTP config not found. Skipping email.")
            return False

        if not recipients:
            recipients = config.get("admin_emails", [])

        if not recipients:
            logger.warning("No recipients defined. Skipping email.")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = config.get("from_email", "noreply@s-panel")
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(config['host'], int(config['port']))
            server.starttls()
            server.login(config['user'], config['password'])
            server.send_message(msg)
            server.quit()
            logger.info(f"Email sent to {recipients}")
            return True
        except Exception as e:
            logger.exception(f"Failed to send email: {e}")
            return False
