from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/consent", response_class=HTMLResponse)
async def get_consent_form(
    request: Request,
    client_id: str,
    redirect_uri: str,
    scope: str,
    response_type: str,
    nonce: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    # In a real application, you would look up the client_id
    # and display information about the client application.
    return templates.TemplateResponse(
        "consent.html", {"request": request, "client_id": client_id, "scope": scope}
    )


@router.post("/consent")
async def handle_consent_form(
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    choice: str = Form(...),
    client_id: str = Form(...),
    redirect_uri: str = Form(...),
    scope: str = Form(...),
    response_type: str = Form(...),
    nonce: str = Form(...),
):
    if choice.lower() != "approve":
        return RedirectResponse(url=f"{redirect_uri}?error=access_denied")

    # In a real application, you would generate an authorization code,
    # store it, and redirect back to the client application.
    # For now, we'll just redirect with a dummy code.
    auth_code = "dummy_auth_code"
    return RedirectResponse(
        url=f"{redirect_uri}?code={auth_code}&state={request.query_params.get('state')}"
    )
