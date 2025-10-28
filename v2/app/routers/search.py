from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import os
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from ..db import get_session
from ..models import TranscriptSegment, Hearing, Committee
from ..services.topics import TopicService
from ..services.embeddings import EmbeddingService

# Initialize services once (avoid reloading model per request)
TOPIC_SERVICE = TopicService()
EMBEDDER = EmbeddingService()


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
        expanded_terms = TOPIC_SERVICE.expand(query)
        with get_session() as session:  # type: Session
            # Simple keyword search across expanded terms
            qset = set(expanded_terms or [query])
            text_filters = [TranscriptSegment.text.ilike(f"%{term}%") for term in qset]
            # Combine OR in SQL for speed
            condition = text_filters[0] if len(text_filters) == 1 else or_(*text_filters)
            segments = (
                session.query(TranscriptSegment)
                .join(Hearing, TranscriptSegment.hearing_id == Hearing.id)
                .join(Committee, Hearing.committee_id == Committee.id)
                .filter(condition)
                .order_by(desc(Hearing.date))
                .limit(100)
                .all()
            )

            # Semantic re-ranking if embedding model is available
            if EMBEDDER.is_available() and segments:
                texts = [s.text for s in segments]
                ranked = EMBEDDER.rank(query, texts, top_k=min(20, len(texts)))
                chosen = [segments[i] for i, _ in ranked]
            else:
                chosen = segments[:20]

            for seg in chosen:
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


