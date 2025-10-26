from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os


router = APIRouter(prefix="/bills", tags=["bills"])


def get_templates() -> Jinja2Templates:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_dir = os.path.join(base_dir, "templates")
    return Jinja2Templates(directory=templates_dir)


@router.get("", response_class=HTMLResponse)
async def bills_index(request: Request, templates: Jinja2Templates = Depends(get_templates)):
    return templates.TemplateResponse("bills.html", {"request": request, "bills": []})


@router.get("/{bill_id}", response_class=HTMLResponse)
async def bill_detail(bill_id: int, request: Request, templates: Jinja2Templates = Depends(get_templates)):
    return templates.TemplateResponse("bill_detail.html", {"request": request, "bill": {"id": bill_id}})


