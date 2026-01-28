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
            return {}

    @staticmethod
    def save_smtp_config(config: dict):
        with Session(engine) as session:
            setting = session.get(SystemSetting, "smtp_config")
            if not setting:
                setting = SystemSetting(key="smtp_config", value=json.dumps(config))
            else:
                setting.value = json.dumps(config)
            session.add(setting)
            session.commit()

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

    @staticmethod
    def send_test_email(to_email: str) -> tuple[bool, str]:
        try:
            success = EmailService.send_email(
                subject="Test Email from S-Panel",
                body="This is a test email to verify your SMTP settings. If you received this, your configuration is correct.",
                recipients=[to_email]
            )
            if success:
                return True, "Email sent successfully"
            return False, "Failed to send email. Check logs for details."
        except Exception as e:
            return False, str(e)

    @staticmethod
    def get_deployment_alert_settings() -> dict:
        config = EmailService.get_smtp_config()
        return {
            "enabled": config.get("deployment_alerts_enabled", False),
            "alert_email": config.get("alert_email_recipient", "")
        }
