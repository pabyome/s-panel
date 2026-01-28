from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.services.email_service import EmailService
from app.api.deps import SessionDep, CurrentUser

router = APIRouter()

class SmtpConfig(BaseModel):
    host: str
    port: int
    user: str
    password: str
    from_email: EmailStr
    admin_emails: list[EmailStr] = []
    deployment_alerts_enabled: bool = False
    alert_email_recipient: EmailStr | None = None

class TestEmailRequest(BaseModel):
    to_email: EmailStr

@router.get("/settings", response_model=SmtpConfig)
def get_notification_settings(session: SessionDep, current_user: CurrentUser):
    config = EmailService.get_smtp_config()
    # Return defaults if empty
    return SmtpConfig(
        host=config.get("host", ""),
        port=config.get("port", 587),
        user=config.get("user", ""),
        password=config.get("password", ""),
        from_email=config.get("from_email", "noreply@example.com"),
        admin_emails=config.get("admin_emails", []),
        deployment_alerts_enabled=config.get("deployment_alerts_enabled", False),
        alert_email_recipient=config.get("alert_email_recipient", "") or None
    )

@router.post("/settings")
def update_notification_settings(config: SmtpConfig, session: SessionDep, current_user: CurrentUser):
    EmailService.save_smtp_config(config.model_dump())
    return {"status": "ok", "message": "Settings saved"}

@router.post("/test-email")
def send_test_email(request: TestEmailRequest, session: SessionDep, current_user: CurrentUser):
    success, message = EmailService.send_test_email(request.to_email)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"status": "ok", "message": message}
