"""
Database models for AyeSpy congressional transparency platform.
Designed to handle millions of records efficiently.
"""

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float, 
    ForeignKey, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()


class BillStatus(enum.Enum):
    """Bill status enumeration for tracking legislative progress."""
    INTRODUCED = "introduced"
    REFERRED = "referred"
    REPORTED = "reported"
    PASSED_COMMITTEE = "passed_committee"
    PASSED_HOUSE = "passed_house"
    PASSED_SENATE = "passed_senate"
    ENACTED = "enacted"
    VETOED = "vetoed"
    FAILED = "failed"
    WITHDRAWN = "withdrawn"


class Chamber(enum.Enum):
    """Congressional chamber enumeration."""
    HOUSE = "house"
    SENATE = "senate"
    JOINT = "joint"


class Party(enum.Enum):
    """Political party enumeration."""
    DEMOCRAT = "democrat"
    REPUBLICAN = "republican"
    INDEPENDENT = "independent"
    LIBERTARIAN = "libertarian"
    GREEN = "green"
    OTHER = "other"


class Representative(Base):
    """Congressional representative model."""
    __tablename__ = "representatives"
    
    id = Column(Integer, primary_key=True)
    bioguide_id = Column(String(20), unique=True, nullable=False, index=True)
    congress_id = Column(String(20), unique=True, nullable=True, index=True)
    full_name = Column(String(200), nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    state = Column(String(2), nullable=False, index=True)
    district = Column(Integer, nullable=True)  # Null for senators
    chamber = Column(String(20), nullable=False, index=True)
    party = Column(String(50), nullable=False, index=True)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    votes = relationship("Vote", back_populates="representative")
    transcript_segments = relationship("TranscriptSegment", back_populates="speaker")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_rep_state_chamber', 'state', 'chamber'),
        Index('idx_rep_party_active', 'party', 'is_active'),
        Index('idx_rep_name_search', 'full_name', 'state'),
    )


class Committee(Base):
    """Congressional committee model."""
    __tablename__ = "committees"
    
    id = Column(Integer, primary_key=True)
    congress_id = Column(String(50), nullable=False, index=True)
    name = Column(String(500), nullable=False, index=True)
    chamber = Column(String(20), nullable=False, index=True)
    committee_type = Column(String(100), nullable=True)  # standing, select, joint, etc.
    parent_committee_id = Column(Integer, ForeignKey("committees.id"), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    parent_committee = relationship("Committee", remote_side=[id])
    subcommittees = relationship("Committee", backref=backref("parent", remote_side=[id]))
    hearings = relationship("Hearing", back_populates="committee")
    
    # Indexes
    __table_args__ = (
        Index('idx_committee_chamber_active', 'chamber', 'is_active'),
        Index('idx_committee_name_search', 'name', 'chamber'),
    )


class Bill(Base):
    """Bill model for tracking legislation."""
    __tablename__ = "bills"
    
    id = Column(Integer, primary_key=True)
    congress = Column(Integer, nullable=False, index=True)
    bill_number = Column(String(20), nullable=False, index=True)
    bill_type = Column(String(10), nullable=False, index=True)  # hr, s, hjres, sjres, etc.
    title = Column(Text, nullable=False, index=True)
    short_title = Column(String(500), nullable=True)
    summary = Column(Text, nullable=True)
    introduced_date = Column(DateTime, nullable=True, index=True)
    sponsor_id = Column(Integer, ForeignKey("representatives.id"), nullable=True)
    current_status = Column(String(100), nullable=True, index=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    sponsor = relationship("Representative", backref="sponsored_bills")
    bill_statuses = relationship("BillStatusHistory", back_populates="bill", order_by="BillStatusHistory.date")
    votes = relationship("Vote", back_populates="bill")
    
    # Indexes
    __table_args__ = (
        Index('idx_bill_congress_type', 'congress', 'bill_type'),
        Index('idx_bill_status_active', 'current_status', 'is_active'),
        Index('idx_bill_introduced_date', 'introduced_date'),
        UniqueConstraint('congress', 'bill_number', 'bill_type', name='uq_bill_identifier'),
    )


class BillStatusHistory(Base):
    """Bill status change history for complete lifecycle tracking."""
    __tablename__ = "bill_status_history"
    
    id = Column(Integer, primary_key=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False, index=True)
    status = Column(String(100), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    description = Column(Text, nullable=True)
    action_by = Column(String(200), nullable=True)  # committee, chamber, president, etc.
    action_details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    bill = relationship("Bill", back_populates="bill_statuses")
    
    # Indexes
    __table_args__ = (
        Index('idx_bill_status_date', 'bill_id', 'date'),
        Index('idx_status_date', 'status', 'date'),
    )


class Hearing(Base):
    """Congressional hearing model."""
    __tablename__ = "hearings"
    
    id = Column(Integer, primary_key=True)
    congress = Column(Integer, nullable=False, index=True)
    committee_id = Column(Integer, ForeignKey("committees.id"), nullable=False, index=True)
    title = Column(Text, nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)
    chamber = Column(String(20), nullable=False, index=True)
    bill_ids = Column(Text, nullable=True)  # JSON array of related bill IDs
    transcript_url = Column(String(1000), nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    committee = relationship("Committee", back_populates="hearings")
    transcript_segments = relationship("TranscriptSegment", back_populates="hearing")
    
    # Indexes
    __table_args__ = (
        Index('idx_hearing_congress_date', 'congress', 'date'),
        Index('idx_hearing_committee_date', 'committee_id', 'date'),
        Index('idx_hearing_title_search', 'title'),
    )


class TranscriptSegment(Base):
    """Searchable transcript segments with vector embeddings."""
    __tablename__ = "transcript_segments"
    
    id = Column(Integer, primary_key=True)
    hearing_id = Column(Integer, ForeignKey("hearings.id"), nullable=False, index=True)
    speaker_id = Column(Integer, ForeignKey("representatives.id"), nullable=True, index=True)
    speaker_name = Column(String(200), nullable=True, index=True)  # Fallback if not in representatives table
    start_time = Column(String(20), nullable=True)  # HH:MM:SS format
    end_time = Column(String(20), nullable=True)
    text = Column(Text, nullable=False, index=True)
    text_embedding = Column(Text, nullable=False)  # JSON array of floats
    segment_length = Column(Integer, nullable=False, index=True)  # Character count
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    hearing = relationship("Hearing", back_populates="transcript_segments")
    speaker = relationship("Representative", back_populates="transcript_segments")
    
    # Indexes for search performance
    __table_args__ = (
        Index('idx_segment_hearing_time', 'hearing_id', 'start_time'),
        Index('idx_segment_speaker', 'speaker_id', 'speaker_name'),
        Index('idx_segment_length', 'segment_length'),
        Index('idx_segment_text_search', 'text'),
    )


class Vote(Base):
    """Representative voting record model."""
    __tablename__ = "votes"
    
    id = Column(Integer, primary_key=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False, index=True)
    representative_id = Column(Integer, ForeignKey("representatives.id"), nullable=False, index=True)
    vote_position = Column(String(20), nullable=False, index=True)  # yes, no, present, not_voting
    vote_date = Column(DateTime, nullable=False, index=True)
    roll_call_number = Column(Integer, nullable=True)
    chamber = Column(String(20), nullable=False, index=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    bill = relationship("Bill", back_populates="votes")
    representative = relationship("Representative", back_populates="votes")
    
    # Indexes
    __table_args__ = (
        Index('idx_vote_bill_rep', 'bill_id', 'representative_id'),
        Index('idx_vote_position_date', 'vote_position', 'vote_date'),
        Index('idx_vote_chamber_date', 'chamber', 'vote_date'),
        UniqueConstraint('bill_id', 'representative_id', 'roll_call_number', name='uq_vote_record'),
    )


class DataUpdateLog(Base):
    """Log of data updates for monitoring and debugging."""
    __tablename__ = "data_update_log"
    
    id = Column(Integer, primary_key=True)
    update_type = Column(String(50), nullable=False, index=True)  # bills, transcripts, votes, etc.
    status = Column(String(20), nullable=False, index=True)  # success, failed, partial
    records_processed = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_added = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_update_type_status', 'update_type', 'status'),
        Index('idx_update_started', 'started_at'),
    ) 