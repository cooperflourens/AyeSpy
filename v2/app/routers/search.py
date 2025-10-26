from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import os
from sqlalchemy.orm import Session

from ..db import get_session
from ..models import TranscriptSegment, Hearing, Committee
from ..services.topics import TopicService


router = APIRouter(tags=["search"])


def get_templates() -> Jinja2Templates:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_dir = os.path.join(base_dir, "templates")
    return Jinja2Templates(directory=templates_dir)


@router.get("/search", response_class=HTMLResponse)
async def search_page(request: Request, templates: Jinja2Templates = Depends(get_templates)):
    return templates.TemplateResponse("search.html", {"request": request, "results": []})


@router.get("/search/partial", response_class=HTMLResponse)
async def search_partial(
    request: Request,
    q: Optional[str] = Query(default=None),
    templates: Jinja2Templates = Depends(get_templates),
):
    results = []
    query = (q or "").strip()
    if query:
        topic_service = TopicService()
        expanded_terms = topic_service.expand(query)
        with get_session() as session:  # type: Session
            # Simple keyword search across expanded terms
            qset = set(expanded_terms or [query])
            text_filters = [TranscriptSegment.text.ilike(f"%{term}%") for term in qset]
            segments = (
                session.query(TranscriptSegment)
                .join(Hearing, TranscriptSegment.hearing_id == Hearing.id)
                .join(Committee, Hearing.committee_id == Committee.id)
                .filter(text_filters[0] if len(text_filters) == 1 else (text_filters[0]))
                .limit(20)
                .all()
            )
            # If more than one term, apply OR filtering in Python (SQLite portability)
            if len(qset) > 1:
                segments = [s for s in segments if any(term.lower() in (s.text or "").lower() for term in qset)]
            for seg in segments:
                # Minimal metadata join for display
                hearing = seg.hearing
                committee = hearing.committee if hearing else None
                results.append(
                    {
                        "speaker_name": seg.speaker_name,
                        "committee_name": committee.name if committee else None,
                        "hearing_date": hearing.date.isoformat() if hearing and hearing.date else None,
                        "text": seg.text,
                    }
                )

    return templates.TemplateResponse(
        "partials/search_results.html",
        {"request": request, "results": results, "query": query},
    )


