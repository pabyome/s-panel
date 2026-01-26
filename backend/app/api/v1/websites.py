from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.api.deps import SessionDep, CurrentUser
from app.schemas.website import WebsiteCreate, WebsiteRead
from app.services.website_manager import WebsiteManager

router = APIRouter()

@router.post("/", response_model=WebsiteRead)
def create_website(
    website: WebsiteCreate,
    session: SessionDep,
    current_user: CurrentUser
):
    manager = WebsiteManager(session)
    return manager.create_website(website)

@router.get("/", response_model=List[WebsiteRead])
def read_websites(
    session: SessionDep,
    current_user: CurrentUser
):
    manager = WebsiteManager(session)
    return manager.get_all_websites()

@router.delete("/{website_id}")
def delete_website(
    website_id: int,
    session: SessionDep,
    current_user: CurrentUser
):
    manager = WebsiteManager(session)
    success = manager.delete_website(website_id)
    if not success:
        raise HTTPException(status_code=404, detail="Website not found")
    return {"ok": True}
