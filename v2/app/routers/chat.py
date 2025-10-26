from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os


router = APIRouter(prefix="/chat", tags=["chat"])


def get_templates() -> Jinja2Templates:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_dir = os.path.join(base_dir, "templates")
    return Jinja2Templates(directory=templates_dir)


@router.get("/rep/{rep_id}", response_class=HTMLResponse)
async def chat_page(rep_id: int, request: Request, templates: Jinja2Templates = Depends(get_templates)):
    return templates.TemplateResponse("chat.html", {"request": request, "rep_id": rep_id, "messages": []})


@router.post("/rep/{rep_id}", response_class=HTMLResponse)
async def chat_turn(rep_id: int, request: Request, message: str = Form(""), templates: Jinja2Templates = Depends(get_templates)):
    # Placeholder: echo back
    messages = [{"role": "user", "text": message}, {"role": "assistant", "text": "Thanks, this is a placeholder response."}]
    return templates.TemplateResponse("partials/chat_messages.html", {"request": request, "messages": messages})


