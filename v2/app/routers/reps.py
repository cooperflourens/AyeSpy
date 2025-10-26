from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os


router = APIRouter(prefix="/reps", tags=["representatives"])


def get_templates() -> Jinja2Templates:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_dir = os.path.join(base_dir, "templates")
    return Jinja2Templates(directory=templates_dir)


@router.get("", response_class=HTMLResponse)
async def reps_index(request: Request, templates: Jinja2Templates = Depends(get_templates)):
    return templates.TemplateResponse("reps.html", {"request": request, "reps": []})


@router.get("/{rep_id}", response_class=HTMLResponse)
async def rep_profile(rep_id: int, request: Request, templates: Jinja2Templates = Depends(get_templates)):
    return templates.TemplateResponse("rep_profile.html", {"request": request, "rep": {"id": rep_id}})


@router.get("/{rep_id}/quotes", response_class=HTMLResponse)
async def rep_quotes(rep_id: int, request: Request, templates: Jinja2Templates = Depends(get_templates)):
    return templates.TemplateResponse("partials/rep_quotes.html", {"request": request, "quotes": [], "rep_id": rep_id})


@router.get("/{rep_id}/votes", response_class=HTMLResponse)
async def rep_votes(rep_id: int, request: Request, templates: Jinja2Templates = Depends(get_templates)):
    return templates.TemplateResponse("partials/rep_votes.html", {"request": request, "votes": [], "rep_id": rep_id})


@router.get("/{rep_id}/policy", response_class=HTMLResponse)
async def rep_policy(rep_id: int, request: Request, templates: Jinja2Templates = Depends(get_templates)):
    return templates.TemplateResponse("partials/rep_policy.html", {"request": request, "axes": [], "rep_id": rep_id})


