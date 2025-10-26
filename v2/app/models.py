from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from .db import Base


class Representative(Base):
    __tablename__ = "representatives"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True, nullable=False)
    chamber = Column(String, index=True)
    party = Column(String, index=True)
    state = Column(String, index=True)
    district = Column(String)
    bio = Column(Text)

    quotes = relationship("TranscriptSegment", back_populates="speaker")
    vote_positions = relationship("VotePosition", back_populates="representative")
    policy_scores = relationship("RepPolicyScore", back_populates="representative")


class Committee(Base):
    __tablename__ = "committees"
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True, nullable=False)
    chamber = Column(String, index=True)

    hearings = relationship("Hearing", back_populates="committee")


class Hearing(Base):
    __tablename__ = "hearings"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    date = Column(Date, index=True)
    committee_id = Column(Integer, ForeignKey("committees.id"), index=True)

    committee = relationship("Committee", back_populates="hearings")
    segments = relationship("TranscriptSegment", back_populates="hearing")


class TranscriptSegment(Base):
    __tablename__ = "transcript_segments"
    id = Column(Integer, primary_key=True)
    hearing_id = Column(Integer, ForeignKey("hearings.id"), index=True)
    speaker_id = Column(Integer, ForeignKey("representatives.id"), nullable=True, index=True)
    speaker_name = Column(String, index=True)
    text = Column(Text, nullable=False)
    start_time = Column(String)
    end_time = Column(String)
    segment_length = Column(Integer)
    text_embedding = Column(Text, default="[]")  # JSON string

    hearing = relationship("Hearing", back_populates="segments")
    speaker = relationship("Representative", back_populates="quotes")
    topics = relationship("QuoteTopic", back_populates="quote")


class Topic(Base):
    __tablename__ = "topics"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True)
    parent_id = Column(Integer, ForeignKey("topics.id"), nullable=True)


class QuoteTopic(Base):
    __tablename__ = "quote_topics"
    id = Column(Integer, primary_key=True)
    quote_id = Column(Integer, ForeignKey("transcript_segments.id"), index=True)
    topic_id = Column(Integer, ForeignKey("topics.id"), index=True)

    quote = relationship("TranscriptSegment", back_populates="topics")


class Bill(Base):
    __tablename__ = "bills"
    id = Column(Integer, primary_key=True)
    bill_type = Column(String, index=True)
    bill_number = Column(String, index=True)
    title = Column(Text)
    introduced_date = Column(Date)
    current_status = Column(String, index=True)
    sponsor_name = Column(String, index=True)
    summary = Column(Text)

    votes = relationship("Vote", back_populates="bill")


class Vote(Base):
    __tablename__ = "votes"
    id = Column(Integer, primary_key=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), index=True)
    date = Column(Date)
    chamber = Column(String, index=True)
    result = Column(String)

    bill = relationship("Bill", back_populates="votes")
    positions = relationship("VotePosition", back_populates="vote")


class VotePosition(Base):
    __tablename__ = "vote_positions"
    id = Column(Integer, primary_key=True)
    vote_id = Column(Integer, ForeignKey("votes.id"), index=True)
    representative_id = Column(Integer, ForeignKey("representatives.id"), index=True)
    position = Column(String, index=True)  # Yea/Nay/Present/Not Voting

    vote = relationship("Vote", back_populates="positions")
    representative = relationship("Representative", back_populates="vote_positions")


class RepPolicyScore(Base):
    __tablename__ = "rep_policy_scores"
    id = Column(Integer, primary_key=True)
    representative_id = Column(Integer, ForeignKey("representatives.id"), index=True)
    issue_key = Column(String, index=True)
    score = Column(Float)  # -1..1
    updated_at = Column(DateTime)

    representative = relationship("Representative", back_populates="policy_scores")


