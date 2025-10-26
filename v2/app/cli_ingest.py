import os
import csv
from datetime import datetime
import click
from sqlalchemy.orm import Session
from typing import Optional

from .db import get_session
from .models import Representative, Committee, Hearing, TranscriptSegment


def _find_hearings_csv() -> str:
    candidates = [
        "congressional_hearings_test2.csv",
        os.path.join("data", "congressional_hearings_test2.csv"),
        os.path.join("data", "congressional_hearings.csv"),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    raise FileNotFoundError("Could not find hearings CSV in repo root or data/ directory")


def _parse_date(value: str):
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y/%m/%d", "%b %d, %Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def _get_or_create_representative(session: Session, full_name: str) -> Representative:
    rep = session.query(Representative).filter(Representative.full_name == full_name).first()
    if rep:
        return rep
    rep = Representative(full_name=full_name)
    session.add(rep)
    session.flush()
    return rep


def _get_or_create_committee(session: Session, name: str) -> Committee:
    name = name or "Unknown Committee"
    committee = session.query(Committee).filter(Committee.name == name).first()
    if committee:
        return committee
    committee = Committee(name=name)
    session.add(committee)
    session.flush()
    return committee


def _get_or_create_hearing(session: Session, title: str, date, committee: Committee) -> Hearing:
    q = session.query(Hearing).filter(Hearing.title == title)
    if committee:
        q = q.filter(Hearing.committee_id == committee.id)
    if date:
        q = q.filter(Hearing.date == date)
    hearing = q.first()
    if hearing:
        return hearing
    hearing = Hearing(title=title or "Hearing", date=date, committee_id=committee.id if committee else None)
    session.add(hearing)
    session.flush()
    return hearing


@click.command()
@click.option("--csv-path", type=click.Path(exists=True, dir_okay=False), default=None, help="Path to hearings CSV")
@click.option("--limit", type=int, default=0, help="Limit number of rows to ingest (0 = all)")
def ingest(csv_path: Optional[str], limit: int):
    """Ingest basic hearings CSV into v2 schema (representatives, committees, hearings, transcript_segments)."""
    path = csv_path or _find_hearings_csv()
    added_segments = 0

    with get_session() as session:
        with open(path, newline='', encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader):
                if limit and idx >= limit:
                    break

                document = (row.get("document") or "").strip()
                speaker_name = (row.get("name") or "").strip() or "Unknown"
                text = (row.get("quote") or "").strip()
                date = _parse_date((row.get("date") or "").strip())

                if not text:
                    continue

                rep = _get_or_create_representative(session, speaker_name)
                committee = _get_or_create_committee(session, document)
                hearing = _get_or_create_hearing(session, title=document or "Hearing", date=date, committee=committee)

                # de-dup simple: same hearing + speaker_name + text
                existing = (
                    session.query(TranscriptSegment)
                    .filter(TranscriptSegment.hearing_id == hearing.id)
                    .filter(TranscriptSegment.speaker_name == speaker_name)
                    .filter(TranscriptSegment.text == text)
                    .first()
                )
                if existing:
                    continue

                seg = TranscriptSegment(
                    hearing_id=hearing.id,
                    speaker_id=rep.id,
                    speaker_name=speaker_name,
                    text=text,
                    segment_length=len(text.split()),
                )
                session.add(seg)
                added_segments += 1

    click.echo(f"Ingestion complete. Added {added_segments} transcript segments.")


if __name__ == "__main__":
    ingest()


