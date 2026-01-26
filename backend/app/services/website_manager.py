from sqlmodel import Session, select
from typing import List, Optional
from app.models.database import Website
from app.schemas.website import WebsiteCreate
from app.services.nginx_manager import NginxManager

class WebsiteManager:
    def __init__(self, session: Session):
        self.session = session

    def get_all_websites(self) -> List[Website]:
        return self.session.exec(select(Website)).all()

    def get_website_by_id(self, website_id: int) -> Optional[Website]:
        return self.session.get(Website, website_id)

    def create_website(self, website_data: WebsiteCreate) -> Website:
        # 1. Create DB Entry
        db_website = Website.model_validate(website_data)
        self.session.add(db_website)
        self.session.commit()
        self.session.refresh(db_website)

        # 2. Generate Nginx Config using reused Manager
        # We wrap this in try/except to rollback DB if Nginx fails,
        # but for MVP we might just log error.
        success = NginxManager.create_site(db_website.domain, db_website.port)
        if not success:
            print(f"Warning: Failed to create Nginx config for {db_website.domain}")
            # Optional: db_website.status = "error"
            # self.session.add(db_website); self.session.commit()

        return db_website

    def delete_website(self, website_id: int) -> bool:
        website = self.get_website_by_id(website_id)
        if not website:
            return False

        # 1. Remove Nginx Config
        NginxManager.remove_site(website.domain)

        # 2. Delete from DB
        self.session.delete(website)
        self.session.commit()
        return True
